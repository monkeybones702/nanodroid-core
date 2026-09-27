#!/usr/bin/env python3
import os
import sys
import subprocess
from nanodroid_ui_parser import UITreeParser

# ==============================================================================
# NanoDroid-Core Self-Healing UI Navigator (v19.0.0 - Optimized Parser Integration)
# ==============================================================================

DUMP_PATH = "/data/local/tmp/window_dump.xml"
LOCAL_DUMP = os.path.expanduser("~/.nanodroid_window_dump.xml")

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def dump_and_index():
    rish_exec(f"rm -f {DUMP_PATH}")
    rish_exec(f"uiautomator dump {DUMP_PATH}")
    pull = rish_exec(f"cat {DUMP_PATH}")
    if pull.returncode == 0 and pull.stdout.strip():
        with open(LOCAL_DUMP, "w") as f:
            f.write(pull.stdout.strip())
    parser = UITreeParser()
    if parser.load_tree():
        return parser
    return None

def tap_node(query):
    print(f"[*] Navigating and tapping node matching: '{query}'")
    parser = dump_and_index()
    if not parser:
        print("[-] Failed to acquire UI tree dump.")
        return False
        
    node = parser.find_node(query)
    if node:
        cx, cy = node["center"]
        print(f"[+] Found node '{node['text'] or node['resource-id']}' at center ({cx}, {cy})")
        rish_exec(f"input tap {cx} {cy}")
        return True
    else:
        print(f"[-] Node matching query '{query}' not found.")
        return False

def type_node(query, text):
    print(f"[*] Locating input field matching: '{query}' and typing text.")
    if tap_node(query):
        import time
        time.sleep(0.5)
        formatted_text = text.replace(' ', '%s')
        rish_exec(f"input text '{formatted_text}'")
        return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 nanodroid_ui_navigator.py {tap <query>|type <query> <text>}")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    if action == "tap":
        tap_node(sys.argv[2])
    elif action == "type" and len(sys.argv) > 3:
        type_node(sys.argv[2], sys.argv[3])
    else:
        print("[-] Invalid arguments.")
        sys.exit(1)
