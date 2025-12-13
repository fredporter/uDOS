"""
Unit tests for KeypadHandler (v1.2.25).

Tests comprehensive keypad functionality including:
- Key registration and handling
- Mode switching (navigation/selection/editing/menu)
- Context management (items, pagination)
- Callback system
- Key hints and formatting
- Enable/disable state
- Integration patterns
"""

import pytest
import logging
from core.input.keypad_handler import (
    KeypadHandler,
    KeypadMode,
    KeypadContext,
    get_keypad_handler
)


class TestKeypadContext:
    """Test KeypadContext class."""
    
    def test_init_default(self):
        """Test default context initialization."""
        ctx = KeypadContext()
        assert ctx.mode == KeypadMode.NAVIGATION
        assert ctx.items == []
        assert ctx.current_index == 0
        assert ctx.max_visible == 9
        assert ctx.page_offset == 0
    
    def test_init_with_items(self):
        """Test context with items."""
        items = ["Item 1", "Item 2", "Item 3"]
        ctx = KeypadContext(items=items, current_index=1)
        assert ctx.items == items
        assert ctx.current_index == 1
    
    def test_max_visible_limit(self):
        """Test max_visible capped at 9."""
        ctx = KeypadContext(max_visible=15)
        assert ctx.max_visible == 9  # Capped at 9
    
    def test_visible_items_first_page(self):
        """Test getting visible items on first page."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        visible = ctx.visible_items
        assert len(visible) == 9
        assert visible == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    
    def test_visible_items_with_offset(self):
        """Test visible items with page offset."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        ctx.page_offset = 9
        visible = ctx.visible_items
        assert len(visible) == 9
        assert visible == [9, 10, 11, 12, 13, 14, 15, 16, 17]
    
    def test_has_more(self):
        """Test has_more property."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        assert ctx.has_more is True
        
        ctx.page_offset = 18  # Near end
        assert ctx.has_more is False
    
    def test_has_previous(self):
        """Test has_previous property."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        assert ctx.has_previous is False
        
        ctx.page_offset = 9
        assert ctx.has_previous is True
    
    def test_next_page(self):
        """Test next page navigation."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        
        assert ctx.page_offset == 0
        result = ctx.next_page()
        assert result is True
        assert ctx.page_offset == 9
    
    def test_next_page_at_end(self):
        """Test next page at end of items."""
        items = list(range(5))
        ctx = KeypadContext(items=items)
        
        result = ctx.next_page()
        assert result is False
        assert ctx.page_offset == 0
    
    def test_previous_page(self):
        """Test previous page navigation."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        ctx.page_offset = 9
        
        result = ctx.previous_page()
        assert result is True
        assert ctx.page_offset == 0
    
    def test_previous_page_at_start(self):
        """Test previous page at start."""
        items = list(range(20))
        ctx = KeypadContext(items=items)
        
        result = ctx.previous_page()
        assert result is False
        assert ctx.page_offset == 0


class TestKeypadHandler:
    """Test KeypadHandler class."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
    
    def test_init(self):
        """Test handler initialization."""
        handler = KeypadHandler()
        assert handler.enabled is True
        assert handler.context.mode == KeypadMode.NAVIGATION
        assert handler.callbacks == {}
    
    def test_key_constants(self):
        """Test key constant definitions."""
        assert KeypadHandler.KEY_UP == '8'
        assert KeypadHandler.KEY_DOWN == '2'
        assert KeypadHandler.KEY_LEFT == '4'
        assert KeypadHandler.KEY_RIGHT == '6'
        assert KeypadHandler.KEY_SELECT == '5'
        assert KeypadHandler.KEY_REDO == '7'
        assert KeypadHandler.KEY_UNDO == '9'
        assert KeypadHandler.KEY_YES == '1'
        assert KeypadHandler.KEY_NO == '3'
        assert KeypadHandler.KEY_MENU == '0'
    
    def test_set_mode(self):
        """Test setting keypad mode."""
        self.handler.set_mode(KeypadMode.SELECTION)
        assert self.handler.context.mode == KeypadMode.SELECTION
        
        self.handler.set_mode(KeypadMode.EDITING)
        assert self.handler.context.mode == KeypadMode.EDITING
    
    def test_set_items(self):
        """Test setting selectable items."""
        items = ["Option 1", "Option 2", "Option 3"]
        self.handler.set_items(items)
        
        assert self.handler.context.items == items
        assert self.handler.context.current_index == 0
        assert self.handler.context.page_offset == 0
    
    def test_set_items_with_current(self):
        """Test setting items with current index."""
        items = ["A", "B", "C"]
        self.handler.set_items(items, current=2)
        
        assert self.handler.context.current_index == 2
    
    def test_register_callback(self):
        """Test registering key callback."""
        called = {'count': 0}
        
        def callback():
            called['count'] += 1
            return "callback_result"
        
        self.handler.register_callback('5', callback)
        assert '5' in self.handler.callbacks
    
    def test_register_callback_invalid_key(self):
        """Test registering callback with invalid key."""
        with pytest.raises(ValueError):
            self.handler.register_callback('a', lambda: None)
    
    def test_handle_key_with_callback(self):
        """Test handling key with registered callback."""
        result_holder = {'result': None}
        
        def callback():
            result_holder['result'] = "custom_action"
            return "custom_action"
        
        self.handler.register_callback('5', callback)
        result = self.handler.handle_key('5')
        
        assert result == "custom_action"
        assert result_holder['result'] == "custom_action"
    
    def test_handle_key_invalid(self):
        """Test handling invalid key."""
        result = self.handler.handle_key('x')
        assert result is None
    
    def test_handle_key_disabled(self):
        """Test handling key when disabled."""
        self.handler.disable()
        result = self.handler.handle_key('5')
        assert result is None


class TestNavigationMode:
    """Test navigation mode handling."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
        self.handler.set_mode(KeypadMode.NAVIGATION)
    
    def test_key_up(self):
        """Test up key in navigation mode."""
        result = self.handler.handle_key('8')
        assert result == "scroll_up"
    
    def test_key_down(self):
        """Test down key in navigation mode."""
        result = self.handler.handle_key('2')
        assert result == "scroll_down"
    
    def test_key_left(self):
        """Test left key in navigation mode."""
        result = self.handler.handle_key('4')
        assert result == "previous"
    
    def test_key_right(self):
        """Test right key in navigation mode."""
        result = self.handler.handle_key('6')
        assert result == "next"
    
    def test_key_select(self):
        """Test select key in navigation mode."""
        result = self.handler.handle_key('5')
        assert result == "select"
    
    def test_key_redo(self):
        """Test redo key in navigation mode."""
        result = self.handler.handle_key('7')
        assert result == "redo"
    
    def test_key_undo(self):
        """Test undo key in navigation mode."""
        result = self.handler.handle_key('9')
        assert result == "undo"
    
    def test_key_menu(self):
        """Test menu key in navigation mode."""
        result = self.handler.handle_key('0')
        assert result == "menu"


class TestSelectionMode:
    """Test selection mode handling."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
        self.handler.set_mode(KeypadMode.SELECTION)
    
    def test_select_item_1(self):
        """Test selecting first item."""
        items = ["Option 1", "Option 2", "Option 3"]
        self.handler.set_items(items)
        
        result = self.handler.handle_key('1')
        assert result == "Option 1"
    
    def test_select_item_5(self):
        """Test selecting fifth item."""
        items = [f"Item {i}" for i in range(1, 10)]
        self.handler.set_items(items)
        
        result = self.handler.handle_key('5')
        assert result == "Item 5"
    
    def test_select_item_out_of_range(self):
        """Test selecting item beyond available."""
        items = ["Only 1", "Only 2"]
        self.handler.set_items(items)
        
        result = self.handler.handle_key('5')
        # Falls back to navigation mode (select action)
        assert result == "select"
    
    def test_key_menu_with_more_pages(self):
        """Test menu key when more pages available."""
        items = [f"Item {i}" for i in range(20)]
        self.handler.set_items(items)
        
        result = self.handler.handle_key('0')
        assert result == "next_page"
        assert self.handler.context.page_offset == 9
    
    def test_key_menu_without_more_pages(self):
        """Test menu key when no more pages."""
        items = ["Item 1", "Item 2"]
        self.handler.set_items(items)
        
        result = self.handler.handle_key('0')
        assert result == "menu"
    
    def test_pagination_selection(self):
        """Test selection across pages."""
        items = [f"Item {i}" for i in range(20)]
        self.handler.set_items(items)
        
        # First page: items 0-8
        result = self.handler.handle_key('1')
        assert result == "Item 0"
        
        # Go to next page
        self.handler.handle_key('0')
        
        # Second page: items 9-17
        result = self.handler.handle_key('1')
        assert result == "Item 9"


class TestEditingMode:
    """Test editing mode handling."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
        self.handler.set_mode(KeypadMode.EDITING)
    
    def test_key_up_history(self):
        """Test up key for history in editing mode."""
        result = self.handler.handle_key('8')
        assert result == "history_previous"
    
    def test_key_down_history(self):
        """Test down key for history in editing mode."""
        result = self.handler.handle_key('2')
        assert result == "history_next"
    
    def test_key_left_cursor(self):
        """Test left key for cursor in editing mode."""
        result = self.handler.handle_key('4')
        assert result == "cursor_left"
    
    def test_key_right_cursor(self):
        """Test right key for cursor in editing mode."""
        result = self.handler.handle_key('6')
        assert result == "cursor_right"
    
    def test_key_select_autocomplete(self):
        """Test select key for autocomplete in editing mode."""
        result = self.handler.handle_key('5')
        assert result == "autocomplete"
    
    def test_key_redo(self):
        """Test redo in editing mode."""
        result = self.handler.handle_key('7')
        assert result == "redo"
    
    def test_key_undo(self):
        """Test undo in editing mode."""
        result = self.handler.handle_key('9')
        assert result == "undo"
    
    def test_key_yes(self):
        """Test yes key in editing mode."""
        result = self.handler.handle_key('1')
        assert result == "accept"
    
    def test_key_no(self):
        """Test no key in editing mode."""
        result = self.handler.handle_key('3')
        assert result == "cancel"
    
    def test_key_menu_options(self):
        """Test menu key for options in editing mode."""
        result = self.handler.handle_key('0')
        assert result == "options"


class TestMenuMode:
    """Test menu mode handling."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
        self.handler.set_mode(KeypadMode.MENU)
    
    def test_menu_item_selection(self):
        """Test menu item selection."""
        items = ["File", "Edit", "View", "Help"]
        self.handler.set_items(items)
        
        result = self.handler.handle_key('2')
        assert result == "menu_item_2"
    
    def test_menu_navigation_fallback(self):
        """Test menu mode falls back to navigation."""
        result = self.handler.handle_key('0')
        assert result == "menu"


class TestFormatting:
    """Test display formatting methods."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
    
    def test_format_selector_simple(self):
        """Test basic selector formatting."""
        items = ["Option 1", "Option 2", "Option 3"]
        formatted = self.handler.format_selector(items)
        
        assert len(formatted) == 3
        assert "1 Option 1" in formatted[0]
        assert "2 Option 2" in formatted[1]
        assert "3 Option 3" in formatted[2]
    
    def test_format_selector_with_emojis(self):
        """Test selector with emojis."""
        items = ["Save", "Load", "Quit"]
        emojis = ["💾", "📂", "🚪"]
        formatted = self.handler.format_selector(items, emojis=emojis)
        
        assert "💾" in formatted[0]
        assert "📂" in formatted[1]
        assert "🚪" in formatted[2]
    
    def test_format_selector_no_numbers(self):
        """Test selector without numbers."""
        items = ["Option A", "Option B"]
        formatted = self.handler.format_selector(items, show_numbers=False)
        
        assert "1" not in formatted[0]
        assert "2" not in formatted[1]
        assert "Option A" in formatted[0]
    
    def test_format_selector_with_more(self):
        """Test selector with more items indicator."""
        items = [f"Item {i}" for i in range(15)]
        formatted = self.handler.format_selector(items)
        
        # Should show 9 items + more indicator
        assert len(formatted) == 10
        assert "More options" in formatted[-1]
        assert "(6 items)" in formatted[-1]
    
    def test_format_selector_max_visible(self):
        """Test selector respects max_visible."""
        items = [f"Item {i}" for i in range(20)]
        formatted = self.handler.format_selector(items)
        
        # Should only show 9 items (+ more indicator)
        visible_items = [f for f in formatted if not "More" in f]
        assert len(visible_items) == 9


class TestKeyHints:
    """Test key hint generation."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
    
    def test_navigation_hints(self):
        """Test hints for navigation mode."""
        self.handler.set_mode(KeypadMode.NAVIGATION)
        hints = self.handler.get_key_hints()
        
        assert "8" in hints
        assert "↑ Up" in hints["8"]
        assert "5" in hints
        assert "✓ Select" in hints["5"]
    
    def test_selection_hints(self):
        """Test hints for selection mode."""
        items = ["A", "B", "C"]
        self.handler.set_mode(KeypadMode.SELECTION)
        self.handler.set_items(items)
        hints = self.handler.get_key_hints()
        
        assert "1-9" in hints
        assert "Select item" in hints["1-9"]
    
    def test_selection_hints_with_more(self):
        """Test hints when more pages available."""
        items = [f"Item {i}" for i in range(20)]
        self.handler.set_mode(KeypadMode.SELECTION)
        self.handler.set_items(items)
        hints = self.handler.get_key_hints()
        
        assert "More options" in hints["0"]
    
    def test_editing_hints(self):
        """Test hints for editing mode."""
        self.handler.set_mode(KeypadMode.EDITING)
        hints = self.handler.get_key_hints()
        
        assert "7" in hints
        assert "Redo" in hints["7"]
        assert "9" in hints
        assert "Undo" in hints["9"]


class TestEnableDisable:
    """Test enable/disable functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.handler = KeypadHandler()
    
    def test_is_enabled_default(self):
        """Test handler is enabled by default."""
        assert self.handler.is_enabled() is True
    
    def test_disable(self):
        """Test disabling handler."""
        self.handler.disable()
        assert self.handler.is_enabled() is False
        assert self.handler.enabled is False
    
    def test_enable(self):
        """Test enabling handler."""
        self.handler.disable()
        self.handler.enable()
        assert self.handler.is_enabled() is True
    
    def test_handle_key_when_disabled(self):
        """Test key handling when disabled."""
        self.handler.disable()
        result = self.handler.handle_key('5')
        assert result is None


class TestReset:
    """Test reset functionality."""
    
    def test_reset(self):
        """Test resetting handler state."""
        handler = KeypadHandler()
        
        # Set some state
        handler.set_mode(KeypadMode.SELECTION)
        handler.set_items(["A", "B", "C"])
        handler.register_callback('5', lambda: "test")
        
        # Reset
        handler.reset()
        
        # Verify reset
        assert handler.context.mode == KeypadMode.NAVIGATION
        assert handler.context.items == []
        assert handler.callbacks == {}


class TestSingleton:
    """Test singleton pattern."""
    
    def test_get_keypad_handler(self):
        """Test getting singleton instance."""
        handler1 = get_keypad_handler()
        handler2 = get_keypad_handler()
        
        assert handler1 is handler2
    
    def test_singleton_state_persists(self):
        """Test singleton maintains state."""
        handler = get_keypad_handler()
        handler.set_mode(KeypadMode.EDITING)
        
        handler2 = get_keypad_handler()
        assert handler2.context.mode == KeypadMode.EDITING


class TestIntegration:
    """Test integration patterns."""
    
    def test_selector_integration(self):
        """Test integration with selector pattern."""
        handler = KeypadHandler()
        handler.set_mode(KeypadMode.SELECTION)
        
        # Set up menu options
        options = ["New File", "Open File", "Save", "Exit"]
        handler.set_items(options)
        
        # User presses 3
        result = handler.handle_key('3')
        assert result == "Save"
    
    def test_callback_override(self):
        """Test callback overrides default behavior."""
        handler = KeypadHandler()
        handler.set_mode(KeypadMode.NAVIGATION)
        
        custom_called = {'value': False}
        
        def custom_select():
            custom_called['value'] = True
            return "custom_select"
        
        handler.register_callback('5', custom_select)
        
        result = handler.handle_key('5')
        assert result == "custom_select"
        assert custom_called['value'] is True
    
    def test_multi_page_workflow(self):
        """Test complete multi-page selection workflow."""
        handler = KeypadHandler()
        handler.set_mode(KeypadMode.SELECTION)
        
        # Create 20 items
        items = [f"Item {i}" for i in range(20)]
        handler.set_items(items)
        
        # Page 1: Select item 5
        result = handler.handle_key('5')
        assert result == "Item 4"
        
        # Next page
        handler.handle_key('0')
        assert handler.context.page_offset == 9
        
        # Page 2: Select item 2 (actually item 10)
        result = handler.handle_key('2')
        assert result == "Item 10"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_items(self):
        """Test handling empty item list."""
        handler = KeypadHandler()
        handler.set_mode(KeypadMode.SELECTION)
        handler.set_items([])
        
        # Key '1' falls back to navigation, which doesn't handle '1'
        result = handler.handle_key('1')
        assert result is None
        
        # But navigation keys should work
        result = handler.handle_key('5')  # SELECT
        assert result == "select"
    
    def test_single_item(self):
        """Test selection with single item."""
        handler = KeypadHandler()
        handler.set_mode(KeypadMode.SELECTION)
        handler.set_items(["Only Item"])
        
        result = handler.handle_key('1')
        assert result == "Only Item"
    
    def test_exactly_nine_items(self):
        """Test with exactly 9 items (no more indicator)."""
        handler = KeypadHandler()
        items = [f"Item {i}" for i in range(9)]
        formatted = handler.format_selector(items)
        
        # Should be exactly 9 items, no more indicator
        assert len(formatted) == 9
        assert not any("More" in f for f in formatted)
    
    def test_ten_items(self):
        """Test with 10 items (triggers more indicator)."""
        handler = KeypadHandler()
        items = [f"Item {i}" for i in range(10)]
        formatted = handler.format_selector(items)
        
        # Should be 9 items + more indicator
        assert len(formatted) == 10
        assert "More" in formatted[-1]
    
    def test_callback_exception(self):
        """Test handling callback that raises exception."""
        handler = KeypadHandler()
        
        def bad_callback():
            raise ValueError("Test exception")
        
        handler.register_callback('5', bad_callback)
        
        # Should raise exception (not caught by handler)
        with pytest.raises(ValueError):
            handler.handle_key('5')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
