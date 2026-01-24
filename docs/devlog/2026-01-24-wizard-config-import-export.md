# Wizard Settings Import/Export - Device Transfer Support

**Date:** 2026-01-24  
**Status:** Complete  
**Scope:** Wizard Server v1.1.0+

---

## Summary

Added comprehensive import/export functionality to Wizard Dashboard Configuration page, enabling secure settings backup and transfer between devices.

## Changes Made

### 1. Backend API Endpoints

**File:** [wizard/routes/config_routes.py](../../wizard/routes/config_routes.py)

#### New Endpoints

| Endpoint                           | Method | Purpose                                          |
| ---------------------------------- | ------ | ------------------------------------------------ |
| `/api/v1/config/export`            | POST   | Export selected configs to timestamped JSON file |
| `/api/v1/config/export/list`       | GET    | List all previous export files                   |
| `/api/v1/config/export/{filename}` | GET    | Download a specific export file                  |
| `/api/v1/config/import`            | POST   | Preview what will be imported (validation)       |
| `/api/v1/config/import/chunked`    | POST   | Import and apply configs from file               |

#### Features

- **Timestamped exports** - Each export gets unique filename: `udos-config-export-YYYY-MM-DDTHH-MM-SSZ.json`
- **Selective export** - Choose which configs to include
- **Security levels** - Redacted (safe, default) or full (include secrets)
- **Conflict detection** - Identify which configs already exist on import device
- **Validation before apply** - Two-step import (preview + confirm)
- **Flexible apply** - Can overwrite existing or skip conflicts

### 2. Frontend UI

**File:** [wizard/dashboard/src/routes/Config.svelte](../../wizard/dashboard/src/routes/Config.svelte)

#### New UI Elements

**Export Modal:**

- Config selection checkboxes (all configs included)
- Security warning about sensitive data
- Toggle for "Include secrets" option
- Download button with progress
- File saved to `memory/config_exports/`

**Import Modal:**

- File upload with drag-drop-style interface
- Preview of what will be imported
- Conflict detection (highlights existing configs)
- Redacted value indicators
- Overwrite toggle for conflicts
- Two-step flow: upload → preview → import

**Main Page Buttons:**

- 📤 Export Settings (blue button)
- 📥 Import Settings (purple button)
- Located above config editor for easy access

### 3. Data Structure

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
        /* ...config... */
      }
    },
    "github_keys": {
      "filename": "github_keys.json",
      "content": { "token": "***REDACTED***" }
    }
  }
}
```

---

## Security Considerations

### ✅ Implemented

- **Automatic redaction** - API keys replaced with `***REDACTED***` by default
- **User choice** - "Include secrets" requires explicit checkbox
- **Conflict prevention** - Asks before overwriting existing configs
- **File isolation** - Exports stored in `memory/config_exports/` (never committed)
- **Preview validation** - Users can review imports before applying
- **Filename safety** - Path traversal checks on import (only allows `udos-config-export-*.json`)

### Warnings Displayed

- ⚠️ "This file contains secrets" when using full export
- ⚠️ "Never commit to git" reminder
- ⚠️ "Keep it secure and delete after transfer"
- ⚠️ Shows which configs have redacted values

---

## Use Cases Enabled

### 1. Device Migration

Export full settings from old device → Import to new device → Re-enter secrets

### 2. Settings Backup

Regular export snapshots for disaster recovery

### 3. Team Onboarding

Export with redacted secrets → Share template → Team fills in their own keys

### 4. Multi-Device Sync

Export from primary Wizard → Import on secondary instances

---

## Testing Checklist

- [x] Export endpoint accepts config list
- [x] Redaction works (secrets hidden by default)
- [x] Include-secrets toggle works
- [x] Export creates timestamped JSON file
- [x] Download endpoint serves file correctly
- [x] Import preview validates file structure
- [x] Conflict detection identifies existing configs
- [x] Import apply writes configs to correct location
- [x] Overwrite toggle prevents accidental overwrites
- [x] UI modals are accessible (keyboard navigation)
- [x] Error messages are clear and helpful
- [x] Status messages confirm success/failure

---

## Files Modified

| File                                                                                         | Changes                                     | Lines    |
| -------------------------------------------------------------------------------------------- | ------------------------------------------- | -------- |
| [wizard/routes/config_routes.py](../../wizard/routes/config_routes.py)                       | Added 5 new endpoints + import/export logic | +450     |
| [wizard/dashboard/src/routes/Config.svelte](../../wizard/dashboard/src/routes/Config.svelte) | Added UI buttons, modals, functions         | +380     |
| [docs/features/config-import-export.md](../features/config-import-export.md)                 | Full feature documentation                  | New file |

---

## Related Documentation

- [docs/features/config-import-export.md](../features/config-import-export.md) - User guide
- [wizard/README.md](../../wizard/README.md) - Wizard Server overview
- [AGENTS.md](../../AGENTS.md) - Architecture & security policies

---

## Notes

### Design Decisions

1. **Redacted by default** - Prioritize security over convenience
2. **Two-step import** - Prevent accidental overwrites
3. **Timestamped filenames** - Easy to identify which export is which
4. **Local storage only** - Never expose configs via API
5. **Selective export** - Users control what to include

### Future Enhancements

- Encryption support for export files
- Scheduled automatic exports
- Export history with diff view
- Selective reimport (choose which configs to apply)
- Integration with git-backed config versioning

---

_Updated: 2026-01-24_  
_Implementation: Wizard Server Config Management_
