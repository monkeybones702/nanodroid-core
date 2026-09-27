import os
import shutil
from datetime import datetime

LOG_FILE = "bastion_audit.log"
VAULT_DIR = "bastion_vault"

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE: Secure Log Vault & Archiver")
    print("==============================================")
    
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        print("[-] No active audit logs found to archive.")
        input("\nPress Enter to return...")
        return

    os.makedirs(VAULT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(VAULT_DIR, f"audit_archive_{timestamp}.log")

    # Copy log to vault and clear active log
    shutil.copy2(LOG_FILE, archive_path)
    open(LOG_FILE, "w").close()

    print(f"[+] Active audit logs successfully secured and vaulted!")
    print(f"    -> Destination: {archive_path}")
    
    archives = os.listdir(VAULT_DIR)
    print(f"\n[+] Total Vault Archives stored: {len(archives)}")
    input("\nPress Enter to return to hub...")

if __name__ == "__main__":
    main()
