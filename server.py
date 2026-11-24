import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Active SSE (Server-Sent Events) clients
sse_clients = []
clients_lock = threading.Lock()

def broadcast_alert(alert_data):
    """Broadcast an alert to all active SSE listeners (OBS overlays)."""
    payload = f"data: {json.dumps(alert_data)}\n\n"
    with clients_lock:
        to_remove = []
        for client in sse_clients:
            try:
                client.wfile.write(payload.encode('utf-8'))
                client.wfile.flush()
            except Exception:
                to_remove.append(client)
        for client in to_remove:
            if client in sse_clients:
                sse_clients.remove(client)

class PetStreamHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 1. Server-Sent Events Endpoint: /events
        if parsed.path == '/events':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send initial ping
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
            except Exception:
                return

            with clients_lock:
                sse_clients.append(self)

            # Keep connection open
            try:
                while True:
                    threading.Event().wait(30)
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
            except Exception:
                with clients_lock:
                    if self in sse_clients:
                        sse_clients.remove(self)
            return

        # 2. Trigger Alert Webhook: /api/alert?name=Alex&platform=youtube&tier=Subscriber
        elif parsed.path == '/api/alert':
            params = urllib.parse.parse_qs(parsed.query)
            name = params.get('name', ['Anonymous'])[0]
            platform = params.get('platform', ['YouTube'])[0]
            tier = params.get('tier', ['Subscriber'])[0]
            msg = params.get('msg', [''])[0]

            alert_payload = {
                'type': 'SUBSCRIBER_ALERT',
                'name': name,
                'platform': platform,
                'tier': tier,
                'message': msg
            }
            broadcast_alert(alert_payload)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'success', 'dispatched': alert_payload}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        # Fallback to standard static file server
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/alert':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                data = {}

            alert_payload = {
                'type': 'SUBSCRIBER_ALERT',
                'name': data.get('name', 'Anonymous'),
                'platform': data.get('platform', 'YouTube'),
                'tier': data.get('tier', 'Subscriber'),
                'message': data.get('message', '')
            }
            broadcast_alert(alert_payload)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'dispatched': alert_payload}).encode('utf-8'))
            return

        super().do_POST()

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), PetStreamHandler)
    print(f"=====================================================")
    print(f"🐾 Buddy Desktop Pet - Stream & Overlay Server Ready")
    print(f"=====================================================")
    print(f"• Overlay URL for OBS:   http://localhost:{PORT}/obs_overlay.html")
    print(f"• Control Dock for OBS:  http://localhost:{PORT}/obs_dock.html")
    print(f"• Interactive Preview:   http://localhost:{PORT}/index.html")
    print(f"• Webhook Endpoint:      http://localhost:{PORT}/api/alert?name=Test&platform=youtube")
    print(f"=====================================================")
    print(f"Listening on port {PORT}... Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()

if __name__ == '__main__':
    run_server()
