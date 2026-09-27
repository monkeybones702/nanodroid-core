#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

# ==============================================================================
# NanoDroid-Core Online LLM Orchestration Bridge (v26.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Cloud Reasoning + Local Shizuku Execution
# ==============================================================================

API_KEY_FILE = os.path.expanduser("~/.nanodroid_api_key")

def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return os.environ.get("NANODROID_API_KEY", "")

def set_api_key(key):
    with open(API_KEY_FILE, "w") as f:
        f.write(key.strip())
    os.chmod(API_KEY_FILE, 0o600)
    print("[+] API Key securely stored in Termux sandbox.")

def query_online_llm(goal, current_context=""):
    api_key = get_api_key()
    if not api_key:
        print("[-] Error: No API key configured. Run: nanodroidctl api-key <your_gemini_key>")
        return None

    print(f"[*] Dispatching goal to Cloud LLM (Gemini API): '{goal}'")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = (
        f"You are the cloud master architect for NanoDroid-Core on a Samsung Galaxy A16. "
        f"User Goal: '{goal}'. "
        f"Context / Last State: '{current_context}'. "
        "Deconstruct this goal into an actionable automation sequence. "
        "Classify into mode: 'intent' (Android system intent), 'bridge' (Gemini-Termux copy-paste bridge), "
        "or 'shell' (Termux shell command). "
        "Return ONLY valid JSON with keys: 'mode', 'target', and 'description'."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 256,
            "responseMimeType": "application/json"
        }
    }
    
    req_data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            candidates = res_body.get("candidates", [])
            if candidates:
                text_response = candidates[0]["content"]["parts"][0]["text"]
                return json.loads(text_response)
    except urllib.error.HTTPError as e:
        print(f"[-] Cloud API HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"[-] Cloud API Request Error: {e}")
        
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 nanodroid_online_llm.py key <api_key>")
        print("  python3 nanodroid_online_llm.py plan '<goal>'")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    if action == "key" and len(sys.argv) > 2:
        set_api_key(sys.argv[2])
    elif action == "plan" and len(sys.argv) > 2:
        plan = query_online_llm(" ".join(sys.argv[2:]))
        print(json.dumps(plan, indent=2) if plan else "[-] Failed to generate plan.")
    else:
        print("[-] Invalid arguments.")
