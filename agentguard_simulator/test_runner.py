import sys

def run_tests():
    print("\n[+] Loading Test Scenario Payloads with Enhanced Security Logic...")
    try:
        with open("payloads.txt", "r") as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if ":" in line:
                tag, prompt = line.split(":", 1)
                tag = tag.strip()
                prompt = prompt.strip()
            else:
                tag = "Unknown"
                prompt = line

            lower_prompt = prompt.lower()

            # Enhanced detection: Catch direct threats OR wrapper/obfuscation bypasses
            direct_threats = ["api key", "secret", "environment variables", "ignore all", "developer debug mode", "unrestricted admin"]
            wrapper_triggers = ["translate", "base64", "decode", "encode", "rot13"]
            
            is_direct = any(kw in lower_prompt for kw in direct_threats)
            is_wrapped = any(w in lower_prompt for w in wrapper_triggers) and any(kw in lower_prompt for kw in ["ignore", "dump", "secret", "override"])

            is_threat = is_direct or is_wrapped
            
            print(f"\n[Test Type: {tag}]")
            print(f"Input: {prompt}")
            if is_threat:
                print("Result: [BLOCKED] Threat vector or bypass wrapper intercepted.")
            else:
                print("Result: [PASSED] Safe execution allowed.")
                
        print("\n[✔] Enhanced test run complete!\n")
    except FileNotFoundError:
        print("[-] Error: payloads.txt not found.")

if __name__ == "__main__":
    run_tests()
