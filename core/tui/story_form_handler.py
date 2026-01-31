"""
Interactive Story Form Handler - TUI integration for story-based forms.

Handles:
- Interactive field rendering
- Keyboard input capture
- Form state management
- Data collection and validation
"""

import sys
import termios
import tty
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.tui.form_fields import (
    TUIFormRenderer,
    FieldType,
    DatePicker,
    TimePicker,
    BarSelector,
    SmartNumberPicker,
)
from core.services.logging_service import get_logger

logger = get_logger("story-form")


class StoryFormHandler:
    """Interactive handler for story-based forms in TUI."""
    
    def __init__(self):
        """Initialize story form handler."""
        self.renderer: Optional[TUIFormRenderer] = None
        self.original_settings = None
    
    def process_story_form(self, form_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process interactive form from story specification.
        
        Args:
            form_spec: Story form specification with fields
            
        Returns:
            Dictionary with collected data
        """
        # Build form from spec
        renderer = TUIFormRenderer(
            title=form_spec.get('title', 'Form'),
            description=form_spec.get('description', ''),
        )
        
        # Add fields
        fields = form_spec.get('fields', [])
        for field_spec in fields:
            self._add_field_from_spec(renderer, field_spec)
        
        # Run interactive form
        return self._run_interactive_form(renderer)
    
    def _add_field_from_spec(self, renderer: TUIFormRenderer, spec: Dict) -> None:
        """Add field to renderer from specification."""
        name = spec.get('name', 'unknown')
        label = spec.get('label', name)
        ftype_str = spec.get('type', 'text').lower()
        
        # Map string type to FieldType
        type_map = {
            'text': FieldType.TEXT,
            'number': FieldType.NUMBER,
            'date': FieldType.DATE,
            'time': FieldType.TIME,
            'datetime_approve': FieldType.DATETIME_APPROVE,
            'select': FieldType.SELECT,
            'checkbox': FieldType.CHECKBOX,
            'textarea': FieldType.TEXTAREA,
                    'location': FieldType.LOCATION,
        }
        
        ftype = type_map.get(ftype_str, FieldType.TEXT)
        
        # Build kwargs from spec
        kwargs = {
            'required': spec.get('required', False),
            'placeholder': spec.get('placeholder', ''),
            'default': spec.get('default'),
        }
        
        if ftype == FieldType.SELECT:
            kwargs['options'] = spec.get('options', [])
        
        if ftype == FieldType.NUMBER:
            kwargs['min_value'] = spec.get('min_value')
            kwargs['max_value'] = spec.get('max_value')
        
        if ftype == FieldType.LOCATION:
            kwargs['timezone_field'] = spec.get('timezone_field', 'user_timezone')
        
        renderer.add_field(name, label, ftype, **kwargs)
    
    def _run_interactive_form(self, renderer: TUIFormRenderer) -> Dict[str, Any]:
        """
        Run interactive form with keyboard input.
        
        Returns:
            Collected form data
        """
        # Setup terminal
        self._setup_terminal()
        
        try:
            while not renderer.current_field_index >= len(renderer.fields):
                # Render current field
                self._clear_screen()
                output = renderer.render()
                print(output, end='', flush=True)
                
                # Get input
                key = self._read_key()
                
                if key == '\x1b':  # Escape key
                    logger.info("[LOCAL] Form cancelled by user")
                    return {"status": "cancelled", "data": {}}
                
                # Handle input
                renderer.handle_input(key)
            
            # Form complete
            data = renderer.get_data()
            logger.info(f"[LOCAL] Form submitted with {len(data)} fields")
            return {"status": "success", "data": data}
        
        finally:
            # Restore terminal
            self._restore_terminal()
    
    def _setup_terminal(self) -> None:
        """Setup terminal for raw input capture."""
        try:
            self.original_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except Exception as e:
            logger.warning(f"[LOCAL] Could not setup terminal: {e}")
    
    def _restore_terminal(self) -> None:
        """Restore terminal to original settings."""
        if self.original_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_settings)
            except Exception as e:
                logger.warning(f"[LOCAL] Could not restore terminal: {e}")
    
    def _read_key(self) -> str:
        """
        Read a single key with support for arrow keys.
        
        Returns:
            Key string ('up', 'down', 'left', 'right', or character)
        """
        ch = sys.stdin.read(1)
        
        if ch == '\x1b':  # Escape sequence
            next_ch = sys.stdin.read(1)
            if next_ch == '[':
                arrow = sys.stdin.read(1)
                if arrow == 'A':
                    return 'up'
                elif arrow == 'B':
                    return 'down'
                elif arrow == 'C':
                    return 'right'
                elif arrow == 'D':
                    return 'left'
        
        return ch
    
    def _clear_screen(self) -> None:
        """Clear terminal screen."""
        print('\033[2J\033[H', end='', flush=True)


# Fallback simple form handler for degraded mode
class SimpleFallbackFormHandler:
    """Fallback form handler using simple input() calls (no interactive UI)."""
    
    def process_story_form(self, form_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process form using simple input prompts."""
        data = {}
        
        for field_spec in form_spec.get('fields', []):
            name = field_spec.get('name', 'unknown')
            label = field_spec.get('label', name)
            default = field_spec.get('default', '')
            options = field_spec.get('options', [])
            ftype = field_spec.get('type', 'text')
            
            if options:
                # Simple selection
                print(f"\n{label}:")
                for i, opt in enumerate(options, 1):
                    print(f"  {i}. {opt}")
                choice = input("Choose option: ").strip()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        data[name] = options[idx]
                except ValueError:
                    pass
            
            elif ftype in ['date', 'time']:
                # Prompt for date/time
                prompt = f"{label} ({default}): "
                value = input(prompt).strip() or default
                data[name] = value
            
            else:
                # Simple text input
                prompt = f"{label}: "
                if default:
                    prompt = f"{label} [{default}]: "
                value = input(prompt).strip() or default
                data[name] = value
        
        return {"status": "success", "data": data}


def get_form_handler() -> StoryFormHandler:
    """Get appropriate form handler (interactive or fallback)."""
    try:
        # Try interactive handler
        handler = StoryFormHandler()
        return handler
    except Exception as e:
        logger.warning(f"[LOCAL] Interactive form unavailable: {e}, using fallback")
        return SimpleFallbackFormHandler()
