import http.server
import json
import os

PORT = 8081
RULES_FILE = "security_rules.json"
CANARY_TOKEN = "CANARY_SECRET_KEY_999"

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {
        "direct_threats": ["api key", "secret", "environment variables", "ignore all"],
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
        is_direct = any(kw in lower_prompt for kw in rules["direct_threats"])

        if is_canary or is_direct:
            print(f"\n🚨 [GATEWAY BLOCKED]: {user_prompt}")
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "GatewayZero Policy Violation"}).encode('utf-8'))
        else:
            print(f"\n✅ [GATEWAY PASSED]: {user_prompt}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Allowed"}).encode('utf-8'))

    def log_message(self, format, *args):
        return

def main():
    print(f"\n[+] GatewayZero Live Proxy running on http://localhost:{PORT}")
    server = http.server.HTTPServer(('127.0.0.1', PORT), GatewayZeroHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Shutting down GatewayZero Proxy.")

if __name__ == "__main__":
    main()
