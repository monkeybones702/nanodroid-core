#!/usr/bin/env python3
import time
import subprocess
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def send_action(payload):
    url = f"{BASE_URL}/ui/execute"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def parse_and_dispatch(text: str):
    text_lower = text.lower().strip()
    print(f"[*] Intercepted Clipboard Event: '{text}'")

    if text_lower == "home":
        print("[+] Triggering System Home keyevent...")
        return send_action({"action": "keyevent", "key_code": 3})
    elif text_lower == "back":
        print("[+] Triggering System Back keyevent...")
        return send_action({"action": "keyevent", "key_code": 4})
    elif text_lower.startswith("click "):
        target = text[6:].strip().strip("'\"")
        print(f"[+] Triggering self-healing click on '{target}'...")
        return send_action({"action": "click", "target_text": target})
    elif text_lower.startswith("launch "):
        pkg = text[7:].strip()
        print(f"[+] Launching package '{pkg}'...")
        return send_action({"action": "launch", "package_name": pkg})
    else:
        print("[-] Clipboard content does not match a registered NanoDroid trigger pattern.")
        return None

def main():
    print("==================================================")
    print("  NanoDroid-Core Event Listener Daemon Active     ")
    print("==================================================")
    print("[*] Monitoring system clipboard via Termux-API...")
    
    last_clipboard = ""
    while True:
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                current_clipboard = res.stdout.strip()
                if current_clipboard and current_clipboard != last_clipboard:
                    # Ignore script blocks or long text dumps
                    if not current_clipboard.startswith(("#!", "import ", "cat <<", "pkg ")) and len(current_clipboard) < 60:
                        result = parse_and_dispatch(current_clipboard)
                        if result:
                            print(f"[+] Dispatch Result: {json.dumps(result, indent=2)}")
                    last_clipboard = current_clipboard
        except Exception:
            # Suppress transient polling exceptions
            pass
        time.sleep(2.0)

if __name__ == "__main__":
    main()
