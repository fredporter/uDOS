# EMPIRE WEBHOOK TEMPLATE: calendar-followup-task

## Meta
- label: Calendar Follow-up Task
- source_system: calendar
- event_type: invite.updated
- target_scope: binder
- target_entity: task
- template_version: 1

## Field Map
- summary -> title
- description -> notes
- start -> due_hint

## Required Fields
- summary

## Notes
Use for calendar-origin follow-up tasks when a binder workflow wants task derivation rather than contact updates.
