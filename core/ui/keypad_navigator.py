"""
Keypad Navigation System (v1.2.13)

Provides numpad-style navigation for terminal interface:
- Movement: 2/4/6/8 (↓/←/→/↑)
- Select: 5 (confirm/enter)
- Edit: 7/9 (undo/redo)
- History: 1/3 (back/forward)
- Menu: 0 (toggle/context)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path
import json


class KeypadAction(Enum):
    """Keypad button actions"""
    MOVE_UP = "8"
    MOVE_DOWN = "2"
    MOVE_LEFT = "4"
    MOVE_RIGHT = "6"
    SELECT = "5"
    UNDO = "7"
    REDO = "9"
    HISTORY_BACK = "1"
    HISTORY_FORWARD = "3"
    MENU = "0"


@dataclass
class NavigationState:
    """Current navigation context"""
    mode: str = "command"  # command, menu, browser, pager
    cursor_pos: int = 0
    selection_index: int = 0
    history_pos: int = 0
    scroll_offset: int = 0
    active_workspace: Optional[str] = None
    undo_stack: List[str] = None
    redo_stack: List[str] = None
    
    def __post_init__(self):
        if self.undo_stack is None:
            self.undo_stack = []
        if self.redo_stack is None:
            self.redo_stack = []


class KeypadNavigator:
    """
    Handles keypad-style navigation across uDOS interface.
    
    Supports:
    - Command line editing with arrow keys
    - Menu navigation
    - File browser navigation
    - Paged output scrolling
    - Undo/redo for text input
    - Command history navigation
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.enabled = self.config.get('keypad_enabled', False)
        self.state = NavigationState()
        self.command_buffer = ""
        self.command_history: List[str] = []
        self.menu_items: List[str] = []
        self.browser_items: List[Path] = []
        
        # Action handlers
        self.handlers: Dict[str, Callable] = {
            KeypadAction.MOVE_UP.value: self._move_up,
            KeypadAction.MOVE_DOWN.value: self._move_down,
            KeypadAction.MOVE_LEFT.value: self._move_left,
            KeypadAction.MOVE_RIGHT.value: self._move_right,
            KeypadAction.SELECT.value: self._select,
            KeypadAction.UNDO.value: self._undo,
            KeypadAction.REDO.value: self._redo,
            KeypadAction.HISTORY_BACK.value: self._history_back,
            KeypadAction.HISTORY_FORWARD.value: self._history_forward,
            KeypadAction.MENU.value: self._toggle_menu,
        }
    
    def toggle(self) -> bool:
        """Toggle keypad navigation on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def handle_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Process keypad input.
        
        Args:
            key: Single character key press
            
        Returns:
            Action result dict or None if key not handled
        """
        if not self.enabled:
            return None
        
        # Check if it's a keypad action
        if key not in [action.value for action in KeypadAction]:
            return None
        
        handler = self.handlers.get(key)
        if handler:
            return handler()
        
        return None
    
    def set_mode(self, mode: str):
        """Change navigation mode (command, menu, browser, pager)"""
        self.state.mode = mode
        self.state.selection_index = 0
        self.state.scroll_offset = 0
    
    def set_command_buffer(self, text: str):
        """Update current command text"""
        # Save to undo stack
        if self.command_buffer != text:
            self.state.undo_stack.append(self.command_buffer)
            self.state.redo_stack.clear()  # Clear redo on new edit
        self.command_buffer = text
    
    def set_menu_items(self, items: List[str]):
        """Set items for menu navigation"""
        self.menu_items = items
        self.state.selection_index = 0
    
    def set_browser_items(self, items: List[Path]):
        """Set items for file browser navigation"""
        self.browser_items = items
        self.state.selection_index = 0
    
    # Movement handlers
    
    def _move_up(self) -> Dict[str, Any]:
        """Handle up arrow (8)"""
        if self.state.mode == "command":
            # In command mode, up = previous command in history
            return self._history_back()
        elif self.state.mode in ["menu", "browser", "pager"]:
            # In list modes, move selection up
            if self.state.selection_index > 0:
                self.state.selection_index -= 1
                # Scroll viewport if needed
                if self.state.selection_index < self.state.scroll_offset:
                    self.state.scroll_offset = self.state.selection_index
            return {
                "action": "move_up",
                "mode": self.state.mode,
                "index": self.state.selection_index,
                "scroll": self.state.scroll_offset
            }
        return {"action": "move_up", "handled": False}
    
    def _move_down(self) -> Dict[str, Any]:
        """Handle down arrow (2)"""
        if self.state.mode == "command":
            # In command mode, down = next command in history
            return self._history_forward()
        elif self.state.mode == "menu":
            max_index = len(self.menu_items) - 1
            if self.state.selection_index < max_index:
                self.state.selection_index += 1
                # Scroll viewport if needed (assume 10 visible items)
                if self.state.selection_index >= self.state.scroll_offset + 10:
                    self.state.scroll_offset += 1
            return {
                "action": "move_down",
                "mode": "menu",
                "index": self.state.selection_index,
                "scroll": self.state.scroll_offset
            }
        elif self.state.mode == "browser":
            max_index = len(self.browser_items) - 1
            if self.state.selection_index < max_index:
                self.state.selection_index += 1
                if self.state.selection_index >= self.state.scroll_offset + 10:
                    self.state.scroll_offset += 1
            return {
                "action": "move_down",
                "mode": "browser",
                "index": self.state.selection_index,
                "scroll": self.state.scroll_offset
            }
        return {"action": "move_down", "handled": False}
    
    def _move_left(self) -> Dict[str, Any]:
        """Handle left arrow (4)"""
        if self.state.mode == "command":
            # Move cursor left in command buffer
            if self.state.cursor_pos > 0:
                self.state.cursor_pos -= 1
            return {
                "action": "move_left",
                "cursor": self.state.cursor_pos
            }
        elif self.state.mode == "browser":
            # Go up one directory level
            return {
                "action": "browser_parent",
                "mode": "browser"
            }
        return {"action": "move_left", "handled": False}
    
    def _move_right(self) -> Dict[str, Any]:
        """Handle right arrow (6)"""
        if self.state.mode == "command":
            # Move cursor right in command buffer
            if self.state.cursor_pos < len(self.command_buffer):
                self.state.cursor_pos += 1
            return {
                "action": "move_right",
                "cursor": self.state.cursor_pos
            }
        elif self.state.mode == "browser":
            # Enter selected directory
            if 0 <= self.state.selection_index < len(self.browser_items):
                item = self.browser_items[self.state.selection_index]
                if item.is_dir():
                    return {
                        "action": "browser_enter",
                        "path": str(item)
                    }
        return {"action": "move_right", "handled": False}
    
    def _select(self) -> Dict[str, Any]:
        """Handle select/confirm (5)"""
        if self.state.mode == "command":
            # Execute current command
            return {
                "action": "execute",
                "command": self.command_buffer
            }
        elif self.state.mode == "menu":
            # Select menu item
            if 0 <= self.state.selection_index < len(self.menu_items):
                return {
                    "action": "menu_select",
                    "item": self.menu_items[self.state.selection_index],
                    "index": self.state.selection_index
                }
        elif self.state.mode == "browser":
            # Select file/directory
            if 0 <= self.state.selection_index < len(self.browser_items):
                return {
                    "action": "browser_select",
                    "path": str(self.browser_items[self.state.selection_index]),
                    "index": self.state.selection_index
                }
        return {"action": "select", "handled": False}
    
    def _undo(self) -> Dict[str, Any]:
        """Handle undo (7)"""
        if self.state.mode == "command" and self.state.undo_stack:
            # Undo text edit
            self.state.redo_stack.append(self.command_buffer)
            self.command_buffer = self.state.undo_stack.pop()
            self.state.cursor_pos = len(self.command_buffer)
            return {
                "action": "undo",
                "text": self.command_buffer,
                "cursor": self.state.cursor_pos
            }
        return {"action": "undo", "handled": False}
    
    def _redo(self) -> Dict[str, Any]:
        """Handle redo (9)"""
        if self.state.mode == "command" and self.state.redo_stack:
            # Redo text edit
            self.state.undo_stack.append(self.command_buffer)
            self.command_buffer = self.state.redo_stack.pop()
            self.state.cursor_pos = len(self.command_buffer)
            return {
                "action": "redo",
                "text": self.command_buffer,
                "cursor": self.state.cursor_pos
            }
        return {"action": "redo", "handled": False}
    
    def _history_back(self) -> Dict[str, Any]:
        """Handle history back (1)"""
        if self.state.mode == "command" and self.command_history:
            # Navigate to previous command
            if self.state.history_pos < len(self.command_history):
                self.state.history_pos += 1
                idx = len(self.command_history) - self.state.history_pos
                if idx >= 0:
                    self.command_buffer = self.command_history[idx]
                    self.state.cursor_pos = len(self.command_buffer)
            return {
                "action": "history_back",
                "text": self.command_buffer,
                "position": self.state.history_pos
            }
        return {"action": "history_back", "handled": False}
    
    def _history_forward(self) -> Dict[str, Any]:
        """Handle history forward (3)"""
        if self.state.mode == "command":
            # Navigate to next command (or clear if at end)
            if self.state.history_pos > 0:
                self.state.history_pos -= 1
                if self.state.history_pos == 0:
                    self.command_buffer = ""
                else:
                    idx = len(self.command_history) - self.state.history_pos
                    self.command_buffer = self.command_history[idx]
                self.state.cursor_pos = len(self.command_buffer)
            return {
                "action": "history_forward",
                "text": self.command_buffer,
                "position": self.state.history_pos
            }
        return {"action": "history_forward", "handled": False}
    
    def _toggle_menu(self) -> Dict[str, Any]:
        """Handle menu toggle (0)"""
        if self.state.mode == "command":
            # Open menu from command mode
            return {
                "action": "menu_open",
                "previous_mode": "command"
            }
        elif self.state.mode == "browser":
            # In browser mode, cycle workspaces instead of closing
            return {
                "action": "cycle_workspace",
                "mode": "browser"
            }
        else:
            # Close menu/browser and return to command mode
            return {
                "action": "menu_close",
                "mode": self.state.mode
            }
    
    def add_to_history(self, command: str):
        """Add command to history"""
        if command and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
            # Keep last 100 commands
            if len(self.command_history) > 100:
                self.command_history = self.command_history[-100:]
        self.state.history_pos = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current navigation status for display"""
        return {
            "enabled": self.enabled,
            "mode": self.state.mode,
            "cursor": self.state.cursor_pos,
            "selection": self.state.selection_index,
            "scroll": self.state.scroll_offset,
            "history_pos": self.state.history_pos,
            "undo_available": len(self.state.undo_stack) > 0,
            "redo_available": len(self.state.redo_stack) > 0
        }
    
    def save_state(self, path: Path):
        """Save navigation state to file"""
        state_data = {
            "command_history": self.command_history[-50:],  # Last 50 commands
            "enabled": self.enabled,
            "active_workspace": self.state.active_workspace
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self, path: Path):
        """Load navigation state from file"""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            self.command_history = data.get('command_history', [])
            self.enabled = data.get('enabled', False)
            self.state.active_workspace = data.get('active_workspace')
