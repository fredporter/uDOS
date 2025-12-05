# Gmail Cloud Sync - v1.2.9

Complete guide to Gmail authentication, email importing, and Google Drive synchronization in uDOS.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Authentication](#authentication)
- [Email Operations](#email-operations)
- [Email Import](#email-import)
- [Cloud Sync](#cloud-sync)
- [Configuration](#configuration)
- [Quota Management](#quota-management)
- [Troubleshooting](#troubleshooting)
- [Security & Privacy](#security--privacy)

## Overview

Gmail Cloud Sync enables:
- ✅ **OAuth2 Authentication** - Secure login with personal Gmail account
- ✅ **Email Import** - Convert emails to notes, checklists, and missions
- ✅ **Task Extraction** - Auto-detect actionable items from email content
- ✅ **Google Drive Sync** - Bidirectional sync for memory/shared content
- ✅ **Conflict Resolution** - Smart handling of concurrent modifications
- ✅ **Quota Management** - Monitor and manage Drive storage (15 MB recommended)

**Key Features:**
- Zero password storage (OAuth2 only)
- Encrypted token persistence
- App-data-only Drive access (no access to personal files)
- Selective sync (choose what to sync)
- Offline-first (Gmail optional, not required)

## Setup

### Prerequisites

1. **Google Cloud Project** (free tier)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project: "uDOS Sync"
   - Enable APIs:
     - Gmail API
     - Google Drive API

2. **OAuth2 Credentials**
   - Navigate to: APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
     - Application type: Desktop app
     - Name: "uDOS Desktop"
   - Download JSON credentials

3. **Install Credentials**
   ```bash
   # Place downloaded credentials in:
   memory/system/user/gmail_credentials.json

   # Verify file exists:
   ls memory/system/user/gmail_credentials.json
   ```

### First-Time Setup

1. **Install Python Dependencies**
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client cryptography
   ```

2. **Run uDOS**
   ```bash
   ./start_udos.sh
   ```

3. **Authenticate**
   ```
   LOGIN GMAIL
   ```

   This will:
   - Open browser for Google consent
   - Request Gmail and Drive permissions
   - Save encrypted tokens to `.env`
   - Show your account info

4. **Verify Authentication**
   ```
   STATUS GMAIL
   ```

## Authentication

### LOGIN GMAIL

Start OAuth2 authentication flow.

**Usage:**
```
LOGIN GMAIL
```

**Process:**
1. Opens browser to Google consent screen
2. Select Google account
3. Grant permissions:
   - Gmail: Read and send emails
   - Drive: App data folder access
   - Profile: Email and name
4. Tokens saved encrypted in `.env`

**Output:**
```
🔐 Starting Gmail authentication...
A browser window will open for Google consent.
Please authorize uDOS to access your Gmail and Drive.

✅ Authentication successful!
Email: user@gmail.com
Name: Your Name

You can now use:
  - EMAIL LIST - View emails
  - EMAIL SEND - Send emails
  - SYNC GMAIL - Sync to Drive
```

### LOGOUT GMAIL

Revoke tokens and clear credentials.

**Usage:**
```
LOGOUT GMAIL
```

**Effect:**
- Revokes OAuth tokens with Google
- Deletes local encrypted tokens
- Clears Gmail/Drive service cache
- Requires re-authentication for future use

### STATUS GMAIL

Show current authentication status and quota.

**Usage:**
```
STATUS GMAIL
```

**Output:**
```
═══ Gmail Connection Status ═══

✅ Authenticated

Account:
  Email: user@gmail.com
  Name: Your Name

Tokens:
  Access token: Valid
  Token expires: 2025-12-06T10:30:00Z
  Time remaining: 55 minutes

OAuth Scopes:
  ✓ gmail.readonly - Read emails
  ✓ gmail.send - Send emails
  ✓ drive.appdata - App data folder
  ✓ userinfo.email - User profile

Last activity: 2 minutes ago
```

## Email Operations

### EMAIL LIST [query]

List recent emails with optional Gmail search query.

**Usage:**
```
EMAIL LIST                      # List 10 most recent
EMAIL LIST is:unread            # Unread only
EMAIL LIST from:boss@company.com # From specific sender
EMAIL LIST subject:project      # Subject contains "project"
```

**Output:**
```
📧 Found 5 email(s)

1. Weekly Project Update
   From: Boss <boss@company.com>
   Date: 2025-12-05T09:00:00Z
   Here are the tasks for this week...

2. Meeting Notes - Q1 Planning
   From: PM <pm@company.com>
   Date: 2025-12-04T14:30:00Z
   Thanks for attending the meeting...

...
```

**Gmail Query Syntax:**
- `is:unread` - Unread emails
- `is:starred` - Starred emails
- `from:email@example.com` - From specific sender
- `to:email@example.com` - To specific recipient
- `subject:keyword` - Subject contains keyword
- `after:2025/12/01` - After date
- `has:attachment` - Has attachments
- Combine with spaces: `is:unread from:boss`

### EMAIL DOWNLOAD <id>

Download specific email by ID and convert to markdown.

**Usage:**
```
EMAIL LIST                      # Get message IDs
EMAIL DOWNLOAD msg_abc123       # Download and convert
```

**Output:**
```
✅ Email downloaded and converted

Type: checklist
File: weekly_project_update_tasks.md
Path: memory/checklists/weekly_project_update_tasks.md

Subject: Weekly Project Update
From: boss@company.com
Date: 2025-12-05T09:00:00Z
```

**Auto-Detection:**
- **Mission** - 3+ tasks detected
- **Checklist** - 1-2 tasks detected
- **Note** - 0 tasks (informational)

### EMAIL TASKS [query]

Show all tasks extracted from emails.

**Usage:**
```
EMAIL TASKS                     # Tasks from unread emails
EMAIL TASKS from:boss           # Tasks from specific sender
EMAIL TASKS subject:project     # Tasks from project emails
```

**Output:**
```
📋 Found 12 task(s) in 5 email(s)

1. Review Q4 metrics by Friday
   From: boss@company.com
   Email: Weekly Project Update
   Deadline: Friday
   Priority: medium

2. Submit expense reports
   From: admin@company.com
   Email: Monthly Reminders
   Deadline: Dec 10
   Priority: high

...

Use 'IMPORT GMAIL --type=checklist' to create task list
Use 'IMPORT GMAIL --type=mission' to create mission workflow
```

## Email Import

### IMPORT GMAIL [query]

Import emails and convert to uDOS formats (notes/checklists/missions).

**Usage:**
```
IMPORT GMAIL                             # Import recent unread
IMPORT GMAIL --preview                   # Preview without importing
IMPORT GMAIL --type=mission from:boss    # Force mission format
IMPORT GMAIL --limit=5 is:starred        # Limit to 5 emails
```

**Options:**
- `--preview` - Show what would be created without creating files
- `--type=<format>` - Force specific format (note, checklist, mission)
- `--limit=<n>` - Limit number of emails to import

**Auto-Detection Logic:**
```
3+ tasks detected  → Mission workflow (.upy)
1-2 tasks detected → Checklist (.md)
0 tasks detected   → Note (.md)
```

**Output:**
```
📥 Importing 3 email(s)...

1. Weekly Project Update
   ✅ Created mission: weekly_project_update_mission.upy
   Tasks: 5

2. Meeting Reminder
   ✅ Created checklist: meeting_reminder_tasks.md
   Tasks: 2

3. FYI: Company News
   ✅ Created note: fyi_company_news.md
   Tasks: 0

============================================================
Import Summary:
  Notes: 1
  Checklists: 1
  Missions: 1
```

**Preview Mode:**
```
IMPORT GMAIL --preview is:unread

Would create:
  - Mission: urgent_production_issue_mission.upy (5 tasks)
  - Checklist: team_meeting_prep_tasks.md (2 tasks)
  - Note: newsletter_december.md (0 tasks)

Run without --preview to import
```

## Cloud Sync

### SYNC GMAIL

Run sync operation now (manual).

**Usage:**
```
SYNC GMAIL
```

**Process:**
1. Scan local syncable directories
2. Calculate MD5 checksums
3. Compare with cloud files
4. Upload new/modified local files
5. Download new/modified cloud files
6. Resolve conflicts (per strategy)
7. Update sync history

**Output:**
```
🔄 Starting sync...

✅ Sync completed successfully

Uploaded: 3
Downloaded: 1
Deleted: 0
Conflicts resolved: 1
```

### SYNC GMAIL STATUS

Show current sync status and history.

**Usage:**
```
SYNC GMAIL STATUS
```

**Output:**
```
═══ Sync Status ═══

✅ Auto-sync enabled (auto)
Interval: 300s
Conflict strategy: newest-wins

Last sync: 5 minutes ago

Last sync stats:
  Uploaded: 3
  Downloaded: 1
  Deleted: 0
  Conflicts: 1
  Errors: 0

Total syncs: 47
🔄 Background sync active
```

### SYNC GMAIL ENABLE [mode]

Enable automatic synchronization.

**Usage:**
```
SYNC GMAIL ENABLE                       # Enable with defaults
SYNC GMAIL ENABLE auto --interval=300   # Auto mode, 5 min interval
SYNC GMAIL ENABLE scheduled             # Scheduled mode
```

**Modes:**
- `auto` - Sync on file changes (default)
- `scheduled` - Sync at fixed interval

**Output:**
```
✅ Auto-sync enabled
Mode: auto
Interval: 300s

Use 'SYNC GMAIL DISABLE' to stop.
```

### SYNC GMAIL DISABLE

Disable automatic synchronization.

**Usage:**
```
SYNC GMAIL DISABLE
```

**Effect:**
- Stops background sync thread
- Manual sync still available via `SYNC GMAIL`

### SYNC GMAIL CHANGES

Show pending changes before syncing.

**Usage:**
```
SYNC GMAIL CHANGES
```

**Output:**
```
📋 Found 7 pending change(s)

New local files (3):
  • memory/missions/new_mission.upy
  • memory/docs/notes.md
  • memory/checklists/tasks.md

Modified local files (2):
  • memory/system/user/settings.json
  • memory/workflows/main.upy

New cloud files (1):
  • system_backup.json

Conflicts (1):
  • memory/docs/important.md

Use 'SYNC GMAIL' to sync now
```

### SYNC GMAIL HISTORY [limit]

Show sync operation history.

**Usage:**
```
SYNC GMAIL HISTORY          # Last 10 syncs
SYNC GMAIL HISTORY 20       # Last 20 syncs
```

**Output:**
```
📜 Last 10 sync operation(s)

1. 2025-12-05T10:25:00 ✅
   Up:3 Down:1 Del:0 Err:0

2. 2025-12-05T10:20:00 ✅
   Up:0 Down:2 Del:1 Err:0

3. 2025-12-05T10:15:00 ❌
   Up:0 Down:0 Del:0 Err:1
   Errors: 1

...
```

## Configuration

### CONFIG GMAIL

Show current sync configuration.

**Usage:**
```
CONFIG GMAIL
```

**Output:**
```
═══ Sync Configuration ═══

Enabled: True
Mode: auto
Interval: 300s
Conflict strategy: newest-wins

Syncable directories:
  ✓ memory/missions
  ✓ memory/workflows
  ✓ memory/checklists
  ✓ memory/system/user
  ✓ memory/docs
  ✓ memory/drafts

File types: .md, .upy, .json, .txt
Max file size: 1 MB
Total quota: 15 MB
```

### CONFIG GMAIL SET <key> <value>

Update sync settings.

**Usage:**
```
CONFIG GMAIL SET interval 600            # 10 minute interval
CONFIG GMAIL SET strategy local-wins     # Always prefer local
```

**Available Keys:**
- `interval` - Sync interval in seconds (60-3600)
- `strategy` - Conflict resolution strategy

**Conflict Strategies:**
- `newest-wins` - Use most recently modified (default)
- `local-wins` - Always prefer local version
- `cloud-wins` - Always prefer cloud version
- `manual` - Prompt user for each conflict

**Output:**
```
✅ Interval set to 600s
```

## Quota Management

### QUOTA GMAIL

Show Google Drive quota usage.

**Usage:**
```
QUOTA GMAIL
```

**Output:**
```
═══ Google Drive Quota ═══

Total Drive Storage: 15360.0 MB
Used: 245.2 MB (1.6%)
Available: 15114.8 MB

uDOS Sync Limit: 15 MB (recommended)
Sync Usage: 3.24 MB (21.6% of limit)
```

**Quota Management:**
- uDOS recommends 15 MB for sync (configurable)
- Only counts app data folder (not personal Drive files)
- Warning at 80% of limit
- Error at 100% of limit

**If Approaching Limit:**
1. Review synced files: `SYNC GMAIL CHANGES`
2. Clean up old files
3. Increase limit: `CONFIG GMAIL SET quota 20`
4. Disable unnecessary directories in config

## Troubleshooting

### Authentication Issues

**Problem:** "Not authenticated" error

**Solutions:**
1. Check credentials file exists:
   ```bash
   ls memory/system/user/gmail_credentials.json
   ```

2. Re-authenticate:
   ```
   LOGOUT GMAIL
   LOGIN GMAIL
   ```

3. Verify OAuth scopes in Google Cloud Console
4. Check `.env` file for encrypted tokens

**Problem:** "Token expired" error

**Solutions:**
- Tokens auto-refresh automatically
- If fails, run: `LOGOUT GMAIL` then `LOGIN GMAIL`

### Sync Issues

**Problem:** Files not syncing

**Solutions:**
1. Check sync is enabled:
   ```
   SYNC GMAIL STATUS
   ```

2. Check for errors:
   ```
   SYNC GMAIL HISTORY
   ```

3. Verify file types allowed:
   ```
   CONFIG GMAIL
   ```

4. Check quota:
   ```
   QUOTA GMAIL
   ```

**Problem:** Conflicts not resolving

**Solutions:**
1. Check current strategy:
   ```
   CONFIG GMAIL
   ```

2. Change strategy:
   ```
   CONFIG GMAIL SET strategy local-wins
   ```

3. Manual resolution:
   ```
   SYNC GMAIL CHANGES
   # Review conflicts
   # Edit files manually
   SYNC GMAIL
   ```

### Import Issues

**Problem:** Emails not importing

**Solutions:**
1. Test with preview:
   ```
   IMPORT GMAIL --preview
   ```

2. Check email format (HTML vs plain)
3. Verify task patterns recognized
4. Use specific query:
   ```
   EMAIL LIST from:sender@example.com
   ```

**Problem:** Wrong format chosen

**Solutions:**
- Force type:
  ```
  IMPORT GMAIL --type=mission subject:project
  ```

- Adjust auto-detection:
  - 3+ tasks = mission
  - 1-2 tasks = checklist
  - 0 tasks = note

## Security & Privacy

### OAuth2 Security

- **No password storage** - Only OAuth tokens
- **Encrypted tokens** - Fernet encryption in `.env`
- **Limited scopes** - Only requested permissions:
  - `gmail.readonly` - Read emails
  - `gmail.send` - Send emails
  - `drive.appdata` - App data folder only
  - `userinfo.email` - User profile

### Data Privacy

- **App-data-only access** - No access to personal Drive files
- **User controls** - You choose what syncs
- **Offline-first** - Gmail optional, not required
- **Local storage** - All data stored locally first
- **Encrypted tokens** - AES-256 encryption

### Best Practices

1. **Review permissions** before OAuth consent
2. **Use strong Google account** with 2FA
3. **Regular audits** - Check synced files periodically
4. **Selective sync** - Only sync what's necessary
5. **Monitor quota** - Prevent accidental overuse

### Revoking Access

**Option 1: Via uDOS**
```
LOGOUT GMAIL
```

**Option 2: Via Google Account**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Navigate to: Third-party apps with account access
3. Find "uDOS Desktop"
4. Click "Remove Access"

## Examples

### Daily Workflow

```
# Morning: Check emails and import tasks
STATUS GMAIL
EMAIL TASKS is:unread
IMPORT GMAIL --preview is:unread
IMPORT GMAIL --type=checklist is:unread

# Afternoon: Sync work
SYNC GMAIL STATUS
SYNC GMAIL CHANGES
SYNC GMAIL

# Evening: Review quota
QUOTA GMAIL
CONFIG GMAIL
```

### Project-Specific Import

```
# Import all project emails as missions
EMAIL LIST subject:project-alpha
IMPORT GMAIL --type=mission subject:project-alpha from:team@company.com

# Extract tasks from project thread
EMAIL TASKS subject:project-alpha
```

### Selective Sync Setup

```
# Configure sync for specific directories
CONFIG GMAIL
CONFIG GMAIL SET interval 600
CONFIG GMAIL SET strategy local-wins

# Enable auto-sync
SYNC GMAIL ENABLE auto --interval=600

# Monitor first sync
SYNC GMAIL STATUS
SYNC GMAIL CHANGES
SYNC GMAIL
```

## Related Documentation

- [Getting Started](Getting-Started.md) - uDOS basics
- [Command Reference](Command-Reference.md) - All commands
- [Extension Development](Extension-Development.md) - Build extensions
- [Knowledge System](Knowledge-System.md) - Offline knowledge bank

## Support

- **GitHub Issues**: [Report bugs](https://github.com/fredporter/uDOS/issues)
- **Discussions**: [Ask questions](https://github.com/fredporter/uDOS/discussions)
- **Wiki**: [More guides](https://github.com/fredporter/uDOS/wiki)

---

**Version:** 1.2.9
**Last Updated:** December 5, 2025
**Status:** ✅ Production Ready
