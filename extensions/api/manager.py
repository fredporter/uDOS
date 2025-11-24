#!/usr/bin/env python3
"""
uDOS API Server Manager
Auto-launch and health monitoring for Teletext API Server
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

# Paths
UDOS_ROOT = Path(__file__).parent.parent.parent
API_SERVER_PATH = UDOS_ROOT / "extensions/api/server.py"
VENV_PYTHON = UDOS_ROOT / ".venv/bin/python"
PID_FILE = UDOS_ROOT / "memory/logs/.api_server.pid"
LOG_FILE = UDOS_ROOT / "memory/logs/api_server.log"

# Default configuration
DEFAULT_PORT = 5001
HEALTH_CHECK_INTERVAL = 30  # seconds
MAX_RESTART_ATTEMPTS = 3
RESTART_DELAY = 5  # seconds


class APIServerManager:
    """Manages the Teletext API server lifecycle."""

    def __init__(self, port=DEFAULT_PORT, auto_restart=True):
        self.port = port
        self.auto_restart = auto_restart
        self.process = None
        self.restart_attempts = 0
        self.running = False

    def is_port_available(self):
        """Check if the configured port is available."""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', self.port))
            sock.close()
            return True
        except OSError:
            return False

    def find_available_port(self):
        """Find an available port starting from the configured port."""
        import socket
        port = self.port
        while port < self.port + 100:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                port += 1
        return None

    def start_server(self):
        """Start the API server."""
        # Check if API server file exists
        if not API_SERVER_PATH.exists():
            print(f"❌ API server not found: {API_SERVER_PATH}")
            print("   Install web extensions or disable api_server_enabled in settings")
            return False

        # Check if already running
        if self.is_running():
            print(f"⚠️  API server already running (PID: {self.get_pid()})")
            return False

        # Check port availability
        if not self.is_port_available():
            print(f"⚠️  Port {self.port} is in use")
            new_port = self.find_available_port()
            if new_port:
                print(f"📡 Using port {new_port} instead")
                self.port = new_port
            else:
                print("❌ No available ports found")
                return False

        # Ensure log directory exists
        LOG_FILE.parent.mkdir(exist_ok=True)

        # Start server process
        env = os.environ.copy()
        env['PORT'] = str(self.port)

        try:
            with open(LOG_FILE, 'a') as log:
                log.write(f"\n{'='*70}\n")
                log.write(f"Starting API server at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                log.write(f"Port: {self.port}\n")
                log.write(f"{'='*70}\n\n")

                self.process = subprocess.Popen(
                    [str(VENV_PYTHON), str(API_SERVER_PATH)],
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=str(UDOS_ROOT)
                )

            # Save PID
            PID_FILE.parent.mkdir(exist_ok=True)
            PID_FILE.write_text(str(self.process.pid))

            # Wait a moment to check if it started successfully
            time.sleep(2)

            if self.process.poll() is None:
                print(f"✅ API server started (PID: {self.process.pid})")
                print(f"🌐 Server: http://localhost:{self.port}")
                print(f"📝 Log file: {LOG_FILE}")
                self.running = True
                self.restart_attempts = 0
                return True
            else:
                print(f"❌ API server failed to start (exit code: {self.process.returncode})")
                return False

        except Exception as e:
            print(f"❌ Failed to start API server: {e}")
            return False

    def stop_server(self):
        """Stop the API server."""
        pid = self.get_pid()

        if pid is None:
            print("⚠️  No API server running")
            return True

        try:
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 Sent shutdown signal to API server (PID: {pid})")

            # Wait for process to terminate
            for _ in range(10):
                try:
                    os.kill(pid, 0)  # Check if process exists
                    time.sleep(0.5)
                except OSError:
                    break

            # Force kill if still running
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
                print(f"⚠️  Force killed API server (PID: {pid})")
            except OSError:
                pass

            # Clean up PID file
            if PID_FILE.exists():
                PID_FILE.unlink()

            print("✅ API server stopped")
            self.running = False
            return True

        except Exception as e:
            print(f"❌ Failed to stop API server: {e}")
            return False

    def restart_server(self):
        """Restart the API server."""
        print("🔄 Restarting API server...")
        self.stop_server()
        time.sleep(RESTART_DELAY)
        return self.start_server()

    def get_pid(self):
        """Get the PID of the running server."""
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text().strip())
                # Check if process is actually running
                os.kill(pid, 0)
                return pid
            except (ValueError, OSError):
                # PID file exists but process is dead
                PID_FILE.unlink()
                return None
        return None

    def is_running(self):
        """Check if the API server is running."""
        return self.get_pid() is not None

    def health_check(self):
        """Perform health check on the API server."""
        if not self.is_running():
            return False

        try:
            import requests
            response = requests.get(f"http://localhost:{self.port}/api/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def monitor(self):
        """Monitor the API server and restart if needed."""
        print(f"\n📡 Monitoring API server (health check every {HEALTH_CHECK_INTERVAL}s)")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while self.running:
                time.sleep(HEALTH_CHECK_INTERVAL)

                if not self.health_check():
                    print(f"⚠️  Health check failed")

                    if self.auto_restart and self.restart_attempts < MAX_RESTART_ATTEMPTS:
                        self.restart_attempts += 1
                        print(f"🔄 Attempting restart ({self.restart_attempts}/{MAX_RESTART_ATTEMPTS})")

                        if self.restart_server():
                            print("✅ Server restarted successfully")
                        else:
                            print(f"❌ Restart failed (attempt {self.restart_attempts})")
                    else:
                        print("❌ Max restart attempts reached or auto-restart disabled")
                        break
                else:
                    print(f"✅ Health check passed (PID: {self.get_pid()})")

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping monitor...")

    def status(self):
        """Show API server status."""
        pid = self.get_pid()

        if pid:
            print(f"✅ API server is running")
            print(f"   PID: {pid}")
            print(f"   Port: {self.port}")
            print(f"   URL: http://localhost:{self.port}")

            if self.health_check():
                print(f"   Health: OK")
            else:
                print(f"   Health: ⚠️  Failed")
        else:
            print("⚠️  API server is not running")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="uDOS API Server Manager")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'monitor'],
                       help='Action to perform')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                       help=f'Port to run server on (default: {DEFAULT_PORT})')
    parser.add_argument('--no-auto-restart', action='store_true',
                       help='Disable automatic restart on failure')

    args = parser.parse_args()

    manager = APIServerManager(port=args.port, auto_restart=not args.no_auto_restart)

    if args.action == 'start':
        manager.start_server()
    elif args.action == 'stop':
        manager.stop_server()
    elif args.action == 'restart':
        manager.restart_server()
    elif args.action == 'status':
        manager.status()
    elif args.action == 'monitor':
        if manager.start_server():
            manager.monitor()


if __name__ == '__main__':
    main()
