import sys
import json
import requests

PROXY_URL = "http://127.0.0.1:8081"

def main():
    if len(sys.argv) < 2:
        print("Usage: aegis-send \"Your prompt text here\"")
        sys.exit(1)
        
    prompt_text = " ".join(sys.argv[1:])
    payload = {"prompt": prompt_text}
    
    print(f"\n[📤] Sending prompt to GatewayZero Proxy: \"{prompt_text}\"")
    
    try:
        response = requests.post(PROXY_URL, json=payload, timeout=5)
        print(f"[📥] Response Status: {response.status_code}")
        print(f"[📄] Response Body: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("[-] Error: Could not connect to GatewayZero Proxy. Is `aegis-proxy` running?")
    except Exception as e:
        print(f"[-] Request failed: {e}")

if __name__ == "__main__":
    main()
