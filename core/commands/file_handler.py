"""
FILE Command Handler

Handles FILE command with workspace selection integration.
Provides interactive file browser with workspace picker.

Commands:
    FILE                    Open workspace picker then file browser
    FILE BROWSE             Same as FILE
    FILE LIST [path]        List files (quick command, no picker)
    FILE SHOW <file>        Display file content

Part of Phase 2 TUI Enhancement — Workspace selection integration
"""

from typing import List, Dict, Any
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.spatial_filesystem import UserRole


class FileHandler(BaseCommandHandler):
    """
    Handle FILE commands with workspace picker integration.
    
    Provides two modes:
    1. Interactive: FILE/FILE BROWSE opens WorkspacePicker → FileBrowser
    2. Quick: FILE LIST/SHOW for direct operations without picker
    """
    
    def __init__(self):
        super().__init__()
        self.user_role = self._get_user_role()
    
    def _get_user_role(self) -> UserRole:
        """Determine user role from state or config."""
        # Check dev mode or admin state
        # For now, default to USER (Phase 4 will add proper role detection)
        admin_mode = self.get_state("dev_mode", False) or self.get_state("admin_mode", False)
        return UserRole.ADMIN if admin_mode else UserRole.USER
    
    def handle(
        self, command: str, params: List[str], grid=None, parser=None
    ) -> Dict[str, Any]:
        """
        Route FILE subcommands.
        
        Args:
            command: "FILE"
            params: Subcommand and parameters
            grid: TUI Grid (optional)
            parser: SmartPrompt parser (optional)
        
        Returns:
            Dict with status, message, output
        """
        if not params or params[0].upper() in ("BROWSE", "PICK", "OPEN"):
            return self._handle_interactive_browse()
        
        subcommand = params[0].upper()
        sub_params = params[1:] if len(params) > 1 else []
        
        if subcommand == "LIST":
            return self._handle_list(sub_params)
        
        if subcommand == "SHOW":
            return self._handle_show(sub_params)
        
        if subcommand == "HELP":
            return self._handle_help()
        
        # Unknown subcommand - show help
        return {
            "status": "error",
            "message": f"Unknown FILE subcommand: {subcommand}",
            "suggestion": "Try: FILE, FILE LIST, FILE SHOW, FILE HELP",
        }
    
    def _handle_interactive_browse(self) -> Dict[str, Any]:
        """
        Launch interactive workspace picker followed by file browser.
        
        This is the main UX improvement from Phase 2: users pick a
        workspace first, then browse files within it.
        """
        try:
            from core.ui.workspace_selector import pick_workspace_then_file
            
            # Launch two-stage picker
            selected_file = pick_workspace_then_file(
                user_role=self.user_role,
                pick_directories=False,  # Files only
            )
            
            if selected_file is None:
                # User cancelled
                return {
                    "status": "cancelled",
                    "message": "File selection cancelled",
                }
            
            # File selected - show info
            output = "\n".join([
                OutputToolkit.banner("FILE BROWSER"),
                f"Selected: {selected_file}",
                f"Size: {selected_file.stat().st_size} bytes",
                "",
                "Use: EDIT <file> to open in editor",
                "     WORKSPACE read @ws/file to read content",
            ])
            
            return {
                "status": "success",
                "message": "File selected",
                "output": output,
                "data": {"path": str(selected_file)},
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"File browser error: {e}",
            }
    
    def _handle_list(self, params: List[str]) -> Dict[str, Any]:
        """
        Quick file listing without picker.
        
        Args:
            params: [workspace_path] (optional)
        """
        try:
            from core.services.spatial_filesystem import SpatialFilesystem
            
            fs = SpatialFilesystem(user_role=self.user_role)
            
            # Default to @sandbox if no path provided
            workspace_ref = params[0] if params else "@sandbox"
            
            # List files
            files = fs.list_files(workspace_ref)
            
            # Format output
            lines = [
                OutputToolkit.banner(f"FILES: {workspace_ref}"),
                "",
            ]
            
            if not files:
                lines.append("  (empty)")
            else:
                for file_info in files:
                    name = file_info.get("name", "?")
                    size = file_info.get("size", 0)
                    is_dir = file_info.get("is_dir", False)
                    icon = "📁" if is_dir else "📄"
                    size_str = f"{size:,} bytes" if not is_dir else ""
                    lines.append(f"  {icon} {name:<40} {size_str}")
            
            lines.append("")
            lines.append(f"Total: {len(files)} items")
            
            return {
                "status": "success",
                "message": f"Listed {len(files)} files",
                "output": "\n".join(lines),
                "data": {"files": files, "workspace": workspace_ref},
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"List error: {e}",
            }
    
    def _handle_show(self, params: List[str]) -> Dict[str, Any]:
        """
        Display file content without picker.
        
        Args:
            params: [workspace_ref] (required)
        """
        if not params:
            return {
                "status": "error",
                "message": "FILE SHOW requires a file path",
                "suggestion": "Usage: FILE SHOW @sandbox/readme.md",
            }
        
        try:
            from core.services.spatial_filesystem import SpatialFilesystem
            
            fs = SpatialFilesystem(user_role=self.user_role)
            workspace_ref = params[0]
            
            # Read file
            content = fs.read_file(workspace_ref)
            
            # Format output
            lines = [
                OutputToolkit.banner(f"FILE: {workspace_ref}"),
                "",
                content,
                "",
                f"─" * 70,
                f"Lines: {len(content.splitlines())} | Chars: {len(content)}",
            ]
            
            return {
                "status": "success",
                "message": "File displayed",
                "output": "\n".join(lines),
                "data": {"path": workspace_ref, "content": content},
            }
        
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"File not found: {params[0]}",
            }
        except PermissionError as e:
            return {
                "status": "error",
                "message": f"Access denied: {e}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Read error: {e}",
            }
    
    def _handle_help(self) -> Dict[str, Any]:
        """Show FILE command help."""
        help_text = """
╭─────────────────────────────────────────────────────────────────╮
│  FILE COMMAND HELP                                              │
╰─────────────────────────────────────────────────────────────────╯

Interactive Mode:
  FILE                       Open workspace picker → file browser
  FILE BROWSE                Same as FILE
  FILE PICK                  Same as FILE

Quick Commands:
  FILE LIST [@workspace]     List files (default: @sandbox)
  FILE SHOW @ws/file.md      Display file content
  FILE HELP                  Show this help

Workspaces:
  @sandbox     Vault sandbox (default)
  @bank        Vault bank
  @inbox       Inbox/Dropbox intake
  @public      Public/open/published
  @submissions Submission intake
  @private     Private explicit share
  @shared      Private shared
  @knowledge   Knowledge base (admin only)
  @wizard      Wizard config (admin only)
  @dev         Development (admin only)

Examples:
  FILE                              # Open picker
  FILE LIST @sandbox                # List sandbox files
  FILE LIST @bank                   # List bank files
  FILE LIST @public                 # List public files
  FILE SHOW @sandbox/readme.md      # Show file content

Related Commands:
  EDIT <file>                       # Open file in editor
  WORKSPACE list @sandbox           # Spatial filesystem commands
  BINDER open @sandbox/project      # Open binder project

Navigation in Picker:
  j/k or 2/8     Move down/up
  1-9            Quick select by number
  Enter or 5     Select item
  n/p or 0       Next/prev page
  q              Cancel/quit
  h/?            Help
""".strip()
        
        return {
            "status": "success",
            "message": "FILE command help",
            "output": help_text,
        }
