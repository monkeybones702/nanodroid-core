import httpx
import time
import sys
import subprocess

BASE_URL = "http://127.0.0.1:8000"

def execute_workflow_step(action: str, target_text: str, input_text: str = None, max_scrolls: int = 3):
    client = httpx.Client(timeout=10.0)
    
    for attempt in range(max_scrolls + 1):
        print(f"[*] Querying UI for target text: '{target_text}' (Attempt {attempt + 1}/{max_scrolls + 1})")
        
        try:
            response = client.post(f"{BASE_URL}/ui/query", json={"text": target_text})
            data = response.json()
            
            if data.get("status") == "found":
                print(f"[+] Target found at center coordinates: {data['center']}")
                
                exec_payload = {
                    "action": action,
                    "target": {"text": target_text},
                    "input_text": input_text
                }
                exec_resp = client.post(f"{BASE_URL}/ui/execute", json=exec_payload)
                print(f"[+] Execution Result: {exec_resp.json()}")
                return True
                
            elif attempt < max_scrolls:
                print("[-] Target not visible. Executing dynamic scroll gesture via Shizuku...")
                subprocess.run(
                    "rish -c 'input swipe 500 1600 500 600 300' || adb shell input swipe 500 1600 500 600 300", 
                    shell=True, check=True
                )
                time.sleep(1.0)
            else:
                print(f"[!] Target '{target_text}' could not be located after {max_scrolls} scroll attempts.")
                return False
                
        except Exception as e:
            print(f"[!] Workflow execution error: {str(e)}")
            return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Battery"
    print(f"[*] Initializing NanoDroid-Core Workflow for target: '{target}'")
    execute_workflow_step(action="click", target_text=target)
