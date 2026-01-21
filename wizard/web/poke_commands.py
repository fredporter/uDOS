"""
POKE Online Commands v1.1.7

Command handlers for POKE Online extension.
Provides tunnel management, sharing, and group collaboration commands.

Commands:
- POKE TUNNEL OPEN <port> [options] - Open tunnel to local port
- POKE TUNNEL CLOSE <id> - Close specific tunnel
- POKE TUNNEL STATUS - Show all tunnel status
- POKE SHARE <file> [options] - Share file via tunnel
- POKE GROUP CREATE <name> - Create collaboration group
- POKE GROUP JOIN <code> - Join collaboration group

Author: uDOS Core Team
License: MIT
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta

# uDOS imports
from wizard.services.logging_manager import get_logger
from .tunnel_manager import create_tunnel_manager, TunnelInfo


class POKECommandHandler:
    """
    Command handler for POKE Online extension.

    Manages tunneling, sharing, and collaboration features.
    """

    def __init__(self):
        """Initialize POKE command handler."""
        self.logger = get_logger('extension-poke-online')
        self.tunnel_manager = create_tunnel_manager()

        # Command routing
        self.commands = {
            'tunnel': self._handle_tunnel,
            'share': self._handle_share,
            'group': self._handle_group,
            'start': self._handle_start,
            'stop': self._handle_stop,
            'restart': self._handle_restart,
            'list': self._handle_list_services,
            'status': self._handle_service_status,
            # Service shortcuts (default action: start)
            'dashboard': lambda args: self._handle_start(['dashboard'] + args),
            'desktop': lambda args: self._handle_start(['desktop'] + args),
            'terminal': lambda args: self._handle_start(['terminal'] + args),
            'teletext': lambda args: self._handle_start(['teletext'] + args)
        }

        # Subcommand routing
        self.tunnel_commands = {
            'open': self._tunnel_open,
            'close': self._tunnel_close,
            'status': self._tunnel_status,
            'list': self._tunnel_list
        }

        self.share_commands = {
            'file': self._share_file,
            'folder': self._share_folder,
            'stop': self._share_stop,
            'list': self._share_list
        }

        self.group_commands = {
            'create': self._group_create,
            'join': self._group_join,
            'leave': self._group_leave,
            'list': self._group_list,
            'invite': self._group_invite
        }

        self.logger.info("POKE command handler initialized")

    def handle_command(self, args: List[str]) -> Tuple[bool, str]:
        """
        Handle POKE command.

        Args:
            args: Command arguments (e.g., ['tunnel', 'open', '5000'])

        Returns:
            (success, message) tuple
        """
        if not args:
            return False, self._show_help()

        command = args[0].lower()

        if command not in self.commands:
            return False, f"Unknown POKE command: {command}\n\n{self._show_help()}"

        try:
            return self.commands[command](args[1:])
        except Exception as e:
            self.logger.error(f"POKE command error: {e}")
            return False, f"Error executing POKE {command}: {e}"

    def _show_help(self) -> str:
        """Show POKE command help."""
        return """POKE Cloud Extension v2.0

SERVICE SHORTCUTS (Core Extensions):
  POKE DASHBOARD [--stop]      - NES-themed system dashboard (port 5555)
  POKE DESKTOP [--stop]        - System desktop interface (port 8892)
  POKE TERMINAL [--stop]       - Web-based terminal (port 8889)
  POKE TELETEXT [--stop]       - Teletext interface (port 9002)

SERVICE MANAGEMENT:
  POKE START <service>         - Start a core extension service
  POKE STOP <service>          - Stop a running service
  POKE RESTART <service>       - Restart a service
  POKE LIST                    - List all services and status
  POKE STATUS                  - Show detailed service panel

TUNNEL COMMANDS:
  POKE TUNNEL OPEN <port> [--provider=ngrok] [--subdomain=name] [--expires=24]
    Open tunnel to local port

  POKE TUNNEL CLOSE <tunnel_id>
    Close specific tunnel

  POKE TUNNEL STATUS
    Show status of all tunnels

  POKE TUNNEL LIST
    List all tunnels (active and inactive)

SHARING COMMANDS:
  POKE SHARE FILE <path> [--port=8000] [--expires=24]
    Share a file via HTTP tunnel

  POKE SHARE FOLDER <path> [--port=8000] [--expires=24]
    Share a folder via HTTP tunnel

  POKE SHARE STOP <share_id>
    Stop sharing a file/folder

  POKE SHARE LIST
    List all active shares

GROUP COMMANDS:
  POKE GROUP CREATE <name> [--private] [--expires=168]
    Create collaboration group

  POKE GROUP JOIN <invite_code>
    Join collaboration group

  POKE GROUP LEAVE <group_id>
    Leave collaboration group

  POKE GROUP LIST
    List your groups

  POKE GROUP INVITE <group_id> <username>
    Invite user to group

EXAMPLES:
  POKE TUNNEL OPEN 5000
  POKE TUNNEL OPEN 3000 --provider=cloudflared --expires=2
  POKE SHARE FILE "knowledge/water/boiling.md"
  POKE GROUP CREATE "survival-team" --private
"""

    def _handle_tunnel(self, args: List[str]) -> Tuple[bool, str]:
        """Handle tunnel commands."""
        if not args:
            return False, "Usage: POKE TUNNEL <subcommand>\nSubcommands: open, close, status, list"

        subcommand = args[0].lower()

        if subcommand not in self.tunnel_commands:
            return False, f"Unknown tunnel command: {subcommand}"

        return self.tunnel_commands[subcommand](args[1:])

    def _tunnel_open(self, args: List[str]) -> Tuple[bool, str]:
        """Open a tunnel."""
        if not args:
            return False, "Usage: POKE TUNNEL OPEN <port> [--provider=ngrok] [--subdomain=name] [--expires=24]"

        # Parse port
        try:
            port = int(args[0])
        except ValueError:
            return False, f"Invalid port number: {args[0]}"

        # Parse options
        options = self._parse_options(args[1:])
        provider = options.get('provider')
        subdomain = options.get('subdomain')
        expires_hours = int(options.get('expires', 24))

        # Check if port is available
        if not self._is_port_available(port):
            return False, f"Port {port} is not available or not listening"

        # Check available providers
        available_providers = self.tunnel_manager.get_available_providers()
        if not available_providers:
            return False, "No tunnel providers available. Install ngrok or cloudflared."

        if provider and provider not in available_providers:
            return False, f"Provider {provider} not available. Available: {', '.join(available_providers)}"

        try:
            tunnel = self.tunnel_manager.create_tunnel(
                port=port,
                provider=provider,
                subdomain=subdomain,
                expires_hours=expires_hours
            )

            message = f"""✅ Tunnel opened successfully!

Tunnel ID: {tunnel.id}
Provider: {tunnel.provider}
Local Port: {tunnel.local_port}
Public URL: {tunnel.public_url}
Expires: {tunnel.expires_at.strftime('%Y-%m-%d %H:%M:%S') if tunnel.expires_at else 'Never'}

Share this URL to allow others to access your uDOS instance.
Use 'POKE TUNNEL CLOSE {tunnel.id}' to close the tunnel."""

            return True, message

        except Exception as e:
            return False, f"Failed to open tunnel: {e}"

    def _tunnel_close(self, args: List[str]) -> Tuple[bool, str]:
        """Close a tunnel."""
        if not args:
            # Show list of tunnels to close
            tunnels = self.tunnel_manager.list_tunnels()
            active_tunnels = [t for t in tunnels if t.status == 'active']

            if not active_tunnels:
                return False, "No active tunnels to close."

            tunnel_list = "\n".join([
                f"  {t.id} - {t.public_url} (port {t.local_port})"
                for t in active_tunnels
            ])

            return False, f"Usage: POKE TUNNEL CLOSE <tunnel_id>\n\nActive tunnels:\n{tunnel_list}"

        tunnel_id = args[0]

        if self.tunnel_manager.close_tunnel(tunnel_id):
            return True, f"✅ Tunnel {tunnel_id} closed successfully."
        else:
            return False, f"Failed to close tunnel {tunnel_id}. Check tunnel ID."

    def _tunnel_status(self, args: List[str]) -> Tuple[bool, str]:
        """Show tunnel status."""
        status = self.tunnel_manager.get_status()

        message = f"""📊 POKE Tunnel Status

Active Tunnels: {status['active_tunnels']}/{status['config']['max_concurrent_tunnels']}
Total Tunnels: {status['total_tunnels']}
Available Providers: {', '.join(status['available_providers']) or 'None'}
"""

        if status['tunnels']:
            message += "\n🔗 Active Tunnels:\n"
            for tunnel_data in status['tunnels']:
                tunnel = TunnelInfo(**tunnel_data)
                time_remaining = tunnel.time_remaining()
                remaining_str = f"{time_remaining}" if time_remaining else "No expiration"

                message += f"""
  ID: {tunnel.id}
  Provider: {tunnel.provider}
  URL: {tunnel.public_url}
  Local Port: {tunnel.local_port}
  Status: {tunnel.status}
  Created: {tunnel.created_at.strftime('%Y-%m-%d %H:%M:%S')}
  Expires: {remaining_str}
  Traffic: {tunnel.traffic_bytes} bytes
"""
        else:
            message += "\n(No active tunnels)"

        return True, message

    def _tunnel_list(self, args: List[str]) -> Tuple[bool, str]:
        """List all tunnels."""
        tunnels = self.tunnel_manager.list_tunnels()

        if not tunnels:
            return True, "No tunnels found."

        message = "📋 All Tunnels:\n"

        for tunnel in tunnels:
            status_emoji = "🟢" if tunnel.status == 'active' else "🔴"
            time_remaining = tunnel.time_remaining()
            remaining_str = f"{time_remaining}" if time_remaining else "Expired/Closed"

            message += f"""
{status_emoji} {tunnel.id}
  Provider: {tunnel.provider}
  URL: {tunnel.public_url}
  Port: {tunnel.local_port}
  Status: {tunnel.status}
  Created: {tunnel.created_at.strftime('%Y-%m-%d %H:%M')}
  Expires: {remaining_str}
"""

        return True, message

    def _handle_share(self, args: List[str]) -> Tuple[bool, str]:
        """Handle share commands."""
        if not args:
            return False, "Usage: POKE SHARE <subcommand>\nSubcommands: file, folder, stop, list"

        subcommand = args[0].lower()

        if subcommand not in self.share_commands:
            return False, f"Unknown share command: {subcommand}"

        return self.share_commands[subcommand](args[1:])

    def _share_file(self, args: List[str]) -> Tuple[bool, str]:
        """Share a file via HTTP."""
        if not args:
            return False, "Usage: POKE SHARE FILE <path> [--port=8000] [--expires=24]"

        file_path = args[0]

        # Validate file exists
        if not Path(file_path).exists():
            return False, f"File not found: {file_path}"

        if not Path(file_path).is_file():
            return False, f"Path is not a file: {file_path}"

        # Parse options
        options = self._parse_options(args[1:])
        port = int(options.get('port', 8000))
        expires_hours = int(options.get('expires', 24))

        # Start HTTP server for file
        try:
            server_port = self._start_file_server(file_path, port)

            # Create tunnel
            tunnel = self.tunnel_manager.create_tunnel(
                port=server_port,
                expires_hours=expires_hours
            )

            message = f"""📤 File shared successfully!

File: {file_path}
Share URL: {tunnel.public_url}
Tunnel ID: {tunnel.id}
Expires: {tunnel.expires_at.strftime('%Y-%m-%d %H:%M:%S') if tunnel.expires_at else 'Never'}

Anyone with this URL can download the file.
Use 'POKE SHARE STOP {tunnel.id}' to stop sharing."""

            return True, message

        except Exception as e:
            return False, f"Failed to share file: {e}"

    def _share_folder(self, args: List[str]) -> Tuple[bool, str]:
        """Share a folder via HTTP."""
        if not args:
            return False, "Usage: POKE SHARE FOLDER <path> [--port=8000] [--expires=24]"

        folder_path = args[0]

        # Validate folder exists
        if not Path(folder_path).exists():
            return False, f"Folder not found: {folder_path}"

        if not Path(folder_path).is_dir():
            return False, f"Path is not a folder: {folder_path}"

        # Parse options
        options = self._parse_options(args[1:])
        port = int(options.get('port', 8000))
        expires_hours = int(options.get('expires', 24))

        # Start HTTP server for folder
        try:
            server_port = self._start_folder_server(folder_path, port)

            # Create tunnel
            tunnel = self.tunnel_manager.create_tunnel(
                port=server_port,
                expires_hours=expires_hours
            )

            message = f"""📁 Folder shared successfully!

Folder: {folder_path}
Browse URL: {tunnel.public_url}
Tunnel ID: {tunnel.id}
Expires: {tunnel.expires_at.strftime('%Y-%m-%d %H:%M:%S') if tunnel.expires_at else 'Never'}

Anyone with this URL can browse and download files.
Use 'POKE SHARE STOP {tunnel.id}' to stop sharing."""

            return True, message

        except Exception as e:
            return False, f"Failed to share folder: {e}"

    def _share_stop(self, args: List[str]) -> Tuple[bool, str]:
        """Stop sharing."""
        if not args:
            return False, "Usage: POKE SHARE STOP <tunnel_id>"

        tunnel_id = args[0]

        if self.tunnel_manager.close_tunnel(tunnel_id):
            return True, f"✅ Stopped sharing tunnel {tunnel_id}."
        else:
            return False, f"Failed to stop sharing {tunnel_id}. Check tunnel ID."

    def _share_list(self, args: List[str]) -> Tuple[bool, str]:
        """List active shares."""
        tunnels = self.tunnel_manager.list_tunnels()
        active_shares = [t for t in tunnels if t.status == 'active']

        if not active_shares:
            return True, "No active shares."

        message = "📤 Active Shares:\n"

        for tunnel in active_shares:
            time_remaining = tunnel.time_remaining()
            remaining_str = f"{time_remaining}" if time_remaining else "No expiration"

            message += f"""
  🔗 {tunnel.id}
  URL: {tunnel.public_url}
  Port: {tunnel.local_port}
  Provider: {tunnel.provider}
  Expires: {remaining_str}
"""

        return True, message

    def _handle_group(self, args: List[str]) -> Tuple[bool, str]:
        """Handle group commands."""
        if not args:
            return False, "Usage: POKE GROUP <subcommand>\nSubcommands: create, join, leave, list, invite"

        subcommand = args[0].lower()

        if subcommand not in self.group_commands:
            return False, f"Unknown group command: {subcommand}"

        return self.group_commands[subcommand](args[1:])

    def _group_create(self, args: List[str]) -> Tuple[bool, str]:
        """Create a collaboration group."""
        # TODO: Implement group functionality
        return False, "Group functionality coming soon in future version."

    def _group_join(self, args: List[str]) -> Tuple[bool, str]:
        """Join a collaboration group."""
        # TODO: Implement group functionality
        return False, "Group functionality coming soon in future version."

    def _group_leave(self, args: List[str]) -> Tuple[bool, str]:
        """Leave a collaboration group."""
        # TODO: Implement group functionality
        return False, "Group functionality coming soon in future version."

    def _group_list(self, args: List[str]) -> Tuple[bool, str]:
        """List groups."""
        # TODO: Implement group functionality
        return False, "Group functionality coming soon in future version."

    def _group_invite(self, args: List[str]) -> Tuple[bool, str]:
        """Invite user to group."""
        # TODO: Implement group functionality
        return False, "Group functionality coming soon in future version."

    def _parse_options(self, args: List[str]) -> Dict[str, str]:
        """Parse command line options."""
        options = {}

        for arg in args:
            if arg.startswith('--'):
                if '=' in arg:
                    key, value = arg[2:].split('=', 1)
                    options[key] = value
                else:
                    options[arg[2:]] = 'true'

        return options

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available (has something listening)."""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            return result == 0  # 0 means connection successful (port is listening)

    def _start_file_server(self, file_path: str, preferred_port: int = 8000) -> int:
        """Start HTTP server for single file."""
        # TODO: Implement HTTP server for file sharing
        # This would use Python's http.server or a similar solution
        # For now, return the preferred port
        return preferred_port

    def _start_folder_server(self, folder_path: str, preferred_port: int = 8000) -> int:
        """Start HTTP server for folder browsing."""
        # TODO: Implement HTTP server for folder sharing
        # This would use Python's http.server with directory listing
        # For now, return the preferred port
        return preferred_port

    # ======================================================================
    # SERVICE MANAGEMENT (v2.0)
    # ======================================================================

    def _get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service configuration."""
        services = {
            'dashboard': {
                'port': 5555,
                'path': 'extensions/cloud/services/dashboard',
                'script': 'start.sh',
                'description': 'NES-themed system dashboard'
            },
            'desktop': {
                'port': 8892,
                'path': 'extensions/play/desktop',
                'script': 'start.sh',
                'description': 'System desktop interface'
            },
            'terminal': {
                'port': 8889,
                'path': 'extensions/web/terminal',
                'script': 'server.py',
                'description': 'Web-based terminal'
            },
            'teletext': {
                'port': 9002,
                'path': 'extensions/web/teletext',
                'script': 'server.py',
                'description': 'Teletext interface'
            },
            'web': {
                'port': 8080,
                'path': 'extensions/cloud/services/web',
                'script': 'server.py',
                'description': 'Web publishing tools'
            }
        }
        return services.get(service_name)

    def _handle_start(self, args: List[str]) -> Tuple[bool, str]:
        """Start a web service."""
        if not args:
            return False, "Usage: POKE START <service>\nServices: dashboard, desktop, terminal, teletext"

        service_name = args[0].lower()
        service_config = self._get_service_config(service_name)

        if not service_config:
            return False, f"Unknown service: {service_name}\nAvailable: dashboard, desktop, terminal, teletext"

        # Check if already running
        if self._is_port_available(service_config['port']):
            return True, f"✅ {service_name.title()} already running at http://localhost:{service_config['port']}"

        # Start service
        try:
            import subprocess
            import sys
            import webbrowser
            from pathlib import Path

            service_path = Path(service_config['path'])
            script_file = service_path / service_config['script']

            if not script_file.exists():
                return False, f"Service script not found: {script_file}"

            # Start server in background
            if service_config['script'].endswith('.sh'):
                subprocess.Popen(
                    ['bash', str(script_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=str(service_path)
                )
            else:
                subprocess.Popen(
                    [sys.executable, str(script_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=str(service_path)
                )

            # Wait for service to start
            import time
            time.sleep(2)

            # Open in browser
            webbrowser.open(f"http://localhost:{service_config['port']}")

            return True, f"""✅ {service_name.title()} started successfully!

🌐 URL: http://localhost:{service_config['port']}
📝 {service_config['description']}

Use: POKE STOP {service_name} to stop
Use: POKE TUNNEL OPEN {service_config['port']} to share publicly
"""

        except Exception as e:
            self.logger.error(f"Failed to start {service_name}: {e}")
            return False, f"Failed to start {service_name}: {e}"

    def _handle_stop(self, args: List[str]) -> Tuple[bool, str]:
        """Stop a web service."""
        if not args:
            return False, "Usage: POKE STOP <service>\\nServices: dashboard, desktop, terminal, teletext, web"

        service_name = args[0].lower()
        service_config = self._get_service_config(service_name)

        if not service_config:
            return False, f"Unknown service: {service_name}"

        # Find and kill process on port
        try:
            import subprocess
            result = subprocess.run(
                ['lsof', '-ti', f":{service_config['port']}"],
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                pid = result.stdout.strip().split('\\n')[0]
                subprocess.run(['kill', pid])
                return True, f"✅ {service_name.title()} stopped (port {service_config['port']})"
            else:
                return True, f"ℹ️  {service_name.title()} is not running"

        except Exception as e:
            self.logger.error(f"Failed to stop {service_name}: {e}")
            return False, f"Failed to stop {service_name}: {e}"

    def _handle_restart(self, args: List[str]) -> Tuple[bool, str]:
        """Restart a web service."""
        if not args:
            return False, "Usage: POKE RESTART <service>"

        service_name = args[0].lower()

        # Stop service
        success, message = self._handle_stop([service_name])
        if not success:
            return False, f"Failed to stop {service_name}: {message}"

        # Wait a moment
        import time
        time.sleep(1)

        # Start service
        return self._handle_start([service_name])

    def _handle_list_services(self, args: List[str]) -> Tuple[bool, str]:
        """List all services and their status."""
        services = ['dashboard', 'desktop', 'terminal', 'teletext', 'web']

        output = []
        output.append("🌐 POKE SERVICES\\n")
        output.append("Service       Port   Status      Description")
        output.append("─" * 70)

        for service in services:
            config = self._get_service_config(service)
            if config:
                is_running = self._is_port_available(config['port'])
                status = "🟢 Running" if is_running else "⚪ Stopped"
                line = f"{service.ljust(12)} {str(config['port']).ljust(6)} {status.ljust(11)} {config['description']}"
                output.append(line)

        output.append("")
        output.append("💡 Use: POKE <service> to start (e.g., POKE DASHBOARD)")
        output.append("💡 Use: POKE STOP <service> to stop")

        return True, "\\n".join(output)

    def _handle_service_status(self, args: List[str]) -> Tuple[bool, str]:
        """Show detailed service status."""
        services = ['dashboard', 'desktop', 'terminal', 'teletext', 'web']

        output = []
        output.append("╔" + "═" * 68 + "╗")
        output.append("║" + " POKE SERVICES STATUS".center(68) + "║")
        output.append("╠" + "═" * 68 + "╣")

        for service in services:
            config = self._get_service_config(service)
            if config:
                is_running = self._is_port_available(config['port'])

                if is_running:
                    status_icon = "🟢"
                    status_text = "RUNNING"
                    url = f"http://localhost:{config['port']}"
                else:
                    status_icon = "⚪"
                    status_text = "STOPPED"
                    url = "─"

                output.append(f"║ {status_icon} {service.upper().ljust(12)} {status_text.ljust(10)} :{str(config['port']).ljust(5)}" + " " * 30 + "║")
                output.append(f"║   {config['description'].ljust(65)} ║")
                if is_running:
                    output.append(f"║   URL: {url.ljust(61)} ║")
                output.append("║" + " " * 68 + "║")

        output.append("╚" + "═" * 68 + "╝")
        output.append("")
        output.append("💡 Quick Start: POKE DASHBOARD | POKE TELETEXT | POKE WEB")
        output.append("💡 Management: POKE STOP <service> | POKE RESTART <service>")

        return True, "\\n".join(output)


# Utility function for getting tunnel status (used by connection status checks)
def get_tunnel_status() -> Optional[str]:
    """Get active tunnel status for connection checks."""
    try:
        handler = POKECommandHandler()
        tunnels = handler.tunnel_manager.list_tunnels()
        active = [t for t in tunnels if t.status == 'active']
        if active:
            return f"{len(active)} tunnel(s) active"
        return None
    except:
        return None


# Main command entry point
def handle_poke_command(args: List[str]) -> Tuple[bool, str]:
    """
    Main entry point for POKE commands.

    Args:
        args: Command arguments

    Returns:
        (success, message) tuple
    """
    handler = POKECommandHandler()
    return handler.handle_command(args)
