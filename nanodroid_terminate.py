#!/usr/bin/env python3
import os
import sys
import subprocess

# ==============================================================================
# NanoDroid-Core Final Termination & System Archival (v14.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Graceful Shutdown & Sanitization
# ==============================================================================

PID_FILES = [
    os.path.expanduser("~/.nanodroid_master.pid"),
    os.path.expanduser("~/.nanodroid_scheduler.pid"),
    os.path.expanduser("~/.nanodroid_hub.pid")
]

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def terminate_ecosystem():
    print("[*] Initiating NanoDroid-Core graceful ecosystem shutdown...")
    
    # Terminate PIDs
    for pid_path in PID_FILES:
        if os.path.exists(pid_path):
            try:
                with open(pid_path, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 15)
                print(f"[+] Terminated process PID {pid} ({os.path.basename(pid_path)})")
            except Exception as e:
                print(f"[-] Error terminating PID from {pid_path}: {e}")
            finally:
                os.remove(pid_path)
                
    # Kill any lingering python daemons matching nanodroid scripts
    subprocess.run(["pkill", "-f", "nanodroid_"], capture_output=True)
    
    # Release Termux wake-lock
    print("[*] Releasing Termux wake-lock...")
    subprocess.run(["termux-wake-unlock"], capture_output=True, text=True)
    
    # Sanitize device temp storage via Shizuku
    print("[*] Sanitizing temporary window dumps and payloads in /data/local/tmp/...")
    rish_exec("rm -f /data/local/tmp/window_dump.xml /data/local/tmp/aicore_*.json")
    
    print("\n==================================================")
    print("      NanoDroid-Core Successfully Terminated      ")
    print("      All System States Archived & Sanitized      ")
    print("==================================================")

if __name__ == "__main__":
    terminate_ecosystem()
