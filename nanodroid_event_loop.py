#!/usr/bin/env python3
import os
import sys
import asyncio
import sqlite3
import json
import time
import subprocess

# ==============================================================================
# NanoDroid-Core Asynchronous Event Dispatcher & Task Engine (v18.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Non-Blocking Concurrency & Event Bus
# ==============================================================================

HOME_DIR = os.path.expanduser("~")
DB_PATH = os.path.join(HOME_DIR, ".nanodroid_state.db")
AGENT_SCRIPT = os.path.join(HOME_DIR, "nanodroid_agent.py")
PID_FILE = os.path.join(HOME_DIR, ".nanodroid_event_loop.pid")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,
            payload TEXT,
            priority INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def poll_task_queue():
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, task_type, payload FROM event_queue WHERE status='PENDING' ORDER BY priority DESC LIMIT 1")
            task = cursor.fetchone()
            
            if task:
                task_id, task_type, payload = task
                cursor.execute("UPDATE event_queue SET status='RUNNING' WHERE id=?", (task_id,))
                conn.commit()
                conn.close()
                
                print(f"[+] EventLoop: Executing task #{task_id} [{task_type}] -> {payload}")
                if task_type == "agent":
                    proc = await asyncio.create_subprocess_exec(
                        "python3", AGENT_SCRIPT, payload,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await proc.communicate()
                    status = "COMPLETED" if proc.returncode == 0 else "FAILED"
                elif task_type == "shell":
                    proc = await asyncio.create_subprocess_shell(
                        payload,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await proc.communicate()
                    status = "COMPLETED" if proc.returncode == 0 else "FAILED"
                else:
                    status = "COMPLETED"
                    
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE event_queue SET status=? WHERE id=?", (status, task_id))
                conn.commit()
                conn.close()
                print(f"[+] EventLoop: Task #{task_id} finished with status: {status}")
            else:
                conn.close()
        except Exception as e:
            print(f"[-] EventLoop Queue Error: {e}")
            
        await asyncio.sleep(2.0)

async def system_telemetry_heartbeat():
    while True:
        try:
            # Read ARM64 CPU thermal / load metrics non-blocking
            load1, load5, load15 = os.getloadavg()
            with open("/proc/meminfo", "r") as f:
                mem_info = f.readlines()
            mem_total = int([x for x in mem_info if "MemTotal" in x][0].split()[1])
            mem_free = int([x for x in mem_info if "MemAvailable" in x][0].split()[1])
            mem_usage_pct = round(((mem_total - mem_free) / mem_total) * 100, 1)
            
            print(f"[HEARTBEAT] CPU Load (1m/5m/15m): {load1}/{load5}/{load15} | RAM Usage: {mem_usage_pct}%")
        except Exception as e:
            pass
        await asyncio.sleep(10.0)

async def main():
    init_db()
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    print("[+] NanoDroid-Core Asynchronous Event Loop ONLINE (v18.0.0)")
    
    await asyncio.gather(
        poll_task_queue(),
        system_telemetry_heartbeat()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        print("\n[+] Event Loop gracefully terminated.")
