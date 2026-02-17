"""Wizard extension hot-reload service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.path_utils import get_repo_root


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ExtensionHotReloadService:
    """Tracks extension file changes and emits hot-reload snapshots."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else get_repo_root()
        self._state_dir = self.repo_root / "memory" / "wizard" / "extensions"
        self._state_path = self._state_dir / "hot_reload_state.json"
        self._state_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        if not self._state_path.exists():
            return {"last_run_at": None, "last_token": None, "last_snapshot": {}, "history": []}
        try:
            return json.loads(self._state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"last_run_at": None, "last_token": None, "last_snapshot": {}, "history": []}

    def _save_state(self, payload: Dict[str, Any]) -> None:
        self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_snapshot(self, extensions: List[Dict[str, Any]]) -> Dict[str, Any]:
        snapshot: Dict[str, Any] = {}
        for ext in extensions:
            ext_id = ext.get("id")
            ext_path = ext.get("path")
            main_file = ext.get("main_file")
            if not ext_id or not ext_path or not main_file:
                continue
            target = self.repo_root / ext_path / main_file
            if target.exists():
                try:
                    snapshot[ext_id] = int(target.stat().st_mtime)
                except Exception:
                    snapshot[ext_id] = 0
            else:
                snapshot[ext_id] = 0
        return snapshot

    def hot_reload(self, extensions: List[Dict[str, Any]]) -> Dict[str, Any]:
        state = self._load_state()
        previous = state.get("last_snapshot") or {}
        current = self._build_snapshot(extensions)
        changed_ids = sorted([ext_id for ext_id, mtime in current.items() if previous.get(ext_id) != mtime])
        run_at = _utc_now()
        token = f"ext_reload_{run_at.replace(':', '').replace('-', '')}"

        event = {
            "run_at": run_at,
            "reload_token": token,
            "changed_extensions": changed_ids,
            "changed_count": len(changed_ids),
            "total_extensions": len(current),
        }
        history = state.get("history") or []
        history.append(event)
        history = history[-200:]
        state.update(
            {
                "last_run_at": run_at,
                "last_token": token,
                "last_snapshot": current,
                "history": history,
            }
        )
        self._save_state(state)
        return event

    def get_status(self, limit: int = 20) -> Dict[str, Any]:
        state = self._load_state()
        history = state.get("history") or []
        limited = history[-max(1, min(limit, 200)) :]
        return {
            "last_run_at": state.get("last_run_at"),
            "last_token": state.get("last_token"),
            "history_count": len(limited),
            "history": limited,
            "state_path": str(self._state_path),
        }


_extension_hot_reload_service: Optional[ExtensionHotReloadService] = None


def get_extension_hot_reload_service(
    repo_root: Optional[Path] = None,
) -> ExtensionHotReloadService:
    global _extension_hot_reload_service
    if repo_root is not None:
        return ExtensionHotReloadService(repo_root=repo_root)
    if _extension_hot_reload_service is None:
        _extension_hot_reload_service = ExtensionHotReloadService()
    return _extension_hot_reload_service
