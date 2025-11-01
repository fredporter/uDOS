#!/usr/bin/env python3
"""
uDOS Web Extensions v1.0.1 - Classicy Integration Launcher
==========================================================

Comprehensive launcher for all web extensions including the new Classicy Desktop
that requires Node.js/React build system.

Features:
• Automatic dependency checking (Python, Node.js)
• Classicy desktop build and serve automation
• All existing web extensions support
• Unified management interface

Author: uDOS Development Team
Version: 1.0.1 + Classicy
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

class ClassicyIntegratedManager:
    """Enhanced web extension manager with Classicy desktop support"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.running = False

    def print_banner(self):
        """Print the enhanced startup banner"""
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                uDOS Web Extensions v1.0.1                   ║
║                 + Classicy Desktop Integration              ║
║              Universal Data Operating System                ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.BOLD}🌟 Complete Classic Mac Experience:{Colors.END}
   🖥️ Classicy Desktop - Full Mac OS 8 environment (React/TypeScript)
   🎨 CSS Framework Showcase (4 retro frameworks)
   🌓 Light/Dark mode dashboard with screensavers
   🔤 Authentic typography and Mac styling throughout

{Colors.BOLD}🚀 Extension Collection:{Colors.END}
   {Colors.GREEN}✅ Classicy Desktop{Colors.END}    - Complete Mac OS 8 interface (React)
   {Colors.GREEN}✅ Dashboard{Colors.END}           - Modern desktop with classic styling
   {Colors.GREEN}✅ CSS Frameworks{Colors.END}     - 4 retro framework demos
   {Colors.GREEN}✅ Terminal{Colors.END}            - Web-based command interface
   {Colors.GREEN}✅ Markdown Viewer{Colors.END}    - Document viewer and editor
   {Colors.GREEN}✅ Font Editor{Colors.END}        - Bitmap font creation tool

""")

    def check_dependencies(self):
        """Enhanced dependency checking for Node.js and Python"""
        print(f"{Colors.BOLD}🔍 Checking Dependencies...{Colors.END}")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"{Colors.RED}❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}{Colors.END}")
            return False
        else:
            print(f"{Colors.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}{Colors.END}")

        # Check Node.js for Classicy
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"{Colors.GREEN}✅ Node.js {node_version}{Colors.END}")

                # Check npm
                npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
                if npm_result.returncode == 0:
                    npm_version = npm_result.stdout.strip()
                    print(f"{Colors.GREEN}✅ npm {npm_version}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠️  npm not found - Classicy desktop may not work{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Node.js not found - Classicy desktop will be skipped{Colors.END}")
                return "python-only"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{Colors.YELLOW}⚠️  Node.js not available - Classicy desktop will be skipped{Colors.END}")
            return "python-only"

        return True

    def setup_classicy_desktop(self):
        """Build and prepare Classicy desktop if needed"""
        classicy_dir = self.base_path / "classicy-desktop"
        dist_dir = classicy_dir / "dist"

        if not classicy_dir.exists():
            print(f"{Colors.YELLOW}⚠️  Classicy desktop not found - skipping{Colors.END}")
            return False

        print(f"{Colors.BOLD}🖥️ Setting up Classicy Desktop...{Colors.END}")

        # Check if already built
        if dist_dir.exists() and (dist_dir / "index.html").exists():
            print(f"{Colors.GREEN}✅ Classicy desktop already built{Colors.END}")
            return True

        try:
            # Install dependencies if needed
            if not (classicy_dir / "node_modules").exists():
                print(f"{Colors.BLUE}📦 Installing Classicy dependencies...{Colors.END}")
                install_result = subprocess.run(
                    ['npm', 'install'],
                    cwd=classicy_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes max
                )
                if install_result.returncode != 0:
                    print(f"{Colors.RED}❌ Failed to install Classicy dependencies{Colors.END}")
                    print(install_result.stderr)
                    return False
                print(f"{Colors.GREEN}✅ Dependencies installed{Colors.END}")

            # Build the project
            print(f"{Colors.BLUE}🔨 Building Classicy desktop...{Colors.END}")
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=classicy_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            if build_result.returncode != 0:
                print(f"{Colors.RED}❌ Failed to build Classicy desktop{Colors.END}")
                print(build_result.stderr)
                return False

            print(f"{Colors.GREEN}✅ Classicy desktop built successfully{Colors.END}")
            return True

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Classicy build timed out{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error setting up Classicy: {e}{Colors.END}")
            return False

    def start_classicy_desktop(self):
        """Start the Classicy desktop server"""
        classicy_dist = self.base_path / "classicy-desktop" / "dist"

        if not classicy_dist.exists():
            print(f"{Colors.RED}❌ Classicy desktop not built{Colors.END}")
            return False

        try:
            # Start HTTP server on the dist directory
            process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "3000"],
                cwd=classicy_dist,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes['classicy-desktop'] = {
                'process': process,
                'port': 3000,
                'path': classicy_dist,
                'url': 'http://localhost:3000',
                'type': 'react-app'
            }

            time.sleep(1)  # Give server time to start

            if process.poll() is None:
                print(f"{Colors.GREEN}✅ Classicy Desktop: Started on port 3000{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Classicy Desktop: Failed to start{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ Classicy Desktop: Error - {e}{Colors.END}")
            return False

    def start_regular_extension(self, name, config):
        """Start a regular Python HTTP server extension"""
        port = config.get('port')
        path = config.get('path', name)

        extension_dir = self.base_path / path
        if not extension_dir.exists():
            print(f"{Colors.RED}❌ {name}: Directory not found - {extension_dir}{Colors.END}")
            return False

        try:
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
                'url': f"http://localhost:{port}",
                'type': 'python-server'
            }

            time.sleep(0.5)

            if process.poll() is None:
                print(f"{Colors.GREEN}✅ {name}: Started on port {port}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ {name}: Failed to start{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ {name}: Error - {e}{Colors.END}")
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
                'url': 'http://localhost:8882-8885',
                'type': 'multi-server'
            }

            time.sleep(2)  # Give frameworks time to start

            if process.poll() is None:
                print(f"{Colors.GREEN}✅ CSS Frameworks: All 4 frameworks started{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ CSS Frameworks: Failed to start{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ CSS Frameworks: Error - {e}{Colors.END}")
            return False

    def start_all(self, node_available=True):
        """Start all web extensions"""
        print(f"\n{Colors.BOLD}🚀 Starting All Extensions...{Colors.END}")

        success_count = 0
        total_count = 0

        # Start Classicy Desktop first (if Node.js available)
        if node_available and node_available != "python-only":
            if self.setup_classicy_desktop():
                total_count += 1
                if self.start_classicy_desktop():
                    success_count += 1

        # Start regular extensions
        regular_extensions = {
            "dashboard": {"port": 8001, "path": "dashboard"},
            "terminal": {"port": 8890, "path": "terminal"},
            "markdown-viewer": {"port": 8889, "path": "markdown-viewer"},
            "font-editor": {"port": 8888, "path": "font-editor"}
        }

        for name, config in regular_extensions.items():
            total_count += 1
            if self.start_regular_extension(name, config):
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
        """Print comprehensive status of all running extensions"""
        if not self.processes:
            print(f"{Colors.YELLOW}No extensions currently running{Colors.END}")
            return

        print(f"\n{Colors.BOLD}🌐 Running Extensions:{Colors.END}")
        print("=" * 80)

        for name, info in self.processes.items():
            process = info['process']
            url = info['url']
            ext_type = info.get('type', 'unknown')

            if process.poll() is None:
                status = f"{Colors.GREEN}🟢 Running{Colors.END}"
            else:
                status = f"{Colors.RED}🔴 Stopped{Colors.END}"

            print(f"   {status} {name.ljust(20)} {url.ljust(25)} ({ext_type})")

        print("\n" + "=" * 80)
        print(f"{Colors.CYAN}💡 Quick Access URLs:{Colors.END}")
        print(f"   🖥️  Classicy Desktop:  http://localhost:3000")
        print(f"   📱 Main Dashboard:    http://localhost:8001")
        print(f"   🎨 CSS Frameworks:    http://localhost:8882-8885")

    def monitor_extensions(self):
        """Enhanced monitoring with better status reporting"""
        self.running = True
        print(f"\n{Colors.BOLD}📱 Live Monitoring Started{Colors.END}")
        print(f"{Colors.CYAN}💡 Tips:{Colors.END}")
        print("   • Press Ctrl+C to stop all extensions")
        print("   • Visit http://localhost:3000 for full Classicy Desktop")
        print("   • Visit http://localhost:8001 for unified dashboard")
        print("   • All frameworks accessible via dashboard or direct URLs")
        print()

        try:
            while self.running:
                time.sleep(5)
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
                if process.poll() is None:
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

def main():
    """Main entry point"""
    manager = ClassicyIntegratedManager()

    if len(sys.argv) < 2:
        command = "start"
    else:
        command = sys.argv[1].lower()

    if command == "start":
        manager.print_banner()
        deps_status = manager.check_dependencies()
        if deps_status:
            if manager.start_all(deps_status):
                manager.print_status()
                manager.monitor_extensions()
    elif command == "stop":
        manager.stop_all()
    elif command == "status":
        manager.print_status()
    else:
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.END}")
        print(f"Use 'python3 classicy-launcher.py start|stop|status'")

if __name__ == "__main__":
    main()
