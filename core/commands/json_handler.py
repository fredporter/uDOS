"""JSON Command Handler

Interactive JSON viewer/editor commands.
Part of uDOS v1.2.22 self-healing system (Task 7).

Commands:
- JSON LOAD <file> - Load JSON file
- JSON VIEW - Show tree view
- JSON EDIT <value> - Edit cursor value
- JSON SAVE [file] - Save changes
- JSON DIFF - Show changes
- JSON UNDO - Undo last change
- JSON REDO - Redo last undone change
- JSON INFO - Show viewer info
- JSON EXPAND - Expand cursor node
- JSON COLLAPSE - Collapse cursor node
- JSON UP - Move cursor up
- JSON DOWN - Move cursor down
- JSON PATH - Show cursor path
"""

from core.commands.base_handler import BaseCommandHandler
from core.services.json_viewer import get_json_viewer


class JSONCommandHandler(BaseCommandHandler):
    """Handler for JSON viewer/editor commands."""
    
    def __init__(self, **kwargs):
        """Initialize JSON command handler.
        
        Args:
            **kwargs: Handler initialization kwargs (config, grid, parser, etc.)
        """
        super().__init__(**kwargs)
        self.viewer = get_json_viewer()
    
    def handle_command(self, cmd_parts):
        """Route JSON commands.
        
        Args:
            cmd_parts: Command parts (e.g., ['JSON', 'LOAD', 'file.json'])
            
        Returns:
            Command output string
        """
        if len(cmd_parts) < 2:
            return self._show_help()
        
        subcommand = cmd_parts[1].upper()
        params = cmd_parts[2:] if len(cmd_parts) > 2 else []
        
        if subcommand == 'LOAD':
            return self._handle_load(params)
        elif subcommand == 'VIEW':
            return self._handle_view(params)
        elif subcommand == 'EDIT':
            return self._handle_edit(params)
        elif subcommand == 'SAVE':
            return self._handle_save(params)
        elif subcommand == 'DIFF':
            return self._handle_diff()
        elif subcommand == 'UNDO':
            return self._handle_undo()
        elif subcommand == 'REDO':
            return self._handle_redo()
        elif subcommand == 'INFO':
            return self._handle_info()
        elif subcommand in ['EXPAND', 'TOGGLE']:
            return self._handle_expand()
        elif subcommand == 'COLLAPSE':
            return self._handle_collapse()
        elif subcommand == 'UP':
            return self._handle_up()
        elif subcommand == 'DOWN':
            return self._handle_down()
        elif subcommand == 'PATH':
            return self._handle_path()
        else:
            return f"❌ Unknown JSON command: {subcommand}\n\n{self._show_help()}"
    
    def _handle_load(self, params):
        """Handle JSON LOAD command.
        
        Args:
            params: Command parameters
            
        Returns:
            Command output
        """
        if not params:
            return "❌ Usage: JSON LOAD <filepath>"
        
        filepath = ' '.join(params)
        success, message = self.viewer.load_file(filepath)
        
        if success:
            # Show initial view
            return f"{message}\n\n{self._handle_view([])}"
        
        return message
    
    def _handle_view(self, params):
        """Handle JSON VIEW command.
        
        Args:
            params: Command parameters
            
        Returns:
            Command output
        """
        if not self.viewer.root:
            return "❌ No JSON loaded. Use: JSON LOAD <file>"
        
        # Get max lines from params or default to 20
        max_lines = 20
        if params:
            try:
                max_lines = int(params[0])
            except ValueError:
                pass
        
        # Get tree view
        lines = self.viewer.get_tree_view(max_lines)
        
        # Get info
        info = self.viewer.get_info()
        
        # Format output
        output = []
        output.append("╔════════════════════════════════════════════════════════════════╗")
        output.append(f"║  JSON Viewer: {info['file']:<48} ║")
        output.append("╚════════════════════════════════════════════════════════════════╝")
        output.append("")
        
        # Show tree
        for line in lines:
            output.append(line)
        
        output.append("")
        output.append("─" * 66)
        
        # Show status
        status = []
        if info['has_changes']:
            status.append("⚠️  Unsaved changes")
        if info['undo_available']:
            status.append("↶ Undo available")
        if info['redo_available']:
            status.append("↷ Redo available")
        
        if status:
            output.append("  " + " | ".join(status))
        else:
            output.append("  ✅ No changes")
        
        # Show navigation
        output.append("")
        output.append("Navigation: JSON UP/DOWN | JSON EXPAND/COLLAPSE")
        output.append("Commands: JSON EDIT <value> | JSON SAVE | JSON DIFF | JSON UNDO")
        
        return '\n'.join(output)
    
    def _handle_edit(self, params):
        """Handle JSON EDIT command.
        
        Args:
            params: Command parameters
            
        Returns:
            Command output
        """
        if not self.viewer.cursor:
            return "❌ No JSON loaded"
        
        if not params:
            return "❌ Usage: JSON EDIT <value>"
        
        new_value = ' '.join(params)
        success, message = self.viewer.edit_value(new_value)
        
        if success:
            # Show updated view
            return f"{message}\n\n{self._handle_view([])}"
        
        return message
    
    def _handle_save(self, params):
        """Handle JSON SAVE command.
        
        Args:
            params: Command parameters
            
        Returns:
            Command output
        """
        filepath = ' '.join(params) if params else None
        success, message = self.viewer.save(filepath)
        
        return message
    
    def _handle_diff(self):
        """Handle JSON DIFF command.
        
        Returns:
            Command output
        """
        diff_lines = self.viewer.get_diff()
        
        output = []
        output.append("╔════════════════════════════════════════════════════════════════╗")
        output.append("║  JSON Diff                                                     ║")
        output.append("╚════════════════════════════════════════════════════════════════╝")
        output.append("")
        
        for line in diff_lines:
            output.append(line)
        
        return '\n'.join(output)
    
    def _handle_undo(self):
        """Handle JSON UNDO command.
        
        Returns:
            Command output
        """
        success, message = self.viewer.undo()
        
        if success:
            return f"{message}\n\n{self._handle_view([])}"
        
        return message
    
    def _handle_redo(self):
        """Handle JSON REDO command.
        
        Returns:
            Command output
        """
        success, message = self.viewer.redo()
        
        if success:
            return f"{message}\n\n{self._handle_view([])}"
        
        return message
    
    def _handle_info(self):
        """Handle JSON INFO command.
        
        Returns:
            Command output
        """
        info = self.viewer.get_info()
        
        output = []
        output.append("╔════════════════════════════════════════════════════════════════╗")
        output.append("║  JSON Viewer Info                                              ║")
        output.append("╚════════════════════════════════════════════════════════════════╝")
        output.append("")
        output.append(f"File: {info['file']}")
        output.append(f"Cursor path: {info['cursor_path']}")
        output.append(f"Total nodes: {info['total_nodes']}")
        output.append(f"Has changes: {'Yes ⚠️' if info['has_changes'] else 'No ✅'}")
        output.append(f"Undo available: {'Yes ↶' if info['undo_available'] else 'No'}")
        output.append(f"Redo available: {'Yes ↷' if info['redo_available'] else 'No'}")
        
        return '\n'.join(output)
    
    def _handle_expand(self):
        """Handle JSON EXPAND command.
        
        Returns:
            Command output
        """
        if self.viewer.toggle_expand():
            return self._handle_view([])
        
        return "❌ Cannot expand current node (not a container)"
    
    def _handle_collapse(self):
        """Handle JSON COLLAPSE command.
        
        Returns:
            Command output
        """
        if self.viewer.cursor and self.viewer.cursor.expanded:
            self.viewer.toggle_expand()
            return self._handle_view([])
        
        return "❌ Node not expanded"
    
    def _handle_up(self):
        """Handle JSON UP command.
        
        Returns:
            Command output
        """
        if self.viewer.navigate_up():
            return self._handle_view([])
        
        return "❌ Already at top"
    
    def _handle_down(self):
        """Handle JSON DOWN command.
        
        Returns:
            Command output
        """
        if self.viewer.navigate_down():
            return self._handle_view([])
        
        return "❌ Already at bottom"
    
    def _handle_path(self):
        """Handle JSON PATH command.
        
        Returns:
            Command output
        """
        if not self.viewer.cursor:
            return "❌ No JSON loaded"
        
        path = self.viewer.cursor.get_path()
        return f"📍 Current path: {path}"
    
    def _show_help(self):
        """Show JSON command help.
        
        Returns:
            Help text
        """
        return """╔════════════════════════════════════════════════════════════════╗
║  JSON Viewer/Editor Commands                                   ║
╚════════════════════════════════════════════════════════════════╝

Loading & Viewing:
  JSON LOAD <file>         Load JSON file
  JSON VIEW [lines]        Show tree view (default 20 lines)
  JSON INFO                Show viewer information

Navigation:
  JSON UP                  Move cursor up
  JSON DOWN                Move cursor down
  JSON EXPAND              Expand cursor node
  JSON COLLAPSE            Collapse cursor node
  JSON PATH                Show cursor path

Editing:
  JSON EDIT <value>        Edit value at cursor
                           Examples:
                             JSON EDIT "new string"
                             JSON EDIT 42
                             JSON EDIT true
                             JSON EDIT null
  
  JSON UNDO                Undo last change
  JSON REDO                Redo last undone change

Saving:
  JSON SAVE                Save to current file
  JSON SAVE <file>         Save to new file
  JSON DIFF                Show changes from original

Examples:
  JSON LOAD memory/bank/user/user.json
  JSON VIEW 30
  JSON DOWN
  JSON DOWN
  JSON EXPAND
  JSON EDIT "new value"
  JSON DIFF
  JSON SAVE

Tree Symbols:
  ▶ - Cursor position
  📁/📦 - Object (collapsed/expanded)
  📄/📋 - Array (collapsed/expanded)
  📝 - String value
  🔢 - Number value
  ✓/✗ - Boolean value
  ∅ - Null value"""


def create_json_handler(**kwargs):
    """Factory function to create JSON handler.
    
    Args:
        **kwargs: Handler initialization kwargs
        
    Returns:
        JSONCommandHandler instance
    """
    return JSONCommandHandler(**kwargs)
