"""
Shared confirmation utilities for standard Yes/No/OK or Yes/No/SKIP prompts.
"""

from __future__ import annotations

from typing import Optional, Tuple, Union


VariantType = str  # "ok" or "skip"
DefaultType = Union[bool, str, None]


def normalize_default(default: DefaultType, variant: VariantType) -> str:
    """Normalize default input to a choice string."""
    if isinstance(default, bool):
        if not default and variant == "skip":
            return "skip"
        return "yes" if default else "no"
    if isinstance(default, str) and default:
        value = default.strip().lower()
        if value in {"yes", "no", "ok", "skip"}:
            if variant == "skip" and value == "ok":
                return "yes"
            if variant == "ok" and value == "skip":
                return "no"
            return value
    if variant == "skip":
        return "skip"
    return "yes"


def format_options(variant: VariantType) -> str:
    if variant == "skip":
        return "[Yes|No|SKIP]"
    return "[Yes|No|OK]"


def format_prompt(question: str, default: str, variant: VariantType) -> str:
    default_display = default.upper()
    return f"{question}? {format_options(variant)} (Enter={default_display}) "


def parse_confirmation(response: str, default: str, variant: VariantType) -> Optional[str]:
    """Return normalized choice or None if invalid."""
    response = (response or "").strip().lower()
    if response == "":
        return default

    if response in {"1", "y", "yes"}:
        return "yes"
    if response in {"0", "n", "no"}:
        return "no"
    if variant == "ok" and response in {"o", "ok", "okay"}:
        return "ok"
    if variant == "skip" and response in {"s", "skip"}:
        return "skip"
    return None


def format_error(variant: VariantType) -> str:
    if variant == "skip":
        return "  ❌ Please enter: 1 (Yes), 0 (No), Yes, No, or SKIP"
    return "  ❌ Please enter: 1 (Yes), 0 (No), Yes, No, or OK"
