#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from datetime import datetime

# ==============================================================================
# NanoDroid-Core Automated Scheduler & Wake-Lock Daemon (v8.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Background Power & Timing Governance
# ==============================================================================

MASTER_DAEMON_SCRIPT = os.path.expanduser("~/nanodroid_master_daemon.py")
PID_FILE = os.path.expanduser("~/.nanodroid_scheduler.pid")
LOG_FILE = os.path.expanduser("~/.nanodroid_scheduler.log")
CYCLE_INTERVAL_SECONDS = 300  # Default: Execute cycle every 5 minutes

def acquire_wakelock():
    print("[*] Requesting Termux wake-lock to prevent CPU suspension in Doze mode...")
    res = subprocess.run(["termux-wake-lock"], capture_output=True, text=True)
    if res.returncode == 0:
        print("[+] Termux wake-lock successfully acquired.")
    else:
        print("[-] Warning: termux-wake-lock failed. Install 'termux-api' package if necessary.")

def release_wakelock():
    print("[*] Releasing Termux wake-lock...")
    subprocess.run(["termux-wake-unlock"], capture_output=True, text=True)
    print("[+] Wake-lock released.")

def trigger_engine_cycle():
    print(f"\n[Scheduler] [{datetime.now().isoformat()}] Triggering scheduled automation cycle...")
    try:
        # Trigger cycle via local FastAPI endpoint or direct script invocation
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8000/api/trigger", method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"[+] Cycle response: {result}")
    except Exception as e:
        print(f"[-] HTTP trigger failed ({e}). Falling back to direct engine execution...")
        subprocess.run(["python3", "-c", "import nanodroid_master_daemon; nanodroid_master_daemon.execute_engine_cycle()"])

def run_scheduler_loop(interval=CYCLE_INTERVAL_SECONDS):
    acquire_wakelock()
    print(f"[*] NanoDroid Scheduler active. Running cycle every {interval} seconds.")
    try:
        while True:
            trigger_engine_cycle()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[*] Scheduler interrupted by user.")
    finally:
        release_wakelock()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_scheduler.py {start|stop|run}")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "run":
        run_scheduler_loop()
    elif cmd == "start":
        if os.path.exists(PID_FILE):
            print("[!] Scheduler is already running.")
            sys.exit(0)
        print("[*] Starting Scheduler daemon in background...")
        with open(LOG_FILE, "a") as log:
            p = subprocess.Popen([sys.executable, __file__, "run"], stdout=log, stderr=log)
            with open(PID_FILE, "w") as f:
                f.write(str(p.pid))
        print(f"[+] Scheduler background daemon active (PID {p.pid})")
    elif cmd == "stop":
        if not os.path.exists(PID_FILE):
            print("[-] Scheduler daemon is not running.")
            sys.exit(0)
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 15)
            print(f"[+] Terminated Scheduler daemon (PID {pid})")
        except Exception as e:
            print(f"[-] Error stopping scheduler: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        release_wakelock()
    else:
        print(f"[-] Unknown command: {cmd}")
