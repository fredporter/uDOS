#!/usr/bin/env python3
"""
uDOS Dashboard Server (stdlib only - no Flask)
Provides REST API for web dashboard to control uDOS servers
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sys
import os
import time
import threading
import subprocess
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Add uDOS core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.uDOS_server import ServerManager

# Global installation tracker
installation_status = {}
installation_lock = threading.Lock()


class DashboardAPIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with API endpoints and static file serving."""

    # Initialize server manager as class variable (shared across requests)
    server_manager = ServerManager()

    # Store dashboard directory for serving static files
    dashboard_dir = Path(__file__).parent

    def __init__(self, *args, **kwargs):
        # Serve static files from dashboard directory
        super().__init__(*args, directory=str(self.dashboard_dir), **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        # API Status endpoint
        if parsed_path.path == '/api/status':
            self.handle_get_status()
            return

        # Installation progress endpoint
        elif parsed_path.path.startswith('/api/install/progress/'):
            extension_name = parsed_path.path.split('/')[-1]
            self.handle_install_progress(extension_name)
            return

        # World map endpoint
        elif parsed_path.path == '/api/worldmap':
            self.handle_get_worldmap()
            return

        # For all other paths, use the parent class's file serving
        # (it will serve from the directory we specified in __init__)
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path.startswith('/api/start/'):
            server_name = parsed_path.path.split('/')[-1]
            self.handle_start_server(server_name)
        elif parsed_path.path.startswith('/api/stop/'):
            server_name = parsed_path.path.split('/')[-1]
            self.handle_stop_server(server_name)
        elif parsed_path.path.startswith('/api/install/'):
            extension_name = parsed_path.path.split('/')[-1]
            self.handle_install_extension(extension_name)
        elif parsed_path.path == '/api/settings/save':
            self.handle_save_settings()
        else:
            self.send_json_response({'error': 'Unknown API endpoint'}, 404)

    def handle_get_status(self):
        """Get status of all servers."""
        try:
            servers_info = []

            # Define available servers with their info
            available_servers = {
                'font-editor': {
                    'name': 'Font Editor',
                    'description': '16×16 bitmap font creator',
                    'icon': '🎨',
                    'port': 8888,
                    'path': 'extensions/web/font-editor'
                },
                'markdown-viewer': {
                    'name': 'Markdown Viewer',
                    'description': 'GitHub-style renderer with uCODE syntax',
                    'icon': '📖',
                    'port': 8889,
                    'path': 'extensions/web/markdown-viewer'
                },
                'cmd': {
                    'name': 'Web Terminal',
                    'description': 'Browser-based terminal emulator',
                    'icon': '💻',
                    'port': 8890,
                    'path': 'extensions/web/cmd'  # Node.js version
                },
                'terminal': {
                    'name': 'Web Terminal (Python)',
                    'description': 'Python-based terminal with xterm.js',
                    'icon': '💻',
                    'port': 8890,
                    'path': 'extensions/web/terminal'  # Python version
                },
                'typo': {
                    'name': 'Typo Editor',
                    'description': 'Modern markdown editor (Svelte)',
                    'icon': '✏️',
                    'port': 5173,
                    'path': 'extensions/clone/web/typo',
                    'setup_script': './extensions/setup_typo.sh'
                },
                'micro': {
                    'name': 'Micro Editor',
                    'description': 'Terminal-based text editor',
                    'icon': '📝',
                    'port': 8891,
                    'path': 'extensions/clone/web/micro',
                    'setup_script': './extensions/setup_micro.sh'
                }
            }

            # Get base path (4 levels up from this file)
            base_path = Path(__file__).parent.parent.parent.parent

            # Check each server
            for server_id, info in available_servers.items():
                # Check if installed
                path = base_path / info['path']
                is_installed = path.exists()

                # Check if running
                is_running = False
                pid = None
                port = info['port']
                uptime = 0

                if server_id in self.server_manager.servers:
                    srv_info = self.server_manager.servers[server_id]
                    pid = srv_info.get('pid')
                    if pid and self.server_manager._is_process_running(pid):
                        is_running = True
                        port = srv_info.get('port', port)
                        started_at = srv_info.get('started_at', 0)
                        if started_at:
                            uptime = int(time.time() - started_at)

                servers_info.append({
                    'id': server_id,
                    'name': info['name'],
                    'description': info['description'],
                    'icon': info['icon'],
                    'port': port,
                    'url': f'http://localhost:{port}',
                    'installed': is_installed,
                    'running': is_running,
                    'pid': pid,
                    'uptime': uptime,
                    'setup_script': info.get('setup_script', None)
                })

            self.send_json_response({
                'success': True,
                'servers': servers_info
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_start_server(self, server_name):
        """Start a specific server."""
        try:
            # Parse request body for options
            content_length = int(self.headers.get('Content-Length', 0))
            body = {}
            if content_length > 0:
                body_bytes = self.rfile.read(content_length)
                body = json.loads(body_bytes.decode('utf-8'))

            port = body.get('port')
            no_browser = body.get('no_browser', True)  # Default to no browser from dashboard

            # Map server names to start methods and default ports
            # Only include servers that have start methods
            server_config = {}

            # Check which methods exist
            if hasattr(self.server_manager, 'start_typo_server'):
                server_config['typo'] = {'method': self.server_manager.start_typo_server, 'port': 5173}

            if hasattr(self.server_manager, 'start_cmd_server'):
                server_config['cmd'] = {'method': self.server_manager.start_cmd_server, 'port': 8890}

            if hasattr(self.server_manager, 'start_terminal_server'):
                server_config['terminal'] = {'method': self.server_manager.start_terminal_server, 'port': 8890}

            if hasattr(self.server_manager, 'start_markdown_viewer'):
                server_config['markdown-viewer'] = {'method': self.server_manager.start_markdown_viewer, 'port': 8889}

            if hasattr(self.server_manager, 'start_font_editor'):
                server_config['font-editor'] = {'method': self.server_manager.start_font_editor, 'port': 8888}

            # Note: micro server method doesn't exist yet, so it won't be added

            if server_name not in server_config:
                self.send_json_response({
                    'success': False,
                    'error': f'Server not available: {server_name}. Extension may not be installed or supported.'
                }, 404)
                return

            # Get server config
            config = server_config[server_name]
            start_method = config['method']
            default_port = config['port']

            # Use provided port or default
            actual_port = port or default_port

            # Call with appropriate parameters
            success, message = start_method(port=actual_port, open_browser=not no_browser)

            self.send_json_response({
                'success': success,
                'message': message,
                'port': actual_port  # Include port in response
            })

        except json.JSONDecodeError:
            self.send_json_response({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, 400)
        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_stop_server(self, server_name):
        """Stop a specific server."""
        try:
            success, message = self.server_manager.stop_server(server_name)

            self.send_json_response({
                'success': success,
                'message': message
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_install_extension(self, extension_name):
        """Install an extension by running its setup script with progress tracking."""
        try:
            # Map extension names to setup scripts
            setup_scripts = {
                'typo': 'extensions/setup_typo.sh',
                'micro': 'extensions/setup_micro.sh'
            }

            if extension_name not in setup_scripts:
                self.send_json_response({
                    'success': False,
                    'error': f'No setup script found for {extension_name}'
                }, 404)
                return

            # Check if already installing
            with installation_lock:
                if extension_name in installation_status:
                    status = installation_status[extension_name]
                    if status['status'] == 'installing':
                        self.send_json_response({
                            'success': False,
                            'error': f'{extension_name} is already being installed'
                        }, 409)
                        return

            # Get absolute path to setup script
            base_path = Path(__file__).parent.parent.parent.parent
            script_path = base_path / setup_scripts[extension_name]

            if not script_path.exists():
                self.send_json_response({
                    'success': False,
                    'error': f'Setup script not found: {script_path}'
                }, 404)
                return

            # Initialize installation status
            with installation_lock:
                installation_status[extension_name] = {
                    'status': 'installing',
                    'progress': 0,
                    'message': 'Starting installation...',
                    'output': [],
                    'started_at': time.time()
                }

            # Run installation in background thread
            def install_thread():
                try:
                    # Update status
                    with installation_lock:
                        installation_status[extension_name]['progress'] = 10
                        installation_status[extension_name]['message'] = 'Running setup script...'

                    # Set up environment for non-interactive installation
                    env = os.environ.copy()
                    env['DEBIAN_FRONTEND'] = 'noninteractive'
                    env['UDOS_AUTO_INSTALL'] = '1'  # Signal to scripts to skip prompts

                    # Run the setup script with forced yes
                    # Use expect-style input feeding for any prompts
                    process = subprocess.Popen(
                        ['bash', str(script_path)],
                        cwd=str(base_path),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        env=env
                    )

                    # Feed 'n' responses to any prompts
                    def feed_input():
                        try:
                            for _ in range(100):  # Feed up to 100 'n' responses
                                process.stdin.write('n\n')
                                process.stdin.flush()
                                time.sleep(0.1)
                        except:
                            pass

                    input_thread = threading.Thread(target=feed_input, daemon=True)
                    input_thread.start()

                    # Read output line by line
                    output_lines = []
                    for line in iter(process.stdout.readline, ''):
                        if not line:
                            break

                        line = line.rstrip()
                        output_lines.append(line)

                        # Update progress based on keywords
                        progress = installation_status[extension_name]['progress']
                        if 'Cloning' in line or 'clone' in line.lower():
                            progress = 30
                            msg = 'Cloning repository...'
                        elif 'Download' in line or 'download' in line.lower():
                            progress = 40
                            msg = 'Downloading files...'
                        elif 'install' in line.lower() and 'dependencies' in line.lower():
                            progress = 50
                            msg = 'Installing dependencies...'
                        elif 'npm install' in line or 'Installing packages' in line:
                            progress = 60
                            msg = 'Installing npm packages...'
                        elif 'Extracting' in line or 'extract' in line.lower():
                            progress = 70
                            msg = 'Extracting files...'
                        elif 'Building' in line or 'Compiling' in line:
                            progress = 80
                            msg = 'Building extension...'
                        elif 'Success' in line or 'complete' in line.lower():
                            progress = 95
                            msg = 'Finalizing...'
                        else:
                            msg = line[:50] if line else installation_status[extension_name]['message']

                        with installation_lock:
                            installation_status[extension_name]['progress'] = min(progress, 95)
                            installation_status[extension_name]['message'] = msg
                            installation_status[extension_name]['output'] = output_lines[-50:]  # Keep last 50 lines

                    # Wait for completion
                    return_code = process.wait()

                    # Capture any remaining output
                    try:
                        remaining = process.stdout.read()
                        if remaining:
                            output_lines.extend(remaining.strip().split('\n'))
                    except:
                        pass

                    # Update final status
                    with installation_lock:
                        if return_code == 0:
                            installation_status[extension_name]['status'] = 'completed'
                            installation_status[extension_name]['progress'] = 100
                            installation_status[extension_name]['message'] = 'Installation completed successfully!'
                        else:
                            installation_status[extension_name]['status'] = 'failed'
                            installation_status[extension_name]['progress'] = 0
                            # Include last error lines in message
                            error_lines = [l for l in output_lines[-10:] if l.strip()]
                            error_msg = ' | '.join(error_lines[-3:]) if error_lines else 'Unknown error'
                            installation_status[extension_name]['message'] = f'Failed (exit {return_code}): {error_msg}'
                            installation_status[extension_name]['output'] = output_lines[-50:]

                except Exception as e:
                    with installation_lock:
                        installation_status[extension_name]['status'] = 'failed'
                        installation_status[extension_name]['progress'] = 0
                        installation_status[extension_name]['message'] = f'Error: {str(e)}'
                        installation_status[extension_name]['output'].append(f'ERROR: {str(e)}')

            # Start installation thread
            thread = threading.Thread(target=install_thread, daemon=True)
            thread.start()

            self.send_json_response({
                'success': True,
                'message': f'Installation started for {extension_name}',
                'extension': extension_name
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_install_progress(self, extension_name):
        """Get installation progress for an extension."""
        try:
            with installation_lock:
                if extension_name in installation_status:
                    status = installation_status[extension_name].copy()
                else:
                    status = {
                        'status': 'not_started',
                        'progress': 0,
                        'message': 'Not started',
                        'output': []
                    }

            self.send_json_response({
                'success': True,
                **status
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_get_worldmap(self):
        """Get world map data from WORLDMAP.UDO."""
        try:
            base_path = Path(__file__).parent.parent.parent.parent
            worldmap_path = base_path / 'data' / 'WORLDMAP.UDO'

            if worldmap_path.exists():
                with open(worldmap_path, 'r') as f:
                    map_data = json.load(f)
                self.send_json_response(map_data)
            else:
                self.send_json_response({
                    'error': 'WORLDMAP.UDO not found'
                }, 404)

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_save_settings(self):
        """Save user settings to USER.UDT."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            settings = json.loads(body_bytes.decode('utf-8'))

            base_path = Path(__file__).parent.parent.parent.parent
            user_path = base_path / 'data' / 'USER.UDT'

            # Load existing USER.UDT
            user_data = {}
            if user_path.exists():
                with open(user_path, 'r') as f:
                    user_data = json.load(f)

            # Update settings
            if 'EDITOR_PREFERENCES' in settings:
                if 'EDITOR_PREFERENCES' not in user_data:
                    user_data['EDITOR_PREFERENCES'] = {}
                user_data['EDITOR_PREFERENCES'].update(settings['EDITOR_PREFERENCES'])

            if 'SESSION_PREFERENCES' in settings:
                if 'SESSION_PREFERENCES' not in user_data:
                    user_data['SESSION_PREFERENCES'] = {}
                user_data['SESSION_PREFERENCES'].update(settings['SESSION_PREFERENCES'])

            if 'LOCATION_DATA' in settings:
                if 'LOCATION_DATA' not in user_data:
                    user_data['LOCATION_DATA'] = {}
                user_data['LOCATION_DATA'].update(settings['LOCATION_DATA'])

            # Save back to file
            with open(user_path, 'w') as f:
                json.dump(user_data, f, indent=2)

            self.send_json_response({
                'success': True,
                'message': 'Settings saved successfully'
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def send_json_response(self, data, status_code=200):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS for local dev
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Override to customize logging."""
        # Only log API calls, not static file requests
        if '/api/' in self.path:
            super().log_message(format, *args)


def run_server(port=8887):
    """Run the dashboard server."""
    # DON'T change directory - ServerManager needs to be in uDOS root
    # Static files are served via directory parameter in __init__

    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardAPIHandler)

    print(f'🔮 uDOS Dashboard Server running on http://localhost:{port}')
    print(f'📁 Serving from: {DashboardAPIHandler.dashboard_dir}')
    print(f'📂 Working directory: {Path.cwd()}')
    print(f'🛑 Press Ctrl+C to stop')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Server stopped')
        httpd.server_close()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8887
    run_server(port)
