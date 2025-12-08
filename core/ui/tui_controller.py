"""
TUI Integration Module (v1.2.17)

Integrates keypad navigation, command prediction, pager, file browser,
and server panel into a unified terminal user interface.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from core.ui.keypad_navigator import KeypadNavigator
from core.ui.command_predictor import CommandPredictor
from core.ui.pager import Pager
from core.ui.file_browser import FileBrowser, Workspace
from core.ui.server_panel import get_server_panel
from core.ui.config_browser import get_config_browser
from core.ui.system_file_browser import get_system_file_browser
from core.ui.debug_panel import get_debug_panel
from core.ui.testing_interface import get_testing_interface
from core.ui.workflow_manager_panel import WorkflowManagerPanel
from core.ui.ok_assistant_panel import get_ok_assistant_panel


class TUIController:
    """
    Master controller for enhanced TUI system.
    
    Coordinates:
    - Keypad navigation
    - Command prediction
    - Paged output
    - File browsing
    - Server panel (v1.2.17)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.keypad = KeypadNavigator(self.config)
        self.predictor = CommandPredictor()
        self.pager = Pager(preserve_scroll=self.config.get('preserve_scroll', True))
        self.browser = FileBrowser()
        self.server_panel = get_server_panel()
        self.config_browser = get_config_browser()
        self.system_browser = get_system_file_browser()
        self.debug_panel = get_debug_panel()
        self.testing_interface = get_testing_interface()
        self.workflow_manager = WorkflowManagerPanel()
        self.ok_panel = get_ok_assistant_panel()
        
        # Current mode
        self.mode = "command"  # command, browser, pager, server_panel, config_panel, dev_browser, debug_panel, test_panel, workflow_panel, ok_panel
        
        # State persistence paths
        from core.utils.paths import PATHS
        self.state_dir = PATHS.MEMORY_SYSTEM_USER
        self.keypad_state_file = self.state_dir / "keypad_state.json"
        self.predictor_state_file = self.state_dir / "predictor_state.json"
        
        # Load saved states
        self._load_states()
    
    def _load_states(self):
        """Load component states from disk"""
        try:
            if self.keypad_state_file.exists():
                self.keypad.load_state(self.keypad_state_file)
            if self.predictor_state_file.exists():
                self.predictor.load_state(self.predictor_state_file)
        except Exception as e:
            print(f"Warning: Could not load TUI state: {e}")
    
    def save_states(self):
        """Save component states to disk"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.keypad.save_state(self.keypad_state_file)
            self.predictor.save_state(self.predictor_state_file)
        except Exception as e:
            print(f"Warning: Could not save TUI state: {e}")
    
    def handle_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Process key input through appropriate handler.
        
        Args:
            key: Key character
            
        Returns:
            Action dict or None
        """
        # Config panel mode - handle panel keys first
        if self.mode == "config_panel":
            if key.lower() == 'c' or key == '\x1b':  # C or ESC to close
                self.close_config_panel()
                return {"source": "config_panel", "action": "closed"}
            
            # Handle config panel navigation
            config_result = self._handle_config_panel_key(key)
            if config_result:
                return {"source": "config_panel", "action": config_result}
        
        # Server panel mode - handle panel keys first
        elif self.mode == "server_panel":
            panel_result = self.server_panel.handle_key(key)
            if panel_result == 'close':
                self.close_server_panel()
                return {"source": "server_panel", "action": "closed"}
            # If key handled by panel, return result
            if panel_result:
                return {"source": "server_panel", "action": panel_result}
            # Otherwise fall through to other handlers
        
        # Try keypad first if enabled
        if self.keypad.enabled:
            result = self.keypad.handle_key(key)
            if result:
                return self._process_keypad_action(result)
        
        # Pass to pager if in paging mode
        if self.mode == "pager":
            pager_result = self.pager.handle_key(key)
            if pager_result != "passthrough":
                return {"source": "pager", "action": pager_result}
        
        return None
    
    def _process_keypad_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process keypad action result"""
        action_type = action.get('action')
        
        if action_type == 'execute':
            # Execute command
            return {
                "source": "keypad",
                "action": "execute_command",
                "command": action.get('command')
            }
        elif action_type == 'menu_open':
            # Open file browser (0 key in command mode)
            return self.open_file_browser()
        elif action_type == 'menu_close':
            # Close browser and return to command mode (0 key in browser mode)
            return self.close_file_browser()
        elif action_type == 'cycle_workspace':
            # Cycle to next workspace (0 key in browser mode)
            if self.mode == "browser":
                workspace = self.browser.cycle_workspace()
                return {
                    "source": "browser",
                    "action": "cycle_workspace",
                    "workspace": workspace.value
                }
        elif action_type == 'move_up':
            # Navigate up in browser
            if self.mode == "browser":
                self.browser.navigate_up()
                return {"source": "browser", "action": "navigate", "direction": "up"}
        elif action_type == 'move_down':
            # Navigate down in browser
            if self.mode == "browser":
                self.browser.navigate_down()
                return {"source": "browser", "action": "navigate", "direction": "down"}
        elif action_type == 'browser_parent':
            # Go to parent directory (4 key in browser)
            if self.mode == "browser":
                self.browser.navigate_parent()
                return {"source": "browser", "action": "navigate", "direction": "parent"}
        elif action_type == 'browser_enter':
            # Enter selected directory (6 key in browser)
            if self.mode == "browser":
                path = self.browser.navigate_into()
                if path:
                    return {"source": "browser", "action": "enter_directory", "path": str(path)}
        elif action_type == 'browser_select':
            # File selected (5 key in browser) - show file operation menu
            if self.mode == "browser":
                selected = self.browser.select_current()
                if selected:
                    if selected.is_dir:
                        # Enter directory
                        path = self.browser.navigate_into()
                        return {"source": "browser", "action": "enter_directory", "path": str(path)}
                    else:
                        # Open file operation menu
                        return {
                            "source": "browser",
                            "action": "show_file_menu",
                            "file": {
                                "path": str(selected.path),
                                "name": selected.name,
                                "extension": selected.extension,
                                "size": selected.size
                            }
                        }
        
        return action
    
    def perform_file_operation(self, operation: str, file_entry = None, **kwargs) -> Dict[str, Any]:
        """
        Perform file operation (open, copy, move, delete, create).
        
        Args:
            operation: Operation type (open, copy, move, delete, create)
            file_entry: FileEntry to operate on
            **kwargs: Operation-specific arguments
            
        Returns:
            Result dict with action details
        """
        if operation == "open":
            return self.browser.open_file(file_entry)
        elif operation == "copy":
            dest = kwargs.get('destination')
            return self.browser.copy_file(file_entry, dest)
        elif operation == "move":
            dest = kwargs.get('destination')
            return self.browser.move_file(file_entry, dest)
        elif operation == "delete":
            confirm = kwargs.get('confirm', False)
            return self.browser.delete_file(file_entry, confirm)
        elif operation == "create":
            template = kwargs.get('template', 'script')
            filename = kwargs.get('filename')
            if not filename:
                return {"error": "Filename required"}
            return self.browser.create_from_template(template, filename)
        elif operation == "search":
            query = kwargs.get('query')
            if not query:
                return {"error": "Search query required"}
            result = self.browser.search(query)
            if result:
                return {
                    "action": "search",
                    "found": True,
                    "file": {
                        "path": str(result.path),
                        "name": result.name
                    }
                }
            else:
                return {
                    "action": "search",
                    "found": False,
                    "query": query
                }
        else:
            return {"error": f"Unknown operation: {operation}"}
        
        return action
    
    def get_predictions(self, partial: str, max_results: int = 5) -> List:
        """Get command predictions"""
        return self.predictor.predict(partial, max_results)
    
    def get_command_tokens(self, command: str) -> List:
        """Get syntax-highlighted tokens for command"""
        return self.predictor.tokenize(command)
    
    def set_pager_content(self, lines: List[str]):
        """Set pager content"""
        self.pager.set_content(lines)
        self.mode = "pager"
    
    def open_file_browser(self) -> Dict[str, Any]:
        """
        Open file browser (0 key action).
        
        Returns:
            Action dict for rendering browser
        """
        self.mode = "browser"
        self.keypad.set_mode("browser")
        return {
            "source": "tui",
            "action": "open_browser",
            "mode": "browser"
        }
    
    def close_file_browser(self) -> Dict[str, Any]:
        """
        Close file browser and return to command mode.
        
        Returns:
            Action dict for returning to command mode
        """
        self.mode = "command"
        self.keypad.set_mode("command")
        return {
            "source": "tui",
            "action": "close_browser",
            "mode": "command"
        }
    
    def render_current_view(self) -> str:
        """Render current TUI view"""
        if self.mode == "browser":
            # Use column layout if enabled (v1.2.16)
            if self.browser.state.column_mode:
                lines = self.browser.render_columns()
            else:
                lines = self.browser.render()
            return "\n".join(lines)
        elif self.mode == "pager":
            return self.pager.render()
        elif self.mode == "server_panel":
            return self.server_panel.render()
        else:
            # Command mode - show predictions if enabled
            return ""
    
    def toggle_browser_view(self) -> bool:
        """
        Toggle between single-column and 3-column browser view.
        
        Returns:
            New column_mode state
        """
        return self.browser.toggle_column_mode()
    
    def open_server_panel(self):
        """Open server monitoring panel"""
        self.mode = "server_panel"
        self.server_panel.refresh()
    
    def close_server_panel(self):
        """Close server panel and return to command mode"""
        self.mode = "command"
    
    def is_server_panel_open(self) -> bool:
        """Check if server panel is currently open"""
        return self.mode == "server_panel"
    
    def open_config_panel(self):
        """Open configuration browser panel"""
        self.mode = "config_panel"
    
    def close_config_panel(self):
        """Close config panel and return to command mode"""
        self.mode = "command"
    
    def is_config_panel_open(self) -> bool:
        """Check if config panel is currently open"""
        return self.mode == "config_panel"
    
    def open_dev_browser(self):
        """Open system file browser (DEV MODE)"""
        self.mode = "dev_browser"
        self.system_browser._load_workspace()
        self.system_browser._load_git_status()
    
    def close_dev_browser(self):
        """Close dev browser and return to command mode"""
        self.mode = "command"
    
    def is_dev_browser_open(self) -> bool:
        """Check if dev browser is currently open"""
        return self.mode == "dev_browser"
    
    def open_debug_panel(self):
        """Open debug panel for log viewing"""
        self.mode = "debug_panel"
        self.debug_panel.refresh_logs()
    
    def close_debug_panel(self):
        """Close debug panel and return to command mode"""
        self.mode = "command"
    
    def is_debug_panel_open(self) -> bool:
        """Check if debug panel is currently open"""
        return self.mode == "debug_panel"
    
    def open_test_panel(self):
        """Open testing interface panel"""
        self.mode = "test_panel"
    
    def close_test_panel(self):
        """Close test panel and return to command mode"""
        self.mode = "command"
    
    def is_test_panel_open(self) -> bool:
        """Check if test panel is currently open"""
        return self.mode == "test_panel"
    
    def _handle_config_panel_key(self, key: str) -> Optional[str]:
        """Handle key input when config panel is active"""
        # Navigation
        if key == '8':  # Up
            self.config_browser.move_selection(-1)
            return 'navigate_up'
        elif key == '2':  # Down
            self.config_browser.move_selection(1)
            return 'navigate_down'
        elif key == '4':  # Left (previous category)
            categories = list(self.config_browser.CATEGORIES.keys())
            current_idx = categories.index(self.config_browser.current_category)
            prev_idx = (current_idx - 1) % len(categories)
            self.config_browser.switch_category(categories[prev_idx])
            return 'category_prev'
        elif key == '6':  # Right (next category)
            categories = list(self.config_browser.CATEGORIES.keys())
            current_idx = categories.index(self.config_browser.current_category)
            next_idx = (current_idx + 1) % len(categories)
            self.config_browser.switch_category(categories[next_idx])
            return 'category_next'
        
        # Actions
        elif key.lower() == 'e':  # Edit
            self.config_browser.start_edit()
            return 'edit_start'
        elif key.lower() == 's':  # Save all
            result = self.config_browser.save_all()
            return 'save_all' if result['success'] else f"error: {result.get('error')}"
        elif key.lower() == 'r':  # Revert
            result = self.config_browser.revert_all()
            return 'revert_all' if result['success'] else f"error: {result.get('error')}"
        elif key == '\n' or key == '\r':  # Enter (save edit)
            if self.config_browser.editing_key:
                result = self.config_browser.save_edit()
                return 'edit_saved' if result['success'] else f"error: {result.get('error')}"
        elif key == '\x1b':  # ESC (cancel edit or close panel)
            if self.config_browser.editing_key:
                self.config_browser.cancel_edit()
                return 'edit_cancelled'
            else:
                self.close_config_panel()
                return 'close'
        
        # Edit buffer input
        elif self.config_browser.editing_key:
            self.config_browser.update_edit_buffer(key)
            return 'edit_input'
        
        return None
    
    def toggle_keypad(self) -> bool:
        """Toggle keypad navigation"""
        enabled = self.keypad.toggle()
        self.save_states()
        return enabled
    
    def add_to_history(self, command: str):
        """Add command to history for all components"""
        self.keypad.add_to_history(command)
        self.predictor.add_to_history(command)
        self.save_states()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive TUI status"""
        return {
            "mode": self.mode,
            "keypad": self.keypad.get_status(),
            "pager": self.pager.get_config(),
            "browser": self.browser.get_stats() if self.mode == "browser" else None,
            "server_panel": self.mode == "server_panel",
            "config_panel": self.mode == "config_panel",
            "dev_browser": self.mode == "dev_browser",
            "debug_panel": self.mode == "debug_panel",
            "test_panel": self.mode == "test_panel",
            "workflow_panel": self.mode == "workflow_panel"
        }
    
    # Workflow Panel Methods (v1.2.20)
    
    def open_workflow_panel(self):
        """Open workflow manager panel"""
        self.mode = "workflow_panel"
        return {"source": "tui", "action": "workflow_panel_opened"}
    
    def close_workflow_panel(self):
        """Close workflow manager panel"""
        self.mode = "command"
        return {"source": "tui", "action": "workflow_panel_closed"}
    
    def is_workflow_panel_open(self) -> bool:
        """Check if workflow panel is currently open"""
        return self.mode == "workflow_panel"
    
    # OK Assistant Panel Methods (v1.2.21)
    
    def open_ok_panel(self):
        """Open OK assistant panel (O-key)"""
        self.mode = "ok_panel"
        return {"source": "tui", "action": "ok_panel_opened"}
    
    def close_ok_panel(self):
        """Close OK assistant panel (ESC)"""
        self.mode = "command"
        return {"source": "tui", "action": "ok_panel_closed"}
    
    def is_ok_panel_open(self) -> bool:
        """Check if OK panel is currently open"""
        return self.mode == "ok_panel"
    
    def shutdown(self):
        """Clean shutdown - save all states"""
        self.save_states()


# Global TUI instance (initialized in uDOS_main.py)
_tui_instance: Optional[TUIController] = None


def get_tui() -> TUIController:
    """Get global TUI controller instance"""
    global _tui_instance
    if _tui_instance is None:
        _tui_instance = TUIController()
    return _tui_instance


def initialize_tui(config: Dict[str, Any] = None) -> TUIController:
    """Initialize TUI system"""
    global _tui_instance
    _tui_instance = TUIController(config)
    return _tui_instance
