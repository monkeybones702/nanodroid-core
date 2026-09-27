import asyncio
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="NanoDroid-Core OmniEngine", version="4.1.2-ARM64")

class OmniActionRequest(BaseModel):
    action: str
    target_text: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    end_x: Optional[int] = None
    end_y: Optional[int] = None
    duration_ms: Optional[int] = 300
    text_payload: Optional[str] = None
    key_code: Optional[int] = None
    package_name: Optional[str] = None
    shell_command: Optional[str] = None

def clean_xml_string(raw_xml: str) -> str:
    if not raw_xml:
        return ""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', raw_xml)
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    return cleaned

def dump_ui_hierarchy() -> Tuple[Optional[ET.Element], Optional[str]]:
    """Optimized UI dump without blocking pkill calls to prevent rish deadlocks."""
    try:
        res = subprocess.run(
            "rish -c 'uiautomator dump /data/local/tmp/window_dump.xml'", 
            shell=True, capture_output=True, text=True, timeout=8
        )
        if res.returncode == 0:
            time.sleep(0.1)
            cat_res = subprocess.run(
                "rish -c 'cat /data/local/tmp/window_dump.xml'", 
                shell=True, capture_output=True, text=True, timeout=5
            )
            if cat_res.returncode == 0 and cat_res.stdout.strip():
                raw_xml = cat_res.stdout
                sanitized_xml = clean_xml_string(raw_xml)
                try:
                    return ET.fromstring(sanitized_xml), raw_xml
                except ET.ParseError:
                    return None, raw_xml
    except subprocess.TimeoutExpired:
        print("[!] Warning: uiautomator dump command timed out.", flush=True)
    except Exception as e:
        print(f"[!] Exception during UI dump: {e}", flush=True)
    return None, None

def parse_bounds(bounds_str: str) -> Optional[Tuple[int, int, int, int]]:
    if not bounds_str:
        return None
    try:
        clean = bounds_str.replace('][', ',').replace('[', '').replace(']', '')
        coords = [int(c) for c in clean.split(',')]
        return tuple(coords) # type: ignore
    except ValueError:
        return None

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NanoDroid-Core Dashboard</title>
        <style>
            body { font-family: monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
            h1 { color: #58a6ff; font-size: 1.5rem; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 15px; }
            button { background: #238636; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; margin: 5px 5px 5px 0; }
            button:hover { background: #2ea043; }
            input { background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 8px; border-radius: 4px; width: calc(100% - 20px); margin-bottom: 10px; }
            pre { background: #010409; padding: 10px; border-radius: 4px; overflow-x: auto; max-height: 300px; font-size: 0.85rem; border: 1px solid #30363d; }
            .flex { display: flex; gap: 10px; flex-wrap: wrap; }
        </style>
    </head>
    <body>
        <h1>NanoDroid-Core OmniEngine v4.1.2</h1>
        <div class="card">
            <h3>Quick Actions</h3>
            <div class="flex">
                <button onclick="sendKey(3)">Home Key</button>
                <button onclick="sendKey(4)">Back Key</button>
                <button onclick="sendKey(187)">Recents</button>
                <button onclick="triggerScroll()">Scroll Down</button>
                <button onclick="fetchContext()">Refresh UI Tree</button>
            </div>
        </div>
        <div class="card">
            <h3>Target Action Dispatcher</h3>
            <label>Target Text / ID:</label>
            <input type="text" id="targetText" placeholder="e.g. Back, Settings, OK">
            <button onclick="clickTarget()">Click Target</button>
        </div>
        <div class="card">
            <h3>Live Screen Nodes / Status</h3>
            <pre id="output">Dashboard online. Click 'Refresh UI Tree'...</pre>
        </div>

        <script>
            async function api(endpoint, method='GET', data=null) {
                try {
                    let res = await fetch(endpoint, {
                        method: method,
                        headers: {'Content-Type': 'application/json'},
                        body: data ? JSON.stringify(data) : null
                    });
                    let json = await res.json();
                    document.getElementById('output').innerText = JSON.stringify(json, null, 2);
                } catch(e) {
                    document.getElementById('output').innerText = "Error: " + e;
                }
            }
            function fetchContext() { api('/ui/context'); }
            function sendKey(code) { api('/ui/execute', 'POST', {action: 'keyevent', key_code: code}); }
            function triggerScroll() { api('/ui/execute', 'POST', {action: 'swipe', x: 540, y: 1600, end_x: 540, end_y: 600}); }
            function clickTarget() {
                let text = document.getElementById('targetText').value;
                if(!text) return alert('Enter target text');
                api('/ui/execute', 'POST', {action: 'click', target_text: text});
            }
        </script>
    </body>
    </html>
    """

@app.get("/ui/context")
async def get_ui_context():
    root, raw_xml = dump_ui_hierarchy()
    interactive_nodes = []
    if root is not None:
        for node in root.iter('node'):
            text = node.get('text', '').strip()
            desc = node.get('content-desc', '').strip()
            resource_id = node.get('resource-id', '').strip().split(':id/')[-1]
            clickable = node.get('clickable') == 'true'
            enabled = node.get('enabled') == 'true'
            
            if enabled and (clickable or text or desc or resource_id):
                bounds_str = node.get('bounds')
                bounds = parse_bounds(bounds_str)
                if bounds:
                    x1, y1, x2, y2 = bounds
                    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                    node_summary = {
                        "id": resource_id if resource_id else None,
                        "text": text if text else None,
                        "desc": desc if desc else None,
                        "clickable": clickable,
                        "bounds": [x1, y1, x2, y2],
                        "center": [center_x, center_y]
                    }
                    interactive_nodes.append({k: v for k, v in node_summary.items() if v is not None})
                    
    if not interactive_nodes:
        raise HTTPException(status_code=500, detail="Could not capture UI dump. Ensure screen is awake and unlocked.")
    return {"status": "success", "node_count": len(interactive_nodes), "elements": interactive_nodes}

@app.post("/ui/execute")
async def execute_omni_action(req: OmniActionRequest):
    root, raw_xml = dump_ui_hierarchy()
    nodes_iter = list(root.iter('node')) if root is not None else []
    
    coords = None
    if req.target_text:
        for node in nodes_iter:
            text = node.get('text', '')
            desc = node.get('content-desc', '')
            resource_id = node.get('resource-id', '')
            if req.target_text.lower() in text.lower() or req.target_text.lower() in desc.lower() or req.target_text in resource_id:
                bounds_str = node.get('bounds')
                bounds = parse_bounds(bounds_str)
                if bounds:
                    coords = ((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
                    break

    if not coords and req.x is not None and req.y is not None:
        coords = (req.x, req.y)

    action = req.action.lower()

    if action == "click":
        if coords:
            x, y = coords
            subprocess.run(f"rish -c 'input tap {x} {y}'", shell=True, check=True, timeout=5)
            return {"status": "success", "action": "click", "coordinates": [x, y]}
        raise HTTPException(status_code=404, detail=f"Target '{req.target_text}' not found.")

    elif action == "swipe":
        x1, y1 = req.x or 540, req.y or 1800
        x2, y2 = req.end_x or 540, req.end_y or 500
        dur = req.duration_ms or 300
        subprocess.run(f"rish -c 'input swipe {x1} {y1} {x2} {y2} {dur}'", shell=True, check=True, timeout=5)
        return {"status": "success", "action": "swipe"}

    elif action == "keyevent":
        if req.key_code is not None:
            subprocess.run(f"rish -c 'input keyevent {req.key_code}'", shell=True, check=True, timeout=5)
            return {"status": "success", "action": "keyevent", "key_code": req.key_code}
        raise HTTPException(status_code=400, detail="Missing key_code.")

    elif action == "launch":
        if req.package_name:
            subprocess.run(f"rish -c 'am start -n {req.package_name}'", shell=True, check=True, timeout=5)
            return {"status": "success", "action": "launch", "package": req.package_name}
        raise HTTPException(status_code=400, detail="Missing package_name.")

    elif action == "shell":
        if req.shell_command:
            res = subprocess.run(f"rish -c '{req.shell_command}'", shell=True, capture_output=True, text=True, timeout=10)
            return {"status": "success", "action": "shell", "stdout": res.stdout.strip()}
        raise HTTPException(status_code=400, detail="Missing shell_command.")

    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
