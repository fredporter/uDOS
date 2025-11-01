#!/usr/bin/env python3
"""
uDOS Web Extensions v1.0.1 - Deployment Manager
===============================================

Comprehensive deployment script for launching and managing all web extensions
in the uDOS ecosystem with proper error handling and status monitoring.

Author: uDOS Development Team
Version: 1.0.1
Date: November 2, 2025
"""

import subprocess
import time
import os
import sys
import json
import signal
import threading
from datetime import datetime
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class WebExtensionManager:
    """Manages all uDOS web extensions"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.config = self.load_version_manifest()
        self.running = False

    def load_version_manifest(self):
        """Load the version manifest with extension configuration"""
        manifest_path = self.base_path / "version-manifest.json"
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Version manifest not found: {manifest_path}{Colors.END}")
            return self.get_default_config()

    def get_default_config(self):
        """Default configuration if manifest is missing"""
        return {
            "extensions": {
                "dashboard": {"port": 8001, "path": "dashboard"},
                "terminal": {"port": 8890, "path": "terminal"},
                "markdown-viewer": {"port": 8889, "path": "markdown-viewer"},
                "font-editor": {"port": 8888, "path": "font-editor"},
                "classicy-desktop": {"port": 3000, "path": "classicy-desktop/dist", "framework": "node"}
            }
        }

    def print_banner(self):
        """Print the startup banner"""
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                   uDOS Web Extensions v1.0.1                ║
║              Universal Data Operating System                 ║
║                  Deployment Manager                         ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.BOLD}🌟 What's New in v1.0.1:{Colors.END}
   🎨 CSS Framework Showcase (4 retro frameworks)
   🖥️ Desktop Interface with macOS styling
   🌓 Light/Dark mode toggle
   🌌 After Dark screensaver integration
   🔤 Chunky retro fonts (VT323)

{Colors.BOLD}📅 Release Date:{Colors.END} {self.config.get('release_date', 'November 2, 2025')}
{Colors.BOLD}🎯 Compatibility:{Colors.END} uDOS v{self.config.get('compatibility', {}).get('uDOS', '1.3.0')}+

""")

    def check_dependencies(self):
        """Check if required dependencies are available"""
        print(f"{Colors.BOLD}🔍 Checking Dependencies...{Colors.END}")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"{Colors.RED}❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}{Colors.END}")
            return False
        else:
            print(f"{Colors.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}{Colors.END}")

        # Check if ports are available
        print(f"\n{Colors.BOLD}🌐 Checking Port Availability...{Colors.END}")
        ports_ok = True
        for ext_name, ext_config in self.config.get('extensions', {}).items():
            if 'port' in ext_config:
                port = ext_config['port']
                if self.is_port_in_use(port):
                    print(f"{Colors.YELLOW}⚠️  Port {port} ({ext_name}) is already in use{Colors.END}")
                else:
                    print(f"{Colors.GREEN}✅ Port {port} ({ext_name}) available{Colors.END}")

        return True

    def is_port_in_use(self, port):
        """Check if a port is currently in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False

    def start_extension(self, name, config):
        """Start a single web extension"""
        port = config.get('port')
        path = config.get('path', name)

        extension_dir = self.base_path / path
        if not extension_dir.exists():
            print(f"{Colors.RED}❌ {name}: Directory not found - {extension_dir}{Colors.END}")
            return False

        try:
            # Start HTTP server
            cmd = [sys.executable, "-m", "http.server", str(port)]
            process = subprocess.Popen(
                cmd,
                cwd=extension_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes[name] = {
                'process': process,
                'port': port,
                'path': extension_dir,
                'url': f"http://localhost:{port}"
            }

            # Give server time to start
            time.sleep(0.5)

            if process.poll() is None:  # Process is still running
                print(f"{Colors.GREEN}✅ {name}: Started on port {port}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ {name}: Failed to start{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ {name}: Error starting - {e}{Colors.END}")
            return False

    def start_css_frameworks(self):
        """Start the CSS framework showcase servers"""
        frameworks_dir = self.base_path / "css-frameworks"
        launcher_script = frameworks_dir / "launch_all.py"

        if not launcher_script.exists():
            print(f"{Colors.YELLOW}⚠️  CSS Frameworks: Launcher not found{Colors.END}")
            return False

        try:
            process = subprocess.Popen(
                [sys.executable, "launch_all.py"],
                cwd=frameworks_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes['css-frameworks'] = {
                'process': process,
                'port': 'multiple',
                'path': frameworks_dir,
                'url': 'http://localhost:8882-8885'
            }

            time.sleep(1)  # Give frameworks time to start

            if process.poll() is None:
                print(f"{Colors.GREEN}✅ CSS Frameworks: All 4 frameworks started{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ CSS Frameworks: Failed to start{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ CSS Frameworks: Error - {e}{Colors.END}")
            return False

    def start_all(self):
        """Start all web extensions"""
        print(f"\n{Colors.BOLD}🚀 Starting Web Extensions...{Colors.END}")

        success_count = 0
        total_count = 0

        # Start individual extensions
        for name, config in self.config.get('extensions', {}).items():
            if name == 'css-frameworks':
                continue  # Handle separately
            if 'external' in config and config['external']:
                print(f"{Colors.BLUE}ℹ️  {name}: External extension (manual start required){Colors.END}")
                continue

            total_count += 1
            if self.start_extension(name, config):
                success_count += 1

        # Start CSS frameworks
        total_count += 1
        if self.start_css_frameworks():
            success_count += 1

        print(f"\n{Colors.BOLD}📊 Startup Summary:{Colors.END}")
        print(f"   ✅ Started: {success_count}/{total_count} extensions")

        if success_count == total_count:
            print(f"{Colors.GREEN}🎉 All extensions started successfully!{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Some extensions failed to start{Colors.END}")

        return success_count > 0

    def print_status(self):
        """Print the status of all running extensions"""
        if not self.processes:
            print(f"{Colors.YELLOW}No extensions currently running{Colors.END}")
            return

        print(f"\n{Colors.BOLD}🌐 Running Extensions:{Colors.END}")
        print("=" * 60)

        for name, info in self.processes.items():
            process = info['process']
            url = info['url']

            if process.poll() is None:  # Still running
                status = f"{Colors.GREEN}🟢 Running{Colors.END}"
            else:
                status = f"{Colors.RED}🔴 Stopped{Colors.END}"

            print(f"   {status} {name.ljust(20)} {url}")

        print("\n" + "=" * 60)

    def monitor_extensions(self):
        """Monitor running extensions and provide live status"""
        self.running = True
        print(f"\n{Colors.BOLD}📱 Live Monitoring Started{Colors.END}")
        print(f"{Colors.CYAN}💡 Tips:{Colors.END}")
        print("   • Press Ctrl+C to stop all extensions")
        print("   • Visit the URLs above to access each extension")
        print("   • Dashboard (8001) provides central control interface")
        print()

        try:
            while self.running:
                # Check process health
                for name, info in list(self.processes.items()):
                    process = info['process']
                    if process.poll() is not None:  # Process has stopped
                        print(f"{Colors.RED}❌ {name} has stopped unexpectedly{Colors.END}")
                        del self.processes[name]

                time.sleep(5)  # Check every 5 seconds

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}🛑 Shutdown requested...{Colors.END}")
            self.stop_all()

    def stop_all(self):
        """Stop all running extensions"""
        self.running = False
        print(f"\n{Colors.BOLD}⏹️  Stopping Extensions...{Colors.END}")

        for name, info in self.processes.items():
            process = info['process']
            try:
                if process.poll() is None:  # Still running
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"{Colors.GREEN}✅ Stopped {name}{Colors.END}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"{Colors.YELLOW}⚠️  Force killed {name}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error stopping {name}: {e}{Colors.END}")

        self.processes.clear()
        print(f"{Colors.GREEN}🎉 All extensions stopped{Colors.END}")

    def print_help(self):
        """Print help information"""
        print(f"""
{Colors.BOLD}uDOS Web Extensions v1.0.1 - Usage Guide{Colors.END}

{Colors.BOLD}Commands:{Colors.END}
   python3 deploy.py start     Start all web extensions
   python3 deploy.py stop      Stop all running extensions
   python3 deploy.py status    Show extension status
   python3 deploy.py help      Show this help message

{Colors.BOLD}Extension URLs (when running):{Colors.END}
   🖥️  Dashboard:        http://localhost:8001
   💻 Terminal:          http://localhost:8890
   📖 Markdown Viewer:   http://localhost:8889
   🎨 Font Editor:       http://localhost:8888

   🎨 CSS Framework Showcase:
   🖥️  Classic.css:      http://localhost:8885
   🎮 NES.css:          http://localhost:8884
   💾 System.css:       http://localhost:8883
   ✨ After Dark CSS:   http://localhost:8882

{Colors.BOLD}Features:{Colors.END}
   • Automatic dependency checking
   • Port conflict detection
   • Live process monitoring
   • Graceful shutdown handling
   • Comprehensive error reporting

{Colors.BOLD}Keyboard Shortcuts (in Dashboard):{Colors.END}
   ⌘T - Toggle Dark Mode
   ⌘R - Refresh Dashboard
   ⌘S/M/D - Open Workspaces
   ESC - Exit Screensaver

{Colors.BOLD}Requirements:{Colors.END}
   • Python 3.8+
   • Modern web browser
   • Available ports 8001, 8882-8890
""")

def main():
    """Main entry point"""
    manager = WebExtensionManager()

    if len(sys.argv) < 2:
        command = "start"
    else:
        command = sys.argv[1].lower()

    if command == "help" or command == "--help" or command == "-h":
        manager.print_help()
    elif command == "start":
        manager.print_banner()
        if manager.check_dependencies():
            if manager.start_all():
                manager.print_status()
                manager.monitor_extensions()
    elif command == "stop":
        manager.stop_all()
    elif command == "status":
        manager.print_status()
    else:
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.END}")
        print(f"Use 'python3 deploy.py help' for usage information")

if __name__ == "__main__":
    main()
