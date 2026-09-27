#!/usr/bin/env python3
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import time

# ==============================================================================
# NanoDroid-Core Shizuku-Gemini Bridge Engine (v23.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Privileged Shizuku & UI Automation Bridge
# ==============================================================================

def rish_exec(cmd):
    """Executes a command with system/root privileges via Shizuku (rish)."""
    try:
        res = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        print(f"[-] Shizuku execution error: {e}")
        return ""

def dump_ui_hierarchy():
    """Dumps the current screen UI hierarchy using uiautomator via Shizuku."""
    print("[*] Capturing screen node hierarchy via Shizuku...")
    rish_exec("uiautomator dump /data/local/tmp/window_dump.xml")
    res = rish_exec("cat /data/local/tmp/window_dump.xml")
    return res

def parse_nodes(xml_content):
    """Parses uiautomator XML string and extracts interactable nodes."""
    nodes = []
    if not xml_content:
        return nodes
    try:
        root = ET.fromstring(xml_content)
        for elem in root.iter('node'):
            text = elem.attrib.get('text', '')
            resource_id = elem.attrib.get('resource-id', '')
            class_name = elem.attrib.get('class', '')
            bounds = elem.attrib.get('bounds', '')
            if text or resource_id:
                nodes.append({
                    'text': text,
                    'resource_id': resource_id,
                    'class': class_name,
                    'bounds': bounds
                })
    except Exception as e:
        print(f"[-] XML parsing error: {e}")
    return nodes

def click_node_by_text(target_text):
    """Finds a node containing target_text and clicks it using computed bounds via Shizuku."""
    xml_data = dump_ui_hierarchy()
    nodes = parse_nodes(xml_data)
    
    for node in nodes:
        if target_text.lower() in node['text'].lower():
            bounds = node['bounds']
            print(f"[+] Found target node '{target_text}' at bounds: {bounds}")
            try:
                coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                x1, y1, x2, y2 = map(int, coords)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                print(f"[*] Simulating tap at coordinates ({center_x}, {center_y}) via Shizuku...")
                rish_exec(f"input tap {center_x} {center_y}")
                return True
            except Exception as e:
                print(f"[-] Error calculating coordinates from bounds: {e}")
    print(f"[-] Target node '{target_text}' not found on active screen.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_shizuku_bridge.py 'dump'")
        print("       python3 nanodroid_shizuku_bridge.py 'click <text>'")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    if action == "dump":
        print(dump_ui_hierarchy())
    elif action == "click" and len(sys.argv) > 2:
        target = " ".join(sys.argv[2:])
        click_node_by_text(target)
    else:
        print("[-] Invalid arguments provided.")
