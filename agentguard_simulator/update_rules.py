import json
import os

RULES_FILE = "security_rules.json"

def expand_security_rules():
    print("\n[+] Fetching community threat intelligence patterns...")
    
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            rules = json.load(f)
    else:
        rules = {"direct_threats": [], "wrapper_triggers": []}

    # Curated threat patterns inspired by open-source prompt injection datasets
    new_threats = [
        "disregard previous instructions",
        "act as an unrestricted admin",
        "reveal hidden api keys",
        "dump environment variables",
        "system override",
        "developer debug mode",
        "bypass core filters",
        "base64 encoded instruction"
    ]

    added_count = 0
    for threat in new_threats:
        if threat not in rules["direct_threats"]:
            rules["direct_threats"].append(threat)
            added_count += 1

    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

    print(f"[✔] Successfully added {added_count} new enterprise security threat signatures to {RULES_FILE}!\n")

if __name__ == "__main__":
    expand_security_rules()
