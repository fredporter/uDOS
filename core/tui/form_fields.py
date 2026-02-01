"""
TUI Form Fields System - Modern, robust form input widgets for interactive TUI.

Provides:
- SmartNumberPicker: Year/Month/Day/Hour/Minute/Second with smart parsing
- DatePicker: Full date selector
- TimePicker: Full time selector
- BarSelector: Multi-option selector with visual bar
- TextInput: Enhanced text entry with validation
- SelectField: Dropdown/multi-select field

All fields support:
- Keyboard navigation (arrow keys, tab, enter)
- Smart input (e.g., typing "75" auto-interprets as 1975)
- Visual feedback and state display
- Validation and error messages
- Degradable to simple input if needed
"""

import sys
import calendar
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable
from pathlib import Path

from core.services.logging_service import get_repo_root
from core.services.maintenance_utils import get_memory_root
from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    """Field input types."""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    TIME = "time"
    DATETIME_APPROVE = "datetime_approve"
    SELECT = "select"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    LOCATION = "location"


@dataclass
class FieldConfig:
    """Configuration for a form field."""
    name: str
    label: str
    type: FieldType
    required: bool = False
    placeholder: str = ""
    default: Any = None
    validation: Optional[Callable] = None
    options: Optional[List[str]] = None  # For SELECT fields
    min_value: Optional[int] = None  # For NUMBER fields
    max_value: Optional[int] = None  # For NUMBER fields


class SmartNumberPicker:
    """Smart number input picker with intelligent parsing."""
    
    def __init__(self, label: str, min_val: int = 0, max_val: int = 9999, 
                 default: Optional[int] = None, width: int = 4):
        """
        Initialize smart number picker.
        
        Args:
            label: Field label
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
            width: Display width (number of digits)
        """
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.default = default or min_val
        self.width = width
        self.value = self.default
        self.input_buffer = ""
        self.cursor_pos = 0
    
    def render(self, focused: bool = False) -> str:
        """Render the picker."""
        val_str = str(self.value).zfill(self.width)
        
        if focused:
            # Show input buffer if typing
            if self.input_buffer:
                display = self.input_buffer.zfill(self.width)
                return f"❯ {self.label}: [{display}]"
            else:
                # Show value with cursor
                return f"❯ {self.label}: [{val_str}]"
        else:
            return f"  {self.label}: {val_str}"
    
    def handle_input(self, char: str) -> bool:
        """
        Handle character input with smart parsing.
        
        Args:
            char: Input character
            
        Returns:
            True if input was handled, False otherwise
        """
        if char == '\x7f' or char == '\b':  # Backspace
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
            return True
        
        elif char.isdigit():
            # Add to input buffer
            new_buffer = self.input_buffer + char
            
            # Smart parsing
            if self.width == 4:  # Year field
                self._handle_year_input(new_buffer)
            elif self.width == 2:  # Month/Day/Hour/Minute/Second
                self._handle_bounded_input(new_buffer)
            
            return True
        
        elif char in ['\n', '\r']:  # Enter
            self._finalize_input()
            return True
        
        elif char == '\t':  # Tab (move to next field - handled by form)
            self._finalize_input()
            return False  # Signal move to next
        
        return False
    
    def _handle_year_input(self, buffer: str) -> None:
        """Smart year parsing: 75 -> 1975, 25 -> 2025, 1985 -> 1985."""
        if len(buffer) > 4:
            return  # Too long
        
        num = int(buffer)
        
        if len(buffer) == 2 and num < 100:
            # Two-digit year: apply intelligent heuristic
            # 00-30 -> 2000-2030 (future)
            # 31-99 -> 1931-1999 (past)
            if num <= 30:
                num += 2000
            else:
                num += 1900
        
        if self.min_val <= num <= self.max_val:
            self.input_buffer = buffer
            self.value = num
    
    def _handle_bounded_input(self, buffer: str) -> None:
        """Handle month/day/hour/minute/second (bounded 1-59)."""
        if len(buffer) > self.width:
            return
        
        num = int(buffer)
        if self.min_val <= num <= self.max_val:
            self.input_buffer = buffer
            self.value = num
    
    def _finalize_input(self) -> None:
        """Finalize the current input buffer."""
        if self.input_buffer:
            self.value = int(self.input_buffer)
        self.input_buffer = ""
    
    def arrow_up(self) -> None:
        """Increment value."""
        if self.value < self.max_val:
            self.value += 1
            self.input_buffer = ""
    
    def arrow_down(self) -> None:
        """Decrement value."""
        if self.value > self.min_val:
            self.value -= 1
            self.input_buffer = ""
    
    def get_value(self) -> int:
        """Get current value."""
        self._finalize_input()
        return self.value


class DatePicker:
    """Interactive date picker with YY/MM/DD fields."""
    
    def __init__(self, label: str, default: Optional[str] = None):
        """
        Initialize date picker.
        
        Args:
            label: Field label
            default: Default date in YYYY-MM-DD format
        """
        self.label = label
        
        # Parse default or use current date
        if default:
            parts = default.split('-')
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            from datetime import datetime
            now = datetime.now()
            year, month, day = now.year, now.month, now.day
        
        self.year_picker = SmartNumberPicker("Year", min_val=1900, max_val=2100, default=year, width=4)
        self.month_picker = SmartNumberPicker("Month", min_val=1, max_val=12, default=month, width=2)
        self.day_picker = SmartNumberPicker("Day", min_val=1, max_val=31, default=day, width=2)
        
        self.current_field = 0  # 0=year, 1=month, 2=day
        self.pickers = [self.year_picker, self.month_picker, self.day_picker]
    
    def render(self) -> str:
        """Render the date picker."""
        lines = [f"\n📅 {self.label}"]
        lines.append("=" * 50)
        
        for i, picker in enumerate(self.pickers):
            focused = i == self.current_field
            lines.append(picker.render(focused=focused))

        lines.append("")
        lines.extend(self._render_calendar())
        
        lines.append("\n▸ Use arrow keys or type | Tab/Enter to confirm")
        return "\n".join(lines)

    def _render_calendar(self) -> List[str]:
        """Render a month calendar with the selected day highlighted."""
        year = self.year_picker.get_value()
        month = self.month_picker.get_value()
        day = self.day_picker.get_value()

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(year, month)
        month_name = calendar.month_name[month]

        lines = [f"  {month_name} {year}", "  Mo Tu We Th Fr Sa Su"]

        for week in weeks:
            day_strs = []
            for d in week:
                if d == 0:
                    day_strs.append("   ")
                elif d == day:
                    day_strs.append(f"[{d:2d}]")
                else:
                    day_strs.append(f" {d:2d} ")
            lines.append(" ".join(day_strs).rstrip())

        return lines
    
    def handle_input(self, key: str) -> Optional[str]:
        """
        Handle keyboard input.
        
        Returns:
            Date string if complete, None otherwise
        """
        current_picker = self.pickers[self.current_field]
        
        if key == '\x1b':  # Escape sequence start
            return None  # Let parent handle escape codes
        
        elif key == '\t':  # Tab - move to next field
            current_picker._finalize_input()
            if self.current_field < len(self.pickers) - 1:
                self.current_field += 1
            return None
        
        elif key == '\n' or key == '\r':  # Enter - confirm
            self._finalize()
            return self.get_value()
        
        elif key == 'up':  # Arrow up
            current_picker.arrow_up()
            return None
        
        elif key == 'down':  # Arrow down
            current_picker.arrow_down()
            return None
        
        else:
            # Try to handle in current picker
            current_picker.handle_input(key)
            return None
    
    def _finalize(self) -> None:
        """Finalize all pickers."""
        for picker in self.pickers:
            picker._finalize_input()
    
    def get_value(self) -> str:
        """Get date as YYYY-MM-DD string."""
        self._finalize()
        year = self.year_picker.get_value()
        month = self.month_picker.get_value()
        day = self.day_picker.get_value()
        return f"{year:04d}-{month:02d}-{day:02d}"


class TimePicker:
    """Interactive time picker with HH/MM/SS fields."""
    
    def __init__(self, label: str, default: Optional[str] = None):
        """
        Initialize time picker.
        
        Args:
            label: Field label
            default: Default time in HH:MM:SS format
        """
        self.label = label
        
        # Parse default or use current time
        if default:
            parts = default.split(':')
            hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
        else:
            from datetime import datetime
            now = datetime.now()
            hour, minute, second = now.hour, now.minute, now.second
        
        self.hour_picker = SmartNumberPicker("Hour", min_val=0, max_val=23, default=hour, width=2)
        self.minute_picker = SmartNumberPicker("Minute", min_val=0, max_val=59, default=minute, width=2)
        self.second_picker = SmartNumberPicker("Second", min_val=0, max_val=59, default=second, width=2)
        
        self.current_field = 0  # 0=hour, 1=minute, 2=second
        self.pickers = [self.hour_picker, self.minute_picker, self.second_picker]
    
    def render(self) -> str:
        """Render the time picker."""
        lines = [f"\n⏱️  {self.label}"]
        lines.append("=" * 50)
        
        for i, picker in enumerate(self.pickers):
            focused = i == self.current_field
            lines.append(picker.render(focused=focused))
        
        lines.append("\n▸ Use arrow keys or type | Tab/Enter to confirm")
        return "\n".join(lines)


class DateTimeApproval:
    """Approval prompt for current date, time, and timezone with ASCII clock."""

    def __init__(self, label: str, timezone_hint: Optional[str] = None):
        self.label = label
        self.timezone_hint = timezone_hint

    def _get_now(self) -> datetime:
        return datetime.now().astimezone()

    def _get_timezone(self, now: datetime) -> str:
        if self.timezone_hint:
            return self.timezone_hint
        tzinfo = now.tzinfo
        if hasattr(tzinfo, "key"):
            return str(tzinfo.key)
        return str(tzinfo) or "UTC"

    def _current_payload(self) -> Dict[str, Any]:
        now = self._get_now()
        tz = self._get_timezone(now)
        return {
            "approved": None,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": tz,
        }

    def _render_clock(self, now: datetime) -> List[str]:
        time_str = now.strftime("%H:%M:%S")
        return [
            "  ┌───────────┐",
            f"  │  {time_str}  │",
            "  └───────────┘",
        ]

    def render(self, focused: bool = False) -> str:
        now = self._get_now()
        tz = self._get_timezone(now)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        lines = [f"\n⏰ {self.label}", "=" * 50]
        lines.append(f"  Date:     {date_str}")
        lines.append(f"  Time:     {time_str}")
        lines.append(f"  Timezone: {tz}")
        lines.append("")
        lines.extend(self._render_clock(now))
        lines.append("")
        lines.append("  Approve? [1-Yes|0-No|Enter-OK]")
        return "\n".join(lines)

    def handle_input(self, key: str) -> Optional[Dict[str, Any]]:
        """Process key input and return status for overlay handling."""
        payload = self._current_payload()
        normalized = (key or "").strip().lower()

        approve_keys = {"", "1", "y", "yes", "ok"}
        deny_keys = {"0", "n", "no", "x", "cancel"}
        newline_keys = {"\n", "\r"}

        if key in newline_keys:
            normalized = ""

        if normalized in approve_keys:
            payload.update(
                {
                    "approved": True,
                    "status": "approved",
                    "override_required": False,
                }
            )
            return payload

        if normalized in deny_keys:
            payload.update(
                {
                    "approved": False,
                    "status": "denied",
                    "override_required": True,
                }
            )
            return payload

        return None
    
class BarSelector:
    """Bar-style selector for multiple options."""
    
    def __init__(self, label: str, options: List[str], default_index: int = 0):
        """
        Initialize bar selector.
        
        Args:
            label: Field label
            options: List of option strings
            default_index: Index of default option
        """
        self.label = label
        self.options = options
        self.selected_index = default_index
    
    def render(self, focused: bool = False) -> str:
        """Render the selector."""
        if not focused:
            selected = self.options[self.selected_index]
            return f"  {self.label}: {selected}"
        
        # Focused view - show all options with selector
        lines = [f"\n  {self.label}:"]
        lines.append("  " + "=" * 48)
        
        for i, option in enumerate(self.options):
            if i == self.selected_index:
                lines.append(f"  ❯ {option}")
            else:
                lines.append(f"    {option}")
        
        lines.append("  " + "=" * 48)
        lines.append("  ▸ Use arrow keys ↑/↓ or click | Enter to select")
        
        return "\n".join(lines)
    
    def handle_input(self, key: str) -> Optional[str]:
        """Handle input. Returns selected option on Enter."""
        if key == 'up':
            if self.selected_index > 0:
                self.selected_index -= 1
            return None
        elif key == 'down':
            if self.selected_index < len(self.options) - 1:
                self.selected_index += 1
            return None
        elif key == '\n' or key == '\r':
            return self.get_value()
        
        return None
    
    def get_value(self) -> str:
        """Get selected option."""
        return self.options[self.selected_index]


class LocationSelector:
    """Interactive location selector with fuzzy search and timezone default."""

    def __init__(
        self,
        label: str,
        locations: List[Dict[str, Any]],
        default_location: Optional[Dict[str, Any]] = None,
        timezone_hint: Optional[str] = None,
        max_results: int = 8,
    ):
        self.label = label
        self.locations = locations
        self.default_location = default_location
        self.timezone_hint = (timezone_hint or "").strip().lower()
        self.max_results = max_results
        self.query = ""
        self.matches = self._filter_matches()
        self.selected_index = 0

        if default_location:
            for i, match in enumerate(self.matches):
                if match.get("id") == default_location.get("id"):
                    self.selected_index = i
                    break

    def _filter_matches(self) -> List[Dict[str, Any]]:
        query_norm = self.query.strip().lower()
        results = []

        for loc in self.locations:
            name = str(loc.get("name", ""))
            loc_id = str(loc.get("id", ""))
            loc_type = str(loc.get("type", ""))
            scale = str(loc.get("scale", ""))
            region = str(loc.get("region", ""))
            continent = str(loc.get("continent", ""))
            timezone_val = str(loc.get("timezone", ""))

            haystack = " ".join(
                [name, loc_id, loc_type, scale, region, continent, timezone_val]
            ).lower()

            if query_norm and query_norm not in haystack:
                if not name.lower().startswith(query_norm):
                    continue

            score = 0
            if query_norm:
                if name.lower().startswith(query_norm):
                    score += 3
                if query_norm in name.lower():
                    score += 2
                if query_norm in loc_id.lower():
                    score += 1
                if query_norm in loc_type.lower() or query_norm in scale.lower():
                    score += 1
            if self.timezone_hint and timezone_val.lower() == self.timezone_hint:
                score += 2

            results.append({**loc, "score": score})

        results.sort(key=lambda r: (-r.get("score", 0), r.get("name", "")))
        return results[: self.max_results]

    def render(self, focused: bool = False) -> str:
        if not focused:
            if self.matches:
                selected = self.matches[self.selected_index]
                return f"  {self.label}: {selected.get('name')}"
            return f"  {self.label}: (no matches)"

        lines = [f"\n  {self.label}:"]
        lines.append("  " + "=" * 48)
        lines.append(f"  Search: {self.query or '(type to search)'}")
        lines.append("  " + "-" * 48)

        if not self.matches:
            lines.append("  (no matches)")
        else:
            for i, match in enumerate(self.matches):
                prefix = "❯" if i == self.selected_index else " "
                name = match.get("name", "Unknown")
                loc_id = match.get("id", "")
                scale = match.get("scale", "")
                tz = match.get("timezone", "")
                lines.append(f"  {prefix} {name} [{loc_id}] ({scale}, {tz})")

            selected = self.matches[self.selected_index]
            lines.append("  " + "-" * 48)
            lines.extend(self._render_map_layer(selected))

        lines.append("  " + "=" * 48)
        lines.append("  ▸ Type to search | ↑/↓ to move | Enter to select")
        return "\n".join(lines)

    def _render_map_layer(self, location: Dict[str, Any]) -> List[str]:
        name = str(location.get("name", ""))[:18]
        layer = str(location.get("layer", ""))
        cell = str(location.get("cell", ""))
        return [
            "  Map Layer (local):",
            "  +--------------------+",
            f"  | {name:<18} |",
            f"  | Layer {layer:<10} |",
            f"  | Cell  {cell:<10} |",
            "  +--------------------+",
        ]

    def handle_input(self, key: str) -> Optional[Dict[str, Any]]:
        if key == 'up':
            if self.selected_index > 0:
                self.selected_index -= 1
            return None
        if key == 'down':
            if self.selected_index < max(0, len(self.matches) - 1):
                self.selected_index += 1
            return None
        if key in ('\n', '\r'):
            return self.get_value()
        if key in ('\x7f', '\b'):
            if self.query:
                self.query = self.query[:-1]
                self.matches = self._filter_matches()
                self.selected_index = 0
            return None
        if len(key) == 1 and key.isprintable():
            self.query += key
            self.matches = self._filter_matches()
            self.selected_index = 0
            return None
        return None

    def get_value(self) -> Optional[Dict[str, Any]]:
        if not self.matches:
            return None
        return self.matches[self.selected_index]


class TUIFormRenderer:
    """Handles interactive TUI form rendering and field management."""
    
    def __init__(self, title: str = "Form", description: str = "", on_field_complete: Optional[Callable] = None):
        """Initialize form renderer."""
        self.title = title
        self.description = description
        self.fields: List[Dict[str, Any]] = []
        self.current_field_index = 0
        self.submitted_data: Dict[str, Any] = {}
        self.on_field_complete = on_field_complete
    
    def add_field(self, name: str, label: str, field_type: FieldType, **kwargs) -> None:
        """Add a field to the form."""
        field = {
            'name': name,
            'label': label,
            'type': field_type,
            'config': kwargs,
            'widget': None,  # Will be initialized on render
            'value': None,
        }
        self.fields.append(field)
    
    def render(self) -> str:
        """Render the current field."""
        if self.current_field_index >= len(self.fields):
            return self._render_completion()
        
        field = self.fields[self.current_field_index]
        
        # Initialize widget if needed
        if field['widget'] is None:
            field['widget'] = self._create_widget(field)
        
        return self._render_field(field)
    
    def _create_widget(self, field: Dict) -> Any:
        """Create appropriate widget for field type."""
        name = field['name']
        label = field['label']
        config = field['config']
        ftype = field['type']
        
        if ftype == FieldType.DATE:
            return DatePicker(label, default=config.get('default'))
        elif ftype == FieldType.TIME:
            return TimePicker(label, default=config.get('default'))
        elif ftype == FieldType.DATETIME_APPROVE:
            timezone_hint = self.submitted_data.get(config.get('timezone_field', 'user_timezone'))
            return DateTimeApproval(label, timezone_hint=timezone_hint)
        elif ftype == FieldType.SELECT:
            options = config.get('options', [])
            default_idx = 0
            if config.get('default'):
                try:
                    default_idx = options.index(config['default'])
                except ValueError:
                    pass
            return BarSelector(label, options, default_idx)
        elif ftype == FieldType.NUMBER:
            return SmartNumberPicker(
                label,
                min_val=config.get('min_value', 0),
                max_val=config.get('max_value', 9999),
                default=config.get('default'),
            )
        elif ftype == FieldType.LOCATION:
            from core.locations import LocationService
            tz_field = config.get('timezone_field', 'user_timezone')
            timezone_hint = self.submitted_data.get(tz_field)
            if not timezone_hint:
                timezone_hint = self._get_system_timezone()

            service = LocationService()
            locations = service.get_all_locations()
            default_location = service.get_default_location_for_timezone(timezone_hint)

            return LocationSelector(
                label,
                locations=locations,
                default_location=default_location,
                timezone_hint=timezone_hint,
            )
        else:
            # TEXT, TEXTAREA - simple input
            return None

    def _get_system_timezone(self) -> str:
        now = datetime.now().astimezone()
        tzinfo = now.tzinfo
        if hasattr(tzinfo, "key"):
            return str(tzinfo.key)
        return str(tzinfo) or "UTC"
    
    def _render_field(self, field: Dict) -> str:
        """Render a single field."""
        lines = []
        
        # Header
        lines.append("\n" + "=" * 60)
        lines.append(f"  {self.title}")
        if self.description:
            lines.append(f"  {self.description}")
        lines.append("=" * 60)
        
        # Progress
        progress = f"{self.current_field_index + 1}/{len(self.fields)}"
        lines.append(f"\n  [{progress}] {field['label']}")
        
        # Field
        widget = field['widget']
        if widget:
            lines.append(widget.render(focused=True))
        else:
            # Simple text input
            lines.append(f"  {field['label']}: [___]")
        
        lines.append("\n")
        
        return "\n".join(lines)
    
    def _render_completion(self) -> str:
        """Render completion screen."""
        lines = [
            "\n" + "=" * 60,
            f"  ✅ {self.title} Complete!",
            "=" * 60,
            "\nCollected data:",
        ]
        
        for field in self.fields:
            lines.append(f"  • {field['label']}: {field['value']}")

        lines.append("\n" + "=" * 60)
        lines.extend(self._render_structure_summary())
        lines.append("\n  ✳️  See docs/SEED-INSTALLATION-GUIDE.md for expectations")
        lines.append("=" * 60)
        
        return "\n".join(lines)

    def _render_structure_summary(self) -> List[str]:
        """Render the local/memory/bank/seed structure confirmation."""
        repo_root = get_repo_root()
        memory_root = get_memory_root()
        bank_root = memory_root / "bank"
        seed_root = repo_root / "core" / "framework" / "seed"
        seed_bank = seed_root / "bank"
        guide_doc = repo_root / "docs" / "SEED-INSTALLATION-GUIDE.md"

        def fmt(label: str, path: Path) -> str:
            status = "✅" if path.exists() else "❌"
            return f"  • {label}: {status} ({path})"

        summary = [
            "\nSystem structure summary:",
            fmt("local repo root", repo_root),
            fmt("memory root", memory_root),
            fmt("memory/bank", bank_root),
            fmt("framework seed root", seed_root),
            fmt("seed bank data", seed_bank),
            fmt("seed installation guide", guide_doc),
        ]
        return summary
    
    def handle_input(self, key: str) -> bool:
        """
        Handle input for current field.
        
        Returns:
            True if form is complete, False otherwise
        """
        if self.current_field_index >= len(self.fields):
            return True
        
        field = self.fields[self.current_field_index]
        widget = field['widget']
        
        if widget:
            result = widget.handle_input(key)
            if result is not None:
                # Extract location ID if this is a location field
                if field['type'] == FieldType.LOCATION and isinstance(result, dict):
                    field['value'] = result.get('id', result)
                    self.submitted_data[field['name']] = result.get('id', result)
                else:
                    field['value'] = result
                    self.submitted_data[field['name']] = result
                
                # Call completion callback if provided
                if self.on_field_complete:
                    self.on_field_complete(field['name'], result, self.submitted_data)
                
                self.current_field_index += 1
                
                # Advance to next
                if self.current_field_index < len(self.fields):
                    self.fields[self.current_field_index]['widget'] = \
                        self._create_widget(self.fields[self.current_field_index])
        
        return self.current_field_index >= len(self.fields)
    
    def get_data(self) -> Dict[str, Any]:
        """Get submitted form data."""
        return self.submitted_data


if __name__ == "__main__":
    # Test the components
    picker = SmartNumberPicker("Year", min_val=1900, max_val=2100, default=2000)
    print(picker.render(focused=True))
    
    date_picker = DatePicker("Date of Birth")
    print(date_picker.render())
    
    selector = BarSelector("Role", ["ghost", "user", "admin"])
    print(selector.render(focused=True))
