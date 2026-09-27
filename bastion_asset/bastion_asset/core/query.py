import os
import sys

LOG_FILE = "bastion_audit.log"
VAULT_DIR = "bastion_vault"

def search_file(filepath, query):
    matches = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                if query.lower() in line.lower():
                    matches.append((line_num, line.strip()))
    except Exception:
        pass
    return matches

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE: Forensic Log Query Engine")
    print("==============================================")
    
    query = input("\nEnter search term or threat keyword (e.g., BLOCKED, SANITIZED, key): ").strip()
    if not query:
        print("[-] Query cannot be empty.")
        input("\nPress Enter to return...")
        return

    print(f"\n[+] Searching active logs and vaults for: '{query}'...\n")
    total_matches = 0

    # Search active log
    if os.path.exists(LOG_FILE):
        matches = search_file(LOG_FILE, query)
        if matches:
            print(f"📁 Source: Active Log ({LOG_FILE})")
            for line_num, content in matches:
                total_matches += 1
                print(f"  [Line {line_num}] {content}")
            print("-" * 46)

    # Search vault archives
    if os.path.exists(VAULT_DIR):
        for archive in sorted(os.listdir(VAULT_DIR)):
            if archive.endswith(".log"):
                archive_path = os.path.join(VAULT_DIR, archive)
                matches = search_file(archive_path, query)
                if matches:
                    print(f"📁 Source: Vault Archive ({archive})")
                    for line_num, content in matches:
                        total_matches += 1
                        print(f"  [Line {line_num}] {content}")
                    print("-" * 46)

    print(f"\n==============================================")
    print(f" Search Complete. Total Matches Found: {total_matches}")
    print("==============================================")
    input("\nPress Enter to return to hub...")

if __name__ == "__main__":
    main()
