"""Command normalization and parsing helpers for uCODE routes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException


OK_CODING_MODES = frozenset({"EXPLAIN", "DIFF", "PATCH"})


@dataclass
class ParsedOKCommand:
    command: str
    ok_args: str
    ok_tokens: list[str]
    ok_mode: str


@dataclass
class OKCodingRequest:
    mode: str
    path: Path
    prompt: str
    use_cloud: bool


def normalize_ok_command(command: str) -> str:
    """Normalize OK command by converting '?' prefix to 'OK'."""
    if command.startswith("?"):
        rest = command[1:].strip()
        return f"OK {rest}".strip()
    return command


def parse_ok_command(command: str) -> ParsedOKCommand | None:
    """Parse OK command into structured components."""
    normalized = normalize_ok_command(command)
    upper = normalized.upper()
    if not (upper == "OK" or upper.startswith("OK ")):
        return None

    ok_args = normalized[2:].strip()
    ok_tokens = ok_args.split() if ok_args else []
    ok_mode = ok_tokens[0].upper() if ok_tokens else "LOCAL"
    return ParsedOKCommand(
        command=normalized,
        ok_args=ok_args,
        ok_tokens=ok_tokens,
        ok_mode=ok_mode,
    )


def parse_ok_file_args(args: str) -> Dict[str, Any]:
    """Parse OK file command arguments (e.g., 'path.py 10 20 --cloud')."""
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
    """Load file content with optional line range."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    content = path.read_text(encoding="utf-8", errors="ignore")
    if line_start and line_end:
        lines = content.splitlines()
        content = "\n".join(lines[line_start - 1 : line_end])
    return content


def build_ok_file_prompt(mode: str, path: Path, content: str) -> str:
    """Build OK file prompt for coding modes (EXPLAIN, DIFF, PATCH)."""
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


def shell_safe(command: str) -> bool:
    """Check if shell command is safe (no destructive operations)."""
    destructive_keywords = {"rm", "mv", ">", "|", "sudo", "rmdir", "dd", "format"}
    cmd_lower = command.lower()
    return not any(kw in cmd_lower for kw in destructive_keywords)


def prepare_ok_coding_request(
    *,
    parsed: ParsedOKCommand,
    is_dev_mode_active: Callable[[], bool],
    logger: Any,
    corr_id: str,
    rejected_log_message: str,
    missing_file_log_message: str,
) -> OKCodingRequest:
    """Prepare OK coding request from parsed command."""
    if parsed.ok_mode not in OK_CODING_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported OK file mode: {parsed.ok_mode}",
        )
    if not is_dev_mode_active():
        raise HTTPException(
            status_code=409,
            detail="OK coding commands require the active Dev extension lane.",
        )

    parsed_file_args = parse_ok_file_args(" ".join(parsed.ok_tokens[1:]))
    if parsed_file_args.get("error"):
        logger.warn(
            rejected_log_message,
            ctx={"corr_id": corr_id, "error": parsed_file_args.get("error")},
        )
        raise HTTPException(status_code=400, detail=parsed_file_args.get("error"))

    path = parsed_file_args["path"]
    try:
        content = load_ok_file_content(
            path,
            line_start=parsed_file_args.get("line_start"),
            line_end=parsed_file_args.get("line_end"),
        )
    except HTTPException:
        logger.warn(
            missing_file_log_message,
            ctx={"corr_id": corr_id, "path": str(path)},
        )
        raise

    return OKCodingRequest(
        mode=parsed.ok_mode,
        path=path,
        prompt=build_ok_file_prompt(parsed.ok_mode, path, content),
        use_cloud=bool(parsed_file_args.get("use_cloud")),
    )
