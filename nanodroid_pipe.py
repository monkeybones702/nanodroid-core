import os
import sys
import subprocess

def execute_shell(cmd: str):
    print(f"[*] Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip() and res.returncode != 0:
        print(f"[!] Error: {res.stderr.strip()}")
    return res.returncode == 0

def process_content(content: str, source_name: str = "payload"):
    if not content.strip():
        print(f"[!] Error: Payload from {source_name} is empty.")
        return
        
    if "app = FastAPI" in content or "engine" in source_name:
        dest = os.path.expanduser("~/nanodroid_engine.py")
    elif "agent" in source_name:
        dest = os.path.expanduser("~/nanodroid_agent.py")
    elif "gem" in source_name:
        dest = os.path.expanduser("~/nanodroid_gem.py")
    else:
        dest = os.path.expanduser("~/nanodroid_engine.py") # Default fallback
        
    with open(dest, "w", encoding="utf-8") as out:
        out.write(content)
    print(f"[+] Successfully deployed code to {dest}")
    
    if "nanodroid_engine.py" in dest:
        execute_shell("~/nanodroidctl restart")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "clipboard":
            try:
                res = subprocess.run("termux-clipboard-get", shell=True, capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    process_content(res.stdout.strip(), "clipboard")
                else:
                    print("[!] termux-clipboard-get returned empty. Falling back to ~/payload.txt")
                    raise Exception()
            except Exception:
                payload_path = os.path.expanduser("~/payload.txt")
                if os.path.exists(payload_path):
                    with open(payload_path, "r", encoding="utf-8") as f:
                        process_content(f.read(), "payload.txt")
                else:
                    print(f"[!] Create {payload_path} with your code snippet or configure Termux-API.")
        else:
            if os.path.exists(arg):
                with open(arg, "r", encoding="utf-8") as f:
                    process_content(f.read(), arg)
            else:
                print(f"[!] File not found: {arg}")
    else:
        print("Usage:")
        print("  python3 nanodroid_pipe.py clipboard")
        print("  python3 nanodroid_pipe.py <filename>")
        print("  (If clipboard fails, paste code into ~/payload.txt and run clipboard command)")
