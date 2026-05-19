import http.server
import json
import os
from datetime import datetime

PORT = int(os.environ.get('PORT', 8080))
FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(FOLDER, 'sr_data.json')

class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FOLDER, **kwargs)

    def do_GET(self):
        # Serve index as default
        if self.path == '/':
            self.path = '/Maximo_SR_Dashboard.html'
        super().do_GET()

    def do_POST(self):
        if self.path == '/save_data':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                payload = json.loads(body)
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False)
                if payload.get('cleared'):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Data CLEARED by Admin")
                else:
                    count = len(payload.get('rows', []))
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Data SAVED — {count} records")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                print(f"Error: {e}")
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]}")

if __name__ == '__main__':
    os.chdir(FOLDER)
    print(f"SR Dashboard Server running on port {PORT}")
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        httpd.serve_forever()
