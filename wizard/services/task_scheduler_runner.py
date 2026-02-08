"""Background runner for TaskScheduler."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from wizard.services.logging_api import get_logger
from wizard.services.task_scheduler import TaskScheduler


@dataclass
class TaskSchedulerRunner:
    """Run TaskScheduler in a background thread."""

    scheduler: TaskScheduler = field(default_factory=TaskScheduler)
    logger: Any = field(
        default_factory=lambda: get_logger(
            "wizard", category="scheduler", name="wizard-scheduler"
        )
    )
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _thread: threading.Thread = field(default=None, init=False)

    def start(self, days: int, dry_run: bool) -> None:
        if self._thread and self._thread.is_alive():
            return

        try:
            self.scheduler.ensure_daily_compost_cleanup(days=days, dry_run=dry_run)
        except Exception:
            pass

        def loop():
            last_error = None
            last_error_ts = 0.0
            while not self._stop.is_set():
                wait_seconds = 60
                try:
                    settings = self.scheduler.get_settings()
                    max_tasks = int(settings.get("max_tasks_per_tick", 2) or 2)
                    tick_seconds = int(settings.get("tick_seconds", 60) or 60)
                    if tick_seconds < 5:
                        tick_seconds = 5
                    wait_seconds = tick_seconds
                    result = self.scheduler.run_pending(max_tasks=max_tasks)
                    if result.get("executed", 0):
                        self.logger.info(
                            f"[WIZ] Scheduler executed {result.get('executed')} task(s)"
                        )
                except Exception as exc:
                    msg = str(exc)
                    now = time.monotonic()
                    if msg != last_error or (now - last_error_ts) > 60:
                        self.logger.warn("[WIZ] Scheduler loop error: %s", exc)
                        last_error = msg
                        last_error_ts = now
                    # Back off when failing to avoid hot-looping.
                    wait_seconds = max(wait_seconds, 60)
                self._stop.wait(wait_seconds)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
