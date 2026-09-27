import os
import json

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

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

def main():
    while True:
        os.system('clear')
        rules = load_rules()
        threats = rules.get("direct_threats", [])
        
        print("==============================================")
        print("   🛡️ AEGISCORE: Dynamic Rule Manager")
        print("==============================================")
        print(f" Active Direct Threat Keywords ({len(threats)}):")
        for i, dt in enumerate(threats, 1):
            print(f"   [{i}] {dt}")
        print("----------------------------------------------")
        print(" Options:")
        print("  [1] Add New Threat Keyword")
        print("  [2] Remove Threat Keyword")
        print("  [3] Return to Main Menu")
        print("==============================================")
        
        choice = input("rules> ").strip()
        
        if choice == "1":
            new_kw = input("\nEnter keyword/phrase to block: ").strip().lower()
            if new_kw:
                if new_kw not in threats:
                    threats.append(new_kw)
                    rules["direct_threats"] = threats
                    save_rules(rules)
                    print(f"\n[+] Successfully added '{new_kw}' to defense filters.")
                else:
                    print("\n[-] Keyword already exists in filters.")
            input("\nPress Enter to continue...")
        elif choice == "2":
            try:
                idx = int(input("\nEnter number of keyword to remove: ").strip()) - 1
                if 0 <= idx < len(threats):
                    removed = threats.pop(idx)
                    rules["direct_threats"] = threats
                    save_rules(rules)
                    print(f"\n[+] Removed '{removed}' from filters.")
                else:
                    print("\n[-] Invalid selection index.")
            except ValueError:
                print("\n[-] Please enter a valid number.")
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            input("\n[-] Invalid option. Press Enter to try again...")

if __name__ == "__main__":
    main()
