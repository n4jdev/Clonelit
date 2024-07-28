from http.server import BaseHTTPRequestHandler
import json

def parse_json_body(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return json.loads(post_data.decode('utf-8'))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Welcome to the TTS API!".encode())

    def do_POST(self):
        if self.path == '/api/tts':
            try:
                data = parse_json_body(self)
                if 'text' not in data or 'voice' not in data:
                    self.send_error(400, "Text and voice are required")
                    return

                text = data['text']
                voice = int(data['voice'])

                if not 1 <= voice <= 8:
                    self.send_error(400, "Voice must be between 1 and 8")
                    return

                if len(text) > 500:
                    self.send_error(400, "Text exceeds character limit")
                    return

                response = {
                    "message": f"TTS request received. Text: {text}, Voice: {voice}"
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")
