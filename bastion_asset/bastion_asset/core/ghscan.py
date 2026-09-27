import os
import json
import re
import sys

RULES_FILE = "security_rules.json"

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {
        "direct_threats": ["api key", "secret", "password", "token"],
        "regex_patterns": [r'sk-[a-zA-Z0-9-_]{20,}', r'(?i)(secret|password|api_key|token)\s*[:=]\s*\S+']
    }

def scan_file(filepath, rules):
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                lower_line = line.lower()
                
                # Check direct threat keywords
                for dt in rules.get("direct_threats", []):
                    if dt in lower_line:
                        findings.append((line_num, f"Direct Threat Keyword '{dt}'", line.strip()))
                
                # Check regex patterns
                for pat in rules.get("regex_patterns", []):
                    if re.search(pat, line):
                        findings.append((line_num, f"Regex Pattern Match", line.strip()))
    except Exception:
        pass
    return findings

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    abs_target = os.path.abspath(target_dir)
    print(f"\n==============================================")
    print(f" 🔍 AEGISCORE REPO & CODE SCANNER")
    print(f" Target: {abs_target}")
    print(f"==============================================\n")
    
    rules = load_rules()
    total_findings = []
    scanned_files = 0
    
    ignore_dirs = {".git", "__pycache__", "venv", ".venv", "node_modules", "dist", "build"}
    code_extensions = ('.py', '.json', '.md', '.js', '.html', '.env', '.txt', '.yml', '.yaml', '.sh')
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(code_extensions):
                filepath = os.path.join(root, file)
                scanned_files += 1
                findings = scan_file(filepath, rules)
                if findings:
                    print(f"📁 Vulnerabilities in: {os.path.relpath(filepath, target_dir)}")
                    for line_num, desc, content in findings:
                        total_findings.append(line_num)
                        print(f"  [Line {line_num}] {desc}")
                        print(f"    -> {content[:75]}")
                    print("-" * 46)
                                
    print(f"\n==============================================")
    print(f" Scan Complete.")
    print(f" - Scanned Files : {scanned_files}")
    print(f" - Total Findings: {len(total_findings)}")
    print(f"==============================================")

if __name__ == "__main__":
    main()
