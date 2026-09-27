#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET
import re
import subprocess

# ==============================================================================
# NanoDroid-Core Dynamic UI Tree Parser & Spatial Indexer (v19.1.0)
# Target: Samsung Galaxy A16 (ARM64) | Auto-Dumping & In-Memory DOM Indexing
# ==============================================================================

LOCAL_DUMP = os.path.expanduser("~/.nanodroid_window_dump.xml")
DUMP_PATH = "/data/local/tmp/window_dump.xml"

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

class UITreeParser:
    def __init__(self):
        self.nodes = []

    def refresh_and_load(self):
        print("[*] Triggering live accessibility tree dump via Shizuku...")
        rish_exec(f"rm -f {DUMP_PATH}")
        rish_exec(f"uiautomator dump {DUMP_PATH}")
        pull = rish_exec(f"cat {DUMP_PATH}")
        if pull.returncode == 0 and pull.stdout.strip():
            with open(LOCAL_DUMP, "w") as f:
                f.write(pull.stdout.strip())
        return self.load_tree()

    def load_tree(self):
        if not os.path.exists(LOCAL_DUMP):
            return self.refresh_and_load()
        try:
            tree = ET.parse(LOCAL_DUMP)
            root = tree.getroot()
            self.nodes = []
            
            for node in root.iter('node'):
                bounds_str = node.get("bounds", "")
                matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
                if len(matches) == 2:
                    x1, y1 = int(matches[0][0]), int(matches[0][1])
                    x2, y2 = int(matches[1][0]), int(matches[1][1])
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    
                    node_data = {
                        "text": node.get("text", "").strip(),
                        "resource-id": node.get("resource-id", "").strip(),
                        "content-desc": node.get("content-desc", "").strip(),
                        "class": node.get("class", "").strip(),
                        "clickable": node.get("clickable", "false") == "true",
                        "bounds": (x1, y1, x2, y2),
                        "center": (cx, cy)
                    }
                    self.nodes.append(node_data)
            return len(self.nodes) > 0
        except Exception as e:
            print(f"[-] UI Tree Parsing Error: {e}")
            return False

    def find_node(self, query):
        if not self.nodes:
            self.load_tree()
        query_lower = query.lower()
        # 1. Exact match on resource-id or text
        for node in self.nodes:
            if query_lower in node["resource-id"].lower() or query_lower == node["text"].lower():
                return node
        # 2. Substring match on text or content-desc
        for node in self.nodes:
            if query_lower in node["text"].lower() or query_lower in node["content-desc"].lower():
                return node
        return None

if __name__ == "__main__":
    parser = UITreeParser()
    if parser.refresh_and_load():
        print(f"[+] Successfully indexed {len(parser.nodes)} DOM nodes from window dump.")
        if len(sys.argv) > 1:
            q = sys.argv[1]
            res = parser.find_node(q)
            if res:
                print(f"[+] Match found for '{q}': {res}")
            else:
                print(f"[-] No match found for '{q}'.")
    else:
        print("[-] Failed to capture or parse UI tree dump via Shizuku.")
