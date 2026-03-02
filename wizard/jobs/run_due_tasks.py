from __future__ import annotations

import time

from wizard.services.monitoring_manager import MonitoringManager
from wizard.services.task_scheduler import TaskScheduler


def main() -> int:
    started = time.time()
    monitoring = MonitoringManager()
    scheduler = TaskScheduler()
    try:
        settings = scheduler.get_settings()
        max_tasks = int(settings.get("max_tasks_per_tick", 2) or 2)
        result = scheduler.run_pending(max_tasks=max_tasks)
        monitoring.record_automation_run(
            "run_due_tasks",
            success=True,
            duration_ms=(time.time() - started) * 1000,
            metadata=result,
        )
        print(result)
        return 0
    except Exception as exc:
        monitoring.record_automation_run(
            "run_due_tasks",
            success=False,
            duration_ms=(time.time() - started) * 1000,
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
