"""
uDOS Variable Resolution System v1.1.9
Provides dynamic variable replacement for templates, commands, and help text.
Now includes JSON schema-based variable system with SPRITE, OBJECT, and STORY types.
Supports scope management (global, session, script, local) and type validation.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, List, Union


class VariableManager:
    """
    Manages system and user variables for template resolution.
    Variables can be static values or dynamic callables.
    Supports JSON schema-based validation and scope management.
    """

    def __init__(self, components: Optional[Dict[str, Any]] = None):
        """
        Initialize the variable manager with system components.

        Args:
            components: Dictionary of system components (grid, env, theme, etc.)
        """
        self.components = components or {}
        self.schemas = {}  # Loaded JSON schemas
        self.variables = {}  # All active variables by scope

        # Initialize scope containers
        self.variables['global'] = {}
        self.variables['session'] = {}
        self.variables['script'] = {}
        self.variables['local'] = {}

        # Load schemas and initialize variables
        self._load_schemas()
        self._init_system_vars()
        self._init_user_vars()
        self._init_path_vars()
        self._init_prompt_vars()
        self._init_generate_vars()
        self._init_api_vars()

    def _load_schemas(self):
        """Load all JSON variable schemas from core/data/variables/."""
        schema_dir = Path(__file__).parent.parent / 'data' / 'variables'
        if not schema_dir.exists():
            return

        schema_files = ['system.json', 'user.json', 'sprite.json', 'object.json', 'story.json']

        for schema_file in schema_files:
            schema_path = schema_dir / schema_file
            if schema_path.exists():
                try:
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                        schema_name = schema_file.replace('.json', '')
                        self.schemas[schema_name] = schema

                        # Initialize default values for each variable
                        for var_name, var_def in schema.get('variables', {}).items():
                            scope = var_def.get('scope', 'global')
                            default = var_def.get('default')
                            self.variables[scope][var_name] = default
                except Exception as e:
                    print(f"Warning: Could not load schema {schema_file}: {e}")

    def validate_variable(self, var_name: str, value: Any, schema_type: str = None) -> tuple[bool, str]:
        """
        Validate a variable value against its schema definition.

        Args:
            var_name: Variable name (e.g., "SPRITE-HP")
            value: Value to validate
            schema_type: Schema to check (system, user, sprite, object, story) or auto-detect

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Find the variable definition
        var_def = None
        found_schema = None

        if schema_type:
            schemas_to_check = [schema_type]
        else:
            schemas_to_check = self.schemas.keys()

        for schema_name in schemas_to_check:
            schema = self.schemas.get(schema_name)
            if schema and var_name in schema.get('variables', {}):
                var_def = schema['variables'][var_name]
                found_schema = schema_name
                break

        if not var_def:
            return (True, "")  # Unknown variables pass validation (user-defined)

        # Type validation
        expected_type = var_def.get('type')
        if expected_type == 'string' and not isinstance(value, str):
            return (False, f"{var_name} must be a string")
        elif expected_type == 'integer' and not isinstance(value, int):
            return (False, f"{var_name} must be an integer")
        elif expected_type == 'number' and not isinstance(value, (int, float)):
            return (False, f"{var_name} must be a number")
        elif expected_type == 'boolean' and not isinstance(value, bool):
            return (False, f"{var_name} must be a boolean")
        elif expected_type == 'array' and not isinstance(value, list):
            return (False, f"{var_name} must be an array")
        elif expected_type == 'object' and not isinstance(value, dict):
            return (False, f"{var_name} must be an object")

        # Additional validation rules
        validation = var_def.get('validation', {})

        # String validations
        if expected_type == 'string':
            if 'minLength' in validation and len(value) < validation['minLength']:
                return (False, f"{var_name} must be at least {validation['minLength']} characters")
            if 'maxLength' in validation and len(value) > validation['maxLength']:
                return (False, f"{var_name} must be at most {validation['maxLength']} characters")
            if 'pattern' in validation:
                if not re.match(validation['pattern'], value):
                    return (False, f"{var_name} does not match required pattern")
            if 'enum' in validation and value not in validation['enum']:
                return (False, f"{var_name} must be one of: {', '.join(validation['enum'])}")

        # Number validations
        if expected_type in ['integer', 'number']:
            if 'minimum' in validation and value < validation['minimum']:
                return (False, f"{var_name} must be at least {validation['minimum']}")
            if 'maximum' in validation and value > validation['maximum']:
                return (False, f"{var_name} must be at most {validation['maximum']}")

        # Array validations
        if expected_type == 'array':
            if 'maxItems' in validation and len(value) > validation['maxItems']:
                return (False, f"{var_name} can have at most {validation['maxItems']} items")

        # Readonly check
        if var_def.get('readonly', False):
            return (False, f"{var_name} is read-only and cannot be modified")

        return (True, "")

    def set_variable(self, var_name: str, value: Any, scope: str = None) -> bool:
        """
        Set a variable value with validation and scope management.

        Args:
            var_name: Variable name (with or without $ prefix)
            value: Value to set
            scope: Target scope (global, session, script, local) or auto-detect

        Returns:
            True if successful, False if validation failed
        """
        # Strip $ prefix if present
        var_name = var_name.lstrip('$')

        # Determine scope if not provided
        if not scope:
            # Find existing scope or use default from schema
            for s in ['local', 'script', 'session', 'global']:
                if var_name in self.variables[s]:
                    scope = s
                    break

            if not scope:
                # Look up default scope in schemas
                for schema in self.schemas.values():
                    if var_name in schema.get('variables', {}):
                        scope = schema['variables'][var_name].get('scope', 'global')
                        break
                if not scope:
                    scope = 'global'  # Default for unknown variables

        # Validate before setting
        is_valid, error = self.validate_variable(var_name, value)
        if not is_valid:
            print(f"Variable validation error: {error}")
            return False

        self.variables[scope][var_name] = value
        return True

    def get_variable(self, var_name: str, default: Any = None) -> Any:
        """
        Get variable value, checking scopes in order: local → script → session → global.

        Args:
            var_name: Variable name (with or without $ prefix)
            default: Default value if variable not found

        Returns:
            Variable value or default
        """
        # Strip $ prefix if present
        var_name = var_name.lstrip('$')

        # Check scopes in priority order
        for scope in ['local', 'script', 'session', 'global']:
            if var_name in self.variables[scope]:
                value = self.variables[scope][var_name]
                # Evaluate if callable
                if callable(value):
                    try:
                        return value()
                    except Exception:
                        return default
                return value

        return default

    def clear_scope(self, scope: str):
        """Clear all variables in a specific scope."""
        if scope in self.variables:
            self.variables[scope] = {}

    def get_scope_variables(self, scope: str) -> Dict[str, Any]:
        """Get all variables in a specific scope."""
        return self.variables.get(scope, {}).copy()

    def _init_system_vars(self):
        """Initialize static and dynamic system variables."""
        # Legacy system vars (kept for backward compatibility)
        legacy_vars = {
            # Version info
            'VERSION': '1.1.9',
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

        # Add legacy vars to global scope
        for var_name, value in legacy_vars.items():
            if var_name not in self.variables['global']:
                self.variables['global'][var_name] = value

    def _init_user_vars(self):
        """Initialize user-specific variables from STORY.UDO."""
        legacy_user_vars = {
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

        # Add legacy vars to global scope if not already defined
        for var_name, value in legacy_user_vars.items():
            if var_name not in self.variables['global']:
                self.variables['global'][var_name] = value

    def _init_path_vars(self):
        """Initialize path template variables for common folders."""
        legacy_path_vars = {
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

        # Add legacy path vars to global scope if not already defined
        for var_name, value in legacy_path_vars.items():
            if var_name not in self.variables['global']:
                self.variables['global'][var_name] = value

    def _init_prompt_vars(self):
        """Initialize PROMPT.* variables for AI prompt injection."""
        prompt_vars = {
            # System prompts (configurable per context)
            'PROMPT.SYSTEM': lambda: self._get_prompt_config('system', 'You are a helpful survival knowledge assistant.'),
            'PROMPT.USER': lambda: self._get_prompt_config('user', ''),
            'PROMPT.CONTEXT': lambda: self._get_prompt_config('context', ''),
            
            # Prompt templates
            'PROMPT.TEMPLATE.QA': lambda: self._get_prompt_template('qa'),
            'PROMPT.TEMPLATE.GUIDE': lambda: self._get_prompt_template('guide'),
            'PROMPT.TEMPLATE.SUMMARY': lambda: self._get_prompt_template('summary'),
            'PROMPT.TEMPLATE.ENHANCE': lambda: self._get_prompt_template('enhance'),
            
            # Prompt modifiers
            'PROMPT.TONE': lambda: self._get_prompt_config('tone', 'professional'),
            'PROMPT.COMPLEXITY': lambda: self._get_prompt_config('complexity', 'detailed'),
            'PROMPT.AUDIENCE': lambda: self._get_prompt_config('audience', 'general'),
        }

        for var_name, value in prompt_vars.items():
            if var_name not in self.variables['session']:
                self.variables['session'][var_name] = value

    def _init_generate_vars(self):
        """Initialize GENERATE.* variables for generation tracking and control."""
        generate_vars = {
            # Generation mode control
            'GENERATE.MODE': lambda: self._get_generate_config('mode', 'auto'),  # auto, offline, online
            'GENERATE.PRIORITY': lambda: self._get_generate_config('priority', 'normal'),  # critical, high, normal, low
            'GENERATE.STYLE': lambda: self._get_generate_config('style', 'balanced'),  # concise, balanced, detailed
            'GENERATE.FORMAT': lambda: self._get_generate_config('format', 'text'),  # text, markdown, json
            
            # Generation statistics (read-only)
            'GENERATE.TOTAL_REQUESTS': lambda: self._get_generate_stat('total_requests', 0),
            'GENERATE.OFFLINE_REQUESTS': lambda: self._get_generate_stat('offline_requests', 0),
            'GENERATE.ONLINE_REQUESTS': lambda: self._get_generate_stat('online_requests', 0),
            'GENERATE.SUCCESS_RATE': lambda: self._get_generate_success_rate(),
            
            # Current generation context
            'GENERATE.LAST_QUERY': lambda: self._get_generate_stat('last_query', ''),
            'GENERATE.LAST_METHOD': lambda: self._get_generate_stat('last_method', ''),
            'GENERATE.LAST_CONFIDENCE': lambda: self._get_generate_stat('last_confidence', 0.0),
            'GENERATE.LAST_COST': lambda: self._get_generate_stat('last_cost', 0.0),
        }

        for var_name, value in generate_vars.items():
            if var_name not in self.variables['session']:
                self.variables['session'][var_name] = value

    def _init_api_vars(self):
        """Initialize API.* variables for API monitoring and cost tracking."""
        api_vars = {
            # API usage statistics (read-only)
            'API.REQUESTS': lambda: self._get_api_stat('total_requests', 0),
            'API.REQUESTS_TODAY': lambda: self._get_api_stat('requests_today', 0),
            'API.REQUESTS_HOUR': lambda: self._get_api_stat('requests_hour', 0),
            
            # Cost tracking
            'API.COST': lambda: self._get_api_stat('total_cost', 0.0),
            'API.COST_TODAY': lambda: self._get_api_stat('cost_today', 0.0),
            'API.COST_HOUR': lambda: self._get_api_stat('cost_hour', 0.0),
            
            # Budget management
            'API.BUDGET': lambda: self._get_api_config('daily_budget', 1.0),
            'API.BUDGET_REMAINING': lambda: self._get_api_budget_remaining(),
            'API.BUDGET_PERCENT': lambda: self._get_api_budget_percent(),
            
            # Rate limiting
            'API.RATE_LIMIT': lambda: self._get_api_config('requests_per_second', 2.0),
            'API.RATE_REMAINING': lambda: self._get_api_rate_remaining(),
            
            # Service status
            'API.OFFLINE_AVAILABLE': lambda: self._get_api_service_status('offline', True),
            'API.GEMINI_AVAILABLE': lambda: self._get_api_service_status('gemini', False),
            'API.BANANA_AVAILABLE': lambda: self._get_api_service_status('banana', False),
        }

        for var_name, value in api_vars.items():
            if var_name not in self.variables['session']:
                self.variables['session'][var_name] = value

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

    # ========== Prompt Variable Helpers ==========

    def _get_prompt_config(self, key: str, default: str = '') -> str:
        """Get prompt configuration value."""
        try:
            if 'env' in self.components:
                env = self.components['env']
                if hasattr(env, 'prompt_config'):
                    return env.prompt_config.get(key, default)
        except Exception:
            pass
        return default

    def _get_prompt_template(self, template_type: str) -> str:
        """Get prompt template by type."""
        templates = {
            'qa': 'Answer the following question concisely and accurately: {query}',
            'guide': 'Create a detailed guide about {topic}. Include practical steps, safety considerations, and common mistakes to avoid.',
            'summary': 'Summarize the following content in {length} style: {content}',
            'enhance': 'Improve and expand the following content while maintaining its core message: {content}'
        }
        return templates.get(template_type, '')

    # ========== Generate Variable Helpers ==========

    def _get_generate_config(self, key: str, default: Any) -> Any:
        """Get GENERATE configuration value."""
        try:
            if 'env' in self.components:
                env = self.components['env']
                if hasattr(env, 'generate_config'):
                    return env.generate_config.get(key, default)
        except Exception:
            pass
        return default

    def _get_generate_stat(self, key: str, default: Any) -> Any:
        """Get GENERATE statistics value."""
        try:
            if 'generate_handler' in self.components:
                handler = self.components['generate_handler']
                if hasattr(handler, 'stats'):
                    return handler.stats.get(key, default)
                # Check generation history for last_* values
                if key.startswith('last_') and hasattr(handler, 'generation_history'):
                    if handler.generation_history:
                        last_gen = handler.generation_history[-1]
                        stat_key = key.replace('last_', '')
                        return last_gen.get(stat_key, default)
        except Exception:
            pass
        return default

    def _get_generate_success_rate(self) -> float:
        """Calculate GENERATE success rate."""
        try:
            if 'generate_handler' in self.components:
                handler = self.components['generate_handler']
                if hasattr(handler, 'stats'):
                    total = handler.stats.get('total_requests', 0)
                    if total == 0:
                        return 0.0
                    # Assume all completed requests are successful (could enhance with failure tracking)
                    return 100.0
        except Exception:
            pass
        return 0.0

    # ========== API Variable Helpers ==========

    def _get_api_stat(self, key: str, default: Any) -> Any:
        """Get API monitoring statistics."""
        try:
            from core.services.api_monitor import get_api_monitor
            monitor = get_api_monitor()
            stats = monitor.get_stats()
            
            # Map stat keys
            key_mapping = {
                'total_requests': 'total_requests',
                'requests_today': 'requests_today',
                'requests_hour': 'requests_hour',
                'total_cost': 'total_cost',
                'cost_today': 'daily_cost',
                'cost_hour': 'hourly_cost'
            }
            
            mapped_key = key_mapping.get(key, key)
            return stats.get(mapped_key, default)
        except Exception:
            pass
        return default

    def _get_api_config(self, key: str, default: Any) -> Any:
        """Get API configuration value."""
        try:
            from core.services.api_monitor import get_api_monitor
            monitor = get_api_monitor()
            
            # Rate limit config
            if key == 'requests_per_second':
                return monitor.rate_config.requests_per_second
            elif key == 'daily_budget':
                return monitor.budget_config.daily_budget_usd
            
        except Exception:
            pass
        return default

    def _get_api_budget_remaining(self) -> float:
        """Calculate remaining API budget for today."""
        try:
            from core.services.api_monitor import get_api_monitor
            monitor = get_api_monitor()
            stats = monitor.get_stats()
            daily_budget = monitor.budget_config.daily_budget_usd
            daily_cost = stats.get('daily_cost', 0.0)
            return max(0.0, daily_budget - daily_cost)
        except Exception:
            pass
        return 0.0

    def _get_api_budget_percent(self) -> float:
        """Calculate API budget usage percentage."""
        try:
            from core.services.api_monitor import get_api_monitor
            monitor = get_api_monitor()
            stats = monitor.get_stats()
            daily_budget = monitor.budget_config.daily_budget_usd
            daily_cost = stats.get('daily_cost', 0.0)
            if daily_budget == 0:
                return 0.0
            return (daily_cost / daily_budget) * 100
        except Exception:
            pass
        return 0.0

    def _get_api_rate_remaining(self) -> int:
        """Get remaining API requests before rate limit."""
        try:
            from core.services.api_monitor import get_api_monitor
            monitor = get_api_monitor()
            # Simple check - how many requests in last second
            now = __import__('time').time()
            recent = [r for r in monitor.requests_last_second if now - r.timestamp < 1.0]
            limit = int(monitor.rate_config.requests_per_second)
            return max(0, limit - len(recent))
        except Exception:
            pass
        return 0

    def _get_api_service_status(self, service: str, default: bool = False) -> bool:
        """Check if an API service is available."""
        try:
            if service == 'offline':
                # Offline engine always available
                return True
            elif service == 'gemini':
                # Check if Gemini extension is available
                try:
                    from extensions.assistant.gemini_service import get_gemini_service
                    svc = get_gemini_service()
                    return svc.is_available
                except ImportError:
                    return False
            elif service == 'banana':
                # Check if Banana service is configured
                if 'env' in self.components:
                    env = self.components['env']
                    if hasattr(env, 'config_manager'):
                        return env.config_manager.get_env('BANANA_API_KEY') is not None
                return False
        except Exception:
            pass
        return default

    def resolve(self, template: str, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Replace {VAR} and $VAR placeholders with actual values.

        Args:
            template: String containing {VAR} or $VAR placeholders
            extra_vars: Additional variables to include (override defaults)

        Returns:
            String with all variables resolved

        Example:
            >>> vm = VariableManager()
            >>> vm.resolve("User: {USER-NAME}, Date: {DATE}")
            "User: survivor, Date: 2025-12-01"
            >>> vm.resolve("Health: $SPRITE-HP / $SPRITE-HP-MAX")
            "Health: 100 / 100"
        """
        result = template

        # Collect all variables from all scopes (priority: local → script → session → global)
        all_vars = {}
        for scope in ['global', 'session', 'script', 'local']:
            all_vars.update(self.variables[scope])

        # Add extra vars (highest priority)
        if extra_vars:
            all_vars.update(extra_vars)

        # Replace {VAR} and $VAR patterns
        for var_name, value in all_vars.items():
            # Handle both {VAR} and $VAR formats
            patterns = [f'{{{var_name}}}', f'${var_name}']

            for pattern in patterns:
                if pattern in result:
                    # Evaluate if callable
                    if callable(value):
                        try:
                            value = value()
                        except Exception as e:
                            value = f'[ERROR:{var_name}]'

                    result = result.replace(pattern, str(value))

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
        Get a snapshot of all current variable values across all scopes.
        Useful for debugging or displaying available variables.

        Returns:
            Dictionary of all variables with resolved values
        """
        result = {}

        # Collect from all scopes (global → session → script → local)
        for scope in ['global', 'session', 'script', 'local']:
            for var_name, value in self.variables[scope].items():
                if callable(value):
                    try:
                        result[var_name] = str(value())
                    except Exception:
                        result[var_name] = '[UNAVAILABLE]'
                else:
                    result[var_name] = str(value)

        return result

    def add_custom_var(self, name: str, value: Any, scope: str = 'global'):
        """
        Add a custom variable at runtime.

        Args:
            name: Variable name (without $ or {} prefix)
            value: Variable value (can be callable)
            scope: Variable scope (global, session, script, local)
        """
        name = name.lstrip('$').strip('{}')
        self.set_variable(name, value, scope)


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

    # Test Character and Object types
    char_mgr = CharacterObjectManager()
    hero = char_mgr.create_character("Frodo", "Archaeologist")
    ring = char_mgr.create_object("One Ring", "ring", rarity="artifact")

    print(f"Character: {hero.get_status_string()}")
    print(f"Object: {ring.get_status_string()}")
    print(f"Timestamp: {generate_udos_timestamp()}")

    # Display all available variables
    print("📋 Available Variables:")


# Character and Object Variable Types for Stories Integration
# =========================================================

@dataclass
class CharacterStats:
    """NetHack-style character statistics."""
    strength: int = 10
    intelligence: int = 10
    dexterity: int = 10
    constitution: int = 10
    wisdom: int = 10
    charisma: int = 10

    def total_stats(self) -> int:
        return self.strength + self.intelligence + self.dexterity + \
               self.constitution + self.wisdom + self.charisma

    def modifier(self, stat_value: int) -> int:
        """Calculate D&D-style ability modifier."""
        return (stat_value - 10) // 2


@dataclass
class CharacterVitals:
    """Character health and experience tracking."""
    level: int = 1
    hp: int = 10
    max_hp: int = 10
    xp: int = 0
    xp_to_next: int = 100
    gold: int = 0
    food: int = 5

    def gain_xp(self, amount: int) -> bool:
        """Gain experience, return True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            return self.level_up()
        return False

    def level_up(self) -> bool:
        """Level up character."""
        if self.xp >= self.xp_to_next:
            self.level += 1
            self.xp -= self.xp_to_next
            self.xp_to_next = int(self.xp_to_next * 1.5)
            hp_gain = max(1, (self.level + 2) // 3)
            self.max_hp += hp_gain
            self.hp = self.max_hp
            return True
        return False


@dataclass
class Character:
    """uDOS Character variable type with NetHack-inspired properties."""
    name: str = "Unnamed"
    char_class: str = "Adventurer"
    race: str = "Human"
    alignment: str = "Neutral"
    background: str = "Wanderer"

    stats: CharacterStats = field(default_factory=CharacterStats)
    vitals: CharacterVitals = field(default_factory=CharacterVitals)

    weapon: str = "bare hands"
    armor: str = "clothes"
    inventory: List[str] = field(default_factory=list)
    status_effects: List[str] = field(default_factory=list)
    location: str = "Unknown"
    story_flags: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_armor_class(self) -> int:
        """Calculate armor class."""
        base_ac = 10
        dex_mod = self.stats.modifier(self.stats.dexterity)
        armor_bonuses = {"leather jacket": 1, "chain mail": 3, "plate mail": 6}
        armor_bonus = armor_bonuses.get(self.armor.lower(), 0)
        return base_ac + armor_bonus + dex_mod

    def get_status_string(self) -> str:
        """Get formatted status string."""
        return f"{self.name} the {self.char_class}: Lvl {self.vitals.level}, " \
               f"HP {self.vitals.hp}/{self.vitals.max_hp}, XP {self.vitals.xp}"


@dataclass
class ObjectProperties:
    """Object properties and enchantments."""
    enchantment: int = 0
    durability: int = 100
    max_durability: int = 100
    magical: bool = False
    cursed: bool = False
    blessed: bool = False

    def get_condition(self) -> str:
        """Get condition based on durability."""
        if self.durability <= 0:
            return "broken"
        elif self.durability < 20:
            return "poor"
        elif self.durability < 50:
            return "fair"
        elif self.durability < 80:
            return "good"
        else:
            return "excellent"


@dataclass
class GameObject:
    """uDOS Object variable type for items and artifacts."""
    name: str = "Unknown Object"
    object_type: str = "misc"
    category: str = "item"
    rarity: str = "common"
    weight: float = 1.0
    value: int = 1

    properties: ObjectProperties = field(default_factory=ObjectProperties)
    description: str = ""
    location_found: str = "Unknown"

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_full_name(self) -> str:
        """Get full descriptive name including enchantment."""
        base_name = self.name
        if self.properties.enchantment > 0:
            base_name = f"+{self.properties.enchantment} {base_name}"
        elif self.properties.enchantment < 0:
            base_name = f"{self.properties.enchantment} {base_name}"
        if self.properties.cursed:
            base_name = f"cursed {base_name}"
        elif self.properties.blessed:
            base_name = f"blessed {base_name}"
        return base_name

    def get_status_string(self) -> str:
        """Get formatted status string."""
        condition = self.properties.get_condition()
        return f"{self.get_full_name()}: {condition}, Value {self.value}g"


class CharacterObjectManager:
    """Manager for Character and Object variables."""

    def __init__(self, data_dir: str = "memory/variables"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.characters: Dict[str, Character] = {}
        self.objects: Dict[str, GameObject] = {}

    def create_character(self, name: str, char_class: str = "Adventurer", **kwargs) -> Character:
        """Create a new character."""
        character = Character(name=name, char_class=char_class, **kwargs)
        self.characters[name] = character
        return character

    def create_object(self, name: str, object_type: str = "misc", **kwargs) -> GameObject:
        """Create a new object."""
        obj = GameObject(name=name, object_type=object_type, **kwargs)
        self.objects[name] = obj
        return obj

    def get_character(self, name: str) -> Optional[Character]:
        """Get character by name."""
        return self.characters.get(name)

    def get_object(self, name: str) -> Optional[GameObject]:
        """Get object by name."""
        return self.objects.get(name)

    def list_characters(self) -> List[str]:
        """List all character names."""
        return list(self.characters.keys())

    def list_objects(self) -> List[str]:
        """List all object names."""
        return list(self.objects.keys())


def generate_udos_timestamp(location_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate uDOS timestamp in format: udos-YYMMDD-HHSS-TMZO-MAPTILE-ZOOM

    Args:
        location_data: Optional dict with location information

    Returns:
        Formatted timestamp string
    """
    now = datetime.now()

    # Date and time components
    date_part = now.strftime("%y%m%d")
    time_part = now.strftime("%H%M")

    # Timezone offset (simplified)
    tz_offset = now.strftime("%z")
    if tz_offset:
        tz_part = tz_offset[:3] if len(tz_offset) >= 3 else "+00"
    else:
        tz_part = "+00"

    # Location components (default if not provided)
    if location_data:
        map_tile = location_data.get("map_tile", "000000")[:6].ljust(6, "0")
        zoom = str(location_data.get("zoom_level", 1))[:2].ljust(2, "0")
    else:
        map_tile = "000000"
        zoom = "01"

    return f"udos-{date_part}-{time_part}-{tz_part}-{map_tile}-{zoom}"
    all_vars = vm.get_all_vars()
    for var, val in sorted(all_vars.items()):
        print(f"  {{{var}}}: {val}")
