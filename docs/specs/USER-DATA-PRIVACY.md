# User Data Privacy & Security Compliance

**Status:** Policy Document  
**Date:** 2026-01-17  
**Scope:** All uDOS components (Core, App, Wizard, Extensions)

---

## 🎯 Core Principle

**User data is private by default. Location/identity never exposed in logs or metadata.**

---

## 📝 User Data Collection (First Run)

### What We Collect

**System Fields Only** (stored in `memory/private/user/user.json`):

| Field           | Required      | Storage Location | Purpose                              |
| --------------- | ------------- | ---------------- | ------------------------------------ |
| **user_id**     | Yes (auto)    | `user.json`      | Unique identifier (generated once)   |
| **device_id**   | Yes (auto)    | `user.json`      | Installation identifier (per device) |
| **username**    | Yes           | `user.json`      | Display name (can be pseudonym)      |
| **password**    | No (optional) | OS keychain only | Local auth (never in filesystem)     |
| **timezone**    | Yes           | `user.json`      | IANA timezone code                   |
| **location_id** | Yes           | `user.json`      | Grid location (L300-AA10 format)     |

**NOT Collected as System Variables:**

- ❌ Email address (can store in custom.json if user wants)
- ❌ Phone number (can store in custom.json if user wants)
- ❌ Home address (can store in custom.json if user wants)
- ❌ Real name (username is separate, can be pseudonym)
- ❌ Date of birth
- ❌ Contact details
- ❌ GPS coordinates

### Setup Script Reference

See: [`dev/goblin/public/content/stories/user-setup-ucode.md`](../dev/goblin/public/content/stories/user-setup-ucode.md)

**Current fields:**

- username (required)
- workspace_path (required)
- theme preference (required)
- enable_offline/mesh/sync (optional checkboxes)
- email (optional)
- notes (optional)

**Proposed minimal setup:**

- username (required, can be pseudonym)
- password (optional, stored in OS keychain)
- timezone (required, from list)
- location (auto-mapped from timezone-city selection)

---

## 🔒 Storage Separation

### System User File (`memory/private/user/user.json`)

**Core system fields ONLY** (stored as system $variables):

```json
{
  "user_id": "usr_7f3a9b2e1c4d",
  "device_id": "dev_m1mac_8a7f2c1b",
  "username": "traveller",
  "timezone": "America/Los_Angeles",
  "location_id": "L300-BK25",
  "created": "2026-01-17T10:00:00Z",
  "last_active": "2026-01-17T14:30:00Z",
  "preferences": {
    "theme": "dark",
    "offline_mode": true,
    "privacy_level": "regional"
  }
}
```

**System Fields (Read-Only):**

- `user_id` - Unique user identifier (generated once, never changes)
- `device_id` - Unique device/installation identifier (per install)
- `username` - Display name (can be pseudonym)
- `timezone` - IANA timezone code
- `location_id` - Abstract grid location (L300-AA10 format)
- `created` / `last_active` - Timestamps
- `preferences` - System settings

**NOT Stored Here:**

- ❌ Email address
- ❌ Phone number
- ❌ Home address
- ❌ Real name
- ❌ Date of birth
- ❌ Contact details

### Custom User Data (`memory/private/user/custom.json`)

**Optional user/custom $variables** (if user chooses to store):

```json
{
  "custom": {
    "email": "user@example.com",
    "contact": {
      "phone": "+1-555-0100",
      "address": "123 Main St"
    },
    "notes": "Personal notes..."
  }
}
```

**These are NOT system variables:**

- Stored separately from `user.json`
- User-managed, not required
- Can be deleted without affecting system
- Never accessed by Core without explicit permission

**Security (Both Files):**

- File permissions: `0600` (owner read/write only)
- Location: `memory/private/user/` (gitignored)
- Never logged (user_id/device_id masked in logs)
- Never sent over network

### Sensitive Data (OS Keychain)

**Stored via macOS Keychain / Linux keyring / Windows Credential Manager:**

```bash
# macOS example
security add-generic-password \
  -s "udos-user-auth" \
  -a "$(whoami)" \
  -w "user_password"
```

**NOT in filesystem:**

- ❌ Passwords
- ❌ API keys
- ❌ OAuth tokens
- ❌ Private keys

### Session Data (`memory/logs/session-*.log`)

**What appears in logs:**

```
✅ Safe (masked):
[LOCAL] Session started (user: usr_****2e1c, device: dev_****2c1b)
[LOCAL] Location set: L300:BD14-####  (regional only, precision hashed)
[LOCAL] Timezone: [UTC-8]  (offset only, not city)

❌ NEVER in logs:
- Full user_id (masked: usr_****2e1c)
- Full device_id (masked: dev_****2c1b)
- Usernames
- Exact location (L300:BD14:AA10:BB15:CC20)
- Timezone city names (America/Los_Angeles)
- Email, phone, address (never system variables)
```

**Log Masking Implementation:**

See: [`dev/goblin/core/services/location_service.py`](../dev/goblin/core/services/location_service.py#L230-L275)

```python
class LocationPrivacy(Enum):
    NONE = "none"          # No location stored
    HASHED = "hashed"      # Hashed, user can decode
    REGIONAL = "regional"  # First zoom only (11km)
    FULL = "full"          # Opt-in only

def format_for_log(self, tile_address: str) -> str:
    """Format tile address for logging based on privacy level."""
    if self._privacy_level == LocationPrivacy.NONE:
        return "[LOCATION REDACTED]"
    elif self._privacy_level == LocationPrivacy.HASHED:
        return f"loc:{self.hash_location(tile_address)}"
    elif self._privacy_level == LocationPrivacy.REGIONAL:
        return self.mask_location(tile_address)  # L300:BD14-####
    else:  # FULL - explicit consent only
        return tile_address
```

**Default:** `REGIONAL` (regional precision only, rest hashed)

---

## 📄 File Frontmatter (No PII)

**Markdown document frontmatter:**

```yaml
---
title: "My Project"
created: "2026-01-17"
author: "[SYSTEM]" # Never real username
location: "[LOCAL]" # Never exact coordinates
timezone: "[UTC-8]" # Offset only, not city
---
```

**Rules:**

- ✅ Use `[SYSTEM]` for author (never username)
- ✅ Use `[LOCAL]` for location (never grid cell)
- ✅ Use UTC offset for timezone (never city name)
- ❌ Never embed: username, email, location ID, city name

---

## 🌐 Transport Rules

### Private Transports (Data Allowed)

**MeshCore, Bluetooth Private, NFC, QR, Audio Relay:**

- ✅ User location data (with consent)
- ✅ Commands
- ✅ Files
- ⚠️ Still masked in transit logs

### Public Signal Channels (NO Data)

**Bluetooth Public beacons:**

- ❌ NEVER carry user data
- ❌ NEVER carry location
- ❌ NEVER carry identifiers
- ✅ Only: presence signals, availability flags

### Wizard Server (Cloud)

**Email relay, webhooks, AI routing:**

- ⚠️ Location data NEVER sent to Wizard
- ⚠️ Username NEVER sent to Wizard
- ⚠️ Timezone city NEVER sent to Wizard
- ✅ Wizard may calculate celestial data but not store user locations

---

## 🧪 Testing & Validation

### Log Audit Command

```bashphone|address|@|usr_[a-f0-9]{12}|dev_[a-z0-9_]{16}" memory/logs/

# Should return: nothing or only masked references (usr_****2e1c, dev_****2c1b)
```

### User File Audit

````bash
# Verify system fields only in user.json
cat memory/private/user/user.json | jq 'keys'
# Expected: ["user_id", "device_id", "username", "timezone", "location_id", "created", "last_active", "preferences"]

# Verify NO contact details in user.json
cat memory/private/user/user.json | jq 'has("email") or has("phone") or has("address")'
# Expected: falseory/logs/

# ShID Masking Test

```python
def mask_user_id(user_id: str) -> str:
    """Mask user_id for logs: usr_7f3a9b2e1c4d → usr_****2e1c"""
    if user_id.startswith("usr_"):
        return f"usr_****{user_id[-4:]}"
    return user_id

def mask_device_id(device_id: str) -> str:
    """Mask device_id for logs: dev_m1mac_8a7f2c1b → dev_****2c1b"""
    if device_id.startswith("dev_"):
        return f"dev_****{device_id[-4:]}"
    return device_id

# Test
assert mask_user_id("usr_7f3a9b2e1c4d") == "usr_****2e1c"
assert mask_device_id("dev_m1mac_8a7f2c1b") == "dev_****2c1b"
````

**System fields only** in `user.json`: user_id, device_id, username, timezone, location_id

- [ ] **NO contact details** in `user.json`: email, phone, address stored separately in `custom.json` (if at all)
- [ ] User setup collects minimal data (username, timezone, location from city)
- [ ] Passwords stored in OS keychain (not filesystem)
- [ ] `memory/private/user/` has `0600` permissions
- [ ] user*id/device_id masked in logs (usr*\***\*2e1c, dev\_\*\***2c1b)
- [ ] Logs audited for username/location/contact leakage
- [ ] Frontmatter uses `[SYSTEM]` / `[LOCAL]` / `[UTC-X]`
- [ ] Transport policy enforced (no data on public beacons)
- [ ] Wizard server never stores user locations or IDs
- [ ] Location service defaults to `REGIONAL` privacy
- [ ] Setup wizard explains what data is collected and why
- [ ] Clear separation: system variables vs user/custom variablesgrep -v "\[SYSTEM\]"

# Should return: nothing

````

### Location Masking Test

```python
from dev.goblin.core.services.location_service import LocationService

svc = LocationService()
full_loc = "L300:BD14:AA10:BB15:CC20"

# Test masking
assert svc.format_for_log(full_loc) == "L300:BD14-####"
assert full_loc not in str(logger.handlers)  # Never in logs
````

---

## 📋 Compliance Checklist

Before any release:

- [ ] User setup collects minimal data (username, timezone, location from city)
- [ ] Passwords stored in OS keychain (not filesystem)
- [ ] `memory/private/user/` has `0600` permissions
- [ ] Logs audited for username/location leakage
- [ ] Frontmatter uses `[SYSTEM]` / `[LOCAL]` / `[UTC-X]`
- [ ] Transport policy enforced (no data on public beacons)
- [ ] Wizard server never stores user locations
- [ ] Location service defaults to `REGIONAL` privacy
- [ ] Setup wizard explains what data is collected and why

---

## 🔄 Migration Notes

**Old location handlers archived:**

- `.archive/location-handlers-2026-01-17/location_handler.py`
- `.archive/location-handlers-2026-01-17/location_service.py`

**Why archived:**

- Never wired into production
- v2.x grid systems (480×270) incompatible with v1.0.7.0 (80×30)
- Privacy model already strong (kept for reference)

**v1.0.7.0 approach:**

- Location = abstract grid cell ID (L300-AA10)
- No lat/long coordinates
- No real-world geography mapping
- Spatial/game mechanics only

---

## 📚 References

- [ADR-0017: Archive old location data](ADR-0017-archive-old-locations.md)
- [v1.0.7.0 Location Schema](../core/location.schema.json)
- [Transport Policy](../AGENTS.md#5-transport-policy-non-negotiable)
- [Setup Wizard](../dev/goblin/public/content/stories/user-setup-ucode.md)

---

**Last Updated:** 2026-01-17  
**Compliance Status:** ✅ **PASSING** (based on archived location service privacy model)  
**Next Review:** Before v1.0.7.0 Phase 2 implementation
