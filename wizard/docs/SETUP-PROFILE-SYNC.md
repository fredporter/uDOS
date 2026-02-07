# Setup Profile Synchronization

**Version:** 1.0.0
**Date:** 2026-01-28
**Status:** Active

---

## Overview

The TUI setup story (`memory/story/wizard-setup-story.md`) collects user and installation details during first-time setup. These values are stored securely in the Wizard secret store and can be accessed via API endpoints or the interactive console.

---

## Data Flow

```
TUI Setup Story
     ↓
[User answers questions]
     ↓
POST /api/setup/story/submit
     ↓
Secret Store (encrypted)
     ├─ wizard-user-profile
     └─ wizard-install-profile
     ↓
[Sync to Wizard config]
     └─ wizard/config/wizard.json (capabilities only)
     ↓
[Display in Console/Dashboard]
     └─ GET /api/setup/profile/combined
```

---

## Stored Profiles

### User Profile

Stored in secret store with key: `wizard-user-profile`

```json
{
  "username": "fred",
  "date_of_birth": "1980-01-15",
  "role": "admin",
  "timezone": "America/Los_Angeles",
  "local_time": "2026-01-28 10:30",
  "location_id": "L001-usa-sanfrancisco",
  "location_name": "San Francisco",
  "permissions": null,
  "created_at": "2026-01-28T10:30:00",
  "updated_at": "2026-01-28T10:30:00"
}
```

### Installation Profile

Stored in secret store with key: `wizard-install-profile`

```json
{
  "installation_id": "udos-a1b2c3d4e5f6g7h8",
  "os_type": "macos",
  "lifespan_mode": "infinite",
  "moves_limit": null,
  "permissions": null,
  "capabilities": {
    "web_proxy": true,
    "gmail_relay": true,
    "ok_gateway": true,
    "github_push": false,
    "hubspot": false,
    "icloud": false,
    "plugin_repo": true,
    "plugin_auto_update": false
  },
  "created_at": "2026-01-28T10:30:00",
  "updated_at": "2026-01-28T10:30:00"
}
```

### Installation Metrics

Stored in filesystem: `memory/wizard/installation-metrics.json`

```json
{
  "moves_used": 0,
  "moves_limit": null,
  "lifespan_mode": "infinite",
  "created_at": "2026-01-28T10:30:00",
  "last_move_at": null
}
```

---

## API Endpoints

### GET /api/setup/profile/user

Retrieve user profile.

**Response:**

```json
{
  "status": "success",
  "profile": {
    /* user profile */
  }
}
```

### GET /api/setup/profile/install

Retrieve installation profile and metrics.

**Response:**

```json
{
  "status": "success",
  "profile": {
    /* install profile */
  },
  "metrics": {
    /* installation metrics */
  }
}
```

### GET /api/setup/profile/combined

Retrieve all profiles in a single call.

**Response:**

```json
{
  "status": "success",
  "user_profile": {
    /* user profile */
  },
  "install_profile": {
    /* install profile */
  },
  "install_metrics": {
    /* metrics */
  },
  "setup_complete": true
}
```

---

## Interactive Console Command

### `setup`

Display the complete setup profile in the Wizard Server console.

**Usage:**

```bash
wizard> setup
```

**Output:**

```
🧙 SETUP PROFILE:

  User Identity:
    • Username: fred
    • Role: admin
    • Timezone: America/Los_Angeles
    • Location: San Francisco (L001-usa-sanfrancisco)

  Installation:
    • ID: udos-a1b2c3d4e5f6g7h8
    • OS Type: macos
    • Lifespan Mode: infinite

  Capabilities:
    ✅ Web Proxy
    ✅ Gmail Relay
    ✅ Ai Gateway
    ❌ GitHub Push
    ❌ Hubspot
    ❌ Icloud
    ✅ Plugin Repo
    ❌ Plugin Auto Update

  Metrics:
    • Moves Used: 0
```

---

## Wizard Config Sync

When the setup story is submitted, capabilities are automatically synced to `wizard/config/wizard.json`:

**Capability Mapping:**

- `web_proxy` → `web_proxy_enabled`
- `gmail_relay` → `gmail_relay_enabled`
- `ok_gateway` → `ok_gateway_enabled`
- `github_push` → `github_push_enabled`
- `hubspot` → `hubspot_enabled`
- `icloud` → `icloud_enabled`
- `plugin_repo` → `plugin_repo_enabled`
- `plugin_auto_update` → `plugin_auto_update`

This ensures Wizard Server services reflect user preferences from the TUI story.

---

## Security

- **User profile** is stored encrypted in the secret store (requires `WIZARD_KEY` env var)
- **Installation profile** is stored encrypted in the secret store
- **Metrics** are stored in plaintext filesystem (non-sensitive data)
- Profiles are only accessible via authenticated API endpoints or localhost console

---

## Development

### Testing Profile Retrieval

```bash
# Via curl (requires admin token)
curl -H "Authorization: Bearer $(cat memory/private/wizard_admin_token.txt)" \
  http://localhost:8765/api/setup/profile/combined

# Via interactive console
./bin/start_wizard.sh
wizard> setup
```

### Updating Profiles

Profiles can only be updated by re-submitting the setup story or manually editing the secret store (not recommended).

---

## References

- [wizard/routes/setup_routes.py](../routes/setup_routes.py) — API endpoints
- [wizard/services/setup_profiles.py](../services/setup_profiles.py) — Profile storage
- [wizard/services/interactive_console.py](../services/interactive_console.py) — Console command
- [memory/story/wizard-setup-story.md](../../memory/story/wizard-setup-story.md) — TUI story

---

**Status:** Active Documentation
**Maintained by:** Wizard Engineering
**Next Review:** 2026-02-28
