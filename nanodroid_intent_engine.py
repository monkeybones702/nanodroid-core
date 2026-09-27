#!/usr/bin/env python3
import os
import sys
import subprocess
import json

# ==============================================================================
# NanoDroid-Core Direct Package & Intent Engine (v20.0.0)
# Target: Samsung Galaxy A16 (ARM64) | Zero UI Gestures, Direct Component Execution
# ==============================================================================

def rish_exec(cmd):
    result = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True)
    return result.stdout.strip()

class IntentEngine:
    @staticmethod
    def list_packages(query=""):
        print(f"[*] Querying installed packages matching '{query}'...")
        output = rish_exec("pm list packages")
        packages = [line.replace("package:", "").strip() for line in output.splitlines()]
        if query:
            packages = [p for p in packages if query.lower() in p.lower()]
        return packages

    @staticmethod
    def start_activity(component_string, action=None, data=None, extras=None):
        """
        Launches an activity explicitly or implicitly.
        component_string: e.g., 'com.sec.android.app.popupcalculator/.Calculator'
        """
        cmd = ["rish", "-c"]
        am_cmd = ["am", "start"]
        
        if "/" in component_string:
            am_cmd.extend(["-n", component_string])
        else:
            am_cmd.extend(["-a", component_string])
            
        if action and "/" in component_string:
            am_cmd.extend(["-a", action])
        if data:
            am_cmd.extend(["-d", data])
            
        if extras:
            for k, v in extras.items():
                if isinstance(v, bool):
                    am_cmd.extend(["--ez", k, str(v).lower()])
                elif isinstance(v, int):
                    am_cmd.extend(["--ei", k, str(v)])
                else:
                    am_cmd.extend(["-e", k, str(v)])
                    
        cmd.append(" ".join(am_cmd))
        print(f"[*] Executing intent command: {' '.join(am_cmd)}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("[+] Activity launched successfully.")
            return True
        else:
            print(f"[-] Launch failed: {res.stderr.strip()}")
            return False

    @staticmethod
    def broadcast(action, extras=None):
        cmd = ["rish", "-c"]
        bc_cmd = ["am", "broadcast", "-a", action]
        if extras:
            for k, v in extras.items():
                bc_cmd.extend(["-e", k, str(v)])
        cmd.append(" ".join(bc_cmd))
        print(f"[*] Broadcasting action: {action}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    @staticmethod
    def dump_package_info(package_name):
        print(f"[*] Inspecting exported components for: {package_name}")
        output = rish_exec(f"dumpsys package {package_name}")
        return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 nanodroid_intent_engine.py list [filter]")
        print("  python3 nanodroid_intent_engine.py start <package/activity>")
        print("  python3 nanodroid_intent_engine.py inspect <package>")
        sys.exit(1)

    action = sys.argv[1].lower()
    engine = IntentEngine()

    if action == "list":
        flt = sys.argv[2] if len(sys.argv) > 2 else ""
        pkgs = engine.list_packages(flt)
        for p in pkgs[:50]:  # Cap output length
            print(f"  -> {p}")
        print(f"[+] Total matching packages: {len(pkgs)}")
    elif action == "start" and len(sys.argv) > 2:
        engine.start_activity(sys.argv[2])
    elif action == "inspect" and len(sys.argv) > 2:
        info = engine.dump_package_info(sys.argv[2])
        print(info[:2000] if len(info) > 2000 else info)
    else:
        print("[-] Invalid arguments or missing parameters.")
        sys.exit(1)
