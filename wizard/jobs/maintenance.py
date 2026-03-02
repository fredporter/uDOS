from __future__ import annotations

from wizard.services.task_scheduler import TaskScheduler


def main() -> int:
    scheduler = TaskScheduler()
    scheduler.ensure_daily_compost_cleanup()
    print({"status": "ok"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
