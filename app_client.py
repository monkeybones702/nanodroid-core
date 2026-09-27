import httpx
import sys
import subprocess

BASE_URL = "http://127.0.0.1:8000"

def launch_package_by_keyword(keyword: str):
    client = httpx.Client(timeout=5.0)
    print(f"[*] Querying local FastAPI server for package matching: '{keyword}'...")
    
    try:
        response = client.get(f"{BASE_URL}/system/packages")
        if response.status_code != 200:
            print(f"[!] Failed to fetch packages. Server status: {response.status_code}")
            return
            
        packages = response.json()
        matches = [pkg for pkg in packages if keyword.lower() in pkg.lower()]
        
        if not matches:
            print(f"[!] No installed packages found matching keyword '{keyword}'.")
            return
            
        target_pkg = matches[0]
        print(f"[+] Match found: {target_pkg}")
        if len(matches) > 1:
            print(f"    [i] Multiple matches found, defaulting to first: {matches}")
            
        print(f"[*] Dispatching launch intent via rish binder...")
        cmd = f"rish -c 'am start -p {target_pkg} -c android.intent.category.LAUNCHER 1' || adb shell am start -p {target_pkg} -c android.intent.category.LAUNCHER 1"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if res.returncode == 0:
            print(f"[+] Successfully launched package: {target_pkg}")
        else:
            # Fallback to monkey intent resolver
            fallback = f"rish -c 'monkey -p {target_pkg} -c android.intent.category.LAUNCHER 1'"
            subprocess.run(fallback, shell=True, check=True)
            print(f"[+] Launched via monkey fallback: {target_pkg}")
            
    except Exception as e:
        print(f"[!] Execution error: {str(e)}")

if __name__ == "__main__":
    search_term = sys.argv[1] if len(sys.argv) > 1 else "loophero"
    launch_package_by_keyword(search_term)
