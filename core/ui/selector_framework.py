"""
Selector Framework (v1.2.25)

Unified selector system for TUI components. Standardizes selection behavior
across menus, lists, file browsers, and all interactive panels.

Features:
- Consistent selection API across all components
- Keypad navigation integration (8 up, 2 down, 4 left, 6 right, 5 select)
- Mouse click support for items
- Visual feedback (highlighting, icons)
- Pagination for long lists
- Multi-select support
- Search/filter capability

Part of v1.2.25 Universal Input Device System - Week 4
"""

from typing import List, Optional, Callable, Any, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class SelectionMode(Enum):
    """Selection mode types."""
    SINGLE = "single"  # One item at a time
    MULTI = "multi"  # Multiple items
    NONE = "none"  # No selection (display only)
    TOGGLE = "toggle"  # Toggle on/off states


class NavigationMode(Enum):
    """Navigation movement modes."""
    LINEAR = "linear"  # Up/down only
    GRID = "grid"  # 2D navigation (up/down/left/right)
    TREE = "tree"  # Hierarchical (expand/collapse)
    WRAP = "wrap"  # Wrap around at edges


@dataclass
class SelectableItem:
    """
    Represents a selectable item in any selector.
    
    Attributes:
        id: Unique identifier
        label: Display text
        value: Associated value/data
        enabled: Can be selected
        selected: Currently selected
        icon: Optional icon/emoji
        metadata: Additional data
    """
    id: str
    label: str
    value: Any = None
    enabled: bool = True
    selected: bool = False
    icon: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.value is None:
            self.value = self.label
    
    def __str__(self):
        icon_str = f"{self.icon} " if self.icon else ""
        select_str = "*" if self.selected else " "
        enabled_str = "" if self.enabled else " (disabled)"
        return f"[{select_str}] {icon_str}{self.label}{enabled_str}"


@dataclass
class SelectorConfig:
    """Configuration for selector behavior."""
    mode: SelectionMode = SelectionMode.SINGLE
    navigation: NavigationMode = NavigationMode.LINEAR
    wrap_around: bool = True
    show_numbers: bool = True  # Show 1-9 numbers for items
    page_size: int = 10
    enable_search: bool = True
    enable_mouse: bool = True
    highlight_color: str = "cyan"
    select_icon: str = "*"
    disabled_icon: str = "x"


class SelectorFramework:
    """
    Unified selector framework for all TUI components.
    
    Provides consistent selection behavior across:
    - Menus (OK panel, config browser, etc.)
    - Lists (file browser, command history)
    - Grids (color picker, icon selector)
    - Trees (folder navigator, JSON viewer)
    """
    
    def __init__(self, config: Optional[SelectorConfig] = None):
        """
        Initialize selector framework.
        
        Args:
            config: Selector configuration
        """
        self.config = config or SelectorConfig()
        
        # Items and state
        self.items: List[SelectableItem] = []
        self.current_index: int = 0
        self.selected_indices: List[int] = []
        
        # Pagination
        self.page: int = 0
        self.page_size: int = self.config.page_size
        
        # Search/filter
        self.search_query: str = ""
        self.filtered_items: Optional[List[SelectableItem]] = None
        
        # Callbacks
        self.on_select: Optional[Callable[[SelectableItem], None]] = None
        self.on_navigate: Optional[Callable[[int], None]] = None
        self.on_confirm: Optional[Callable[[List[SelectableItem]], None]] = None
        
        # Mouse support
        self.mouse_enabled: bool = self.config.enable_mouse
    
    def set_items(self, items: List[SelectableItem]):
        """
        Set items to select from.
        
        Args:
            items: List of selectable items
        """
        self.items = items
        self.current_index = 0
        self.selected_indices = []
        self.filtered_items = None
        self.page = 0
    
    def add_item(self, item: SelectableItem):
        """Add a single item."""
        self.items.append(item)
    
    def remove_item(self, item_id: str) -> bool:
        """
        Remove item by ID.
        
        Args:
            item_id: Item identifier
            
        Returns:
            True if removed
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                if self.current_index >= len(self.items):
                    self.current_index = max(0, len(self.items) - 1)
                return True
        return False
    
    def get_item(self, item_id: str) -> Optional[SelectableItem]:
        """Get item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_current_item(self) -> Optional[SelectableItem]:
        """Get currently highlighted item."""
        items = self.get_visible_items()
        if 0 <= self.current_index < len(items):
            return items[self.current_index]
        return None
    
    def get_selected_items(self) -> List[SelectableItem]:
        """Get all selected items."""
        return [item for item in self.items if item.selected]
    
    def get_visible_items(self) -> List[SelectableItem]:
        """Get items for current page (after filtering)."""
        items = self.filtered_items if self.filtered_items else self.items
        start = self.page * self.page_size
        end = start + self.page_size
        return items[start:end]
    
    def navigate_up(self) -> bool:
        """
        Navigate to previous item.
        
        Returns:
            True if navigation occurred
        """
        items = self.get_visible_items()
        if not items:
            return False
        
        if self.current_index > 0:
            self.current_index -= 1
            if self.on_navigate:
                self.on_navigate(self.current_index)
            return True
        elif self.config.wrap_around:
            self.current_index = len(items) - 1
            if self.on_navigate:
                self.on_navigate(self.current_index)
            return True
        
        return False
    
    def navigate_down(self) -> bool:
        """
        Navigate to next item.
        
        Returns:
            True if navigation occurred
        """
        items = self.get_visible_items()
        if not items:
            return False
        
        if self.current_index < len(items) - 1:
            self.current_index += 1
            if self.on_navigate:
                self.on_navigate(self.current_index)
            return True
        elif self.config.wrap_around:
            self.current_index = 0
            if self.on_navigate:
                self.on_navigate(self.current_index)
            return True
        
        return False
    
    def navigate_to(self, index: int) -> bool:
        """
        Navigate to specific index.
        
        Args:
            index: Target index
            
        Returns:
            True if navigation occurred
        """
        items = self.get_visible_items()
        if 0 <= index < len(items):
            self.current_index = index
            if self.on_navigate:
                self.on_navigate(self.current_index)
            return True
        return False
    
    def select_current(self) -> bool:
        """
        Select currently highlighted item.
        
        Returns:
            True if selection occurred
        """
        current = self.get_current_item()
        if not current or not current.enabled:
            return False
        
        if self.config.mode == SelectionMode.SINGLE:
            # Deselect all others
            for item in self.items:
                item.selected = False
            current.selected = True
            self.selected_indices = [self.current_index]
        
        elif self.config.mode == SelectionMode.MULTI:
            # Toggle selection
            current.selected = not current.selected
            if current.selected and self.current_index not in self.selected_indices:
                self.selected_indices.append(self.current_index)
            elif not current.selected and self.current_index in self.selected_indices:
                self.selected_indices.remove(self.current_index)
        
        elif self.config.mode == SelectionMode.TOGGLE:
            # Simple toggle
            current.selected = not current.selected
        
        if self.on_select:
            self.on_select(current)
        
        return True
    
    def select_by_number(self, number: int) -> bool:
        """
        Select item by number (1-9).
        
        Args:
            number: Number key pressed (1-9)
            
        Returns:
            True if selection occurred
        """
        if not self.config.show_numbers:
            return False
        
        items = self.get_visible_items()
        index = number - 1  # Convert 1-based to 0-based
        
        if 0 <= index < len(items):
            self.navigate_to(index)
            return self.select_current()
        
        return False
    
    def confirm_selection(self) -> bool:
        """
        Confirm selection and trigger callback.
        
        Returns:
            True if confirmation occurred
        """
        selected = self.get_selected_items()
        if selected and self.on_confirm:
            self.on_confirm(selected)
            return True
        return False
    
    def filter_items(self, query: str):
        """
        Filter items by search query.
        
        Args:
            query: Search string
        """
        self.search_query = query.lower()
        
        if not query:
            self.filtered_items = None
        else:
            self.filtered_items = [
                item for item in self.items
                if query.lower() in item.label.lower()
                or (item.metadata and query.lower() in str(item.metadata).lower())
            ]
        
        self.current_index = 0
        self.page = 0
    
    def clear_filter(self):
        """Clear search filter."""
        self.search_query = ""
        self.filtered_items = None
    
    def next_page(self) -> bool:
        """
        Navigate to next page.
        
        Returns:
            True if page changed
        """
        items = self.filtered_items if self.filtered_items else self.items
        total_pages = (len(items) + self.page_size - 1) // self.page_size
        
        if self.page < total_pages - 1:
            self.page += 1
            self.current_index = 0
            return True
        return False
    
    def prev_page(self) -> bool:
        """
        Navigate to previous page.
        
        Returns:
            True if page changed
        """
        if self.page > 0:
            self.page -= 1
            self.current_index = 0
            return True
        return False
    
    def get_display_lines(self) -> List[str]:
        """
        Get formatted display lines for current view.
        
        Returns:
            List of formatted strings
        """
        lines = []
        items = self.get_visible_items()
        
        if not items:
            lines.append("  (no items)")
            return lines
        
        for i, item in enumerate(items):
            # Number prefix (1-9)
            number_str = f"{i + 1}. " if self.config.show_numbers and i < 9 else "   "
            
            # Selection indicator
            if i == self.current_index:
                indicator = "> "
            else:
                indicator = "  "
            
            # Icon
            icon_str = f"{item.icon} " if item.icon else ""
            
            # Selection checkbox
            if self.config.mode in (SelectionMode.MULTI, SelectionMode.TOGGLE):
                checkbox = f"[{self.config.select_icon}] " if item.selected else "[ ] "
            else:
                checkbox = ""
            
            # Disabled state
            if not item.enabled:
                style = "dim"
            elif i == self.current_index:
                style = "highlight"
            else:
                style = "normal"
            
            # Build line
            line = f"{indicator}{number_str}{checkbox}{icon_str}{item.label}"
            lines.append(line)
        
        # Pagination info
        if len(self.items) > self.page_size:
            items_total = len(self.filtered_items) if self.filtered_items else len(self.items)
            total_pages = (items_total + self.page_size - 1) // self.page_size
            lines.append("")
            lines.append(f"  Page {self.page + 1}/{total_pages} | {items_total} items")
        
        # Search info
        if self.search_query:
            lines.append(f"  Search: '{self.search_query}'")
        
        return lines
    
    def handle_keypad_input(self, key: str) -> bool:
        """
        Handle keypad navigation input.
        
        Args:
            key: Key pressed (0-9)
            
        Returns:
            True if handled
        """
        if key == "8":  # Up
            return self.navigate_up()
        elif key == "2":  # Down
            return self.navigate_down()
        elif key == "5":  # Select/Confirm
            return self.select_current()
        elif key == "4":  # Previous page
            return self.prev_page()
        elif key == "6":  # Next page
            return self.next_page()
        elif key in "123456789":  # Number selection
            return self.select_by_number(int(key))
        elif key == "0":  # Cancel/Back
            return False
        
        return False
    
    def clear_selection(self):
        """Clear all selections."""
        for item in self.items:
            item.selected = False
        self.selected_indices = []
    
    def select_all(self):
        """Select all enabled items (multi-select mode only)."""
        if self.config.mode != SelectionMode.MULTI:
            return
        
        for i, item in enumerate(self.items):
            if item.enabled:
                item.selected = True
                if i not in self.selected_indices:
                    self.selected_indices.append(i)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get selector statistics."""
        items = self.filtered_items if self.filtered_items else self.items
        return {
            'total_items': len(self.items),
            'visible_items': len(items),
            'selected_items': len(self.get_selected_items()),
            'current_index': self.current_index,
            'page': self.page,
            'search_active': bool(self.search_query)
        }
    
    def __repr__(self):
        return (f"SelectorFramework(mode={self.config.mode.value}, "
                f"items={len(self.items)}, "
                f"selected={len(self.get_selected_items())})")
