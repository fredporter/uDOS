#!/usr/bin/env python3
"""
uDOS Variable Access Library for uSCRIPT
Provides standardized access to uDOS system variables from Python scripts
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class UDOSVariables:
    """uDOS Variable Manager for Python scripts."""

    def __init__(self):
        self.udos_root = os.environ.get('UDOS_ROOT', self._find_udos_root())
        self.system_vars_file = Path(self.udos_root) / 'uMEMORY' / 'system' / 'variables' / 'system-variables.json'
        self.user_vars_dir = Path(self.udos_root) / 'uMEMORY' / 'user' / 'variables'
        self._cache = {}

    def _find_udos_root(self) -> str:
        """Find uDOS root directory."""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / 'uCORE').exists():
                return str(current)
            current = current.parent
        raise RuntimeError("uDOS root directory not found")

    def load_system_variables(self) -> Dict[str, Any]:
        """Load system variable definitions."""
        if not self.system_vars_file.exists():
            return {}

        with open(self.system_vars_file, 'r') as f:
            data = json.load(f)
            return data.get('variables', {})

    def get_variable(self, name: str, session: str = 'current') -> Optional[str]:
        """Get variable value with fallback to default."""
        # Try to get from environment first (fastest)
        var_def = self.load_system_variables().get(name, {})
        env_name = var_def.get('env_name')
        if env_name and env_name in os.environ:
            return os.environ[env_name]

        # Try to get from session values
        values_file = self.user_vars_dir / f'values-{session}.json'
        if values_file.exists():
            with open(values_file, 'r') as f:
                data = json.load(f)
                value = data.get('values', {}).get(name)
                if value is not None:
                    return value

        # Fall back to default value
        return var_def.get('default', '')

    def get_user_role(self) -> str:
        """Get current user role."""
        return self.get_variable('USER-ROLE') or 'GHOST'

    def get_user_level(self) -> int:
        """Get current user level."""
        try:
            return int(self.get_variable('USER-LEVEL') or 10)
        except ValueError:
            return 10

    def get_display_mode(self) -> str:
        """Get current display mode."""
        return self.get_variable('DISPLAY-MODE') or 'CLI'

    def get_project_name(self) -> str:
        """Get current project name."""
        return self.get_variable('PROJECT-NAME') or ''

    def get_session_id(self) -> str:
        """Get current session ID."""
        return self.get_variable('SESSION-ID') or ''

    def is_dev_mode(self) -> bool:
        """Check if development mode is enabled."""
        dev_mode = self.get_variable('DEV-MODE')
        if isinstance(dev_mode, bool):
            return dev_mode
        return str(dev_mode).lower() in ('true', '1', 'yes')

    def get_debug_level(self) -> str:
        """Get debug level."""
        return self.get_variable('DEBUG-LEVEL') or 'INFO'

    def get_all_variables(self, session: str = 'current') -> Dict[str, str]:
        """Get all available variables as dictionary."""
        variables = {}
        system_vars = self.load_system_variables()

        for var_name in system_vars.keys():
            value = self.get_variable(var_name, session)
            if value is not None:
                variables[var_name] = value

        return variables

    def get_scoped_variables(self, scope: str) -> Dict[str, str]:
        """Get variables for a specific scope."""
        system_vars = self.load_system_variables()
        scoped_vars = {}

        for var_name, var_def in system_vars.items():
            if var_def.get('scope') == scope:
                value = self.get_variable(var_name)
                if value is not None:
                    scoped_vars[var_name] = value

        return scoped_vars

# Convenience instance
udos_vars = UDOSVariables()

# Convenience functions
def get_user_role() -> str:
    """Get current user role."""
    return udos_vars.get_user_role()

def get_user_level() -> int:
    """Get current user level."""
    return udos_vars.get_user_level()

def get_display_mode() -> str:
    """Get current display mode."""
    return udos_vars.get_display_mode()

def get_project_name() -> str:
    """Get current project name."""
    return udos_vars.get_project_name()

def is_dev_mode() -> bool:
    """Check if development mode is enabled."""
    return udos_vars.is_dev_mode()

def get_variable(name: str) -> Optional[str]:
    """Get any variable by name."""
    return udos_vars.get_variable(name)
