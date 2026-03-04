"""Logic Assist Context Store."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_memory_dir, get_repo_root

logger = get_logger("wizard.ok-context")


DEFAULT_FILES = [
    "AGENTS.md",
    "docs/STATUS.md",
    "docs/README.md",
    "dev/ops/DEVLOG.md",
    "dev/docs/roadmap/ROADMAP.md",
]


def _read_text(path: Path) -> str:
    try:
        return path.read_text()
    except Exception:
        return ""


def build_ok_context_bundle() -> Dict[str, str]:
    repo_root = get_repo_root()
    context: Dict[str, str] = {}

    for rel in DEFAULT_FILES:
        path = repo_root / rel
        if path.exists():
            context[rel] = _read_text(path)

    # Recent logs
    log_dir = repo_root / "memory" / "logs"
    if log_dir.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        for log_type in ["debug", "error", "system", "api", "session-commands"]:
            log_path = log_dir / f"{log_type}-{today}.log"
            if log_path.exists():
                context[f"logs/{log_type}-{today}.log"] = _read_text(log_path)[-4000:]

    return context


def _write_context_bundle(context: Dict[str, str], context_dir: Path) -> Path:
    context_dir.mkdir(parents=True, exist_ok=True)
    json_path = context_dir / "context.json"
    md_path = context_dir / "context.md"
    json_path.write_text(json.dumps(context, indent=2), encoding="utf-8")

    md_parts: List[str] = []
    for name, content in context.items():
        md_parts.append(f"=== {name} ===\n{content}")
    md_path.write_text("\n\n".join(md_parts), encoding="utf-8")
    return json_path


def write_ok_context_bundle() -> Path:
    memory_dir = get_memory_dir()
    context = build_ok_context_bundle()
    json_path = _write_context_bundle(context, memory_dir / "ok")
    logger.info(f"[WIZ] OK context bundle written to {json_path}")
    return json_path
