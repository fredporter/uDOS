"""
Selector Base Class - v1.2.25

Base class for all selection interfaces in uDOS.
Provides standardized number-based selection with consistent formatting.

Features:
    - Auto-numbering (1-9 for visible items, 0 for more/menu)
    - Visual indicators (emoji + number + label)
    - Pagination support
    - Consistent layout across all panels
    - Integration with keypad_handler

Usage:
    class MySelector(SelectorBase):
        def get_items(self):
            return ["Option 1", "Option 2", "Option 3"]
        
        def on_select(self, item, index):
            print(f"Selected: {item}")

Version: 1.0.0 (v1.2.25 - Universal Input Device System)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any, Dict
from core.input.keypad_handler import get_keypad_handler, KeypadMode


class SelectorBase(ABC):
    """Base class for all selection interfaces."""
    
    def __init__(self, 
                 title: str = "",
                 max_visible: int = 9,
                 show_numbers: bool = True,
                 show_emojis: bool = True):
        """Initialize selector.
        
        Args:
            title: Selector title/header
            max_visible: Maximum visible items (1-9)
            show_numbers: Show number prefixes
            show_emojis: Show emoji indicators
        """
        self.title = title
        self.max_visible = min(max_visible, 9)
        self.show_numbers = show_numbers
        self.show_emojis = show_emojis
        self.page_offset = 0
        self.selected_index = 0
        self.keypad = get_keypad_handler()
        
    @abstractmethod
    def get_items(self) -> List[Any]:
        """Get list of items to display.
        
        Returns:
            List of items (can be strings or objects)
        """
        pass
    
    @abstractmethod
    def on_select(self, item: Any, index: int) -> Any:
        """Handle item selection.
        
        Args:
            item: Selected item
            index: Item index in full list
            
        Returns:
            Result of selection (optional)
        """
        pass
    
    def get_item_label(self, item: Any) -> str:
        """Get display label for item.
        
        Override to customize item display.
        
        Args:
            item: Item to get label for
            
        Returns:
            Display string
        """
        return str(item)
    
    def get_item_emoji(self, item: Any, index: int) -> str:
        """Get emoji for item.
        
        Override to customize emojis per item.
        
        Args:
            item: Item to get emoji for
            index: Item index in full list
            
        Returns:
            Emoji character(s)
        """
        return "•"
    
    def get_visible_items(self) -> List[Any]:
        """Get currently visible items."""
        items = self.get_items()
        start = self.page_offset
        end = start + self.max_visible
        return items[start:end]
    
    def has_more_items(self) -> bool:
        """Check if there are more items to show."""
        items = self.get_items()
        return (self.page_offset + self.max_visible) < len(items)
    
    def has_previous_items(self) -> bool:
        """Check if there are previous items."""
        return self.page_offset > 0
    
    def next_page(self) -> bool:
        """Move to next page."""
        if self.has_more_items():
            self.page_offset += self.max_visible
            return True
        return False
    
    def previous_page(self) -> bool:
        """Move to previous page."""
        if self.has_previous_items():
            self.page_offset = max(0, self.page_offset - self.max_visible)
            return True
        return False
    
    def format_item(self, item: Any, number: int, absolute_index: int) -> str:
        """Format single item for display.
        
        Args:
            item: Item to format
            number: Display number (1-9)
            absolute_index: Absolute index in full list
            
        Returns:
            Formatted display string
        """
        label = self.get_item_label(item)
        emoji = self.get_item_emoji(item, absolute_index) if self.show_emojis else ""
        
        if self.show_numbers:
            if emoji:
                return f"{emoji} {number} {label}"
            else:
                return f"  {number} {label}"
        else:
            if emoji:
                return f"{emoji}   {label}"
            else:
                return f"    {label}"
    
    def format_more_indicator(self) -> str:
        """Format 'more items' indicator."""
        remaining = len(self.get_items()) - (self.page_offset + self.max_visible)
        return f"⋯ 0 More options ({remaining} items)"
    
    def render(self) -> str:
        """Render selector as formatted string.
        
        Returns:
            Complete selector display
        """
        lines = []
        
        # Title
        if self.title:
            lines.append(self.title)
            lines.append("=" * len(self.title))
            lines.append("")
        
        # Items
        visible = self.get_visible_items()
        for i, item in enumerate(visible, 1):
            absolute_index = self.page_offset + i - 1
            formatted = self.format_item(item, i, absolute_index)
            lines.append(formatted)
        
        # More indicator
        if self.has_more_items():
            lines.append("")
            lines.append(self.format_more_indicator())
        
        return "\n".join(lines)
    
    def handle_key(self, key: str) -> Optional[Any]:
        """Handle keypad input.
        
        Args:
            key: Key code (0-9)
            
        Returns:
            Result from selection or None
        """
        if key == '0':
            # Menu/more options
            if self.has_more_items():
                self.next_page()
                return "next_page"
            return "menu"
        
        if key in '123456789':
            # Select item
            number = int(key)
            visible = self.get_visible_items()
            
            if 1 <= number <= len(visible):
                index = number - 1
                absolute_index = self.page_offset + index
                item = visible[index]
                return self.on_select(item, absolute_index)
        
        return None
    
    def select(self, key: str) -> Tuple[bool, Optional[Any]]:
        """Select item by key press.
        
        Args:
            key: Key code (0-9)
            
        Returns:
            (success: bool, result: Any)
        """
        result = self.handle_key(key)
        
        if result == "next_page":
            return (True, None)
        elif result == "menu":
            return (False, "menu")
        elif result is not None:
            return (True, result)
        
        return (False, None)
    
    def get_key_hints(self) -> Dict[str, str]:
        """Get key hints for current selector.
        
        Returns:
            Dictionary of key->description
        """
        hints = {}
        
        visible = self.get_visible_items()
        if visible:
            if len(visible) == 1:
                hints["1"] = "Select"
            else:
                hints[f"1-{len(visible)}"] = "Select item"
        
        if self.has_more_items():
            hints["0"] = f"More ({len(self.get_items()) - self.page_offset - self.max_visible} more)"
        
        return hints


class MenuSelector(SelectorBase):
    """Simple menu selector with string items."""
    
    def __init__(self, 
                 items: List[str],
                 title: str = "Menu",
                 emojis: Optional[List[str]] = None):
        """Initialize menu selector.
        
        Args:
            items: List of menu item labels
            title: Menu title
            emojis: Optional emoji for each item
        """
        super().__init__(title=title)
        self.items = items
        self.emojis = emojis or []
        self.selection_result = None
    
    def get_items(self) -> List[str]:
        """Get menu items."""
        return self.items
    
    def on_select(self, item: str, index: int) -> str:
        """Handle menu selection."""
        self.selection_result = item
        return item
    
    def get_item_emoji(self, item: str, index: int) -> str:
        """Get emoji for menu item."""
        if self.emojis and index < len(self.emojis):
            return self.emojis[index]
        return "•"


class ListSelector(SelectorBase):
    """Generic list selector for any objects."""
    
    def __init__(self,
                 items: List[Any],
                 title: str = "",
                 label_func: Optional[callable] = None,
                 emoji_func: Optional[callable] = None):
        """Initialize list selector.
        
        Args:
            items: List of items to select from
            title: Selector title
            label_func: Function to get label from item
            emoji_func: Function to get emoji from item
        """
        super().__init__(title=title)
        self.items = items
        self.label_func = label_func or str
        self.emoji_func = emoji_func
    
    def get_items(self) -> List[Any]:
        """Get items list."""
        return self.items
    
    def on_select(self, item: Any, index: int) -> Any:
        """Handle item selection."""
        return item
    
    def get_item_label(self, item: Any) -> str:
        """Get item display label."""
        return self.label_func(item)
    
    def get_item_emoji(self, item: Any, index: int) -> str:
        """Get item emoji."""
        if self.emoji_func:
            return self.emoji_func(item, index)
        return "•"


# Example usage functions

def create_menu(items: List[str], 
                title: str = "Menu",
                emojis: Optional[List[str]] = None) -> MenuSelector:
    """Create a simple menu selector.
    
    Args:
        items: Menu item labels
        title: Menu title
        emojis: Optional emoji for each item
        
    Returns:
        MenuSelector instance
    """
    return MenuSelector(items, title, emojis)


def create_list_selector(items: List[Any],
                        title: str = "",
                        label_func: Optional[callable] = None,
                        emoji_func: Optional[callable] = None) -> ListSelector:
    """Create a list selector.
    
    Args:
        items: Items to select from
        title: Selector title
        label_func: Function to get label from item
        emoji_func: Function to get emoji from item
        
    Returns:
        ListSelector instance
    """
    return ListSelector(items, title, label_func, emoji_func)
