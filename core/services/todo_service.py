# Todo Scheduling Service
# ========================
#
# Core-only helper that tracks todo tasks, due dates, durations, and exposes 80×40
# grid renderers, ASCII clocks, calendar views, and Markdown-friendly Gantt schema
# helpers. Wizard remains the canonical scheduler, but this service lets Core render
# the results, remind users, and project the same data into task blocks.

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time as dtime
from typing import Dict, Iterable, List, Optional

from core.services.logging_service import get_logger, get_repo_root

logger = get_logger("todo")

GRID_WIDTH = 80
GRID_HEIGHT = 40
CALENDAR_HEIGHT = 30


def _rounded_hours(td: timedelta) -> float:
    return round(td.total_seconds() / 3600.0, 2)


def _count_tasks_in_range(tasks: Iterable["Task"], start: datetime, end: datetime) -> int:
    """Return how many tasks overlap the `[start, end)` window."""
    return sum(1 for task in tasks if task.start_date < end and task.end_date > start)


@dataclass
class Task:
    task_id: str
    title: str
    due_date: datetime
    duration_hours: float
    description: str = ""
    status: str = "pending"  # pending | in-progress | done
    start_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.start_date:
            horizon = timedelta(hours=self.duration_hours)
            self.start_date = self.due_date - horizon

    @property
    def end_date(self) -> datetime:
        return self.start_date + timedelta(hours=self.duration_hours)

    @property
    def remaining_hours(self) -> float:
        now = datetime.utcnow()
        if now >= self.end_date:
            return 0.0
        return _rounded_hours(self.end_date - now)

    def to_task_block(self) -> Dict[str, object]:
        return {
            "type": "to_do",
            "checked": self.status == "done",
            "text": self.title,
            "properties": {
                "Due": self.due_date.isoformat(),
                "Duration": f"{self.duration_hours}h",
                "Tags": ", ".join(self.tags),
            },
        }


class TodoManager:
    """Manages todo tasks, schedules, and reminders."""

    def __init__(self, tasks: Optional[Iterable[Task]] = None):
        self.tasks: Dict[str, Task] = {}
        for task in tasks or []:
            self.tasks[task.task_id] = task

    def add(self, task: Task):
        self.tasks[task.task_id] = task

    def list_pending(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.status != "done"]

    def due_in_days(self, days: int) -> List[Task]:
        cutoff = datetime.utcnow() + timedelta(days=days)
        return [task for task in self.list_pending() if task.due_date <= cutoff]

    def mark_done(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.status = "done"
        return True

    def gantt_schema(self) -> str:
        lines = [
            "```gantt",
            "dateFormat  YYYY-MM-DD",
            "title uDOS Todo Gantt",
        ]
        for task in sorted(self.tasks.values(), key=lambda t: t.start_date):
            status = "done" if task.status == "done" else "active"
            lines.append(
                f"section {task.tags[0] if task.tags else 'Tasks'}"
                f"\n{task.title}:{status}, {task.start_date.date()}, {task.duration_hours}h"
            )
        lines.append("```")
        return "\n".join(lines)


class GridRenderer:
    """Render tasks onto an 80x40 grid for curses/teletext outputs."""

    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height

    def render(self, tasks: Iterable[Task], window_days: int = 14) -> List[str]:
        start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=window_days)
        span_hours = (end - start).total_seconds() / 3600.0
        cells = [
            [" " for _ in range(self.width)] for _ in range(self.height)
        ]
        header = f" {start.date().isoformat()} → {end.date().isoformat()} ".center(self.width, "=")
        lines = [header]
        for row in range(self.height - 1):
            lines.append(" " * self.width)
        for task in tasks:
            task_start = max(task.start_date, start)
            task_end = min(task.end_date, end)
            if task_end <= task_start:
                continue
            start_col = int(((task_start - start).total_seconds() / 3600.0) / span_hours * self.width)
            end_col = min(self.width - 1, max(0, int(((task_end - start).total_seconds() / 3600.0) / span_hours * self.width)))
            row = 1 + (hash(task.task_id) % (self.height - 1))
            for col in range(start_col, end_col + 1):
                cells[row][col] = "#" if task.status != "done" else "="

        for r in range(self.height - 1):
            lines[1 + r] = "".join(cells[r + 1])
        return lines


class CalendarGridRenderer:
    """Render calendar grids (daily / weekly / monthly) inside an 80×30 window."""

    def __init__(self, width: int = GRID_WIDTH, height: int = CALENDAR_HEIGHT):
        self.width = width
        self.height = height

    def render_calendar(
        self,
        tasks: Iterable[Task],
        view: str = "weekly",
        start_date: Optional[datetime] = None,
    ) -> List[str]:
        view = (view or "weekly").lower()
        now = datetime.utcnow()
        if view == "daily":
            return self._render_daily(tasks, start_date or now)
        if view == "weekly":
            return self._render_weekly(tasks, (start_date or now).date())
        if view == "monthly":
            return self._render_monthly(tasks, (start_date or now).date())
        raise ValueError(f"Unknown calendar view: {view}")

    def _render_daily(
        self, tasks: Iterable[Task], reference: datetime
    ) -> List[str]:
        date = reference.date()
        header = f" Calendar Daily · {date.isoformat()} ".center(self.width, "=")
        border = "+" + "-" * (self.width - 2) + "+"
        lines = [header, border]

        start_dt = datetime.combine(date, dtime.min)
        for hour in range(24):
            slot_start = start_dt + timedelta(hours=hour)
            slot_end = slot_start + timedelta(hours=1)
            line_label = slot_start.strftime("%H:%M")
            prefix = f"| {line_label} |"
            suffix = "|"
            bar_width = max(5, self.width - len(prefix) - len(suffix))
            count = _count_tasks_in_range(tasks, slot_start, slot_end)
            fill_char = "#" if count else "."
            bars = fill_char * bar_width
            lines.append(f"{prefix}{bars}{suffix}")
            if len(lines) >= self.height:
                break

        while len(lines) < self.height:
            lines.append(" " * self.width)

        return lines

    def _render_weekly(self, tasks: Iterable[Task], reference: datetime.date) -> List[str]:
        header = f" Calendar Weekly · {reference.isoformat()} ".center(self.width, "=")
        border = "+" + "-" * (self.width - 2) + "+"
        lines = [header, border]

        week_start = reference - timedelta(days=reference.weekday())
        days = [week_start + timedelta(days=i) for i in range(7)]
        column_widths = self._column_widths(len(days))

        def build_row(contents: List[str]) -> str:
            cells = []
            for idx, value in enumerate(contents):
                cells.append(value.center(column_widths[idx]))
            return "|" + "|".join(cells) + "|"

        day_names = [day.strftime("%a %d") for day in days]
        lines.append(build_row(day_names))

        counts = [
            str(
                _count_tasks_in_range(
                    tasks,
                    datetime.combine(day, dtime.min),
                    datetime.combine(day, dtime.max),
                )
            )
            for day in days
        ]
        lines.append(build_row([f"{count} tasks" for count in counts]))

        lines.append(border)
        while len(lines) < self.height:
            lines.append(" " * self.width)

        return lines

    def _render_monthly(
        self, tasks: Iterable[Task], reference: datetime.date
    ) -> List[str]:
        header = f" Calendar Monthly · {reference.strftime('%B %Y')} ".center(
            self.width, "="
        )
        border = "+" + "-" * (self.width - 2) + "+"
        lines = [header, border]

        month_start = reference.replace(day=1)
        start_cell = month_start - timedelta(days=month_start.weekday())

        column_widths = self._column_widths(7)

        def build_row(cells: List[str]) -> str:
            row_cells = []
            for idx, content in enumerate(cells):
                row_cells.append(content.center(column_widths[idx]))
            return "|" + "|".join(row_cells) + "|"

        day_cells = []
        for offset in range(42):
            day = start_cell + timedelta(days=offset)
            count = _count_tasks_in_range(
                tasks,
                datetime.combine(day, dtime.min),
                datetime.combine(day, dtime.max),
            )
            marker = "*" if count else " "
            day_cells.append(f"{day.day:2d}{marker}")

        for week in range(6):
            slice_start = week * 7
            slice_end = slice_start + 7
            lines.append(build_row(day_cells[slice_start:slice_end]))
        lines.append(border)

        while len(lines) < self.height:
            lines.append(" " * self.width)

        return lines

    def _column_widths(self, cols: int) -> List[int]:
        available = self.width - (cols + 1)
        base = max(6, available // cols)
        extra = max(0, available - base * cols)
        widths = []
        for i in range(cols):
            widths.append(base + (1 if i < extra else 0))
        return widths


class GanttGridRenderer(GridRenderer):
    """Produce a gantt-style ASCII timeline inside an 80×30 canvas."""

    LABEL_WIDTH = 16

    def __init__(self, width: int = GRID_WIDTH, height: int = CALENDAR_HEIGHT):
        super().__init__(width=width, height=height)

    def render_gantt(
        self, tasks: Iterable[Task], window_days: int = 30
    ) -> List[str]:
        tasks_list = sorted(tasks, key=lambda t: t.start_date)
        if not tasks_list:
            return ["No tasks to display in Gantt chart."]

        start = tasks_list[0].start_date
        end = start + timedelta(days=window_days)
        header = f" GANTT · {start.date().isoformat()} → {end.date().isoformat()} ".center(
            self.width, "="
        )
        lines = [header]

        timeline_width = max(20, self.width - self.LABEL_WIDTH - 4)
        border = "+" + "-" * (self.width - 2) + "+"
        lines.append(border)

        span_hours = max(1.0, window_days * 24.0)
        max_rows = self.height - 3
        for task in tasks_list[:max_rows]:
            row_label = task.title[: self.LABEL_WIDTH].ljust(self.LABEL_WIDTH)
            timeline = ["." for _ in range(timeline_width)]
            start_offset = max(0.0, (task.start_date - start).total_seconds() / 3600.0)
            end_offset = max(0.0, (task.end_date - start).total_seconds() / 3600.0)
            start_col = min(
                timeline_width - 1,
                int((start_offset / span_hours) * timeline_width),
            )
            end_col = min(
                timeline_width,
                int((end_offset / span_hours) * timeline_width),
            )
            fill = "=" if task.status == "done" else "#"
            for idx in range(start_col, max(start_col, end_col)):
                if 0 <= idx < timeline_width:
                    timeline[idx] = fill
            lines.append(f"| {row_label} |{''.join(timeline)}|")

        lines.append(border)
        while len(lines) < self.height:
            lines.append(" " * self.width)

        return lines


class AsciiClock:
    """Generates a simple ASCII clock at the specified UTC time."""

    @staticmethod
    def render(now: Optional[datetime] = None) -> List[str]:
        now = now or datetime.utcnow()
        time_str = now.strftime("%H:%M UTC")
        lines = [
            "     .--------.     ",
            "    / .======. \\    ",
            "   / /        \\ \\   ",
            "  | |  {:^5}  | |  ".format(time_str),
            "  | |          | |  ",
            "   \\ \\        / /   ",
            "    '========'    ",
        ]
        return lines


_TODO_MANAGER: Optional[TodoManager] = None


def _load_seed_tasks() -> List[Task]:
    repo_root = get_repo_root()
    seed_path = repo_root / "core" / "framework" / "seed" / "bank" / "system" / "todos.json"
    tasks: List[Task] = []
    if seed_path.exists():
        try:
            data = json.loads(seed_path.read_text(encoding="utf-8"))
            for entry in data.get("tasks", []):
                entry["due_date"] = datetime.fromisoformat(entry["due_date"])
                tasks.append(Task(**entry))
        except Exception as exc:
            logger.warning("[TODO] Failed to load seed tasks: %s", exc)
    return tasks


def get_service() -> TodoManager:
    """Singleton helper for service wiring."""
    global _TODO_MANAGER
    if _TODO_MANAGER is None:
        _TODO_MANAGER = TodoManager(_load_seed_tasks())
    return _TODO_MANAGER
