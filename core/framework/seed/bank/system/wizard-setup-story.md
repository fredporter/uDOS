---
title: Wizard Setup Story
type: story
version: "1.0.1"
description: "Core identity setup - captures essential .env variables only"
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
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
type: date
required: true
placeholder: "1980-01-01"
validation:
  pattern: "^\d{4}-\d{2}-\d{2}$"
  message: "Please enter date as YYYY-MM-DD"
```

```story
name: user_role
label: Role
type: select
required: true
options:
  - admin
  - user
  - ghost
display_format: dropdown
show_all_options: true
```

```story
name: user_password
label: Local Password (optional for user/admin, leave blank for ghost)
type: password
required: false
placeholder: "Leave blank for no password"
show_if:
  field: user_role
  values: [admin, user]
```

---

## Time & Place

Confirm the timezone, local time, and a uDOS grid location. The location defaults to your
timezone city and can be refined by typing a more precise place.

```story
name: user_timezone
label: Timezone (e.g. America/Los_Angeles or UTC-8)
type: select
required: true
placeholder: "(Press Enter for system timezone)"
options_endpoint: "/api/v1/setup/data/timezones"
allow_custom: true
default_from_system: true
validation:
  message: "Invalid timezone - check spelling or use system default"
```

```story
name: user_local_time
label: Local time now (YYYY-MM-DD HH:MM)
type: datetime
required: true
placeholder: "(Press Enter for current system time)"
default_from_system: true
validation:
  pattern: "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
  message: "Please enter time as YYYY-MM-DD HH:MM"
```

```story
name: user_location_id
label: Location (uDOS grid)
type: location
required: true
placeholder: "Start typing a city or press Enter for timezone default"
timezone_field: user_timezone
name_field: user_location_name
options_endpoint: "/api/v1/setup/data/locations"
searchable: true
default_from_timezone: true
allow_custom: false
```

---

## Operating System

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

---
