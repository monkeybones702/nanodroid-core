import os
import time
import subprocess
import sys

LOG_FILE = "bastion_audit.log"

def send_termux_notification(title, message):
    try:
        subprocess.run(["termux-notification", "--title", title, "--content", message, "--priority", "high"], check=False)
    except Exception:
        pass

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE: Real-Time Security Watchdog")
    print("==============================================\n")
    print(f"[+] Monitoring '{LOG_FILE}' for live threats... Press Ctrl+C to stop.\n")
    
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    try:
        with open(LOG_FILE, "r") as f:
            # Move to the end of the file to tail new entries
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                clean_line = line.strip()
                if "BLOCKED" in clean_line:
                    print(f"🚨 [ALERT DETECTED]: {clean_line}")
                    send_termux_notification("AegisCore Security Alert", "Threat Blocked by Gateway Proxy!")
                elif "SANITIZED" in clean_line:
                    print(f"⚠️ [LEAK REDACTED]: {clean_line}")
                    send_termux_notification("AegisCore DLP Notice", "Secret / API Key Sanitized!")
                elif "PASSED" in clean_line:
                    print(f"🟢 [PASSED]: {clean_line}")
    except KeyboardInterrupt:
        print("\n[+] Watchdog daemon stopped.")

if __name__ == "__main__":
    main()
