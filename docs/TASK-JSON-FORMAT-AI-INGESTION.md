# Task JSON Format v1.0 — AI Ingestion & Import Mapping

**Date:** 20 Feb 2026
**Version:** 1.0
**Status:** ✅ COMPLETE
**Purpose:** Unified JSON format for task/move management supporting AI ingestion and imported item handling

---

## Overview

All tasks in `moves.json` follow a **unified, extensible schema** designed for:

1. **AI Ingestion** — Complete structured data for LLM processing
2. **Import Mapping** — Calendar events, invites, reminders, emails → tasks
3. **Type Flexibility** — Support for multiple item types (task, calendar_event, invite, reminder, imported)
4. **Metadata Extensibility** — Custom fields via metadata object for future enhancements

---

## Core Schema

Every move in `moves.json` conforms to this structure:

```json
{
  "id": "task-identifier",
  "mission_id": "project-name",
  "title": "Task Title",
  "description": "Full task description",
  "item_type": "task|calendar_event|invite|reminder|imported",
  "status": "todo|in_progress|blocked|review|done|archived",
  "priority": "high|medium|low|null",
  "assigned_to": "person-email@domain.com|null",
  "tags": ["tag1", "tag2"],
  "due_date": "2026-02-25T17:00:00|null",
  "start_date": "2026-02-25T10:00:00|null",
  "end_date": "2026-02-25T17:00:00|null",
  "organizer": "organizer@domain.com|null",
  "attendees": [
    {
      "name": "Alice Smith",
      "email": "alice@domain.com",
      "status": "accepted|declined|tentative|no_response"
    }
  ],
  "source": "manual|calendar|invite|reminder|email|slack|jira|linear|etc",
  "source_id": "original-id-from-source-system|null",
  "metadata": {
    "custom_field": "value",
    "import_timestamp": "2026-02-20T10:30:00",
    "item_category": "category"
  },
  "created": "2026-02-20T10:30:00",
  "updated": "2026-02-20T10:35:00",
  "completed": "2026-02-22T14:00:00|null"
}
```

---

## Item Types & Field Usage

### 1. Standard Task (`item_type: "task"`)

**Purpose:** General work item

**Required Fields:**
- `id`, `mission_id`, `title`, `description`, `item_type`, `status`

**Optional Fields:**
- `priority`, `assigned_to`, `tags`, `due_date`

**Example:**

```json
{
  "id": "uuid-12345",
  "mission_id": "product-roadmap",
  "title": "Implement OAuth2 integration",
  "description": "Add OAuth2 authentication support for third-party services",
  "item_type": "task",
  "status": "in_progress",
  "priority": "high",
  "assigned_to": "dev-team@company.com",
  "tags": ["feature", "backend", "security"],
  "due_date": "2026-02-25T17:00:00",
  "source": "manual",
  "created": "2026-02-20T10:30:00",
  "updated": "2026-02-20T10:35:00"
}
```

### 2. Calendar Event (`item_type: "calendar_event"`)

**Purpose:** Calendar/meeting items mapped as tasks

**Key Fields:**
- `start_date`, `end_date` — Event timing
- `location` — Meeting location (in metadata)
- `organizer` — Meeting organizer
- `attendees` — List of participants
- `metadata.recurring` — If event repeats

**Example:**

```json
{
  "id": "uuid-67890",
  "mission_id": "product-roadmap",
  "title": "Q2 Planning Meeting",
  "description": "Quarterly planning session for Q2 roadmap",
  "item_type": "calendar_event",
  "status": "todo",
  "priority": null,
  "start_date": "2026-03-01T14:00:00",
  "end_date": "2026-03-01T15:30:00",
  "organizer": "product-lead@company.com",
  "attendees": [
    {
      "name": "Alice Smith",
      "email": "alice@company.com",
      "status": "accepted"
    },
    {
      "name": "Bob Johnson",
      "email": "bob@company.com",
      "status": "tentative"
    }
  ],
  "tags": ["meeting", "calendar", "planning"],
  "source": "calendar",
  "source_id": "google-calendar-event-id-xyz",
  "metadata": {
    "calendar_location": "Zoom: meeting-link",
    "recurring": false,
    "conference_link": "https://zoom.us/j/..."
  },
  "created": "2026-02-20T09:00:00",
  "updated": "2026-02-20T09:00:00"
}
```

### 3. Meeting Invite (`item_type: "invite"`)

**Purpose:** Meeting invitations requiring RSVP

**Key Fields:**
- `organizer` — Who sent the invite
- `attendees` — Recipients with RSVP status
- `metadata.response_due` — Deadline for RSVP
- `metadata.rsvp_required` — If RSVP is required

**Example:**

```json
{
  "id": "uuid-11111",
  "mission_id": "hiring-pipeline",
  "title": "Candidate Interview - Alice Smith",
  "description": "Technical interview for Senior Backend Engineer position",
  "item_type": "invite",
  "status": "todo",
  "priority": "high",
  "start_date": "2026-02-26T10:00:00",
  "end_date": "2026-02-26T10:45:00",
  "organizer": "hiring-manager@company.com",
  "attendees": [
    {
      "name": "You",
      "email": "your-email@company.com",
      "status": "no_response"
    },
    {
      "name": "Interview Panel",
      "email": "tech-panel@company.com",
      "status": "accepted"
    }
  ],
  "tags": ["meeting", "invite", "hiring"],
  "source": "invite",
  "source_id": "outlook-invite-id-abc123",
  "metadata": {
    "response_due": "2026-02-25T17:00:00",
    "rsvp_required": true,
    "meeting_link": "https://teams.microsoft.com/l/..."
  },
  "created": "2026-02-23T09:00:00",
  "updated": "2026-02-23T09:00:00"
}
```

### 4. Reminder (`item_type: "reminder"`)

**Purpose:** Time-sensitive reminders and alerts

**Key Fields:**
- `due_date` — When reminder is due
- `metadata.alert_type` — Type of alert (notification, email, sms)
- `metadata.alert_interval` — When to alert (e.g., "15min", "1hour", "1day")

**Example:**

```json
{
  "id": "uuid-22222",
  "mission_id": "hiring-pipeline",
  "title": "Follow up with candidate - Bob Jones",
  "description": "Send follow-up email to Bob regarding interview feedback",
  "item_type": "reminder",
  "status": "todo",
  "priority": "high",
  "due_date": "2026-02-27T09:00:00",
  "tags": ["reminder", "hiring", "followup"],
  "source": "reminder",
  "metadata": {
    "alert_type": "notification",
    "alert_interval": "1hour",
    "context": "Interview was completed 2026-02-26"
  },
  "created": "2026-02-26T14:00:00",
  "updated": "2026-02-26T14:00:00"
}
```

### 5. Imported Item (`item_type: "imported"`)

**Purpose:** Generic items from external systems (email, Slack, Jira, Linear, etc.)

**Key Fields:**
- `source` — External system (email, slack, jira, linear, etc.)
- `source_id` — ID from original system
- `metadata.item_category` — Category of imported item
- `metadata.original_format` — Original format/structure

**Example - Email:**

```json
{
  "id": "uuid-33333",
  "mission_id": "urgent-issues",
  "title": "[BUG] Production API timeout on /auth endpoint",
  "description": "Received from customer support: API returns 504 errors during peak hours",
  "item_type": "imported",
  "status": "todo",
  "priority": "high",
  "tags": ["imported", "email", "bug", "production", "urgent"],
  "source": "email",
  "source_id": "message-id-xyz123",
  "metadata": {
    "item_category": "bug_report",
    "from": "bugs@customer.io",
    "subject": "[BUG] Production API timeout on /auth endpoint",
    "import_timestamp": "2026-02-24T08:30:00",
    "customer": "Acme Inc"
  },
  "created": "2026-02-24T08:30:00",
  "updated": "2026-02-24T08:30:00"
}
```

**Example - Jira Ticket:**

```json
{
  "id": "uuid-44444",
  "mission_id": "backend-refactor",
  "title": "PROJ-1234: Refactor database connection pooling",
  "description": "Optimize connection pool size and timeout configuration",
  "item_type": "imported",
  "status": "todo",
  "priority": "medium",
  "assigned_to": "backend-team@company.com",
  "tags": ["imported", "jira", "refactor", "performance"],
  "source": "jira",
  "source_id": "PROJ-1234",
  "metadata": {
    "item_category": "technical_debt",
    "jira_key": "PROJ-1234",
    "jira_type": "Task",
    "estimated_hours": 8,
    "sprint": "Sprint 24",
    "import_timestamp": "2026-02-20T14:30:00"
  },
  "due_date": "2026-03-05T17:00:00",
  "created": "2026-02-20T14:30:00",
  "updated": "2026-02-20T14:30:00"
}
```

---

## Backward Compatibility

**Existing moves.json files remain valid.** Fields not present default to:
- `item_type` → `"task"`
- `status` → Value from original
- `priority` → Value from original
- `source` → `"manual"`
- Other optional fields → `null` or `[]`

Example migration of old format → new format:

**Old:**
```json
{
  "id": "move-123",
  "mission_id": "project",
  "title": "Task",
  "description": "Description",
  "priority": "high",
  "status": "in_progress",
  "assigned_to": "alice@company.com",
  "created": "2026-02-20T10:30:00",
  "updated": "2026-02-20T10:35:00"
}
```

**Automatically Enhanced:**
```json
{
  "id": "move-123",
  "mission_id": "project",
  "title": "Task",
  "description": "Description",
  "item_type": "task",
  "priority": "high",
  "status": "in_progress",
  "assigned_to": "alice@company.com",
  "tags": [],
  "due_date": null,
  "start_date": null,
  "end_date": null,
  "source": "manual",
  "source_id": null,
  "metadata": {},
  "created": "2026-02-20T10:30:00",
  "updated": "2026-02-20T10:35:00"
}
```

---

## Complete moves.json Example

```json
{
  "moves": [
    {
      "id": "uuid-1",
      "mission_id": "product-v2",
      "title": "Design new dashboard UI",
      "description": "Create responsive dashboard with real-time metrics",
      "item_type": "task",
      "status": "in_progress",
      "priority": "high",
      "assigned_to": "designer@company.com",
      "tags": ["feature", "frontend", "ui"],
      "due_date": "2026-02-28T17:00:00",
      "source": "manual",
      "metadata": {
        "design_tool": "figma",
        "design_link": "https://figma.com/..."
      },
      "created": "2026-02-18T10:00:00",
      "updated": "2026-02-20T14:30:00"
    },
    {
      "id": "uuid-2",
      "mission_id": "product-v2",
      "title": "Q1 Alignment Meeting",
      "description": "Quarterly alignment with stakeholders",
      "item_type": "calendar_event",
      "status": "todo",
      "start_date": "2026-03-01T14:00:00",
      "end_date": "2026-03-01T15:30:00",
      "organizer": "product-lead@company.com",
      "attendees": [
        {
          "name": "Product Lead",
          "email": "product-lead@company.com",
          "status": "accepted"
        },
        {
          "name": "Engineering Lead",
          "email": "eng-lead@company.com",
          "status": "accepted"
        }
      ],
      "tags": ["meeting", "calendar", "planning"],
      "source": "calendar",
      "source_id": "google-calendar-xyz",
      "metadata": {
        "recurring": false,
        "conference_link": "https://zoom.us/..."
      },
      "created": "2026-02-20T09:00:00",
      "updated": "2026-02-20T09:00:00"
    },
    {
      "id": "uuid-3",
      "mission_id": "product-v2",
      "title": "Review API design proposal",
      "description": "Technical review of new REST API endpoint design",
      "item_type": "imported",
      "status": "review",
      "priority": "medium",
      "assigned_to": "tech-lead@company.com",
      "tags": ["imported", "email", "api", "design"],
      "source": "email",
      "source_id": "msg-id-456",
      "metadata": {
        "item_category": "design_review",
        "from": "architect@company.com",
        "subject": "API Design Proposal for v2.0"
      },
      "created": "2026-02-20T11:20:00",
      "updated": "2026-02-20T14:00:00"
    }
  ]
}
```

---

## AI Ingestion Benefits

This unified format enables:

1. **Rich Context** — AI models have complete task metadata
2. **Type Awareness** — Different task types can be processed appropriately
3. **Relationship Mapping** — Attendees, components, dependencies visible
4. **Temporal Reasoning** — Start, end, due dates enable scheduling assistance
5. **Audio/Visual Processing** — Extensible metadata for attachments, links
6. **Historical Context** — Created, updated, completed timestamps enable trend analysis

### Example AI Prompts

**Task Analysis:**
```
Analyze all "high" priority items in the product-v2 mission and suggest:
1. Dependencies between tasks
2. Optimal assignment based on due dates
3. Risk factors (overdue reminders, blocked items)
```

**Calendar Optimization:**
```
Find all calendar_event items in March with overlapping attendees
and suggest rescheduling options to reduce meeting conflicts.
```

**Import Reconciliation:**
```
Show all imported items from email source created this week,
suggest which should be promoted to standard tasks with full context.
```

---

## API Methods for New Format

See [VibeBinderService](../core/services/vibe_binder_service.py) for:

- `add_move()` — Add standard task
- `add_calendar_event()` — Import calendar event
- `add_invite()` — Import meeting invite
- `add_reminder()` — Add reminder
- `add_imported_item()` — Import from any external source
- `list_moves_by_type()` — Filter by item type
- `list_moves_by_date_range()` — Schedule queries
- `list_moves_by_source()` — Track import sources
- `get_imported_items_summary()` — Overview of mapped imports
- `get_task_summary_for_ai()` — Complete AI ingestion data

---

## Migration & Import Scripts

### Example: Calendar Import Handler

```python
from datetime import datetime
from core.services.vibe_binder_service import get_binder_service

def import_calendar_event(calendar_event_dict, mission_id):
    """Import Google Calendar event as task."""
    binder = get_binder_service()

    return binder.add_calendar_event(
        mission_id=mission_id,
        title=calendar_event_dict["summary"],
        description=calendar_event_dict.get("description", ""),
        start_date=calendar_event_dict["start"]["dateTime"],
        end_date=calendar_event_dict["end"]["dateTime"],
        location=calendar_event_dict.get("location"),
        organizer=calendar_event_dict["creator"]["email"],
        attendees=[
            {
                "name": att.get("displayName", att["email"]),
                "email": att["email"],
                "status": att.get("responseStatus", "noreply")
            }
            for att in calendar_event_dict.get("attendees", [])
        ],
        source="calendar",
        source_id=calendar_event_dict["id"],
        metadata={
            "conference_link": calendar_event_dict.get("conferenceData", {}).get("entryPoints"),
            "recurring": "recurrence" in calendar_event_dict
        }
    )
```

### Example: Email Import Handler

```python
def import_email(email_dict, mission_id, priority="medium"):
    """Import email as task."""
    binder = get_binder_service()

    return binder.add_imported_item(
        mission_id=mission_id,
        title=f"[EMAIL] {email_dict['subject']}",
        description=email_dict.get("body_excerpt", ""),
        source="email",
        source_id=email_dict["id"],
        priority=priority,
        item_category="email",
        metadata={
            "from": email_dict["from"],
            "subject": email_dict["subject"],
            "has_attachments": email_dict.get("has_attachments", False)
        },
        tags=["imported", "email"]
    )
```

---

## Future Enhancements

- [ ] Nested tasks/subtasks (tasks.tasks array)
- [ ] Time tracking fields (estimate_hours, actual_hours)
- [ ] Task dependencies (depends_on, blocks)
- [ ] Comment threads (comments array)
- [ ] Attachment/file references
- [ ] Custom field schema per mission
- [ ] Workflow automation rules
- [ ] SLA/service level indicators

---

## Summary

✅ **Unified Format** — Single schema for all task types
✅ **AI-Ready** — Complete metadata for LLM processing
✅ **Import-Friendly** — Support for calendar, email, invites, etc.
✅ **Extensible** — Metadata object for custom fields
✅ **Backward Compatible** — Existing tasks still work
✅ **Type-Aware** — Different types handled appropriately
✅ **Query-Rich** — Filter by type, source, date, tags
✅ **Human-Readable** — JSON format for version control

This format transforms task management from a simple to-do system into a **comprehensive, AI-friendly knowledge base** integrated across all uDOS interfaces.
