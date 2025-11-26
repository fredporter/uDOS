"""
uDOS Path Validator - Data Architecture Enforcement

Validates file operations respect the boundary between:
- /core/data/ - Immutable reference data (read-only)
- /memory/ - User workspace (read-write)

Author: uDOS Development Team
Version: 1.1.0
Feature: 1.1.0.14
"""

from pathlib import Path
from typing import Optional, Tuple


# Writable directories (user workspace)
WRITABLE_DIRS = {'memory', 'sandbox', 'output'}

# Read-only directories (system data)
READONLY_DIRS = {'knowledge', 'core', 'extensions', 'data', 'docs', 'wiki'}


def is_writable_path(path: str, root: str = None) -> bool:
    """
    Check if a path is in a writable directory.

    Args:
        path: Path to check
        root: Project root directory (optional)

    Returns:
        True if path is writable, False if read-only

    Examples:
        >>> is_writable_path('/root/memory/test.json', '/root')
        True
        >>> is_writable_path('/root/core/data/data.json', '/root')
        False
    """
    path_obj = Path(path).resolve()

    if root:
        root_obj = Path(root).resolve()
        try:
            rel_path = path_obj.relative_to(root_obj)
        except ValueError:
            # Path is outside root
            return False
    else:
        # Use path as-is
        rel_path = Path(path)

    parts = rel_path.parts
    if not parts:
        return False

    top_dir = parts[0]

    # Check if in writable directory
    if top_dir in WRITABLE_DIRS:
        return True

    # Check if in read-only directory
    if top_dir in READONLY_DIRS:
        return False

    # Unknown directory - default to not writable
    return False


def is_system_path(path: str, root: str = None) -> bool:
    """
    Check if a path is in system (read-only) directories.

    Args:
        path: Path to check
        root: Project root directory (optional)

    Returns:
        True if path is system/read-only
    """
    path_obj = Path(path).resolve()

    if root:
        root_obj = Path(root).resolve()
        try:
            rel_path = path_obj.relative_to(root_obj)
        except ValueError:
            return False
    else:
        rel_path = Path(path)

    parts = rel_path.parts
    if not parts:
        return False

    return parts[0] in READONLY_DIRS


def detect_boundary_violation(source: str, dest: str, root: str = None) -> Optional[str]:
    """
    Detect cross-boundary access violations.

    Args:
        source: Source path
        dest: Destination path
        root: Project root directory (optional)

    Returns:
        Error message if violation detected, None if valid

    Violations:
        - Writing from memory/ to core/data/
        - Writing from core/ to core/data/
        - Any user data writes to system directories

    Examples:
        >>> detect_boundary_violation('memory/test.json', 'core/data/data.json', '/root')
        'User-to-system write: memory -> knowledge'
    """
    source_path = Path(source).resolve()
    dest_path = Path(dest).resolve()

    if root:
        root_path = Path(root).resolve()
        try:
            source_rel = source_path.relative_to(root_path)
            dest_rel = dest_path.relative_to(root_path)
        except ValueError:
            return "Path outside project root"
    else:
        source_rel = Path(source)
        dest_rel = Path(dest)

    source_parts = source_rel.parts
    dest_parts = dest_rel.parts

    if not source_parts or not dest_parts:
        return "Invalid path"

    source_top = source_parts[0]
    dest_top = dest_parts[0]

    # Violation: Writing from writable to readonly
    if source_top in WRITABLE_DIRS and dest_top in READONLY_DIRS:
        return f"User-to-system write: {source_top} -> {dest_top}"

    # Violation: Cross-system writes (between different system directories)
    if source_top in READONLY_DIRS and dest_top in READONLY_DIRS:
        if source_top != dest_top:
            return f"Cross-system write: {source_top} -> {dest_top}"

    # No violation detected
    return None


def validate_write_operation(path: str, command: str = None, root: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate a write operation is allowed.

    Args:
        path: Path to write to
        command: Command performing the write (for logging)
        root: Project root directory (optional)

    Returns:
        (success, error_message) tuple

    Examples:
        >>> validate_write_operation('memory/test.json')
        (True, None)
        >>> validate_write_operation('core/data/data.json')
        (False, 'Cannot write to read-only system directory: knowledge')
    """
    if not is_writable_path(path, root):
        path_obj = Path(path)
        if root:
            try:
                rel = path_obj.resolve().relative_to(Path(root).resolve())
                top_dir = rel.parts[0] if rel.parts else 'unknown'
            except ValueError:
                top_dir = 'unknown'
        else:
            top_dir = path_obj.parts[0] if path_obj.parts else 'unknown'

        error = f"Cannot write to read-only system directory: {top_dir}"
        if command:
            error = f"{command}: {error}"

        return (False, error)

    return (True, None)


def get_writable_alternatives(path: str, root: str = None) -> list:
    """
    Suggest writable alternatives for a read-only path.

    Args:
        path: Read-only path
        root: Project root directory (optional)

    Returns:
        List of suggested writable paths

    Example:
        >>> get_writable_alternatives('core/data/themes/custom.json')
        ['memory/themes/custom.json', 'memory/planet/themes/custom.json']
    """
    path_obj = Path(path)

    if root:
        try:
            rel = path_obj.resolve().relative_to(Path(root).resolve())
        except ValueError:
            rel = path_obj
    else:
        rel = path_obj

    parts = list(rel.parts)
    if not parts:
        return []

    # Remove top-level directory if it's readonly
    if parts[0] in READONLY_DIRS:
        parts = parts[1:]

    # Suggest alternatives in writable directories
    alternatives = []

    # Primary: memory/config/ for configuration overrides
    if 'themes' in str(path) or 'config' in str(path):
        alternatives.append(str(Path('memory/config') / Path(*parts)))

    # Secondary: memory/planet/ for general work
    alternatives.append(str(Path('memory/planet') / Path(*parts)))

    # Tertiary: sandbox/ for temporary work
    alternatives.append(str(Path('sandbox') / Path(*parts)))

    return alternatives


def validate_directory_structure(root: str) -> list:
    """
    Validate required directory structure exists.

    Args:
        root: Project root directory

    Returns:
        List of missing directories

    Creates standard uDOS directory structure:
        /core/data/ - System reference data
        /memory/private/ - Encrypted personal data
        /memory/shared/ - Shared knowledge
        /memory/groups/ - Community groups
        /memory/sandbox/ - Temporary workspace
        /memory/planet/ - User planet workspace
        /memory/ - User configuration
        /sandbox/ - General scratch space
        /output/ - Generated output
    """
    root_path = Path(root)

    required_dirs = [
        'core/data',
        'memory/private',
        'memory/shared',
        'memory/groups',
        'memory/sandbox',
        'memory/planet',
        'memory/config',
        'sandbox',
        'output'
    ]

    missing = []
    for dir_path in required_dirs:
        full_path = root_path / dir_path
        if not full_path.exists():
            missing.append(dir_path)

    return missing
