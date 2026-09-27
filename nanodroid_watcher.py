import subprocess
import time
import os

print("[*] NanoDroid Automatic Clipboard Watcher active...")
print("[*] Copy any script block from chat to execute/save it automatically.")

last_clipboard = ""

while True:
    try:
        res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            current_clipboard = res.stdout.strip()
            
            # Detect if clipboard contains a deployable script block or command sequence
            if current_clipboard != last_clipboard and current_clipboard.startswith(("#!", "import ", "cat <<", "pkg ", "python3")):
                print(f"[+] New code snippet detected in clipboard ({len(current_clipboard)} chars).")
                
                # Auto-save to an incoming staging script
                stage_path = os.path.expanduser("~/nanodroid_staging.sh")
                with open(stage_path, "w") as f:
                    f.write(current_clipboard)
                os.chmod(stage_path, 0o755)
                
                print(f"[+] Staged successfully to {stage_path}. Executing...")
                subprocess.run(["bash", stage_path])
                
                last_clipboard = current_clipboard
    except Exception as e:
        # Suppress transient polling errors
        pass
        
    time.sleep(2.0)
