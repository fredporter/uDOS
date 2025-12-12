"""
Config Browser UI Component (v1.2.18)

Browse and edit all CONFIG settings with visual editor and type validation.
C-key panel for configuration management.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from core.config import Config
from core.services.ok_config import get_ok_config
from core.utils.column_formatter import ColumnFormatter, ColumnConfig


class ConfigBrowser:
    """
    TUI browser for CONFIG settings.
    
    Features:
    - Navigate all CONFIG key/value pairs
    - Visual editor with type validation
    - Save/revert changes
    - Search/filter settings
    - Category organization
    """
    
    # Setting categories for organization
    CATEGORIES = {
        'display': ['theme', 'viewport_width', 'viewport_height', 'use_color', 'show_hints'],
        'paths': ['last_location', 'default_workspace', 'data_dir', 'extensions_dir'],
        'ai': ['ai_provider', 'ai_model', 'ai_temperature', 'use_ai'],
        'ok': ['ok_model', 'ok_temperature', 'ok_max_tokens', 'ok_cost_tracking', 'ok_context_length'],
        'system': ['debug_mode', 'log_level', 'auto_save', 'backup_enabled'],
        'network': ['offline_mode', 'api_timeout', 'cache_enabled']
    }
    
    def __init__(self):
        """Initialize config browser"""
        self.config = Config()
        self.ok_config = get_ok_config()
        self.current_category = 'display'
        self.selected_index = 0
        self.editing_key = None
        self.edit_buffer = None
        self.modified_keys = set()
        self.formatter = ColumnFormatter(ColumnConfig(width=70))
        
    def render(self) -> str:
        """
        Render the config browser panel.
        
        Returns:
            Formatted panel content
        """
        output = []
        
        # Header
        output.append(self._render_header())
        output.append("")
        
        # Category tabs
        output.append(self._render_category_tabs())
        output.append("=" * 70)
        output.append("")
        
        # Settings list
        output.extend(self._render_settings())
        
        # Footer
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    def _render_header(self) -> str:
        """Render panel header"""
        modified_indicator = f" ({len(self.modified_keys)} modified)" if self.modified_keys else ""
        title = f"CONFIG Browser{modified_indicator}"
        return self.formatter.box_top(title)odified)" if self.modified_keys else ""
        return f"╔══ CONFIG Browser ══╗{modified_indicator}"
    
    def _render_category_tabs(self) -> str:
        """Render category tabs"""
        tabs = []
        for category in self.CATEGORIES.keys():
            if category == self.current_category:
                tabs.append(f"[{category.upper()}]")
            else:
                tabs.append(f" {category} ")
        
        return "  |  ".join(tabs)
    
    def _render_settings(self) -> List[str]:
        """Render settings for current category"""
        output = []
        
        # Get settings for current category
        category_keys = self.CATEGORIES.get(self.current_category, [])
        
        if not category_keys:
            output.append("  (No settings in this category)")
            return output
        
        # Render each setting
        for i, key in enumerate(category_keys):
            # Get value from appropriate config (OK config for ok_* keys)
            if key.startswith('ok_'):
                ok_key = key[3:]  # Remove 'ok_' prefix
                value = self.ok_config.get(ok_key, '(not set)')
            else:
                value = self.config.get(key, '(not set)')
            
            # Highlight selected
            prefix = "→ " if i == self.selected_index else "  "
            
            # Modified indicator
            modified = "*" if key in self.modified_keys else " "
            
            # Editing indicator
            if self.editing_key == key:
                output.append(f"{prefix}{modified}{key}: [{self.edit_buffer}]_")
            else:
                # Format value based on type
                display_value = self._format_value(value)
                output.append(f"{prefix}{modified}{key}: {display_value}")
        
        return output
    
    def _format_value(self, value: Any) -> str:
        """Format value for display"""
        if value is None:
            return "(None)"
        elif isinstance(value, bool):
            return "✓ True" if value else "✗ False"
        elif isinstance(value, str):
            return f'"{value}"' if value else '""'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    def _render_footer(self) -> str:
        """Render panel footer with controls"""
        if self.editing_key:
            controls = ["[ENTER] Save", "[ESC] Cancel", "[TAB] Type help"]
        else:
            controls = [
                "↑↓ Navigate",
                "[E]dit",
                "[S]ave All",
                "[R]evert",
                "[/] Search",
                "[ESC] Close"
            ]
        
        return "  ".join(controls)
    
    def switch_category(self, category: str):
        """Switch to a different category"""
        if category in self.CATEGORIES:
            self.current_category = category
            self.selected_index = 0
            self.editing_key = None
    
    def move_selection(self, delta: int):
        """Move selection up/down"""
        category_keys = self.CATEGORIES.get(self.current_category, [])
        if not category_keys:
            return
        
        self.selected_index = (self.selected_index + delta) % len(category_keys)
    
    def start_edit(self):
        """Start editing selected setting"""
        category_keys = self.CATEGORIES.get(self.current_category, [])
        if not category_keys or self.selected_index >= len(category_keys):
            return
        
        key = category_keys[self.selected_index]
        
        # Get value from appropriate config
        if key.startswith('ok_'):
            ok_key = key[3:]
            current_value = self.ok_config.get(ok_key, '')
        else:
            current_value = self.config.get(key, '')
        
        self.editing_key = key
        self.edit_buffer = str(current_value) if current_value is not None else ''
    
    def update_edit_buffer(self, char: str):
        """Update edit buffer with character"""
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
        
        # Save to appropriate config (OK config for ok_* keys)
        if key.startswith('ok_'):
            ok_key = key[3:]  # Remove 'ok_' prefix
            success = self.ok_config.set(ok_key, result['value'])
            if success:
                self.ok_config.save()
            else:
                return {'success': False, 'error': f'Invalid value for {key}'}
        else:
            self.config.set(key, result['value'])
        
        self.modified_keys.add(key)
        
        # Clear edit state
        self.editing_key = None
        self.edit_buffer = None
        
        return {'success': True, 'key': key, 'value': result['value']}
    
    def cancel_edit(self):
        """Cancel current edit"""
        self.editing_key = None
        self.edit_buffer = None
    
    def _validate_and_convert(self, key: str, value_str: str) -> Dict[str, Any]:
        """
        Validate and convert value based on expected type.
        
        Args:
            key: Setting key
            value_str: String value to convert
            
        Returns:
            Dict with success status and converted value
        """
        # Get current value to infer type
        current = self.config.get(key)
        
        # Type conversion
        if isinstance(current, bool):
            # Boolean: accept true/false, yes/no, 1/0
            value_lower = value_str.lower()
            if value_lower in ['true', 'yes', '1', 'on']:
                return {'success': True, 'value': True}
            elif value_lower in ['false', 'no', '0', 'off']:
                return {'success': True, 'value': False}
            else:
                return {'success': False, 'error': f'Invalid boolean: {value_str}'}
        
        elif isinstance(current, int):
            # Integer
            try:
                return {'success': True, 'value': int(value_str)}
            except ValueError:
                return {'success': False, 'error': f'Invalid integer: {value_str}'}
        
        elif isinstance(current, float):
            # Float
            try:
                return {'success': True, 'value': float(value_str)}
            except ValueError:
                return {'success': False, 'error': f'Invalid number: {value_str}'}
        
        else:
            # String (default)
            return {'success': True, 'value': value_str}
    
    def save_all(self) -> Dict[str, Any]:
        """Save all modified settings to disk"""
        if not self.modified_keys:
            return {'success': True, 'saved': 0}
        
        try:
            self.config.save()
            saved_count = len(self.modified_keys)
            self.modified_keys.clear()
            return {'success': True, 'saved': saved_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def revert_all(self) -> Dict[str, Any]:
        """Revert all unsaved changes"""
        if not self.modified_keys:
            return {'success': True, 'reverted': 0}
        
        try:
            # Reload config from disk
            self.config.load()
            reverted_count = len(self.modified_keys)
            self.modified_keys.clear()
            return {'success': True, 'reverted': reverted_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search(self, query: str) -> List[str]:
        """
        Search for settings matching query.
        
        Args:
            query: Search term
            
        Returns:
            List of matching keys
        """
        query_lower = query.lower()
        matches = []
        
        # Search all categories
        for category, keys in self.CATEGORIES.items():
            for key in keys:
                if query_lower in key.lower():
                    matches.append(f"{category}/{key}")
        
        return matches
    
    def get_summary(self) -> Dict[str, Any]:
        """Get config browser summary"""
        total_settings = sum(len(keys) for keys in self.CATEGORIES.values())
        
        return {
            'total_settings': total_settings,
            'categories': len(self.CATEGORIES),
            'modified': len(self.modified_keys),
            'current_category': self.current_category,
            'editing': self.editing_key is not None
        }


# Global instance
_config_browser_instance: Optional[ConfigBrowser] = None


def get_config_browser() -> ConfigBrowser:
    """Get global ConfigBrowser instance"""
    global _config_browser_instance
    if _config_browser_instance is None:
        _config_browser_instance = ConfigBrowser()
    return _config_browser_instance
