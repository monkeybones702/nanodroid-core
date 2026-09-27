#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import sqlite3
from datetime import datetime

# ==============================================================================
# NanoDroid-Core Self-Healing Watchdog & CLI Manager (v7.0.0)
# Target: Samsung Galaxy A16 (ARM64) | System Governance & Recovery
# ==============================================================================

MASTER_DAEMON_SCRIPT = os.path.expanduser("~/nanodroid_master_daemon.py")
PID_FILE = os.path.expanduser("~/.nanodroid_master.pid")
LOG_FILE = os.path.expanduser("~/.nanodroid_master.log")
DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
DUMP_PATH = "/data/local/tmp/window_dump.xml"

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def is_daemon_running():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        res = subprocess.run(["ps", "-p", str(pid)], capture_output=True, text=True)
        return str(pid) in res.stdout
    except Exception:
        return False

def start_daemon():
    if is_daemon_running():
        print("[!] Master Daemon is already running.")
        return
    print("[*] Starting Master AICore Daemon under Watchdog supervision...")
    with open(LOG_FILE, "a") as log:
        p = subprocess.Popen(["python3", MASTER_DAEMON_SCRIPT], stdout=log, stderr=log)
        with open(PID_FILE, "w") as f:
            f.write(str(p.pid))
    print(f"[+] Master Daemon started with PID {p.pid}")

def stop_daemon():
    if not is_daemon_running():
        print("[-] Master Daemon is not running.")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, 15)
        print(f"[+] Terminated Master Daemon (PID {pid})")
    except Exception as e:
        print(f"[-] Error stopping daemon: {e}")
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def system_health_check():
    print("==================================================")
    print("      NanoDroid System Health & Telemetry        ")
    print("==================================================")
    
    # Check Daemon Status
    running = is_daemon_running()
    print(f" * Master Daemon Status: {'ONLINE' if running else 'OFFLINE'}")
    if running:
        with open(PID_FILE, "r") as f:
            print(f" * Daemon PID: {f.read().strip()}")

    # Check Database Records
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM execution_log")
            count = cursor.fetchone()[0]
            print(f" * SQLite Execution Records: {count}")
            
            cursor.execute("SELECT timestamp, status FROM execution_log ORDER BY id DESC LIMIT 1")
            last = cursor.fetchone()
            if last:
                print(f" * Last Execution: {last[0]} [{last[1]}]")
            conn.close()
        except Exception as e:
            print(f"[-] Database inspection error: {e}")
    else:
        print(" * SQLite Database: Not initialized yet.")

    # Check Galaxy A16 System Load via Shizuku
    mem_res = rish_exec("free -m")
    if mem_res.returncode == 0:
        print("\n--- Android RAM Status (Shizuku) ---")
        print(mem_res.stdout.strip())

    thermal_res = rish_exec("cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null")
    if thermal_res.returncode == 0 and thermal_res.stdout.strip():
        print("\n--- Thermal Sensors ---")
        temps = [int(t) // 1000 for t in thermal_res.stdout.strip().split() if t.isdigit()]
        if temps:
            print(f" * Average CPU Temperature: {sum(temps) // len(temps)}°C")

def cleanup_stale_files():
    print("[*] Purging stale XML dumps and temporary buffers...")
    rish_exec(f"rm -f {DUMP_PATH} /data/local/tmp/aicore_*.json")
    print("[+] System temporary storage sanitized.")

def watch_loop(interval=30):
    print(f"[*] NanoDroid Watchdog active. Monitoring daemon every {interval}s...")
    try:
        while True:
            if not is_daemon_running():
                print(f"[!] [{datetime.now().isoformat()}] Daemon dropped! Auto-restarting...")
                start_daemon()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[*] Watchdog loop terminated by user.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_watchdog.py {start|stop|restart|status|watch|clean}")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "start":
        start_daemon()
    elif cmd == "stop":
        stop_daemon()
    elif cmd == "restart":
        stop_daemon()
        time.sleep(1)
        start_daemon()
    elif cmd == "status":
        system_health_check()
    elif cmd == "clean":
        cleanup_stale_files()
    elif cmd == "watch":
        watch_loop()
    else:
        print(f"[-] Unknown command: {cmd}")
