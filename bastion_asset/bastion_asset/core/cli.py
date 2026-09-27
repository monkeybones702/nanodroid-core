import os
import json
import re
import sys

RULES_FILE = "security_rules.json"

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {
        "direct_threats": ["api key", "secret", "environment variables", "ignore all"],
        "regex_patterns": ["(?i)ignore.*previous.*instructions"],
        "wrapper_triggers": ["translate", "base64", "decode"]
    }

def evaluate_prompt(prompt, rules):
    lower_prompt = prompt.lower()
    is_direct = any(kw in lower_prompt for kw in rules.get("direct_threats", []))
    is_regex_match = any(re.search(pat, prompt) for pat in rules.get("regex_patterns", []))
    
    if is_direct or is_regex_match:
        print(f"🚨 [THREAT DETECTED]: Policy violation found in payload!")
        if is_direct:
            print(f"   - Triggered direct threat keyword.")
        if is_regex_match:
            print(f"   - Triggered strict regex pattern match.")
    else:
        print(f"✅ [CLEAN]: Payload passed security rules check.")

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE CLI: Security Payload Scanner")
    print("==============================================")
    rules = load_rules()
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        evaluate_prompt(prompt, rules)
    else:
        while True:
            try:
                prompt = input("\nEnter prompt to scan (or 'exit'): ").strip()
                if prompt.lower() in ['exit', 'quit']:
                    break
                if not prompt:
                    continue
                evaluate_prompt(prompt, rules)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting CLI scanner.")
                break

if __name__ == "__main__":
    main()
