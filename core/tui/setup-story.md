---
title: uDOS Core Setup
format: story
version: 1.3.0
author: uDOS Engineering
tags: [setup, interactive, core]
description: "Core identity setup for .env file. Extended settings via Wizard and hot-reload/self-heal training per the v1.1+ roadmap."
---

# Core Setup

Quick setup: 5 essential fields for your local .env file.

**Extended settings** (API keys, cloud services, etc.) are configured later via Wizard.
Mistral API key can be provided at first run to unlock local/online AI stabilization.

This story also runs the hot reload/self-heal verification described in `v1.3.1-milestones.md` so `REPAIR`, `RESTART`, and `PLUGIN` keep logging healthy stats to `memory/logs/health-training.log` as part of the v1.1+ roadmap.

---

## Repository Root Setup

```story
name: setup_udos_root
label: Configure repository root (UDOS_ROOT)
type: text
required: true
placeholder: "/home/user/uDOS or /Users/yourname/Code/uDOS"
help: >
  Path to uDOS repository root (contains uDOS.py marker file).

  For container deployments: /home/user/uDOS (standard Docker path)
  For local development: ~/Code/uDOS or your actual repo location

  This enables proper path resolution across Core, Wizard, Goblin, and App components.
  Auto-detected from local setup, but required for container or unusual installations.
validation: path
```

---

## Identity (5 fields)

```form
name: user_username
label: Username
type: text
required: true
placeholder: "e.g. Ghost"
help: "3-32 characters. Letters, numbers, underscore, hyphen only. Username 'Ghost' forces Ghost Mode."
validation: name
minlength: 3
maxlength: 32
```

```form
name: user_dob
label: Date of birth (YYYY-MM-DD)
type: text
required: true
placeholder: "e.g. 1990-01-15"
help: "Used for age-based features. Must be at least 5 years old."
validation: date
format: "YYYY-MM-DD"
```

```form
name: user_role
label: Role
type: select
required: true
options:
  - admin: Full system access
  - user: Standard access (recommended)
  - ghost: Demo mode (limited)
help: "Your access level. Role 'ghost' forces Ghost Mode."
default: user
```
```story
name: ok_helper_install
label: Download and Install Vibe OK Helper...?
type: select
required: true
options:
  - yes: Yes (install Ollama, Vibe CLI, Mistral2 small/large, Devstral2 small)
  - no: No (skip for now)
  - skip: Skip (ask me later)
help: "Runs OK SETUP to install Ollama + Vibe CLI + recommended local models. Wizard can later add Mistral online sanity checks and quotas."
default: no
```
```story
name: mistral_api_key
label: Mistral API key (for Vibe helper)
type: text
required: false
placeholder: "sk-..."
help: "Required if you chose Yes above. Stored in Wizard secret store once admin token is generated."
```
---
---

## Location & System

```story
name: system_datetime_approve
label: Confirm local date/time/zone (with ASCII clock)
type: datetime_approve
required: true
help: >
  Approve the detected date/time/timezone while viewing the ASCII clock. Decline to adjust timezone/date/time edits immediately before continuing.
```

```story
name: udos_shell_enabled
label: Enable shell routing in TUI (UDOS_SHELL_ENABLED)
type: select
required: true
options:
  - 1: Enabled (default)
  - 0: Disabled (no shell routing)
help: "Controls whether the TUI can execute shell commands. Disable for strict command-only mode."
default: 1
```

```story
name: install_os_type
label: OS Type
type: select
required: true
options:
  - mac: macOS workstation
  - alpine: Alpine edge node
  - ubuntu: Linux server
  - windows: Windows media/gaming target
default: mac
help: "Used for optional tooling and build scripts."
```

```story
name: user_location_id
label: Location
type: location
required: true
timezone_field: user_timezone
help: >
  Choose your home grid/location (final question). The selector renders last so the approval (or overrides) are confirmed before you pick a grid.
```

---

## Training & Dev Ops

- This story writes the latest hot reload/self-heal summary to `memory/logs/health-training.log` so automation can verify the training pass before moving on.
- Completing the flow confirms the local repo/memory/system/vault structure plus the CLI dev operations (REPAIR/RESTART/PLUGIN) remain ready per the v1.1+ roadmap.
- After submission, the completion banner reprints the directories (local repo, memory, system, vault, framework seed) with status indicators and references `docs/SEED-INSTALLATION-GUIDE.md`, ensuring the “local memory/system + vault structure” is explicitly confirmed before resuming the next milestone.

## Complete

✅ **Core identity saved to .env!**

Your local setup is complete. These values are stored in:
- `.env` file (local Core boundary)
- `memory/system` (seed templates, zipped by REPAIR --seed)
- `local/memory` storage (verified via `docs/SEED-INSTALLATION-GUIDE.md`)

**Next:**
- **SETUP --profile** → View your settings
- **STORY wizard-setup** → Continue with Wizard identity & keystore
- **HELP** → See all commands

---
