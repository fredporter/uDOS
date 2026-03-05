"""Core network gate policy for bootstrap downloads and strict default deny."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core.services.loopback_host_utils import is_loopback_host
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("network-gate-policy")
_DEFAULT_TTL_SECONDS = 20 * 60
_EVENT_HISTORY_LIMIT = 50


class NetworkGateBlockedError(PermissionError):
    """Raised when a core network operation is blocked by gate policy."""


def _state_path() -> Path:
    return Path(get_repo_root()) / "memory" / "system" / "network_gate_state.json"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(ts: datetime) -> str:
    return ts.replace(microsecond=0).isoformat()


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _default_state() -> dict[str, Any]:
    return {
        "gate_open": False,
        "scope": "bootstrap-downloads",
        "opened_at": "",
        "expires_at": "",
        "opened_by": "",
        "close_reason": "default-closed",
        "events": [],
    }


def _read_state() -> dict[str, Any]:
    path = _state_path()
    if not path.exists():
        return _default_state()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            merged = _default_state()
            merged.update(payload)
            return merged
    except Exception as exc:
        logger.warning("[NETGATE] Failed to read state file: %s", exc)
    return _default_state()


def _write_state(state: dict[str, Any]) -> dict[str, Any]:
    events = state.get("events")
    if not isinstance(events, list):
        state["events"] = []
    elif len(events) > _EVENT_HISTORY_LIMIT:
        state["events"] = events[-_EVENT_HISTORY_LIMIT:]
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def _append_event(
    state: dict[str, Any],
    *,
    action: str,
    reason: str,
    opened_by: str,
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    events = state.get("events")
    if not isinstance(events, list):
        events = []
    event: dict[str, Any] = {
        "timestamp": _iso(_utcnow()),
        "action": action,
        "reason": reason,
    }
    if opened_by:
        event["opened_by"] = opened_by
    if ttl_seconds is not None:
        event["ttl_seconds"] = int(ttl_seconds)
    events.append(event)
    state["events"] = events[-_EVENT_HISTORY_LIMIT:]
    return state


def _is_loopback_host(host: str | None) -> bool:
    return is_loopback_host(host)


def is_loopback_url(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    return _is_loopback_host(parsed.hostname)


def is_first_run_setup_pending() -> bool:
    env_path = Path(get_repo_root()) / ".env"
    if not env_path.exists():
        return True
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() != "USER_NAME":
                continue
            if value.strip().strip('"\''):
                return False
    except Exception:
        return True
    return True


def gate_status() -> dict[str, Any]:
    state = _read_state()
    if not state.get("gate_open"):
        return state
    expires_at = _parse_ts(str(state.get("expires_at") or ""))
    if expires_at is None:
        return state
    if _utcnow() <= expires_at:
        return state
    return close_bootstrap_gate(reason="expired")


def open_bootstrap_gate(
    *,
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
    opened_by: str = "core.setup",
    reason: str = "bootstrap-downloads",
) -> dict[str, Any]:
    ttl = max(1, int(ttl_seconds))
    now = _utcnow()
    expires_at = now + timedelta(seconds=ttl)
    current = _read_state()
    state = {
        "gate_open": True,
        "scope": "bootstrap-downloads",
        "opened_at": _iso(now),
        "expires_at": _iso(expires_at),
        "opened_by": opened_by,
        "close_reason": reason,
        "events": current.get("events", []),
    }
    _append_event(
        state,
        action="open",
        reason=reason,
        opened_by=opened_by,
        ttl_seconds=ttl,
    )
    logger.info(
        "[NETGATE] Opened bootstrap gate (opened_by=%s ttl=%ss)",
        opened_by,
        ttl_seconds,
    )
    return _write_state(state)


def close_bootstrap_gate(*, reason: str = "closed") -> dict[str, Any]:
    current = _read_state()
    state = {
        "gate_open": False,
        "scope": str(current.get("scope") or "bootstrap-downloads"),
        "opened_at": str(current.get("opened_at") or ""),
        "expires_at": str(current.get("expires_at") or ""),
        "opened_by": str(current.get("opened_by") or ""),
        "close_reason": reason,
        "events": current.get("events", []),
    }
    _append_event(
        state,
        action="close",
        reason=reason,
        opened_by=str(current.get("opened_by") or ""),
    )
    logger.info("[NETGATE] Closed bootstrap gate (reason=%s)", reason)
    return _write_state(state)


def allow_non_loopback_core_network() -> bool:
    return bool(gate_status().get("gate_open"))


def gate_events(*, limit: int = 20) -> list[dict[str, Any]]:
    state = gate_status()
    events = state.get("events")
    if not isinstance(events, list):
        return []
    trimmed = events[-max(1, int(limit)) :]
    return list(reversed([e for e in trimmed if isinstance(e, dict)]))


def ensure_url_allowed(url: str, *, purpose: str) -> None:
    if is_loopback_url(url):
        return
    if allow_non_loopback_core_network():
        return
    raise NetworkGateBlockedError(
        f"Core network gate is closed for {purpose}: {url}. "
        "Use temporary bootstrap gate during setup or route through Wizard."
    )


@contextmanager
def bootstrap_download_gate(
    *,
    opened_by: str = "core.setup",
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
):
    open_bootstrap_gate(opened_by=opened_by, ttl_seconds=ttl_seconds)
    try:
        yield gate_status()
    finally:
        close_bootstrap_gate(reason="setup-complete")
