# Phase 4: Notification History & Export

**Status:** 🚀 In Progress  
**Date Started:** 2026-01-17  
**Target Completion:** 2026-01-19

---

## Mission

Persist toast notifications to SQLite, build history viewer UI, and export to JSON/CSV/Markdown.

---

## Architecture

### Database Schema (`/memory/notifications.db`)

```sql
-- Notifications log
CREATE TABLE notifications (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,           -- info, success, warning, error, progress
  title TEXT,
  message TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  duration_ms INTEGER,          -- 5000, 0 for sticky
  sticky BOOLEAN DEFAULT FALSE,
  action_count INTEGER DEFAULT 0,
  dismissed_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Actions within notifications
CREATE TABLE notification_actions (
  id TEXT PRIMARY KEY,
  notification_id TEXT NOT NULL,
  label TEXT NOT NULL,
  action_type TEXT,             -- primary, secondary
  callback_data TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(notification_id) REFERENCES notifications(id)
);

-- Export history
CREATE TABLE notification_exports (
  id TEXT PRIMARY KEY,
  export_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  format TEXT NOT NULL,         -- json, csv, markdown
  file_path TEXT,
  record_count INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_notifications_timestamp ON notifications(timestamp);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_actions_notification_id ON notification_actions(notification_id);
```

### Service Layer

**Backend (`/wizard/services/notification_history_service.py`)**

- `save_notification(id, type, title, message, duration, sticky)` → persist to DB
- `get_notifications(limit, offset, start_date, end_date)` → paginated history
- `search_notifications(query, type_filter)` → full-text search
- `delete_notification(id)` → remove single
- `clear_old_notifications(days=30)` → auto-cleanup
- `export_notifications(format, date_range)` → JSON/CSV/Markdown
- `get_stats()` → count by type, total saved

**Frontend (`/app/src/lib/notification-db.ts`)**

- `saveNotification()` → Tauri invoke backend
- `getHistory()` → Fetch from backend
- `searchHistory()` → Query with filters
- `exportHistory()` → Trigger export + download

### UI Components

**Notification History Viewer**

- `/app/src/components/NotificationHistory/NotificationHistory.svelte`

  - List with pagination (20 per page)
  - Filter by type (info, success, warning, error)
  - Date range picker
  - Search box
  - Export buttons (JSON, CSV, Markdown)
  - Delete individual or bulk

- `/app/src/components/NotificationHistory/NotificationHistoryItem.svelte`

  - Display notification details
  - Timestamp + duration
  - Type badge with color
  - Actions count
  - Delete button

- `/app/src/components/NotificationHistory/ExportModal.svelte`
  - Select format (JSON, CSV, Markdown)
  - Date range selector
  - File name input
  - Progress indicator
  - Download link

### Export Formats

**JSON** - Full structured export

```json
{
  "exported_at": "2026-01-17T14:30:00Z",
  "total_records": 42,
  "notifications": [
    {
      "id": "toast-123",
      "type": "success",
      "title": "Saved",
      "message": "/Users/fred/file.txt",
      "timestamp": "2026-01-17T14:25:00Z",
      "duration_ms": 5000,
      "sticky": false
    }
  ]
}
```

**CSV** - Tabular format

```
id,type,title,message,timestamp,duration_ms,sticky
toast-123,success,Saved,/Users/fred/file.txt,2026-01-17T14:25:00Z,5000,false
```

**Markdown** - Human-readable

```markdown
# Notification History Export

Generated: 2026-01-17 14:30 UTC

## Summary

- Total: 42 notifications
- Success: 28 | Info: 10 | Warning: 3 | Error: 1

## Notifications

### Success (28)

- **[14:25]** Saved: /Users/fred/file.txt
```

---

## Implementation Plan

### Step 1: SQLite Schema & Tauri Bridge (1 day)

- [ ] Create notification_history_service.py
- [ ] Tauri command handlers for CRUD ops
- [ ] Database migration on app startup

### Step 2: Frontend Utilities (1 day)

- [ ] notification-db.ts with Tauri invoke wrapper
- [ ] notificationHistory store (Svelte writable)
- [ ] Auto-save integration with toast store

### Step 3: UI Components (2 days)

- [ ] NotificationHistory.svelte + item component
- [ ] Search, filter, pagination logic
- [ ] Export modal dialog

### Step 4: Export Logic (1 day)

- [ ] JSON formatter
- [ ] CSV formatter
- [ ] Markdown formatter
- [ ] File download via Tauri

### Step 5: Integration & Testing (1 day)

- [ ] Wire into App.svelte
- [ ] Test persistence across restarts
- [ ] Verify all 3 export formats
- [ ] UI/UX polish

### Step 6: Documentation (1 day)

- [ ] NOTIFICATION-HISTORY.md guide
- [ ] Usage examples
- [ ] Troubleshooting
- [ ] Update devlog

---

## Success Criteria

✅ Notifications persisted to SQLite with full metadata  
✅ History UI shows last 100 notifications with pagination  
✅ Search by title/message/type works  
✅ Export to JSON, CSV, Markdown produces correct output  
✅ Auto-cleanup removes notifications older than 30 days  
✅ File download saves to user's downloads folder  
✅ UI integrated into App.svelte sidebar or modal  
✅ All 3 export formats tested with real data

---

## File Structure After Phase 4

```
/app/src/
├── components/
│   ├── NotificationHistory/
│   │   ├── NotificationHistory.svelte
│   │   ├── NotificationHistoryItem.svelte
│   │   └── ExportModal.svelte
│   └── Toast/
├── lib/
│   └── notification-db.ts
└── stores/
    ├── notifications.ts (existing)
    └── notificationHistory.ts (new - pagination state)

/wizard/services/
└── notification_history_service.py (new - 300-400 lines)

/memory/
└── notifications.db (auto-created on first toast save)
```

---

## Phase 4 Progress

| Component       | Status | Lines       | Completed |
| --------------- | ------ | ----------- | --------- |
| SQLite Schema   | ⏳     | -           | 0%        |
| Backend Service | ⏳     | 0/350       | 0%        |
| Frontend Utils  | ⏳     | 0/100       | 0%        |
| UI Components   | ⏳     | 0/400       | 0%        |
| Export Logic    | ⏳     | 0/150       | 0%        |
| Integration     | ⏳     | 0/50        | 0%        |
| Documentation   | ⏳     | 0/300       | 0%        |
| **TOTAL**       | **⏳** | **0/1,350** | **0%**    |

---

**Phase 4 Kickoff:** 2026-01-17  
**Estimated Completion:** 2026-01-19  
**Next Milestone:** v1.0.6.0 complete with full notification history + export system
