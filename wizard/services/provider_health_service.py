"""Provider health checks and availability monitoring for Wizard."""

from __future__ import annotations

import json
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.integration_registry import get_provider_definitions
from wizard.services.path_utils import get_repo_root


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ProviderHealthService:
    """Runs provider availability checks and stores monitoring history."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else get_repo_root()
        self.providers = get_provider_definitions()
        self._lock = threading.Lock()
        self._state_dir = self.repo_root / "memory" / "wizard" / "providers"
        self._state_path = self._state_dir / "provider_health_state.json"
        self._state_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _run_shell_check(cmd: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=8,
            )
            return {
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "detail": (result.stderr or result.stdout or "").strip(),
            }
        except Exception as exc:
            return {"ok": False, "returncode": -1, "detail": str(exc)}

    def _load_state(self) -> Dict[str, Any]:
        if not self._state_path.exists():
            return {"last_checked_at": None, "checks": [], "history": []}
        try:
            return json.loads(self._state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"last_checked_at": None, "checks": [], "history": []}

    def _save_state(self, payload: Dict[str, Any]) -> None:
        self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def run_checks(self) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        healthy = 0
        for provider_id, provider in self.providers.items():
            check_cmd = provider.get("check_cmd")
            if check_cmd:
                result = self._run_shell_check(check_cmd)
                available = bool(result["ok"])
                detail = result["detail"] or ("available" if available else "unavailable")
            else:
                available = True
                detail = "no check_cmd configured; assumed available"
            if available:
                healthy += 1
            checks.append(
                {
                    "provider_id": provider_id,
                    "name": provider.get("name"),
                    "available": available,
                    "status": "healthy" if available else "degraded",
                    "detail": detail,
                }
            )

        snapshot = {
            "checked_at": _utc_now(),
            "total": len(checks),
            "healthy": healthy,
            "degraded": max(0, len(checks) - healthy),
            "checks": checks,
        }

        with self._lock:
            state = self._load_state()
            history = state.get("history") or []
            history.append(snapshot)
            history = history[-200:]
            state.update(
                {
                    "last_checked_at": snapshot["checked_at"],
                    "checks": checks,
                    "history": history,
                    "summary": {
                        "total": snapshot["total"],
                        "healthy": snapshot["healthy"],
                        "degraded": snapshot["degraded"],
                    },
                }
            )
            self._save_state(state)

        return snapshot

    def get_summary(self, auto_check_if_stale: bool = True, stale_seconds: int = 300) -> Dict[str, Any]:
        with self._lock:
            state = self._load_state()
        last_checked_at = state.get("last_checked_at")

        if auto_check_if_stale:
            should_refresh = True
            if last_checked_at:
                try:
                    last = datetime.fromisoformat(last_checked_at.replace("Z", "+00:00"))
                    should_refresh = (datetime.now(timezone.utc) - last).total_seconds() > stale_seconds
                except Exception:
                    should_refresh = True
            if should_refresh:
                return self.run_checks()

        return {
            "checked_at": last_checked_at,
            "total": (state.get("summary") or {}).get("total", len(state.get("checks") or [])),
            "healthy": (state.get("summary") or {}).get("healthy", 0),
            "degraded": (state.get("summary") or {}).get("degraded", 0),
            "checks": state.get("checks") or [],
        }

    def get_history(self, limit: int = 20) -> Dict[str, Any]:
        with self._lock:
            state = self._load_state()
        history = state.get("history") or []
        limited = history[-max(1, min(limit, 200)) :]
        return {"count": len(limited), "history": limited}


_provider_health_service: Optional[ProviderHealthService] = None


def get_provider_health_service(repo_root: Optional[Path] = None) -> ProviderHealthService:
    global _provider_health_service
    if repo_root is not None:
        return ProviderHealthService(repo_root=repo_root)
    if _provider_health_service is None:
        _provider_health_service = ProviderHealthService()
    return _provider_health_service
