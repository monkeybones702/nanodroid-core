import os
import zipfile
from datetime import datetime

BACKUP_DIR = "aegis_backups"

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE: Secure Backup & Snapshot Manager")
    print("==============================================")
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = os.path.join(BACKUP_DIR, f"aegis_snapshot_{timestamp}.zip")

    target_files = [
        "security_rules.json",
        "bastion_audit.log",
        "bastion_security_report.json",
        "pyproject.toml"
    ]

    print(f"[+] Creating backup archive: {backup_filename}\n")
    
    archived_count = 0
    with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual critical files if they exist
        for fpath in target_files:
            if os.path.exists(fpath):
                zipf.write(fpath)
                print(f"  ✅ [ADDED] {fpath}")
                archived_count += 1
            else:
                print(f"  ⚠️ [SKIPPED] {fpath} (not found)")

        # Add vault directory if it exists
        if os.path.exists("bastion_vault"):
            vault_files_added = 0
            for root, _, files in os.walk("bastion_vault"):
                for file in files:
                    full_path = os.path.join(root, file)
                    zipf.write(full_path)
                    vault_files_added += 1
            print(f"  ✅ [ADDED] Vault Directory ({vault_files_added} archives)")
            archived_count += vault_files_added

    print(f"\n==============================================")
    print(f" Backup Complete! Total Items Archived: {archived_count}")
    print(f" Location: {os.path.abspath(backup_filename)}")
    print("==============================================")
    input("\nPress Enter to return to hub...")

if __name__ == "__main__":
    main()
