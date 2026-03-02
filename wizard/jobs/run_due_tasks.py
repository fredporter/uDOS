from __future__ import annotations

from wizard.services.task_scheduler import TaskScheduler


def main() -> int:
    scheduler = TaskScheduler()
    settings = scheduler.get_settings()
    max_tasks = int(settings.get("max_tasks_per_tick", 2) or 2)
    result = scheduler.run_pending(max_tasks=max_tasks)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
