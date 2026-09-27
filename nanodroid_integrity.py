#!/usr/bin/env python3
import os
import sys
import hashlib
import subprocess

# ==============================================================================
# NanoDroid-Core File Integrity & Manifest Verifier (v17.4.0)
# Target: Samsung Galaxy A16 (ARM64) | SHA-256 Checksum & Git Tree Validation
# ==============================================================================

HOME_DIR = os.path.expanduser("~")
MANIFEST_PATH = os.path.join(HOME_DIR, "MANIFEST.sha256")

MANAGED_FILES = [
    "nanodroidctl",
    "nanodroid_watchdog.py",
    "nanodroid_scheduler.py",
    "nanodroid_updater.py",
    "nanodroid_queue.py",
    "nanodroid_ws_hub.py",
    "nanodroid_ui_navigator.py",
    "nanodroid_macro.py",
    "nanodroid_agent.py",
    "nanodroid_terminate.py",
    "nanodroid_git_sync.py",
    "nanodroid_integrity.py"
]

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return None

def generate_manifest():
    print("[*] Generating SHA-256 integrity baseline manifest...")
    manifest_data = {}
    for filename in MANAGED_FILES:
        filepath = os.path.join(HOME_DIR, filename)
        if os.path.exists(filepath):
            file_hash = compute_sha256(filepath)
            if file_hash:
                manifest_data[filename] = file_hash
                print(f"    [HASHED] {filename} -> {file_hash[:12]}...")
        else:
            print(f"    [MISSING] {filename}")

    with open(MANIFEST_PATH, "w") as f:
        for fname, fhash in manifest_data.items():
            f.write(f"{fhash}  {fname}\n")
    print(f"[+] Integrity manifest successfully written to {MANIFEST_PATH}")

def verify_integrity():
    if not os.path.exists(MANIFEST_PATH):
        print("[-] No integrity manifest found. Run 'nanodroidctl integrity-gen' first.")
        return False

    print("[*] Verifying NanoDroid-Core file integrity against baseline...")
    stored_manifest = {}
    with open(MANIFEST_PATH, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                stored_manifest[parts[1]] = parts[0]

    integrity_passed = True
    for filename in MANAGED_FILES:
        filepath = os.path.join(HOME_DIR, filename)
        if not os.path.exists(filepath):
            print(f"    [-] CRITICAL: Managed file missing: {filename}")
            integrity_passed = False
            continue

        current_hash = compute_sha256(filepath)
        expected_hash = stored_manifest.get(filename)

        if not expected_hash:
            print(f"    [!] WARNING: Untracked managed file: {filename}")
        elif current_hash != expected_hash:
            print(f"    [-] CORRUPTION DETECTED: {filename} hash mismatch!")
            print(f"        Expected: {expected_hash}")
            print(f"        Got:      {current_hash}")
            integrity_passed = False
        else:
            print(f"    [OK] {filename}")

    # Also check Git status for dirty working tree
    res = subprocess.run(["git", "status", "--porcelain"], cwd=HOME_DIR, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        print("\n[!] Notice: Git working tree contains uncommitted changes:")
        for line in res.stdout.strip().split("\n"):
            print(f"    {line}")

    if integrity_passed:
        print("\n[+] All core automation modules verified intact.")
        return True
    else:
        print("\n[-] Integrity check FAILED. Investigate modified or corrupted files.")
        return False

if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "verify"
    if action == "generate":
        generate_manifest()
    elif action == "verify":
        verify_integrity()
    else:
        print("Usage: python3 nanodroid_integrity.py {verify|generate}")
        sys.exit(1)
