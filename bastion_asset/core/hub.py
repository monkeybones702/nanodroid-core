import os
import sys
import subprocess

LOG_FILE = "bastion_audit.log"
REPORT_FILE = "bastion_security_report.json"

def get_log_stats():
    if not os.path.exists(LOG_FILE):
        return 0, 0, 0
    blocked = 0
    sanitized = 0
    passed = 0
    with open(LOG_FILE, "r") as f:
        for line in f:
            if "BLOCKED" in line:
                blocked += 1
            elif "SANITIZED" in line:
                sanitized += 1
            elif "PASSED" in line:
                passed += 1
    return blocked, sanitized, passed

def main():
    while True:
        os.system('clear')
        blocked, sanitized, passed = get_log_stats()
        print("==============================================")
        print("   🛡️ AEGISCORE CITADEL: Master Control Hub")
        print("==============================================")
        print(f" [📊 Live Audit Stats]")
        print(f"   - Blocked Threats : {blocked}")
        print(f"   - Sanitized Leaks : {sanitized}")
        print(f"   - Passed Requests : {passed}")
        print("----------------------------------------------")
        print(" Select an option:")
        print("  [1] Run Security Payload Scan (aegis-cli)")
        print("  [2] Start Live Gateway Proxy (aegis-proxy)")
        print("  [3] View Recent Audit Logs")
        print("  [4] Launch Nanodroid Clipboard Daemon / Package Manager")
        print("  [5] Run System Diagnostics & Pytest Suite")
        print("  [6] Run Repository Code Security Scan")
        print("  [7] Manage Security Threat Rules (aegis-rules)")
        print("  [8] Start Real-Time Watchdog Daemon")
        print("  [9] Run Threat Simulation & Integration Test")
        print("  [10] Export JSON Security Threat Report")
        print("  [11] Secure & Vault Audit Logs (aegis-vault)")
        print("  [12] Forensic Log Query Engine (aegis-query)")
        print("  [13] Run System Health & Integrity Doctor (aegis-doctor)")
        print("  [14] Export Secure Backup Snapshot (aegis-backup)")
        print("  [15] Threat Analytics & Metrics Dashboard (aegis-metrics)")
        print("  [16] Proxy Firewall & Access Control (aegis-firewall)")
        print("  [17] Webhook & Incident Notifier (aegis-notify)")
        print("  [18] Exit Control Hub")
        print("==============================================")
        
        choice = input("aegis-hub> ").strip()
        
        if choice == "1":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.cli"])
            input("\nPress Enter to return to hub...")
        elif choice == "2":
            print("\n[+] Starting proxy... Press Ctrl+C to return to hub.")
            try:
                subprocess.run([sys.executable, "-m", "bastion_asset.core.proxy"])
            except KeyboardInterrupt:
                pass
        elif choice == "3":
            print("\n--- Recent Audit Log Entries ---")
            if os.path.exists(LOG_FILE):
                subprocess.run(["tail", "-n", "15", LOG_FILE])
            else:
                print("[-] No audit logs found yet.")
            input("\nPress Enter to return to hub...")
        elif choice == "4":
            print("\n--- Nanodroid Clipboard Daemon & Package Manager ---")
            inp = input("Enter command (leave blank to launch nanodroid daemon, or type 'pip install ...'): ").strip()
            if inp.startswith("pip install") or inp.startswith("pip "):
                print(f"\n[+] Executing: {inp}")
                subprocess.run(inp, shell=True)
                print("\n[+] Package installation complete. Automatically restarting Aegis Hub...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("\n[+] Launching continuous nanodroid clipboard daemon... Press Ctrl+C to return.")
                try:
                    subprocess.run([sys.executable, "-m", "bastion_asset.daemon.clipboard"])
                except KeyboardInterrupt:
                    pass
        elif choice == "5":
            print("\n[+] Running automated test suite (pytest)...")
            subprocess.run([sys.executable, "-m", "pytest", "-v", "bastion_asset"])
            input("\nPress Enter to return to hub...")
        elif choice == "6":
            print("\n[+] Running repository code security scan...")
            subprocess.run([sys.executable, "-m", "bastion_asset.core.ghscan", "."])
            input("\nPress Enter to return to hub...")
        elif choice == "7":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.rules_mgr"])
        elif choice == "8":
            print("\n[+] Starting real-time watchdog... Press Ctrl+C to stop.")
            try:
                subprocess.run([sys.executable, "-m", "bastion_asset.daemon.watchdog"])
            except KeyboardInterrupt:
                pass
        elif choice == "9":
            print("\n[+] Running integration threat simulation...")
            subprocess.run([sys.executable, "-m", "bastion_asset.core.simulator"])
            input("\nPress Enter to return to hub...")
        elif choice == "10":
            print("\n[+] Generating security incident report...")
            subprocess.run([sys.executable, "-m", "bastion_asset.core.reporter"])
            if os.path.exists(REPORT_FILE):
                print(f"[+] Report saved to {REPORT_FILE}")
            input("\nPress Enter to return to hub...")
        elif choice == "11":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.vault"])
        elif choice == "12":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.query"])
        elif choice == "13":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.doctor"])
        elif choice == "14":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.backup"])
        elif choice == "15":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.metrics"])
        elif choice == "16":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.firewall"])
        elif choice == "17":
            subprocess.run([sys.executable, "-m", "bastion_asset.core.notifier"])
        elif choice == "18":
            print("\n[+] Exiting AegisCore Citadel. Stay secure!")
            break
        else:
            input("\n[-] Invalid option. Press Enter to try again...")

if __name__ == "__main__":
    main()
