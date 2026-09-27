#!/usr/bin/env python3
import os
import sys
import time
import sqlite3
import hashlib
import subprocess
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

# ==============================================================================
# NanoDroid-Core Master AICore Daemon (v6.1.0)
# Target: Samsung Galaxy A16 (ARM64) | AICore + Shizuku (rish) Integration
# ==============================================================================

DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
DUMP_PATH = "/data/local/tmp/window_dump.xml"
TERMUX_PKG = "com.termux"
AI_CORE_SERVICE = "com.google.android.aicore"
BROADCAST_ACTION = "com.google.android.aicore.GENERATE_PROMPT"

CANDIDATE_GEMINI_PKGS = [
    "com.google.android.apps.bard",
    "com.google.android.googlequicksearchbox",
    "com.android.chrome"
]

app = FastAPI(title="NanoDroid Master AICore Daemon", version="6.1.0")

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

def query_native_aicore(prompt_text):
    print(f"[*] Querying native AICore: '{prompt_text}'")
    payload = {"prompt": prompt_text, "temperature": 0.2, "max_tokens": 512}
    temp_json_path = "/data/local/tmp/aicore_payload.json"
    
    with open("/tmp/aicore_payload.json", "w") as f:
        f.write(json.dumps(payload))
    
    rish_exec(f"cp /tmp/aicore_payload.json {temp_json_path}")
    rish_exec(f"chmod 644 {temp_json_path}")
    
    res = rish_exec(f"am broadcast -a {BROADCAST_ACTION} --ei max_tokens 512 -e payload_path {temp_json_path}")
    if res.returncode == 0:
        time.sleep(1.0)
        pull_res = rish_exec("cat /data/local/tmp/aicore_response.json")
        if pull_res.returncode == 0 and pull_res.stdout.strip():
            try:
                data = json.loads(pull_res.stdout.strip())
                return data.get("response", None)
            except:
                pass
    return None

def send_prompt(gemini_pkg, prompt_text):
    # Attempt native AICore broadcast first; fallback to UI injection if needed
    native_res = query_native_aicore(prompt_text)
    if native_res:
        print(f"[+] AICore responded natively. Injecting response into session...")
        launch_app(gemini_pkg)
        time.sleep(1.5)
        _, xml_data = get_xml_state()
        if not find_and_click_node("ask gemini", xml_data) and not find_and_click_node("message", xml_data):
            tap(540, 2150)
        time.sleep(0.5)
        type_via_clipboard(native_res)
        time.sleep(0.5)
        rish_exec("input keyevent 66")
        return

    print(f"[*] Fallback: Interfacing via UI input bar ({gemini_pkg})...")
    launch_app(gemini_pkg)
    time.sleep(2.5)
    _, xml_data = get_xml_state()
    if not find_and_click_node("ask gemini", xml_data) and not find_and_click_node("message", xml_data):
        tap(540, 2150)
    time.sleep(0.5)
    type_via_clipboard(prompt_text)
    time.sleep(0.5)
    rish_exec("input keyevent 66")
    print("[+] Fallback prompt transmitted successfully.")

def execute_engine_cycle():
    init_database()
    gemini_pkg = get_active_gemini_pkg()
    print(f"\n[NanoDroid Master] Cycle Initiated [Target: {gemini_pkg}]")

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
            print("[!] Scroll boundary reached. Triggering continuation prompt.")
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
    
    # Check sqlite ledger
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM execution_log WHERE snippet_hash = ?", (snippet_hash,))
    exists = cursor.fetchone()
    conn.close()

    if exists:
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

    # Log to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO execution_log (timestamp, snippet_hash, snippet_content, status)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), snippet_hash, code_snippet, "SUCCESS"))
    conn.commit()
    conn.close()

    send_prompt(gemini_pkg, "Give me the next code block.")
    return "success"

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NanoDroid Master AICore Daemon</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4">
    <div class="max-w-md mx-auto space-y-4">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex justify-between items-center">
            <div>
                <h1 class="text-xl font-bold text-emerald-400">NanoDroid Master</h1>
                <p class="text-xs text-slate-400">AICore / Galaxy A16 | v6.1.0</p>
            </div>
            <span class="px-2.5 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 rounded-full animate-pulse">Online</span>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Control Panel</h2>
            <div class="grid grid-cols-2 gap-2">
                <button onclick="triggerCycle()" class="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold p-2.5 rounded-lg text-sm transition">Run Cycle</button>
                <button onclick="fetchTelemetry()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold p-2.5 rounded-lg text-sm transition">Refresh Logs</button>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Execution Ledger</h2>
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
