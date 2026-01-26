"""
Markdown Frontmatter Helper (Core)
=================================

Shared parsing logic so every uDOS subsystem resolves YAML frontmatter consistently.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Tuple, Sequence

import yaml

FRONTMATTER_PATTERN = re.compile(r"^\s*---\s*\n([\s\S]*?)\n---\s*\n?", re.MULTILINE)

DEFAULT_FRONTMATTER: Dict[str, Any] = {
    "title": "Story",
    "description": "",
}


def parse_markdown_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from the top of a Markdown document.

    Returns (frontmatter_dict, body), where body is the remainder after the frontmatter.
    Missing or invalid frontmatter falls back to DEFAULT_FRONTMATTER.
    """
    trimmed = content.lstrip()
    match = FRONTMATTER_PATTERN.match(trimmed)
    if not match:
        return DEFAULT_FRONTMATTER.copy(), trimmed

    raw_frontmatter = match.group(1)
    try:
        frontmatter = yaml.safe_load(raw_frontmatter) or {}
    except Exception as exc:
        logging.getLogger("core.markdown.frontmatter").warning(
            "Failed to parse frontmatter (%s); falling back to defaults", exc
        )
        frontmatter = {}

    if not isinstance(frontmatter, dict):
        frontmatter = {}
    combined = {**DEFAULT_FRONTMATTER, **frontmatter}
    body = trimmed[match.end() :].lstrip("\n")
    return combined, body


def validate_frontmatter(
    frontmatter: Dict[str, Any], required_keys: Sequence[str]
) -> None:
    """
    Ensure the parsed frontmatter contains all required keys.

    Raises ValueError if a required key is missing or falsy.
    """
    missing = [key for key in required_keys if not frontmatter.get(key)]
    if missing:
        raise ValueError(f"Missing required frontmatter keys: {', '.join(missing)}")
