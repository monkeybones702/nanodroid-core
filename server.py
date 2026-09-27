import http.server
import socketserver
import subprocess
import os
import socket

PORT = 8000
SCREEN_PATH = "/data/data/com.termux/files/home/shared/screenshot.png"

class CastHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>TermuxCast Viewer</title>
                <meta http-equiv="refresh" content="1">
                <style>
                    body { background: #000; color: #fff; text-align: center; font-family: sans-serif; margin: 0; padding-top: 2vh; }
                    img { width: 85%; max-width: 1280px; border: 3px solid #333; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
                </style>
            </head>
            <body>
                <h2>TermuxCast Live Display</h2>
                <div>
                    <img src="/screenshot.png" alt="Casting Stream" />
                </div>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            
        elif self.path == "/screenshot.png":
            subprocess.run(["termux-screenshot", "-d", SCREEN_PATH], capture_output=True)
            if os.path.exists(SCREEN_PATH):
                with open(SCREEN_PATH, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.send_header("Content-length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Screenshot not ready")
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    server_ip = get_local_ip()
    print(f"[*] TermuxCast Server running at: http://{server_ip}:{PORT}")
    print("[*] Open this URL in your Fire Stick 4K Silk Browser.")
    
    # Allow immediate reuse of the address to prevent OSError [Errno 98]
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), CastHandler) as httpd:
        httpd.serve_forever()
