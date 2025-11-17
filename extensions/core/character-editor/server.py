#!/usr/bin/env python3
"""
uDOS Font Editor Server
Serves the font editor interface
"""

import http.server
import socketserver
import sys
from pathlib import Path

# Default port (can be overridden by command-line argument)
DEFAULT_PORT = 8888

class FontEditorHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for font editor static files"""

    def end_headers(self):
        """Add CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


def main():
    """Start the font editor server"""
    port = DEFAULT_PORT

    # Check for port argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default {DEFAULT_PORT}")

    # Change to the font-editor directory
    server_dir = Path(__file__).parent
    import os
    os.chdir(server_dir)

    # Enable port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    # Create and start server
    with socketserver.TCPServer(("", port), FontEditorHandler) as httpd:
        print(f"🎨 Font Editor running at http://localhost:{port}/")
        print(f"📁 Serving files from: {server_dir}")
        print("Press Ctrl+C to stop")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Font Editor stopped")
            sys.exit(0)


if __name__ == "__main__":
    main()
