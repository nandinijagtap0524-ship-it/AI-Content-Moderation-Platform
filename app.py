"""Local web interface for the demo text moderation classifier."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from moderation import ContentModerator


ROOT = Path(__file__).resolve().parent
MAX_REQUEST_BYTES = 16_384
moderator = ContentModerator()


class ModerationHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        body_bytes = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'")
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, (ROOT / "index.html").read_text(encoding="utf-8"), "text/html; charset=utf-8")
        elif path == "/style.css":
            self._send(200, (ROOT / "style.css").read_text(encoding="utf-8"), "text/css; charset=utf-8")
        elif path == "/app.js":
            self._send(200, (ROOT / "app.js").read_text(encoding="utf-8"), "text/javascript; charset=utf-8")
        else:
            self._send(404, "Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        if urlparse(self.path).path != "/api/moderate":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length"})
            return

        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "Request must contain between 1 and 16,384 bytes"})
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Request body must be valid UTF-8 JSON"})
            return

        if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
            self._send_json(400, {"error": "Provide text as a JSON string"})
            return

        text = payload["text"]
        if not text.strip():
            self._send_json(400, {"error": "Enter some text to analyze"})
            return
        if len(text) > 2_000:
            self._send_json(400, {"error": "Text must be 2,000 characters or fewer"})
            return

        self._send_json(200, moderator.moderate(text))

    def _send_json(self, status, payload):
        self._send(status, json.dumps(payload), "application/json; charset=utf-8")

    def log_message(self, format_string, *args):
        # Keep the local demo's console output concise and avoid logging submitted text.
        super().log_message(format_string, *args)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ModerationHandler)
    print("AI Content Moderation Platform running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
