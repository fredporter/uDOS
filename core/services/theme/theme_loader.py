"""
uDOS Theme Loader & Validator
Handles theme loading, merging, and validation

Consolidates theme_loader.py and theme_validator.py
Version: 1.1.0
"""

from pathlib import Path
import json
import re
from typing import Dict, Any, List, Tuple, Set


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def load_theme(theme_name: str = 'default', root_path: Path = None) -> Dict[str, Dict[str, Any]]:
    """
    Load a theme lexicon by merging bundled themes with optional user overrides.

    Search order:
    1. core/data/themes/ (system themes for layers 100-399)
    2. extensions/play/data/themes/ (gameplay themes for layers 400-899)
    3. memory/themes/ (user overrides - highest priority)

    Precedence: memory override > extensions/play > core.

    Returns a dict with keys: 'TERMINOLOGY', 'MESSAGES', 'META', and optionally
    'THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON'.
    """
    if root_path is None:
        root_path = Path(__file__).parent.parent.parent

    # Search paths in order (lowest to highest priority)
    core_theme_path = root_path / 'core' / 'data' / 'themes' / f"{theme_name}.json"
    extensions_theme_path = root_path / 'extensions' / 'play' / 'data' / 'themes' / f"{theme_name}.json"
    memory_theme_path = root_path / 'memory' / 'themes' / f"{theme_name}.json"

    # Merge themes (memory overrides extensions overrides core)
    merged = {
        'TERMINOLOGY': {},
        'MESSAGES': {},
        'META': {
            'theme_name': theme_name,
            'source_core': str(core_theme_path) if core_theme_path.exists() else None,
            'source_extensions': str(extensions_theme_path) if extensions_theme_path.exists() else None,
            'source_memory': str(memory_theme_path) if memory_theme_path.exists() else None
        }
    }

    # Load from core first (system themes)
    if core_theme_path.exists():
        with core_theme_path.open('r', encoding='utf-8') as f:
            core_data = json.load(f)
            merged['TERMINOLOGY'].update(core_data.get('TERMINOLOGY', {}))
            merged['MESSAGES'].update(core_data.get('MESSAGES', {}))
            # Copy metadata fields
            for key in ['THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON']:
                if key in core_data:
                    merged[key] = core_data[key]

    # Overlay extensions (gameplay themes)
    if extensions_theme_path.exists():
        with extensions_theme_path.open('r', encoding='utf-8') as f:
            extensions_data = json.load(f)
            merged['TERMINOLOGY'].update(extensions_data.get('TERMINOLOGY', {}))
            merged['MESSAGES'].update(extensions_data.get('MESSAGES', {}))
            # Extensions can override metadata
            for key in ['THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON']:
                if key in extensions_data:
                    merged[key] = extensions_data[key]

    # Overlay user customizations from memory (highest priority)
    if memory_theme_path.exists():
        with memory_theme_path.open('r', encoding='utf-8') as f:
            memory_data = json.load(f)
            merged['TERMINOLOGY'].update(memory_data.get('TERMINOLOGY', {}))
            merged['MESSAGES'].update(memory_data.get('MESSAGES', {}))
            # User can override metadata too
            for key in ['THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON']:
                if key in memory_data:
                    merged[key] = memory_data[key]

    return merged


class ThemeValidator:
    """Validates theme JSON structure and content."""

    REQUIRED_KEYS = {'THEME_NAME', 'TERMINOLOGY', 'MESSAGES'}
    REQUIRED_MESSAGES = {
        'ERROR_CRASH', 'ERROR_INVALID_UCODE_FORMAT', 'ERROR_UNKNOWN_MODULE',
        'ERROR_UNKNOWN_SYSTEM_COMMAND', 'ERROR_UNKNOWN_FILE_COMMAND',
        'ERROR_GENERIC', 'INFO_EXIT'
    }

    def __init__(self, root_path: Path = None):
        if root_path is None:
            root_path = Path(__file__).parent.parent.parent
        self.root_path = root_path
        # Check both core and extensions theme directories
        self.core_theme_dir = root_path / 'core' / 'data' / 'themes'
        self.extensions_theme_dir = root_path / 'extensions' / 'play' / 'data' / 'themes'

    def validate_theme_file(self, theme_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a single theme JSON file.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Load JSON
        try:
            with theme_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Failed to read file: {e}"]

        # Check required top-level keys
        missing_keys = self.REQUIRED_KEYS - set(data.keys())
        if missing_keys:
            errors.append(f"Missing required keys: {', '.join(missing_keys)}")

        # Validate TERMINOLOGY section
        if 'TERMINOLOGY' in data:
            if not isinstance(data['TERMINOLOGY'], dict):
                errors.append("TERMINOLOGY must be a dictionary")

        # Validate MESSAGES section
        if 'MESSAGES' in data:
            if not isinstance(data['MESSAGES'], dict):
                errors.append("MESSAGES must be a dictionary")
            else:
                # Collect all message keys
                all_msg_keys = set()

                def collect_message_keys(msg_dict, prefix=''):
                    for key, value in msg_dict.items():
                        if isinstance(value, dict):
                            collect_message_keys(value, prefix)
                        elif isinstance(value, str):
                            all_msg_keys.add(key)

                collect_message_keys(data['MESSAGES'])

                # Check for required messages
                missing_msgs = self.REQUIRED_MESSAGES - all_msg_keys
                if missing_msgs:
                    errors.append(f"Missing required messages: {', '.join(missing_msgs)}")

                # Validate format strings
                def validate_format_strings(msg_dict, prefix=''):
                    for key, template in msg_dict.items():
                        if isinstance(template, dict):
                            validate_format_strings(template, f"{key}.")
                        elif isinstance(template, str):
                            try:
                                placeholders = re.findall(r'\{([^}]+)\}', template)
                                dummy_kwargs = {p: 'test' for p in placeholders}
                                template.format(**dummy_kwargs)
                            except Exception as e:
                                errors.append(f"Message {prefix}{key} has invalid format string: {e}")

                validate_format_strings(data['MESSAGES'])

        return len(errors) == 0, errors

    def find_theme(self, theme_name: str) -> Path:
        """Find theme file in core or extensions directories."""
        core_path = self.core_theme_dir / f"{theme_name}.json"
        if core_path.exists():
            return core_path

        extensions_path = self.extensions_theme_dir / f"{theme_name}.json"
        if extensions_path.exists():
            return extensions_path

        raise FileNotFoundError(f"Theme '{theme_name}' not found in core or extensions")


class ThemeLoader:
    """Unified theme loading and validation."""

    def __init__(self, root_path: Path = None):
        if root_path is None:
            root_path = Path(__file__).parent.parent.parent
        self.root_path = root_path
        self.validator = ThemeValidator(root_path)

    def load(self, theme_name: str = 'default', validate: bool = False) -> Dict[str, Any]:
        """Load theme with optional validation."""
        theme_data = load_theme(theme_name, self.root_path)

        if validate:
            try:
                theme_path = self.find_theme(theme_name)
                is_valid, errors = self.validator.validate_theme_file(theme_path)
                if not is_valid:
                    print(f"⚠️  Theme '{theme_name}' has validation errors:")
                    for error in errors:
                        print(f"  - {error}")
            except FileNotFoundError:
                # Theme not found - might be loaded from memory only
                pass

        return theme_data
