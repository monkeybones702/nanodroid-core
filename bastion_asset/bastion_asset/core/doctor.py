import os
import json
import subprocess
import sys

REQUIRED_FILES = [
    "pyproject.toml",
    "security_rules.json",
    "bastion_asset/core/hub.py",
    "bastion_asset/core/cli.py",
    "bastion_asset/core/proxy.py",
    "bastion_asset/core/reporter.py",
    "bastion_asset/core/ghscan.py",
    "bastion_asset/core/rules_mgr.py",
    "bastion_asset/core/simulator.py",
    "bastion_asset/core/vault.py",
    "bastion_asset/core/query.py",
    "bastion_asset/daemon/clipboard.py",
    "bastion_asset/daemon/watchdog.py"
]

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE: System Health & Integrity Doctor")
    print("==============================================\n")
    
    checks_passed = 0
    checks_total = 0

    print("[+] Checking required project files...")
    for fpath in REQUIRED_FILES:
        checks_total += 1
        if os.path.exists(fpath):
            print(f"  ✅ [FOUND] {fpath}")
            checks_passed += 1
        else:
            print(f"  ❌ [MISSING] {fpath}")

    print("\n[+] Verifying security_rules.json formatting...")
        checks_total += 1
    try:
        with open("security_rules.json", "r") as f:
            rules = json.load(f)
            if "direct_threats" in rules and "regex_patterns" in rules:
                print("  ✅ [VALID] security_rules.json structure is sound.")
                checks_passed += 1
            else:
                print("  ❌ [INVALID] security_rules.json missing core keys.")
    except Exception as e:
        print(f"  ❌ [ERROR] Could not parse security_rules.json: {e}")

    print("\n[+] Checking active audit log status...")
    checks_total += 1
    if os.path.exists("bastion_audit.log"):
        size = os.path.getsize("bastion_audit.log")
        print(f"  ✅ [ACTIVE] bastion_audit.log present ({size} bytes).")
        checks_passed += 1
    else:
        print("  ⚠️ [NOTICE] bastion_audit.log not created yet (will initialize on first event).")
        checks_passed += 1

    print("\n==============================================")
    print(f" Health Check Complete: {checks_passed}/{checks_total} Checks Passed.")
    print("==============================================")
    input("\nPress Enter to return to hub...")

if __name__ == "__main__":
    main()
