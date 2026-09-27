#!/usr/bin/env python3
import os
import sys
import time
import json
import sqlite3
import asyncio
import subprocess
import threading
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

# ==============================================================================
# NanoDroid-Core WebSocket Telemetry Hub & Job Manager (v12.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Real-Time Reactive Dashboard & Queue
# ==============================================================================

DB_PATH = os.path.expanduser("~/.nanodroid_state.db")
LOG_FILE = os.path.expanduser("~/.nanodroid_master.log")
QUEUE_SCRIPT = os.path.expanduser("~/.nanodroid_queue.py")

app = FastAPI(title="NanoDroid WebSocket Telemetry & Queue Hub", version="12.0.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                pass

manager = ConnectionManager()

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def get_system_metrics():
    mem_res = rish_exec("free -m | grep Mem")
    ram_info = mem_res.stdout.strip() if mem_res.returncode == 0 else "N/A"
    
    thermal_res = rish_exec("cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null")
    avg_temp = "N/A"
    if thermal_res.returncode == 0 and thermal_res.stdout.strip():
        temps = [int(t) // 1000 for t in thermal_res.stdout.strip().split() if t.isdigit()]
        if temps:
            avg_temp = f"{sum(temps) // len(temps)}°C"
            
    return {"ram": ram_info, "temp": avg_temp}

async def tail_log_file():
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
        
    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue
            event = {
                "type": "log",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "content": line.strip()
            }
            await manager.broadcast(event)

def start_queue_worker_thread():
    def run_worker():
        subprocess.run(["python3", os.path.expanduser("~/nanodroid_queue.py"), "worker"])
    t = threading.Thread(target=run_worker, daemon=True)
    t.start()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tail_log_file())
    start_queue_worker_thread()

REALTIME_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NanoDroid Job Queue Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4">
    <div class="max-w-md mx-auto space-y-4">
        <!-- Header -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex justify-between items-center">
            <div>
                <h1 class="text-xl font-bold text-emerald-400">NanoDroid Hub</h1>
                <p class="text-xs text-slate-400">Persistent Job Queue | v12.0.0</p>
            </div>
            <div id="connection-badge" class="px-2.5 py-1 text-xs font-semibold bg-amber-900/50 text-amber-300 border border-amber-700/50 rounded-full">
                Connecting...
            </div>
        </div>

        <!-- Telemetry Cards -->
        <div class="grid grid-cols-2 gap-2">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                <span class="text-[10px] text-slate-400 uppercase tracking-wider">CPU Temp</span>
                <p id="metric-temp" class="text-lg font-mono font-bold text-emerald-400">--</p>
            </div>
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                <span class="text-[10px] text-slate-400 uppercase tracking-wider">Queue Engine</span>
                <p class="text-lg font-mono font-bold text-cyan-400">ACTIVE</p>
            </div>
        </div>

        <!-- Control Actions -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Job Dispatcher</h2>
            <div class="space-y-2">
                <input id="task-payload" type="text" placeholder="Enter task command or snippet..." class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500">
                <div class="grid grid-cols-2 gap-2">
                    <button onclick="enqueueTask('snippet')" class="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold p-2 rounded-lg text-xs transition">Enqueue Snippet</button>
                    <button onclick="enqueueTask('shell')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold p-2 rounded-lg text-xs transition">Enqueue Shell</button>
                </div>
            </div>
        </div>

        <!-- Live Terminal Stream -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-2">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Live Execution Stream</h2>
            <div id="terminal-stream" class="bg-slate-950 border border-slate-800 p-3 rounded-lg h-52 overflow-y-auto font-mono text-[11px] space-y-1 text-slate-300">
                <p class="text-slate-500">Establishing WebSocket secure tunnel...</p>
            </div>
        </div>
    </div>

    <script>
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const ws = new WebSocket(wsProtocol + window.location.host + '/ws');
        const badge = document.getElementById('connection-badge');
        const terminal = document.getElementById('terminal-stream');

        ws.onopen = function() {
            badge.textContent = "Live Stream";
            badge.className = "px-2.5 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 rounded-full animate-pulse";
        };

        ws.onclose = function() {
            badge.textContent = "Disconnected";
            badge.className = "px-2.5 py-1 text-xs font-semibold bg-rose-900/50 text-rose-300 border border-rose-700/50 rounded-full";
        };

        ws.onmessage = function(event) {
            let data = JSON.parse(event.data);
            if (data.type === 'log') {
                let p = document.createElement('p');
                p.innerHTML = `<span class="text-slate-500">[${data.timestamp}]</span> ${escapeHtml(data.content)}`;
                terminal.appendChild(p);
                terminal.scrollTop = terminal.scrollHeight;
            }
        };

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        async function enqueueTask(type) {
            let payload = document.getElementById('task-payload').value;
            if (!payload) {
                alert("Please enter a task payload.");
                return;
            }
            let res = await fetch('/api/queue/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: type, payload: payload, priority: 5})
            });
            let data = await res.json();
            alert("Enqueued Task ID: " + data.task_id);
            document.getElementById('task-payload').value = "";
        }

        setInterval(async () => {
            let res = await fetch('/api/metrics');
            let data = await res.json();
            document.getElementById('metric-temp').textContent = data.temp;
        }, 5000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_root():
    return REALTIME_DASHBOARD_HTML

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/metrics")
def api_metrics():
    return get_system_metrics()

@app.post("/api/queue/add")
async def api_queue_add(data: dict):
    t_type = data.get("type", "snippet")
    payload = data.get("payload")
    priority = data.get("priority", 5)
    if not payload:
        raise HTTPException(status_code=400, detail="Missing payload")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO task_queue (priority, task_type, payload, status, created_at, updated_at)
        VALUES (?, ?, ?, 'PENDING', ?, ?)
    ''', (priority, t_type, payload, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "task_id": task_id}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
