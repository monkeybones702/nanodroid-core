#!/usr/bin/env python3
import sys
import json
import argparse
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def send_request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"[-] Connection Error: {e.reason}. Is the NanoDroid-Core daemon running? Run './nanodroidctl start'")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error: {str(e)}")
        sys.exit(1)

def cmd_status(args):
    res = send_request("/")
    print(json.dumps(res, indent=2))

def cmd_packages(args):
    res = send_request("/system/packages")
    print(f"[+] Installed Packages ({len(res)} total):")
    for pkg in res[:30]:  # Show first 30
        print(f"  - {pkg}")

def cmd_run_macro(args):
    macro_path = args.file
    try:
        with open(macro_path, "r") as f:
            macro_data = json.load(f)
    except Exception as e:
        print(f"[-] Failed to load macro JSON from {macro_path}: {e}")
        sys.exit(1)
        
    print(f"[*] Dispatching macro '{macro_data.get('macro_name', 'Unnamed')} ({len(macro_data.get('steps', []))} steps)...")
    res = send_request("/macro/execute", method="POST", data=macro_data)
    print(json.dumps(res, indent=2))

def cmd_click(args):
    payload = {"action": "click", "target_text": args.text}
    print(f"[*] Attempting self-healing click for target: '{args.text}'...")
    res = send_request("/ui/execute", method="POST", data=payload)
    print(json.dumps(res, indent=2))

def main():
    parser = argparse.ArgumentParser(description="NanoDroid-Core OmniEngine CLI Runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Status command
    subparsers.add_parser("status", help="Check engine status")
    
    # Packages command
    subparsers.add_parser("packages", help="List installed package names")
    
    # Run macro command
    p_macro = subparsers.add_parser("macro", help="Execute a multi-step macro JSON file")
    p_macro.add_argument("-f", "--file", required=True, help="Path to macro JSON file")
    
    # Click command
    p_click = subparsers.add_parser("click", help="Perform a self-healing click on text")
    p_click.add_argument("-t", "--text", required=True, help="Target UI text to tap")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status(args)
    elif args.command == "packages":
        cmd_packages(args)
    elif args.command == "macro":
        cmd_run_macro(args)
    elif args.command == "click":
        cmd_click(args)

if __name__ == "__main__":
    main()
