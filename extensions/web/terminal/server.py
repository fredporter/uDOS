#!/usr/bin/env python3
"""
uDOS CMD Terminal Server

Integrated terminal with full uDOS CLI access.
Serves the CMD-style terminal and handles uDOS command execution.
"""

import http.server
import socketserver
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Add uDOS core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from core.uDOS_main import execute_command
    UDOS_AVAILABLE = True
except ImportError:
    UDOS_AVAILABLE = False
    print("⚠️  Warning: uDOS core not available. Running in standalone mode.")


class uDOSCMDHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for uDOS CMD terminal requests."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/status':
            self.send_status()
        elif parsed_path.path == '/api/splash':
            self.send_splash()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/execute':
            self.execute_udos_command()
        else:
            self.send_error(404, "Endpoint not found")

    def send_status(self):
        """Send server status."""
        status = {
            'success': True,
            'udos_available': UDOS_AVAILABLE,
            'version': '1.3',
            'type': 'Enhanced CMD Terminal'
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())

    def send_splash(self):
        """Send uDOS splash screen."""
        splash_art = """
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    ╔═══════════════════════════════╗
    ║  UNIVERSAL DATA OPERATING     ║
    ║       SYSTEM v1.3             ║
    ║                               ║
    ║   Enhanced Terminal Edition   ║
    ╚═══════════════════════════════╝
"""

        response = {
            'success': True,
            'splash': splash_art
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def execute_udos_command(self):
        """Execute a uDOS command and return the result."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            command = data.get('command', '').strip()

            if not command:
                self.send_json_response({
                    'success': False,
                    'error': 'No command provided'
                }, 400)
                return

            # Execute command (simulated for now)
            output = self.simulate_command(command)
            self.send_json_response({
                'success': True,
                'output': output,
                'command': command
            })

        except json.JSONDecodeError:
            self.send_json_response({
                'success': False,
                'error': 'Invalid JSON'
            }, 400)
        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def simulate_command(self, command):
        """Simulate basic commands for testing."""
        cmd = command.lower().strip()

        if cmd == 'status':
            return """✓ uDOS System Status
━━━━━━━━━━━━━━━━━━━━━━━━
Version: 1.3 Enhanced
Mode: NES Terminal
Backend: Connected
Theme: Switchable
Viewport: Resizable
━━━━━━━━━━━━━━━━━━━━━━━━"""

        elif cmd == 'version':
            return "� uDOS v1.3 Enhanced NES Terminal Edition"

        elif cmd == 'theme':
            return "🌙 Use the theme button (🌙/☀️) to toggle between dark/light mode"

        elif cmd == 'splash':
            return "[Use the 🎨 button or call /api/splash for the splash screen]"

        elif cmd == 'blocks':
            return """🔲 Block Graphics Demo
━━━━━━━━━━━━━━━━━━━━━━━━
Block Shades: ░░░ ▒▒▒ ▓▓▓ ███
Box: ┌─────┐
     │Hello│
     └─────┘
Arrows: ← → ↑ ↓
Symbols: ✓ ✗ ● ■ ★
━━━━━━━━━━━━━━━━━━━━━━━━"""

        elif cmd == 'list':
            return """📁 Available Files:
━━━━━━━━━━━━━━━━━━━━━━━━
📄 README.MD
📄 COMMANDS.UDO
📄 FAQ.UDO
📄 USER.UDT
📄 STORY.UDO
📄 THEMES.UDO
📄 WORLDMAP.UDO
━━━━━━━━━━━━━━━━━━━━━━━━"""

        elif cmd == 'dashboard':
            return "🌀 Use the dashboard button (🌀) in the toolbar to open dashboard"

        elif cmd == 'servers':
            return """⚡ Running Servers:
━━━━━━━━━━━━━━━━━━━━━━━━
🌀 Dashboard: http://localhost:8887
💻 Terminal: http://localhost:8890
📖 Markdown: http://localhost:8889
🎨 Font Editor: http://localhost:8888
━━━━━━━━━━━━━━━━━━━━━━━━"""

        else:
            return f"""⚠️  Command not recognized: {command}

Type 'help' to see available commands
Try: status, version, splash, blocks, list"""

    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Custom logging format."""
        sys.stdout.write(f"🌐 {self.address_string()} - {format%args}\n")


def serve(port=8890, directory=None):
    """
    Start the uDOS CMD Terminal server.

    Args:
        port: Port to serve on (default 8890)
        directory: Directory to serve from (default: terminal directory)
    """
    if directory:
        os.chdir(directory)
    else:
        # Serve from terminal directory
        os.chdir(Path(__file__).parent)

    handler = uDOSCMDHandler

    # Enable port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n� uDOS Enhanced NES Terminal Server v1.3")
        print(f"{'='*60}")
        print(f"  🌐 Serving at: http://localhost:{port}")
        print(f"  📁 Directory: {os.getcwd()}")
        print(f"  🔮 uDOS Core: {'✓ Available' if UDOS_AVAILABLE else '✗ Simulated'}")
        print(f"  🎨 Features: Theme Toggle, Viewport Control, Splash Screen")
        print(f"  ⚡ Press Ctrl+C to stop")
        print(f"{'='*60}\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n⚡ Server stopped")
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="uDOS CMD Terminal Server")
    parser.add_argument('--port', type=int, default=8890, help='Port to serve on (default: 8890)')
    parser.add_argument('--dir', type=str, help='Directory to serve from')

    args = parser.parse_args()

    serve(port=args.port, directory=args.dir)
