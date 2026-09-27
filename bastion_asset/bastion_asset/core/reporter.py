import os
import json
from datetime import datetime

LOG_FILE = "bastion_audit.log"
REPORT_FILE = "bastion_security_report.json"

def generate_report():
    if not os.path.exists(LOG_FILE):
        print("[-] No audit log found to analyze.")
        return False

    blocked = []
    sanitized = []
    passed = 0

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(" - ", 2)
            if len(parts) >= 3:
                timestamp, level, message = parts[0], parts[1], parts[2]
                if "BLOCKED" in message:
                    blocked.append({"timestamp": timestamp, "details": message})
                elif "SANITIZED" in message:
                    sanitized.append({"timestamp": timestamp, "details": message})
                elif "PASSED" in message:
                    passed += 1

    report_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_blocked": len(blocked),
            "total_sanitized": len(sanitized),
            "total_passed": passed,
            "total_events": len(blocked) + len(sanitized) + passed
        },
        "blocked_incidents": blocked,
        "sanitized_incidents": sanitized
    }

    with open(REPORT_FILE, "w") as out:
        json.dump(report_data, out, indent=4)
    
    print(f"\n[+] Security report generated successfully -> {REPORT_FILE}")
    return True

def main():
    generate_report()

if __name__ == "__main__":
    main()
