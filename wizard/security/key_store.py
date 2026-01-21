"""Key store module stub."""

from typing import Optional


def get_wizard_key(key_name: str) -> Optional[str]:
    """Get a wizard key from secure storage."""
    return None


def set_wizard_key(key_name: str, key_value: str) -> bool:
    """Store a wizard key in secure storage."""
    return False
