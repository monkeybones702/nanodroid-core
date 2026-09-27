#!/usr/bin/env python3
"""
================================================================================
GEMINI TERMUX MACRO RUNNER (Ultra-Low Token Loop with Android Intents)
Model Target : gemini-2.5-flash
Token Mode   : EXTREME (Minimal Tokens Engine)
Watchdog     : 14s (Auto-"continue" UI Intent)
Error Limit  : 5 loops
================================================================================
"""

import os
import sys
import re
import time
import subprocess
import shutil

# CONFIGURATION
MODEL = "gemini-2.5-flash"
INPUT_X = 540
INPUT_Y = 2200
SEND_X = 980
SEND_Y = 2200
WATCHDOG_TIMEOUT = 14
EXEC_TIMEOUT = 45
MAX_ERROR_LOOPS = 5
TARGET_APP = "browser"
BROWSER_URL = "https://gemini.google.com/app"
USE_MODE = "none"  # none | root_tsu | adb_wifi
STRIP_COMMENTS = True
TRUNCATE_ERR_LINES = 5

RUNNER_SCRIPT_PATH = os.path.expanduser("~/gemini_exec_temp.sh")
LAST_CLIPBOARD_FILE = os.path.expanduser("~/.gemini_last_clip.txt")

def run_cmd(cmd_list, shell=False):
    """Run shell command safely in Termux"""
    try:
        res = subprocess.run(cmd_list, shell=shell, capture_output=True, text=True)
        return res.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def send_android_ui_command(cmd_str):
    """Dispatch UI screen interaction via Intent, su, or Termux tools"""
    if USE_MODE == "adb_wifi":
        full_cmd = f"adb shell {cmd_str}"
    elif USE_MODE == "root_tsu":
        full_cmd = f"su -c '{cmd_str}'"
    else:
        full_cmd = cmd_str
    
    subprocess.run(full_cmd, shell=True, capture_output=True)

def open_gemini_ui():
    """Launch Gemini window via Android View Intent"""
    print("[INTENT] Launching Gemini surface...")
    if TARGET_APP == "gemini_app":
        send_android_ui_command("am start -a android.intent.action.VIEW -d 'https://gemini.google.com/app'")
    elif TARGET_APP == "tasker_intent":
        send_android_ui_command("am broadcast -a net.dinglisch.android.tasker.ACTION_TASK --es task_name 'OpenGemini'")
    else:
        send_android_ui_command(f"am start -a android.intent.action.VIEW -d '{BROWSER_URL}'")
    time.sleep(1.5)

def type_continue_to_gemini():
    """Watchdog triggered: auto-types 'continue' intent into Gemini UI"""
    print("[WATCHDOG] Gemini stalled or silent! Typing 'continue' via Intent...")
    open_gemini_ui()
    
    # 1. Tap input box
    send_android_ui_command(f"input tap {INPUT_X} {INPUT_Y}")
    time.sleep(0.3)
    
    # 2. Type 'continue' (minimal tokens)
    send_android_ui_command("input text continue")
    time.sleep(0.2)
    
    # 3. Press Enter / Tap Send
    send_android_ui_command("input keyevent 66")  # Keycode 66 = Enter
    send_android_ui_command(f"input tap {SEND_X} {SEND_Y}")
    
    # Notify user
    subprocess.run(["termux-notification", "--title", "Gemini Watchdog", "--content", "Dispatched 'continue' intent"], capture_output=True)

def get_clipboard():
    """Fetch clipboard contents via Termux:API"""
    try:
        res = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=5)
        return res.stdout
    except Exception:
        return ""

def set_clipboard(text):
    """Set clipboard contents via Termux:API"""
    try:
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=text, timeout=5)
    except Exception as e:
        print(f"[WARN] Failed to set clipboard: {e}")

def extract_bash_block(text):
    """Extract bash code from markdown code block or fallback to raw content"""
    if not text:
        return ""
    match = re.search(r"```(?:bash|sh)?s*\n([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        code = match.group(1).strip()
    else:
        lines = [l for l in text.splitlines() if not l.startswith("Here is") and not l.startswith("```")]
        code = "\n".join(lines).strip()
    
    if STRIP_COMMENTS:
        clean_lines = [l for l in code.splitlines() if not l.strip().startswith("#")]
        code = "\n".join(clean_lines).strip()
        
    return code

def compress_error(raw_stderr, exit_code):
    """Compress stderr to absolute minimum token footprint for Gemini 2.5"""
    clean_err = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_stderr)
    lines = [l.strip() for l in clean_err.splitlines() if l.strip()]
    compact_lines = lines[-TRUNCATE_ERR_LINES:] if len(lines) > TRUNCATE_ERR_LINES else lines
    joined_err = "\n".join(compact_lines)
    return f"ERR exit {exit_code}:\n{joined_err}\nOutput ONLY fixed ```bash``` block."

def execute_bash_code(code_text):
    """Writes code to temp script and runs with bash"""
    with open(RUNNER_SCRIPT_PATH, "w") as f:
        f.write("#!/bin/bash\nset -e\n" + code_text + "\n")
    
    os.chmod(RUNNER_SCRIPT_PATH, 0o755)
    print("--------------------------------------------------")
    print(f"[RUNNING] Executing bash code ({len(code_text.splitlines())} lines)...")
    print("--------------------------------------------------")
    
    try:
        proc = subprocess.run(
            ["bash", RUNNER_SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"Timeout expired after {EXEC_TIMEOUT}s"
    except Exception as e:
        return 1, "", str(e)

def send_error_to_gemini(error_prompt):
    """Copy compressed error and switch to Gemini UI to paste and run"""
    print("[LOOP] Copying compact error to clipboard & switching to Gemini...")
    set_clipboard(error_prompt)
    
    open_gemini_ui()
    send_android_ui_command(f"input tap {INPUT_X} {INPUT_Y}")
    time.sleep(0.3)
    
    send_android_ui_command("input keyevent 279")  # KEYCODE_PASTE
    time.sleep(0.3)
    send_android_ui_command("input keyevent 66")   # KEYCODE_ENTER
    send_android_ui_command(f"input tap {SEND_X} {SEND_Y}")
    
    subprocess.run(["termux-notification", "--title", "Gemini Loop", "--content", "Sent error back to Gemini"], capture_output=True)

def main():
    print("==================================================")
    print("  GEMINI TERMUX MACRO RUNNER STARTED")
    print("  Listening for copied Gemini bash code...")
    print("==================================================")
    
    last_clip = ""
    error_loop_count = 0
    waiting_start_time = None
    continue_sent_for_current_wait = False

    while True:
        clip = get_clipboard()
        
        if clip and clip != last_clip and ("```" in clip or "#!/bin" in clip or "sudo" in clip or "pkg " in clip or "apt " in clip):
            last_clip = clip
            waiting_start_time = None
            continue_sent_for_current_wait = False
            
            bash_code = extract_bash_block(clip)
            if not bash_code:
                time.sleep(1)
                continue
                
            print(f"\n[NEW CODE DETECTED] ({len(bash_code)} chars)")
            returncode, stdout, stderr = execute_bash_code(bash_code)
            
            if returncode == 0:
                print("\n[SUCCESS] Code executed successfully with code 0!")
                if stdout:
                    print(f"Output:\n{stdout}")
                error_loop_count = 0
                subprocess.run(["termux-vibrate", "-d", "100"], capture_output=True)
                subprocess.run(["termux-notification", "--title", "Gemini Success", "--content", "Bash executed successfully!"], capture_output=True)
            else:
                error_loop_count += 1
                print(f"\n[FAIL] Exit code {returncode} (Loop {error_loop_count}/{MAX_ERROR_LOOPS})")
                print(f"Stderr: {stderr}")
                
                if error_loop_count > MAX_ERROR_LOOPS:
                    print("[ABORT] Reached max error loops. Pausing macro.")
                    break
                    
                repair_prompt = compress_error(stderr, returncode)
                send_error_to_gemini(repair_prompt)
                
                waiting_start_time = time.time()
                continue_sent_for_current_wait = False
                
        else:
            if waiting_start_time and not continue_sent_for_current_wait:
                elapsed = time.time() - waiting_start_time
                if elapsed > WATCHDOG_TIMEOUT:
                    print(f"[WATCHDOG] {WATCHDOG_TIMEOUT}s elapsed with no response from Gemini!")
                    type_continue_to_gemini()
                    continue_sent_for_current_wait = True
                    waiting_start_time = time.time()
                    
        time.sleep(1.0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STOPPED] Gemini macro runner terminated by user.")
