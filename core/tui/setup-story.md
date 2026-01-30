---
title: uDOS Core Setup
format: story
version: 1.3.0
author: uDOS Engineering
tags: [setup, interactive, core]
description: "Core identity setup for .env file. Extended settings via Wizard."
---

# Core Setup

Quick setup: 5 essential fields for your local .env file.

**Extended settings** (API keys, cloud services, etc.) are configured later via Wizard.

---

## Identity (5 fields)

```form
name: user_username
label: Username
type: text
required: true
placeholder: "e.g. Ghost"
help: "3-32 characters. Letters, numbers, underscore, hyphen only."
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
help: "Your access level"
default: user
```

```form
name: user_location
label: Location
type: text
required: true
placeholder: "e.g. Sydney, New York, Tokyo"
help: "City or region. Used for timezone detection."
minlength: 2
```

```form
name: user_timezone
label: Timezone
type: text
required: true
placeholder: "AEST, EST, Asia/Tokyo, or blank for auto"
help: "IANA timezone or alias. Leave blank to auto-detect from system."
allow_aliases: true
default: [system_timezone]
```

---

## Complete

✅ **Core identity saved to .env!**

Your local setup is complete. These values are stored in:
- `.env` file (local Core boundary - 5 fields)

**Next:**
- **SETUP --profile** → View your settings
- **WIZARD start** → Configure extended settings (API keys, cloud services, etc.)
- **HELP** → See all commands

---
