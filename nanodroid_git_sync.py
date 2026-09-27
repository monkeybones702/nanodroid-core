#!/usr/bin/env python3
import os
import subprocess

# ==============================================================================
# NanoDroid-Core GitHub Synchronization Engine (v28.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Automated Git Commit & GitHub Push
# ==============================================================================

HOME_DIR = os.path.expanduser("~")
REPO_NAME = "monkeybones702/nanodroid-core"

def run_cmd(cmd):
    print(f"[*] Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip() and res.returncode != 0:
        print(f"[-] Error: {res.stderr.strip()}")
    return res.returncode == 0

def sync_repository():
    os.chdir(HOME_DIR)
    print(f"[*] Synchronizing NanoDroid-Core components from {HOME_DIR}...")
    
    # 1. Initialize git if not already initialized
    if not os.path.exists(".git"):
        print("[*] Initializing local Git repository...")
        run_cmd("git init")
        run_cmd("git branch -M main")
        
    # 2. Check if remote exists, if not, create repo via GitHub CLI (gh)
    remotes = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
    if remotes.returncode != 0:
        print(f"[*] Configuring GitHub remote for {REPO_NAME}...")
        # Check if gh is authenticated
        auth_check = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if auth_check.returncode != 0:
            print("[-] GitHub CLI (gh) is not authenticated. Please run 'gh auth login' first.")
            return False
            
        # Try creating the repo on GitHub (will succeed or report already exists)
        run_cmd(f"gh repo create {REPO_NAME} --public --confirm")
        run_cmd(f"git remote add origin https://github.com/{REPO_NAME}.git")
        
    # 3. Stage all NanoDroid core files
    files_to_sync = [
        "nanodroidctl",
        "nanodroid_executive.py",
        "nanodroid_shizuku_bridge.py",
        "nanodroid_vision.py",
        "nanodroid_optimizer.py",
        "nanodroid_bridge.py",
        "nanodroid_online_llm.py",
        "nanodroid_intent_engine.py",
        "nanodroid_ui_parser.py"
    ]
    
    staged_count = 0
    for f in files_to_sync:
        if os.path.exists(f):
            run_cmd(f"git add {f}")
            staged_count += 1
            
    if staged_count == 0:
        print("[-] No NanoDroid core files found to sync.")
        return False
        
    # 4. Commit and push
    commit_msg = "NanoDroid-Core v28.0.0: Hybrid Executive, Cloud/Local LLM Bridge, Self-Healing Vision & Optimizer"
    run_cmd(f'git commit -m "{commit_msg}"')
    
    print("[*] Pushing updates to GitHub (main branch)...")
    success = run_cmd("git push -u origin main")
    
    if success:
        print(f"[+] Successfully synchronized repository to https://github.com/{REPO_NAME}")
    else:
        print("[-] Push failed. Check your network connection or branch protection rules.")
    return success

if __name__ == "__main__":
    sync_repository()
