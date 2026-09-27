import os
import subprocess
import tempfile
import shutil
import time
import sys

def send_notification(title, message):
    try:
        subprocess.run(["termux-notification", "--title", title, "--content", message, "--priority", "high"], check=False)
    except Exception:
        pass

def get_clipboard():
    try:
        res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def main():
    print("==============================================")
    print("   📋 AEGISCORE: Continuous Clipboard Daemon")
    print("==============================================")
    print("[+] Monitoring clipboard for new text... Press Ctrl+C to stop.\n")
    
    last_content = get_clipboard()
    if last_content:
        print(f"[-] Initial clipboard loaded ({len(last_content)} chars). Waiting for new copies...")

    try:
        while True:
            current_content = get_clipboard()
            if current_content and current_content != last_content:
                last_content = current_content
                print(f"\n[+] New clipboard entry detected ({len(current_content)} chars):")
                print("-" * 46)
                print(current_content[:300] + ("..." if len(current_content) > 300 else ""))
                print("-" * 46)

                send_notification("AegisCore Clipboard Exec", "New clipboard entry detected & executing!")
                print("[+] Confirmation notification sent. Launching execution window...")

                script_fd, script_path = tempfile.mkstemp(suffix=".sh", prefix="aegis_exec_")
                os.close(script_fd)
                
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write("#!/data/data/com.termux/files/usr/bin/bash\n")
                    f.write("echo '=== AegisCore Clipboard Execution Window ==='\n")
                    f.write(current_content + "\n")
                    f.write("\necho '=============================================='\n")
                    f.write("echo 'Execution finished.'\n")

                os.chmod(script_path, 0o755)

                try:
                    if shutil.which("tmux"):
                        subprocess.run(["tmux", "new-window", f"bash {script_path}"])
                        print("[+] Started in new tmux window.")
                    else:
                        subprocess.run(["bash", script_path])
                except Exception as e:
                    print(f"[-] Error launching execution window: {e}")
                    os.system(f"bash {script_path}")

            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n[+] Continuous clipboard daemon stopped. Returning to hub...")

if __name__ == "__main__":
    main()
