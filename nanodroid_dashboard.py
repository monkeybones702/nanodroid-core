#!/usr/bin/env python3
import os
import sqlite3
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="NanoDroid-Core Telemetry Dashboard", version="5.1.0")
DB_PATH = os.path.expanduser("~/.nanodroid_state.db")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NanoDroid-Core Master Telemetry</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4">
    <div class="max-w-lg mx-auto space-y-4">
        <!-- Header -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex justify-between items-center">
            <div>
                <h1 class="text-xl font-bold text-emerald-400">NanoDroid-Core</h1>
                <p class="text-xs text-slate-400">Samsung Galaxy A16 | ARM64 Engine v5.1.0</p>
            </div>
            <span class="px-2.5 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 rounded-full animate-pulse">Online</span>
        </div>

        <!-- Controls -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Engine Controls</h2>
            <div class="grid grid-cols-2 gap-2">
                <button onclick="triggerEngine()" class="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold p-2.5 rounded-lg text-sm transition">Run Cycle</button>
                <button onclick="fetchTelemetry()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold p-2.5 rounded-lg text-sm transition">Refresh Data</button>
            </div>
        </div>

        <!-- Telemetry Status -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Execution Log Telemetry</h2>
            <div id="log-container" class="space-y-2 max-h-64 overflow-y-auto font-mono text-xs">
                <p class="text-slate-500">Loading execution records...</p>
            </div>
        </div>
    </div>

    <script>
        async function fetchTelemetry() {
            try {
                let res = await fetch('/api/telemetry');
                let data = await res.json();
                let container = document.getElementById('log-container');
                if (data.records.length === 0) {
                    container.innerHTML = '<p class="text-slate-500">No execution records found yet.</p>';
                    return;
                }
                container.innerHTML = data.records.reverse().map(r => `
                    <div class="bg-slate-950 border border-slate-800 p-2 rounded flex flex-col space-y-1">
                        <div class="flex justify-between text-[10px] text-slate-400">
                            <span>ID: ${r[0]} | ${r[1]}</span>
                            <span class="text-emerald-400 font-bold">${r[4]}</span>
                        </div>
                        <pre class="text-slate-300 truncate">${r[3].substring(0, 100)}...</pre>
                    </div>
                `).join('');
            } catch (e) {
                console.error(e);
            }
        }

        async function triggerEngine() {
            let res = await fetch('/api/trigger', {method: 'POST'});
            let data = await res.json();
            alert("Engine Cycle Result: " + data.status);
            fetchTelemetry();
        }

        fetchTelemetry();
        setInterval(fetchTelemetry, 5000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return DASHBOARD_HTML

@app.get("/api/telemetry")
def get_telemetry():
    if not os.path.exists(DB_PATH):
        return {"records": []}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, snippet_hash, snippet_content, status FROM execution_log ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return {"records": rows}

@app.post("/api/trigger")
def trigger_engine():
    res = subprocess.run(["python3", os.path.expanduser("~/nanodroid_core_engine.py")], capture_output=True, text=True)
    return {"status": "executed", "returncode": res.returncode, "output": res.stdout[-300:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
