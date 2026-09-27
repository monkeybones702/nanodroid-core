import subprocess
import sys

def get_android_clipboard() -> str | None:
    try:
        # Enforce a 3-second timeout to prevent indefinite hangs
        res = subprocess.run(
            ["termux-clipboard-get"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if res.returncode == 0:
            return res.stdout.strip()
        return None
    except subprocess.TimeoutExpired:
        print("[!] Warning: termux-clipboard-get timed out. Verify Termux:API app permissions.")
        return None
    except FileNotFoundError:
        print("[!] Error: 'termux-api' package is missing. Run 'pkg install termux-api'.")
        return None
    except Exception as e:
        print(f"[!] Unexpected error reading clipboard: {e}")
        return None

def main():
    print("[*] Querying Android system clipboard...")
    snippet = get_android_clipboard()
    if snippet:
        print(f"[+] Clipboard Data: {snippet}")
    else:
        print("[-] Failed to retrieve clipboard content or clipboard is empty.")

if __name__ == "__main__":
    main()
