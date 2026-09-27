import sys
import json
import os

RULES_FILE = "security_rules.json"

# Initialize default rules if missing
if not os.path.exists(RULES_FILE):
    initial_rules = {
        "direct_threats": ["api key", "secret", "environment variables", "ignore all", "developer debug mode", "unrestricted admin"],
        "wrapper_triggers": ["translate", "base64", "decode", "encode", "rot13"]
    }
    with open(RULES_FILE, "w") as f:
        json.dump(initial_rules, f, indent=4)

def load_rules():
    with open(RULES_FILE, "r") as f:
        return json.load(f)

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

def run_self_healing_test():
    print("\n[+] Initializing Self-Healing Security Runner...")
    rules = load_rules()
    
    try:
        with open("payloads.txt", "r") as f:
            lines = f.readlines()
            
        failures_detected = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if ":" in line:
                tag, prompt = line.split(":", 1)
                tag = tag.strip()
                prompt = prompt.strip()
            else:
                tag = "Unknown"
                prompt = line

            lower_prompt = prompt.lower()

            # Check rules
            is_direct = any(kw in lower_prompt for kw in rules["direct_threats"])
            is_wrapped = any(w in lower_prompt for w in rules["wrapper_triggers"]) and any(kw in lower_prompt for kw in ["ignore", "dump", "secret", "override"])
            
            # Basic heuristic for obfuscation detection (e.g. numbers replacing letters like 'ap1' or 's3cr3t')
            is_obfuscated = ("g3t" in lower_prompt or "ap1" in lower_prompt or "s3cr3t" in lower_prompt or "d-u-m-p" in lower_prompt)

            is_threat = is_direct or is_wrapped or is_obfuscated
            
            # If it was marked as a malicious or obfuscated type, but our filter missed it -> FAILURE!
            actual_is_bad = tag in ["Malicious", "Sneaky", "Obfuscated"]
            
            print(f"\n[Test Type: {tag}]")
            print(f"Input: {prompt}")
            
            if actual_is_bad and not is_threat:
                print("Result: [FAILURE] Threat slipped through filter! Triggering auto-patcher...")
                failures_detected += 1
                
                # Auto-patching logic: extract a keyword from the prompt to patch the rules
                new_keyword = prompt.split()[1].lower() if len(prompt.split()) > 1 else "obfuscated"
                if new_keyword not in rules["direct_threats"]:
                    rules["direct_threats"].append(new_keyword)
                    save_rules(rules)
                    print(f"[AUTO-PATCH] Added new rule signature '{new_keyword}' to {RULES_FILE}")
            elif is_threat:
                print("Result: [BLOCKED] Threat vector intercepted.")
            else:
                print("Result: [PASSED] Safe execution allowed.")
                
        print(f"\n[✔] Simulation complete. Total filter bypasses auto-patched: {failures_detected}\n")
        
    except FileNotFoundError:
        print("[-] Error: payloads.txt not found.")

if __name__ == "__main__":
    run_self_healing_test()
