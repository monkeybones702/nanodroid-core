#!/usr/bin/env python3
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import time
import re

# ==============================================================================
# NanoDroid-Core Self-Healing UI Vision Engine (v24.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Robust Node Traversal & Coordinate Mapping
# ==============================================================================

def rish_exec(cmd):
    """Executes a command with system privileges via Shizuku (rish)."""
    try:
        res = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        print(f"[-] Shizuku execution error: {e}")
        return ""

def dump_ui_hierarchy():
    """Forces uiautomator to dump the active window node tree."""
    rish_exec("uiautomator dump /data/local/tmp/window_dump.xml")
    return rish_exec("cat /data/local/tmp/window_dump.xml")

def parse_nodes(xml_content):
    """Extracts all interactable nodes with text, resource-id, and bounds."""
    nodes = []
    if not xml_content:
        return nodes
    try:
        root = ET.fromstring(xml_content)
        for elem in root.iter('node'):
            text = elem.attrib.get('text', '')
            resource_id = elem.attrib.get('resource-id', '')
            clickable = elem.attrib.get('clickable', 'false')
            bounds = elem.attrib.get('bounds', '')
            if text or resource_id:
                nodes.append({
                    'text': text,
                    'resource_id': resource_id,
                    'clickable': clickable,
                    'bounds': bounds
                })
    except Exception as e:
        print(f"[-] XML parsing error: {e}")
    return nodes

def extract_bounds_center(bounds_str):
    """Parses [x1,y1][x2,y2] bounds string and returns central (x, y) coordinates."""
    match = re.findall(r'\d+', bounds_str)
    if len(match) == 4:
        x1, y1, x2, y2 = map(int, match)
        return (x1 + x2) // 2, (y1 + y2) // 2
    return None, None

def self_healing_click(target_query, retries=3, delay=1.0):
    """
    Self-healing routine: attempts to find and tap a target node by text or resource ID.
    If layout is stale or loading, it refreshes the UI dump up to 'retries' times.
    """
    query_lower = target_query.lower()
    
    for attempt in range(1, retries + 1):
        print(f"[*] Vision Engine: Searching for '{target_query}' (Attempt {attempt}/{retries})...")
        xml_data = dump_ui_hierarchy()
        nodes = parse_nodes(xml_data)
        
        # Pass 1: Exact or substring text match
        for node in nodes:
            if query_lower in node['text'].lower() or query_lower in node['resource_id'].lower():
                cx, cy = extract_bounds_center(node['bounds'])
                if cx and cy:
                    print(f"[+] Match found! Node Text: '{node['text']}' | ID: '{node['resource_id']}'")
                    print(f"[*] Dispatching tap to coordinates ({cx}, {cy}) via Shizuku...")
                    rish_exec(f"input tap {cx} {cy}")
                    return True
                    
        print(f"[-] Node not found on attempt {attempt}. Retrying in {delay}s...")
        time.sleep(delay)
        
    print(f"[-] Self-Healing Error: Failed to locate target '{target_query}' after {retries} attempts.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_vision.py '<target_text_or_id>'")
        sys.exit(1)
        
    target = " ".join(sys.argv[1:])
    self_healing_click(target)
