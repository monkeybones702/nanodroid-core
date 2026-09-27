#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import xml.etree.ElementTree as ET
import re

# ==============================================================================
# NanoDroid-Core Semantic UI Node Navigator (v13.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Resilient DOM Parsing & Touch Injection
# ==============================================================================

DUMP_PATH = "/data/local/tmp/window_dump.xml"
LOCAL_DUMP = os.path.expanduser("~/.nanodroid_window_dump.xml")

def rish_exec(cmd):
    return subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)

def capture_accessibility_tree():
    print("[*] Triggering accessibility node dump via Shizuku...")
    rish_exec(f"rm -f {DUMP_PATH}")
    res = rish_exec(f"uiautomator dump {DUMP_PATH}")
    if res.returncode != 0:
        print(f"[-] uiautomator dump failed: {res.stderr}")
        return False
        
    pull_res = rish_exec(f"cat {DUMP_PATH}")
    if pull_res.returncode == 0 and pull_res.stdout.strip():
        with open(LOCAL_DUMP, "w") as f:
            f.write(pull_res.stdout.strip())
        return True
    return False

def parse_bounds(bounds_str):
    # Format: [x1,y1][x2,y2]
    matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
    if len(matches) == 2:
        x1, y1 = int(matches[0][0]), int(matches[0][1])
        x2, y2 = int(matches[1][0]), int(matches[1][1])
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return center_x, center_y, (x1, y1, x2, y2)
    return None

def find_node(query, attribute="text"):
    if not capture_accessibility_tree():
        return None
        
    try:
        tree = ET.parse(LOCAL_DUMP)
        root = tree.getroot()
        
        for node in root.iter('node'):
            attr_val = node.get(attribute, "")
            content_desc = node.get("content-desc", "")
            resource_id = node.get("resource-id", "")
            
            # Case-insensitive substring matching across primary attributes
            if (query.lower() in attr_val.lower() or 
                query.lower() in content_desc.lower() or 
                query.lower() in resource_id.lower()):
                
                bounds = node.get("bounds")
                coords = parse_bounds(bounds)
                if coords:
                    return {
                        "cx": coords[0],
                        "cy": coords[1],
                        "bounds": coords[2],
                        "text": attr_val,
                        "resource-id": resource_id
                    }
    except Exception as e:
        print(f"[-] XML parsing error: {e}")
    return None

def tap_node(query):
    node = find_node(query)
    if node:
        print(f"[+] Found node '{query}' at center ({node['cx']}, {node['cy']}) [ID: {node['resource-id']}]")
        rish_exec(f"input tap {node['cx']} {node['cy']}")
        return True
    else:
        print(f"[-] Node matching '{query}' not found on screen.")
        return False

def type_text_into_node(query, text):
    node = find_node(query)
    if node:
        print(f"[+] Clicking text field '{query}' at ({node['cx']}, {node['cy']})")
        rish_exec(f"input tap {node['cx']} {node['cy']}")
        time.sleep(0.5)
        # Escape spaces for shell input
        escaped_text = text.replace(" ", "%s")
        rish_exec(f"input text '{escaped_text}'")
        print(f"[+] Injected text: {text}")
        return True
    else:
        print(f"[-] Text field matching '{query}' not found.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nanodroid_ui_navigator.py {dump|find <query>|tap <query>|type <query> <text>}")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "dump":
        if capture_accessibility_tree():
            print(f"[+] UI DOM successfully dumped to {LOCAL_DUMP}")
    elif cmd == "find" and len(sys.argv) > 2:
        res = find_node(sys.argv[2])
        print(res if res else "Node not found.")
    elif cmd == "tap" and len(sys.argv) > 2:
        tap_node(sys.argv[2])
    elif cmd == "type" and len(sys.argv) > 3:
        type_text_into_node(sys.argv[2], sys.argv[3])
    else:
        print("[-] Invalid arguments.")
        sys.exit(1)
    EOF

chmod +x ~/nanodroid_ui_navigator.py

cat << 'EOF' > ~/nanodroidctl
#!/usr/bin/env bash
WATCHDOG_SCRIPT="$HOME/nanodroid_watchdog.py"
SCHEDULER_SCRIPT="$HOME/nanodroid_scheduler.py"
UPDATER_SCRIPT="$HOME/nanodroid_updater.py"
HUB_SCRIPT="$HOME/nanodroid_ws_hub.py"
QUEUE_SCRIPT="$HOME/nanodroid_queue.py"
NAVIGATOR_SCRIPT="$HOME/nanodroid_ui_navigator.py"
PID_FILE="$HOME/.nanodroid_hub.pid"
LOG_FILE="$HOME/.nanodroid_master.log"

case "$1" in
    start)
        python3 "$UPDATER_SCRIPT" snapshot
        python3 "$WATCHDOG_SCRIPT" start
        python3 "$SCHEDULER_SCRIPT" start
        
        if [ ! -f "$PID_FILE" ]; then
            echo "[*] Starting NanoDroid Full Ecosystem at http://127.0.0.1:8000..."
            nohup python3 "$HUB_SCRIPT" > "$LOG_FILE" 2>&1 &
            echo $! > "$PID_FILE"
        fi
        echo "[+] NanoDroid-Core Full Ecosystem ONLINE (v13.0.0 UI Navigator Active)."
        ;;
    stop)
        python3 "$SCHEDULER_SCRIPT" stop
        python3 "$WATCHDOG_SCRIPT" stop
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") 2>/dev/null
            rm -f "$PID_FILE"
        fi
        echo "[+] NanoDroid-Core Ecosystem OFFLINE."
        ;;
    restart)
        "$0" stop
        sleep 1
        "$0" start
        ;;
    status)
        python3 "$WATCHDOG_SCRIPT" status
        if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
            echo " * Ecosystem Hub Status: ONLINE (PID: $(cat "$PID_FILE"))"
        else
            echo " * Ecosystem Hub Status: OFFLINE"
        fi
        ;;
    ui-tap)
        if [ -z "$2" ]; then
            echo "Usage: nanodroidctl ui-tap '<button_text_or_id>'"
            exit 1
        fi
        python3 "$NAVIGATOR_SCRIPT" tap "$2"
        ;;
    ui-type)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: nanodroidctl ui-type '<field_query>' '<text>'"
            exit 1
        fi
        python3 "$NAVIGATOR_SCRIPT" type "$2" "$3"
        ;;
    enqueue)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: nanodroidctl enqueue <type> '<payload>' [priority]"
            exit 1
        fi
        python3 "$QUEUE_SCRIPT" add "$2" "$3" "${4:-5}"
        ;;
    clean)
        python3 "$WATCHDOG_SCRIPT" clean
        ;;
    watch)
        python3 "$WATCHDOG_SCRIPT" watch
        ;;
    snapshot)
        python3 "$UPDATER_SCRIPT" snapshot
        ;;
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -n 50 -f "$LOG_FILE"
        else
            echo "[-] No master log file found."
        fi
        ;;
    *)
        echo "NanoDroid-Core Supervisor (v13.0.0)"
        echo "Usage: nanodroidctl {start|stop|restart|status|ui-tap '<query>'|ui-type '<query>' '<text>'|enqueue ...|clean|watch|snapshot|logs}"
        exit 1
        ;;
esac
