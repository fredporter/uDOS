"""
Mouse Handler for TUI System (v1.2.25)

Provides comprehensive mouse event handling for the uDOS TUI, including:
- Click detection (left, right, middle)
- Drag and drop support
- Scroll wheel events
- Mouse position tracking
- Coordinate translation for grid/viewport
- Component hit detection

Part of v1.2.25 Universal Input Device System
"""

from dataclasses import dataclass
from typing import Optional, Callable, Dict, List, Tuple, Any
from enum import Enum
import time


class MouseButton(Enum):
    """Mouse button types."""
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5


class MouseEventType(Enum):
    """Mouse event types."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    DRAG_START = "drag_start"
    DRAG_MOVE = "drag_move"
    DRAG_END = "drag_end"
    SCROLL = "scroll"
    HOVER = "hover"
    MOVE = "move"


@dataclass
class MousePosition:
    """Mouse position in terminal coordinates."""
    x: int  # Column (0-based)
    y: int  # Row (0-based)
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def distance_to(self, other: 'MousePosition') -> float:
        """Calculate distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class MouseEvent:
    """Mouse event information."""
    event_type: MouseEventType
    button: Optional[MouseButton]
    position: MousePosition
    timestamp: float
    modifiers: Dict[str, bool] = None  # shift, ctrl, alt
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = {'shift': False, 'ctrl': False, 'alt': False}
    
    def __str__(self):
        mods = [k for k, v in self.modifiers.items() if v]
        mod_str = f"+{'+'.join(mods)}" if mods else ""
        btn_str = self.button.name if self.button else "NONE"
        return f"{self.event_type.value}({btn_str}{mod_str}) @ {self.position}"


@dataclass
class ClickableRegion:
    """Defines a clickable region in the terminal."""
    name: str
    x1: int  # Top-left column
    y1: int  # Top-left row
    x2: int  # Bottom-right column
    y2: int  # Bottom-right row
    callback: Callable[[MouseEvent], None]
    enabled: bool = True
    
    def contains(self, pos: MousePosition) -> bool:
        """Check if position is within this region."""
        return (self.enabled and 
                self.x1 <= pos.x <= self.x2 and 
                self.y1 <= pos.y <= self.y2)
    
    def __str__(self):
        return f"{self.name} [{self.x1},{self.y1}-{self.x2},{self.y2}]"


class MouseHandler:
    """
    Handles mouse events for TUI system.
    
    Features:
    - Click/double-click detection
    - Drag and drop support
    - Scroll wheel events
    - Clickable region management
    - Mouse position tracking
    """
    
    def __init__(self, viewport=None, config=None):
        """
        Initialize mouse handler.
        
        Args:
            viewport: Viewport instance for coordinate translation
            config: Config instance for settings
        """
        self.viewport = viewport
        self.config = config
        
        # Mouse state
        self.current_position: Optional[MousePosition] = None
        self.last_click_time: float = 0
        self.last_click_position: Optional[MousePosition] = None
        self.double_click_threshold: float = 0.3  # seconds
        self.drag_threshold: int = 3  # pixels
        
        # Drag state
        self.is_dragging: bool = False
        self.drag_start_position: Optional[MousePosition] = None
        self.drag_button: Optional[MouseButton] = None
        
        # Clickable regions
        self.regions: List[ClickableRegion] = []
        
        # Event handlers
        self.event_handlers: Dict[MouseEventType, List[Callable]] = {
            event_type: [] for event_type in MouseEventType
        }
        
        # Mouse enabled state
        self.enabled: bool = True
        
        # Statistics
        self.stats = {
            'clicks': 0,
            'double_clicks': 0,
            'drags': 0,
            'scrolls': 0,
            'moves': 0
        }
    
    def enable(self):
        """Enable mouse input."""
        self.enabled = True
        return "Mouse input enabled"
    
    def disable(self):
        """Disable mouse input."""
        self.enabled = False
        return "Mouse input disabled"
    
    def is_enabled(self) -> bool:
        """Check if mouse input is enabled."""
        return self.enabled
    
    def add_region(self, region: ClickableRegion):
        """
        Add a clickable region.
        
        Args:
            region: ClickableRegion to add
        """
        self.regions.append(region)
    
    def remove_region(self, name: str) -> bool:
        """
        Remove a clickable region by name.
        
        Args:
            name: Region name
            
        Returns:
            True if removed, False if not found
        """
        original_len = len(self.regions)
        self.regions = [r for r in self.regions if r.name != name]
        return len(self.regions) < original_len
    
    def get_region(self, name: str) -> Optional[ClickableRegion]:
        """
        Get a clickable region by name.
        
        Args:
            name: Region name
            
        Returns:
            ClickableRegion or None
        """
        for region in self.regions:
            if region.name == name:
                return region
        return None
    
    def enable_region(self, name: str):
        """Enable a clickable region."""
        region = self.get_region(name)
        if region:
            region.enabled = True
    
    def disable_region(self, name: str):
        """Disable a clickable region."""
        region = self.get_region(name)
        if region:
            region.enabled = False
    
    def find_region_at(self, pos: MousePosition) -> Optional[ClickableRegion]:
        """
        Find clickable region at position.
        
        Args:
            pos: Mouse position
            
        Returns:
            ClickableRegion or None
        """
        # Check regions in reverse order (top-most first)
        for region in reversed(self.regions):
            if region.contains(pos):
                return region
        return None
    
    def register_handler(self, event_type: MouseEventType, handler: Callable):
        """
        Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Callback function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    def unregister_handler(self, event_type: MouseEventType, handler: Callable):
        """
        Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler: Callback function to remove
        """
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def parse_mouse_event(self, event_data: str) -> Optional[MouseEvent]:
        """
        Parse mouse event from terminal escape sequence.
        
        Format: ESC[<button;x;y(M|m)
        - M = button press
        - m = button release
        
        Args:
            event_data: Raw event string
            
        Returns:
            MouseEvent or None
        """
        if not self.enabled:
            return None
        
        try:
            # Example: "\x1b[<0;45;12M" (left button press at column 45, row 12)
            if not event_data.startswith('\x1b[<'):
                return None
            
            # Parse button, x, y
            parts = event_data[3:-1].split(';')
            if len(parts) < 3:
                return None
            
            button_code = int(parts[0])
            x = int(parts[1]) - 1  # Convert to 0-based
            y = int(parts[2]) - 1  # Convert to 0-based
            
            is_press = event_data[-1] == 'M'
            
            # Decode button
            button = self._decode_button(button_code)
            position = MousePosition(x, y)
            
            # Detect modifiers
            modifiers = {
                'shift': bool(button_code & 4),
                'alt': bool(button_code & 8),
                'ctrl': bool(button_code & 16)
            }
            
            # Determine event type
            event_type = self._determine_event_type(
                button, position, is_press, modifiers
            )
            
            event = MouseEvent(
                event_type=event_type,
                button=button,
                position=position,
                timestamp=time.time(),
                modifiers=modifiers
            )
            
            return event
            
        except (ValueError, IndexError):
            return None
    
    def _decode_button(self, code: int) -> Optional[MouseButton]:
        """Decode button from event code."""
        base_code = code & 3  # Lower 2 bits
        scroll = (code & 64) >> 6  # Bit 6
        
        if scroll:
            # Scroll events
            if base_code == 0:
                return MouseButton.SCROLL_UP
            elif base_code == 1:
                return MouseButton.SCROLL_DOWN
        else:
            # Button events
            if base_code == 0:
                return MouseButton.LEFT
            elif base_code == 1:
                return MouseButton.MIDDLE
            elif base_code == 2:
                return MouseButton.RIGHT
        
        return None
    
    def _determine_event_type(self, button: Optional[MouseButton], 
                             position: MousePosition, is_press: bool,
                             modifiers: Dict[str, bool]) -> MouseEventType:
        """Determine event type from button and state."""
        # Update current position
        self.current_position = position
        self.stats['moves'] += 1
        
        # Scroll events
        if button in (MouseButton.SCROLL_UP, MouseButton.SCROLL_DOWN):
            self.stats['scrolls'] += 1
            return MouseEventType.SCROLL
        
        # Button press events
        if is_press:
            # Check for double-click
            if self._is_double_click(position):
                self.stats['double_clicks'] += 1
                return MouseEventType.DOUBLE_CLICK
            
            # Start potential drag
            if button == MouseButton.LEFT:
                self.drag_start_position = position
                self.drag_button = button
            
            self.last_click_time = time.time()
            self.last_click_position = position
            self.stats['clicks'] += 1
            return MouseEventType.CLICK
        
        # Button release events
        else:
            # Check if we were dragging
            if self.is_dragging:
                self.is_dragging = False
                self.stats['drags'] += 1
                return MouseEventType.DRAG_END
            
            return MouseEventType.CLICK
        
        return MouseEventType.MOVE
    
    def _is_double_click(self, position: MousePosition) -> bool:
        """Check if this is a double-click."""
        if not self.last_click_position:
            return False
        
        time_diff = time.time() - self.last_click_time
        distance = position.distance_to(self.last_click_position)
        
        return (time_diff < self.double_click_threshold and 
                distance < self.drag_threshold)
    
    def process_event(self, event: MouseEvent) -> bool:
        """
        Process a mouse event.
        
        Args:
            event: MouseEvent to process
            
        Returns:
            True if event was handled
        """
        if not self.enabled:
            return False
        
        handled = False
        
        # Check for drag events
        if event.event_type == MouseEventType.CLICK and self.drag_start_position:
            distance = event.position.distance_to(self.drag_start_position)
            if distance >= self.drag_threshold and not self.is_dragging:
                # Start dragging
                self.is_dragging = True
                drag_event = MouseEvent(
                    event_type=MouseEventType.DRAG_START,
                    button=self.drag_button,
                    position=self.drag_start_position,
                    timestamp=event.timestamp,
                    modifiers=event.modifiers
                )
                self._dispatch_event(drag_event)
                handled = True
        
        if self.is_dragging and event.event_type == MouseEventType.MOVE:
            # Continue dragging
            drag_event = MouseEvent(
                event_type=MouseEventType.DRAG_MOVE,
                button=self.drag_button,
                position=event.position,
                timestamp=event.timestamp,
                modifiers=event.modifiers
            )
            self._dispatch_event(drag_event)
            handled = True
        
        # Check clickable regions
        region = self.find_region_at(event.position)
        if region and event.event_type == MouseEventType.CLICK:
            try:
                region.callback(event)
                handled = True
            except Exception as e:
                print(f"Warning: error in region callback: {e}")
        
        # Dispatch to registered handlers
        if not handled:
            self._dispatch_event(event)
        
        return handled
    
    def _dispatch_event(self, event: MouseEvent):
        """Dispatch event to registered handlers."""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Warning: error in event handler: {e}")
    
    def translate_to_grid(self, pos: MousePosition) -> Optional[str]:
        """
        Translate terminal position to grid TILE code.
        
        Args:
            pos: Mouse position in terminal coordinates
            
        Returns:
            TILE code or None
        """
        if not self.viewport:
            return None
        
        try:
            # This would use viewport's coordinate system
            # Placeholder implementation
            return None
        except Exception:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get mouse usage statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'enabled': self.enabled,
            'current_position': str(self.current_position) if self.current_position else "Unknown",
            'is_dragging': self.is_dragging,
            'regions': len(self.regions),
            'active_regions': len([r for r in self.regions if r.enabled]),
            'statistics': self.stats.copy()
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            'clicks': 0,
            'double_clicks': 0,
            'drags': 0,
            'scrolls': 0,
            'moves': 0
        }
    
    def clear_regions(self):
        """Clear all clickable regions."""
        self.regions.clear()
    
    def __repr__(self):
        return (f"MouseHandler(enabled={self.enabled}, "
                f"regions={len(self.regions)}, "
                f"position={self.current_position})")
