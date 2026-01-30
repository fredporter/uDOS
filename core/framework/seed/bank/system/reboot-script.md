---
title: uDOS Reboot Script
type: script
version: "1.0.0"
description: "Default Core reboot script."
tags: [system, reboot, core]
---

# Reboot

This script is executed on system reboot to capture shutdown state and perform re-init.

```script
$system.status = "reboot"
$system.last_reboot = $now
```

# Notes

- Extend this script with additional reboot logic as needed.
- Use RUN to execute: RUN memory/bank/system/reboot-script.md
