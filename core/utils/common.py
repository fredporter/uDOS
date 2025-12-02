"""
uDOS v1.1.13 - Common Utilities

Shared utility functions used across command handlers to promote DRY principles.

Categories:
- Path operations: validate_path, resolve_path, ensure_dir, safe_read, safe_write
- JSON operations: load_json_safe, save_json_atomic
- Formatting: format_success, format_error, format_info, format_warning
- Parsing: parse_key_value_args, parse_flags
- Validation: is_valid_filename, is_valid_extension

Created: v1.1.5.3 (Dec 2025)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# PATH OPERATIONS
# ============================================================================

def validate_path(path: str, must_exist: bool = False, base_dir: Optional[Path] = None) -> Tuple[bool, Optional[Path], str]:
    """
    Validate a file path and convert to absolute Path object.

    Args:
        path: Path string to validate
        must_exist: Whether path must exist on filesystem
        base_dir: Base directory for relative paths (default: cwd)

    Returns:
        Tuple of (is_valid, resolved_path, error_message)
        - is_valid: True if path is valid
        - resolved_path: Absolute Path object (None if invalid)
        - error_message: Empty string if valid, error description if invalid

    Examples:
        >>> validate_path("core/data/themes/galaxy.json", must_exist=True)
        (True, Path('/Users/.../uDOS/core/data/themes/galaxy.json'), '')

        >>> validate_path("/nonexistent/file.txt", must_exist=True)
        (False, None, 'Path does not exist: /nonexistent/file.txt')
    """
    try:
        # Convert to Path object
        p = Path(path)

        # Resolve to absolute path
        if not p.is_absolute():
            if base_dir:
                p = base_dir / p
            else:
                p = p.resolve()

        # Check existence if required
        if must_exist and not p.exists():
            return False, None, f"Path does not exist: {p}"

        return True, p, ""

    except (ValueError, OSError) as e:
        return False, None, f"Invalid path: {e}"


def resolve_path(path: str, base_dir: Optional[Path] = None) -> Path:
    """
    Resolve a path string to absolute Path object.

    Args:
        path: Path string (relative or absolute)
        base_dir: Base directory for relative paths (default: cwd)

    Returns:
        Absolute Path object

    Examples:
        >>> resolve_path("core/data")
        Path('/Users/.../uDOS/core/data')
    """
    p = Path(path)
    if not p.is_absolute():
        if base_dir:
            p = base_dir / p
        else:
            p = p.resolve()
    return p


def ensure_dir(path: Path, parents: bool = True) -> Tuple[bool, str]:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path
        parents: Whether to create parent directories

    Returns:
        Tuple of (success, error_message)
        - success: True if directory exists or was created
        - error_message: Empty string if success, error description if failed

    Examples:
        >>> ensure_dir(Path("sandbox/test/nested"))
        (True, '')
    """
    try:
        path.mkdir(parents=parents, exist_ok=True)
        return True, ""
    except (PermissionError, OSError) as e:
        return False, f"Failed to create directory {path}: {e}"


def safe_read(path: Path, encoding: str = 'utf-8') -> Tuple[bool, Optional[str], str]:
    """
    Safely read file contents with error handling.

    Args:
        path: File path to read
        encoding: File encoding (default: utf-8)

    Returns:
        Tuple of (success, content, error_message)
        - success: True if read succeeded
        - content: File contents (None if failed)
        - error_message: Empty string if success, error description if failed

    Examples:
        >>> safe_read(Path("core/data/themes/galaxy.json"))
        (True, '{"TERMINOLOGY": {...}}', '')
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return True, f.read(), ""
    except FileNotFoundError:
        return False, None, f"File not found: {path}"
    except PermissionError:
        return False, None, f"Permission denied: {path}"
    except UnicodeDecodeError as e:
        return False, None, f"Encoding error in {path}: {e}"
    except OSError as e:
        return False, None, f"Failed to read {path}: {e}"


def safe_write(path: Path, content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> Tuple[bool, str]:
    """
    Safely write content to file with error handling.

    Args:
        path: File path to write
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Whether to create parent directories

    Returns:
        Tuple of (success, error_message)
        - success: True if write succeeded
        - error_message: Empty string if success, error description if failed

    Examples:
        >>> safe_write(Path("sandbox/test.txt"), "Hello uDOS")
        (True, '')
    """
    try:
        # Create parent directories if needed
        if create_dirs:
            success, error = ensure_dir(path.parent)
            if not success:
                return False, error

        # Write file
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True, ""

    except PermissionError:
        return False, f"Permission denied: {path}"
    except OSError as e:
        return False, f"Failed to write {path}: {e}"


# ============================================================================
# JSON OPERATIONS
# ============================================================================

def load_json_safe(path: Path) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Safely load JSON file with error handling.

    Args:
        path: JSON file path

    Returns:
        Tuple of (success, data, error_message)
        - success: True if load succeeded
        - data: Parsed JSON dict (None if failed)
        - error_message: Empty string if success, error description if failed

    Examples:
        >>> load_json_safe(Path("core/data/themes/galaxy.json"))
        (True, {'TERMINOLOGY': {...}}, '')
    """
    # First read the file
    success, content, error = safe_read(path)
    if not success:
        return False, None, error

    # Parse JSON
    try:
        data = json.loads(content)
        return True, data, ""
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON in {path}: {e}"


def save_json_atomic(path: Path, data: Dict[str, Any], indent: int = 2, create_dirs: bool = True) -> Tuple[bool, str]:
    """
    Atomically save JSON data to file (write to temp, then rename).

    Args:
        path: JSON file path
        data: Dictionary to save
        indent: JSON indentation (default: 2)
        create_dirs: Whether to create parent directories

    Returns:
        Tuple of (success, error_message)
        - success: True if save succeeded
        - error_message: Empty string if success, error description if failed

    Examples:
        >>> save_json_atomic(Path("sandbox/config.json"), {"key": "value"})
        (True, '')
    """
    try:
        # Serialize JSON
        content = json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        return False, f"Failed to serialize JSON: {e}"

    # Write atomically (temp file + rename)
    temp_path = path.with_suffix('.tmp')
    success, error = safe_write(temp_path, content, create_dirs=create_dirs)
    if not success:
        return False, error

    try:
        temp_path.replace(path)  # Atomic on POSIX systems
        return True, ""
    except OSError as e:
        # Clean up temp file on failure
        try:
            temp_path.unlink()
        except:
            pass
        return False, f"Failed to save {path}: {e}"


# ============================================================================
# PARSING
# ============================================================================

def parse_key_value_args(args: List[str]) -> Dict[str, str]:
    """
    Parse key=value argument pairs.

    Args:
        args: List of argument strings

    Returns:
        Dictionary of key-value pairs

    Examples:
        >>> parse_key_value_args(["name=test", "type=water"])
        {'name': 'test', 'type': 'water'}

        >>> parse_key_value_args(["mode", "key=value"])
        {'key': 'value'}  # Non-KV args ignored
    """
    result = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def parse_flags(args: List[str]) -> Tuple[List[str], Dict[str, bool]]:
    """
    Parse flag arguments (--flag) from argument list.

    Args:
        args: List of argument strings

    Returns:
        Tuple of (non_flag_args, flag_dict)
        - non_flag_args: Arguments that aren't flags
        - flag_dict: Dictionary of flag names (without --) to True

    Examples:
        >>> parse_flags(["file.txt", "--verbose", "--force"])
        (['file.txt'], {'verbose': True, 'force': True})
    """
    non_flags = []
    flags = {}

    for arg in args:
        if arg.startswith('--'):
            flag_name = arg[2:]
            flags[flag_name] = True
        else:
            non_flags.append(arg)

    return non_flags, flags


# ============================================================================
# VALIDATION
# ============================================================================

def is_valid_filename(filename: str, allow_dirs: bool = False) -> bool:
    """
    Check if filename is valid (no path separators, illegal chars).

    Args:
        filename: Filename to validate
        allow_dirs: Whether to allow directory separators

    Returns:
        True if valid filename

    Examples:
        >>> is_valid_filename("test.txt")
        True

        >>> is_valid_filename("../etc/passwd")
        False

        >>> is_valid_filename("dir/file.txt", allow_dirs=True)
        True
    """
    if not filename or filename in ('.', '..'):
        return False

    # Check for path separators (unless allowed)
    if not allow_dirs:
        if '/' in filename or '\\' in filename:
            return False

    # Check for null bytes and control characters
    if '\0' in filename or any(ord(c) < 32 for c in filename):
        return False

    return True


def is_valid_extension(filename: str, allowed: List[str]) -> bool:
    """
    Check if file has one of the allowed extensions.

    Args:
        filename: Filename to check
        allowed: List of allowed extensions (with or without dots)

    Returns:
        True if extension is allowed

    Examples:
        >>> is_valid_extension("test.upy", [".upy", ".py"])
        True

        >>> is_valid_extension("test.txt", ["upy", "py"])
        False
    """
    # Normalize extensions to include dots
    normalized = [ext if ext.startswith('.') else f'.{ext}' for ext in allowed]

    # Get file extension
    _, ext = os.path.splitext(filename)

    return ext.lower() in normalized
