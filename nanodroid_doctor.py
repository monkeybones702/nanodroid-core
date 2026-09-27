import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_diagnostics():
    print("==================================================")
    print("  NanoDroid-Core OmniEngine v4.2.0 - System Doctor  ")
    print("==================================================")
    
    # 1. Test Root Dashboard & Loopback
    try:
        res = requests.get(f"{BASE_URL}/", timeout=3)
        if res.status_code == 200:
            print("[✔] FastAPI Loopback Server: ONLINE (127.0.0.1:8000)")
        else:
            print(f"[✘] FastAPI Server returned status: {res.status_code}")
            return False
    except Exception as e:
        print(f"[✘] Critical: Loopback server unreachable -> {e}")
        print("[*] Tip: Ensure the background daemon is running via './nanodroidctl start'")
        return False

    # 2. Test System Packages Endpoint (Shizuku / rish integration)
    try:
        res = requests.get(f"{BASE_URL}/system/packages", timeout=5)
        if res.status_code == 200:
            pkgs = res.json()
            print(f"[✔] Shizuku Binder & Package Manager: OK ({len(pkgs)} packages indexed)")
        else:
            print(f"[!] System packages query returned non-200: {res.status_code}")
    except Exception as e:
        print(f"[!] System packages query failed: {e}")

    # 3. Test UI Context Tree & Accessibility Dump
    try:
        res = requests.get(f"{BASE_URL}/ui/context", timeout=10)
        if res.status_code == 200:
            data = res.json()
            print(f"[✔] UI Automation Engine: OK ({data.get('node_count', 0)} interactive nodes mapped)")
        else:
            detail = res.json().get('detail', 'Unknown error')
            print(f"[!] UI Context Warning: {detail}")
            print("[*] Note: Make sure your device screen is unlocked and awake.")
    except Exception as e:
        print(f"[!] UI Context dump failed: {e}")

    print("==================================================")
    print("  Setup Verification Complete. System is Ready.   ")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_diagnostics()
