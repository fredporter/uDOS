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
from datetime import datetime

from core.tui.form_fields import (
    TUIFormRenderer,
    FieldType,
    DatePicker,
    TimePicker,
    BarSelector,
    SmartNumberPicker,
)
from core.services.logging_api import get_logger
from core.utils.tty import interactive_tty_status

logger = get_logger("story-form")


class StoryFormHandler:
    """Interactive handler for story-based forms in TUI."""
    
    def __init__(self):
        """Initialize story form handler."""
        self.renderer: Optional[TUIFormRenderer] = None
        self.original_settings = None
        self._override_fields_inserted = False
        self._pending_location_specs: List[Dict[str, Any]] = []
        self.interactive_reason: Optional[str] = None
    
    def process_story_form(self, form_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process interactive form from story specification.
        
        Args:
            form_spec: Story form specification with fields
            
        Returns:
            Dictionary with collected data
        """
        if not self._is_interactive():
            logger.info("[LOCAL] Non-interactive terminal detected, using fallback form handler")
            return SimpleFallbackFormHandler().process_story_form(form_spec)

        # Build form from spec
        renderer = TUIFormRenderer(
            title=form_spec.get('title', 'Form'),
            description=form_spec.get('description', ''),
            on_field_complete=self._on_field_complete,
        )
        self.renderer = renderer
        self._override_fields_inserted = False
        self._pending_location_specs = []

        # Add fields (non-location first, location fields queued for last)
        fields = form_spec.get('fields', [])
        for field_spec in fields:
            self._add_field_from_spec(renderer, field_spec)

        for location_spec in self._pending_location_specs:
            self._add_field_from_spec(renderer, location_spec, force_add=True)
        self._reorder_location_fields()
        
        # Run interactive form
        return self._run_interactive_form(renderer, form_spec)
    
    def _add_field_from_spec(self, renderer: TUIFormRenderer, spec: Dict, force_add: bool = False) -> None:
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

        if ftype == FieldType.LOCATION and not force_add:
            self._pending_location_specs.append(spec)
            return
        
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

    def _reorder_location_fields(self) -> None:
        """Ensure location fields render last."""
        if not self.renderer:
            return
        location_fields = [f for f in self.renderer.fields if f['type'] == FieldType.LOCATION]
        if not location_fields:
            return
        non_location = [f for f in self.renderer.fields if f['type'] != FieldType.LOCATION]
        self.renderer.fields = non_location + location_fields
    
    def _run_interactive_form(self, renderer: TUIFormRenderer, form_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run interactive form with keyboard input.
        
        Returns:
            Collected form data
        """
        # Setup terminal
        if not self._setup_terminal():
            logger.warning("[LOCAL] Terminal not interactive, using fallback form handler")
            return SimpleFallbackFormHandler().process_story_form(form_spec)
        
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
    
    def _on_field_complete(self, name: str, result: Any, submitted_data: Dict[str, Any]) -> None:
        """Hook called after each field is completed."""
        if name != "system_datetime_approve" or not isinstance(result, dict):
            return

        tz = result.get("timezone")
        if tz:
            submitted_data.setdefault("user_timezone", tz)

        if result.get("override_required"):
            self._insert_datetime_override_fields(result)

    def _insert_datetime_override_fields(self, approval_payload: Dict[str, Any]) -> None:
        """Insert manual override fields after the datetime approval question."""
        if self._override_fields_inserted or not self.renderer:
            return

        idx = self.renderer.current_field_index + 1
        override_fields = self._build_datetime_override_fields(approval_payload)
        self.renderer.fields[idx:idx] = override_fields
        self._override_fields_inserted = True
        self._reorder_location_fields()

    def _build_datetime_override_fields(self, approval_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build the override field definitions."""
        timezone_default = approval_payload.get("timezone", "UTC")
        date_default = approval_payload.get("date")
        time_default = approval_payload.get("time")

        return [
            self._create_field_record(
                name="user_timezone",
                label="Timezone (override)",
                field_type=FieldType.SELECT,
                config={
                    "required": True,
                    "options": [
                        "UTC",
                        "America/New_York",
                        "America/Los_Angeles",
                        "America/Chicago",
                        "Europe/London",
                        "Europe/Paris",
                        "Asia/Tokyo",
                        "Australia/Sydney",
                    ],
                    "default": timezone_default,
                    "placeholder": "Select timezone",
                },
            ),
            self._create_field_record(
                name="current_date",
                label="Current date (override)",
                field_type=FieldType.DATE,
                config={
                    "required": True,
                    "default": date_default,
                    "placeholder": "YYYY-MM-DD",
                },
            ),
            self._create_field_record(
                name="current_time",
                label="Current time (override)",
                field_type=FieldType.TIME,
                config={
                    "required": True,
                    "default": time_default,
                    "placeholder": "HH:MM:SS",
                },
            ),
        ]

    def _create_field_record(
        self, name: str, label: str, field_type: FieldType, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a renderer field record."""
        return {
            "name": name,
            "label": label,
            "type": field_type,
            "config": config,
            "widget": None,
            "value": None,
        }

    def _setup_terminal(self) -> bool:
        """Setup terminal for raw input capture."""
        try:
            if not self._is_interactive():
                return False
            self.original_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            return True
        except Exception as e:
            logger.warning(f"[LOCAL] Could not setup terminal: {e}")
            return False
    
    def _restore_terminal(self) -> None:
        """Restore terminal to original settings."""
        if self.original_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_settings)
            except Exception as e:
                logger.warning(f"[LOCAL] Could not restore terminal: {e}")

    def _is_interactive(self) -> bool:
        """Check if running in interactive terminal."""
        try:
            interactive, reason = interactive_tty_status()
            self.interactive_reason = reason
            return interactive
        except Exception:
            return False
    
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
            elif ftype == 'datetime_approve':
                now = datetime.now().astimezone()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                tz = now.tzname() or str(now.tzinfo) or "UTC"
                prompt = (
                    f"\n{label} (Detected {date_str} {time_str} {tz})\n"
                    "Approve? [Y/n]: "
                )
                choice = input(prompt).strip().lower()
                approved = choice in ("1", "y", "yes", "")
                payload = {
                    "approved": approved,
                    "date": date_str,
                    "time": time_str,
                    "timezone": tz,
                }
                data[name] = payload
                data.setdefault("user_timezone", tz)
                if not approved:
                    overrides = self._collect_datetime_overrides(payload)
                    data.update(overrides)
            
            else:
                # Simple text input
                prompt = f"{label}: "
                if default:
                    prompt = f"{label} [{default}]: "
                value = input(prompt).strip() or default
                data[name] = value
        
        return {"status": "success", "data": data}

    def _collect_datetime_overrides(self, base_payload: Dict[str, str]) -> Dict[str, str]:
        """Prompt for timezone, date, and time overrides when approval is declined."""
        overrides = {}
        tz_default = base_payload.get("timezone", "UTC")
        date_default = base_payload.get("date", "")
        time_default = base_payload.get("time", "")

        overrides["user_timezone"] = self._prompt_override("Timezone (override)", tz_default)
        overrides["current_date"] = self._prompt_override("Current date (override)", date_default)
        overrides["current_time"] = self._prompt_override("Current time (override)", time_default)

        return overrides

    def _prompt_override(self, label: str, default: str) -> str:
        """Prompt for an override value, falling back to the provided default."""
        prompt = f"{label} [{default}]: "
        try:
            value = input(prompt).strip()
        except EOFError:
            return default
        return value or default


def get_form_handler() -> StoryFormHandler:
    """Get appropriate form handler (interactive or fallback)."""
    if not _interactive_tty_available():
        logger.warning("[LOCAL] Terminal not interactive; using fallback form handler.")
        return SimpleFallbackFormHandler()

    try:
        handler = StoryFormHandler()
        return handler
    except Exception as e:
        logger.warning(f"[LOCAL] Interactive form unavailable: {e}, using fallback")
        return SimpleFallbackFormHandler()


def _interactive_tty_available() -> bool:
    """Detect if stdin and stdout support interactive TTY."""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:
        return False
