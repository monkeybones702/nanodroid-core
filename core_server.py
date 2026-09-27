import os
import subprocess
import time
import xml.etree.ElementTree as ET
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="NanoDroid-Core OmniEngine", version="4.4.1")

class ActionPayload(BaseModel):
    action: str
    target_text: Optional[str] = None
    key_code: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    end_x: Optional[int] = None
    end_y: Optional[int] = None
    duration_ms: Optional[int] = 300
    shell_command: Optional[str] = None
    package_name: Optional[str] = None
    wait_seconds: Optional[float] = 1.0

class MacroPayload(BaseModel):
    macro_name: str
    steps: List[ActionPayload]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NanoDroid-Core OmniEngine Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4">
    <div class="max-w-md mx-auto space-y-4">
        <!-- Header -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
            <div class="flex justify-between items-center">
                <h1 class="text-xl font-bold text-emerald-400">NanoDroid-Core</h1>
                <span id="engine-status" class="px-2.5 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 rounded-full animate-pulse">Online</span>
            </div>
            <p class="text-xs text-slate-400 mt-1">Samsung Galaxy A16 ARM64 OmniEngine v4.4.1</p>
        </div>

        <!-- Quick Actions -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider">Quick Actions</h2>
            <div class="grid grid-cols-3 gap-2">
                <button onclick="executeAction({action: 'keyevent', key_code: 3})" class="bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-slate-700 p-2.5 rounded-lg text-sm font-medium transition">Home</button>
                <button onclick="executeAction({action: 'keyevent', key_code: 4})" class="bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-slate-700 p-2.5 rounded-lg text-sm font-medium transition">Back</button>
                <button onclick="executeAction({action: 'keyevent', key_code: 187})" class="bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-slate-700 p-2.5 rounded-lg text-sm font-medium transition">Recents</button>
            </div>
        </div>

        <!-- Self-Healing Click Trigger -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider">Self-Healing Tap</h2>
            <div class="flex gap-2">
                <input type="text" id="target-input" placeholder="Target text (e.g., Settings)" class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500">
                <button onclick="triggerClick()" class="bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 px-4 py-2 rounded-lg text-sm font-semibold transition">Tap</button>
            </div>
        </div>

        <!-- Live UI Tree Inspector -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
            <div class="flex justify-between items-center">
                <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider">UI Context Tree</h2>
                <button onclick="fetchUiContext()" class="text-xs bg-slate-800 hover:bg-slate-700 px-2.5 py-1.5 rounded border border-slate-700 transition">Refresh</button>
            </div>
            <div id="ui-nodes" class="bg-slate-950 border border-slate-800 rounded-lg p-3 h-48 overflow-y-auto text-xs font-mono space-y-1 text-slate-300">
                <span class="text-slate-500">Click Refresh to load active screen nodes...</span>
            </div>
        </div>

        <!-- Console Log Output -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-2">
            <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Console Log</h2>
            <pre id="console-output" class="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs font-mono text-emerald-400 h-24 overflow-y-auto">Ready for execution...</pre>
        </div>
    </div>

    <script>
        function log(msg) {
            const out = document.getElementById('console-output');
            out.innerText += '\\n> ' + msg;
            out.scrollTop = out.scrollHeight;
        }

        async function executeAction(payload) {
            log("Executing: " + JSON.stringify(payload));
            try {
                let res = await fetch('/ui/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                let data = await res.json();
                log("Result: " + JSON.stringify(data));
            } catch (err) {
                log("Error: " + err);
            }
        }

        function triggerClick() {
            const text = document.getElementById('target-input').value.trim();
            if (!text) {
                alert("Please enter target text");
                return;
            }
            executeAction({action: 'click', target_text: text});
        }

        async function fetchUiContext() {
            log("Fetching active UI context tree...");
            const container = document.getElementById('ui-nodes');
            container.innerHTML = '<span class="text-amber-400 animate-pulse">Dumping window hierarchy...</span>';
            try {
                let res = await fetch('/ui/context');
                let data = await res.json();
                container.innerHTML = '';
                if (data.interactive_elements && data.interactive_elements.length > 0) {
                    data.interactive_elements.forEach(node => {
                        const div = document.createElement('div');
                        div.className = "p-1.5 hover:bg-slate-900 rounded cursor-pointer border-b border-slate-900/50 flex justify-between items-center";
                        div.innerHTML = `<span class="text-emerald-300 truncate max-w-[200px]">${node.text || '<No Text>'}</span><span class="text-slate-500 text-[10px]">${node.resource_id || ''}</span>`;
                        div.onclick = () => {
                            if (node.text) {
                                document.getElementById('target-input').value = node.text;
                                log("Selected target text: " + node.text);
                            }
                        };
                        container.appendChild(div);
                    });
                    log("Loaded " + data.node_count + " total nodes.");
                } else {
                    container.innerHTML = '<span class="text-slate-500">No interactive nodes found. Ensure screen is unlocked.</span>';
                }
            } catch (err) {
                container.innerHTML = '<span class="text-rose-400">Failed to load UI context.</span>';
                log("Error fetching UI context: " + err);
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return DASHBOARD_HTML

@app.get("/api/status")
def root():
    return {"status": "online", "engine": "NanoDroid-Core OmniEngine v4.4.1", "target": "Samsung Galaxy A16 ARM64"}

@app.get("/system/packages")
def get_packages():
    try:
        res = subprocess.run(["rish", "-c", "pm list packages"], capture_output=True, text=True, check=True, timeout=5)
        return [line.replace("package:", "").strip() for line in res.stdout.splitlines() if line.startswith("package:")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch packages: {str(e)}")

@app.get("/ui/context")
def get_ui_context():
    xml_path = "/data/local/tmp/window_dump.xml"
    try:
        subprocess.run(["rish", "-c", "input keyevent KEYCODE_WAKEUP && input swipe 540 1800 540 500 200"], capture_output=True, timeout=4)
        time.sleep(1.0)
        dump_res = subprocess.run(["rish", "-c", f"uiautomator dump {xml_path}"], capture_output=True, text=True, timeout=6)
        if dump_res.returncode != 0:
            raise HTTPException(status_code=500, detail="uiautomator dump failed.")
        
        cat_res = subprocess.run(["rish", "-c", f"cat {xml_path}"], capture_output=True, text=True, timeout=5)
        root_elem = ET.fromstring(cat_res.stdout.strip())
        
        nodes = []
        for elem in root_elem.iter('node'):
            text = elem.get('text', '')
            res_id = elem.get('resource-id', '')
            bounds = elem.get('bounds', '')
            if text or res_id:
                nodes.append({"text": text, "resource_id": res_id, "bounds": bounds})
        return {"node_count": len(nodes), "interactive_elements": nodes[:50]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ui/execute")
def execute_action(payload: ActionPayload):
    action = payload.action.lower()
    try:
        if action == "keyevent" and payload.key_code is not None:
            subprocess.run(["rish", "-c", f"input keyevent {payload.key_code}"], check=True, timeout=3)
            return {"status": "success", "executed": f"keyevent {payload.key_code}"}
        elif action == "swipe":
            cmd = f"input swipe {payload.x} {payload.y} {payload.end_x} {payload.end_y} {payload.duration_ms}"
            subprocess.run(["rish", "-c", cmd], check=True, timeout=3)
            return {"status": "success", "executed": cmd}
        elif action == "launch" and payload.package_name:
            cmd = f"am start -p {payload.package_name} -c android.intent.category.LAUNCHER"
            subprocess.run(["rish", "-c", cmd], check=True, timeout=3)
            return {"status": "success", "executed": cmd}
        elif action == "shell" and payload.shell_command:
            res = subprocess.run(["rish", "-c", payload.shell_command], capture_output=True, text=True, check=True, timeout=5)
            return {"status": "success", "output": res.stdout.strip()}
        elif action == "wait":
            time.sleep(payload.wait_seconds)
            return {"status": "success", "executed": f"wait {payload.wait_seconds}s"}
        elif action == "click":
            target = payload.target_text
            if not target:
                raise HTTPException(status_code=400, detail="Target text required for click.")
            xml_path = "/data/local/tmp/window_dump.xml"
            subprocess.run(["rish", "-c", f"uiautomator dump {xml_path}"], check=True, timeout=6)
            cat_res = subprocess.run(["rish", "-c", f"cat {xml_path}"], capture_output=True, text=True, check=True)
            root_elem = ET.fromstring(cat_res.stdout.strip())
            
            found_bounds = None
            for elem in root_elem.iter('node'):
                if target.lower() in elem.get('text', '').lower() or target.lower() in elem.get('resource-id', '').lower():
                    found_bounds = elem.get('bounds')
                    break
            if not found_bounds:
                return {"status": "not_found", "message": f"Target '{target}' not visible."}
            
            import re
            coords = list(map(int, re.findall(r'\d+', found_bounds)))
            cx, cy = (coords[0] + coords[2]) // 2, (coords[1] + coords[3]) // 2
            subprocess.run(["rish", "-c", f"input tap {cx} {cy}"], check=True, timeout=3)
            return {"status": "found", "coordinates": [cx, cy], "executed": f"tap {cx} {cy}"}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/macro/execute")
def execute_macro(macro: MacroPayload):
    results = []
    for i, step in enumerate(macro.steps):
        try:
            res = execute_action(step)
            results.append({"step": i+1, "action": step.action, "result": res})
            time.sleep(step.wait_seconds if step.wait_seconds else 0.5)
        except Exception as e:
            results.append({"step": i+1, "action": step.action, "status": "error", "detail": str(e)})
            break
    return {"macro_name": macro.macro_name, "status": "completed", "steps_executed": results}

@app.get("/manual")
def get_manual():
    manual_path = os.path.expanduser("~/nanodroid_manual.md")
    if os.path.exists(manual_path):
        with open(manual_path, "r") as mf:
            return {"manual": mf.read()}
    return {"error": "Manual not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
