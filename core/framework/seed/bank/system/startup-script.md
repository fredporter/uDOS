---
title: uDOS Startup Script
type: script
version: "1.0.0"
description: "Default Core startup script."
tags: [system, startup, core]
---

# Startup

This script is executed on system startup to perform basic checks and initialization.

```script
$system.status = "startup"
$system.last_startup = $now
```

# Notes

- Extend this script with additional startup checks as needed.
- Use RUN to execute: RUN memory/bank/system/startup-script.md
