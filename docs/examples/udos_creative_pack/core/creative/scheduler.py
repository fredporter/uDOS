from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta, timezone


@dataclass
class ScheduleWindow:
    """Defines when to run a phase."""
    run_at_iso: str  # ISO datetime
    allow_auto_approval: bool = False


def schedule_next(run_every_hours: int = 12) -> ScheduleWindow:
    now = datetime.now(timezone.utc)
    nxt = now + timedelta(hours=run_every_hours)
    return ScheduleWindow(run_at_iso=nxt.isoformat(), allow_auto_approval=False)
