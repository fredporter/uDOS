---
title: uDOS Startup Script
type: script
version: "1.0.0"
description: "Default Core startup script."
tags: [system, startup, core]
allow_stdlib_commands: true
---

# Startup

This script is executed on system startup to perform basic checks and initialization.

```script
$system.status = "startup"
$system.last_startup = $now
DRAW BLOCK ucodesmile-ascii.md
DRAW PAT TEXT "Startup ready"
```

# Notes

- Extend this script with additional startup checks as needed.
- Use RUN to execute: RUN memory/bank/system/startup-script.md
- This script now runs automatically at boot and renders a DRAW PAT banner for demo/testing confirmation.
