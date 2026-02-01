"""Monitoring assistant used by the Wizard gateway telemetry tooling."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Optional, Any, Tuple, List

from core.services.logging_service import get_repo_root, get_logger

logger = get_logger("monitoring-manager", source="wizard")


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthRecord:
    monitor: str
    status: HealthStatus
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "monitor": self.monitor,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class MonitoringManager:
    """Lightweight monitoring collector for training/automation scripts."""

    SUMMARY_FILENAME = "monitoring-summary.json"
    HISTORY_FILENAME = "monitoring-history.log"

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        check_interval: int = 60,
    ):
        repo_root = get_repo_root()
        if data_dir is None:
            data_dir = repo_root / "memory" / "monitoring"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.check_interval = check_interval
        self.history_path = self.data_dir / self.HISTORY_FILENAME
        self.summary_path = self.data_dir / self.SUMMARY_FILENAME
        self.records: List[HealthRecord] = []

    def check_health(
        self,
        monitor: str,
        health_fn: Callable[[], Tuple[HealthStatus, str, Dict[str, Any]]],
    ) -> HealthRecord:
        status, message, metadata = health_fn()
        record = HealthRecord(monitor, status, message, metadata)
        self.records.append(record)
        self._persist(record)
        logger.info("[Monitoring] %s => %s", monitor, status.value)
        return record

    def log_training_summary(self) -> Dict[str, Any]:
        counts = {status.value: 0 for status in HealthStatus}
        alerts: List[Dict[str, Any]] = []
        last_status: Dict[str, str] = {}

        for record in self.records:
            counts[record.status.value] += 1
            last_status[record.monitor] = record.status.value
            if record.status != HealthStatus.HEALTHY:
                alerts.append({
                    "monitor": record.monitor,
                    "status": record.status.value,
                    "message": record.message,
                    "metadata": record.metadata,
                    "timestamp": record.timestamp,
                })

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "check_interval": self.check_interval,
            "total_checks": len(self.records),
            "status_counts": counts,
            "alerts": alerts,
            "last_status": last_status,
        }

        try:
            with open(self.summary_path, "w") as handle:
                json.dump(summary, handle, indent=2)
        except Exception as exc:
            logger.warning("[Monitoring] Unable to write summary: %s", exc)

        return summary

    def latest_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r") as handle:
                lines = [line.strip() for line in handle if line.strip()]
            return [json.loads(line) for line in lines[-limit:]]
        except Exception as exc:
            logger.warning("[Monitoring] Failed to read history: %s", exc)
            return []
