import sys
import re
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def parse_and_dispatch(command_text: str):
    text = command_text.lower().strip()
    print(f"[*] Parsing intent for command: '{command_text}'")

    # Intent Pattern Matching for Zero-Overhead Execution
    if "home" in text:
        payload = {"action": "keyevent", "key_code": 3}
    elif "back" in text:
        payload = {"action": "keyevent", "key_code": 4}
    elif "recents" in text or "recent apps" in text:
        payload = {"action": "keyevent", "key_code": 187}
    elif "scroll" in text:
        payload = {"action": "swipe", "x": 540, "y": 1600, "end_x": 540, "end_y": 600, "duration_ms": 300}
    elif "click" in text or "tap" in text or "press" in text:
        # Extract target entity using regex after action keywords
        match = re.search(r'(?:click|tap|press)\s+(?:on\s+)?["\']?([^"\']+)["\']?', text)
        if match:
            target = match.group(1).strip()
            payload = {"action": "click", "target_text": target}
        else:
            print("[!] Error: Could not extract target text for click action.")
            return
    elif "launch" in text or "open" in text:
        match = re.search(r'(?:launch|open)\s+["\']?([^"\']+)["\']?', text)
        if match:
            app_query = match.group(1).strip()
            # Resolve package via system packages endpoint
            try:
                res = requests.get(f"{BASE_URL}/system/packages", timeout=5)
                if res.status_code == 200:
                    packages = res.json()
                    matches = [p for p in packages if app_query in p.lower()]
                    if matches:
                        payload = {"action": "launch", "package_name": matches[0]}
                        print(f"[+] Resolved package: {matches[0]}")
                    else:
                        print(f"[!] No installed package found matching '{app_query}'.")
                        return
                else:
                    print("[!] Failed to query system packages from engine.")
                    return
            except Exception as e:
                print(f"[!] Connection error to engine: {e}")
                return
        else:
            print("[!] Error: Could not extract application name.")
            return
    else:
        # Fallback to direct shell command execution if prefixed with 'shell'
        if text.startswith("shell "):
            shell_cmd = command_text[6:].strip()
            payload = {"action": "shell", "shell_command": shell_cmd}
        else:
            print(f"[!] Unrecognized intent pattern: '{command_text}'")
            return

    # Dispatch to FastAPI OmniEngine
    try:
        res = requests.post(f"{BASE_URL}/ui/execute", json=payload, timeout=10)
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(f"[!] Execution failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ai_intent_bridge.py \"Open Loop Hero\" or \"Click 'Continue'\"")
        sys.exit(1)
    
    user_prompt = " ".join(sys.argv[1:])
    parse_and_dispatch(user_prompt)
