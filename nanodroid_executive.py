#!/usr/bin/env python3
import os
import sys
import json
import time
import subprocess

# ==============================================================================
# NanoDroid-Core Executive Autonomous Coordinator (v22.1.0)
# Target: Samsung Galaxy A16 (ARM64) | Sandbox-Safe Path Resolution
# ==============================================================================

HOME_DIR = os.path.expanduser("~")
LOCAL_PAYLOAD = os.path.join(HOME_DIR, ".nanodroid_aicore_exec.json")
AICORE_PAYLOAD = "/data/local/tmp/aicore_executive_payload.json"
AICORE_RESPONSE = "/data/local/tmp/aicore_executive_response.json"
BROADCAST_ACTION = "com.google.android.aicore.GENERATE_PROMPT"

BRIDGE_SCRIPT = os.path.join(HOME_DIR, "nanodroid_bridge.py")

def rish_exec(cmd):
    res = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)
    return res.stdout.strip()

def query_native_aicore(goal):
    print(f"[*] Dispatching goal to native on-device Gemini Nano AICore: '{goal}'")
    prompt = (
        f"You are the executive planner for NanoDroid-Core on a Samsung Galaxy A16. "
        f"Goal: '{goal}'. Classify this goal into one of three execution modes: "
        "1. 'intent': for direct Android system settings or package launches (provide 'command'). "
        "2. 'bridge': for copy-pasting code or interacting between Gemini and Termux (provide 'payload'). "
        "3. 'shell': for direct Termux shell execution (provide 'command'). "
        "Return ONLY a valid JSON object with keys 'mode' and 'target' (no markdown, no preamble)."
    )
    
    payload = {"prompt": prompt, "temperature": 0.1, "max_tokens": 256}
    try:
        with open(LOCAL_PAYLOAD, "w") as f:
            json.dump(payload, f)
    except Exception as e:
        print(f"[-] Failed to write local payload: {e}")
        return None
        
    rish_exec(f"cp {LOCAL_PAYLOAD} {AICORE_PAYLOAD}")
    rish_exec(f"chmod 644 {AICORE_PAYLOAD}")
    
    res = rish_exec(f"am broadcast -a {BROADCAST_ACTION} --ei max_tokens 256 -e payload_path {AICORE_PAYLOAD}")
    if res.returncode == 0:
        time.sleep(1.5)
        pull = rish_exec(f"cat {AICORE_RESPONSE}")
        if pull:
            raw = pull.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            try:
                return json.loads(raw.strip())
            except Exception as e:
                print(f"[-] AICore JSON parse error: {e}\nRaw: {raw}")
    return None

def execute_goal(goal):
    print(f"\n==================================================")
    print(f"[EXECUTIVE] Processing Goal: '{goal}'")
    print(f"==================================================")
    
    plan = query_native_aicore(goal)
    if not plan:
        print("[*] Fallback: Direct intent shortcut routing activated.")
        goal_lower = goal.lower()
        if "display" in goal_lower or "brightness" in goal_lower:
            plan = {"mode": "intent", "target": "am start -a android.settings.DISPLAY_SETTINGS"}
        elif "wifi" in goal_lower:
            plan = {"mode": "intent", "target": "am start -a android.settings.WIFI_SETTINGS"}
        else:
            plan = {"mode": "intent", "target": "am start -a android.settings.SETTINGS"}
            
    print(f"[+] Execution Plan Decoded: {plan}")
    mode = plan.get("mode")
    target = plan.get("target")
    
    if mode == "intent" or mode == "shell":
        print(f"[*] Executing via System Intent/Shell: {target}")
        rish_exec(target)
        print("[+] Execution complete.")
    elif mode == "bridge":
        print(f"[*] Executing via Bidirectional Context Bridge...")
        subprocess.run(["python3", BRIDGE_SCRIPT, target])
    else:
        print(f"[-] Unknown execution mode: {mode}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_executive.py '<natural_language_goal>'")
        sys.exit(1)
    execute_goal(" ".join(sys.argv[1:]))
