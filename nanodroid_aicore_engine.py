#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def send_request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[-] OmniEngine communication error: {e}")
        sys.exit(1)

def translate_intent_to_macro(prompt: str) -> dict:
    prompt_lower = prompt.lower().strip()
    steps = []
    macro_name = f"AICore Intent: {prompt}"

    print(f"[*] AICore Engine analyzing prompt: '{prompt}'...")

    # Dynamic intent breakdown optimized for local device execution
    if "open" in prompt_lower or "launch" in prompt_lower:
        # Extract target app name
        for word in ["open", "launch"]:
            if word in prompt_lower:
                parts = prompt_lower.split(word, 1)
                if len(parts) > 1:
                    target = parts[1].strip().strip("'\"")
                    steps.append({"action": "keyevent", "key_code": 3, "wait_seconds": 1.0})
                    steps.append({"action": "click", "target_text": target, "wait_seconds": 1.5})
                    break
    elif "click" in prompt_lower or "tap" in prompt_lower:
        for word in ["click", "tap"]:
            if word in prompt_lower:
                parts = prompt_lower.split(word, 1)
                if len(parts) > 1:
                    target = parts[1].strip().strip("'\"")
                    steps.append({"action": "click", "target_text": target, "wait_seconds": 1.0})
                    break
    elif "home" in prompt_lower:
        steps.append({"action": "keyevent", "key_code": 3, "wait_seconds": 0.5})
    elif "back" in prompt_lower:
        steps.append({"action": "keyevent", "key_code": 4, "wait_seconds": 0.5})
    else:
        # Fallback: treat raw string as general text search/click target
        steps.append({"action": "click", "target_text": prompt.strip(), "wait_seconds": 1.0})

    return {
        "macro_name": macro_name,
        "steps": steps
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_aicore_engine.py \"Your natural language command here\"")
        print("Example: python3 nanodroid_aicore_engine.py \"Open Settings\"")
        sys.exit(1)

    natural_prompt = " ".join(sys.argv[1:])
    macro_payload = translate_intent_to_macro(natural_prompt)

    if not macro_payload["steps"]:
        print("[-] Could not resolve intent into executable steps.")
        sys.exit(1)

    print(f"[+] Generated Macro Schema:\n{json.dumps(macro_payload, indent=2)}")
    print("[*] Dispatching macro to OmniEngine daemon...")
    
    result = send_request("/macro/execute", method="POST", data=macro_payload)
    print(f"[+] Execution Response:\n{json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
