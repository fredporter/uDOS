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
```

---

## Location & System

```story
name: system_datetime_approve
label: Confirm local date/time/zone
type: datetime_approve
required: true
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
```

---
