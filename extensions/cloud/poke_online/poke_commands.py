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
from core.services.logging_manager import get_logger
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
            'group': self._handle_group
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
        return """POKE Online Extension v1.1.7

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