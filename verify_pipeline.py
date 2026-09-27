import requests
import sys
import json

BASE_URL = "http://127.0.0.1:8000"

def test_pipeline():
    print("==================================================")
    print("  NanoDroid-Core Pipeline Verification Suite      ")
    print("==================================================")
    
    success_count = 0
    total_tests = 4

    # 1. Test Loopback Server & FastAPI Daemon
    try:
        res = requests.get(f"{BASE_URL}/", timeout=3)
        if res.status_code == 200:
            data = res.json()
            print(f"[✔] Layer 1 (FastAPI Loopback): ONLINE ({data.get('engine')})")
            success_count += 1
        else:
            print(f"[✘] Layer 1 (FastAPI Loopback): FAILED (Status {res.status_code})")
    except Exception as e:
        print(f"[✘] Layer 1 (FastAPI Loopback): UNREACHABLE -> {e}")
        print("    [*] Tip: Start daemon with './nanodroidctl start'")
        return

    # 2. Test Shizuku / rish Binder Bridge (Package Enumeration)
    try:
        res = requests.get(f"{BASE_URL}/system/packages", timeout=5)
        if res.status_code == 200:
            pkgs = res.json()
            print(f"[✔] Layer 2 (Shizuku Binder): OK ({len(pkgs)} packages indexed via rish)")
            success_count += 1
        else:
            print(f"[✘] Layer 2 (Shizuku Binder): FAILED (Status {res.status_code})")
    except Exception as e:
        print(f"[✘] Layer 2 (Shizuku Binder): ERROR -> {e}")

    # 3. Test UI Accessibility Tree Dump & Self-Healing Parser
    try:
        res = requests.get(f"{BASE_URL}/ui/context", timeout=10)
        if res.status_code == 200:
            data = res.json()
            print(f"[✔] Layer 3 (UI Automation Tree): OK ({data.get('node_count', 0)} nodes parsed)")
            success_count += 1
        else:
            print(f"[✘] Layer 3 (UI Automation Tree): FAILED -> {res.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"[✘] Layer 3 (UI Automation Tree): ERROR -> {e}")

    # 4. Test Action Execution Dispatch (Safe Keyevent: Home / Keycode 3)
    try:
        payload = {"action": "keyevent", "key_code": 3}
        res = requests.post(f"{BASE_URL}/ui/execute", json=payload, timeout=5)
        if res.status_code == 200:
            print("[✔] Layer 4 (Action Dispatcher): OK (Home keyevent dispatched successfully)")
            success_count += 1
        else:
            print(f"[✘] Layer 4 (Action Dispatcher): FAILED (Status {res.status_code})")
    except Exception as e:
        print(f"[✘] Layer 4 (Action Dispatcher): ERROR -> {e}")

    print("==================================================")
    print(f"  Verification Result: {success_count}/{total_tests} Subsystems Operational")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()
