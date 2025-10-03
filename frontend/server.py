#!/usr/bin/env python3
"""
Simple HTTP server for StreetPass frontend that supports all HTTP methods
and properly handles static files.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FrontendRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for root path or unknown paths
        if self.path == '/' or '.' not in os.path.basename(self.path):
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # Support other HTTP methods (they'll be forwarded to the backend by the frontend JavaScript)
    def do_POST(self): self.do_GET()
    def do_PUT(self): self.do_GET()
    def do_DELETE(self): self.do_GET()
    def do_PATCH(self): self.do_GET()

def run(host="0.0.0.0", port=8080, directory=None):
    if directory:
        os.chdir(directory)

    while True:
        try:
            with socketserver.TCPServer((host, port), FrontendRequestHandler) as httpd:
                logging.info(f"Frontend serving at http://{host}:{port}")
                httpd.serve_forever()
        except OSError as e:
            if e.errno == 98:  # Address already in use
                logging.warning(f"Port {port} is in use, waiting...")
                import time
                time.sleep(5)
                continue
            raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.dirname(os.path.abspath(__file__))

    # Get host/port from environment or use defaults
    host = os.getenv("FRONTEND_HOST", "0.0.0.0")
    port = int(os.getenv("FRONTEND_PORT", 8080))

    run(host, port, directory)
