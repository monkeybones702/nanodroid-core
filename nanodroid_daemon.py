#!/usr/bin/env python3
import os
import sys
import time
import sqlite3
import hashlib
import subprocess
import threading
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

# ==============================================================================
# NanoDroid-Core Unified Supervisor Daemon (v5.2.0)
# Target: Samsung Galaxy A16 (ARM64) | Shizuku (rish) Binder Architecture
# ==============================================================================

DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
DUMP_PATH = "/data/local/tmp/window_dump.xml"
TERMUX_PKG = "com.termux"
CANDIDATE_GEMINI_PKGS = [
    "com.google.android.apps.bard",
    "com.google.android.googlequicksearchbox",
    "com.android.chrome"
]

app = FastAPI(title="NanoDroid Unified Telemetry & Engine", version="5.2.0")

# --- Database Initialization ---
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            snippet_hash TEXT UNIQUE,
            snippet_content TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Android System Hooks (Shizuku / rish) ---
def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def tap(x, y):
    rish_exec(f"input tap {x} {y}")

def swipe_up():
    rish_exec("input swipe 540 1600 540 600 300")

def launch_app(pkg):
    rish_exec(f"am start -p {pkg} -c android.intent.category.LAUNCHER")

def get_active_gemini_pkg():
    for pkg in CANDIDATE_GEMINI_PKGS:
        res = rish_exec(f"pm path {pkg}")
        if res.returncode == 0 and "package:" in res.stdout:
            return pkg
    return CANDIDATE_GEMINI_PKGS[1]

def type_via_clipboard(text):
    try:
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=text)
        time.sleep(0.3)
        rish_exec("input keyevent 279") # KEYCODE_PASTE
    except Exception as e:
        print(f"[-] Clipboard injection error: {e}")

def get_xml_state():
    rish_exec(f"uiautomator dump {DUMP_PATH}")
    res = rish_exec(f"cat {DUMP_PATH}")
    if res.returncode == 0:
        content = res.stdout.strip()
        return hashlib.md5(content.encode('utf-8')).hexdigest(), content
    return "", ""

def find_and_click_node(keyword, xml_content):
    try:
        root = ET.fromstring(xml_content)
        for elem in root.iter('node'):
            text = elem.get('text', '').lower()
            desc = elem.get('content-desc', '').lower()
            if keyword in text or keyword in desc:
                bounds = elem.get('bounds')
                if bounds:
                    coords = list(map(int, ''.join(c for c in bounds if c.isdigit() or c == ' ').split()))
                    if len(coords) == 4:
                        cx, cy = (coords[0] + coords[2]) // 2, (coords[1] + coords[3]) // 2
                        tap(cx, cy)
                        return True
    except Exception as e:
        print(f"[-] XML parse error: {e}")
    return False

def is_snippet_executed(snippet_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM execution_log WHERE snippet_hash = ?", (snippet_hash,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def log_execution(snippet_hash, snippet_content, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO execution_log (timestamp, snippet_hash, snippet_content, status)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), snippet_hash, snippet_content, status))
    conn.commit()
    conn.close()

def send_prompt(gemini_pkg, prompt_text):
    print(f"[*] Switching back to Gemini ({gemini_pkg})...")
    launch_app(gemini_pkg)
    time.sleep(2.5)
    _, xml_data = get_xml_state()
    if not find_and_click_node("ask gemini", xml_data) and not find_and_click_node("message", xml_data):
        tap(540, 2150) # Fallback input bar coordinate for Galaxy A16
    time.sleep(0.5)
    print(f"[*] Injecting prompt: '{prompt_text}'")
    type_via_clipboard(prompt_text)
    time.sleep(0.5)
    rish_exec("input keyevent 66") # ENTER / Send
    print("[+] Prompt transmitted successfully.")

def execute_engine_cycle():
    init_database()
    gemini_pkg = get_active_gemini_pkg()
    print(f"\n[NanoDroid Daemon] Starting Engine Cycle [Target: {gemini_pkg}]")

    launch_app(gemini_pkg)
    time.sleep(2.5)

    hash_val, xml_data = get_xml_state()
    clicked = find_and_click_node("copy code", xml_data) or find_and_click_node("copy", xml_data)

    scroll_attempts = 0
    while not clicked and scroll_attempts < 5:
        old_hash = hash_val
        swipe_up()
        time.sleep(1.2)
        hash_val, xml_data = get_xml_state()
        if hash_val == old_hash:
            print("[!] Scroll boundary reached. Sending continuation prompt.")
            send_prompt(gemini_pkg, "continue software creation coding")
            return "scroll_boundary_reached"
        clicked = find_and_click_node("copy code", xml_data) or find_and_click_node("copy", xml_data)
        scroll_attempts += 1

    if not clicked:
        print("[!] Max depth reached without locating code block.")
        send_prompt(gemini_pkg, "continue software creation coding")
        return "max_depth_reached"

    print("[+] Code block copy button triggered!")
    time.sleep(1.0)

    res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True)
    code_snippet = res.stdout.strip()

    if not code_snippet or len(code_snippet) < 3:
        print("[-] Clipboard payload invalid.")
        send_prompt(gemini_pkg, "continue software creation coding")
        return "invalid_clipboard"

    snippet_hash = hashlib.md5(code_snippet.encode('utf-8')).hexdigest()
    if is_snippet_executed(snippet_hash):
        print("[!] Snippet already executed. Skipping duplicate.")
        send_prompt(gemini_pkg, "continue software creation coding")
        return "duplicate_skipped"

    print(f"[+] Executing snippet ({len(code_snippet)} chars) in Termux...")
    launch_app(TERMUX_PKG)
    time.sleep(1.5)

    script_path = os.path.expanduser("~/nanodroid_active_task.sh")
    with open(script_path, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(code_snippet + "\n")
    os.chmod(script_path, 0o755)

    type_via_clipboard(f"bash {script_path}")
    time.sleep(0.5)
    rish_exec("input keyevent 66")
    time.sleep(4.0)

    log_execution(snippet_hash, code_snippet, "SUCCESS")
    send_prompt(gemini_pkg, "Give me the next code block.")
    return "success"

# --- FastAPI Web Dashboard & API Endpoints ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NanoDroid Unified Daemon</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4">
    <div class="max-w-md mx-auto space-y-4">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex justify-between items-center">
            <div>
                <h1 class="text-xl font-bold text-emerald-400">NanoDroid Daemon</h1>
                <p class="text-xs text-slate-400">Galaxy A16 ARM64 | v5.2.0</p>
            </div>
            <span class="px-2.5 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 rounded-full animate-pulse">Active</span>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Control Panel</h2>
            <div class="grid grid-cols-2 gap-2">
                <button onclick="triggerCycle()" class="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold p-2.5 rounded-lg text-sm transition">Run Cycle</button>
                <button onclick="fetchTelemetry()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold p-2.5 rounded-lg text-sm transition">Refresh Logs</button>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Execution History</h2>
            <div id="log-container" class="space-y-2 max-h-64 overflow-y-auto font-mono text-xs">
                <p class="text-slate-500">Loading telemetry data...</p>
            </div>
        </div>
    </div>
    <script>
        async function fetchTelemetry() {
            let res = await fetch('/api/telemetry');
            let data = await res.json();
            let container = document.getElementById('log-container');
            if (data.records.length === 0) {
                container.innerHTML = '<p class="text-slate-500">No execution records found.</p>';
                return;
            }
            container.innerHTML = data.records.map(r => `
                <div class="bg-slate-950 border border-slate-800 p-2 rounded flex flex-col space-y-1">
                    <div class="flex justify-between text-[10px] text-slate-400">
                        <span>#${r[0]} | ${r[1]}</span>
                        <span class="text-emerald-400 font-bold">${r[4]}</span>
                    </div>
                    <pre class="text-slate-300 truncate">${r[3].substring(0, 80)}...</pre>
                </div>
            `).join('');
        }
        async function triggerCycle() {
            let res = await fetch('/api/trigger', {method: 'POST'});
            let data = await res.json();
            alert("Cycle Result: " + data.result);
            fetchTelemetry();
        }
        fetchTelemetry();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_root():
    return DASHBOARD_HTML

@app.get("/api/telemetry")
def get_telemetry():
    if not os.path.exists(DB_PATH):
        return {"records": []}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, snippet_hash, snippet_content, status FROM execution_log ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return {"records": rows}

@app.post("/api/trigger")
def api_trigger():
    res = execute_engine_cycle()
    return {"status": "success", "result": res}

if __name__ == "__main__":
    init_database()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
