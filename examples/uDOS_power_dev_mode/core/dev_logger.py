
from datetime import datetime, timezone
import os
import re
import json
from typing import IO, Optional, Dict, Any

REDACT_KEYS = re.compile(r"(token|secret|password|apikey|api_key|key)$", re.I)

def _now_iso_utc() -> str:
    # uDOS timestamp pattern: ISO8601 UTC (seconds precision) with Z
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _tizo_default() -> str:
    return os.getenv("UDOS_TIZO", "AUS-BNE")

def _zoom_default() -> int:
    try:
        return int(os.getenv("UDOS_ZOOM", "3"))
    except ValueError:
        return 3

def dev_log_path(tizo: Optional[str] = None, zoom: Optional[int] = None, root: str = "sandbox/logs") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    tizo = tizo or _tizo_default()
    zoom = zoom if zoom is not None else _zoom_default()
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, f"dev-{ts}_{tizo}_Z{zoom}.log")

def _redact_env_like(s: str) -> str:
    # aggressively redact anything that looks like an env assignment (FOO=...),
    # and any high-entropy tokens between quotes that are >24 chars.
    s = re.sub(r"\b[A-Z0-9_]{2,}=[^\s]+", lambda m: m.group(0).split("=")[0] + "=REDACTED", s)
    s = re.sub(r"(['\"])([A-Za-z0-9_\-]{24,})(['\"])", r"\1REDACTED\3", s)
    return s

def _redact_mapping(d: Dict[str, Any]) -> Dict[str, Any]:
    redacted = {}
    for k, v in d.items():
        if REDACT_KEYS.search(k):
            redacted[k] = "REDACTED"
        else:
            redacted[k] = v
    return redacted

def attach_user_context(msg: str, user_json_path: str = "sandbox/user.json") -> str:
    """Optionally append minimal user context from sandbox/user.json (if present)."""
    try:
        with open(user_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # safe: redact sensitive-looking keys, then compress to k=v pairs
        safe = _redact_mapping(data if isinstance(data, dict) else {})
        # only include 2-4 high-signal fields
        keys = [k for k in safe.keys() if k.lower() in ("workspace", "theme", "profile_version", "timezone", "tizo", "zoom")]
        compact = " ".join(f"{k}={safe[k]}" for k in keys)
        return f"{msg} | ctx: {compact}" if compact else msg
    except Exception:
        return msg

def dev_log(fp: IO[str], tizo: Optional[str], zoom: Optional[int], cmd: str, code: int, ms: int, msg: str, with_user_ctx: bool = False) -> None:
    # Never read .env, never echo env vars; redact any env-like content in msg.
    stamp = _now_iso_utc()
    tizo = tizo or _tizo_default()
    zoom = zoom if zoom is not None else _zoom_default()
    safe_msg = _redact_env_like(msg)
    if with_user_ctx:
        safe_msg = attach_user_context(safe_msg)
    line = f"{stamp} | {tizo} | Z{zoom} | {cmd} | {code} | {ms} | {safe_msg}".rstrip()
    fp.write(line + "\n")
    fp.flush()
