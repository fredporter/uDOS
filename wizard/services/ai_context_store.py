"""
AI Context Store
================

Builds a normalized context bundle for Wizard AI tools (Vibe/Ollama/Mistral).
Stores context in memory/ai/context.json and memory/ai/context.md.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.ai-context")


DEFAULT_FILES = [
    "AGENTS.md",
    "docs/_index.md",
    "docs/roadmap.md",
]


def _read_text(path: Path) -> str:
    try:
        return path.read_text()
    except Exception:
        return ""


def build_context_bundle() -> Dict[str, str]:
    repo_root = get_repo_root()
    context: Dict[str, str] = {}

    for rel in DEFAULT_FILES:
        path = repo_root / rel
        if path.exists():
            context[rel] = _read_text(path)

    # Current devlog (by month)
    devlog_dir = repo_root / "docs" / "devlog"
    if devlog_dir.exists():
        current_month = datetime.now().strftime("%Y-%m")
        devlog_path = devlog_dir / f"{current_month}.md"
        if devlog_path.exists():
            context[f"docs/devlog/{current_month}.md"] = _read_text(devlog_path)

    # Recent logs
    log_dir = repo_root / "memory" / "logs"
    if log_dir.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        for log_type in ["debug", "error", "system", "api", "session-commands"]:
            log_path = log_dir / f"{log_type}-{today}.log"
            if log_path.exists():
                context[f"logs/{log_type}-{today}.log"] = _read_text(log_path)[-4000:]

    return context


def write_context_bundle() -> Path:
    repo_root = get_repo_root()
    context_dir = repo_root / "memory" / "ai"
    context_dir.mkdir(parents=True, exist_ok=True)

    context = build_context_bundle()

    json_path = context_dir / "context.json"
    md_path = context_dir / "context.md"

    json_path.write_text(json.dumps(context, indent=2))

    md_parts: List[str] = []
    for name, content in context.items():
        md_parts.append(f"=== {name} ===\n{content}")
    md_path.write_text("\n\n".join(md_parts))

    logger.info(f"[WIZ] AI context bundle written to {json_path}")
    return json_path
