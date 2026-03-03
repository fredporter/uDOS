from __future__ import annotations

import re

from .contracts import IntentFrame


_WORKFLOW_ID = r"(?P<workflow_id>[A-Za-z0-9._:-]+)"
_TEMPLATE_ID = r"(?P<template_id>[A-Za-z0-9._:-]+)"
_PATH_VALUE = r"(?P<path>[A-Za-z0-9_./:-]+)"
_SOURCE_PATH = r"(?P<source_path>[A-Za-z0-9_./:-]+)"
_TARGET_PATH = r"(?P<target_path>[A-Za-z0-9_./:-]+)"


_PATTERNS: list[tuple[re.Pattern[str], str, str, callable]] = [
    (
        re.compile(r"^\s*UCODE\b", re.IGNORECASE),
        "command",
        "ucode.raw",
        lambda match, text: {"command_text": text.strip()},
    ),
    (
        re.compile(r"^\s*WORKFLOW\s+LIST\b", re.IGNORECASE),
        "workflow",
        "workflow.list",
        lambda match, text: {},
    ),
    (
        re.compile(rf"\bworkflow\s+status\s+{_WORKFLOW_ID}\b", re.IGNORECASE),
        "workflow",
        "workflow.status",
        lambda match, text: {"workflow_id": match.group("workflow_id")},
    ),
    (
        re.compile(rf"\bworkflow\s+run\s+{_WORKFLOW_ID}\b", re.IGNORECASE),
        "workflow",
        "workflow.run",
        lambda match, text: {"workflow_id": match.group("workflow_id")},
    ),
    (
        re.compile(rf"\bworkflow\s+approve\s+{_WORKFLOW_ID}\b", re.IGNORECASE),
        "workflow",
        "workflow.approve",
        lambda match, text: {"workflow_id": match.group("workflow_id")},
    ),
    (
        re.compile(rf"\bworkflow\s+escalate\s+{_WORKFLOW_ID}\b", re.IGNORECASE),
        "workflow",
        "workflow.escalate",
        lambda match, text: {"workflow_id": match.group("workflow_id")},
    ),
    (
        re.compile(
            rf"\b(?:new|create)\s+workflow\s+{_TEMPLATE_ID}(?:\s+as\s+{_WORKFLOW_ID})?\b",
            re.IGNORECASE,
        ),
        "workflow",
        "workflow.new",
        lambda match, text: {
            "template_id": match.group("template_id"),
            "workflow_id": match.groupdict().get("workflow_id", ""),
        },
    ),
    (
        re.compile(r"\b(?:project\s+)?status\b", re.IGNORECASE),
        "guidance",
        "project.status",
        lambda match, text: {},
    ),
    (
        re.compile(
            rf"\b(?:browse|open|show)\s+(?:knowledge(?:-bank)?|library|seed)\b(?:\s+{_PATH_VALUE})?",
            re.IGNORECASE,
        ),
        "knowledge",
        "knowledge.browse",
        lambda match, text: {"knowledge_path": match.groupdict().get("path", "")},
    ),
    (
        re.compile(
            rf"\b(?:duplicate|copy)\s+(?:template|runbook|workflow|mission)\s+{_SOURCE_PATH}\s+(?:to|into)\s+{_TARGET_PATH}\b",
            re.IGNORECASE,
        ),
        "knowledge",
        "knowledge.duplicate",
        lambda match, text: {
            "source_path": match.group("source_path"),
            "target_path": match.group("target_path"),
        },
    ),
    (
        re.compile(
            r"\b(?:capture|gather|summari[sz]e|classify|enrich)\b",
            re.IGNORECASE,
        ),
        "knowledge",
        "knowledge.capture",
        lambda match, text: {"text": text.strip()},
    ),
]


def parse_input(text: str) -> list[IntentFrame]:
    normalized = text.strip()
    if not normalized:
        return []

    frames: list[IntentFrame] = []
    for pattern, input_class, intent, slot_factory in _PATTERNS:
        match = pattern.search(normalized)
        if not match:
            continue
        frames.append(
            IntentFrame(
                input_class=input_class,
                intent=intent,
                slots=slot_factory(match, normalized),
                confidence=0.8,
            )
        )

    if frames:
        return _dedupe_frames(frames)

    return [
        IntentFrame(
            input_class="guidance",
            intent="guidance.plan",
            slots={"text": normalized},
            confidence=0.2,
        )
    ]


def parse_primary_input(text: str) -> IntentFrame | None:
    frames = parse_input(text)
    if not frames:
        return None
    return frames[0]


def _dedupe_frames(frames: list[IntentFrame]) -> list[IntentFrame]:
    seen: set[tuple[str, str, tuple[tuple[str, str], ...]]] = set()
    unique: list[IntentFrame] = []
    for frame in frames:
        key = (
            frame.input_class,
            frame.intent,
            tuple(sorted((k, str(v)) for k, v in frame.slots.items())),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(frame)
    return unique
