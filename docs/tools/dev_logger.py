#!/usr/bin/env python3
"""
uDOS Dev Logger

Provides structured logging for uDOS dev sessions with:
- ISO8601Z timestamps (UTC)
- TIZO and zoom context
- Automatic secrets redaction
- Optional user context from memory/sandbox/user.json

Format: ISO8601Z | TIZO | Z{zoom} | CMD | CODE | MS | MSG | [ctx: ...]
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


def dev_log_path(tizo: str = "AUS-BNE", zoom: int = 3) -> Path:
    """
    Generate dev log file path in memory/logs/

    Format: dev-YYYYMMDD-HHMMSS_TIZO_Z{n}.log
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"dev-{timestamp}_{tizo}_Z{zoom}.log"

    # Ensure memory/logs exists
    log_dir = Path(__file__).parent.parent / "memory" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir / filename


def _redact_secrets(text: str) -> str:
    """
    Redact sensitive information from log messages.

    Patterns redacted:
    - Environment variable patterns: ${VAR}, $VAR
    - API keys, tokens, secrets (case insensitive)
    - Common secret patterns
    """
    # Environment variable patterns
    text = re.sub(r'\$\{[^}]+\}', '[REDACTED_ENV]', text)
    text = re.sub(r'\$[A-Z_][A-Z0-9_]*', '[REDACTED_ENV]', text)

    # API keys, tokens, secrets (case insensitive)
    secret_patterns = [
        r'["\']?[a-zA-Z0-9_]*(?:token|key|secret|apikey|password|pwd)["\']?\s*[:=]\s*["\']?[^"\s]+["\']?',
        r'Bearer\s+[a-zA-Z0-9_-]+',
        r'[a-f0-9]{32,}',  # Long hex strings (potential hashes/keys)
    ]

    for pattern in secret_patterns:
        text = re.sub(pattern, '[REDACTED_SECRET]', text, flags=re.IGNORECASE)

    return text


def _load_user_context() -> Dict[str, Any]:
    """
    Load safe user context from memory/sandbox/user.json

    Only includes safe keys: workspace, theme, tizo, zoom
    """
    try:
        user_file = Path(__file__).parent.parent / "memory" / "sandbox" / "user.json"
        if user_file.exists():
            with open(user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Only extract safe keys
            safe_keys = {'workspace', 'theme', 'tizo', 'zoom'}
            return {k: v for k, v in data.items() if k in safe_keys}
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass

    return {}


def dev_log(
    fp,
    tizo: str,
    zoom: int,
    command: str,
    code: int,
    ms: int,
    message: str,
    with_user_ctx: bool = False
) -> None:
    """
    Write a dev log entry to the file pointer.

    Args:
        fp: Open file pointer
        tizo: Location code (e.g., "AUS-BNE")
        zoom: Zoom level (e.g., 3)
        command: Command executed
        code: Return code (0 = success)
        ms: Execution time in milliseconds
        message: Log message
        with_user_ctx: Include user context from memory/sandbox/user.json
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Redact secrets from all components
    safe_command = _redact_secrets(command)
    safe_message = _redact_secrets(message)

    # Build log line
    log_parts = [
        timestamp,
        tizo,
        f"Z{zoom}",
        safe_command,
        str(code),
        str(ms),
        safe_message
    ]

    # Add user context if requested
    if with_user_ctx:
        user_ctx = _load_user_context()
        if user_ctx:
            ctx_str = " ".join(f"{k}={v}" for k, v in user_ctx.items())
            log_parts.append(f"ctx: {ctx_str}")

    # Write log line
    log_line = " | ".join(log_parts)
    fp.write(log_line + "\n")
    fp.flush()


def quick_dev_log(
    tizo: str,
    zoom: int,
    command: str,
    code: int,
    ms: int,
    message: str,
    with_user_ctx: bool = False
) -> Path:
    """
    Quick dev log - creates file and writes single entry.

    Returns the path to the log file created.
    """
    log_path = dev_log_path(tizo, zoom)

    with open(log_path, "a", encoding="utf-8") as fp:
        dev_log(fp, tizo, zoom, command, code, ms, message, with_user_ctx)

    return log_path


# Example usage and test function
if __name__ == "__main__":
    # Test the logger
    test_tizo = "AUS-BNE"
    test_zoom = 3

    path = dev_log_path(test_tizo, test_zoom)
    print(f"Log path: {path}")

    with open(path, "a", encoding="utf-8") as fp:
        dev_log(fp, test_tizo, test_zoom, "TEST --init", 0, 42, "dev logger initialized", with_user_ctx=True)
        dev_log(fp, test_tizo, test_zoom, "TEST --secrets", 0, 15, "testing secret=${API_KEY} and token=abc123", with_user_ctx=False)

    print(f"Test logs written to: {path}")
