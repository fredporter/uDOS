"""
uDOS v1.0.13 - Dynamic Theme Manager
Provides dynamic color themes, accessibility support, customizable color schemes,
and full JSON theme management with preview, import/export, and validation.

Enhanced in v1.0.13 with:
- Full JSON theme loading and management
- Theme preview before applying
- Import/export (.udostheme format)
- Theme validation and safety checks
- Theme comparison and statistics

Version: 1.0.13 (Enhanced from v1.0.6)
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class ThemeMode(Enum):
    """Theme modes for different accessibility needs."""
    CLASSIC = "classic"
    CYBERPUNK = "cyberpunk"
    ACCESSIBILITY = "accessibility"
    MONOCHROME = "monochrome"
    CUSTOM = "custom"


@dataclass
class ThemeMetadata:
    """Metadata for a full JSON theme."""
    name: str
    version: str
    style: str
    description: str
    icon: str
    author: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class ColorScheme:
    """Color scheme definition for terminal output."""
    # Basic colors
    primary: str = "\033[94m"      # Blue
    secondary: str = "\033[92m"    # Green
    accent: str = "\033[93m"       # Yellow
    error: str = "\033[91m"        # Red
    warning: str = "\033[93m"      # Yellow
    success: str = "\033[92m"      # Green
    info: str = "\033[96m"         # Cyan

    # Text colors
    text_primary: str = "\033[97m"    # Bright White
    text_secondary: str = "\033[37m"  # White
    text_muted: str = "\033[90m"      # Dark Gray

    # UI elements
    border: str = "\033[94m"          # Blue
    highlight: str = "\033[103m"      # Yellow background
    selection: str = "\033[106m"      # Cyan background

    # Reset and special
    reset: str = "\033[0m"
    bold: str = "\033[1m"
    dim: str = "\033[2m"
    italic: str = "\033[3m"
    underline: str = "\033[4m"

    # Accessibility
    high_contrast_bg: str = "\033[40m"  # Black background
    high_contrast_fg: str = "\033[97m"  # Bright white text


class ThemeManager:
    """
    Advanced theme management with accessibility features and dynamic switching.
    """

    def __init__(self):
        """Initialize theme manager with default settings."""
        self.current_mode = ThemeMode.CLASSIC
        self.custom_themes = {}
        self.accessibility_mode = False
        self.high_contrast_mode = False
        self.colorblind_mode = None  # None, 'deuteranopia', 'protanopia', 'tritanopia'

        # Theme storage
        self.themes_dir = Path("memory/themes")
        self.themes_dir.mkdir(parents=True, exist_ok=True)

        # JSON theme storage (v1.0.13+)
        self.json_themes_dir = Path("data/themes")
        self.json_themes_cache = {}
        self.available_json_themes = self._scan_json_themes()

        # Load custom themes
        self._load_custom_themes()

        # Initialize predefined themes
        self._init_predefined_themes()

    def _init_predefined_themes(self):
        """Initialize predefined color themes."""
        self.predefined_themes = {
            ThemeMode.CLASSIC: ColorScheme(
                primary="\033[94m",      # Blue
                secondary="\033[92m",    # Green
                accent="\033[93m",       # Yellow
                error="\033[91m",        # Red
                warning="\033[93m",      # Yellow
                success="\033[92m",      # Green
                info="\033[96m",         # Cyan
                text_primary="\033[97m", # Bright White
                text_secondary="\033[37m", # White
                text_muted="\033[90m",   # Dark Gray
                border="\033[94m",       # Blue
                highlight="\033[103m",   # Yellow bg
                selection="\033[106m"    # Cyan bg
            ),

            ThemeMode.CYBERPUNK: ColorScheme(
                primary="\033[95m",      # Magenta
                secondary="\033[96m",    # Cyan
                accent="\033[92m",       # Green
                error="\033[91m",        # Red
                warning="\033[93m",      # Yellow
                success="\033[92m",      # Green
                info="\033[96m",         # Cyan
                text_primary="\033[97m", # Bright White
                text_secondary="\033[95m", # Magenta
                text_muted="\033[90m",   # Dark Gray
                border="\033[95m",       # Magenta
                highlight="\033[105m",   # Magenta bg
                selection="\033[106m"    # Cyan bg
            ),

            ThemeMode.ACCESSIBILITY: ColorScheme(
                primary="\033[94m",      # Blue (colorblind safe)
                secondary="\033[93m",    # Yellow (colorblind safe)
                accent="\033[97m",       # Bright White
                error="\033[91m",        # Red
                warning="\033[93m",      # Yellow
                success="\033[92m",      # Green
                info="\033[96m",         # Cyan
                text_primary="\033[97m", # Bright White
                text_secondary="\033[37m", # White
                text_muted="\033[37m",   # White (higher contrast)
                border="\033[97m",       # Bright White
                highlight="\033[43m\033[30m",   # Yellow bg, black text
                selection="\033[47m\033[30m",   # White bg, black text
                high_contrast_bg="\033[40m",    # Black bg
                high_contrast_fg="\033[97m"     # Bright white fg
            ),

            ThemeMode.MONOCHROME: ColorScheme(
                primary="\033[97m",      # Bright White
                secondary="\033[37m",    # White
                accent="\033[1m",        # Bold
                error="\033[91m",        # Red (only color kept)
                warning="\033[93m",      # Yellow (only color kept)
                success="\033[37m",      # White
                info="\033[37m",         # White
                text_primary="\033[97m", # Bright White
                text_secondary="\033[37m", # White
                text_muted="\033[90m",   # Dark Gray
                border="\033[37m",       # White
                highlight="\033[7m",     # Reverse video
                selection="\033[7m"      # Reverse video
            )
        }

    def get_current_scheme(self) -> ColorScheme:
        """Get the currently active color scheme."""
        if self.current_mode == ThemeMode.CUSTOM and self.custom_themes:
            custom_name = list(self.custom_themes.keys())[0]
            return self.custom_themes[custom_name]
        return self.predefined_themes.get(self.current_mode, self.predefined_themes[ThemeMode.CLASSIC])

    def set_theme(self, mode: ThemeMode) -> bool:
        """
        Set the active theme mode.

        Args:
            mode: Theme mode to activate

        Returns:
            True if successful, False otherwise
        """
        if mode in self.predefined_themes or (mode == ThemeMode.CUSTOM and self.custom_themes):
            self.current_mode = mode
            self._save_settings()
            return True
        return False

    def enable_accessibility_mode(self, enable: bool = True):
        """Enable or disable accessibility mode."""
        self.accessibility_mode = enable
        if enable:
            self.current_mode = ThemeMode.ACCESSIBILITY
        self._save_settings()

    def enable_high_contrast_mode(self, enable: bool = True):
        """Enable or disable high contrast mode."""
        self.high_contrast_mode = enable
        self._save_settings()

    def set_colorblind_support(self, colorblind_type: Optional[str] = None):
        """
        Set colorblind support mode.

        Args:
            colorblind_type: 'deuteranopia', 'protanopia', 'tritanopia', or None
        """
        valid_types = ['deuteranopia', 'protanopia', 'tritanopia']
        if colorblind_type is None or colorblind_type in valid_types:
            self.colorblind_mode = colorblind_type
            if colorblind_type:
                self.current_mode = ThemeMode.ACCESSIBILITY
            self._save_settings()
            return True
        return False

    def create_custom_theme(self, name: str, scheme: ColorScheme) -> bool:
        """
        Create a custom theme.

        Args:
            name: Theme name
            scheme: Color scheme definition

        Returns:
            True if successful, False otherwise
        """
        if not name or not isinstance(scheme, ColorScheme):
            return False

        self.custom_themes[name] = scheme
        self._save_custom_theme(name, scheme)
        return True

    def list_available_themes(self) -> Dict[str, str]:
        """
        List all available themes with descriptions.

        Returns:
            Dictionary of theme names and descriptions
        """
        themes = {
            "classic": "🎨 Classic uDOS theme with blue/green accents",
            "cyberpunk": "🌆 Cyberpunk theme with magenta/cyan neon colors",
            "accessibility": "♿ High contrast theme for accessibility",
            "monochrome": "⚫ Monochrome theme for terminal compatibility"
        }

        for name in self.custom_themes:
            themes[f"custom-{name}"] = f"🎯 Custom theme: {name}"

        return themes

    def format_text(self, text: str, style: str = "primary") -> str:
        """
        Format text with current theme colors.

        Args:
            text: Text to format
            style: Style name (primary, error, success, etc.)

        Returns:
            Formatted text with ANSI codes
        """
        scheme = self.get_current_scheme()

        # Apply accessibility modifications
        if self.high_contrast_mode:
            if style in ['error', 'warning']:
                return f"{scheme.high_contrast_bg}{scheme.high_contrast_fg}{text}{scheme.reset}"

        # Get color for style
        color = getattr(scheme, style, scheme.primary)

        # Apply colorblind adjustments
        if self.colorblind_mode:
            color = self._adjust_for_colorblind(color, style)

        return f"{color}{text}{scheme.reset}"

    def format_command_output(self, command: str, output: str) -> str:
        """
        Format command output with syntax highlighting.

        Args:
            command: Command that was executed
            output: Command output to format

        Returns:
            Formatted output with appropriate colors
        """
        scheme = self.get_current_scheme()

        # Different formatting for different command types
        if command.upper().startswith('ERROR'):
            return self.format_text(output, 'error')
        elif command.upper().startswith('SUCCESS'):
            return self.format_text(output, 'success')
        elif command.upper().startswith('WARNING'):
            return self.format_text(output, 'warning')
        elif command.upper().startswith('INFO'):
            return self.format_text(output, 'info')
        else:
            return self.format_text(output, 'text_primary')

    def format_table(self, headers: list, rows: list) -> str:
        """
        Format a table with theme colors.

        Args:
            headers: Table headers
            rows: Table rows

        Returns:
            Formatted table string
        """
        scheme = self.get_current_scheme()

        # Calculate column widths
        if not rows:
            return ""

        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Format table
        result = []

        # Headers
        header_row = "│ "
        for i, header in enumerate(headers):
            header_row += self.format_text(str(header).ljust(col_widths[i]), 'accent')
            header_row += f"{scheme.reset} │ "
        result.append(self.format_text("┌" + "─" * (len(header_row) - 6) + "┐", 'border'))
        result.append(header_row)
        result.append(self.format_text("├" + "─" * (len(header_row) - 6) + "┤", 'border'))

        # Rows
        for row in rows:
            data_row = "│ "
            for i, cell in enumerate(row):
                data_row += self.format_text(str(cell).ljust(col_widths[i]), 'text_primary')
                data_row += f"{scheme.reset} │ "
            result.append(data_row)

        result.append(self.format_text("└" + "─" * (len(header_row) - 6) + "┘", 'border'))

        return "\n".join(result)

    def _adjust_for_colorblind(self, color: str, style: str) -> str:
        """Adjust colors for colorblind users."""
        if not self.colorblind_mode:
            return color

        # Simplified colorblind adjustments
        if self.colorblind_mode in ['deuteranopia', 'protanopia']:
            # Red-green colorblind - use blue/yellow palette
            if style in ['error', 'success']:
                return "\033[94m"  # Blue for both
            elif style == 'warning':
                return "\033[93m"  # Yellow
        elif self.colorblind_mode == 'tritanopia':
            # Blue-yellow colorblind - use red/green palette
            if style in ['info', 'accent']:
                return "\033[92m"  # Green

        return color

    def _load_custom_themes(self):
        """Load custom themes from disk."""
        custom_themes_file = self.themes_dir / "custom_themes.json"
        if custom_themes_file.exists():
            try:
                with open(custom_themes_file, 'r') as f:
                    data = json.load(f)
                    for name, scheme_data in data.items():
                        scheme = ColorScheme(**scheme_data)
                        self.custom_themes[name] = scheme
            except Exception:
                pass  # Graceful fallback

    def _save_custom_theme(self, name: str, scheme: ColorScheme):
        """Save a custom theme to disk."""
        custom_themes_file = self.themes_dir / "custom_themes.json"

        # Load existing
        data = {}
        if custom_themes_file.exists():
            try:
                with open(custom_themes_file, 'r') as f:
                    data = json.load(f)
            except Exception:
                pass

        # Add new theme
        data[name] = {
            'primary': scheme.primary,
            'secondary': scheme.secondary,
            'accent': scheme.accent,
            'error': scheme.error,
            'warning': scheme.warning,
            'success': scheme.success,
            'info': scheme.info,
            'text_primary': scheme.text_primary,
            'text_secondary': scheme.text_secondary,
            'text_muted': scheme.text_muted,
            'border': scheme.border,
            'highlight': scheme.highlight,
            'selection': scheme.selection,
            'reset': scheme.reset,
            'bold': scheme.bold,
            'dim': scheme.dim,
            'italic': scheme.italic,
            'underline': scheme.underline
        }

        # Save
        try:
            with open(custom_themes_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Graceful fallback

    def _save_settings(self):
        """Save theme settings to disk."""
        settings_file = self.themes_dir / "settings.json"
        settings = {
            'current_mode': self.current_mode.value,
            'accessibility_mode': self.accessibility_mode,
            'high_contrast_mode': self.high_contrast_mode,
            'colorblind_mode': self.colorblind_mode
        }

        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass  # Graceful fallback

    def load_settings(self):
        """Load theme settings from disk."""
        settings_file = self.themes_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_mode = ThemeMode(settings.get('current_mode', 'classic'))
                    self.accessibility_mode = settings.get('accessibility_mode', False)
                    self.high_contrast_mode = settings.get('high_contrast_mode', False)
                    self.colorblind_mode = settings.get('colorblind_mode', None)
            except Exception:
                pass  # Graceful fallback

    def get_theme_info(self) -> Dict:
        """Get current theme information."""
        return {
            'current_mode': self.current_mode.value,
            'accessibility_mode': self.accessibility_mode,
            'high_contrast_mode': self.high_contrast_mode,
            'colorblind_mode': self.colorblind_mode,
            'available_themes': list(self.list_available_themes().keys()),
            'custom_themes_count': len(self.custom_themes),
            'json_themes_count': len(self.available_json_themes)
        }

    # ==================== JSON Theme Management (v1.0.13+) ====================

    def _scan_json_themes(self) -> List[str]:
        """Scan data/themes directory for JSON theme files."""
        themes = []
        if not self.json_themes_dir.exists():
            return themes

        for file in self.json_themes_dir.glob("*.json"):
            # Skip special files
            if file.name.startswith('_'):
                continue
            theme_name = file.stem
            themes.append(theme_name)

        return sorted(themes)

    def load_json_theme(self, theme_name: str) -> Optional[Dict]:
        """
        Load a full JSON theme by name.

        Args:
            theme_name: Name of theme (without .json extension)

        Returns:
            Theme data dict or None if not found
        """
        # Check cache first
        if theme_name in self.json_themes_cache:
            return self.json_themes_cache[theme_name]

        theme_file = self.json_themes_dir / f"{theme_name}.json"
        if not theme_file.exists():
            return None

        try:
            with open(theme_file, 'r') as f:
                theme_data = json.load(f)
                # Cache the theme
                self.json_themes_cache[theme_name] = theme_data
                return theme_data
        except Exception as e:
            print(f"Error loading theme '{theme_name}': {e}")
            return None

    def validate_json_theme(self, theme_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate full JSON theme structure.

        Args:
            theme_data: Theme data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required top-level fields
        required_fields = ["THEME_NAME", "VERSION", "NAME", "STYLE", "DESCRIPTION"]
        for field in required_fields:
            if field not in theme_data:
                errors.append(f"Missing required field: {field}")

        # Check required sections
        required_sections = ["CORE_SYSTEM", "CORE_USER", "TERMINOLOGY"]
        for section in required_sections:
            if section not in theme_data:
                errors.append(f"Missing required section: {section}")

        # Validate TERMINOLOGY section
        if "TERMINOLOGY" in theme_data:
            term = theme_data["TERMINOLOGY"]
            basic_commands = ["CMD_CATALOG", "CMD_LOAD", "CMD_SAVE", "CMD_HELP"]
            for cmd in basic_commands:
                if cmd not in term:
                    errors.append(f"Missing terminology for: {cmd}")

        return (len(errors) == 0, errors)

    def get_json_theme_metadata(self, theme_name: str) -> Optional[ThemeMetadata]:
        """
        Extract metadata from a JSON theme.

        Args:
            theme_name: Name of theme

        Returns:
            ThemeMetadata object or None
        """
        theme_data = self.load_json_theme(theme_name)
        if not theme_data:
            return None

        return ThemeMetadata(
            name=theme_data.get("THEME_NAME", theme_name.upper()),
            version=theme_data.get("VERSION", "1.0.0"),
            style=theme_data.get("STYLE", "Unknown"),
            description=theme_data.get("DESCRIPTION", "No description"),
            icon=theme_data.get("ICON", "🎨"),
            author=theme_data.get("AUTHOR"),
            created=theme_data.get("CREATED"),
            modified=theme_data.get("MODIFIED"),
            tags=theme_data.get("TAGS", [])
        )

    def list_json_themes(self, detailed: bool = False) -> str:
        """
        List all available JSON themes.

        Args:
            detailed: Include detailed information

        Returns:
            Formatted string of themes
        """
        output = []
        output.append("\n╔═══════════════════════════════════════════════════════════╗")
        output.append("║              AVAILABLE JSON THEMES                        ║")
        output.append("╚═══════════════════════════════════════════════════════════╝\n")

        if not self.available_json_themes:
            output.append("  No themes found.\n")
            return "\n".join(output)

        for theme_name in self.available_json_themes:
            metadata = self.get_json_theme_metadata(theme_name)
            if not metadata:
                continue

            if detailed:
                output.append(f"  {metadata.icon} {metadata.name}")
                output.append(f"     Style: {metadata.style}")
                output.append(f"     Description: {metadata.description}")
                output.append(f"     Version: {metadata.version}")
                if metadata.author:
                    output.append(f"     Author: {metadata.author}")
                output.append("")
            else:
                output.append(f"  {metadata.icon} {theme_name:<15} - {metadata.description}")

        return "\n".join(output)

    def preview_json_theme(self, theme_name: str) -> str:
        """
        Generate a preview of a JSON theme without applying it.

        Args:
            theme_name: Name of theme to preview

        Returns:
            Formatted preview string
        """
        theme_data = self.load_json_theme(theme_name)
        if not theme_data:
            return f"Error: Theme '{theme_name}' not found"

        metadata = self.get_json_theme_metadata(theme_name)
        output = []

        output.append("\n╔═══════════════════════════════════════════════════════════╗")
        output.append(f"║  {metadata.icon} THEME PREVIEW: {metadata.name.upper().center(40)} ║")
        output.append("╚═══════════════════════════════════════════════════════════╝\n")

        # Preview system prompt
        if "CORE_SYSTEM" in theme_data:
            core = theme_data["CORE_SYSTEM"]
            prompt = core.get("PROMPT_BASE", ">")
            system_name = core.get("SYSTEM_NAME", "SYSTEM")
            output.append(f"  System Prompt: {prompt}")
            output.append(f"  System Name: {system_name}")
            output.append("")

        # Preview user settings
        if "CORE_USER" in theme_data:
            user = theme_data["CORE_USER"]
            output.append("  User Configuration:")
            output.append(f"    Name: {user.get('USER_NAME', 'User')}")
            output.append(f"    Title: {user.get('USER_TITLE', 'N/A')}")
            output.append(f"    Location: {user.get('USER_LOCATION', 'Unknown')}")
            output.append(f"    Project: {user.get('USER_PROJECT', 'None')}")
            output.append("")

        # Preview terminology
        if "TERMINOLOGY" in theme_data:
            term = theme_data["TERMINOLOGY"]
            output.append("  Command Terminology:")
            term_examples = [
                ("CMD_CATALOG", "List"),
                ("CMD_LOAD", "Open"),
                ("CMD_SAVE", "Save"),
                ("CMD_HELP", "Help"),
                ("CMD_CLS", "Clear")
            ]
            for cmd_key, default in term_examples:
                cmd_value = term.get(cmd_key, default)
                output.append(f"    {cmd_key}: {cmd_value}")
            output.append("")

        # Show character theme if present
        if "CHARACTER_TYPES" in theme_data:
            char = theme_data["CHARACTER_TYPES"]
            output.append("  Character Theme:")
            output.append(f"    Name: {char.get('CHARACTER_NAME', 'Character')}")
            output.append(f"    Class: {char.get('CHARACTER_CLASS', 'User')}")
            output.append("")

        output.append("  " + "─" * 59)
        output.append(f"  Validation: ", end="")
        is_valid, errors = self.validate_json_theme(theme_data)
        output.append("✅ VALID" if is_valid else "❌ INVALID")
        output.append("")

        return "\n".join(output)

    def export_json_theme(self, theme_name: str, output_path: str) -> bool:
        """
        Export a JSON theme to a .udostheme file.

        Args:
            theme_name: Name of theme to export
            output_path: Path to save exported theme

        Returns:
            True if successful, False otherwise
        """
        theme_data = self.load_json_theme(theme_name)
        if not theme_data:
            print(f"Error: Theme '{theme_name}' not found")
            return False

        # Add export metadata
        export_data = theme_data.copy()
        export_data["EXPORTED"] = datetime.now().isoformat()
        export_data["UDOS_VERSION"] = "1.0.13"
        export_data["FORMAT_VERSION"] = "1.0"

        try:
            output_file = Path(output_path)
            # Ensure .udostheme extension
            if output_file.suffix != '.udostheme':
                output_file = output_file.with_suffix('.udostheme')

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"✅ Theme exported to: {output_file}")
            return True

        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False

    def import_json_theme(self, import_path: str, theme_name: Optional[str] = None) -> bool:
        """
        Import a theme from a .udostheme file.

        Args:
            import_path: Path to .udostheme file
            theme_name: Optional custom name for imported theme

        Returns:
            True if successful, False otherwise
        """
        import_file = Path(import_path)
        if not import_file.exists():
            print(f"Error: File not found: {import_path}")
            return False

        try:
            with open(import_file, 'r') as f:
                theme_data = json.load(f)

            # Validate imported theme
            is_valid, errors = self.validate_json_theme(theme_data)
            if not is_valid:
                print(f"Error: Invalid theme file:")
                for error in errors:
                    print(f"  - {error}")
                return False

            # Determine theme name
            if theme_name:
                final_name = theme_name
            else:
                final_name = theme_data.get("THEME_NAME", import_file.stem).lower()

            # Check for conflicts
            target_file = self.json_themes_dir / f"{final_name}.json"
            if target_file.exists():
                print(f"Warning: Theme '{final_name}' already exists")
                # In non-interactive mode, just skip
                print("Import cancelled (theme already exists)")
                return False

            # Save imported theme
            with open(target_file, 'w') as f:
                json.dump(theme_data, f, indent=2)

            # Update available themes list
            if final_name not in self.available_json_themes:
                self.available_json_themes.append(final_name)
                self.available_json_themes.sort()

            print(f"✅ Theme imported as: {final_name}")
            return True

        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in import file: {e}")
            return False
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False

    def get_json_theme_stats(self) -> str:
        """
        Get statistics about available JSON themes.

        Returns:
            Formatted statistics string
        """
        output = []
        output.append("\n╔═══════════════════════════════════════════════════════════╗")
        output.append("║                  JSON THEME STATISTICS                    ║")
        output.append("╚═══════════════════════════════════════════════════════════╝\n")

        output.append(f"  Total JSON Themes: {len(self.available_json_themes)}")
        output.append(f"  Themes Cached: {len(self.json_themes_cache)}")
        output.append(f"  Themes Directory: {self.json_themes_dir}")
        output.append("")

        # Count themes by style/type
        styles = {}
        for theme_name in self.available_json_themes:
            metadata = self.get_json_theme_metadata(theme_name)
            if metadata:
                style = metadata.style.split('/')[0].strip() if '/' in metadata.style else metadata.style
                styles[style] = styles.get(style, 0) + 1

        if styles:
            output.append("  Themes by Style:")
            for style, count in sorted(styles.items()):
                output.append(f"    {style}: {count}")

        return "\n".join(output)
