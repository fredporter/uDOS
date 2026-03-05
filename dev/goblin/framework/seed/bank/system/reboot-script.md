---
title: uDOS Reboot Script
type: script
version: "1.0.0"
description: "Default Core reboot script."
tags: [system, reboot, core]
allow_stdlib_commands: true
---

# Reboot

This script is executed on system reboot to capture shutdown state and perform re-init.

```script
$system.status = "reboot"
$system.last_reboot = $now
DRAW PAT TEXT "Reboot ready"
```

# Notes

- Extend this script with additional reboot logic as needed.
- Use RUN to execute: RUN memory/bank/system/reboot-script.md
- Auto-run ensures this script fires on every reboot and renders a DRAW PAT banner for testing visibility.
