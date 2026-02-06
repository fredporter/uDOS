---
title: Wizard Setup Story
type: story
version: "1.0.0"
description: "Securely capture user and installation setup variables for Wizard."
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: true
---

## User Identity

We will capture the core user profile data for this installation. These values are stored
securely in the Wizard keystore and never shared across installations.

```story
name: user_username
label: Username (no spaces or special characters)
type: text
required: true
placeholder: "Ghost"
```

```story
name: user_dob
label: Date of birth (YYYY-MM-DD)
type: text
required: true
placeholder: "1980-01-01"
```

```story
name: user_role
label: Role
type: select
required: true
options:
  - admin
  - user
  - ghost *default/test-user
```

---

## Time & Place

Confirm the timezone, local time, and a uDOS grid location. The location defaults to your
timezone city and can be refined by typing a more precise place.

```story
name: user_timezone
label: Timezone (e.g. America/Los_Angeles or UTC-8)
type: text
required: true
placeholder: "America/Los_Angeles"
```

```story
name: user_local_time
label: Local time now (YYYY-MM-DD HH:MM)
type: text
required: true
placeholder: "2026-01-26 13:45"
```

```story
name: user_location_id
label: Location (uDOS grid)
type: location
required: true
placeholder: "Start typing a city..."
timezone_field: user_timezone
name_field: user_location_name
```

---

## Installation

Installation variables are scoped to this device only and stored securely. Lifespan is
tracked by move-count; if set to moves, the Wizard Dashboard will show progress toward EOL.

```story
name: install_id
label: Installation ID (leave blank to auto-generate)
type: text
required: false
placeholder: "auto"
```

```story
name: install_os_type
label: OS Type
type: select
required: true
options:
  - alpine
  - ubuntu
  - mac
  - windows
```

```story
name: install_lifespan_mode
label: Lifespan mode
type: select
required: true
options:
  - infinite *default = 0
  - moves * = number of moves lifespan
```

```story
name: install_moves_limit
label: Moves limit (required if lifespan is moves)
type: number
required: false
placeholder: "1000" ** not required
```

---

## Capabilities & Permissions

Toggle installation-level capabilities. These map to Wizard config settings.

```story
name: install_permissions
label: Installation permissions (optional)
type: textarea
required: false
placeholder: "Notes or policies for this installation"
```

```story
name: capability_web_proxy
label: Allow web proxy (APIs + scraping)
type: checkbox
```

```story
name: capability_gmail_relay
label: Allow Gmail relay
type: checkbox
```

```story
name: capability_ai_gateway
label: Allow AI gateway routing
type: checkbox
```

```story
name: capability_github_push
label: Allow GitHub push
type: checkbox
```

```story
name: capability_notion
label: Allow Notion integration
type: checkbox
```

```story
name: capability_hubspot
label: Allow HubSpot integration
type: checkbox
```

```story
name: capability_icloud
label: Allow iCloud integration
type: checkbox
```

```story
name: capability_plugin_repo
label: Allow plugin repository
type: checkbox
```

```story
name: capability_plugin_auto_update
label: Allow plugin auto-update
type: checkbox
```

---
