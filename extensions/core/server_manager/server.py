"""
uDOS Server Manager
Manages web-based extension servers (typo, etc.)
"""

import os
import sys
import json
import subprocess
import time
import signal
import webbrowser
from pathlib import Path
from typing import Dict, Optional, Tuple


class ServerManager:
    """Manages web server processes for uDOS extensions."""

    def __init__(self, state_file='sandbox/.server_state.json'):
        self.state_file = state_file
        # Get absolute path to uDOS root (where extensions/ folder is)
        self.udos_root = Path(__file__).parent.parent.parent.parent
        self.extensions_dir = self.udos_root / 'extensions'
        self.cloned_dir = self.extensions_dir / 'cloned'  # External cloned extensions
        self.core_dir = self.extensions_dir / 'core'      # Built-in core extensions
        self.web_dir = self.cloned_dir  # Web extensions are in cloned/
        self.servers = self._load_state()

    def _get_python_executable(self) -> str:
        """Get Python executable, preferring venv."""
        venv_python = self.udos_root / '.venv' / 'bin' / 'python3'
        if venv_python.exists():
            return str(venv_python)
        return sys.executable

    def _use_bulletproof_launcher(self, server_name: str, port: Optional[int] = None,
                                   open_browser: bool = True) -> Tuple[bool, str]:
        """
        Use the unified extensions server to launch web extensions.
        """
        # Path to unified extensions server
        server_script = self.core_dir / 'extensions_server.py'

        if not server_script.exists():
            return False, f"❌ Extensions server not found: {server_script}"

        # Map server names to extension names in extensions_server.py
        server_map = {
            'dashboard': 'dashboard',
            'teletext': 'teletext',
            'terminal': 'terminal',
            'markdown-viewer': 'markdown',
            'markdown': 'markdown',
            'typo': 'typo',  # If typo is added to extensions_server.py
            'font-editor': 'character',
            'character': 'character'
        }

        extension_name = server_map.get(server_name)
        if not extension_name:
            available = ', '.join(server_map.keys())
            return False, f"❌ Unknown server: {server_name}\nAvailable: {available}"

        # Get Python executable (prefer venv)
        python_exe = self._get_python_executable()

        # Build command
        cmd = [python_exe, str(server_script), extension_name]
        if port:
            cmd.extend(['--port', str(port)])
        # Note: extensions_server doesn't have --no-browser flag, it doesn't auto-open by default

        try:
            # Start server in background using Popen (don't wait for it)
            log_dir = Path('memory/logs')
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f'{server_name}_{port or "default"}.log'

            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,  # Detach from parent
                    cwd=str(self.udos_root)  # Run from uDOS root
                )

            # Wait briefly to check if it started successfully
            time.sleep(2)

            # Check if process is still running
            if process.poll() is None:
                # Process is running - save state
                actual_port = port or self._get_default_port(server_name)
                self.servers[server_name] = {
                    'pid': process.pid,
                    'port': actual_port,
                    'started_at': time.time(),
                    'url': f'http://localhost:{actual_port}',
                    'log_file': str(log_file)
                }
                self._save_state()

                url = f'http://localhost:{actual_port}'
                browser_msg = " (opening in browser...)" if open_browser else ""
                return True, f"✅ {server_name} started on {url} (PID: {process.pid}){browser_msg}\n📋 Logs: {log_file}"
            else:
                # Process exited - check log for errors
                with open(log_file, 'r') as f:
                    error_log = f.read()
                return False, f"❌ {server_name} failed to start. Log:\n{error_log[-500:]}"

        except Exception as e:
            return False, f"❌ Error starting {server_name}: {e}"

    def _get_default_port(self, server_name: str) -> int:
        """Get default port for a server."""
        default_ports = {
            'dashboard': 8887,
            'font-editor': 8888,
            'markdown-viewer': 8889,
            'terminal': 8890,
            'cmd': 8890,
            'typo': 5173
        }
        return default_ports.get(server_name, 8000)

    def _load_state(self) -> Dict:
        """Load server state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def _save_state(self):
        """Save server state to file."""
        try:
            # Create parent directory if needed
            os.makedirs(os.path.dirname(self.state_file) or '.', exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.servers, f, indent=2)
        except IOError as e:
            print(f"⚠️  Warning: Could not save server state: {e}")

    def start_typo_server(self, port=5173, open_browser=True) -> Tuple[bool, str]:
        """
        Start the typo web editor server.

        Args:
            port (int): Port to run server on
            open_browser (bool): Open browser after starting

        Returns:
            tuple: (success, message)
        """
        typo_dir = self.web_dir / 'typo'

        # Check if typo is installed
        if not (typo_dir / 'package.json').exists():
            return False, ("📦 typo not installed\n"
                          "Run: cd extensions && ./setup_typo.sh")

        # Check if already running
        if 'typo' in self.servers:
            pid = self.servers['typo'].get('pid')
            if pid and self._is_process_running(pid):
                url = f"http://localhost:{self.servers['typo'].get('port', port)}"
                return False, f"⚠️  typo server already running on {url}"

        # Check if port is available
        if self._is_port_in_use(port):
            return False, f"❌ Port {port} is already in use\nTry a different port: server start typo --port <number>"

        # Check for Node.js/npm
        if not self._check_node():
            return False, ("❌ Node.js not found\n"
                          "Install Node.js from https://nodejs.org")

        # Start server
        try:
            # Start npm run dev in background, fully detached
            # Redirect output to log file
            log_dir = Path('memory/logs')
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f'typo_{port}.log'

            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    ['npm', 'run', 'dev', '--', '--port', str(port), '--host'],
                    cwd=str(typo_dir),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,  # Detach from parent process
                    preexec_fn=os.setpgrp if sys.platform != 'win32' else None  # Create new process group
                )

            # Save server state immediately (don't wait)
            self.servers['typo'] = {
                'pid': process.pid,
                'port': port,
                'started_at': time.time(),
                'url': f'http://localhost:{port}',
                'log_file': str(log_file)
            }
            self._save_state()

            url = f'http://localhost:{port}'

            # Open browser in background if requested
            if open_browser:
                # Use a background thread or process to avoid blocking
                subprocess.Popen(
                    ['python3', '-c', f'import time, webbrowser; time.sleep(3); webbrowser.open("{url}")'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                browser_msg = f"🌐 Opening {url} in browser..."
            else:
                browser_msg = f"🌐 Access at: {url}"

            return True, (f"✅ typo server starting in background (PID: {process.pid})\n"
                         f"📍 {browser_msg}\n"
                         f"📋 Logs: {log_file}\n"
                         f"⏹️  Stop with: OUTPUT STOP typo\n"
                         f"💡 Server will be ready in ~3 seconds")

        except FileNotFoundError:
            return False, ("❌ npm not found\n"
                          "Ensure Node.js and npm are installed")
        except Exception as e:
            return False, f"❌ Failed to start server: {e}"

    def start_cmd_server(self, port=3000, open_browser=True) -> Tuple[bool, str]:
        """
        Start the cmd.js web terminal server.

        Args:
            port (int): Port to run server on
            open_browser (bool): Open browser after starting

        Returns:
            tuple: (success, message)
        """
        cmd_dir = self.web_dir / 'cmd'

        # Check if cmd is installed
        if not (cmd_dir / 'package.json').exists():
            return False, ("📦 cmd not installed\n"
                          "Run: bash extensions/setup_cmd.sh")

        # Check if already running
        if 'cmd' in self.servers:
            pid = self.servers['cmd'].get('pid')
            if pid and self._is_process_running(pid):
                url = f"http://localhost:{self.servers['cmd'].get('port', port)}"
                return False, f"⚠️  cmd server already running on {url}"

        # Check if port is available
        if self._is_port_in_use(port):
            return False, f"❌ Port {port} is already in use\nTry a different port: server start cmd --port <number>"

        # Check for Node.js/npm
        if not self._check_node():
            return False, ("❌ Node.js not found\n"
                          "Install Node.js from https://nodejs.org")

        # Check if http-server is available
        try:
            subprocess.run(['which', 'http-server'],
                          capture_output=True, check=True)
        except subprocess.CalledProcessError:
            # Try to install http-server globally
            print("📦 Installing http-server globally...")
            try:
                subprocess.run(['npm', 'install', '-g', 'http-server'],
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                return False, ("❌ Failed to install http-server\n"
                             "Run manually: npm install -g http-server")

        # Start server
        try:
            # Start http-server in background, fully detached
            # Redirect output to log file
            log_dir = Path('memory/logs')
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f'cmd_{port}.log'

            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    ['http-server', '.', '-p', str(port), '-c-1', '--cors'],
                    cwd=str(cmd_dir),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,  # Detach from parent process
                    preexec_fn=os.setpgrp if sys.platform != 'win32' else None  # Create new process group
                )

            # Save server state immediately
            self.servers['cmd'] = {
                'pid': process.pid,
                'port': port,
                'started_at': time.time(),
                'url': f'http://localhost:{port}/udos_cmd_bridge.html',
                'log_file': str(log_file)
            }
            self._save_state()

            url = f'http://localhost:{port}/udos_cmd_bridge.html'

            # Open browser in background if requested
            if open_browser:
                # Use a background thread or process to avoid blocking
                subprocess.Popen(
                    ['python3', '-c', f'import time, webbrowser; time.sleep(3); webbrowser.open("{url}")'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                browser_msg = f"🌐 Opening {url} in browser..."
            else:
                browser_msg = f"🌐 Access at: {url}"

            return True, (f"✅ cmd terminal server starting in background (PID: {process.pid})\n"
                         f"📍 {browser_msg}\n"
                         f"📋 Logs: {log_file}\n"
                         f"🔤 Font: Monaspace Neon (change via FONT SET command)\n"
                         f"⏹️  Stop with: OUTPUT STOP cmd\n"
                         f"💡 Server will be ready in ~3 seconds")

        except FileNotFoundError:
            return False, ("❌ http-server not found\n"
                          "Install: npm install -g http-server")
        except Exception as e:
            return False, f"❌ Failed to start server: {e}"

    def start_markdown_viewer(self, port=8889, open_browser=True) -> Tuple[bool, str]:
        """
        Start the markdown viewer server using bulletproof launcher.

        Args:
            port (int): Port to run server on
            open_browser (bool): Open browser after starting

        Returns:
            tuple: (success, message)
        """
        return self._use_bulletproof_launcher('markdown-viewer', port, open_browser)

    def start_font_editor(self, port=8888, open_browser=True) -> Tuple[bool, str]:
        """
        Start the font editor server using bulletproof launcher.

        Args:
            port (int): Port to run server on
            open_browser (bool): Open browser after starting

        Returns:
            tuple: (success, message)
        """
        return self._use_bulletproof_launcher('font-editor', port, open_browser)

    def start_terminal_server(self, port=8890, open_browser=True) -> Tuple[bool, str]:
        """
        Start the web terminal server using bulletproof launcher.

        Args:
            port (int): Port to run server on
            open_browser (bool): Open browser after starting

        Returns:
            tuple: (success, message)
        """
        return self._use_bulletproof_launcher('terminal', port, open_browser)

    def start_dashboard(self, port=8887, open_browser=True) -> Tuple[bool, str]:
        """
        Start the unified web dashboard server using bulletproof launcher.

        Args:
            port (int): Port to run server on
            open_browser (bool): Open browser after starting

        Returns:
            tuple: (success, message)
        """
        # Use bulletproof launcher for reliability
        return self._use_bulletproof_launcher('dashboard', port, open_browser)

    def start_server(self, name: str, port: Optional[int] = None, open_browser: bool = True) -> str:
        """
        Unified method to start any web server.

        Args:
            name (str): Server name (typo, cmd, font-editor, markdown-viewer, dashboard, terminal)
            port (int, optional): Custom port number
            open_browser (bool): Whether to open browser after starting

        Returns:
            str: Status message for OUTPUT command
        """
        # Map server names to their start methods
        server_methods = {
            'typo': self.start_typo_server,
            'cmd': self.start_cmd_server,
            'terminal': self.start_terminal_server,
            'font-editor': self.start_font_editor,
            'markdown-viewer': self.start_markdown_viewer,
            'dashboard': self.start_dashboard
        }

        method = server_methods.get(name)
        if not method:
            available = ', '.join(server_methods.keys())
            return f"❌ Unknown server: {name}\nAvailable: {available}"

        # Use default port if none specified
        if port is None:
            port = self._get_default_port(name)

        # Call the appropriate start method
        try:
            success, message = method(port=port, open_browser=open_browser)
            if success:
                return f"🌐 {message}"
            else:
                return f"⚠️  {message}"
        except Exception as e:
            return f"❌ Error starting {name}: {str(e)}"

    def stop_server(self, name: str) -> Tuple[bool, str]:
        """
        Stop a running server.

        Args:
            name (str): Server name (e.g., 'typo', 'cmd')

        Returns:
            tuple: (success, message)
        """
        if name not in self.servers:
            return False, f"⚠️  No server '{name}' is registered"

        server_info = self.servers[name]
        pid = server_info.get('pid')

        if not pid:
            return False, f"❌ No PID found for '{name}'"

        if not self._is_process_running(pid):
            # Process not running, clean up state
            del self.servers[name]
            self._save_state()
            return False, f"⚠️  Server '{name}' was not running (cleaned up)"

        try:
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)

            # Wait for process to terminate
            for _ in range(10):
                if not self._is_process_running(pid):
                    break
                time.sleep(0.5)

            # Force kill if still running
            if self._is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)

            # Clean up state
            del self.servers[name]
            self._save_state()

            return True, f"✅ Stopped {name} server (PID: {pid})"

        except ProcessLookupError:
            # Process already dead
            del self.servers[name]
            self._save_state()
            return True, f"✅ Server '{name}' already stopped"
        except PermissionError:
            return False, f"❌ Permission denied stopping PID {pid}"
        except Exception as e:
            return False, f"❌ Error stopping server: {e}"

    def get_status(self, name: Optional[str] = None) -> str:
        """
        Get status of server(s).

        Args:
            name (str, optional): Specific server name, or None for all

        Returns:
            str: Status message
        """
        if name:
            if name not in self.servers:
                return f"⚠️  No server '{name}' registered"

            server_info = self.servers[name]
            pid = server_info.get('pid')
            port = server_info.get('port')
            url = server_info.get('url')
            started_at = server_info.get('started_at', 0)
            log_file = server_info.get('log_file', 'Unknown')

            if self._is_process_running(pid):
                uptime = time.time() - started_at
                uptime_str = self._format_uptime(uptime)
                return (f"✅ {name} is running\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       f"📍 PID: {pid}\n"
                       f"🔗 URL: {url}\n"
                       f"🔌 Port: {port}\n"
                       f"⏱️  Uptime: {uptime_str}\n"
                       f"📋 Logs: {log_file}\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       f"⏹️  Stop: OUTPUT STOP {name}")
            else:
                # Clean up dead process
                del self.servers[name]
                self._save_state()
                return f"❌ {name} is not running (cleaned up stale state)"
        else:
            # Show all servers
            if not self.servers:
                return "📭 No servers running"

            status_lines = ["� Server Status", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]

            for srv_name, info in list(self.servers.items()):
                pid = info.get('pid')
                url = info.get('url', 'Unknown')
                port = info.get('port', '?')
                started_at = info.get('started_at', 0)

                if self._is_process_running(pid):
                    uptime = time.time() - started_at
                    uptime_str = self._format_uptime(uptime)
                    status_lines.append(f"✅ {srv_name.ljust(18)} {url.ljust(30)} ⏱ {uptime_str}")
                    status_lines.append(f"   PID: {pid}  Port: {port}")
                else:
                    status_lines.append(f"❌ {srv_name}: Not running (stale)")
                    del self.servers[srv_name]

            status_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            status_lines.append("")
            status_lines.append("Commands:")
            status_lines.append("  OUTPUT START <name>   - Start a server")
            status_lines.append("  OUTPUT STOP <name>    - Stop a server")
            status_lines.append("  OUTPUT LIST           - List all available extensions")

            self._save_state()
            return '\n'.join(status_lines)

    def list_servers(self) -> str:
        """List all available servers (installed or not)."""
        lines = ["📋 Available Servers:", "━━━━━━━━━━━━━━━━━━"]

        # Check typo (cloned external extension)
        typo_dir = self.cloned_dir / 'typo'
        if (typo_dir / 'package.json').exists():
            status = "✅ Installed"
            if 'typo' in self.servers and self._is_process_running(self.servers['typo'].get('pid')):
                status += f" (Running on port {self.servers['typo'].get('port', 5173)})"
        else:
            status = "❌ Not installed"
        lines.append(f"typo            - Web markdown editor - {status}")

        # Check dashboard (built-in core extension)
        dashboard_dir = self.core_dir / 'dashboard'
        if (dashboard_dir / 'index.html').exists():
            status = "✅ Installed"
            if 'dashboard' in self.servers and self._is_process_running(self.servers['dashboard'].get('pid')):
                status += f" (Running on port {self.servers['dashboard'].get('port', 8887)})"
        else:
            status = "❌ Not installed"
        lines.append(f"dashboard       - Unified extension hub - {status}")

        # Check desktop (built-in core extension)
        desktop_dir = self.core_dir / 'desktop'
        if (desktop_dir / 'index.html').exists():
            status = "✅ Installed"
            if 'desktop' in self.servers and self._is_process_running(self.servers['desktop'].get('pid')):
                status += f" (Running on port {self.servers['desktop'].get('port', 8886)})"
        else:
            status = "❌ Not installed"
        lines.append(f"desktop         - Mac OS System 1 desktop - {status}")

        # Check terminal (built-in core extension)
        terminal_dir = self.core_dir / 'terminal'
        if (terminal_dir / 'index.html').exists():
            status = "✅ Installed"
            if 'terminal' in self.servers and self._is_process_running(self.servers['terminal'].get('pid')):
                status += f" (Running on port {self.servers['terminal'].get('port', 8890)})"
        else:
            status = "❌ Not installed"
        lines.append(f"terminal        - Web terminal interface - {status}")

        # Check teletext (built-in core extension)
        teletext_dir = self.core_dir / 'teletext'
        if (teletext_dir / 'index.html').exists():
            status = "✅ Installed"
            if 'teletext' in self.servers and self._is_process_running(self.servers['teletext'].get('pid')):
                status += f" (Running on port {self.servers['teletext'].get('port', 8891)})"
        else:
            status = "❌ Not installed"
        lines.append(f"teletext        - BBC Teletext interface - {status}")

        lines.append("")
        lines.append("To install:")
        lines.append("  typo:      bash extensions/setup/setup_typo.sh")
        lines.append("  All other extensions are pre-installed")
        lines.append("")
        lines.append("Usage:")
        lines.append("  OUTPUT START <name> [--port N] [--no-browser]")
        lines.append("  OUTPUT STOP <name>")
        lines.append("  OUTPUT STATUS [name]")

        return '\n'.join(lines)

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process is running."""
        if not pid:
            return False
        try:
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            return True
        except (OSError, ProcessLookupError):
            return False

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True

    def _check_node(self) -> bool:
        """Check if Node.js is available."""
        try:
            subprocess.run(['node', '--version'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def cleanup_all(self):
        """Stop all running servers (called on uDOS exit)."""
        for name in list(self.servers.keys()):
            self.stop_server(name)

    def open_in_browser(self, url: str) -> bool:
        """
        Open URL in browser.

        Args:
            url (str): URL to open

        Returns:
            bool: Success status
        """
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print(f"🔗 Open manually: {url}")
            return False
