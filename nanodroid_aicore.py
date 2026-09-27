#!/usr/bin/env python3
import sys
import time
import subprocess
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def send_action(payload):
    url = f"{BASE_URL}/ui/execute"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[-] OmniEngine dispatch error: {e}")
        return {"status": "error", "detail": str(e)}

def parse_and_execute_intent(text: str):
    text_lower = text.lower().strip()
    print(f"[*] AICore Intent Parser received text: '{text}'")
    
    # Simple semantic intent mapping aligned with local engine capabilities
    if "home" in text_lower:
        print("[+] Intent matched: System Home keyevent")
        return send_action({"action": "keyevent", "key_code": 3})
    elif "back" in text_lower:
        print("[+] Intent matched: System Back keyevent")
        return send_action({"action": "keyevent", "key_code": 4})
    elif text_lower.startswith("click "):
        target = text[6:].strip().strip("'\"")
        print(f"[+] Intent matched: Self-healing click on '{target}'")
        return send_action({"action": "click", "target_text": target})
    elif text_lower.startswith("launch "):
        pkg = text[7:].strip()
        print(f"[+] Intent matched: Launch package '{pkg}'")
        return send_action({"action": "launch", "package_name": pkg})
    else:
        print("[-] Intent pattern not recognized as direct UI action.")
        return None

def main():
    print("==================================================")
    print("  NanoDroid-Core AICore Event-Driven Bridge v4.3  ")
    print("==================================================")
    print("[*] Monitoring system clipboard for natural language intents...")
    print("[*] Copy text formatted like 'Click Settings' or 'Home' anywhere on device.")
    
    last_clipboard = ""
    
    while True:
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                current_clipboard = res.stdout.strip()
                if current_clipboard and current_clipboard != last_clipboard:
                    # Check if clipboard looks like an intent command rather than raw source code
                    if not current_clipboard.startswith(("#!", "import ", "cat <<", "pkg ", "def ")) and len(current_clipboard) < 80:
                        result = parse_and_execute_intent(current_clipboard)
                        if result:
                            print(f"[+] Execution Result: {json.dumps(result, indent=2)}")
                    last_clipboard = current_clipboard
        except Exception:
            # Suppress transient polling exceptions
            pass
            
        time.sleep(2.0)

if __name__ == "__main__":
    main()
