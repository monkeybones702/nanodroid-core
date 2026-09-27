#!/usr/bin/env python3
import os
import sys
import subprocess

# ==============================================================================
# NanoDroid-Core Git Repository Sync & Release Utility (v17.2.0)
# Target: Samsung Galaxy A16 (ARM64) | Robust Identity & Remote Push
# ==============================================================================

HOME_DIR = os.path.expanduser("~")

GITIGNORE_CONTENT = """# NanoDroid-Core Volatile & Runtime Artifacts
*.db
*.pid
*.log
*.json
*.xml
.nanodroid_*
__pycache__/
.cache/
"""

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
    "nanodroid_git_sync.py"
]

def run_git(args):
    res = subprocess.run(["git"] + args, cwd=HOME_DIR, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def initialize_and_sync(repo_url=None):
    print("[*] Checking Git environment...")
    code, out, err = run_git(["--version"])
    if code != 0:
        print("[-] Git is not installed. Please run: pkg install git")
        return False

    git_dir = os.path.join(HOME_DIR, ".git")
    if not os.path.exists(git_dir):
        print("[+] Initializing local Git repository...")
        run_git(["init"])

    # Always enforce local repository identity configuration
    run_git(["config", "user.name", "NanoDroid-Architect"])
    run_git(["config", "user.email", "nanodroid@apexarchitect.local"])
    print("[+] Git author identity configured.")

    # Write .gitignore
    gitignore_path = os.path.join(HOME_DIR, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write(GITIGNORE_CONTENT)
    print("[+] Updated .gitignore for runtime isolation.")

    # Add managed files
    print("[+] Staging NanoDroid-Core automation modules...")
    for filename in MANAGED_FILES:
        filepath = os.path.join(HOME_DIR, filename)
        if os.path.exists(filepath):
            run_git(["add", filename])
            print(f"    Staged: {filename}")
        else:
            print(f"    Skipped (not found): {filename}")

    run_git(["add", ".gitignore"])

    # Commit changes
    commit_msg = "NanoDroid-Core v17.0.0: Intent-Aware Agent & Full Ecosystem Release"
    code, out, err = run_git(["commit", "-m", commit_msg])
    if code == 0 or "nothing to commit" in out or "nothing to commit" in err:
        print(f"[+] Commit status: Success / Up to date.")
    else:
        print(f"[-] Commit notice: {out} {err}")

    # Handle remote configuration if URL provided
    if repo_url:
        print(f"[*] Configuring remote origin: {repo_url}")
        run_git(["remote", "remove", "origin"])
        code, out, err = run_git(["remote", "add", "origin", repo_url])
        if code != 0:
            print(f"[-] Failed to set remote origin: {err}")
            return False

        print("[*] Pushing main branch to remote GitHub repository...")
        run_git(["branch", "-M", "main"])
        p_code, p_out, p_err = run_git(["push", "-u", "origin", "main"])
        if p_code == 0:
            print("[+] Successfully pushed NanoDroid-Core to GitHub!")
            return True
        else:
            print(f"[-] Push failed. Please verify your GitHub credentials or Personal Access Token:\n{p_err}")
            return False
    else:
        print("[+] Local Git synchronization complete. Run with remote URL to push.")
        return True

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    initialize_and_sync(url)
