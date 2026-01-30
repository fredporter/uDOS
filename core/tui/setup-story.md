---
title: uDOS Setup
format: story
version: 1.0.0
author: uDOS Engineering
tags: [setup, interactive, core]
description: "Set up your uDOS identity and basic preferences. This runs entirely in the TUI."
---

# Welcome to uDOS

Let's set up your identity and basic preferences. This only takes a moment.

---

## Your Identity

```form
name: user_real_name
label: Your name
type: text
required: true
placeholder: "e.g. Alice, Bob, Maria"
help: "Cannot be blank or reserved names"
validation: name
```

```form
name: user_dob
label: Date of birth (YYYY-MM-DD)
type: text
required: true
placeholder: "e.g. 1990-01-15"
help: "For age-appropriate features"
validation: date
```

```form
name: user_role
label: Your role
type: select
required: true
options:
  - admin
  - user
  - ghost
help: "admin=full access, user=standard, ghost=demo/test"
default: user
```

---

## Location & Time

```form
name: user_timezone
label: Your timezone
type: text
required: true
placeholder: "e.g. America/New_York"
help: "Leave blank to use system timezone"
default: [system_timezone]
```

```form
name: user_location
label: Your location
type: text
required: true
placeholder: "e.g. New York, NYC, Home"
help: "City or grid location"
validation: text
```

```form
name: user_time_confirmed
label: Current time looks correct
type: checkbox
required: true
default: true
help: "System time: [system_time]"
```

---

## Confirmation

Your setup is ready! Here's what we'll save:

- **Name:** [user_real_name]
- **DOB:** [user_dob]
- **Role:** [user_role]
- **Timezone:** [user_timezone]
- **Location:** [user_location]

```form
name: confirm
label: Save and continue
type: checkbox
required: true
help: "Confirm to complete setup"
```

---

## Complete

✅ Setup saved! You're ready to go.

Next steps:
- **STATUS** — View system status
- **HELP** — See available commands
- **MAP** — Explore the world

---
