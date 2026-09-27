import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def test_workflow():
    print("[*] Testing NanoDroid-Core Shizuku Bridge & UI Query...")
    
    # 1. Test Query Endpoint (Looking for a common node like 'Settings' or any app text)
    query_payload = {
        "text": "Settings"
    }
    
    try:
        print("[*] Dispatching POST /ui/query...")
        response = httpx.post(f"{BASE_URL}/ui/query", json=query_payload, timeout=5.0)
        print(f"[*] Query Status Code: {response.status_code}")
        data = response.json()
        print(f"[*] Query Result: {json.dumps(data, indent=2)}")
        
        if data.get("status") == "found":
            print(f"[+] Target located at Center: {data['center']}")
            
            # 2. Test Execution Endpoint (Optional: Uncomment to execute a click)
            # exec_payload = {
            #     "action": "click",
            #     "target": {"text": "Settings"}
            # }
            # exec_resp = httpx.post(f"{BASE_URL}/ui/execute", json=exec_payload, timeout=5.0)
            # print(f"[*] Execution Response: {exec_resp.json()}")
        else:
            print("[!] Node not found on screen. Ensure target text is visible.")
            
    except Exception as e:
        print(f"[!] Connection or Request failed: {str(e)}")

if __name__ == "__main__":
    test_workflow()
