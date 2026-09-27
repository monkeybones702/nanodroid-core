import subprocess
import time
import datetime
import os

LOG_FILE = "nanodroid.log"

def get_clipboard():
    try:
        result = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=2)
        return result.stdout.strip()
    except Exception:
        return ""

def show_toast(message):
    try:
        subprocess.run(["termux-toast", message], capture_output=True, timeout=1)
    except Exception:
        pass

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

def main():
    print("\n==============================================")
    print("   🤖 NANODROID: Background Clipboard Daemon")
    print("==============================================")
    print(f"[+] Logging active -> {LOG_FILE}")
    print("[+] Monitoring clipboard for instructions...")
    print("[+] Press Ctrl+C to terminate.\n")
    
    last_clip = get_clipboard()
    
    try:
        while True:
            current_clip = get_clipboard()
            if current_clip and current_clip != last_clip:
                log_event(f"New Payload Detected: {current_clip}")
                show_toast("Nanodroid Executing Payload")
                
                try:
                    # Execute and capture output to log file
                    process = subprocess.run(current_clip, shell=True, capture_output=True, text=True)
                    if process.returncode == 0:
                        log_event(f"[SUCCESS] Command executed cleanly.")
                        if process.stdout.strip():
                            log_event(f"Output: {process.stdout.strip()}")
                    else:
                        log_event(f"[ERROR] Exit code {process.returncode}: {process.stderr.strip()}")
                except Exception as e:
                    log_event(f"[EXCEPTION] Execution failed: {e}")
                    
                last_clip = current_clip
            time.sleep(1.5)
    except KeyboardInterrupt:
        log_event("Nanodroid daemon terminated by user.")

if __name__ == "__main__":
    main()
