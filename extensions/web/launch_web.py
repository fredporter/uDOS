#!/usr/bin/env python3
"""
uDOS Web Extension Launcher (Python)
Bulletproof, cross-platform web server manager
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
import json
import socket
from typing import Optional, Tuple, Dict


class WebExtensionLauncher:
    """Manages uDOS web extension servers."""

    # Server configurations
    SERVERS = {
        'dashboard': {
            'port': 8887,
            'path': 'extensions/web/dashboard',
            'name': 'Dashboard',
            'icon': '🌀',
            'script': 'server.py'
        },
        'font-editor': {
            'port': 8888,
            'path': 'extensions/web/font-editor',
            'name': 'Font Editor',
            'icon': '🎨',
            'script': 'server.py'
        },
        'markdown-viewer': {
            'port': 8889,
            'path': 'extensions/web/markdown-viewer',
            'name': 'Markdown Viewer',
            'icon': '📖',
            'script': 'server.py'
        },
        'terminal': {
            'port': 8890,
            'path': 'extensions/web/terminal',
            'name': 'Web Terminal',
            'icon': '💻',
            'script': 'server.py'
        }
    }

    def __init__(self, udos_root: Optional[Path] = None):
        """Initialize launcher."""
        if udos_root is None:
            # Assume we're in extensions/web
            self.udos_root = Path(__file__).parent.parent.parent
        else:
            self.udos_root = Path(udos_root)

        self.pid_dir = Path('/tmp')
        self.log_dir = Path('/tmp')

    def is_port_in_use(self, port: int) -> bool:
        """Check if port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def get_process_on_port(self, port: int) -> Optional[int]:
        """Get PID of process using port."""
        try:
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except (subprocess.SubprocessError, ValueError):
            pass
        return None

    def kill_port(self, port: int) -> bool:
        """Kill process on port and wait for it to be released."""
        pid = self.get_process_on_port(port)
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                # Force kill if still running
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                print(f"⚠️  Killed process {pid} on port {port}")

                # Wait for port to be released (up to 5 seconds)
                for i in range(10):
                    time.sleep(0.5)
                    if not self.is_port_in_use(port):
                        return True

                print(f"⚠️  Warning: Port {port} may still be in use")
                return True
            except ProcessLookupError:
                pass
        return False

    def get_python_executable(self) -> str:
        """Get Python executable, preferring venv."""
        venv_python = self.udos_root / '.venv' / 'bin' / 'python3'
        if venv_python.exists():
            return str(venv_python)
        return sys.executable

    def start_server(self, server_id: str, port: Optional[int] = None,
                     open_browser: bool = True) -> Tuple[bool, str]:
        """Start a web server."""
        if server_id not in self.SERVERS:
            return False, f"Unknown server: {server_id}"

        config = self.SERVERS[server_id]
        server_port = port or config['port']
        server_path = self.udos_root / config['path']
        server_script = server_path / config['script']

        # Verify server exists
        if not server_script.exists():
            return False, f"Server script not found: {server_script}"

        # Kill existing process on port
        if self.is_port_in_use(server_port):
            print(f"⚠️  Port {server_port} in use, killing existing process...")
            self.kill_port(server_port)
            # kill_port() now polls until port is released

        # Prepare command
        python_exe = self.get_python_executable()

        if server_id == 'dashboard':
            cmd = [python_exe, str(server_script), str(server_port)]
        elif server_id == 'terminal':
            # Terminal server doesn't support --no-browser flag
            cmd = [python_exe, str(server_script), '--port', str(server_port)]
        else:
            cmd = [python_exe, str(server_script), '--port', str(server_port)]
            if not open_browser:
                cmd.append('--no-browser')

        # Start server
        log_file = self.log_dir / f'udos-{server_id}.log'
        pid_file = self.pid_dir / f'udos-{server_id}.pid'

        try:
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    cwd=str(server_path),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )

            # Save PID
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))

            # Wait and verify
            time.sleep(2)

            if self.is_port_in_use(server_port):
                icon = config['icon']
                name = config['name']
                url = f'http://localhost:{server_port}'
                print(f"✅ {icon} {name} started on {url} (PID: {process.pid})")

                # Open browser if requested
                browser_opened = False
                if open_browser:
                    try:
                        if sys.platform == 'darwin':
                            subprocess.Popen(['open', url],
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
                            browser_opened = True
                        elif sys.platform == 'linux' and os.environ.get('DISPLAY'):
                            subprocess.Popen(['xdg-open', url],
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
                            browser_opened = True
                    except Exception:
                        pass  # Silent fail on browser open

                if browser_opened:
                    print(f"🌐 Opening {url} in your browser...")
                    return True, f"Started on port {server_port}, opening in browser"
                else:
                    print(f"🌐 Access at: {url}")
                    return True, f"Started on port {server_port}"
            else:
                # Server failed to start
                with open(log_file, 'r') as f:
                    error_log = f.read()
                return False, f"Failed to bind to port {server_port}. Log:\n{error_log[-500:]}"

        except Exception as e:
            return False, f"Error starting server: {e}"

    def stop_server(self, server_id: str) -> Tuple[bool, str]:
        """Stop a web server."""
        if server_id not in self.SERVERS:
            return False, f"Unknown server: {server_id}"

        config = self.SERVERS[server_id]
        port = config['port']
        pid_file = self.pid_dir / f'udos-{server_id}.pid'

        # Try to kill by PID file first
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                pid_file.unlink()
                print(f"✅ Stopped {config['name']} (PID: {pid})")
                return True, "Stopped"
            except (ValueError, ProcessLookupError, FileNotFoundError):
                pass

        # Fallback to port-based kill
        if self.kill_port(port):
            return True, f"Killed process on port {port}"

        return False, f"No server running on port {port}"

    def start_all(self, open_browser: bool = True):
        """Start all web servers."""
        print("🚀 Starting all uDOS web extensions...\n")

        for server_id in ['dashboard', 'font-editor', 'markdown-viewer', 'terminal']:
            # Only open browser for dashboard
            should_open = open_browser and server_id == 'dashboard'
            success, message = self.start_server(server_id, open_browser=should_open)
            if not success:
                print(f"❌ Failed to start {server_id}: {message}")

        print("\n✨ All servers started!")
        self.show_status()

    def stop_all(self):
        """Stop all web servers."""
        print("🛑 Stopping all uDOS web extensions...\n")

        for server_id in self.SERVERS:
            self.stop_server(server_id)

        print("\n✅ All servers stopped")

    def show_status(self):
        """Show status of all servers."""
        print("\n" + "="*50)
        print("  uDOS Web Extensions Status")
        print("="*50 + "\n")

        for server_id, config in self.SERVERS.items():
            port = config['port']
            icon = config['icon']
            name = config['name']

            if self.is_port_in_use(port):
                pid = self.get_process_on_port(port)
                status = f"✅ RUNNING (PID: {pid})"
                url = f"http://localhost:{port}"
                print(f"  {icon} {name:<18} {status}")
                print(f"     └─ {url}")
            else:
                print(f"  ⭕ {name:<18} STOPPED")

        print("\n" + "="*50 + "\n")

    def restart_all(self):
        """Restart all servers."""
        self.stop_all()
        time.sleep(2)
        self.start_all()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='uDOS Web Extension Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Start all servers
  %(prog)s dashboard          Start dashboard only
  %(prog)s --stop             Stop all servers
  %(prog)s --status           Show server status
  %(prog)s --restart          Restart all servers
        """
    )

    parser.add_argument('server', nargs='?',
                       choices=['dashboard', 'font-editor', 'markdown-viewer', 'terminal'],
                       help='Specific server to start')
    parser.add_argument('--port', type=int, help='Custom port number')
    parser.add_argument('--no-browser', action='store_true',
                       help='Do not open browser')
    parser.add_argument('--stop', action='store_true',
                       help='Stop all servers')
    parser.add_argument('--status', action='store_true',
                       help='Show server status')
    parser.add_argument('--restart', action='store_true',
                       help='Restart all servers')

    args = parser.parse_args()

    launcher = WebExtensionLauncher()

    try:
        if args.stop:
            launcher.stop_all()
        elif args.status:
            launcher.show_status()
        elif args.restart:
            launcher.restart_all()
        elif args.server:
            success, message = launcher.start_server(
                args.server,
                port=args.port,
                open_browser=not args.no_browser
            )
            if not success:
                print(f"❌ Error: {message}")
                sys.exit(1)
        else:
            launcher.start_all(open_browser=not args.no_browser)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
