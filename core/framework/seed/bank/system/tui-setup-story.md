---
title: TUI Setup
type: story
version: "1.0.0"
description: "Quick TUI setup - essential identity only"
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
---

## User Identity

Quick setup for your local identity. All values stay on this device only.

```story
name: user_username
label: Username
type: text
required: true
placeholder: "Ghost"
default: "Ghost"
help: "Username 'Ghost' forces Ghost Mode (case-insensitive exact match)."
```

```story
name: user_dob
label: Date of birth
type: date
required: true
default: "1980-01-01"
```

```story
name: user_role
label: Role
type: select
required: true
options:
  - ghost
  - user
  - admin
default: "ghost"
help: "Role 'ghost' forces Ghost Mode."
```

---

## Location & System

```story
name: system_datetime_approve
label: Confirm local date/time/zone (with approval)
type: datetime_approve
required: true
help: |
  Approve the detected date/time/timezone and view the ASCII clock. Approving keeps the values, decline to immediately edit the timezone, date, and time overrides.
```

```story
name: install_os_type
label: OS Type
type: select
required: true
options:
  - mac
  - alpine
  - ubuntu
  - windows
default: "mac"
```

```story
name: user_location_id
label: Location
type: location
timezone_field: user_timezone
required: true
help: |
  Choose your home grid/location. This selector always renders last so the approval (and optional overrides) are locked in before you confirm your grid.
```

---

## Completion Confirmation

- The TUI prints the local repo/memory/system/vault structure summary (see docs/SEED-INSTALLATION-GUIDE.md) once the story completes so you can confirm seeds, vault, and memory structure before the next training round.
