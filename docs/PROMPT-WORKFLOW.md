# PROMPT Workflow & Ollama Model Playbook

This guide keeps the PROMPT instruction parser, seed templates, and Ollama workflows in one place so future rounds can keep the “todo checklist → calendar/Gantt → reminder” pipeline steady.

## Instruction seeds

- The story seeds in `core/framework/seed/bank/templates/story.template.json` now reference `prompt_parser_seed.json`, which defines:
  * `todo.checklist` (primary target for action items that map into `TodoManager` and the 80×30 calendar/Gantt renderers).
  * `novel.outline` (chapter/plot scaffolds referencing the Squibler/Novel outline templates).
  * `workflow.schedule` (meta-schedule instructions that should render via `/api/tasks/calendar` and `/api/tasks/gantt` before committing to a plan).
- The parser returns metadata (`instruction_id`, guidance, reference links) plus the generated `Task` objects (with due dates/durations), so every PROMPT run can drop them straight into `TodoManager.add()` and the subsequent renderers.

## PROMPT interpreter APIs

- CLI: `uCODETUI` exposes `PROMPT "<instruction text>"`, which classifies the input, adds the derived tasks to `TodoManager`, renders the 80×30 calendar and Gantt previews, and surfaces the `todo_reminder` payload.  
- HTTP: POST `/api/tasks/prompt` (wizard route) accepts the same text, optional calendar view/window hints, returns the instruction metadata, calendar/Gantt lines (text + JSON), and reminder object; dashboards, automation scripts, and the Hotkey Center can consume this payload for consistent UX.
- Reminder wiring: `TodoReminderService.log_reminder` runs during every prompt parse and system script so the health log and notification history capture due-soon alerts; the Hotkey Center documents these paths alongside `memory/logs/health-training.log`.

## Ollama / Apertus stack

We’re standardizing on **Apertus** (Apache 2.0, EU AI-ready, excellent reasoning) as the launch model:

1. Install via Ollama:
   ```bash
   ollama pull apertus
   ollama run apertus
   ```
2. Use the PROMPT workflow by piping the instruction text into Ollama (the parser can wrap the user string with templates describing the expected output type, e.g. todo checklist).  
3. Keep the parser focused on the `prompt_parser_seed.json` signals so the model can be instructed to "emit bullets, due dates, and owners" before the CLI or Wizard steps in.

### Local uDOS skill

Every round builds on Apertus, so craft uDOS-specific skills that:
* Wrap the model in a `PROMPT` context (prefix with `You are uDOS prompt parser...`).
* Highlight the instruction types (`todo.checklist`, `workflow.schedule`, etc.).
* Emit JSON that matches `TodoManager` payloads for renderer consumption.
* Append the reminder request (horizon + message) so the health log knows when to surface the reminder.

## Alternatives to explore (after Apertus)

- **Llama 4 Maverick (via Ollama)** – 200K context; good for multi-step scheduling but heavier.  
- **Qwen 3 (via Ollama)** – Balanced reasoning/knowledge; build a fallback skill if Apertus is busy.  
- **DeepSeek V3** – Strong for creative writing; pair with `novel.outline` to keep chapters fresh.  
- **OpenAssistant LLaMA-2** – Lightweight fallback for quick todo lists or offline clients.

Keep Apertus as the canonical “focus model” while documenting alt flows for robustness; mention the chosen backup in this doc so future squads always know what to pull/install first.
