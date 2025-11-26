#!/usr/bin/env python3
"""
uDOS Core Extensions Server v1.0.25
Unified HTTP server for all web-based extensions
"""

import http.server
import socketserver
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Setup logging to memory/logs
LOG_DIR = Path(__file__).parent.parent.parent / 'memory' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

ext_logger = logging.getLogger('uDOS.Extensions')

# Extension Configuration
EXTENSIONS = {
    'dashboard': {
        'port': 8888,
        'path': 'dashboard',
        'name': 'Dashboard Builder',
        'description': 'Arcade-style customizable dashboard',
        'enabled': True
    },
    'teletext': {
        'port': 9002,
        'path': 'teletext',
        'name': 'Teletext Interface',
        'description': 'Teletext with Synthwave DOS styling',
        'enabled': True
    },
    'terminal': {
        'port': 8889,
        'path': 'terminal',
        'name': 'Retro Terminal',
        'description': 'Retro style terminal',
        'enabled': True
    },
    'markdown': {
        'port': 9000,
        'path': 'markdown',
        'name': 'Markdown Viewer',
        'description': 'Knowledge base markdown viewer',
        'enabled': True
    },
    'character': {
        'port': 8891,
        'path': 'character',
        'name': 'Character Editor',
        'description': 'Pixel art and character editor',
        'enabled': True
    },
    'desktop': {
        'port': 8892,
        'path': 'desktop',
        'name': 'System Desktop',
        'description': 'Retro desktop environment with window manager',
        'enabled': True
    }
}

class ExtensionHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with extension routing and CORS support"""

    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests with extension routing"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Log request
        ext_logger.debug(f'GET {path} from {self.client_address[0]}')

        # API endpoint for extension info
        if path == '/api/extensions':
            self.serve_extension_info()
            return

        # Health check
        if path == '/api/health':
            self.serve_health_check()
            return

        # Serve extension status page
        if path == '/api/status':
            self.serve_status_page()
            return

        # Default file serving
        super().do_GET()

    def serve_extension_info(self):
        """Serve extension configuration as JSON"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        info = {
            'server': 'uDOS Core Extensions Server',
            'version': '1.0.25',
            'extensions': EXTENSIONS
        }

        self.wfile.write(json.dumps(info, indent=2).encode())

    def serve_health_check(self):
        """Serve health check response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        health = {
            'status': 'healthy',
            'server': 'uDOS Core Extensions Server',
            'version': '1.0.25',
            'extensions_active': len([e for e in EXTENSIONS.values() if e['enabled']])
        }

        self.wfile.write(json.dumps(health, indent=2).encode())

    def serve_status_page(self):
        """Serve HTML status page"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>uDOS Extensions Server Status</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            color: #00ffff;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            text-shadow: 0 0 10px #00ffff;
        }}
        .extension {{
            background: #0f3460;
            border: 2px solid #00ffff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .extension h3 {{
            color: #ff00ff;
            margin: 0 0 10px 0;
        }}
        .status {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 12px;
        }}
        .status.active {{
            background: #00ff00;
            color: #000;
        }}
        .status.inactive {{
            background: #ff0000;
            color: #fff;
        }}
        a {{
            color: #00ffff;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>🎮 uDOS Core Extensions Server v1.0.25</h1>
    <p style="text-align: center;">Status: <span class="status active">RUNNING</span></p>

    <h2>Active Extensions</h2>
"""

        for ext_id, ext in EXTENSIONS.items():
            status = 'active' if ext['enabled'] else 'inactive'
            status_text = 'ACTIVE' if ext['enabled'] else 'INACTIVE'
            html += f"""
    <div class="extension">
        <h3>{ext['name']} <span class="status {status}">{status_text}</span></h3>
        <p>{ext['description']}</p>
        <p>📂 Path: <code>{ext['path']}</code></p>
        <p>🔌 Port: <code>{ext['port']}</code></p>
        {'<p>🌐 <a href="http://localhost:' + str(ext['port']) + '" target="_blank">Open Extension →</a></p>' if ext['enabled'] else ''}
    </div>
"""

        html += """
    <h2>API Endpoints</h2>
    <div class="extension">
        <p>📊 <a href="/api/extensions">/api/extensions</a> - Extension configuration (JSON)</p>
        <p>💚 <a href="/api/health">/api/health</a> - Health check (JSON)</p>
        <p>📈 <a href="/api/status">/api/status</a> - This status page (HTML)</p>
    </div>
</body>
</html>
"""

        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Custom log formatting with extension info"""
        sys.stderr.write(f"\033[36m[uDOS]\033[0m {self.address_string()} - {format % args}\n")

def run_server(extension_name=None, port=None):
    """Run the unified extensions server"""

    # Determine server root (core extensions directory)
    server_root = Path(__file__).parent
    os.chdir(server_root)

    # Setup file logging for this server instance
    if extension_name and extension_name in EXTENSIONS:
        log_file = LOG_DIR / f'{extension_name}_server.log'
    else:
        log_file = LOG_DIR / 'extensions_server.log'

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ))
    ext_logger.addHandler(file_handler)

    ext_logger.info('='*70)
    ext_logger.info(f'uDOS Extensions Server Starting')
    ext_logger.info(f'Log file: {log_file}')
    ext_logger.info(f'Extension: {extension_name or "all"}')
    ext_logger.info(f'Port: {port or "default"}')
    ext_logger.info('='*70)

    # If specific extension requested, serve only that
    if extension_name and extension_name in EXTENSIONS:
        ext = EXTENSIONS[extension_name]
        port = port or ext['port']
        ext_path = server_root / ext['path']

        if ext_path.exists():
            os.chdir(ext_path)
            print(f"\n\033[1;36m{'='*60}\033[0m")
            print(f"\033[1;35m🎮 uDOS Extension Server v1.0.25\033[0m")
            print(f"\033[1;36m{'='*60}\033[0m")
            print(f"\n\033[1;33m📦 Extension:\033[0m {ext['name']}")
            print(f"\033[1;33m📂 Path:\033[0m {ext['path']}")
            print(f"\033[1;33m🔌 Port:\033[0m {port}")
            print(f"\033[1;32m🌐 URL:\033[0m http://localhost:{port}")
            print(f"\033[1;33m📝 Log:\033[0m {log_file}")
            print(f"\n\033[1;36m{'='*60}\033[0m")
            print(f"\033[1;37mPress Ctrl+C to stop\033[0m\n")
            ext_logger.info(f'Starting {ext["name"]} on port {port}')
        else:
            error_msg = f'Extension path not found: {ext_path}'
            ext_logger.error(error_msg)
            print(f"\033[1;31m❌ Error: {error_msg}\033[0m")
            sys.exit(1)
    else:
        # Run main server (serves all extensions from their ports)
        port = port or 8888
        print(f"\n\033[1;36m{'='*60}\033[0m")
        print(f"\033[1;35m🎮 uDOS Core Extensions Server v1.0.25\033[0m")
        print(f"\033[1;36m{'='*60}\033[0m")
        print(f"\n\033[1;33m🏠 Serving from:\033[0m {server_root}")
        print(f"\033[1;33m🔌 Main Port:\033[0m {port}")
        print(f"\033[1;32m🌐 Status Page:\033[0m http://localhost:{port}/api/status")
        print(f"\033[1;33m📝 Log:\033[0m {log_file}")
        print(f"\n\033[1;36mActive Extensions:\033[0m")
        ext_logger.info(f'Starting main server on port {port}')

        for ext_id, ext in EXTENSIONS.items():
            if ext['enabled']:
                print(f"  \033[32m✓\033[0m {ext['name']:<25} → http://localhost:{ext['port']}")

        print(f"\n\033[1;36m{'='*60}\033[0m")
        print(f"\033[1;37mPress Ctrl+C to stop\033[0m\n")

    # Start server
    try:
        with socketserver.TCPServer(("", port), ExtensionHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n\033[1;33m⚠️  Server stopped\033[0m\n")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n\033[1;31m❌ Error: Port {port} already in use\033[0m")
            print(f"\033[1;33m💡 Try: pkill -f 'python.*{port}' or use a different port\033[0m\n")
        else:
            ext_logger.error(f'Server error: {e}', exc_info=True)
            print(f"\n\033[1;31m❌ Error: {e}\033[0m\n")
        sys.exit(1)

def main():
    """Main entry point with CLI argument parsing"""
    import argparse

    parser = argparse.ArgumentParser(
        description='uDOS Core Extensions Server v1.0.25',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 extensions_server.py                    # Run main server on port 8888
  python3 extensions_server.py dashboard          # Run dashboard on port 8888
  python3 extensions_server.py teletext           # Run teletext on port 9002
  python3 extensions_server.py terminal --port 8080  # Run terminal on port 8080

Available extensions: dashboard, teletext, terminal, markdown, character
        """
    )

    parser.add_argument(
        'extension',
        nargs='?',
        choices=list(EXTENSIONS.keys()) + ['all'],
        default='all',
        help='Extension to run (default: all)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        help='Port number (overrides default)'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available extensions'
    )

    args = parser.parse_args()

    # List extensions
    if args.list:
        print(f"\n\033[1;35m🎮 uDOS Core Extensions v1.0.25\033[0m\n")
        for ext_id, ext in EXTENSIONS.items():
            status = '\033[32m✓\033[0m' if ext['enabled'] else '\033[31m✗\033[0m'
            print(f"{status} \033[1m{ext_id}\033[0m")
            print(f"   {ext['name']}")
            print(f"   Port: {ext['port']} | Path: {ext['path']}")
            print(f"   {ext['description']}\n")
        sys.exit(0)

    # Run server
    extension = None if args.extension == 'all' else args.extension
    run_server(extension, args.port)

if __name__ == '__main__':
    main()
