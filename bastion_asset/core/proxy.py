import http.server
import json
import os
import re
import logging
from logging.handlers import RotatingFileHandler
from bastion_asset.core.sanitizer import sanitize_prompt

PORT = 8081
RULES_FILE = "security_rules.json"
CANARY_TOKEN = "CANARY_SECRET_KEY_999"
LOG_FILE = "bastion_audit.log"

logger = logging.getLogger("BastionAudit")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {
        "direct_threats": ["api key", "secret", "environment variables", "ignore all"],
        "regex_patterns": ["(?i)ignore.*previous.*instructions"],
        "wrapper_triggers": ["translate", "base64", "decode"]
    }

class GatewayZeroHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
            user_prompt = data.get("prompt", "")
        except json.JSONDecodeError:
            user_prompt = body.decode('utf-8')

        rules = load_rules()
        lower_prompt = user_prompt.lower()

        is_canary = CANARY_TOKEN.lower() in lower_prompt
        is_direct = any(kw in lower_prompt for kw in rules.get("direct_threats", []))
        is_regex_match = any(re.search(pattern, user_prompt) for pattern in rules.get("regex_patterns", []))

        # 1. Check for malicious override threats (Block outright)
        if is_canary or is_direct or is_regex_match:
            print(f"\n🚨 [GATEWAY BLOCKED]: {user_prompt}")
            logger.warning(f"BLOCKED | Client: {self.client_address[0]} | Payload: {user_prompt}")
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "GatewayZero Policy Violation"}).encode('utf-8'))
        
        else:
            # 2. Check for accidental token leaks and sanitize them instead of blocking
            clean_prompt, was_sanitized = sanitize_prompt(user_prompt)
            if was_sanitized:
                print(f"\n⚠️ [GATEWAY SANITIZED]: Original '{user_prompt}' -> Cleaned '{clean_prompt}'")
                logger.info(f"SANITIZED | Client: {self.client_address[0]} | Cleaned Payload: {clean_prompt}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "Allowed",
                    "warning": "Sensitive tokens were sanitized",
                    "sanitized_prompt": clean_prompt
                }).encode('utf-8'))
            else:
                print(f"\n✅ [GATEWAY PASSED]: {user_prompt}")
                logger.info(f"PASSED | Client: {self.client_address[0]} | Payload: {user_prompt}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "Allowed"}).encode('utf-8'))

    def log_message(self, format, *args):
        return

def main():
    print(f"\n[+] GatewayZero Live Proxy running on http://localhost:{PORT}")
    print(f"[+] Audit logging active -> {LOG_FILE} (Rotating with DLP Sanitization)")
    server = http.server.HTTPServer(('127.0.0.1', PORT), GatewayZeroHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Shutting down GatewayZero Proxy.")

if __name__ == "__main__":
    main()
