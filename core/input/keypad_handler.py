"""
Universal KEYPAD Handler - v1.2.25

Unified 0-9 key mapping system for consistent navigation and selection
across all uDOS contexts (menus, panels, browsers, editors).

Key Mappings:
    8 - Up/Scroll Up
    2 - Down/Scroll Down
    4 - Left/Previous
    6 - Right/Next
    5 - OK/Select/Confirm
    7 - Redo
    9 - Undo
    1 - Yes
    3 - No
    0 - Menu/Options

Context Modes:
    - navigation: Browse/scroll through content
    - selection: Choose from numbered options
    - editing: Text input with keypad shortcuts
    - menu: Navigate menu systems

Integration:
    - Works with existing keypad_navigator.py (v1.2.15)
    - Extends device_manager.py input modes
    - Standardizes all selector interfaces

Version: 1.0.0 (v1.2.25 - Universal Input Device System)
"""

from enum import Enum
from typing import Callable, Dict, List, Optional, Any
import logging


class KeypadMode(Enum):
    """Keypad operation modes."""
    NAVIGATION = "navigation"  # Scroll/browse content
    SELECTION = "selection"    # Choose numbered options
    EDITING = "editing"        # Text input with shortcuts
    MENU = "menu"             # Menu navigation


class KeypadContext:
    """Context for keypad operations."""
    
    def __init__(self, 
                 mode: KeypadMode = KeypadMode.NAVIGATION,
                 items: Optional[List[Any]] = None,
                 current_index: int = 0,
                 max_visible: int = 9):
        """Initialize keypad context.
        
        Args:
            mode: Current operation mode
            items: List of selectable items
            current_index: Currently selected item index
            max_visible: Maximum visible items (1-9)
        """
        self.mode = mode
        self.items = items or []
        self.current_index = current_index
        self.max_visible = min(max_visible, 9)  # Max 9 for number keys
        self.page_offset = 0
        
    @property
    def visible_items(self) -> List[Any]:
        """Get currently visible items."""
        start = self.page_offset
        end = start + self.max_visible
        return self.items[start:end]
    
    @property
    def has_more(self) -> bool:
        """Check if there are more items to show."""
        return (self.page_offset + self.max_visible) < len(self.items)
    
    @property
    def has_previous(self) -> bool:
        """Check if there are previous items."""
        return self.page_offset > 0
    
    def next_page(self) -> bool:
        """Move to next page of items."""
        if self.has_more:
            self.page_offset += self.max_visible
            return True
        return False
    
    def previous_page(self) -> bool:
        """Move to previous page of items."""
        if self.has_previous:
            self.page_offset = max(0, self.page_offset - self.max_visible)
            return True
        return False


class KeypadHandler:
    """Universal keypad handler for all uDOS contexts."""
    
    # Key mapping constants
    KEY_UP = '8'
    KEY_DOWN = '2'
    KEY_LEFT = '4'
    KEY_RIGHT = '6'
    KEY_SELECT = '5'
    KEY_REDO = '7'
    KEY_UNDO = '9'
    KEY_YES = '1'
    KEY_NO = '3'
    KEY_MENU = '0'
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize keypad handler.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.context = KeypadContext()
        self.callbacks: Dict[str, Callable] = {}
        self.enabled = True
        
    def set_mode(self, mode: KeypadMode) -> None:
        """Set keypad operation mode.
        
        Args:
            mode: KeypadMode enum value
        """
        self.context.mode = mode
        self.logger.debug(f"Keypad mode set to: {mode.value}")
    
    def set_items(self, items: List[Any], current: int = 0) -> None:
        """Set items for selection mode.
        
        Args:
            items: List of selectable items
            current: Current selection index
        """
        self.context.items = items
        self.context.current_index = current
        self.context.page_offset = 0
        self.logger.debug(f"Keypad items set: {len(items)} items")
    
    def register_callback(self, key: str, callback: Callable) -> None:
        """Register callback for specific key.
        
        Args:
            key: Key code (0-9)
            callback: Function to call when key pressed
        """
        if key in '0123456789':
            self.callbacks[key] = callback
            self.logger.debug(f"Registered callback for key: {key}")
        else:
            raise ValueError(f"Invalid keypad key: {key}")
    
    def handle_key(self, key: str) -> Optional[Any]:
        """Handle keypad key press.
        
        Args:
            key: Key code (0-9)
            
        Returns:
            Result from handler or None
        """
        if not self.enabled:
            return None
        
        if key not in '0123456789':
            return None
        
        # Check for registered callback first
        if key in self.callbacks:
            return self.callbacks[key]()
        
        # Standard key handling based on mode
        if self.context.mode == KeypadMode.NAVIGATION:
            return self._handle_navigation(key)
        elif self.context.mode == KeypadMode.SELECTION:
            return self._handle_selection(key)
        elif self.context.mode == KeypadMode.EDITING:
            return self._handle_editing(key)
        elif self.context.mode == KeypadMode.MENU:
            return self._handle_menu(key)
        
        return None
    
    def _handle_navigation(self, key: str) -> Optional[str]:
        """Handle navigation mode keys.
        
        Args:
            key: Key code
            
        Returns:
            Navigation action string
        """
        actions = {
            self.KEY_UP: "scroll_up",
            self.KEY_DOWN: "scroll_down",
            self.KEY_LEFT: "previous",
            self.KEY_RIGHT: "next",
            self.KEY_SELECT: "select",
            self.KEY_REDO: "redo",
            self.KEY_UNDO: "undo",
            self.KEY_MENU: "menu"
        }
        
        action = actions.get(key)
        if action:
            self.logger.debug(f"Navigation: {action}")
        return action
    
    def _handle_selection(self, key: str) -> Optional[Any]:
        """Handle selection mode keys.
        
        Args:
            key: Key code (1-9 select item, 0 for more/menu)
            
        Returns:
            Selected item or action
        """
        if key == self.KEY_MENU:  # 0 key
            if self.context.has_more:
                self.context.next_page()
                return "next_page"
            return "menu"
        
        # Number keys 1-9 select items
        if key in '123456789':
            index = int(key) - 1
            visible = self.context.visible_items
            
            if 0 <= index < len(visible):
                selected = visible[index]
                self.logger.debug(f"Selected item {key}: {selected}")
                return selected
        
        # Fallback to navigation
        return self._handle_navigation(key)
    
    def _handle_editing(self, key: str) -> Optional[str]:
        """Handle editing mode keys.
        
        Args:
            key: Key code
            
        Returns:
            Editing action string
        """
        actions = {
            self.KEY_UP: "history_previous",
            self.KEY_DOWN: "history_next",
            self.KEY_LEFT: "cursor_left",
            self.KEY_RIGHT: "cursor_right",
            self.KEY_SELECT: "autocomplete",
            self.KEY_REDO: "redo",
            self.KEY_UNDO: "undo",
            self.KEY_YES: "accept",
            self.KEY_NO: "cancel",
            self.KEY_MENU: "options"
        }
        
        action = actions.get(key)
        if action:
            self.logger.debug(f"Editing: {action}")
        return action
    
    def _handle_menu(self, key: str) -> Optional[str]:
        """Handle menu mode keys.
        
        Args:
            key: Key code
            
        Returns:
            Menu action string
        """
        if key in '123456789':
            # Direct menu item selection
            index = int(key) - 1
            visible = self.context.visible_items
            
            if 0 <= index < len(visible):
                return f"menu_item_{key}"
        
        # Standard navigation
        return self._handle_navigation(key)
    
    def format_selector(self, items: List[str], 
                       emojis: Optional[List[str]] = None,
                       show_numbers: bool = True) -> List[str]:
        """Format items for numbered selection display.
        
        Args:
            items: List of item labels
            emojis: Optional emoji for each item
            show_numbers: Show number prefix
            
        Returns:
            List of formatted display strings
        """
        formatted = []
        visible = items[:self.context.max_visible]
        
        for i, item in enumerate(visible, 1):
            emoji = emojis[i-1] if emojis and len(emojis) >= i else "-"
            if show_numbers:
                formatted.append(f"{emoji} {i} {item}")
            else:
                formatted.append(f"{emoji}   {item}")
        
        # Add "more" indicator if needed
        if len(items) > self.context.max_visible:
            remaining = len(items) - self.context.max_visible
            formatted.append(f".. 0 More options ({remaining} items)")
        
        return formatted
    
    def get_key_hints(self) -> Dict[str, str]:
        """Get key hints for current mode.
        
        Returns:
            Dictionary of key->description
        """
        base_hints = {
            "8": "Up",
            "2": "Down",
            "4": "Left",
            "6": "Right",
            "5": "Select",
            "0": "Menu"
        }
        
        if self.context.mode == KeypadMode.SELECTION:
            base_hints = {
                "1-9": "Select item",
                "0": "More options" if self.context.has_more else "Menu"
            }
        elif self.context.mode == KeypadMode.EDITING:
            base_hints.update({
                "7": "Redo",
                "9": "Undo",
                "1": "Yes",
                "3": "No"
            })
        
        return base_hints
    
    def enable(self) -> None:
        """Enable keypad input."""
        self.enabled = True
        self.logger.debug("Keypad enabled")
    
    def disable(self) -> None:
        """Disable keypad input."""
        self.enabled = False
        self.logger.debug("Keypad disabled")
    
    def is_enabled(self) -> bool:
        """Check if keypad is enabled."""
        return self.enabled
    
    def reset(self) -> None:
        """Reset keypad state."""
        self.context = KeypadContext()
        self.callbacks.clear()
        self.logger.debug("Keypad reset")


# Singleton instance
_keypad_handler = None


def get_keypad_handler(logger: Optional[logging.Logger] = None) -> KeypadHandler:
    """Get singleton keypad handler instance.
    
    Args:
        logger: Optional logger instance
        
    Returns:
        KeypadHandler singleton
    """
    global _keypad_handler
    if _keypad_handler is None:
        _keypad_handler = KeypadHandler(logger)
    return _keypad_handler
