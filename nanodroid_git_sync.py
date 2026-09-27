#!/usr/bin/env python3
import os
import sys
import subprocess

# ==============================================================================
# NanoDroid-Core Git Repository Sync & Creation Utility (v17.3.0)
# Target: Samsung Galaxy A16 (ARM64) | Automated GitHub CLI Provisioning
# ==============================================================================

HOME_DIR = os.path.expanduser("~")
REPO_NAME = "nanodroid-core"

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

def run_cmd(args, cwd=HOME_DIR):
    res = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def setup_repository():
    print("[*] Initializing NanoDroid-Core Git environment...")
    
    # Ensure git and gh are available
    if run_cmd(["git", "--version"])[0] != 0:
        print("[-] Git is missing. Run: pkg install git")
        return False
        
    if run_cmd(["gh", "--version"])[0] != 0:
        print("[-] GitHub CLI (gh) is missing. Run: pkg install gh")
        return False

    git_dir = os.path.join(HOME_DIR, ".git")
    if not os.path.exists(git_dir):
        run_cmd(["git", "init"])

    # Enforce local identity
    run_cmd(["git", "config", "user.name", "NanoDroid-Architect"])
    run_cmd(["git", "config", "user.email", "nanodroid@apexarchitect.local"])

    # Write .gitignore
    with open(os.path.join(HOME_DIR, ".gitignore"), "w") as f:
        f.write(GITIGNORE_CONTENT)
    print("[+] .gitignore configured for runtime isolation.")

    # Stage files
    print("[+] Staging NanoDroid-Core automation scripts...")
    for filename in MANAGED_FILES:
        if os.path.exists(os.path.join(HOME_DIR, filename)):
            run_cmd(["git", "add", filename])
            print(f"    Staged: {filename}")
    run_cmd(["git", "add", ".gitignore"])

    # Commit
    code, out, err = run_cmd(["git", "commit", "-m", "NanoDroid-Core v17.3.0: Full Ecosystem Release"])
    if code == 0 or "nothing to commit" in out:
        print("[+] Local commit successful.")

    # Check GitHub CLI authentication status
    auth_code, _, _ = run_cmd(["gh", "auth", "status"])
    if auth_code != 0:
        print("\n[!] Authentication Required: Please authenticate GitHub CLI.")
        print("Run the following command first, then re-run sync:")
        print("    gh auth login\n")
        return False

    # Create remote repo and push using GitHub CLI
    print(f"[*] Provisioning remote repository '{REPO_NAME}' on GitHub...")
    # Try creating repo (if it already exists, gh will report and we proceed to push)
    run_cmd(["gh", "repo", "create", REPO_NAME, "--public", "--description", "NanoDroid-Core Automation Suite for Samsung Galaxy A16 (ARM64)"])

    print("[*] Linking remote origin and pushing main branch...")
    run_cmd(["git", "branch", "-M", "main"])
    
    # Set remote and push
    username_res = run_cmd(["gh", "api", "user", "--jq", ".login"])
    gh_user = username_res[1] if username_res[0] == 0 else "monkeybones702"
    remote_url = f"https://github.com/{gh_user}/{REPO_NAME}.git"
    
    run_cmd(["git", "remote", "remove", "origin"])
    run_cmd(["git", "remote", "add", "origin", remote_url])
    
    push_code, push_out, push_err = run_cmd(["git", "push", "-u", "origin", "main"])
    if push_code == 0:
        print(f"\n[+] SUCCESS! Repository created and pushed to: {remote_url}")
        return True
    else:
        print(f"[-] Push output: {push_out}\n[-] Error: {push_err}")
        return False

if __name__ == "__main__":
    setup_repository()
