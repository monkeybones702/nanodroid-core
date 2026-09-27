#!/usr/bin/env python3
import os
import sys
import sqlite3
import json
import time
datetime_module_available = True
try:
    import datetime
except ImportError:
    datetime_module_available = False

# ==============================================================================
# NanoDroid-Core Self-Upgrading Optimizer Engine (v25.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Adaptive SQLite State & Parameter Evolution
# ==============================================================================

HOME_DIR = os.path.expanduser("~")
DB_PATH = os.path.join(HOME_DIR, ".nanodroid_state.db")
CONFIG_PATH = os.path.join(HOME_DIR, ".nanodroid_config.json")

def init_database():
    """Initializes the local SQLite database for metrics tracking and self-tuning."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Execution history log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal TEXT,
            mode TEXT,
            success INTEGER,
            latency_ms INTEGER,
            timestamp TEXT
        )
    ''')
    
    # Adaptive system parameters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_params (
            key TEXT PRIMARY KEY,
            value REAL,
            confidence REAL,
            updated_at TEXT
        )
    ''')
    
    # Seed default parameters if table is empty
    cursor.execute('SELECT COUNT(*) FROM system_params')
    if cursor.fetchone()[0] == 0:
        defaults = [
            ("retry_attempts", 3.0, 0.8),
            ("ui_scan_delay", 1.0, 0.9),
            ("timeout_limit", 10.0, 0.85),
            ("fuzzy_threshold", 0.75, 0.8)
        ]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.executemany('INSERT INTO system_params (key, value, confidence, updated_at) VALUES (?, ?, ?, ?)', 
                           [(k, v, c, timestamp) for k, v, c in defaults])
        
    conn.commit()
    conn.close()

def log_execution(goal, mode, success, latency_ms):
    """Logs a single execution run into the state database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO execution_logs (goal, mode, success, latency_ms, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (goal, mode, 1 if success else 0, latency_ms, timestamp))
    conn.commit()
    conn.close()

def run_optimization_loop():
    """
    Analyzes historical execution logs, computes success rates and latencies,
    and adaptively mutates system parameters for self-improvement.
    """
    print("[*] Optimizer Loop: Analyzing execution history and telemetry...")
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch recent execution metrics (last 50 runs)
    cursor.execute('SELECT success, latency_ms FROM execution_logs ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    
    if not rows:
        print("[*] No execution history found. Baseline parameters maintained.")
        conn.close()
        return
        
    total_runs = len(rows)
    successes = sum(r[0] for r in rows)
    success_rate = successes / total_runs
    avg_latency = sum(r[1] for r in rows) / total_runs
    
    print(window_status := f"[+] Telemetry Analysis: Success Rate = {success_rate*100:.1f}% | Avg Latency = {avg_latency:.1f}ms")
    
    # Fetch current parameters
    cursor.execute('SELECT key, value, confidence FROM system_params')
    params = {row[0]: {'value': row[1], 'confidence': row[2]} for row in cursor.fetchall()}
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Adaptive Mutation Logic
    if success_rate < 0.8:
        print("[-] Low success rate detected. Mutating parameters to increase resilience...")
        # Increase retry attempts and scan delays to handle UI lag
        if 'retry_attempts' in params:
            params['retry_attempts']['value'] = min(5.0, params['retry_attempts']['value'] + 1.0)
        if 'ui_scan_delay' in params:
            params['ui_scan_delay']['value'] = min(2.5, params['ui_scan_delay']['value'] + 0.25)
    elif success_rate > 0.95 and avg_latency < 500:
        print("[+] High performance detected. Optimizing for speed...")
        # Decrease delays slightly for faster execution
        if 'ui_scan_delay' in params:
            params['ui_scan_delay']['value'] = max(0.5, params['ui_scan_delay']['value'] - 0.1)
            
    # Write updated parameters back to SQLite
    for key, data in params.items():
        cursor.execute('''
            UPDATE system_params SET value = ?, confidence = ?, updated_at = ? WHERE key = ?
        ''', (data['value'], data['confidence'], timestamp, key))
        
    conn.commit()
    
    # Export hot-reloadable JSON configuration for runtime automation scripts
    config_export = {k: v['value'] for k, v in params.items()}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_export, f, indent=2)
        
    print(f"[+] Optimization complete. Updated config exported to: {CONFIG_PATH}")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        # Usage: python3 nanodroid_optimizer.py log "<goal>" "<mode>" <success_0_1> <latency_ms>
        if len(sys.argv) == 6:
            log_execution(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    else:
        run_optimization_loop()
