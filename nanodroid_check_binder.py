#!/usr/bin/env python3
import subprocess
import json

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

print("==================================================")
print("  NanoDroid-Core: Binder & Gemini Diagnostics     ")
print("==================================================")

# 1. Check rish / Shizuku Binder status
code, out, err = run_cmd("rish -c 'echo BINDER_ACTIVE'")
if code == 0 and "BINDER_ACTIVE" in out:
    print("[+] Shizuku 'rish' Binder Bridge: ONLINE & PRIVILEGED")
else:
    print("[-] Shizuku 'rish' Binder Bridge: OFFLINE or UNAVAILABLE")
    print(f"    Error/Output: {out or err}")

# 2. Check Gemini Package status
pkg = "com.google.android.apps.bard"
code, out, err = run_cmd(f"rish -c 'pm path {pkg}'")
if code == 0 and out.startswith("package:"):
    print(f"[+] Gemini Package ({pkg}): INSTALLED")
    print(f"    Path: {out}")
else:
    print(f"[-] Gemini Package ({pkg}): NOT FOUND or INACCESSIBLE")

# 3. Test uiautomator window node dump capability
dump_path = "/data/local/tmp/test_dump.xml"
code, out, err = run_cmd(f"rish -c 'uiautomator dump {dump_path}'")
if code == 0:
    print("[+] UIAutomator Binder Hook: FUNCTIONAL (Screen tree accessible)")
else:
    print("[-] UIAutomator Binder Hook: FAILED (Ensure screen is unlocked)")
    print(f"    Details: {err}")

print("==================================================")
