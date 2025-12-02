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


def load_theme(theme_name: str = 'dungeon', root_path: Path = None) -> Dict[str, Dict[str, Any]]:
    """
    Load a theme lexicon by merging the bundled theme under `knowledge` with
    optional user overrides in `memory`.

    Precedence: memory override (if present) > knowledge bundled theme.

    Returns a dict with keys: 'TERMINOLOGY', 'MESSAGES', 'META', and optionally
    'THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON'.
    """
    if root_path is None:
        root_path = Path(__file__).parent.parent.parent

    knowledge_theme_path = root_path / 'knowledge' / 'system' / 'themes' / f"{theme_name}.json"
    memory_theme_path = root_path / 'memory' / 'system' / 'themes' / f"{theme_name}.json"

    # Merge themes (memory overrides knowledge)
    merged = {
        'TERMINOLOGY': {},
        'MESSAGES': {},
        'META': {
            'theme_name': theme_name,
            'source_knowledge': str(knowledge_theme_path) if knowledge_theme_path.exists() else None,
            'source_memory': str(memory_theme_path) if memory_theme_path.exists() else None
        }
    }

    # Load from bundled knowledge first
    if knowledge_theme_path.exists():
        with knowledge_theme_path.open('r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
            merged['TERMINOLOGY'].update(knowledge_data.get('TERMINOLOGY', {}))
            merged['MESSAGES'].update(knowledge_data.get('MESSAGES', {}))
            # Copy metadata fields
            for key in ['THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON']:
                if key in knowledge_data:
                    merged[key] = knowledge_data[key]

    # Overlay user customizations from memory
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
        self.theme_dir = root_path / 'knowledge' / 'system' / 'themes'

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


class ThemeLoader:
    """Unified theme loading and validation."""

    def __init__(self, root_path: Path = None):
        if root_path is None:
            root_path = Path(__file__).parent.parent.parent
        self.root_path = root_path
        self.validator = ThemeValidator(root_path)

    def load(self, theme_name: str = 'dungeon', validate: bool = False) -> Dict[str, Any]:
        """Load theme with optional validation."""
        theme_data = load_theme(theme_name, self.root_path)

        if validate:
            theme_path = self.root_path / 'knowledge' / 'system' / 'themes' / f"{theme_name}.json"
            if theme_path.exists():
                is_valid, errors = self.validator.validate_theme_file(theme_path)
                if not is_valid:
                    print(f"⚠️  Theme '{theme_name}' has validation errors:")
                    for error in errors:
                        print(f"  - {error}")

        return theme_data
