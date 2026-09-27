import sys
import json
import os

RULES_FILE = "security_rules.json"
CANARY_TOKEN = "CANARY_SECRET_KEY_999"

def load_rules():
    if not os.path.exists(RULES_FILE):
        default_rules = {
            "direct_threats": ["api key", "secret", "environment variables", "ignore all", "developer debug mode", "unrestricted admin", "system override"],
            "wrapper_triggers": ["translate", "base64", "decode", "encode", "rot13"]
        }
        with open(RULES_FILE, "w") as f:
            json.dump(default_rules, f, indent=4)
        return default_rules
    with open(RULES_FILE, "r") as f:
        return json.load(f)

def run_agentguard():
    print("\n==============================================")
    print("   🛡️ AGENTGUARD: Local Security CLI & MVP")
    print("==============================================")
    
    rules = load_rules()
    
    try:
        with open("payloads.txt", "r") as f:
            lines = f.readlines()
            
        passed_count = 0
        blocked_count = 0
        canary_breaches = 0
        
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

            # 1. Canary Token Check (Honeytoken trap)
            is_canary_hit = CANARY_TOKEN.lower() in lower_prompt

            # 2. Rule Match Checks
            is_direct = any(kw in lower_prompt for kw in rules["direct_threats"])
            is_wrapped = any(w in lower_prompt for w in rules["wrapper_triggers"]) and any(kw in lower_prompt for kw in ["ignore", "dump", "secret", "override"])
            is_obfuscated = any(sub in lower_prompt for sub in ["g3t", "ap1", "s3cr3t", "d-u-m-p", "r2v0", "c o n f i g"])

            is_threat = is_direct or is_wrapped or is_obfuscated or is_canary_hit
            actual_is_bad = tag in ["Malicious", "Sneaky", "Obfuscated", "File-Upload", "LLM-Bypass"]
            
            print(f"\n[Type: {tag}] Input: {prompt}")
            
            if is_canary_hit:
                print(f"🚨 [CRITICAL ALERT] Canary token '{CANARY_TOKEN}' triggered! Honeytrap sprang.")
                canary_breaches += 1
                blocked_count += 1
            elif is_threat:
                print("Result: [BLOCKED] Threat vector or evasion wrapper intercepted.")
                blocked_count += 1
            else:
                print("Result: [PASSED] Safe execution allowed.")
                passed_count += 1
                
        print("\n==============================================")
        print(f" [✔] Scan Summary: {blocked_count} Blocked | {passed_count} Passed | {canary_breaches} Canaries Tripped")
        print("==============================================\n")
        
    except FileNotFoundError:
        print("[-] Error: payloads.txt not found. Please ensure your payload suite is initialized.")

if __name__ == "__main__":
    run_agentguard()
