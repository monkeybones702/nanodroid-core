import httpx
import subprocess

def verify_system_integrity():
    print("==========================================")
    print(" NanoDroid-Core System Integrity Audit")
    print("==========================================\n")
    
    # 1. Check Shizuku / rish binder hook
    rish_res = subprocess.run("rish -V", shell=True, capture_output=True, text=True)
    if rish_res.returncode == 0:
        print(f"[+] Shizuku Binder (rish): ONLINE")
        print(f"    -> {rish_res.stdout.strip()}")
    else:
        print("[!] Shizuku Binder (rish): OFFLINE or Unauthorized")

    # 2. Check FastAPI Loopback & Package Endpoint
    try:
        client = httpx.Client(timeout=3.0)
        response = client.get("http://127.0.0.1:8000/system/packages")
        if response.status_code == 200:
            pkg_count = len(response.json())
            print(f"[+] FastAPI Loopback Server: ONLINE")
            print(f"    -> Successfully indexed {pkg_count} packages via API.")
        else:
            print(f"[!] FastAPI Server responded with status code: {response.status_code}")
    except Exception as e:
        print(f"[!] FastAPI Loopback Server: OFFLINE (Start core_server.py)")
        
    print("\n[*] Integrity audit complete.")

if __name__ == "__main__":
    verify_system_integrity()
