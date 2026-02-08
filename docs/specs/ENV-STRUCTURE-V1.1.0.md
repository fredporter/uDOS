# .env Structure & Data Boundaries (v1.1.0, v1.3-aligned)

**Date:** 2026-01-30  
**Status:** Active (v1.3 alignment)

---

## Overview

This document defines the clear boundary between local Core identity data (stored in `.env`) and extended sensitive data (stored in Wizard keystore).

## v1.3 Alignment (Preserve v1.2 Setup Flow)

- The **v1.2 setup story flow** remains canonical in v1.3 (`core/tui/setup-story.md`).
- `SETUP` is still the single entry-point; it writes `.env` + Wizard keystore the same way as v1.2.
- `UDOS_LOCATION` is still free text, but it must resolve to coordinates in the spatial layer (see `docs/specs/SPATIAL-FILESYSTEM.md`).

## Data Boundaries

### Core .env (Local Identity Only)

The `.env` file contains **ONLY** essential local identity and system settings:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `USER_NAME` | string | Yes | Username |
| `USER_DOB` | date | Yes | Date of birth (YYYY-MM-DD) |
| `USER_ROLE` | enum | Yes | `ghost` \| `user` \| `admin` |
| `USER_PASSWORD` | string | Optional | Local password (can be blank, user/admin only) |
| `UDOS_LOCATION` | string | Yes | City name or grid coordinates (must resolve to spatial coordinates) |
| `UDOS_TIMEZONE` | string | Yes | IANA timezone (e.g., America/Los_Angeles) |
| `OS_TYPE` | enum | Yes | `alpine` \| `ubuntu` \| `mac` \| `windows` |
| `WIZARD_KEY` | uuid | Auto | Gateway to Wizard keystore (auto-generated) |

**Key Points:**
- Password is **optional** - can be blank for any role
- These values stay local and are never synced
- Works completely offline without Wizard Server

### Wizard Keystore (Extended Data)

All other sensitive data goes in the Wizard keystore:

**API Keys:**
- GitHub personal access tokens
- Anthropic API keys
- OpenAI API keys
- HubSpot API keys

**OAuth Tokens:**
- Gmail OAuth refresh tokens
- Google Calendar tokens
- Google Drive credentials

**Cloud Credentials:**
- AWS access keys
- GCP service account keys
- Azure credentials

**Integrations:**
- Webhook URLs and secrets
- OK gateway routing config
- Provider credentials
- Custom integration settings

**Installation Extended Settings:**
- Installation ID
- Lifespan mode and moves limit
- Capability flags (web proxy, ok gateway, etc.)
- Installation-level permissions

---

## Password Policy

The `USER_PASSWORD` field is **optional** and can be left blank:

- **Ghost role:** Password ignored (no local auth needed for demo/test)
- **User role:** Can set password or leave blank (protects local functions)
- **Admin role:** Can set password or leave blank (protects admin operations)

**Important:**
- Password protects **local Core functions only**
- Cloud services use Wizard keystore credentials (separate)
- Empty string or omitted = no local password required

---

## File Locations

| Data Type | Storage Location | Format |
|-----------|------------------|--------|
| Local Identity | `/uDOS/.env` | Plain text env vars |
| Wizard Key | `/uDOS/.env` | UUID (unencrypted) |
| Extended Data | `wizard/secrets.tomb` | Encrypted keystore |
| Admin Token | `memory/private/wizard_admin_token.txt` | Token file |

---

## Setup Workflows

### 1. Local Core Setup (Offline)

```bash
SETUP                    # Run interactive setup
SETUP --profile          # View current settings
nano .env                # Manual edit
```

Creates `.env` with core identity fields only.

### 2. Wizard Server Setup (Online)

```bash
python -m wizard.server --no-interactive
# Visit http://localhost:8765/dashboard
# Navigate to Settings > Integrations
```

Imports `.env` identity and adds extended settings to keystore.

### 3. DESTROY/REPAIR Operations

**DESTROY:**
- Wipes user profiles via user_manager (NOT .env)
- Can archive memory to `.archive/compost/`
- Does NOT touch `.env` identity fields
- Can clear Wizard keystore (separate operation)

**REPAIR:**
- Checks system health
- Does NOT modify `.env`
- Can reinstall dependencies
- `REPAIR --refresh-runtime` removes runtime caches (.venv, extensions, dashboard builds, human caches)
  and re-installs any enabled integrations via the Wizard `LibraryManagerService`.
- `REPAIR --install-plugin <name>` talks directly to the Wizard plugin catalog so you
  can reinstall or upgrade individual integrations with the same safety checks that power the GUI config panel.

---

## Security Model

### Local (.env)
- **Plaintext** - not encrypted
- **Local only** - never committed to git
- **Minimal PII** - only name, DOB, location
- **No credentials** - no API keys or tokens (except WIZARD_KEY which is just a UUID)

### Wizard Keystore
- **Encrypted** - secrets.tomb uses Fernet encryption
- **Unlocked by WIZARD_KEY** - from .env
- **Full credentials** - API keys, OAuth, cloud credentials
- **Access controlled** - requires admin token

---

## Commands Reference

### Core Commands

```bash
SETUP                       # Configure local identity
SETUP --profile             # Show current .env settings
SETUP --clear               # Clear .env identity data
CONFIG SHOW                 # Show all settings (local + extended)
```

### Wizard Commands

```bash
WIZARD start                # Start Wizard Server
WIZARD stop                 # Stop Wizard Server
WIZARD setup                # Run Wizard setup wizard
```

### Cleanup Commands

```bash
DESTROY 1                   # Wipe user data (not .env)
DESTROY 2                   # Archive memory
DESTROY 3                   # Wipe + archive + reload
DESTROY 4                   # NUCLEAR: Full reset (includes .env)
```

### Maintenance Commands

```bash
BACKUP [scope]              # Creates a <timestamp>-<label>.tar.gz under <scope>/.backup
RESTORE [scope] [archive]   # Extracts the .tar.gz into <scope>; use --force to overwrite
UNDO [scope]                # Re-applies the latest .tar.gz backup for <scope> (Alpine-style tar/gzip)
```

Backups, restores, and undo migrations all serialize to `.tar.gz` (tar + gzip) archives under each scope’s `.backup` folder so they follow Alpine conventions. `BACKUP` writes a manifest, `RESTORE` extracts the archive (and respects `--force`), and `UNDO` simply runs the most recent `tar.gz` again to roll back to the last checkpoint.

**Default backup targets (Wizard Repair UI):**
- `wizard-config` → `wizard/config/`
- `wizard-memory` → `memory/wizard/`
- `memory-private` → `memory/private/`
- `memory-binders` → `memory/binders/`
- `library` → `library/`

---

## Files Updated (v1.1.0)

| File | Change | Status |
|------|--------|--------|
| `.env.example` | Simplified, clarified boundaries, removed old fields | ✅ |
| `core/tui/setup-story.md` | Added optional password field | ✅ |
| `core/framework/seed/bank/system/tui-setup-story.md` | Canonical TUI setup story | ✅ |
| `core/commands/setup_handler.py` | Updated docs and password handling | ✅ |
| `core/commands/config_handler.py` | Updated to include USER_PASSWORD in setup keys | ✅ |

**Removed (v1.1.0):**
- `tui-setup-story.md` - Removed duplicate (seed is canonical)
- `wizard/templates/setup-wizard-story.md` - Removed duplicate (seed is canonical)
- `wizard/templates/setup-wizard-advanced-story.md` - Removed orphaned template
- `core/commands/tui_setup_handler.py` - Removed duplicate setup handler

---

## Testing Checklist

- [ ] `SETUP` creates .env with correct fields
- [ ] Password field is optional (can be blank)
- [ ] `SETUP --profile` shows password status (yes/blank)
- [ ] `CONFIG SHOW` displays .env correctly
- [ ] `DESTROY 1` does NOT delete .env identity
- [ ] `DESTROY 4` CAN reset .env (with confirmation)
- [ ] Wizard Server imports .env on first run
- [ ] Extended settings go to Wizard keystore

---

## References

- [.env.example](/.env.example) - Template file
- [setup_handler.py](/core/commands/setup_handler.py) - Setup command
- [config_handler.py](/core/commands/config_handler.py) - Config management
- [wizard/README.md](/wizard/README.md) - Wizard Server docs
- [AGENTS.md](/AGENTS.md) - System boundaries

---

_Last Updated: 2026-02-04_  
_Version: 1.1.0_
