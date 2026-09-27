#!/usr/bin/env python3
import os
import sys
import sqlite3
import time
import subprocess
import threading
from datetime import datetime

# ==============================================================================
# NanoDroid-Core Priority Job Queue & Task Dispatcher (v12.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Persistent Asynchronous Job Engine
# ==============================================================================

DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
ORCHESTRATOR_SCRIPT = os.path.expanduser("~/nanodroid_orchestrator.py")

def init_queue_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            priority INTEGER DEFAULT 5,
            task_type TEXT,
            payload TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def enqueue_task(task_type, payload, priority=5):
    init_queue_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO task_queue (priority, task_type, payload, status, created_at, updated_at)
        VALUES (?, ?, ?, 'PENDING', ?, ?)
    ''', (priority, task_type, payload, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    print(f"[+] Enqueued task #{task_id} [{task_type}] with priority {priority}")
    return task_id

def process_queue_worker():
    init_queue_table()
    print("[*] Task Queue worker background loop started.")
    while True:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Fetch highest priority, oldest pending task
        cursor.execute('''
            SELECT id, task_type, payload FROM task_queue 
            WHERE status = 'PENDING' 
            ORDER BY priority ASC, id ASC LIMIT 1
        ''')
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            time.sleep(3.0)
            continue
            
        task_id, task_type, payload = row
        
        # Mark as RUNNING atomically
        cursor.execute('''
            UPDATE task_queue SET status = 'RUNNING', updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()
        
        print(f"[+] Executing queued task #{task_id} ({task_type})...")
        
        success = False
        try:
            if task_type == "snippet":
                res = subprocess.run(["python3", ORCHESTRATOR_SCRIPT, payload], capture_output=True, text=True)
                success = (res.returncode == 0)
            elif task_type == "shell":
                res = subprocess.run(["bash", "-c", payload], capture_output=True, text=True)
                success = (res.returncode == 0)
            else:
                print(f"[-] Unknown task type: {task_type}")
        except Exception as e:
            print(f"[-] Task execution exception: {e}")
            
        # Update final status
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        final_status = 'COMPLETED' if success else 'FAILED'
        cursor.execute('''
            UPDATE task_queue SET status = ?, updated_at = ? WHERE id = ?
        ''', (final_status, datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()
        print(f"[+] Task #{task_id} finished with status: {final_status}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_queue.py {worker|add <type> <payload> [priority]}")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "worker":
        process_queue_worker()
    elif cmd == "add" and len(sys.argv) > 3:
        t_type = sys.argv[2]
        t_payload = sys.argv[3]
        t_priority = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        enqueue_task(t_type, t_payload, t_priority)
    else:
        print("[-] Invalid arguments.")
        sys.exit(1)
