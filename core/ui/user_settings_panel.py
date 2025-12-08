"""
User Settings Panel (v1.2.18)

Manage user-specific preferences separate from CONFIG.
Theme selection, TUI preferences, workspace defaults.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from core.config import Config


class UserSettingsPanel:
    """
    Panel for user-specific settings.
    
    Features:
    - Theme selection (list available themes)
    - TUI preferences (keypad, pager, browser)
    - Default workspaces
    - Keypad key customization
    - Per-user storage in memory/system/user/
    """
    
    # Available setting sections
    SECTIONS = {
        'appearance': ['theme', 'use_color', 'show_hints', 'panel_style'],
        'tui': ['keypad_enabled', 'pager_enabled', 'browser_columns', 'autocomplete_enabled'],
        'workspace': ['default_workspace', 'auto_restore_workspace', 'recent_files_count'],
        'behavior': ['auto_save', 'confirmation_prompts', 'sound_enabled']
    }
    
    def __init__(self):
        """Initialize user settings panel"""
        self.config = Config()
        
        # User settings storage
        from core.utils.paths import PATHS
        self.settings_file = PATHS.MEMORY_SYSTEM_USER / "user_settings.json"
        
        # Load user settings
        self.user_settings = self._load_settings()
        
        # UI state
        self.current_section = 'appearance'
        self.selected_index = 0
        self.editing_key = None
        self.edit_buffer = None
        self.modified = False
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load user settings from disk"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Return defaults
        return {
            'theme': 'foundation',
            'use_color': True,
            'show_hints': True,
            'panel_style': 'bordered',
            'keypad_enabled': False,
            'pager_enabled': True,
            'browser_columns': 1,
            'autocomplete_enabled': True,
            'default_workspace': 'memory/ucode/scripts/',
            'auto_restore_workspace': False,
            'recent_files_count': 10,
            'auto_save': True,
            'confirmation_prompts': True,
            'sound_enabled': False
        }
    
    def _save_settings(self) -> Dict[str, Any]:
        """Save user settings to disk"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.user_settings, f, indent=2)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def render(self) -> str:
        """Render user settings panel"""
        output = []
        
        # Header
        modified_indicator = " *modified*" if self.modified else ""
        output.append(f"╔══ USER SETTINGS ══╗{modified_indicator}")
        output.append("")
        
        # Section tabs
        output.append(self._render_section_tabs())
        output.append("=" * 70)
        output.append("")
        
        # Settings list
        output.extend(self._render_settings())
        
        # Footer
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_section_tabs(self) -> str:
        """Render section tabs"""
        tabs = []
        for section in self.SECTIONS.keys():
            if section == self.current_section:
                tabs.append(f"[{section.upper()}]")
            else:
                tabs.append(f" {section} ")
        
        return "  |  ".join(tabs)
    
    def _render_settings(self) -> List[str]:
        """Render settings for current section"""
        output = []
        
        # Get settings for current section
        section_keys = self.SECTIONS.get(self.current_section, [])
        
        if not section_keys:
            output.append("  (No settings in this section)")
            return output
        
        # Render each setting
        for i, key in enumerate(section_keys):
            value = self.user_settings.get(key, '(not set)')
            
            # Highlight selected
            prefix = "→ " if i == self.selected_index else "  "
            
            # Editing indicator
            if self.editing_key == key:
                output.append(f"{prefix}{key}: [{self.edit_buffer}]_")
            else:
                display_value = self._format_value(key, value)
                output.append(f"{prefix}{key}: {display_value}")
                
                # Add description
                desc = self._get_setting_description(key)
                if desc and i == self.selected_index:
                    output.append(f"     ⤷ {desc}")
        
        return output
    
    def _format_value(self, key: str, value: Any) -> str:
        """Format value for display"""
        # Special formatting for theme
        if key == 'theme':
            available = self._get_available_themes()
            if value in available:
                return f'"{value}" (available)'
            else:
                return f'"{value}" (missing!)'
        
        # Boolean
        if isinstance(value, bool):
            return "✓ Enabled" if value else "✗ Disabled"
        
        # String
        if isinstance(value, str):
            return f'"{value}"'
        
        # Number
        return str(value)
    
    def _get_setting_description(self, key: str) -> str:
        """Get description for setting"""
        descriptions = {
            'theme': 'Visual theme for uDOS interface',
            'use_color': 'Enable ANSI color codes',
            'show_hints': 'Show context hints at prompt',
            'panel_style': 'Border style for panels (bordered, simple, none)',
            'keypad_enabled': 'Enable numpad navigation (8/2/4/6 for movement)',
            'pager_enabled': 'Enable pager for long output',
            'browser_columns': 'File browser columns (1 or 3)',
            'autocomplete_enabled': 'Enable command autocomplete',
            'default_workspace': 'Default workspace directory',
            'auto_restore_workspace': 'Restore last workspace on startup',
            'recent_files_count': 'Number of recent files to track',
            'auto_save': 'Auto-save config changes',
            'confirmation_prompts': 'Show confirmation for destructive actions',
            'sound_enabled': 'Enable sound effects (if available)'
        }
        return descriptions.get(key, '')
    
    def _get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        from core.utils.paths import PATHS
        theme_dir = PATHS.CORE_DATA / 'themes'
        
        if not theme_dir.exists():
            return []
        
        themes = []
        for theme_file in theme_dir.glob('*.json'):
            themes.append(theme_file.stem)
        
        return sorted(themes)
    
    def _render_footer(self) -> str:
        """Render footer with controls"""
        if self.editing_key:
            controls = ["[ENTER] Save", "[ESC] Cancel", "[TAB] Options"]
        else:
            controls = [
                "↑↓ Navigate",
                "[E]dit",
                "[S]ave",
                "[R]eset",
                "[ESC] Back"
            ]
        
        return "  ".join(controls)
    
    def switch_section(self, section: str):
        """Switch to a different section"""
        if section in self.SECTIONS:
            self.current_section = section
            self.selected_index = 0
            self.editing_key = None
    
    def move_selection(self, delta: int):
        """Move selection up/down"""
        section_keys = self.SECTIONS.get(self.current_section, [])
        if not section_keys:
            return
        
        self.selected_index = (self.selected_index + delta) % len(section_keys)
    
    def start_edit(self):
        """Start editing selected setting"""
        section_keys = self.SECTIONS.get(self.current_section, [])
        if not section_keys or self.selected_index >= len(section_keys):
            return
        
        key = section_keys[self.selected_index]
        current_value = self.user_settings.get(key, '')
        
        self.editing_key = key
        self.edit_buffer = str(current_value) if current_value is not None else ''
    
    def update_edit_buffer(self, char: str):
        """Update edit buffer"""
        if self.edit_buffer is None:
            self.edit_buffer = ''
        
        if char == '\x7f':  # Backspace
            self.edit_buffer = self.edit_buffer[:-1]
        elif char.isprintable():
            self.edit_buffer += char
    
    def save_edit(self) -> Dict[str, Any]:
        """Save current edit"""
        if not self.editing_key or self.edit_buffer is None:
            return {'success': False, 'error': 'No edit in progress'}
        
        key = self.editing_key
        value_str = self.edit_buffer
        
        # Type validation and conversion
        result = self._validate_and_convert(key, value_str)
        if not result['success']:
            return result
        
        # Save to user settings
        self.user_settings[key] = result['value']
        self.modified = True
        
        # Clear edit state
        self.editing_key = None
        self.edit_buffer = None
        
        return {'success': True, 'key': key, 'value': result['value']}
    
    def cancel_edit(self):
        """Cancel current edit"""
        self.editing_key = None
        self.edit_buffer = None
    
    def _validate_and_convert(self, key: str, value_str: str) -> Dict[str, Any]:
        """Validate and convert value"""
        # Get current value to infer type
        current = self.user_settings.get(key)
        
        # Boolean
        if isinstance(current, bool):
            value_lower = value_str.lower()
            if value_lower in ['true', 'yes', '1', 'on', 'enabled']:
                return {'success': True, 'value': True}
            elif value_lower in ['false', 'no', '0', 'off', 'disabled']:
                return {'success': True, 'value': False}
            else:
                return {'success': False, 'error': f'Invalid boolean: {value_str}'}
        
        # Integer
        elif isinstance(current, int):
            try:
                return {'success': True, 'value': int(value_str)}
            except ValueError:
                return {'success': False, 'error': f'Invalid integer: {value_str}'}
        
        # String
        else:
            # Special validation for theme
            if key == 'theme':
                available = self._get_available_themes()
                if value_str not in available:
                    return {
                        'success': False,
                        'error': f'Unknown theme. Available: {", ".join(available)}'
                    }
            
            return {'success': True, 'value': value_str}
    
    def save_all(self) -> Dict[str, Any]:
        """Save all settings to disk"""
        result = self._save_settings()
        if result['success']:
            self.modified = False
        return result
    
    def reset_defaults(self) -> Dict[str, Any]:
        """Reset all settings to defaults"""
        self.user_settings = {
            'theme': 'foundation',
            'use_color': True,
            'show_hints': True,
            'panel_style': 'bordered',
            'keypad_enabled': False,
            'pager_enabled': True,
            'browser_columns': 1,
            'autocomplete_enabled': True,
            'default_workspace': 'memory/ucode/scripts/',
            'auto_restore_workspace': False,
            'recent_files_count': 10,
            'auto_save': True,
            'confirmation_prompts': True,
            'sound_enabled': False
        }
        self.modified = True
        return {'success': True}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get panel summary"""
        return {
            'total_settings': sum(len(keys) for keys in self.SECTIONS.values()),
            'sections': len(self.SECTIONS),
            'modified': self.modified,
            'current_section': self.current_section,
            'editing': self.editing_key is not None
        }


# Global instance
_user_settings_panel: Optional[UserSettingsPanel] = None


def get_user_settings_panel() -> UserSettingsPanel:
    """Get global UserSettingsPanel instance"""
    global _user_settings_panel
    if _user_settings_panel is None:
        _user_settings_panel = UserSettingsPanel()
    return _user_settings_panel
