"""Canonical launch/session state service for Wizard platform adapters."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wizard.services.deploy_mode import is_managed_mode
from wizard.services.store import get_wizard_store

LIFECYCLE_STATES = ("planned", "starting", "ready", "stopping", "stopped", "error")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class LaunchSessionService:
    """Manage canonical launch sessions under memory/wizard/launch."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self._managed = is_managed_mode()
        self.store = get_wizard_store()
        self.state_dir = self.repo_root / "memory" / "wizard" / "launch"
        if not self._managed:
            self.state_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        return self.state_dir / f"{session_id}.json"

    def _write_session(self, payload: dict[str, Any]) -> None:
        if self._managed:
            session_id = str(payload["session_id"])
            try:
                self.store.get_launch_session(session_id)
                self.store.update_launch_session(session_id, payload)
            except FileNotFoundError:
                self.store.create_launch_session(payload)
            return
        self._session_path(str(payload["session_id"])).write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def get_session(self, session_id: str) -> dict[str, Any]:
        if self._managed:
            return self.store.get_launch_session(session_id)
        path = self._session_path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"Launch session not found: {session_id}")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_sessions(self, *, target: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self._managed:
            return self.store.list_launch_sessions(target=target, limit=limit)
        normalized_target = (target or "").strip().lower()
        sessions: list[dict[str, Any]] = []
        for path in sorted(self.state_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if normalized_target and str(payload.get("target", "")).strip().lower() != normalized_target:
                continue
            sessions.append(payload)
            if len(sessions) >= limit:
                return sessions
        return sessions

    def create_session(
        self,
        *,
        target: str,
        mode: str,
        launcher: str | None = None,
        workspace: str | None = None,
        profile_id: str | None = None,
        auth: dict[str, Any] | None = None,
        state: str = "planned",
    ) -> dict[str, Any]:
        normalized_state = state.strip().lower()
        if normalized_state not in LIFECYCLE_STATES:
            raise ValueError(f"Unsupported launch lifecycle state: {state}")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        session_id = f"{target.strip().lower().replace(' ', '-')}-{timestamp}-{secrets.token_hex(4)}"
        payload = {
            "session_id": session_id,
            "target": target,
            "mode": mode,
            "launcher": launcher,
            "workspace": workspace,
            "profile_id": profile_id,
            "auth": auth or {},
            "state": normalized_state,
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
        }
        self._write_session(payload)
        return payload

    def transition(
        self,
        session_id: str,
        state: str,
        *,
        error: str | None = None,
        updates: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_state = state.strip().lower()
        if normalized_state not in LIFECYCLE_STATES:
            raise ValueError(f"Unsupported launch lifecycle state: {state}")
        payload = self.get_session(session_id)
        payload["state"] = normalized_state
        payload["updated_at"] = _utc_now()
        if updates:
            payload.update(updates)
        if error:
            payload["error"] = error
        elif "error" in payload and normalized_state != "error":
            payload.pop("error", None)
        self._write_session(payload)
        return payload


def get_launch_session_service(repo_root: Path | None = None) -> LaunchSessionService:
    return LaunchSessionService(repo_root=repo_root)
