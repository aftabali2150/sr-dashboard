import http.server
import json
import os
from datetime import datetime

PORT = int(os.environ.get('PORT', 10000))
FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(FOLDER, 'sr_data.json')

class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FOLDER, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/Maximo_SR_Dashboard.html'
        # Serve sr_data.json with no-cache headers
        if self.path == '/sr_data.json' or self.path.startswith('/sr_data.json?'):
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/save_data':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                payload = json.loads(body)
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False)
                count = len(payload.get('rows', []))
                if payload.get('cleared'):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] CLEARED by Admin", flush=True)
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] SAVED {count} records — all users updated", flush=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                print(f"Error: {e}", flush=True)
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    os.chdir(FOLDER)
    print(f"SR Dashboard Server running on port {PORT}", flush=True)
    with http.server.HTTPServer(('0.0.0.0', PORT), Handler) as httpd:
        httpd.serve_forever()
