from __future__ import annotations

import time
from datetime import datetime

from wizard.services.monitoring_manager import MonitoringManager
from wizard.services.task_scheduler import TaskScheduler


def _within_window(window: str, now: datetime) -> bool:
    value = str(window or "").strip()
    if not value:
        return True
    start_raw, end_raw = value.split("-", 1)
    start = datetime.strptime(start_raw, "%H:%M").time()
    end = datetime.strptime(end_raw, "%H:%M").time()
    current = now.time()
    if start <= end:
        return start <= current <= end
    return current >= start or current <= end


def main() -> int:
    started = time.time()
    monitoring = MonitoringManager()
    scheduler = TaskScheduler()
    try:
        scheduler.ensure_daily_compost_cleanup()
        settings = scheduler.get_settings()
        policy = settings.get("auto_retry_deferred_policy") or {}
        global_dry_run = bool(settings.get("maintenance_retry_dry_run", False))
        retried_by_reason = {}
        preview_by_reason = {}
        skipped_by_window = {}
        now = datetime.now()
        if policy:
            for reason, reason_policy in policy.items():
                if not isinstance(reason_policy, dict) or not reason_policy.get("enabled", True):
                    continue
                limit = max(0, int(reason_policy.get("limit", settings.get("auto_retry_deferred_limit", 10) or 0)))
                preview = scheduler.list_deferred_items(reason=str(reason), limit=limit)
                preview_by_reason[str(reason)] = len(preview)
                window = str(reason_policy.get("window", "") or "").strip()
                if preview and not _within_window(window, now):
                    skipped_by_window[str(reason)] = len(preview)
                    retried_by_reason[str(reason)] = 0
                    continue
                if global_dry_run or bool(reason_policy.get("dry_run", False)):
                    retried_by_reason[str(reason)] = 0
                    continue
                retried = scheduler.retry_deferred_items(reason=str(reason), limit=limit)
                retried_by_reason[str(reason)] = len(retried)
        else:
            for reason in settings.get("auto_retry_deferred_reasons", []):
                limit = int(settings.get("auto_retry_deferred_limit", 10) or 0)
                preview = scheduler.list_deferred_items(reason=str(reason), limit=limit)
                preview_by_reason[str(reason)] = len(preview)
                if global_dry_run:
                    retried_by_reason[str(reason)] = 0
                    continue
                retried = scheduler.retry_deferred_items(reason=str(reason), limit=limit)
                retried_by_reason[str(reason)] = len(retried)
        payload = {
            "status": "ok",
            "maintenance_retry_dry_run": global_dry_run,
            "auto_retry_deferred_reasons": settings.get("auto_retry_deferred_reasons", []),
            "auto_retry_deferred_limit": settings.get("auto_retry_deferred_limit", 10),
            "auto_retry_deferred_policy": policy,
            "preview_by_reason": preview_by_reason,
            "retried_by_reason": retried_by_reason,
            "skipped_by_window": skipped_by_window,
        }
        operation = "maintenance_preview" if global_dry_run else "maintenance"
        monitoring.record_automation_run(
            operation,
            success=True,
            duration_ms=(time.time() - started) * 1000,
            metadata=payload,
        )
        print(payload)
        return 0
    except Exception as exc:
        operation = "maintenance_preview" if bool(locals().get("global_dry_run", False)) else "maintenance"
        monitoring.record_automation_run(
            operation,
            success=False,
            duration_ms=(time.time() - started) * 1000,
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
