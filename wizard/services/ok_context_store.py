"""Logic assist context store."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_memory_dir, get_repo_root

logger = get_logger("wizard.ok-context")


DEFAULT_FILES = [
    "AGENTS.md",
    "docs/STATUS.md",
    "docs/README.md",
    "dev/ops/tasks.md",
    "dev/ops/tasks.json",
    "dev/ops/DEVLOG.md",
    "dev/docs/roadmap/ROADMAP.md",
]

WORKSPACE_FILES = {
    "@dev": [
        "dev/AGENTS.md",
        "dev/ops/AGENTS.md",
        "dev/docs/specs/V1-5-STABLE-RELEASE-PROGRAM.md",
    ],
    "dev": [
        "dev/AGENTS.md",
        "dev/ops/AGENTS.md",
        "dev/docs/specs/V1-5-STABLE-RELEASE-PROGRAM.md",
    ],
    "wizard": [
        "wizard/AGENTS.md",
    ],
    "core": [
        "core/AGENTS.md",
    ],
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text()
    except Exception:
        return ""


def _workspace_key(workspace: str | None) -> str:
    normalized = str(workspace or "core").strip().lower()
    if normalized.startswith("@"):
        return normalized
    return normalized


def _context_files_for_workspace(workspace: str | None) -> list[str]:
    selected: list[str] = list(DEFAULT_FILES)
    selected.extend(WORKSPACE_FILES.get(_workspace_key(workspace), []))
    deduped: list[str] = []
    seen: set[str] = set()
    for item in selected:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def build_ok_context_bundle(workspace: str | None = "core") -> Dict[str, str]:
    repo_root = get_repo_root()
    context: Dict[str, str] = {}

    for rel in _context_files_for_workspace(workspace):
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


def build_ok_context_payload(workspace: str | None = "core") -> Dict[str, Any]:
    context = build_ok_context_bundle(workspace=workspace)
    digest = hashlib.sha256()
    for name in sorted(context):
        digest.update(name.encode("utf-8"))
        digest.update(b"\n")
        digest.update(context[name].encode("utf-8"))
        digest.update(b"\n---\n")
    return {
        "workspace": str(workspace or "core"),
        "hash": digest.hexdigest(),
        "files": sorted(context.keys()),
        "count": len(context),
        "bundle": context,
    }


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


def write_ok_context_bundle(workspace: str | None = "core") -> Path:
    memory_dir = get_memory_dir()
    payload = build_ok_context_payload(workspace=workspace)
    context = payload["bundle"]
    json_path = _write_context_bundle(context, memory_dir / "ok")
    logger.info(f"[WIZ] OK context bundle written to {json_path}")
    return json_path
