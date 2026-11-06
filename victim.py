"""A tiny service whose only job is to stay alive."""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

START = time.time()
NAME = sys.argv[1] if len(sys.argv) > 1 else "victim"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "service": NAME,
            "pid": os.getpid(),
            "uptime_s": round(time.time() - START, 1),
            "status": "ok",
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # keep the terminal quiet


if __name__ == "__main__":
    print(f"[{NAME}] up, pid={os.getpid()}, port={PORT}", flush=True)
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
