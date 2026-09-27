#!/usr/bin/env python3
import os
import sys
import subprocess
import sqlite3
import time
import hashlib
from datetime import datetime

# ==============================================================================
# NanoDroid-Core Autonomous Self-Correction Orchestrator (v11.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Closed-Loop Error Recovery & Execution
# ==============================================================================

DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
ACTIVE_SCRIPT_PATH = os.path.expanduser("~/nanodroid_active_task.sh")
AICORE_PAYLOAD_PATH = "/data/local/tmp/aicore_payload.json"
AICORE_RESPONSE_PATH = "/data/local/tmp/aicore_response.json"
BROADCAST_ACTION = "com.google.android.aicore.GENERATE_PROMPT"

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def query_native_aicore_correction(error_msg, failed_code):
    print(f"[*] Dispatching execution failure context to AICore for auto-correction...")
    prompt = f"The following bash/python script failed with an error. Please fix the code and return only the corrected executable script block.\n\nError Output:\n{error_msg}\n\nFailed Code:\n{failed_code}"
    
    payload = {"prompt": prompt, "temperature": 0.1, "max_tokens": 1024}
    with open("/tmp/aicore_payload.json", "w") as f:
        f.write(json.dumps(payload))
        
    rish_exec(f"cp /tmp/aicore_payload.json {AICORE_PAYLOAD_PATH}")
    rish_exec(f"chmod 644 {AICORE_PAYLOAD_PATH}")
    
    res = rish_exec(f"am broadcast -a {BROADCAST_ACTION} --ei max_tokens 1024 -e payload_path {AICORE_PAYLOAD_PATH}")
    if res.returncode == 0:
        time.sleep(2.0)
        pull_res = rish_exec(f"cat {AICORE_RESPONSE_PATH}")
        if pull_res.returncode == 0 and pull_res.stdout.strip():
            try:
                data = json.loads(pull_res.stdout.strip())
                return data.get("response", None)
            except Exception:
                return pull_res.stdout.strip()
    return None

def execute_with_self_healing(code_snippet):
    snippet_hash = hashlib.md5(code_snippet.encode('utf-8')).hexdigest()
    print(f"[*] Executing managed snippet [{snippet_hash[:8]}]...")
    
    with open(ACTIVE_SCRIPT_PATH, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(code_snippet + "\n")
    os.chmod(ACTIVE_SCRIPT_PATH, 0o755)
    
    # Run script and capture output/stderr
    res = subprocess.run(["bash", ACTIVE_SCRIPT_PATH], capture_output=True, text=True)
    
    if res.returncode == 0:
        print("[+] Execution successful.")
        log_execution(snippet_hash, code_snippet, "SUCCESS")
        return True
    else:
        print(f"[-] Execution failed with exit code {res.returncode}")
        print(f"[-] Stderr:\n{res.stderr.strip()}")
        
        # Attempt self-healing via AICore
        corrected_code = query_native_aicore_correction(res.stderr, code_snippet)
        if corrected_code:
            print("[+] Received patched code from AICore. Re-attempting execution...")
            return execute_with_self_healing(corrected_code)
        else:
            print("[-] Self-healing failed: AICore returned no patch.")
            log_execution(snippet_hash, code_snippet, "FAILED")
            return False

def log_execution(snippet_hash, content, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO execution_log (timestamp, snippet_hash, snippet_content, status)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), snippet_hash, content, status))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_orchestrator.py '<code_snippet>'")
        sys.exit(1)
        
    code = sys.argv[1]
    execute_with_self_healing(code)
