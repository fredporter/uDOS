# Config Import/Export — Settings Transfer Between Devices

**Feature Added:** 2026-01-24  
**Status:** Implemented in Wizard Server v1.1.0+  
**UI Location:** Wizard Dashboard → Configuration page

---

## Overview

The import/export feature allows you to backup and transfer Wizard configuration settings (API keys, webhooks, OAuth tokens, etc.) between devices securely.

### Use Cases

- **Device Migration**: Move your Wizard setup from an old device to a new one
- **Settings Backup**: Export a snapshot of your current configuration
- **Team Onboarding**: Share configuration templates with team members (without secrets)
- **Multi-Device Setup**: Sync settings across multiple Wizard instances

---

## How It Works

### Export Settings

**To export:**

1. Open Wizard Dashboard → **Configuration** page
2. Click **📤 Export Settings** button
3. Select configs to export:
   - ⚙️ Wizard Settings
   - 🤖 Assistant Keys
   - 🐙 GitHub Keys
   - 📔 Notion Integration
   - 🔐 OAuth Providers
   - 💬 Slack Integration
   - 📈 HubSpot
4. Choose security level:
   - **Redacted (default)**: API keys replaced with `***REDACTED***` — safe to share
   - **Full Export**: Include actual API keys — keep file secure!
5. Click **📥 Export & Download**

**Output:** Timestamped JSON file (e.g., `udos-config-export-2026-01-24T15-30-45Z.json`)

### Import Settings

**To import:**

1. Open Wizard Dashboard → **Configuration** page
2. Click **📥 Import Settings** button
3. Select an exported JSON file
4. Review the preview:
   - Shows what configs will be imported
   - Highlights conflicts (existing configs on device)
   - Shows redacted vs full imports
5. Choose conflict handling:
   - **Don't overwrite** (default): Skip existing configs
   - **Overwrite conflicts**: Replace existing configs
6. Click **✓ Import**

**Result:** Configs written to `wizard/config/` (local machine only, never shared)

---

## API Endpoints

### POST `/api/config/export`

**Request:**

```json
{
  "file_ids": ["wizard", "github_keys", "oauth"],
  "include_secrets": false
}
```

**Response:**

```json
{
  "success": true,
  "filename": "udos-config-export-2026-01-24T15-30-45Z.json",
  "path": "/path/to/file",
  "size": 2048,
  "timestamp": "2026-01-24T15:30:45Z",
  "exported_configs": ["wizard", "github_keys", "oauth"],
  "include_secrets": false,
  "warning": "⚠️ This file contains secrets. Keep it secure!"
}
```

### GET `/api/config/export/list`

Lists all previous exports (for re-downloading).

**Response:**

```json
{
  "exports": [
    {
      "filename": "udos-config-export-2026-01-24T15-30-45Z.json",
      "path": "/path/to/file",
      "size": 2048,
      "modified": "2026-01-24T15:30:45Z"
    }
  ]
}
```

### GET `/api/config/export/{filename}`

Download a previously exported file.

### POST `/api/config/import`

Preview what will be imported (validates file, shows conflicts).

**Request:** Multipart form file upload

**Response:**

```json
{
  "success": true,
  "preview": {
    "wizard": {
      "filename": "wizard.json",
      "has_content": true,
      "is_redacted": false
    },
    "github_keys": {
      "filename": "github_keys.json",
      "has_content": true,
      "is_redacted": true
    }
  },
  "conflicts": ["wizard"],
  "timestamp": "2026-01-24T15:30:45Z",
  "exported_from": "uDOS Wizard Server"
}
```

### POST `/api/config/import/chunked`

Import configs from file (one-step process).

**Request:** Multipart form file + JSON body:

```json
{
  "overwrite_conflicts": false,
  "file_ids": ["wizard", "github_keys"]
}
```

**Response:**

```json
{
  "success": true,
  "imported": ["wizard", "github_keys"],
  "skipped": [
    {
      "file_id": "oauth",
      "reason": "Config was redacted during export"
    }
  ],
  "errors": [],
  "timestamp": "2026-01-24T15:30:45Z"
}
```

---

## File Format

Export files are standard JSON with metadata:

```json
{
  "export_timestamp": "2026-01-24T15:30:45Z",
  "exported_from": "uDOS Wizard Server",
  "version": "1.0",
  "include_secrets": false,
  "configs": {
    "wizard": {
      "filename": "wizard.json",
      "content": {
        "host": "0.0.0.0",
        "port": 8765,
        "ai_gateway_enabled": true,
        "plugin_repo_enabled": true
      }
    },
    "github_keys": {
      "filename": "github_keys.json",
      "content": {
        "token": "***REDACTED***",
        "webhook_secret": "***REDACTED***"
      }
    }
  }
}
```

---

## Security Considerations

### ✅ Safe Practices

- ✓ Export with **redacted secrets** (default) for team/public sharing
- ✓ Store full exports in secure location (encrypted volume)
- ✓ Delete exported files after transfer
- ✓ Never commit exports to git (add to `.gitignore`)
- ✓ Verify file ownership before importing
- ✓ Review preview before applying import

### ⚠️ Warnings

- **Redacted exports:** Missing actual API keys — you'll need to re-enter them on new device
- **Full exports:** Contain secrets — keep encrypted and delete after use
- **File transfers:** Use secure transport (encrypted email, USB drive, etc.)
- **Shared configs:** Test on non-production device first

### 🔒 Implementation Details

- All configs stored locally only (never uploaded)
- Files written to `wizard/config/` with restricted permissions
- No automatic overwrite of existing configs
- Preview step prevents accidental overwrites
- Redaction applied automatically for safety

---

## Examples

### Scenario 1: Migrate to New Machine

1. **On old machine:**
   - Export: ⚙️ Wizard, 🤖 Assistant Keys, 🐙 GitHub
   - Choose: **Full Export** (include secrets)
   - Download file
   - Securely transfer to new machine

2. **On new machine:**
   - Import: Select transferred file
   - Review: Confirm no conflicts (first setup)
   - Apply: Click Import
   - Test: Verify APIs work

### Scenario 2: Share Setup Template (No Secrets)

1. **Export:** Select ⚙️ Wizard only, **Redacted** (default)
2. **Share:** Send file to team
3. **Their import:**
   - Preview shows structure
   - Redacted values show they need to add their own keys
   - They apply and fill in their settings

### Scenario 3: Backup Current Settings

1. **Export:** Select all configs, **Redacted**
2. **Store:** Save to encrypted backup location
3. **Later:** If settings corrupted, re-import from backup
4. **Add secrets:** Re-enter API keys from secure storage

---

## Troubleshooting

### Import Shows "Redacted" Values

**Problem:** Exported file had `include_secrets=false`

**Solution:**

- You must manually re-enter API keys
- OR get full export from original device

### "Config Already Exists" Error

**Problem:** You're importing but config already exists

**Solution:**

- Check "Overwrite existing configs" if you want to replace
- Or review and delete conflicting configs first

### Import Preview Looks Empty

**Problem:** Export file doesn't have content for that config

**Solution:**

- Check that configs were actually set on export device
- Re-export with all desired configs selected

---

## Related Docs

- [docs/specs/wizard-config-structure.md](../specs/wizard-config-structure.md) — Config file format
- [wizard/README.md](../../wizard/README.md) — Wizard Server overview
- [AGENTS.md](../../AGENTS.md) — Security policies

---

_Last Updated: 2026-01-24_  
_uDOS Wizard Server v1.1.0+_
