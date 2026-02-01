"""Tools for automation scripts to read health + provider logs."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.health_training import get_health_log_path
from core.services.logging_service import get_repo_root, get_logger

logger = get_logger("automation-monitor")


class AutomationMonitor:
    """Reads the enriched training payloads so automation can gate runs."""

    def __init__(self, memory_root: Optional[Path] = None):
        repo_root = get_repo_root()
        self.memory_root = Path(memory_root or repo_root / "memory")
        self.memory_root.mkdir(parents=True, exist_ok=True)
        self.health_log = get_health_log_path()
        self.provider_log = self.memory_root / "logs" / "provider-load.log"
        self.notification_log = self.memory_root / "logs" / "notification-history.log"

    def _read_last_json(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
            if not lines:
                return None
            return json.loads(lines[-1])
        except Exception as exc:
            logger.warning("[AutomationMonitor] Failed to read %s: %s", path.name, exc)
            return None

    def _read_recent_events(self, path: Path, limit: int = 5) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
            return [json.loads(line) for line in reversed(lines[-limit:]) if line]
        except Exception as exc:
            logger.warning("[AutomationMonitor] Failed to parse %s: %s", path.name, exc)
            return []

    def last_health_payload(self) -> Optional[Dict[str, Any]]:
        return self._read_last_json(self.health_log)

    def last_throttle_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self._read_recent_events(self.provider_log, limit=limit)

    def notification_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self._read_recent_events(self.notification_log, limit=limit)

    def summary(self) -> Dict[str, Any]:
        payload = self.last_health_payload() or {}
        self_heal = payload.get("self_heal", {})
        remaining = self_heal.get("remaining", 0)
        monitoring_summary = payload.get("monitoring_summary", {})
        throttles = self.last_throttle_events()
        notifications = self.notification_history()

        gate_reasons = []
        if remaining:
            gate_reasons.append(f"{remaining} Self-Heal issue(s)")
        summary_status = monitoring_summary.get("summary", {}).get("status")
        if summary_status and summary_status != "healthy":
            gate_reasons.append(f"Monitoring status: {summary_status}")
        if throttles:
            gate_reasons.append(f"{len(throttles)} throttle event(s)")

        gate_reason = "; ".join(gate_reasons)

        return {
            "health_payload": payload,
            "monitoring_summary": monitoring_summary,
            "self_heal": self_heal,
            "remaining": remaining,
            "notifications": notifications,
            "throttles": throttles,
            "should_gate": bool(gate_reasons),
            "gate_reason": gate_reason,
        }
