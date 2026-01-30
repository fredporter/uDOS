---
title: uDOS Setup
format: story
version: 1.2.0
author: uDOS Engineering
tags: [setup, interactive, core]
description: "Set up your uDOS identity (6 essential fields only). Saves to .env and syncs to Wizard."
---

# Welcome to uDOS

Let's set up your identity. Just 6 essential questions.

---

## Your Identity (4 fields)

```form
name: user_username
label: Username
type: text
required: true
placeholder: "e.g. Ghost"
help: "3-32 characters. Letters, numbers, underscore, hyphen only. Cannot be reserved names."
validation: name
minlength: 3
maxlength: 32
pattern: "^[a-zA-Z0-9_-]+$"
```

```form
name: user_dob
label: Date of birth (YYYY-MM-DD)
type: text
required: true
placeholder: "e.g. 1990-01-15"
help: "Used for age-appropriate features and starsign calculation. Must be at least 5 years old."
validation: date
format: "YYYY-MM-DD"
min_age: 5
max_age: 150
```

```form
name: user_role
label: Your role
type: select
required: true
options:
  - admin: Full access to all features and settings
  - user: Standard user with most features available
  - ghost: Demo/test mode with limited access (default)
help: "Choose your access level"
default: user
```

```form
name: user_password
label: Local password (optional)
type: password
required: false
placeholder: "Leave blank for no password"
help: "Min 8 chars: 1 uppercase, 1 lowercase, 1 number (e.g., MyPass123). Protects local Core only."
show_if:
  field: user_role
  values: [admin, user]
minlength: 8
pattern: "^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])"
```

---

## Location & System (2 fields)

```form
name: user_location
label: Your location
type: text
required: true
placeholder: "Start typing a city (e.g. Sydney, New York, Tokyo)"
help: "City name or region. Type to autocomplete from location database."
searchable: true
search_endpoint: "local:location_service"
default_from_timezone: true
minlength: 2
maxlength: 100
```

```form
name: user_timezone
label: Your timezone
type: text
required: true
placeholder: "AEST, EST, Asia/Tokyo, or leave blank for system default"
help: "Type timezone alias (AEST, EST, PST) or IANA zone. Tab to accept suggestion, or leave blank for system timezone."
fuzzy_match: true
allow_aliases: true
autocomplete: true
suggestions_from: [AEST, AEDT, EST, PST, GMT, UTC, CET, JST, IST]
default: [system_timezone]
```

---

## OS Type (1 field)

```form
name: install_os_type
label: Operating system
type: select
required: true
options:
  - alpine: Alpine Linux (lightweight, minimal)
  - ubuntu: Ubuntu Linux (standard, full-featured)
  - mac: macOS (Apple)
  - windows: Windows
help: "This device's operating system. Will be auto-detected if unsure."
suggested_from: system_detection
```

---

## Confirmation

Your identity will be saved to .env and synced to Wizard:

- **Username:** [user_username]
- **DOB:** [user_dob] ([_age] years old)
- **🔐 UDOS Crypt:** [_crypt_id] ([_starsign], [_generation])
- **Role:** [user_role]
- **Location:** [user_location]
- **Timezone:** [user_timezone]
- **OS:** [install_os_type]

```form
name: confirm
label: Save and continue
type: checkbox
required: true
help: "Confirm to complete setup"
```

---

## Complete

✅ Setup saved to .env!

Next steps:
- **SETUP --profile** — View your profile
- **CONFIG** — Manage extended settings in Wizard
- **STATUS** — View system status

---
