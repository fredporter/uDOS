"""
Story Service (Core)
====================

Centralized parsing logic for `-story.md` documents. This ensures every subsystem
that consumes story files (Wizard setup, dashboards, TUI) relies on a single
validated payload rather than duplicating markdown parsing logic client-side.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Sequence, Optional

import yaml

from core.services.markdown_frontmatter import (
    parse_markdown_frontmatter,
    validate_frontmatter,
)

LOGGER = logging.getLogger("core.story")

STORY_BLOCK_REGEX = re.compile(r"```story\n([\s\S]*?)\n```", re.MULTILINE)
SECTION_SEPARATOR = re.compile(r"\n---\n")
DEFAULT_SECTION_TITLE = "Section"


def parse_story_document(
    content: str, required_frontmatter_keys: Sequence[str] | None = None
) -> Dict[str, Any]:
    """
    Parse a complete story markdown document into a structured payload.
    """
    frontmatter, body = parse_markdown_frontmatter(content)
    if required_frontmatter_keys:
        validate_frontmatter(frontmatter, required_frontmatter_keys)

    sections = []
    for idx, raw_section in enumerate(_split_sections(body)):
        section = _parse_section(raw_section, index=idx)
        if section["content"] or section["questions"]:
            sections.append(section)

    answers = {**(frontmatter.get("variables") or {})}
    for section in sections:
        for question in section["questions"]:
            name = question.get("name")
            if name and name not in answers:
                answers[name] = question.get("value") or ""

    return {
        "frontmatter": frontmatter,
        "sections": sections,
        "answers": answers,
        "currentSectionIndex": 0,
        "isComplete": False,
        "body": body.strip(),
        "metadata": {},
    }


def _split_sections(body: str) -> List[str]:
    if not body:
        return []
    parts = SECTION_SEPARATOR.split(body)
    return [part.strip() for part in parts if part.strip()]


def _parse_section(section_text: str, index: int) -> Dict[str, Any]:
    trimmed = section_text.strip()
    lines = trimmed.splitlines()
    title = f"{DEFAULT_SECTION_TITLE} {index + 1}"
    content_start = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip() or title
        content_start = 1
    content = "\n".join(lines[content_start:]).strip()
    questions = _extract_story_blocks(trimmed)
    return {
        "id": f"section-{index}",
        "title": title,
        "content": content,
        "questions": questions,
        "order": index,
    }


def _extract_story_blocks(section_text: str) -> List[Dict[str, Any]]:
    matches = STORY_BLOCK_REGEX.finditer(section_text)
    questions = []
    for match in matches:
        block = match.group(1)
        field = _parse_story_block(block)
        if field:
            questions.append(field)
    return questions


def _parse_story_block(block_content: str) -> Optional[Dict[str, Any]]:
    try:
        data = yaml.safe_load(block_content) or {}
    except Exception as exc:
        LOGGER.warning("Failed to parse story block YAML: %s", exc)
        return None

    name = data.get("name")
    label = data.get("label")
    if not name or not label:
        LOGGER.warning("Story block missing required name/label: %s", block_content)
        return None

    field_type = str(data.get("type") or "text").lower()
    required = bool(data.get("required"))

    known_keys = {
        "name",
        "label",
        "type",
        "required",
        "placeholder",
        "options",
        "value",
        "validation",
    }

    meta = {k: v for k, v in data.items() if k not in known_keys}

    field: Dict[str, Any] = {
        "name": name,
        "label": label,
        "type": field_type,
        "required": required,
        "placeholder": data.get("placeholder"),
        "options": data.get("options")
        if isinstance(data.get("options"), list)
        else ([] if field_type in {"select", "radio"} else None),
        "value": data.get("value"),
        "meta": meta or None,
        "validation": data.get("validation"),
    }
    # Clean up falsy optional values
    for key in ("placeholder", "options", "value", "validation"):
        if not field.get(key):
            field.pop(key, None)
    return field
