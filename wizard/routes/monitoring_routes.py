"""
Monitoring Routes (Wizard)
==========================

Provides lightweight monitoring endpoints for health summaries,
diagnostics, and log access.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from wizard.services.logging_manager import get_logging_manager
from wizard.services.monitoring_manager import MonitoringManager, AlertSeverity, AlertType
from wizard.services.path_utils import get_logs_dir, get_repo_root
from wizard.services.system_info_service import get_system_info_service

_monitoring_manager: Optional[MonitoringManager] = None


def _get_monitoring_manager() -> MonitoringManager:
    global _monitoring_manager
    if _monitoring_manager is None:
        data_dir = get_logs_dir() / "monitoring"
        _monitoring_manager = MonitoringManager(data_dir=data_dir)
    return _monitoring_manager


def _tail_lines(path: Path, lines: int) -> list[str]:
    buffer: deque[str] = deque(maxlen=lines)
    with open(path, "r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            buffer.append(line.rstrip("\n"))
    return list(buffer)


def _sanitize_log_name(log_name: str) -> str:
    if "/" in log_name or "\\" in log_name or ".." in log_name:
        raise HTTPException(status_code=400, detail="Invalid log name")
    if not log_name.endswith(".log"):
        raise HTTPException(status_code=400, detail="Log name must end with .log")
    return log_name


def create_monitoring_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/monitoring", tags=["monitoring"], dependencies=dependencies)

    @router.get("/summary")
    async def get_health_summary() -> Dict[str, Any]:
        monitoring = _get_monitoring_manager()
        monitoring.run_default_checks()
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "health": monitoring.get_health_summary(),
        }

    @router.get("/diagnostics")
    async def get_diagnostics() -> Dict[str, Any]:
        monitoring = _get_monitoring_manager()
        monitoring.run_default_checks()
        logging_manager = get_logging_manager()
        system_service = get_system_info_service(get_repo_root())
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "health": monitoring.get_health_summary(),
            "system": {
                "os": system_service.get_os_info().to_dict(),
                "stats": system_service.get_system_stats(),
                "library": system_service.get_library_status().to_dict(),
            },
            "logs": logging_manager.get_log_stats(),
        }

    @router.get("/logs")
    async def list_logs() -> Dict[str, Any]:
        log_dir = get_logs_dir()
        entries = []
        for log_path in log_dir.glob("*.log"):
            try:
                stat = log_path.stat()
                entries.append(
                    {
                        "name": log_path.name,
                        "size_bytes": stat.st_size,
                        "updated_at": datetime.utcfromtimestamp(stat.st_mtime).isoformat()
                        + "Z",
                    }
                )
            except FileNotFoundError:
                continue
        entries.sort(key=lambda item: item["updated_at"], reverse=True)
        return {"count": len(entries), "logs": entries}

    @router.get("/logs/stats")
    async def log_stats() -> Dict[str, Any]:
        logging_manager = get_logging_manager()
        return logging_manager.get_log_stats()

    @router.get("/logs/{log_name}")
    async def tail_log(
        log_name: str,
        lines: int = Query(200, ge=1, le=2000),
    ) -> Dict[str, Any]:
        log_name = _sanitize_log_name(log_name)
        log_dir = get_logs_dir()
        log_path = (log_dir / log_name).resolve()
        if log_path.parent != log_dir.resolve():
            raise HTTPException(status_code=400, detail="Invalid log path")
        if not log_path.exists():
            raise HTTPException(status_code=404, detail="Log not found")
        data = _tail_lines(log_path, lines)
        return {"log": log_name, "lines": lines, "total_lines": len(data), "data": data}

    def _parse_severity(value: Optional[str]) -> Optional[AlertSeverity]:
        if not value:
            return None
        try:
            return AlertSeverity(value)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid severity")

    def _parse_type(value: Optional[str]) -> Optional[AlertType]:
        if not value:
            return None
        try:
            return AlertType(value)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid alert type")

    @router.get("/alerts")
    async def list_alerts(
        severity: Optional[str] = None,
        type: Optional[str] = None,
        service: Optional[str] = None,
        unacknowledged_only: bool = False,
        limit: int = Query(100, ge=1, le=500),
    ) -> Dict[str, Any]:
        monitoring = _get_monitoring_manager()
        alerts = monitoring.get_alerts(
            severity=_parse_severity(severity),
            type=_parse_type(type),
            service=service,
            unacknowledged_only=unacknowledged_only,
            limit=limit,
        )
        return {"count": len(alerts), "alerts": [a.to_dict() for a in alerts]}

    @router.post("/alerts/{alert_id}/ack")
    async def acknowledge_alert(alert_id: str) -> Dict[str, Any]:
        monitoring = _get_monitoring_manager()
        ok = monitoring.acknowledge_alert(alert_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"success": True, "alert_id": alert_id, "acknowledged": True}

    @router.post("/alerts/{alert_id}/resolve")
    async def resolve_alert(alert_id: str) -> Dict[str, Any]:
        monitoring = _get_monitoring_manager()
        ok = monitoring.resolve_alert(alert_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"success": True, "alert_id": alert_id, "resolved": True}

    return router
