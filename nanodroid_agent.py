#!/usr/bin/env python3
import os
import sys
import json
import time
import subprocess

# ==============================================================================
# NanoDroid-Core Autonomous AI Goal-Driven Agent & Planner (v16.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Natural Language Goal Decomposition
# ==============================================================================

AICORE_PAYLOAD_PATH = "/data/local/tmp/aicore_payload.json"
AICORE_RESPONSE_PATH = "/data/local/tmp/aicore_response.json"
BROADCAST_ACTION = "com.google.android.aicore.GENERATE_PROMPT"
NAVIGATOR_SCRIPT = os.path.expanduser("~/nanodroid_ui_navigator.py")

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def query_aicore_planner(goal):
    print(f"[*] Dispatching goal to native Gemini Nano AICore: '{goal}'")
    prompt = (
        f"You are an Android automation planner. Given the user goal: '{goal}', "
        "decompose it into a sequence of JSON action steps. Each step must have a 'action' "
        "('tap', 'type', 'wait', 'shell') and arguments ('query' for tap/type, 'text' for type, "
        "'seconds' for wait, 'command' for shell). Return ONLY a valid JSON array of objects, with no markdown formatting."
    )
    
    payload = {"prompt": prompt, "temperature": 0.1, "max_tokens": 512}
    with open("/tmp/aicore_payload.json", "w") as f:
        f.write(json.dumps(payload))
        
    rish_exec(f"cp /tmp/aicore_payload.json {AICORE_PAYLOAD_PATH}")
    rish_exec(f"chmod 644 {AICORE_PAYLOAD_PATH}")
    
    res = rish_exec(f"am broadcast -a {BROADCAST_ACTION} --ei max_tokens 512 -e payload_path {AICORE_PAYLOAD_PATH}")
    if res.returncode == 0:
        time.sleep(2.5)
        pull_res = rish_exec(f"cat {AICORE_RESPONSE_PATH}")
        if pull_res.returncode == 0 and pull_res.stdout.strip():
            raw_output = pull_res.stdout.strip()
            # Clean markdown code blocks if present
            if raw_output.startswith("```"):
                raw_output = raw_output.split("```")[1]
                if raw_output.startswith("json"):
                    raw_output = raw_output[4:]
            try:
                return json.loads(raw_output.strip())
            except Exception as e:
                print(f"[-] Failed to parse JSON plan from AICore: {e}\nRaw: {raw_output}")
    return None

def execute_agent_plan(goal):
    plan = query_aicore_planner(goal)
    if not plan or not isinstance(plan, list):
        print("[-] Agent planner failed to generate a valid execution plan.")
        return False
        
    print(f"[+] Received execution plan with {len(plan)} steps:")
    for idx, step in enumerate(plan):
        print(f"    {idx+1}. Action: {step.get('action')} | Details: {step}")
        
    for idx, step in enumerate(plan):
        action = step.get("action")
        print(f"\n[*] Executing Step {idx+1}/{len(plan)}: {action}")
        
        if action == "tap":
            query = step.get("query")
            subprocess.run(["python3", NAVIGATOR_SCRIPT, "tap", query])
        elif action == "type":
            query = step.get("query")
            text = step.get("text")
            subprocess.run(["python3", NAVIGATOR_SCRIPT, "type", query, text])
        elif action == "wait":
            secs = float(step.get("seconds", 1.0))
            time.sleep(secs)
        elif action == "shell":
            cmd = step.get("command")
            rish_exec(cmd)
        else:
            print(f"[-] Unknown action type: {action}")
        time.sleep(1.0)
        
    print("[+] Autonomous agent goal execution completed successfully.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_agent.py '<natural_language_goal>'")
        sys.exit(1)
        
    goal_str = sys.argv[1]
    execute_agent_plan(goal_str)
