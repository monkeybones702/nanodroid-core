import sys
import json
import time
import httpx
from typing import Optional, Dict, Any, List

BASE_URL = "http://127.0.0.1:8000"

def ask_yes_no(prompt: str) -> bool:
    """Enforces strict binary y/n user interaction."""
    while True:
        try:
            choice = input(f"[?] {prompt} (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            print("Invalid input. Please enter 'y' or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Operation aborted by user.")
            sys.exit(0)

def api_request(endpoint: str, method: str = "GET", payload: Optional[Dict] = None) -> Optional[Any]:
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            res = httpx.get(url, timeout=15.0)
        else:
            res = httpx.post(url, json=payload, timeout=15.0)
        return res.json()
    except Exception as e:
        print(f"[!] API Connection Error ({endpoint}): {e}")
        return None

def execute_omni_action(payload: Dict[str, Any]) -> Optional[Dict]:
    return api_request("/ui/execute", method="POST", payload=payload)

def get_screen_context() -> Optional[Dict[str, Any]]:
    return api_request("/ui/context", method="GET")

def run_autonomous_extraction_loop(target_query: str = "back"):
    print(f"[*] Initializing NanoDroid-Gem Autonomous Loop targeting: '{target_query}'")
    
    if not ask_yes_no("Do you want to initiate the autonomous screen scan and execution cycle?"):
        print("[*] Cycle aborted.")
        return

    max_cycles = 5
    cycle = 0

    while cycle < max_cycles:
        cycle += 1
        print(f"\n--- Autonomous Cycle {cycle}/{max_cycles} ---")
        
        # 1. Fetch live UI context
        ctx = get_screen_context()
        if not ctx or "elements" not in ctx:
            print("[!] Failed to retrieve screen context. Retrying...")
            time.sleep(2.0)
            continue
            
        elements = ctx.get("elements", [])
        print(f"[*] Scanned {len(elements)} interactive nodes on screen.")
        
        # 2. Locate target commands (e.g., back commands or matching elements)
        matched_element = None
        for el in elements:
            text = (el.get("text") or "").lower()
            desc = (el.get("desc") or "").lower()
            elem_id = (el.get("id") or "").lower()
            
            if target_query in text or target_query in desc or target_query in elem_id:
                matched_element = el
                break
                
        if matched_element:
            target_text = matched_element.get("text") or matched_element.get("id") or target_query
            print(f"[+] Located target: '{target_text}' at center {matched_element.get('center')}")
            
            if ask_yes_no(f"Execute action on located target '{target_text}'?"):
                # 3. Copy / Execute
                payload = {"action": "click", "target_text": target_text}
                result = execute_omni_action(payload)
                print(f"[+] Execution Result Sent to Gemini Pipeline: {json.dumps(result, indent=2)}")
                
                # 4. Wait until complete
                print("[*] Waiting for UI state stabilization...")
                time.sleep(2.5)
            else:
                print("[*] Skipping this target per user instruction.")
        else:
            print(f"[-] No target matching '{target_query}' visible on current screen view.")
            if ask_yes_no("Perform kinetic scroll gesture to reveal more items?"):
                # Scroll down action via omni-engine
                scroll_payload = {"action": "swipe", "x": 540, "y": 1600, "end_x": 540, "end_y": 600, "duration_ms": 300}
                execute_omni_action(scroll_payload)
                print("[*] Scroll dispatched. Waiting for render...")
                time.sleep(2.0)
            else:
                print("[*] Stopping scan cycle.")
                break

        if cycle < max_cycles:
            if not ask_yes_no("Continue to the next item / cycle?"):
                print("[*] Autonomous loop terminated by user.")
                break

    print("\n[+] NanoDroid-Gem Autonomous Loop completed successfully.")

if __name__ == "__main__":
    query = "back"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    run_autonomous_extraction_loop(query)
