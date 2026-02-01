# Todo Renderers & Reminder API

This reference keeps the new Core todo renderers, reminder payloads, and Hotkey/health hooks in one place so future Wizard rounds can reuse the same text grids and alerts without guessing sizes.

## Task renderers

| Component | Signature | Output | Notes |
| --- | --- | --- | --- |
| `GridRenderer.render(tasks, window_days=14)` | `(Iterable[Task], window_days: int = 14)` | `List[str]` of 80×40 lines (default) with task bars per row; uses `GRID_WIDTH`/`GRID_HEIGHT`. | Good for retro ASCII/teletext dashboards. |
| `CalendarGridRenderer.render_calendar(tasks, view="weekly", start_date=None)` | `(Iterable[Task], view: str, start_date: Optional[datetime])` | 30-line 80-column grids covering `daily`, `weekly`, or `monthly` views; pads to `CALENDAR_HEIGHT` so output stays consistent with the Hotkey Center snapshots. | Pass `view` (“daily”/“weekly”/“monthly”) plus optional ISO start date to align with CLI prompts; default weekly view shows dates + counts for the upcoming week. |
| `GanttGridRenderer.render_gantt(tasks, window_days=30)` | `(Iterable[Task], window_days: int = 30)` | 80×30 Gantt chart with task labels (16-char) and timeline bars (#/=); spans the next `window_days` and caps rows to `CALENDAR_HEIGHT`. | Use for timelines in CLI/dashboards; reuses the same width/height constants as the calendar renderer. |
| `Task.to_notion_block()` | `Task` method | Notion-style `{"type":"to_do",...}` block | Call before storing or syncing tasks to ensure payloads always include due duration/tags. |

## Reminder/notification flow

1. `TodoReminderService` (`core/services/todo_reminder_service.py`) polls `TodoManager.list_pending()` for tasks due within a horizon (default 24h) and logs the reminder payload via `append_training_entry`.
2. `record_notification()` (`core/services/notification_history_service.py`) stores reminder metadata in `memory/logs/notification-history.log` alongside the self-heal summary so the Hotkey Center and automation scripts can compare both feeds.
3. `SystemScriptRunner` calls `todo_reminder.log_reminder()` before every startup/reboot script and surfaces the payload under `"todo_reminder"` in its return value, making the ASCII clock banner (via `core/services/hotkey_map.py`) or other watchers aware that a reminder exists.

## Hotkey/health ties

- Hotkey payload builders (`core/services/hotkey_map.py`) already include the plugin/Sonic doc path plus `memory/logs/health-training.log` references; add the new reminder entries to those logs so automation can tie a Gantt/calendar view to the latest health snapshot before gating PATTERN/REPAIR.
- The reminder payloads append to `memory/logs/health-training.log` (same file used by Self-Heal automation) so you can replay both plugin and todo events when deciding whether to rerun the self-heal sequence.

## Usage notes

- For CLI/dashboard routes, use the `/api/tasks/calendar` and `/api/tasks/gantt` endpoints in `wizard/routes/task_routes.py`; they accept `view`/`start_date` or `window_days` plus optional `format=text|json` to keep the outputs consumable by both ASCII renderers and automation UI layers.
- Pair the calendar/gantt output with `Task.to_notion_block()` for Notion exports, and use the rendered ASCII clock (via `core/services/todo_service.AsciiClock.render()`) to highlight reminder timestamps in the UI.
- When building new flows (PROMPT classification, Wizard scheduling stories, etc.), let the reminder service emit a `"todo_reminder"` block and log it alongside `notification_reminder`; future Hotkey Center snapshots or monitoring scripts can then show both the botched tasks and the not-yet-closed health issues together.
