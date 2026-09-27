import subprocess
import time

def get_clipboard():
    try:
        result = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=2)
        return result.stdout.strip()
    except Exception:
        return ""

def main():
    print("\n==============================================")
    print("   🤖 NANODROID: Background Clipboard Daemon")
    print("==============================================")
    print("[+] Monitoring clipboard for instructions...")
    
    last_clip = get_clipboard()
    
    try:
        while True:
            current_clip = get_clipboard()
            if current_clip and current_clip != last_clip:
                print(f"\n[⚡] New Payload Detected: {current_clip}")
                try:
                    subprocess.Popen(current_clip, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("[✔] Command dispatched to background execution.")
                except Exception as e:
                    print(f"[-] Execution failed: {e}")
                last_clip = current_clip
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n[-] Nanodroid daemon terminated.")

if __name__ == "__main__":
    main()
