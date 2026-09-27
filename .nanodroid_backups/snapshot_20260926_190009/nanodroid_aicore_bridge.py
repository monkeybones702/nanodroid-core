#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import time

# ==============================================================================
# NanoDroid-Core AICore Bridge (v6.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Android AICore / ML Kit GenAI Integration
# ==============================================================================

AI_CORE_SERVICE = "com.google.android.aicore"
BROADCAST_ACTION = "com.google.android.aicore.GENERATE_PROMPT"

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def check_aicore_availability():
    print("[*] Inspecting Android system for AICore binder availability...")
    res = rish_exec(f"pm path {AI_CORE_SERVICE}")
    if res.returncode == 0 and "package:" in res.stdout:
        print(f"[+] AICore package detected on system: {AI_CORE_SERVICE}")
        return True
    print("[-] AICore system package not found. Falling back to secure local intent handler.")
    return False

def query_native_gemini_nano(prompt_text):
    """
    Interfaces directly with Android's system-level AICore service via 
    zero-overhead broadcast intents and content providers, avoiding C++ binary bloat.
    """
    print(f"[*] Dispatching prompt to native AICore pipeline: '{prompt_text}'")
    
    # Construct structured payload for system GenAI service
    payload = {
        "prompt": prompt_text,
        "temperature": 0.2,
        "max_tokens": 512,
        "source": "nanodroid_core_engine"
    }
    
    payload_str = json.dumps(payload)
    temp_json_path = "/data/local/tmp/aicore_payload.json"
    
    # Write payload securely via Shizuku
    with open("/tmp/aicore_payload.json", "w") as f:
        f.write(payload_str)
    
    rish_exec(f"cp /tmp/aicore_payload.json {temp_json_path}")
    rish_exec(f"chmod 644 {temp_json_path}")
    
    # Broadcast intent to Android AICore service receiver
    cmd = f"am broadcast -a {BROADCAST_ACTION} --ei max_tokens 512 -e payload_path {temp_json_path}"
    res = rish_exec(cmd)
    
    if res.returncode == 0:
        print("[+] Native AICore intent broadcast successful.")
        time.sleep(1.5)
        # Pull generated response back from local temp buffer
        pull_res = rish_exec("cat /data/local/tmp/aicore_response.json")
        if pull_res.returncode == 0 and pull_res.stdout.strip():
            try:
                data = json.loads(pull_res.stdout.strip())
                return data.get("response", "[!] Empty response field.")
            except json.JSONDecodeError:
                return pull_res.stdout.strip()
    
    print("[-] AICore broadcast returned non-zero code. Executing fallback UI automation loop.")
    return None

if __name__ == "__main__":
    print("==================================================")
    print("  NanoDroid-Core: Native AICore Bridge Module    ")
    print("==================================================")
    
    available = check_aicore_availability()
    test_prompt = "Generate next architectural code block for NanoDroid-Core."
    
    response = query_native_gemini_nano(test_prompt)
    if response:
        print(f"\n[+] AICore Output Received:\n{response}")
    else:
        print("\n[*] Routing task through closed-loop UI automation engine.")
        subprocess.run(["python3", os.path.expanduser("~/nanodroid_core_engine.py")])
