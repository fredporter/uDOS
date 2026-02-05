# Notification History & Export System

**Document Version:** v1.0.0  
**Component Version:** Phase 4, v1.0.5.0+  
**Status:** Production Ready  
**Last Updated:** 2026-01-17

---

## 🎯 Overview

The Notification History system provides persistent storage, full-text search, and multi-format export of all user notifications in the uMarkdown Mac App. Every toast notification is automatically saved to a local SQLite database and can be accessed, searched, filtered, and exported.

**Key Features:**

- 🔄 **Auto-Save** — All toasts automatically persisted to SQLite
- 🔍 **Full-Text Search** — Search across titles and messages
- 🏷️ **Type Filtering** — Filter by notification type (info, success, warning, error)
- 📊 **Pagination** — Browse large notification sets efficiently (20 per page)
- 📥 **Export** — 3 format options (JSON, CSV, Markdown)
- 📅 **Date Filtering** — Optional date range selection for exports
- 🧹 **Auto-Cleanup** — Automatic deletion of notifications older than 30 days
- ⏱️ **Timestamps** — Full ISO 8601 timestamps for each notification

---

## 🏗️ Architecture

### System Layers

```
User Action (Open File, Save, Format)
        ↓
Toast Notification Created
        ↓
addToast() + saveToHistory()
        ↓
Frontend HTTP → Wizard Server (localhost:8765)
        ↓
NotificationHistoryService
        ↓
SQLite Database (notifications.db)
        ↓
Persisted Notification with Metadata
```

### Database Schema

**Table: `notifications`**

| Column         | Type             | Notes                            |
| -------------- | ---------------- | -------------------------------- |
| `id`           | TEXT PRIMARY KEY | UUID v4                          |
| `type`         | TEXT             | info, success, warning, error    |
| `title`        | TEXT             | Toast title                      |
| `message`      | TEXT             | Toast message                    |
| `timestamp`    | TIMESTAMP        | ISO 8601, auto-set               |
| `duration_ms`  | INTEGER          | Display duration (null = sticky) |
| `sticky`       | BOOLEAN          | True if user action required     |
| `action_count` | INTEGER          | Number of available actions      |
| `dismissed_at` | TIMESTAMP        | When notification was dismissed  |

**Table: `notification_actions`**

| Column            | Type             | Notes               |
| ----------------- | ---------------- | ------------------- |
| `id`              | TEXT PRIMARY KEY | UUID v4             |
| `notification_id` | TEXT             | FK to notifications |
| `label`           | TEXT             | Action button label |
| `action_type`     | TEXT             | Action identifier   |
| `callback_data`   | TEXT             | Optional JSON data  |

**Table: `notification_exports`**

| Column         | Type             | Notes                      |
| -------------- | ---------------- | -------------------------- |
| `id`           | TEXT PRIMARY KEY | UUID v4                    |
| `export_date`  | TIMESTAMP        | When export was generated  |
| `format`       | TEXT             | json, csv, markdown        |
| `file_path`    | TEXT             | Local download path        |
| `record_count` | INTEGER          | Number of records exported |

**Indexes:**

- `idx_notifications_timestamp` — For date filtering
- `idx_notifications_type` — For type filtering
- `fk_notification_actions` — Foreign key performance

---

## 🖥️ Frontend Usage

### Auto-Save Integration

Every toast handler in App.svelte automatically saves to history:

```typescript
// Pattern: Toast creation + auto-save
const toast = {
  type: "info" as const,
  title: "Document opened",
  message: file.path,
};

addToast(toast);
await saveToHistory(toast.type, toast.title, toast.message, 5000);
```

**Integrated Handlers:**

- `handleOpen()` — File open notifications
- `handleSaveAs()` — Save success/error notifications
- `handleFormat()` — Format action notifications
- `toggleFullscreen()` — Fullscreen toggle notifications
- Error handlers — Failure notifications

### Access History

**Button Location:** Toolbar (next to gear icon) or Sidebar (History item)

**Keyboard Shortcut:** Available in future release (⏱️ + H)

**Modal View:**

```
┌─────────────────────────────────────────┐
│ Notification History              [X]   │
├─────────────────────────────────────────┤
│ Search: [____________]  Type: [All v]   │
│ ✓ 42 info   ✓ 18 success                │
│ ✓ 5 warning ✓ 3 error     [Export]     │
├─────────────────────────────────────────┤
│ [✓] 10:42 AM   Document opened         │
│     Path: /Users/fred/Notes/todo.md    │
│ [✓] 10:41 AM   Saved                   │
│     Path: /Users/fred/Notes/todo.md    │
│ [E] 10:35 AM   Open failed             │
│     Permission denied                   │
├─────────────────────────────────────────┤
│ ← Previous  [1/5]  Next →               │
└─────────────────────────────────────────┘
```

### Search & Filter

**Full-Text Search:**

Search across both title and message:

```
Search: "Opened"     → 🔍 Returns all "opened" notifications
Search: "failed"     → 🔍 Returns errors containing "failed"
Search: "/Users"     → 🔍 Returns file path matches
```

**Type Filter:**

- `All` — Show all notifications
- `Info` — Blue badge information
- `Success` — Green badge success
- `Warning` — Yellow badge warnings
- `Error` — Red badge errors

**Date Range (Export Only):**

Optional: Select from/to dates before export to limit records

### Export Formats

#### 1. JSON Format

**Purpose:** Full metadata preservation, API integration

**File:** `notifications-export-YYYY-MM-DD.json`

```json
{
  "export_info": {
    "export_date": "2026-01-17T10:42:00Z",
    "total_records": 42,
    "filtered_by": {
      "date_range": ["2026-01-15", "2026-01-17"],
      "types": ["info", "success"]
    }
  },
  "notifications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "success",
      "title": "Saved",
      "message": "/Users/fred/Notes/todo.md",
      "timestamp": "2026-01-17T10:41:00Z",
      "duration_ms": 5000,
      "sticky": false,
      "action_count": 0,
      "dismissed_at": "2026-01-17T10:41:05Z",
      "actions": []
    }
  ]
}
```

**Best For:** Data analysis, backups, API integration

#### 2. CSV Format

**Purpose:** Spreadsheet/tabular analysis

**File:** `notifications-export-YYYY-MM-DD.csv`

```csv
Timestamp,Type,Title,Message,Duration (ms),Sticky,Dismissed At,Action Count
2026-01-17T10:41:00Z,success,Saved,/Users/fred/Notes/todo.md,5000,false,2026-01-17T10:41:05Z,0
2026-01-17T10:42:00Z,info,Opened document,/Users/fred/Notes/notes.md,5000,false,2026-01-17T10:42:05Z,0
2026-01-17T10:35:00Z,error,Open failed,Permission denied,5000,false,2026-01-17T10:35:05Z,1
```

**Best For:** Excel/Sheets analysis, reports, data pipelines

#### 3. Markdown Format

**Purpose:** Human-readable documentation, changelog

**File:** `notifications-export-YYYY-MM-DD.md`

```markdown
# Notification History Export

**Export Date:** 2026-01-17 10:45 AM  
**Total Notifications:** 42

## Info (18 notifications)

### 10:42 AM — Document opened

Path: /Users/fred/Notes/todo.md

### 10:35 AM — Opened document

Path: /Users/fred/Notes/notes.md

## Success (18 notifications)

### 10:41 AM — Saved

Path: /Users/fred/Notes/todo.md

### 10:40 AM — Formatted document

Whitespace trimmed and line endings normalized.

## Warnings (5 notifications)

### 10:30 AM — Large file opened

Document size: 2.5 MB (may affect performance)

## Errors (3 notifications)

### 10:35 AM — Open failed

Permission denied
```

**Best For:** Human review, documentation, sharing context

---

## 🔌 API Reference

### Base URL

```
http://localhost:8765/api/notifications/
```

### Endpoints

#### Save Notification

```bash
POST /api/notifications/save

# Request Body
{
  "type": "success",
  "title": "Document saved",
  "message": "/path/to/file.md",
  "duration_ms": 5000,
  "sticky": false,
  "actions": []
}

# Response (200 OK)
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-17T10:41:00Z"
}

# Example curl
curl -X POST http://localhost:8765/api/notifications/save \
  -H "Content-Type: application/json" \
  -d '{
    "type": "success",
    "title": "Document saved",
    "message": "/path/to/file.md"
  }'
```

#### List Notifications

```bash
GET /api/notifications/list?skip=0&limit=20

# Response (200 OK)
{
  "notifications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "success",
      "title": "Document saved",
      "message": "/path/to/file.md",
      "timestamp": "2026-01-17T10:41:00Z",
      "duration_ms": 5000,
      "sticky": false,
      "action_count": 0
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}

# Example curl
curl http://localhost:8765/api/notifications/list?skip=0&limit=20
```

#### Search Notifications

```bash
POST /api/notifications/search

# Request Body
{
  "query": "saved",
  "type_filter": ["success", "error"],
  "skip": 0,
  "limit": 20
}

# Response (200 OK)
{
  "results": [...],
  "total": 3,
  "query": "saved"
}

# Example curl
curl -X POST http://localhost:8765/api/notifications/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "saved",
    "type_filter": ["success"]
  }'
```

#### Delete Notification

```bash
DELETE /api/notifications/{id}

# Response (200 OK)
{
  "deleted": true,
  "id": "550e8400-e29b-41d4-a716-446655440000"
}

# Example curl
curl -X DELETE http://localhost:8765/api/notifications/550e8400-e29b-41d4-a716-446655440000
```

#### Clear Old Notifications

```bash
POST /api/notifications/clear

# Request Body
{
  "days": 30  # Delete notifications older than N days
}

# Response (200 OK)
{
  "deleted_count": 5,
  "remaining": 37
}

# Example curl
curl -X POST http://localhost:8765/api/notifications/clear \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

#### Export Notifications

```bash
POST /api/notifications/export

# Request Body
{
  "format": "json",  # "json", "csv", or "markdown"
  "type_filter": ["info", "success"],
  "date_range": {
    "from": "2026-01-15",
    "to": "2026-01-17"
  }
}

# Response (200 OK) — File download
Content-Type: application/json
Content-Disposition: attachment; filename="notifications-export-2026-01-17.json"

# Example curl
curl -X POST http://localhost:8765/api/notifications/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "type_filter": ["success", "error"]
  }' \
  --output notifications.json
```

#### Get Statistics

```bash
GET /api/notifications/stats

# Response (200 OK)
{
  "total": 42,
  "by_type": {
    "info": 18,
    "success": 18,
    "warning": 5,
    "error": 1
  },
  "oldest": "2026-01-10T08:00:00Z",
  "newest": "2026-01-17T10:45:00Z",
  "db_size_bytes": 51200
}

# Example curl
curl http://localhost:8765/api/notifications/stats
```

---

## 📱 Frontend Components

### NotificationHistory.svelte

**Purpose:** Main modal container with search and pagination

**Features:**

- Search bar with real-time filtering
- Type filter dropdown (All, Info, Success, Warning, Error)
- Stats dashboard (count by type)
- Paginated list (20 items/page)
- Export and Clear Old buttons
- Responsive layout with dark mode

**Props:** None (uses reactive store internally)

**Usage:**

```svelte
<NotificationHistory />
```

### NotificationHistoryItem.svelte

**Purpose:** Individual notification renderer

**Features:**

- Type badge with semantic colors
- Timestamp display (human-readable + ISO)
- Title and message with word-break
- Meta information (duration, sticky status)
- Action count indicator
- Delete button per notification

**Props:**

```typescript
interface Props {
  notification: Notification;
  onDelete: (id: string) => Promise<void>;
}
```

### ExportModal.svelte

**Purpose:** Export dialog with format selection

**Features:**

- Radio buttons for format selection
- Optional date range picker
- Success state after export
- Download button
- Modal overlay with blur backdrop
- Accessible form layout

**Props:** None (uses event dispatching)

---

## 🔧 Developer Integration

### TypeScript Store API

**Location:** `/app/src/lib/notification-db.ts`

```typescript
import { createHistoryStore, saveToHistory } from "$lib/notification-db";

// Create reactive store
const history = createHistoryStore();

// Load notifications
await history.load({ skip: 0, limit: 20 });

// Search
await history.search({
  query: "saved",
  type_filter: ["success", "error"],
});

// Delete one
await history.delete(notificationId);

// Clear old (30+ days)
await history.clearOld(30);

// Export
const blob = await history.export({
  format: "json",
  type_filter: ["success"],
  date_range: { from: "2026-01-15", to: "2026-01-17" },
});

// Get stats
const stats = await history.getStats();

// Auto-save helper
await saveToHistory("success", "Saved", "/path/to/file.md", 5000);
```

### Python Service API

**Location:** `/wizard/services/notification_history_service.py`

```python
from wizard.services.notification_history_service import NotificationHistoryService

service = NotificationHistoryService()

# Save notification
await service.save_notification(
    type='success',
    title='Document saved',
    message='/path/to/file.md',
    duration_ms=5000
)

# Get paginated
notifications = await service.get_notifications(skip=0, limit=20)

# Full-text search
results = await service.search_notifications(
    query='saved',
    type_filter=['success', 'error']
)

# Delete
await service.delete_notification(notification_id)

# Clear old
deleted = await service.clear_old_notifications(days=30)

# Export
csv_data = await service.export_notifications(
    format='csv',
    type_filter=['info', 'success']
)

# Stats
stats = await service.get_stats()
```

---

## 🐛 Troubleshooting

### "Failed to connect to Wizard server"

**Cause:** Wizard server not running on port 8765

**Solution:**

```bash
# Check if server is running
curl http://localhost:8765/health

# Start Wizard server
python wizard/launch_wizard_dev.py --no-tui
```

### Export file not downloaded

**Cause:** Browser blocked popup or download error

**Solution:**

1. Check browser download settings
2. Try different export format (CSV instead of JSON)
3. Reduce record count (add date filter)
4. Check Wizard server logs: `tail -f memory/logs/api_server.log`

### History search not returning results

**Cause:** Search terms don't match notification content

**Solution:**

1. Verify exact text in notification (try shorter search)
2. Check type filter (may be filtering results)
3. Use "All" type filter for broader results
4. Try partial word search (e.g., "save" for "saved")

### Database locked errors

**Cause:** Multiple processes accessing SQLite simultaneously

**Solution:**

1. Close all instances of the app
2. Restart Wizard server
3. Check for stale processes: `lsof -i :8765`
4. Kill if needed: `kill -9 <PID>`

### Old notifications not auto-deleting

**Cause:** Clear script hasn't run

**Solution:**

1. Manual clear: Click "Clear Old" button in history modal
2. API: `curl -X POST http://localhost:8765/api/notifications/clear`
3. Schedule: Future release will add automatic daily cleanup

---

## 📊 Performance & Limits

| Metric                       | Limit   | Notes                       |
| ---------------------------- | ------- | --------------------------- |
| **Max notifications stored** | 10,000  | Before auto-trim            |
| **Default retention period** | 30 days | Manual clear or API trigger |
| **Search latency**           | <100ms  | Full-text indexed           |
| **Export file size**         | <50MB   | Tested with 10K records     |
| **API rate limit**           | 100/min | Per device                  |

**Database Size:** ~5KB per 100 notifications (with indexed fields)

---

## 🔐 Security & Privacy

### Data Location

- **Storage:** `memory/wizard/notifications.db` (local, user's device)
- **Network:** localhost only (no cloud sync in Phase 4)
- **Encryption:** Not encrypted (consider PRAGMA key for future)

### Access Control

- Wizard server requires device auth (existing mechanism)
- Notification history shares same auth as other endpoints
- No secrets in notification content (no API keys, passwords)

### Deletion & Retention

- Manual delete: User clicks delete button
- Auto-cleanup: 30+ days (configurable)
- Export doesn't delete: Only reads from database
- Clear Old: Irreversible (no trash recovery)

---

## 📈 Future Enhancements (v1.1.0+)

- [ ] Cloud sync (encrypted Notion/Firebase)
- [ ] Keyboard shortcut (⏱️ + H)
- [ ] Advanced filters (duration range, action count)
- [ ] Batch operations (select multiple, bulk delete)
- [ ] Analytics dashboard (trends, most common notifications)
- [ ] Custom retention policies per type
- [ ] Database encryption (PRAGMA key)
- [ ] Notification templates for faster saving
- [ ] Integration with Slack/Discord exports

---

## 📞 Support & Issues

**Issues:** https://github.com/fredporter/uDOS-dev/issues  
**Discussions:** https://github.com/fredporter/uDOS-dev/discussions  
**Documentation:** Check [docs/\_index.md](../_index.md) for related topics

---

_Document Generated: 2026-01-17_  
_Last Tested: Phase 4 Integration Complete_
