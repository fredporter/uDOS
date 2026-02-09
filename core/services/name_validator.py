"""
Name Validation Service
========================

Validates usernames and real names for uDOS.

Rules:
  1. Cannot be blank/empty
  2. Cannot match forbidden names (case-insensitive)
  3. Forbidden: wizard, admin, goblin, tomb, crypt, drone, portal, user

Usage:
    from core.services.name_validator import validate_name, validate_username

    # Validate real name
    is_valid, error = validate_name("Alice")
    if not is_valid:
        print(f"Invalid: {error}")

    # Validate username
    is_valid, error = validate_username("alice_42")
    if not is_valid:
        print(f"Invalid: {error}")

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

# Forbidden usernames - cannot be used (case-insensitive)
FORBIDDEN_NAMES = {
    "wizard",   # Reserved for wizard component
    "admin",    # Reserved for system admin
    "goblin",   # Reserved for Goblin MODE
    "tomb",     # Reserved for encryption
    "crypt",    # Reserved for cryptography
    "drone",    # Reserved for automation
    "portal",   # Reserved for web portal
    "user",     # Reserved generic user
}


def validate_name(name: str, field_name: str = "Name") -> tuple[bool, str]:
    """
    Validate a real name (can contain spaces, accents, etc).

    Args:
        name: The name to validate
        field_name: Field name for error messages (default: "Name")

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        - If valid: (True, "")
        - If invalid: (False, error_message)
    """
    # Check blank
    if not name or not name.strip():
        return False, f"{field_name} cannot be blank"

    cleaned = name.strip()

    # Check forbidden (case-insensitive)
    if cleaned.lower() in FORBIDDEN_NAMES:
        return False, f"{field_name} '{cleaned}' is reserved and cannot be used"

    return True, ""


def validate_username(username: str, field_name: str = "Username") -> tuple[bool, str]:
    """
    Validate a username (no spaces, alphanumeric + underscore/dash).

    Args:
        username: The username to validate
        field_name: Field name for error messages (default: "Username")

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        - If valid: (True, "")
        - If invalid: (False, error_message)
    """
    # Check blank
    if not username or not username.strip():
        return False, f"{field_name} cannot be blank"

    cleaned = username.strip()

    # Check forbidden (case-insensitive)
    if cleaned.lower() in FORBIDDEN_NAMES:
        return False, f"{field_name} '{cleaned}' is reserved and cannot be used"

    # Check valid characters (alphanumeric, underscore, dash)
    if not all(c.isalnum() or c in "_-" for c in cleaned):
        return False, f"{field_name} can only contain letters, numbers, underscore, and dash"

    # Check length
    if len(cleaned) < 2:
        return False, f"{field_name} must be at least 2 characters"

    if len(cleaned) > 32:
        return False, f"{field_name} must be at most 32 characters"

    return True, ""


def validate_real_name(name: str) -> tuple[bool, str]:
    """
    Alias for validate_name() - validates real names.

    Args:
        name: The real name to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    return validate_name(name, field_name="Name")


def get_forbidden_names_list() -> list[str]:
    """
    Get list of forbidden names (sorted).

    Returns:
        List of forbidden names in alphabetical order
    """
    return sorted(FORBIDDEN_NAMES)


def get_forbidden_names_display() -> str:
    """
    Get forbidden names as a formatted string for display.

    Returns:
        Comma-separated list of forbidden names
    """
    return ", ".join(get_forbidden_names_list())
