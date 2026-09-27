#!/usr/bin/env python3
import os
import sys
import time
import json
import subprocess
import xml.etree.ElementTree as ET
import re

# ==============================================================================
# NanoDroid-Core Semantic Macro Recorder & Replay Engine (v15.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Coordinate-Independent Macro Compilation
# ==============================================================================

MACRO_DIR = os.path.expanduser("~/.nanodroid_macros")
LOCAL_DUMP = os.path.expanduser("~/.nanodroid_window_dump.xml")
DUMP_PATH = "/data/local/tmp/window_dump.xml"

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def init_macro_storage():
    os.makedirs(MACRO_DIR, exist_ok=True)

def dump_ui_tree():
    rish_exec(f"rm -f {DUMP_PATH}")
    rish_exec(f"uiautomator dump {DUMP_PATH}")
    pull = rish_exec(f"cat {DUMP_PATH}")
    if pull.returncode == 0 and pull.stdout.strip():
        with open(LOCAL_DUMP, "w") as f:
            f.write(pull.stdout.strip())
        return True
    return False

def find_node_by_coords(target_x, target_y):
    if not dump_ui_tree():
        return None
    try:
        tree = ET.parse(LOCAL_DUMP)
        root = tree.getroot()
        best_match = None
        min_distance = float('inf')
        
        for node in root.iter('node'):
            bounds = node.get("bounds")
            if not bounds:
                continue
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds)
            if len(matches) == 2:
                x1, y1 = int(matches[0][0]), int(matches[0][1])
                x2, y2 = int(matches[1][0]), int(matches[1][1])
                
                # Check if target coordinates fall within node bounds
                if x1 <= target_x <= x2 and y1 <= target_y <= y2:
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    dist = abs(cx - target_x) + abs(cy - target_y)
                    if dist < min_distance:
                        min_distance = dist
                        best_match = {
                            "text": node.get("text", ""),
                            "resource-id": node.get("resource-id", ""),
                            "content-desc": node.get("content-desc", ""),
                            "class": node.get("class", "")
                        }
        return best_match
    except Exception as e:
        print(f"[-] DOM coordinate parsing error: {e}")
    return None

def record_macro_step(macro_name, action_type, x=0, y=0, text=""):
    init_macro_storage()
    macro_path = os.path.join(MACRO_DIR, f"{macro_name}.json")
    
    steps = []
    if os.path.exists(macro_path):
        try:
            with open(macro_path, "r") as f:
                steps = json.load(f)
        except Exception:
            steps = []
            
    step_data = {"type": action_type}
    if action_type == "tap":
        semantic = find_node_by_coords(x, y)
        if semantic and (semantic["text"] or semantic["resource-id"]):
            step_data["selector"] = semantic["text"] or semantic["resource-id"]
            step_data["selector_type"] = "text" if semantic["text"] else "resource-id"
            print(f"[+] Mapped tap ({x},{y}) to semantic node: {step_data['selector']}")
        else:
            step_data["x"] = x
            step_data["y"] = y
            print(f"[!] Warning: No semantic node found at ({x},{y}). Falling back to absolute coordinates.")
    elif action_type == "type":
        step_data["text"] = text
        
    steps.append(step_data)
    with open(macro_path, "w") as f:
        json.dump(steps, f, indent=2)
    print(f"[+] Recorded step [{action_type}] to macro '{macro_name}'.")

def replay_macro(macro_name):
    macro_path = os.path.join(MACRO_DIR, f"{macro_name}.json")
    if not os.path.exists(macro_path):
        print(f"[-] Macro '{macro_name}' not found.")
        return
        
    with open(macro_path, "r") as f:
        steps = json.load(f)
        
    print(f"[*] Replaying semantic macro '{macro_name}' ({len(steps)} steps)...")
    for idx, step in enumerate(steps):
        print(f" -> Step {idx+1}: {step['type']}")
        if step['type'] == 'tap':
            if 'selector' in step:
                # Use navigator logic to locate and tap dynamically
                from nanodroid_ui_navigator import tap_node
                tap_node(step['selector'])
            else:
                rish_exec(f"input tap {step['x']} {step['y']}")
        elif step['type'] == 'type':
            rish_exec(f"input text '{step['text'].replace(' ', '%s')}'")
        time.sleep(1.0)
    print(f"[+] Macro '{macro_name}' playback completed.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 nanodroid_macro.py {record-tap <name> <x> <y>|replay <name>}")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    m_name = sys.argv[2]
    
    if cmd == "record-tap" and len(sys.argv) > 4:
        record_macro_step(m_name, "tap", int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "replay":
        replay_macro(m_name)
    else:
        print("[-] Invalid arguments.")
        sys.exit(1)
