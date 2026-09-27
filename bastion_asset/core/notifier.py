import os
import json
import requests

CONFIG_FILE = "webhook_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "webhook_url": "",
        "enabled": False,
        "alert_on": ["BLOCKED", "SANITIZED"]
    }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def send_alert(message, level="WARNING"):
    config = load_config()
    if not config.get("enabled", False) or not config.get("webhook_url"):
        return False
    
    payload = {
        "content": f"🛡️ **AEGISCORE ALERT [{level}]**\n{message}"
    }
    try:
        resp = requests.post(config["webhook_url"], json=payload, timeout=5)
        return resp.status_code in [200, 201, 204]
    except Exception as e:
        print(f"[-] Webhook dispatch failed: {e}")
        return False

def main():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        config = load_config()
        
        print("==============================================")
        print("   🛡️ AEGISCORE: Webhook & Incident Notifier")
        print("==============================================")
        print(f" Status       : {'ENABLED 🟢' if config.get('enabled') else 'DISABLED 🔴'}")
        print(f" Webhook URL  : {config.get('webhook_url') or 'Not Configured'}")
        print("----------------------------------------------")
        print(" [1] Configure Webhook URL")
        print(" [2] Toggle Notifications (Enable/Disable)")
        print(" [3] Test Webhook Dispatch")
        print(" [4] Return to Master Control Hub")
        print("==============================================")
        
        choice = input("aegis-notify> ").strip()
        
        if choice == "1":
            url = input("\nEnter Webhook URL (Discord/Slack/Custom): ").strip()
            if url:
                config["webhook_url"] = url
                save_config(config)
                print("[+] Webhook URL updated successfully.")
            input("\nPress Enter to continue...")
        elif choice == "2":
            current = config.get("enabled", False)
            config["enabled"] = not current
            save_config(config)
            print(f"[+] Notifications toggled to: {'ENABLED' if config['enabled'] else 'DISABLED'}")
            input("\nPress Enter to continue...")
        elif choice == "3":
            print("\n[+] Sending test alert to webhook...")
            success = send_alert("This is a test notification from AegisCore Citadel security suite.", level="INFO")
            if success:
                print("[+] Test alert sent successfully!")
            else:
                print("[-] Failed to send test alert. Check URL or network connection.")
            input("\nPress Enter to continue...")
        elif choice == "4":
            break
        else:
            input("[-] Invalid option. Press Enter to try again...")

if __name__ == "__main__":
    main()
