"""Helper utilities for uCODE bridge route parsing and prompt construction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import HTTPException


def shell_safe(command: str) -> bool:
    destructive_keywords = {"rm", "mv", ">", "|", "sudo", "rmdir", "dd", "format"}
    cmd_lower = command.lower()
    return not any(kw in cmd_lower for kw in destructive_keywords)


def parse_ok_file_args(args: str) -> Dict[str, Any]:
    tokens = args.strip().split()
    use_cloud = False
    clean_tokens = []
    for token in tokens:
        if token.lower() in ("--cloud", "--onvibe"):
            use_cloud = True
        else:
            clean_tokens.append(token)

    if not clean_tokens:
        return {"error": "Missing file path", "use_cloud": use_cloud}

    file_token = clean_tokens[0]
    line_start: Optional[int] = None
    line_end: Optional[int] = None

    if len(clean_tokens) >= 3 and clean_tokens[1].isdigit() and clean_tokens[2].isdigit():
        line_start = int(clean_tokens[1])
        line_end = int(clean_tokens[2])
    elif len(clean_tokens) >= 2 and any(
        sep in clean_tokens[1] for sep in (":", "-", "..")
    ):
        parts = clean_tokens[1].replace("..", ":").replace("-", ":").split(":")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            line_start = int(parts[0])
            line_end = int(parts[1])

    path = Path(file_token)
    try:
        from core.services.logging_api import get_repo_root

        if not path.is_absolute():
            path = get_repo_root() / path
    except Exception:
        if not path.is_absolute():
            path = Path.cwd() / path

    return {
        "path": path,
        "line_start": line_start,
        "line_end": line_end,
        "use_cloud": use_cloud,
    }


def load_ok_file_content(
    path: Path, line_start: Optional[int] = None, line_end: Optional[int] = None
) -> str:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    content = path.read_text(encoding="utf-8", errors="ignore")
    if line_start and line_end:
        lines = content.splitlines()
        content = "\n".join(lines[line_start - 1 : line_end])
    return content


def build_ok_file_prompt(mode: str, path: Path, content: str) -> str:
    mode_upper = mode.upper()
    if mode_upper == "EXPLAIN":
        return (
            f"Explain this code from {path}:\n\n"
            f"```python\n{content}\n```\n\n"
            "Provide: 1) purpose, 2) key logic, 3) risks or follow-ups."
        )
    if mode_upper == "DIFF":
        return (
            f"Propose a unified diff for improvements to {path}.\n\n"
            f"```python\n{content}\n```\n\n"
            "Return a unified diff only (no commentary)."
        )
    if mode_upper == "PATCH":
        return (
            f"Draft a patch (unified diff) for {path}. Keep the diff minimal.\n\n"
            f"```python\n{content}\n```\n\n"
            "Return a unified diff only."
        )
    raise HTTPException(status_code=400, detail=f"Unsupported OK file mode: {mode}")
