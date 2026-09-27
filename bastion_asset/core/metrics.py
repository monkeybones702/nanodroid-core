import os
import re

LOG_FILE = "bastion_audit.log"
VAULT_DIR = "bastion_vault"

def analyze_logs():
    total = 0
    blocked = 0
    sanitized = 0
    passed = 0
    keywords_hit = {}

    files_to_check = [LOG_FILE]
    if os.path.exists(VAULT_DIR):
        for f in os.listdir(VAULT_DIR):
            if f.endswith(".log"):
                files_to_check.append(os.path.join(VAULT_DIR, f))

    for filepath in files_to_check:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    total += 1
                    if "BLOCKED" in line:
                        blocked += 1
                    elif "SANITIZED" in line:
                        sanitized += 1
                    elif "PASSED" in line:
                        passed += 1
                    
                    # Extract keywords if present
                    if "Direct Threat Keyword" in line or "Keyword" in line:
                        match = re.search(r"'(.*?)'", line)
                        if match:
                            kw = match.group(1)
                            keywords_hit[kw] = keywords_hit.get(kw, 0) + 1
        except Exception:
            pass

    return total, blocked, sanitized, passed, keywords_hit

def draw_bar(val, max_val, width=25):
    if max_val == 0:
        filled = 0
    else:
        filled = int((val / max_val) * width)
    return "█" * filled + "░" * (width - filled)

def main():
    print("==============================================")
    print("   🛡️ AEGISCORE: Threat Analytics Dashboard")
    print("==============================================")
    
    total, blocked, sanitized, passed, keywords = analyze_logs()

    if total == 0:
        print("\n[-] No security event logs found to analyze yet.")
        input("\nPress Enter to return...")
        return

    block_pct = (blocked / total) * 100 if total > 0 else 0
    sanitize_pct = (sanitized / total) * 100 if total > 0 else 0
    pass_pct = (passed / total) * 100 if total > 0 else 0

    print(f"\n[📊] Overall Audit Scope: {total} total recorded events\n")
    print(f"  • Blocked Threats  : {blocked:3d} ({block_pct:5.1f}%) {draw_bar(blocked, total)}")
    print(f"  • Sanitized Leaks  : {sanitized:3d} ({sanitize_pct:5.1f}%) {draw_bar(sanitized, total)}")
    print(f"  • Passed Requests  : {passed:3d} ({pass_pct:5.1f}%) {draw_bar(passed, total)}")

    print("\n----------------------------------------------")
    print(" 🔍 Top Triggered Threat Indicators:")
    if keywords:
        sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
        for kw, count in sorted_kw:
            print(f"  - '{kw}': {count} hits")
    else:
        print("  - No specific keyword frequency data recorded.")

    # Calculate basic security posture rating
    print("\n----------------------------------------------")
    if block_pct > 30:
        posture = "🛡️ HIGH ALERT (Frequent attack vectors intercepted)"
    elif block_pct > 10:
        posture = "⚠️ MODERATE (Active proxy mitigation in effect)"
    else:
        posture = "🟢 SECURE / NOMINAL (Clean traffic profile)"
    print(f" Posture Rating: {posture}")
    print("==============================================")
    input("\nPress Enter to return to hub...")

if __name__ == "__main__":
    main()
