#!/usr/bin/env python3
"""
uDOS Markdown Server
Serves markdown and UDO files as GitHub-style HTML
Supports ```ucode syntax highlighting
"""

import http.server
import socketserver
import urllib.parse
import os
import sys
import json
import mimetypes
from pathlib import Path

# Default port (can be overridden by command-line argument)
DEFAULT_PORT = 8889
UDOS_ROOT = Path(__file__).parent.parent.parent.parent.absolute()

class MarkdownHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for markdown files"""

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # Serve the markdown viewer
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_viewer()

        # Serve file content
        elif parsed_path.path.startswith('/file/'):
            file_path = parsed_path.path[6:]  # Remove '/file/' prefix
            self.serve_file_content(file_path)

        # Serve markdown as HTML
        elif parsed_path.path.endswith('.md') or parsed_path.path.endswith('.MD'):
            self.serve_markdown_as_html(parsed_path.path[1:])  # Remove leading /

        # Serve UDO files as JSON with syntax highlighting
        elif parsed_path.path.endswith('.UDO') or parsed_path.path.endswith('.udo'):
            self.serve_udo_as_html(parsed_path.path[1:])

        # Default: serve static files
        else:
            super().do_GET()

    def serve_viewer(self):
        """Serve the markdown viewer HTML"""
        viewer_path = UDOS_ROOT / 'extensions' / 'web' / 'markdown-viewer' / 'index.html'
        try:
            with open(viewer_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(404, f"Viewer not found: {e}")

    def serve_file_content(self, file_path):
        """Serve raw file content"""
        full_path = UDOS_ROOT / file_path

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(404, f"File not found: {e}")

    def serve_markdown_as_html(self, file_path):
        """Serve markdown file through the viewer"""
        full_path = UDOS_ROOT / file_path

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Redirect to viewer with file parameter
            redirect_url = f"/?file={urllib.parse.quote(file_path)}"
            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()

        except Exception as e:
            self.send_error(404, f"Markdown file not found: {e}")

    def serve_udo_as_html(self, file_path):
        """Serve UDO file as formatted JSON"""
        full_path = UDOS_ROOT / file_path

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                udo_content = f.read()

            # Try to parse as JSON and pretty-print
            try:
                udo_json = json.loads(udo_content)
                formatted = json.dumps(udo_json, indent=2)
            except:
                formatted = udo_content

            # Create markdown with JSON code block
            markdown = f"# {os.path.basename(file_path)}\n\n```json\n{formatted}\n```"

            # URL encode the markdown
            encoded_markdown = urllib.parse.quote(markdown)
            redirect_url = f"/?file={urllib.parse.quote(file_path)}&content={encoded_markdown}"

            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()

        except Exception as e:
            self.send_error(404, f"UDO file not found: {e}")

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[uDOS Markdown Server] {format % args}")


def main():
    """Start the markdown server"""
    # Parse command-line arguments
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        if sys.argv[1] == '--port' and len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print(f"❌ Invalid port number: {sys.argv[2]}")
                sys.exit(1)
        else:
            print(f"Usage: {sys.argv[0]} [--port PORT]")
            sys.exit(1)

    os.chdir(UDOS_ROOT)

    # Enable port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", port), MarkdownHandler) as httpd:
        print("━" * 60)
        print("🌐 uDOS Markdown Server")
        print("━" * 60)
        print(f"✅ Server running on: http://localhost:{port}")
        print(f"📁 Serving from: {UDOS_ROOT}")
        print("")
        print("Examples:")
        print(f"  • README: http://localhost:{port}/README.MD")
        print(f"  • Commands: http://localhost:{port}/commands/COMMANDS.UDO")
        print(f"  • Viewer: http://localhost:{port}/")
        print("")
        print("Features:")
        print("  ✅ GitHub-style markdown rendering")
        print("  ✅ Syntax highlighting for code blocks")
        print("  ✅ Custom uCODE language support")
        print("  ✅ JSON formatting for .UDO files")
        print("")
        print("Press Ctrl+C to stop")
        print("━" * 60)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped")

if __name__ == "__main__":
    main()
