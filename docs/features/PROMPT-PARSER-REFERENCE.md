# PROMPT Parser Reference

The new PROMPT workflow classifies incoming instructions, wires them into `TodoManager`, and produces outputs for the CLI, dashboard, and automation hooks.

## Instruction types

Seeded in `core/framework/seed/bank/templates/prompt_parser_seed.json`, the parser recognizes:

- **todo.checklist** – Short-term actionable tasks. Maps to `TodoManager`, task blocks, calendar/Gantt renders, and triggers the todo reminder service.
- **novel.outline** – Narrative drafting instructions (chapter beats, arcs). Points back to the book-writing templates referenced in the seed file.
- **workflow.schedule** – Scheduling/coordination directives (meta ad spend, call planning). Targets the `/api/tasks/calendar` and `/api/tasks/gantt` endpoints for immediate planner renderings.

## Core service

- `core/services/prompt_parser_service.PromptParserService` loads `prompt_parser_seed.json`, matches the best instruction type, and splits the input text into fragments (splitting by newline, bullet, or semicolon).
- Each fragment becomes a `Task` with a generated ID, default duration, due-in-a-few-hours timeline, and `instruction_id` tag.
- The parser returns metadata (instruction label/description/story guidance/reference links) plus the new tasks so callers can persist them and surface helpful guidance.

## Wiring to todo service

- `core/services/todo_service.get_service()` now returns a singleton `TodoManager` so add/remove operations persist across CLI sessions and HTTP calls.
- `uCODETUI._cmd_prompt` (added in `core/tui/ucode.py`) consumes `get_prompt_parser_service()`, adds the parsed tasks to `TodoManager`, renders the 80×30 calendar/Gantt previews, and prints task block payloads.
- `wizard/routes/task_routes.parse_prompt` exposes `/api/tasks/prompt`; it returns the parsed instruction metadata, task block list, calendar/Gantt lines (text + JSON options), and the reminder payload emitted by `TodoReminderService`.

## Reminder integration

- `core/services/todo_reminder_service.TodoReminderService` now logs due-soon entries to `memory/logs/health-training.log` and `notification-history.log`.
- `SystemScriptRunner` calls `log_reminder()` before startup/reboot workflows so the ASCII banner, Hotkey Center, and health automation know when a todo reminder is active.
- Use the reminder payload in dashboards (e.g., `memory/logs/notification-history.log`) to highlight due-soon tasks and drive the ASCII clock or watchers whenever `PROMPT` adds fresh items.
