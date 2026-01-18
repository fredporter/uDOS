#!/usr/bin/env python3
"""
uDOS Server Manager - Unified Control for All uDOS Servers
Bulletproof server lifecycle management with health monitoring
"""

import sys
import os
import time
import json
import requests
from pathlib import Path

# Add extensions to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))
from shared import get_port_manager


class ServerManager:
    """Manages all uDOS servers with health monitoring"""

    SERVERS = {
        'api': {
            'name': 'API Server',
            'port': 5001,
            'health_url': 'http://localhost:5001/api/health',
            'command': 'PORT=5001 python extensions/api/server.py'
        },
        'terminal': {
            'name': 'Retro Terminal',
            'port': 8889,
            'health_url': 'http://localhost:8889/health',
            'command': 'python extensions/core/extensions_server.py terminal'
        },
        'dashboard': {
            'name': 'System Dashboard',
            'port': 8888,
            'health_url': 'http://localhost:8888/health',
            'command': 'python extensions/core/extensions_server.py dashboard'
        },
        'teletext': {
            'name': 'Teletext Display',
            'port': 9002,
            'health_url': 'http://localhost:9002/health',
            'command': 'python extensions/core/extensions_server.py teletext'
        },
        'desktop': {
            'name': 'Retro Desktop',
            'port': 8892,
            'health_url': 'http://localhost:8892/health',
            'command': 'python extensions/core/extensions_server.py desktop'
        }
    }

    def __init__(self):
        self.port_manager = get_port_manager()
        self.root = Path(__file__).parent

    def check_health(self, server_key, port=None):
        """Check server health via HTTP endpoint, with optional port override."""
        server = self.SERVERS.get(server_key)
        if not server:
            return False, "Unknown server"

        health_url = server['health_url']
        if port:
            # If a custom port is used, we need to adjust the health check URL
            default_port = server['port']
            if str(default_port) in health_url:
                health_url = health_url.replace(str(default_port), str(port))

        try:
            response = requests.get(health_url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                return True, data.get('status', 'unknown')
            else:
                return False, f"HTTP {response.status_code}"
        except requests.RequestException as e:
            return False, str(e)

    def cleanup_server(self, server_key):
        """Cleanup a specific server"""
        server = self.SERVERS.get(server_key)
        if not server:
            print(f"❌ Unknown server: {server_key}")
            return False

        port = server['port']
        print(f"🧹 Cleaning up {server['name']} (port {port})...")

        if self.port_manager.cleanup_port(port):
            print(f"✓ {server['name']} cleaned up successfully")
            return True
        else:
            print(f"❌ Failed to cleanup {server['name']}")
            return False

    def cleanup_all(self):
        """Cleanup all servers"""
        print("\n🧹 Cleaning up all servers...\n")
        success = True
        for key in self.SERVERS:
            if not self.cleanup_server(key):
                success = False
        return success

    def status(self, server_key=None):
        """Show server status"""
        servers = [server_key] if server_key else list(self.SERVERS.keys())

        print(f"\n{'='*70}")
        print(f"{'uDOS Server Status':^70}")
        print(f"{'='*70}\n")

        for key in servers:
            server = self.SERVERS[key]
            port = server['port']

            # Check if port is in use
            port_in_use = not self.port_manager.is_port_available(port)

            # Check health
            healthy, status_msg = self.check_health(key)

            # Determine status
            if healthy:
                status_icon = "✅"
                status_text = "HEALTHY"
                status_color = "\033[32m"
            elif port_in_use:
                status_icon = "⚠️"
                status_text = "RUNNING (no health check)"
                status_color = "\033[33m"
            else:
                status_icon = "❌"
                status_text = "STOPPED"
                status_color = "\033[31m"

            print(f"{status_icon} {server['name']:<20} {status_color}{status_text:<30}\033[0m Port: {port}")
            if healthy:
                print(f"   └─ Health: {status_msg}")
            print()

        print(f"{'='*70}\n")

    def start_server(self, server_key, port=None, open_browser=False):
        """Start a specific server, with optional port override."""
        server = self.SERVERS.get(server_key)
        if not server:
            print(f"❌ Unknown server: {server_key}")
            return False

        # Use provided port or default from config
        start_port = port or server['port']

        # Check if already running
        if not self.port_manager.is_port_available(start_port):
            # Check health on the potentially custom port
            healthy, _ = self.check_health(server_key, port=start_port)
            if healthy:
                print(f"✓ {server['name']} is already running and healthy on port {start_port}")
                if open_browser:
                    self._open_browser_for_server(server_key, start_port)
                return True
            else:
                print(f"⚠️ Port {start_port} in use but server unhealthy, cleaning up...")
                # Cleanup should also be aware of the port
                self.port_manager.cleanup_port(start_port)

        # Start server
        print(f"🚀 Starting {server['name']} on port {start_port}...")

        # Construct command with potential port override
        command = server['command']
        env_vars = ""
        
        # Debug: Check command type
        if not isinstance(command, str):
            error_msg = f"❌ Invalid command configuration for {server['name']}\n"
            error_msg += f"   Expected: string\n"
            error_msg += f"   Got: {type(command).__name__}\n"
            error_msg += f"   Value: {command}\n"
            print(error_msg)
            return False

        if 'extensions_server.py' in command and start_port:
            # For extensions_server, add the port as an argument
            command = f"{command} --port {start_port}"
        elif 'PORT=' in command and start_port:
            # For API server, override the PORT env var
            env_vars = f"PORT={start_port} "
            command = command.split(' ', 1)[1]

        # Use absolute path for python from venv
        python_executable = f"{self.root.parent}/.venv/bin/python"
        command = command.replace("python", python_executable, 1)

        full_command = f"cd {self.root.parent} && source .venv/bin/activate && {env_vars}{command} > memory/logs/{server_key}_server.log 2>&1 &"

        os.system(full_command)

        # Wait and verify
        time.sleep(3) # Increased wait time
        healthy, status = self.check_health(server_key, port=start_port)

        if healthy:
            print(f"✅ {server['name']} started successfully")
            display_url = self._get_server_url(server_key, start_port)
            print(f"   URL: {display_url}")

            if open_browser:
                self._open_browser_for_server(server_key, start_port)
            return True
        else:
            print(f"❌ {server['name']} failed to start on port {start_port}: {status}")
            log_path = f"memory/logs/{server_key}_server.log"
            print(f"   Check log for details: {log_path}")
            return False

    def _get_server_url(self, server_key, port):
        """Gets the base URL for a server, using a specific port."""
        server = self.SERVERS[server_key]
        url = server['health_url'].replace('/health', '')
        # Replace default port with the one it's actually running on
        return url.replace(str(server['port']), str(port))

    def _open_browser_for_server(self, server_key, port):
        """Opens a browser for a given server and port."""
        import webbrowser
        url = self._get_server_url(server_key, port)
        print(f"🌐 Opening browser to {url}...")
        webbrowser.open(url)

    def start_all(self):
        """Start all servers"""
        print("\n🚀 Starting all uDOS servers...\n")

        # Start API first (other servers depend on it)
        if 'api' in self.SERVERS:
            self.start_server('api')
            time.sleep(1)

        # Start other servers
        for key in self.SERVERS:
            if key != 'api':
                self.start_server(key)
                time.sleep(1)

        # Show final status
        time.sleep(1)
        self.status()

    def restart_server(self, server_key):
        """Restart a specific server"""
        print(f"\n🔄 Restarting {self.SERVERS[server_key]['name']}...\n")
        self.cleanup_server(server_key)
        time.sleep(1)
        self.start_server(server_key)

    def restart_all(self):
        """Restart all servers"""
        print("\n🔄 Restarting all servers...\n")
        self.cleanup_all()
        time.sleep(2)
        self.start_all()


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='uDOS Server Manager - Bulletproof Server Control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server_manager.py status                 # Show all server status
  python server_manager.py start api              # Start API server
  python server_manager.py start-all              # Start all servers
  python server_manager.py restart terminal       # Restart terminal server
  python server_manager.py cleanup-all            # Stop all servers
  python server_manager.py health api             # Check API health

Available servers: api, terminal, dashboard, teletext, desktop
        """
    )

    parser.add_argument(
        'action',
        choices=['status', 'start', 'start-all', 'stop', 'stop-all', 'restart', 'restart-all', 'cleanup', 'cleanup-all', 'health'],
        help='Action to perform'
    )

    parser.add_argument(
        'server',
        nargs='?',
        choices=['api', 'terminal', 'dashboard', 'teletext', 'desktop'],
        help='Server to act on (required for single-server actions)'
    )

    args = parser.parse_args()

    manager = ServerManager()

    # Handle actions
    if args.action == 'status':
        manager.status(args.server)

    elif args.action == 'start':
        if not args.server:
            print("❌ Error: server name required for 'start' action")
            sys.exit(1)
        manager.start_server(args.server)

    elif args.action == 'start-all':
        manager.start_all()

    elif args.action in ['stop', 'cleanup']:
        if not args.server:
            print("❌ Error: server name required for 'stop' action")
            sys.exit(1)
        manager.cleanup_server(args.server)

    elif args.action in ['stop-all', 'cleanup-all']:
        manager.cleanup_all()

    elif args.action == 'restart':
        if not args.server:
            print("❌ Error: server name required for 'restart' action")
            sys.exit(1)
        manager.restart_server(args.server)

    elif args.action == 'restart-all':
        manager.restart_all()

    elif args.action == 'health':
        if not args.server:
            print("❌ Error: server name required for 'health' action")
            sys.exit(1)
        healthy, status = manager.check_health(args.server)
        server = manager.SERVERS[args.server]
        if healthy:
            print(f"✅ {server['name']} is HEALTHY")
            print(f"   Status: {status}")
        else:
            print(f"❌ {server['name']} is UNHEALTHY")
            print(f"   Error: {status}")
        sys.exit(0 if healthy else 1)


if __name__ == '__main__':
    main()
