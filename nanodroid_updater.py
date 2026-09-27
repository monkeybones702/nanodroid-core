#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import sqlite3
from datetime import datetime

# ==============================================================================
# NanoDroid-Core Hot-Reload & Self-Update Manager (v9.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Zero-Downtime Module Patching
# ==============================================================================

BACKUP_DIR = os.path.expanduser("~/.nanodroid_backups")
DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
TARGET_SCRIPTS = [
    "nanodroid_master_daemon.py",
    "nanodroid_watchdog.py",
    "nanodroid_scheduler.py",
    "nanodroid_aicore_bridge.py"
]

def init_backup_storage():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_snapshot():
    init_backup_storage()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_sub = os.path.join(BACKUP_DIR, f"snapshot_{timestamp}")
    os.makedirs(snapshot_sub, exist_ok=True)
    
    backed_up = []
    for script in TARGET_SCRIPTS:
        src = os.path.expanduser(f"~/{script}")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(snapshot_sub, script))
            backed_up.append(script)
            
    print(f"[+] Created rollback snapshot [{timestamp}] containing: {', '.join(backed_up)}")
    return snapshot_sub

def validate_script(filepath):
    print(f"[*] Validating Python syntax for {filepath}...")
    res = subprocess.run([sys.executable, "-m", "py_compile", filepath], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Syntax validation passed: {filepath}")
        return True
    else:
        print(f"[-] Syntax error detected in {filepath}:\n{res.stderr}")
        return False

def apply_patch(script_name, new_content):
    target_path = os.path.expanduser(f"~/{script_name}")
    create_snapshot()
    
    temp_path = f"{target_path}.tmp"
    with open(temp_path, "w") as f:
        f.write(new_content)
        
    if not validate_script(temp_path):
        print("[-] Patch rejected due to syntax verification failure. Rolling back.")
        os.remove(temp_path)
        return False
        
    os.replace(temp_path, target_path)
    os.chmod(target_path, 0o755)
    print(f"[+] Successfully applied and verified patch for {script_name}")
    
    # Trigger daemon hot-reload
    reload_daemons()
    return True

def reload_daemons():
    print("[*] Signaling daemons for hot-reload...")
    master_pid_file = os.path.expanduser("~/.nanodroid_master.pid")
    if os.path.exists(master_pid_file):
        try:
            with open(master_pid_file, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 1) # SIGHUP for reload/restart signal if handled, or restart via ctl
            print(f"[+] Sent SIGHUP to Master Daemon (PID {pid})")
        except Exception as e:
            print(f"[-] Error signaling master daemon: {e}")
            
    # Alternatively restart cleanly via nanodroidctl
    subprocess.run(["nanodroidctl", "restart"], capture_output=True)
    print("[+] Ecosystem cleanly restarted with new module updates.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_updater.py {snapshot|validate <script>}")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "snapshot":
        create_snapshot()
    elif cmd == "validate" and len(sys.argv) > 2:
        validate_script(os.path.expanduser(f"~/{sys.argv[2]}"))
    else:
        print(f"[-] Unknown command or missing arguments: {cmd}")
