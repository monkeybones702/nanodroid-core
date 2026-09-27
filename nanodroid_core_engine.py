#!/usr/init/env python3
import os
import sys
import time
import sqlite3
import hashlib
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

# ==============================================================================
# NanoDroid-Core Master Orchestration Engine (v5.0.0)
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

def execute_cycle():
    init_database()
    gemini_pkg = get_active_gemini_pkg()
    print(f"\n==================================================")
    print(f"  NanoDroid Master Engine [Target: {gemini_pkg}]")
    print(f"==================================================")

    launch_app(gemini_pkg)
    time.sleep(2.5)

    hash_val, xml_data = get_xml_state()
    clicked = find_and_click_node("copy code", xml_data) or find_and_click_node("copy", xml_data)

    scroll_attempts = 0
    while not clicked and scroll_attempts < 5:
        print(f"[*] Scanning viewport (Attempt {scroll_attempts+1}/5)...")
        old_hash = hash_val
        swipe_up()
        time.sleep(1.2)
        hash_val, xml_data = get_xml_state()
        if hash_val == old_hash:
            print("[!] Scroll boundary reached. No further code blocks found.")
            send_prompt(gemini_pkg, "continue software creation coding")
            return False
        clicked = find_and_click_node("copy code", xml_data) or find_and_click_node("copy", xml_data)
        scroll_attempts += 1

    if not clicked:
        print("[!] Max depth reached without locating code block.")
        send_prompt(gemini_pkg, "continue software creation coding")
        return False

    print("[+] Code block copy button triggered!")
    time.sleep(1.0)

    # Intercept Clipboard
    res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True)
    code_snippet = res.stdout.strip()

    if not code_snippet or len(code_snippet) < 3:
        print("[-] Clipboard payload invalid.")
        send_prompt(gemini_pkg, "continue software creation coding")
        return False

    snippet_hash = hashlib.md5(code_snippet.encode('utf-8')).hexdigest()
    if is_snippet_executed(snippet_hash):
        print("[!] Snippet already executed previously. Skipping duplicate.")
        send_prompt(gemini_pkg, "continue software creation coding")
        return True

    print(f"[+] Intercepted Snippet ({len(code_snippet)} chars). Executing in Termux...")
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
    return True

if __name__ == "__main__":
    try:
        execute_cycle()
    except KeyboardInterrupt:
        print("\n[*] Engine execution interrupted by user.")
