"""
uDOS Variable Resolution System
Provides dynamic variable replacement for templates, commands, and help text.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Callable, Optional


class VariableManager:
    """
    Manages system and user variables for template resolution.
    Variables can be static values or dynamic callables.
    """

    def __init__(self, components: Optional[Dict[str, Any]] = None):
        """
        Initialize the variable manager with system components.

        Args:
            components: Dictionary of system components (grid, env, theme, etc.)
        """
        self.components = components or {}
        self._init_system_vars()
        self._init_user_vars()
        self._init_path_vars()

    def _init_system_vars(self):
        """Initialize static and dynamic system variables."""
        self.system_vars = {
            # Version info
            'VERSION': '1.0.0',
            'PYTHON_VERSION': sys.version.split()[0],

            # Paths
            'INSTALL_DIR': os.getcwd(),
            'DATA_DIR': os.path.join(os.getcwd(), 'data'),
            'CORE_DIR': os.path.join(os.getcwd(), 'core'),
            'SANDBOX_DIR': os.path.join(os.getcwd(), 'sandbox'),
            'MEMORY_DIR': os.path.join(os.getcwd(), 'memory'),
            'KNOWLEDGE_DIR': os.path.join(os.getcwd(), 'knowledge'),

            # Time (dynamic - evaluated on each call)
            'TIMESTAMP': lambda: datetime.now().isoformat(),
            'DATE': lambda: datetime.now().strftime('%Y-%m-%d'),
            'TIME': lambda: datetime.now().strftime('%H:%M:%S'),
            'YEAR': lambda: str(datetime.now().year),
            'MONTH': lambda: datetime.now().strftime('%B'),
            'DAY': lambda: str(datetime.now().day),

            # System info
            'OS': sys.platform,
            'HOSTNAME': lambda: os.uname().nodename if hasattr(os, 'uname') else 'unknown',
        }

    def _init_user_vars(self):
        """Initialize user-specific variables from STORY.UDO."""
        self.user_vars = {
            'USERNAME': lambda: self._get_story_value('USER_PROFILE', 'NAME', 'Adventurer'),
            'USER_ROLE': lambda: self._get_story_value('USER_PROFILE', 'ROLE', 'Explorer'),
            'PROJECT': lambda: self._get_story_value('PROJECT', 'NAME', 'Unknown'),
            'PROJECT_DESC': lambda: self._get_story_value('PROJECT', 'DESCRIPTION', ''),
            'THEME': lambda: self._get_active_theme_name(),
            'THEME_ICON': lambda: self._get_theme_icon(),
            'SESSION': lambda: self._get_story_value('SESSION_STATS', 'CURRENT_SESSION', '1'),
            'TOTAL_SESSIONS': lambda: self._get_story_value('SESSION_STATS', 'TOTAL_SESSIONS', '0'),
            'ACTIVE_PANEL': lambda: self._get_active_panel(),
        }

    def _init_path_vars(self):
        """Initialize path template variables for common folders."""
        self.path_vars = {
            'FOLDER_SANDBOX': 'sandbox',
            'FOLDER_MEMORY': 'memory',
            'FOLDER_KNOWLEDGE': 'knowledge',
            'FOLDER_HISTORY': 'history',
            'FOLDER_CORE': 'core',
            'FOLDER_WIKI': 'wiki',
            'FOLDER_EXTENSIONS': 'extensions',
            'FOLDER_EXAMPLES': 'examples',
            'FOLDER_DATA': 'data',
        }

    def _get_story_value(self, section: str, key: str, default: str = '') -> str:
        """
        Retrieve value from STORY.UDO data.

        Args:
            section: Top-level section (e.g., 'USER_PROFILE')
            key: Key within section (e.g., 'NAME')
            default: Default value if not found

        Returns:
            String value or default
        """
        try:
            if 'env' in self.components:
                env = self.components['env']
                if hasattr(env, 'story_data') and env.story_data:
                    if section in env.story_data:
                        return str(env.story_data[section].get(key, default))
        except Exception:
            pass
        return default

    def _get_active_theme_name(self) -> str:
        """Get the currently active theme name."""
        try:
            if 'env' in self.components:
                env = self.components['env']
                if hasattr(env, 'story_data') and env.story_data:
                    system_opts = env.story_data.get('SYSTEM_OPTIONS', {})
                    return system_opts.get('THEME', 'DUNGEON')
        except Exception:
            pass
        return 'DUNGEON'

    def _get_theme_icon(self) -> str:
        """Get the icon for the active theme."""
        theme = self._get_active_theme_name()
        icons = {
            'DUNGEON': '⚔️',
            'GALAXY': '🚀',
            'FOUNDATION': '📊'
        }
        return icons.get(theme.upper(), '⚔️')

    def _get_active_panel(self) -> str:
        """Get the currently active panel name."""
        try:
            if 'grid' in self.components:
                grid = self.components['grid']
                if hasattr(grid, 'active_panel_name'):
                    return grid.active_panel_name
        except Exception:
            pass
        return 'main'

    def resolve(self, template: str, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Replace {VAR} placeholders with actual values.

        Args:
            template: String containing {VAR} placeholders
            extra_vars: Additional variables to include (override defaults)

        Returns:
            String with all variables resolved

        Example:
            >>> vm = VariableManager()
            >>> vm.resolve("User: {USERNAME}, Date: {DATE}")
            "User: Adventurer, Date: 2025-10-31"
        """
        # Combine all variable sources
        all_vars = {
            **self.system_vars,
            **self.user_vars,
            **self.path_vars,
            **(extra_vars or {})
        }

        result = template

        # Replace each variable
        for var_name, value in all_vars.items():
            placeholder = f'{{{var_name}}}'
            if placeholder in result:
                # Evaluate if callable
                if callable(value):
                    try:
                        value = value()
                    except Exception as e:
                        value = f'[ERROR:{var_name}]'

                result = result.replace(placeholder, str(value))

        return result

    def resolve_dict(self, template_dict: Dict[str, Any],
                    extra_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recursively resolve variables in a dictionary.

        Args:
            template_dict: Dictionary with string values containing {VAR}
            extra_vars: Additional variables to include

        Returns:
            Dictionary with all string values resolved
        """
        result = {}
        for key, value in template_dict.items():
            if isinstance(value, str):
                result[key] = self.resolve(value, extra_vars)
            elif isinstance(value, dict):
                result[key] = self.resolve_dict(value, extra_vars)
            elif isinstance(value, list):
                result[key] = [
                    self.resolve(item, extra_vars) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def get_all_vars(self) -> Dict[str, str]:
        """
        Get a snapshot of all current variable values.
        Useful for debugging or displaying available variables.

        Returns:
            Dictionary of all variables with resolved values
        """
        result = {}
        all_vars = {
            **self.system_vars,
            **self.user_vars,
            **self.path_vars
        }

        for var_name, value in all_vars.items():
            if callable(value):
                try:
                    result[var_name] = str(value())
                except Exception:
                    result[var_name] = '[UNAVAILABLE]'
            else:
                result[var_name] = str(value)

        return result

    def add_custom_var(self, name: str, value: Any):
        """
        Add a custom variable at runtime.

        Args:
            name: Variable name (without braces)
            value: Variable value (can be callable)
        """
        self.user_vars[name] = value


def create_variable_manager(components: Optional[Dict[str, Any]] = None) -> VariableManager:
    """
    Factory function to create a VariableManager instance.

    Args:
        components: System components dictionary

    Returns:
        Configured VariableManager instance
    """
    return VariableManager(components)


# Example usage and testing
if __name__ == "__main__":
    print("🔧 uDOS Variable Manager Test\n")

    # Create instance
    vm = VariableManager()

    # Test basic resolution
    template = "Welcome {USERNAME}! Today is {DATE} at {TIME}."
    print(f"Template: {template}")
    print(f"Resolved: {vm.resolve(template)}\n")

    # Test path variables
    path_template = "Load file from {FOLDER_SANDBOX}/test.txt"
    print(f"Path Template: {path_template}")
    print(f"Resolved: {vm.resolve(path_template)}\n")

    # Test extra variables
    extra = {"FILE_NAME": "example.md", "AUTHOR": "Test User"}
    doc_template = "File: {FILE_NAME} by {AUTHOR}, created {DATE}"
    print(f"Extra Vars Template: {doc_template}")
    print(f"Resolved: {vm.resolve(doc_template, extra)}\n")

    # Display all available variables
    print("📋 Available Variables:")
    all_vars = vm.get_all_vars()
    for var, val in sorted(all_vars.items()):
        print(f"  {{{var}}}: {val}")
