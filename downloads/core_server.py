import os
import subprocess
import xml.etree.ElementTree as ET
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

app = FastAPI(title="NanoDroid-Core Shizuku Bridge", version="1.1.0")

class UIQueryRequest(BaseModel):
    text: str

class UIExecuteRequest(BaseModel):
    action: str
    target: Dict[str, str]
    input_text: Optional[str] = None

def execute_shizuku_command(command: str) -> str:
    """Executes commands via Shizuku's rish binder interface or fallback."""
    try:
        full_cmd = f"rish -c '{command}'"
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Fallback to direct local shell if rish fails
        fallback = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return fallback.stdout

def dump_and_parse_accessibility_tree() -> ET.Element:
    xml_path = "/data/local/tmp/window_dump.xml"
    execute_shizuku_command(f"uiautomator dump {xml_path}")
    xml_content = execute_shizuku_command(f"cat {xml_path}")
    
    if not xml_content.strip():
        raise HTTPException(status_code=500, detail="Failed to capture UI accessibility dump.")
        
    return ET.fromstring(xml_content)

def parse_bounds(bounds_str: str) -> tuple:
    cleaned = bounds_str.replace("][", ",").replace("[", "").replace("]", "")
    coords = list(map(int, cleaned.split(",")))
    return (coords[0] + coords[2]) // 2, (coords[1] + coords[3]) // 2

@app.post("/ui/query")
def query_ui_node(payload: UIQueryRequest):
    try:
        root = dump_and_parse_accessibility_tree()
        target_text = payload.text.lower()
        
        for node in root.iter("node"):
            text = node.get("text", "").lower()
            desc = node.get("content-desc", "").lower()
            
            if target_text in text or target_text in desc:
                bounds = node.get("bounds")
                if bounds:
                    cx, cy = parse_bounds(bounds)
                    return {
                        "status": "found",
                        "text": node.get("text"),
                        "bounds": bounds,
                        "center": [cx, cy]
                    }
                    
        return {"status": "not_found", "message": f"Target '{payload.text}' not located."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ui/execute")
def execute_ui_action(payload: UIExecuteRequest):
    try:
        root = dump_and_parse_accessibility_tree()
        target_text = payload.target.get("text", "").lower()
        
        cx, cy = None, None
        for node in root.iter("node"):
            if target_text in node.get("text", "").lower() or target_text in node.get("content-desc", "").lower():
                bounds = node.get("bounds")
                if bounds:
                    cx, cy = parse_bounds(bounds)
                    break
                    
        if cx is None or cy is None:
            raise HTTPException(status_code=404, detail=f"Target node '{target_text}' not found.")
            
        action = payload.action.lower()
        if action == "click":
            execute_shizuku_command(f"input tap {cx} {cy}")
        elif action == "text" and payload.input_text:
            execute_shizuku_command(f"input tap {cx} {cy}")
            escaped_text = payload.input_text.replace(" ", "%s")
            execute_shizuku_command(f"input text \"{escaped_text}\"")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action '{action}'.")
            
        return {"status": "success", "action": action, "executed_at": [cx, cy]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
