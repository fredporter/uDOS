"""
Advanced TUI Form Field Handler - Enhanced Story Forms

Provides:
  - Syntax-highlighting style predictive answers
  - Auto-complete with system data (timezone, city, time)
  - Tab navigation between fields with default acceptance
  - Enter key to accept default values
  - Real-time validation with feedback
  - Color-coded field states (empty, valid, error, predictive)

Example field with prediction:
  Label: Your timezone
  [Hint: America/Los_Angeles] ← Pre-filled suggestion
  User input: [Tab to accept or type to override]
              [Enter to accept default]

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

import sys
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import json
import termios
import tty

from core.utils.tty import interactive_tty_status
from core.tui.form_fields import DatePicker

from core.services.logging_api import get_logger, LogTags

logger = get_logger("tui-form-handler")

# ANSI Color codes for syntax highlighting
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

    @staticmethod
    def disable():
        """Disable colors (for piped output)."""
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')


class AdvancedFormField:
    """Advanced form field handler with predictions and smart navigation."""

    def __init__(self):
        """Initialize form field handler."""
        self.history = []
        self.predictions = {}
        self.use_typeform_layout = True
        self._terminal_settings = None

    @staticmethod
    def _clean_input(raw_input: str) -> str:
        """Remove ANSI escape sequences from input (e.g., arrow keys).

        Args:
            raw_input: Raw input string that may contain escape sequences

        Returns:
            Cleaned input string with escape sequences removed
        """
        import re
        # Remove ANSI escape sequences (arrow keys, etc.)
        # Pattern matches ESC [ followed by any characters up to a letter
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
        cleaned = ansi_escape.sub('', raw_input)
        # Also remove any remaining control characters
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', cleaned)
        return cleaned.strip()

    # ========================================================================
    # PREDICTIVE SUGGESTIONS
    # ========================================================================

    def load_system_suggestions(self) -> Dict[str, Any]:
        """Load system-detected suggestions for common fields.

        Returns:
            Dictionary of field names to suggested values
        """
        try:
            import subprocess
            from datetime import datetime

            suggestions = {}

            # System timezone
            try:
                import time
                tz_name = time.tzname[0] if time.daylight == 0 else time.tzname[1]
                suggestions['user_timezone'] = self._get_iana_timezone()
            except:
                suggestions['user_timezone'] = 'UTC'

            # System time
            suggestions['user_local_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            suggestions['user_date'] = datetime.now().strftime("%Y-%m-%d")
            suggestions['time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            suggestions['date'] = datetime.now().strftime("%Y-%m-%d")
            suggestions['datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M")

            # System hostname (possible location hint)
            try:
                hostname = subprocess.check_output(['hostname']).decode().strip()
                suggestions['_hostname'] = hostname
            except:
                pass

            return suggestions
        except Exception as e:
            logger.debug(f"[LOCAL] Failed to load suggestions: {e}")
            return {}

    def _get_iana_timezone(self) -> str:
        """Get IANA timezone name for system.

        Returns:
            IANA timezone string (e.g., "America/Los_Angeles")
        """
        try:
            import subprocess
            # Try to get current timezone from timedatectl
            result = subprocess.check_output(['timedatectl', 'show', '-p', 'Timezone', '--value'],
                                            text=True, stderr=subprocess.DEVNULL)
            if result:
                return result.strip()
        except:
            pass

        try:
            # Fallback: read from /etc/timezone on Linux
            with open('/etc/timezone', 'r') as f:
                return f.read().strip()
        except:
            pass

        try:
            # macOS fallback
            import subprocess
            tz = subprocess.check_output(
                ['systemsetup', '-gettimezone'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if tz.startswith('Time Zone: '):
                return tz.replace('Time Zone: ', '')
        except:
            pass

        return 'UTC'

    # ========================================================================
    # FIELD RENDERING WITH PREDICTIONS
    # ========================================================================

    def render_field(self, field: Dict, suggestion: Optional[str] = None) -> str:
        """Render a form field with syntax highlighting and suggestion.

        Args:
            field: Field definition with name, label, type, validation, etc.
            suggestion: Optional suggested value to display

        Returns:
            Formatted field display string
        """
        name = field.get('name', 'unknown')
        label = field.get('label', 'Field')
        required = field.get('required', False)
        req_label = f"{Colors.BRIGHT_RED}*{Colors.RESET}" if required else " "

        # Build field display
        lines = []
        lines.append(f"\n{Colors.BOLD}{req_label} {label}:{Colors.RESET}")

        # Show help text if present
        help_text = field.get('help', '')
        if help_text:
            lines.append(f"  {Colors.DIM}{help_text}{Colors.RESET}")

        # Show suggestion if available
        if suggestion:
            lines.append(f"  {Colors.CYAN}Suggestion:{Colors.RESET} {Colors.BRIGHT_CYAN}{suggestion}{Colors.RESET}")
            lines.append(f"  {Colors.DIM}(Press Tab to accept, or type to override){Colors.RESET}")

        # Show placeholder
        placeholder = field.get('placeholder', '')
        if placeholder:
            lines.append(f"  {Colors.DIM}e.g., {placeholder}{Colors.RESET}")

        return "\n".join(lines)

    # ========================================================================
    # FIELD INPUT COLLECTION
    # ========================================================================

    def collect_field_input(self, field: Dict, suggestion: Optional[str] = None) -> Optional[str]:
        """Collect user input for a field with suggestion support.

        Supports:
          - Enter/Tab to accept suggestion
          - Type to override
          - Backspace to clear
          - Ctrl+U to clear line
          - Validation feedback

        Args:
            field: Field definition
            suggestion: Optional suggested value

        Returns:
            User input (or suggestion if accepted), or None if skipped
        """
        if not self._is_interactive():
            logger.info("[LOCAL] Non-interactive mode detected for field input, using basic input()")
            return self._collect_field_input_fallback(field, suggestion)

        name = field.get('name', 'unknown')
        field_type = field.get('type', 'text')
        required = field.get('required', False)
        validation = field.get('validation')
        default_from_system = field.get('default_from_system', False)
        options = field.get('options', [])

        # Handle date fields with TUI datepicker
        if field_type == 'date' or 'dob' in name.lower():
            return self._collect_datepicker_field(field, suggestion)

        # Handle select fields with menu
        if field_type == 'select' and options:
            return self._collect_select_field(field, suggestion)

        # Auto-generate system default for datetime/date/time fields with default_from_system
        if default_from_system and not suggestion:
            suggestions = self.load_system_suggestions()
            if field_type == 'datetime' or 'time' in name.lower():
                suggestion = suggestions.get('datetime') or suggestions.get('user_local_time')
            elif field_type == 'date':
                suggestion = suggestions.get('date') or suggestions.get('user_date')
            elif field_type == 'time':
                suggestion = suggestions.get('time') or datetime.now().strftime("%H:%M")

        # Render field with suggestion
        self._maybe_clear_screen()
        print(self.render_field(field, suggestion))

        # Get input
        if suggestion:
            print(f"\n{Colors.BRIGHT_CYAN}❯{Colors.RESET} ", end="", flush=True)
            raw_input = input()
            user_input = self._clean_input(raw_input)

            # If user just pressed Enter/Tab with suggestion, use it
            if not user_input and suggestion:
                print(f"  {Colors.GREEN}✓{Colors.RESET}")
                return suggestion
        else:
            print(f"\n{Colors.BRIGHT_CYAN}❯{Colors.RESET} ", end="", flush=True)
            raw_input = input()
            user_input = self._clean_input(raw_input)

        # Handle empty input
        if not user_input:
            if required:
                print(f"  {Colors.RED}✗ Required field{Colors.RESET}")
                return self.collect_field_input(field, suggestion)
            else:
                print(f"  {Colors.DIM}(Skipped){Colors.RESET}")
                return None

        # Validate input
        is_valid, error = self.validate_field(field_type, user_input, validation, name)
        if not is_valid:
            print(f"  {Colors.RED}✗ {error}{Colors.RESET}")
            return self.collect_field_input(field, suggestion)

        print(f"  {Colors.GREEN}✓{Colors.RESET}")
        return user_input

    def validate_field(self, field_type: str, value: str, validation: Optional[str] = None, field_name: str = '') -> Tuple[bool, str]:
        """Validate field input with enhanced rules using FormFieldValidator.

        Args:
            field_type: Type of field (text, email, date, password, etc.)
            value: Value to validate
            validation: Optional validation rule (name, date, email, etc.)
            field_name: Optional field name for context-aware validation

        Returns:
            Tuple of (valid: bool, message: str)
        """
        if not value:
            return False, "Cannot be empty"

        # Use specialized validators for known field types
        try:
            from core.tui.form_field_validator import FormFieldValidator

            # Detect field type from name
            if 'username' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_username(value)
                return is_valid, error or "Valid"

            elif 'dob' in field_name.lower() or 'birth' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_dob(value)
                return is_valid, error or "Valid"

            elif 'timezone' in field_name.lower() or 'tz' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_timezone(value)
                return is_valid, error or "Valid"

            elif 'location' in field_name.lower() or 'city' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_location(value)
                return is_valid, error or "Valid"

            elif 'role' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_role(value)
                return is_valid, error or "Valid"

            elif 'os' in field_name.lower() or 'operating' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_os_type(value)
                return is_valid, error or "Valid"

            elif 'password' in field_name.lower() or 'pwd' in field_name.lower():
                is_valid, error = FormFieldValidator.validate_password(value)
                return is_valid, error or "Valid"

        except ImportError:
            logger.debug("FormFieldValidator not available, using basic validation")

        # Type-specific validation fallback
        if field_type == 'email':
            if '@' not in value or '.' not in value:
                return False, "Invalid email format"

        elif field_type == 'date':
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return False, "Use YYYY-MM-DD format"

        elif field_type == 'datetime':
            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M")
            except ValueError:
                return False, "Use YYYY-MM-DD HH:MM format"

        elif field_type == 'number':
            try:
                float(value)
            except ValueError:
                return False, "Must be a number"

        elif field_type == 'password':
            if len(value) < 8:
                return False, "Password must be at least 8 characters"

        # Custom validation rules
        if validation:
            if validation == 'name':
                if len(value) < 2:
                    return False, "Name too short"
                if any(c.isdigit() for c in value):
                    return False, "Name cannot contain numbers"

            elif validation == 'date':
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    return False, "Use YYYY-MM-DD format (e.g., 1990-01-15)"

            elif validation == 'text':
                if len(value) < 1:
                    return False, "Cannot be empty"

        return True, "Valid"

    def _collect_select_field(self, field: Dict, suggestion: Optional[str] = None) -> Optional[str]:
        """Collect input for a select field with numbered menu.

        Args:
            field: Field definition with options
            suggestion: Optional suggested value

        Returns:
            Selected option value or None
        """
        label = field.get('label', field.get('name', 'Select'))
        options = field.get('options', [])
        required = field.get('required', False)

        if not options:
            logger.warning(f"[LOCAL] Select field '{label}' has no options")
            return None

        # Display label and options
        self._maybe_clear_screen()
        print(f"\n{Colors.BOLD}* {label}:{Colors.RESET}")
        for idx, option in enumerate(options, start=1):
            # Highlight suggestion
            if suggestion and option == suggestion:
                print(f"  {Colors.BRIGHT_GREEN}{idx}. {option} ← (default){Colors.RESET}")
            else:
                print(f"  {idx}. {option}")

        # Get choice
        print(f"\n{Colors.DIM}Choose 1-{len(options)}" + (f" or Enter for default" if suggestion else "") + f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}❯{Colors.RESET} ", end="", flush=True)
        raw_input = input()
        user_input = self._clean_input(raw_input)

        # Accept Enter for default
        if not user_input and suggestion:
            print(f"  {Colors.GREEN}✓{Colors.RESET}")
            return suggestion

        # Handle numeric choice
        try:
            choice = int(user_input)
            if 1 <= choice <= len(options):
                print(f"  {Colors.GREEN}✓{Colors.RESET}")
                return options[choice - 1]
            else:
                print(f"  {Colors.RED}✗ Choose a number between 1 and {len(options)}{Colors.RESET}")
                return self._collect_select_field(field, suggestion)
        except ValueError:
            # Check if they typed the option name
            for option in options:
                if user_input.lower() == option.lower():
                    print(f"  {Colors.GREEN}✓{Colors.RESET}")
                    return option

            if required:
                print(f"  {Colors.RED}✗ Invalid choice. Enter a number 1-{len(options)}{Colors.RESET}")
                return self._collect_select_field(field, suggestion)
            else:
                print(f"  {Colors.DIM}(Skipped){Colors.RESET}")
                return None

    # ========================================================================
    # FORM SUMMARY & CONFIRMATION
    # ========================================================================

    def render_form_summary(self, collected: Dict, form_fields: List[Dict]) -> str:
        """Render a summary of collected form data.

        Args:
            collected: Dictionary of field names to values
            form_fields: List of original field definitions

        Returns:
            Formatted summary string
        """
        lines = [f"\n{Colors.BOLD}📋 FORM SUMMARY:{Colors.RESET}\n"]

        for field in form_fields:
            name = field.get('name')
            label = field.get('label')
            value = collected.get(name, '(not provided)')

            # Mask sensitive fields
            if field.get('type') == 'password':
                value = '••••••••' if value != '(not provided)' else value

            lines.append(f"  {Colors.BRIGHT_CYAN}{label}:{Colors.RESET}")
            lines.append(f"    {Colors.GREEN}{value}{Colors.RESET}")

        lines.append("")
        return "\n".join(lines)

    def confirm_and_save(self, collected: Dict) -> bool:
        """Get user confirmation before saving form data.

        Args:
            collected: Collected form data

        Returns:
            True if user confirms, False otherwise
        """
        print(f"\n{Colors.BOLD}Ready to save?{Colors.RESET}")
        print(f"{Colors.DIM}(y/n):{Colors.RESET} ", end="", flush=True)
        response = input().lower().strip()

        if response in {'y', 'yes', 'ok'}:
            return True
        else:
            print(f"{Colors.YELLOW}Setup cancelled.{Colors.RESET}")
            return False

    # ========================================================================
    # ACCESSIBILITY & TERMINAL CONTROL
    # ========================================================================

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        import os
        os.system('clear' if os.name != 'nt' else 'cls')

    def disable_colors(self) -> None:
        """Disable ANSI colors for piped output or non-TTY terminals."""
        Colors.disable()
        logger.debug("[LOCAL] ANSI colors disabled")

    def check_terminal_supports_colors(self) -> bool:
        """Check if terminal supports ANSI colors.

        Returns:
            True if colors are supported, False otherwise
        """
        try:
            interactive, reason = interactive_tty_status()
            if not interactive:
                logger.debug("[LOCAL] ANSI color support skipped: %s", reason)
                return False

            import os
            if os.environ.get('NO_COLOR'):
                return False

            return True
        except Exception as exc:
            logger.debug("[LOCAL] ANSI color check failed: %s", exc)
            return False

    def _is_interactive(self) -> bool:
        """Check if running in interactive terminal."""
        try:
            interactive, reason = interactive_tty_status()
            if not interactive and reason:
                logger.debug("[LOCAL] Interactive check failed: %s", reason)
            return interactive
        except Exception:
            return False

    def _collect_field_input_fallback(self, field: Dict, suggestion: Optional[str] = None) -> Optional[str]:
        """Fallback field input collection using basic input().

        Used when terminal is non-interactive.

        Args:
            field: Field definition
            suggestion: Optional suggested value

        Returns:
            User input or None if skipped
        """
        name = field.get('name', 'unknown')
        label = field.get('label', name)
        required = field.get('required', False)

        # Print field label
        req_label = "*" if required else " "
        print(f"\n{req_label} {label}:")

        # Show suggestion if available
        if suggestion:
            print(f"  Suggestion: {suggestion}")
            print(f"  (Press Enter to accept, or type to override)")

        # Get input using basic input()
        try:
            user_input = input("> ").strip()

            # If user just pressed Enter with suggestion, use it
            if not user_input and suggestion:
                return suggestion

            # Handle empty input
            if not user_input:
                if required:
                    print(f"  (Required field)")
                    return self._collect_field_input_fallback(field, suggestion)
                else:
                    print(f"  (Skipped)")
                    return None

            return user_input
        except EOFError:
            # Handle EOF (pipe/redirect)
            if suggestion:
                logger.debug("[LOCAL] EOF detected, using suggestion for %s", name)
                return suggestion
            if not required:
                logger.debug("[LOCAL] EOF detected, skipping optional field %s", name)
                return None
            logger.warning("[LOCAL] EOF in required field %s", name)
            return None
        except Exception as e:
            logger.warning("[LOCAL] Fallback field input failed for %s: %s", name, e)
            return None

    def _maybe_clear_screen(self) -> None:
        """Clear screen between questions to avoid overlapping prompts."""
        if not self.use_typeform_layout:
            return
        try:
            interactive, _ = interactive_tty_status()
            if interactive:
                # ANSI clear for tighter control
                sys.stdout.write('\033[2J\033[H')
                sys.stdout.flush()
        except Exception:
            return

    def _setup_terminal_raw(self) -> bool:
        """Configure terminal for raw key capture."""
        try:
            interactive, _ = interactive_tty_status()
            if not interactive:
                return False
            self._terminal_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            return True
        except Exception as exc:
            logger.debug("[LOCAL] Raw terminal setup failed: %s", exc)
            return False

    def _restore_terminal_raw(self) -> None:
        """Restore terminal settings after raw capture."""
        if not self._terminal_settings:
            return
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._terminal_settings)
        except Exception as exc:
            logger.debug("[LOCAL] Raw terminal restore failed: %s", exc)
        finally:
            self._terminal_settings = None

    def _read_key(self) -> str:
        """Read a single key with arrow-key support."""
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Escape sequence
            next_ch = sys.stdin.read(1)
            if next_ch == '[':
                arrow = sys.stdin.read(1)
                if arrow == 'A':
                    return 'up'
                if arrow == 'B':
                    return 'down'
                if arrow == 'C':
                    return 'right'
                if arrow == 'D':
                    return 'left'
            return '\x1b'
        return ch

    def _collect_datepicker_field(self, field: Dict, suggestion: Optional[str] = None) -> Optional[str]:
        """Collect input for a date field using the TUI DatePicker."""
        if not self._is_interactive():
            return self._collect_field_input_fallback(field, suggestion)

        label = field.get('label', field.get('name', 'Date'))
        default = suggestion or field.get('default')
        picker = DatePicker(label, default=default)

        if not self._setup_terminal_raw():
            return self._collect_field_input_fallback(field, suggestion)

        try:
            while True:
                self._maybe_clear_screen()
                print(picker.render(), end='', flush=True)
                key = self._read_key()
                if key == '\x1b':
                    # Escape cancels
                    return None
                result = picker.handle_input(key)
                if result:
                    return result
        finally:
            self._restore_terminal_raw()



# Singleton instance
_form_handler = None


def get_form_handler() -> AdvancedFormField:
    """Get singleton form handler instance."""
    global _form_handler
    if _form_handler is None:
        _form_handler = AdvancedFormField()
        # Disable colors if terminal doesn't support them
        if not _form_handler.check_terminal_supports_colors():
            _form_handler.disable_colors()
    return _form_handler
