"""
Typo Web Editor Manager
Manages the Typo markdown editor server and file opening.

Version: 1.0.0
"""

import subprocess
import os
import time
import webbrowser
import socket
from pathlib import Path
from typing import Tuple, Optional


class TypoManager:
    """
    Manage Typo web-based markdown editor.

    Features:
    - Start/stop Typo development server
    - Open files in Typo editor
    - Detect server status
    - Port management
    - Mode selection (edit/preview/slides)
    """

    def __init__(self, config=None):
        """
        Initialize Typo manager.

        Args:
            config: Config instance (optional)
        """
        self.config = config
        self.typo_path = Path("extensions/cloned/typo")
        self.port = self._get_port()
        self.process = None
        self._startup_wait = 5  # Seconds to wait for server start

    def _get_port(self) -> int:
        """Get configured Typo port."""
        if self.config:
            return self.config.get('editor.typo_port', 9000)
        return 9000

    def is_installed(self) -> bool:
        """
        Check if Typo is installed.

        Returns:
            True if Typo is installed (package.json exists)
        """
        package_json = self.typo_path / "package.json"
        node_modules = self.typo_path / "node_modules"
        return package_json.exists() and node_modules.exists()

    def is_running(self) -> bool:
        """
        Check if Typo server is running.

        Returns:
            True if server is accessible on configured port
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def find_available_port(self, start_port: int = 9000, max_attempts: int = 10) -> Optional[int]:
        """
        Find an available port starting from start_port.

        Args:
            start_port: Port to start checking from
            max_attempts: Maximum number of ports to try

        Returns:
            Available port number or None
        """
        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()

                # Port is available if connection fails
                if result != 0:
                    return port
            except Exception:
                continue

        return None

    def start_server(self, background: bool = True, auto_open: bool = False) -> Tuple[bool, str]:
        """
        Start Typo development server.

        Args:
            background: Run server in background
            auto_open: Automatically open browser

        Returns:
            (success, message) tuple
        """
        # Check if installed
        if not self.is_installed():
            return (False,
                   "❌ Typo not installed\n\n"
                   "Install with: ./extensions/setup/setup_typo.sh\n"
                   "Or: cd extensions/cloned/typo && npm install")

        # Check if already running
        if self.is_running():
            return (True,
                   f"ℹ️  Typo already running at http://localhost:{self.port}")

        # Find available port if configured port is taken
        available_port = self.port
        if not self._is_port_available(self.port):
            available_port = self.find_available_port(self.port)
            if not available_port:
                return (False,
                       f"❌ No available ports found (tried {self.port}-{self.port+9})")

        try:
            # Build command
            cmd = ["npm", "run", "dev", "--", "--port", str(available_port)]

            if auto_open:
                cmd.append("--open")

            if background:
                # Start in background
                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(self.typo_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )

                # Wait for server to start
                print(f"⏳ Starting Typo server (port {available_port})...")

                for i in range(self._startup_wait):
                    time.sleep(1)
                    if self.is_running():
                        break
                    print(f"   Waiting... {i+1}/{self._startup_wait}s")

                if self.is_running():
                    # Update port if it changed
                    if available_port != self.port:
                        self.port = available_port
                        if self.config:
                            self.config.set('editor.typo_port', available_port)
                            self.config.save()

                    return (True,
                           f"✅ Typo server started\n"
                           f"🌐 URL: http://localhost:{self.port}\n"
                           f"💡 Use Ctrl+C to stop, or run: TYPO STOP")
                else:
                    return (False,
                           "❌ Typo server failed to start\n"
                           "Check logs: npm run dev --prefix extensions/cloned/typo")
            else:
                # Foreground mode (blocking)
                print(f"🚀 Starting Typo server on port {available_port}...")
                print("💡 Press Ctrl+C to stop")
                subprocess.run(cmd, cwd=str(self.typo_path))
                return (True, "Typo server stopped")

        except FileNotFoundError:
            return (False,
                   "❌ npm not found\n"
                   "Install Node.js: https://nodejs.org/")
        except Exception as e:
            return (False, f"❌ Error starting Typo: {str(e)}")

    def stop_server(self) -> Tuple[bool, str]:
        """
        Stop Typo server.

        Returns:
            (success, message) tuple
        """
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
                return (True, "✅ Typo server stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process = None
                return (True, "✅ Typo server killed (force)")
            except Exception as e:
                return (False, f"❌ Error stopping server: {str(e)}")
        else:
            # Try to find and kill via lsof/fuser
            try:
                result = subprocess.run(
                    ['lsof', '-ti', f':{self.port}'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), 15)  # SIGTERM
                        except:
                            pass

                    time.sleep(1)

                    if not self.is_running():
                        return (True, "✅ Typo server stopped")

                return (False, "ℹ️  No Typo server process found")

            except FileNotFoundError:
                return (False, "ℹ️  Cannot stop server (lsof not available)")
            except Exception as e:
                return (False, f"❌ Error: {str(e)}")

    def open_file(self, file_path: str, mode: str = 'edit', auto_start: bool = True) -> Tuple[bool, str]:
        """
        Open file in Typo editor.

        Note: Due to browser File System API, Typo cannot directly open files.
        This method opens Typo and provides instructions for the user.

        Args:
            file_path: Path to markdown file
            mode: 'edit', 'preview', or 'slides'
            auto_start: Auto-start server if not running

        Returns:
            (success, message) tuple
        """
        # Check if installed
        if not self.is_installed():
            return (False,
                   "❌ Typo not installed\n\n"
                   "Install with: ./extensions/setup/setup_typo.sh")

        # Ensure server is running
        if not self.is_running():
            if auto_start:
                success, msg = self.start_server(background=True)
                if not success:
                    return (False, msg)
            else:
                return (False,
                       f"❌ Typo server not running\n"
                       f"Start with: TYPO START\n"
                       f"Or visit: http://localhost:{self.port}")

        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        file_name = os.path.basename(abs_path)

        # Build URL with mode parameter
        url = f"http://localhost:{self.port}"

        # Typo view modes
        if mode == 'slides':
            url += "?view=slides"
        elif mode == 'preview':
            url += "?view=document"
        # 'edit' mode is default (no parameter needed)

        try:
            # Open in default browser
            webbrowser.open(url)

            # Build helpful message
            mode_name = {
                'edit': 'Editor',
                'preview': 'Preview',
                'slides': 'Slideshow'
            }.get(mode, 'Editor')

            return (True,
                   f"✅ Opened Typo {mode_name}\n"
                   f"🌐 URL: {url}\n\n"
                   f"📝 To open your file:\n"
                   f"   1. Click 'Open' button in Typo\n"
                   f"   2. Navigate to: {abs_path}\n"
                   f"   3. Select: {file_name}\n\n"
                   f"💡 Typo uses browser File System API for security\n"
                   f"💾 Changes auto-save to your local file")

        except Exception as e:
            return (False,
                   f"❌ Error opening browser: {str(e)}\n"
                   f"Manual URL: http://localhost:{self.port}")

    def open_editor(self, mode: str = 'edit') -> Tuple[bool, str]:
        """
        Open Typo editor without specific file.

        Args:
            mode: 'edit', 'preview', or 'slides'

        Returns:
            (success, message) tuple
        """
        return self.open_file('', mode=mode)

    def get_status(self) -> dict:
        """
        Get Typo server status.

        Returns:
            Status dictionary with server info
        """
        return {
            'installed': self.is_installed(),
            'running': self.is_running(),
            'port': self.port,
            'url': f'http://localhost:{self.port}' if self.is_running() else None,
            'path': str(self.typo_path),
            'process': self.process is not None
        }

    def _is_port_available(self, port: int) -> bool:
        """Check if a specific port is available."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # Available if connection fails
        except Exception:
            return False


# Convenience function for quick access
def get_typo_manager(config=None) -> TypoManager:
    """
    Get TypoManager instance.

    Args:
        config: Config instance (optional)

    Returns:
        TypoManager instance
    """
    return TypoManager(config)
