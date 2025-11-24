"""
uDOS Theme Schema Validator

Validates theme JSON files for:
- Required keys (THEME_NAME, TERMINOLOGY, MESSAGES)
- Consistent placeholder usage
- Format string compatibility
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import re


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
                # Collect all message keys (support both flat and nested structures)
                all_msg_keys = set()

                def collect_message_keys(msg_dict, prefix=''):
                    """Recursively collect message keys from nested structure."""
                    for key, value in msg_dict.items():
                        if isinstance(value, dict):
                            # Nested category (e.g., SUCCESS, INFO, ERROR)
                            collect_message_keys(value, prefix)
                        elif isinstance(value, str):
                            # Direct message
                            all_msg_keys.add(key)
                        else:
                            errors.append(f"Message {prefix}{key} must be a string")

                collect_message_keys(data['MESSAGES'])

                # Check for required messages
                missing_msgs = self.REQUIRED_MESSAGES - all_msg_keys
                if missing_msgs:
                    errors.append(f"Missing required messages: {', '.join(missing_msgs)}")

                # Validate format strings
                def validate_format_strings(msg_dict, prefix=''):
                    """Recursively validate format strings."""
                    for key, template in msg_dict.items():
                        if isinstance(template, dict):
                            validate_format_strings(template, f"{key}.")
                        elif isinstance(template, str):
                            try:
                                # Extract placeholders
                                placeholders = re.findall(r'\{([^}]+)\}', template)
                                # Try formatting with dummy values
                                dummy_kwargs = {p: 'test' for p in placeholders}
                                template.format(**dummy_kwargs)
                            except Exception as e:
                                errors.append(f"Message {prefix}{key} has invalid format string: {e}")

                validate_format_strings(data['MESSAGES'])

        return len(errors) == 0, errors

    def validate_all_themes(self) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all theme files in knowledge/system/themes/.

        Returns:
            Dict mapping theme_name -> (is_valid, errors)
        """
        results = {}

        if not self.theme_dir.exists():
            return {'_error': (False, [f"Theme directory not found: {self.theme_dir}"])}

        for theme_file in self.theme_dir.glob('*.json'):
            theme_name = theme_file.stem

            # Skip metadata/schema files
            if theme_name.startswith('_'):
                continue

            is_valid, errors = self.validate_theme_file(theme_file)
            results[theme_name] = (is_valid, errors)

        return results

    def get_all_message_keys(self) -> Set[str]:
        """Get all unique message keys used across all themes."""
        all_keys = set()

        for theme_file in self.theme_dir.glob('*.json'):
            try:
                with theme_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'MESSAGES' in data:
                        all_keys.update(data['MESSAGES'].keys())
            except Exception:
                pass

        return all_keys

    def print_validation_report(self):
        """Print a formatted validation report to stdout."""
        results = self.validate_all_themes()

        print("=" * 70)
        print("uDOS THEME VALIDATION REPORT")
        print("=" * 70)
        print()

        valid_count = sum(1 for is_valid, _ in results.values() if is_valid)
        total_count = len(results)

        for theme_name, (is_valid, errors) in sorted(results.items()):
            status = "✅ VALID" if is_valid else "❌ INVALID"
            print(f"{status}: {theme_name}")

            if errors:
                for error in errors:
                    print(f"  └─ {error}")
                print()

        print("=" * 70)
        print(f"Summary: {valid_count}/{total_count} themes valid")
        print("=" * 70)

        return valid_count == total_count


if __name__ == '__main__':
    validator = ThemeValidator()
    all_valid = validator.print_validation_report()

    if not all_valid:
        exit(1)
