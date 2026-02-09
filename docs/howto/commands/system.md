# System Commands

> **Version:** Core v1.1.0.0

Commands for system management, development, and installation.

---

## SYSTEM

Core system management and status.

### Syntax

```bash
SYSTEM [subcommand] [args]
```

### Subcommands

| Command    | Description                  |
| ---------- | ---------------------------- |
| `STATUS`   | Show system status (default) |
| `INFO`     | Detailed system information  |
| `REBOOT`   | Restart uDOS                 |
| `SHUTDOWN` | Exit uDOS                    |
| `CONFIG`   | View/edit configuration      |
| `REPAIR`   | Run diagnostics              |

### Examples

```bash
SYSTEM
SYSTEM STATUS
SYSTEM INFO
SYSTEM CONFIG theme
SYSTEM REPAIR
```

---

## DEV

Development mode and script debugging.

### Syntax

```bash
DEV MODE [ON|OFF|STATUS|HELP]
DEV [ENABLE|BREAK|STEP|CONTINUE|VARS]
```

### Dev Mode

Enable Wizard Server capabilities on dev machine:

```bash
DEV MODE ON           # Enable wizard features
DEV MODE OFF          # Return to offline mode
DEV MODE STATUS       # Check current state
```

### Script Debugging

```bash
DEV ENABLE            # Enable script debugging
DEV BREAK <line>      # Set breakpoint
DEV STEP              # Step through code
DEV CONTINUE          # Continue to next breakpoint
DEV VARS              # Show variables
```

### Notes

- Dev Mode enables AI commands, web access, Gmail relay
- Script debugging works with TypeScript in `.md` files
- See [Wizard Server](../wizard/README.md) for Dev Mode details

---

## STACK

Capability-based installation for common workflows.

### Syntax

```bash
STACK [ADD|REMOVE|LIST|STATUS] [capability]
```

### Available Stacks

| Stack      | Packages              | Description         |
| ---------- | --------------------- | ------------------- |
| `meshcore` | meshtastic, bluetooth | P2P mesh networking |
| `audio`    | pygame, portaudio     | Groovebox audio     |
| `wizard`   | openssl, curl         | Wizard server deps  |
| `dev`      | git, gcc              | Development tools   |
| `graphics` | pillow, svgwrite      | Image generation    |

### Examples

```bash
STACK LIST            # Show available stacks
STACK STATUS          # Show installed stacks
STACK ADD meshcore    # Install meshcore capability
STACK REMOVE audio    # Remove audio capability
```

---

## INSTALL

Plugin/package management for Alpine Linux.

### Syntax

```bash
INSTALL [package] [--options]
INSTALL LIST
INSTALL SEARCH <query>
INSTALL REMOVE <package>
```

### Examples

```bash
INSTALL nano          # Install nano editor
INSTALL python3.11-pip
INSTALL LIST          # List installed packages
INSTALL SEARCH editor # Search for packages
INSTALL REMOVE nano   # Remove package
```

### Notes

- Alpine-specific (apk or plugin bundles)
- Requires internet for download
- Packages persist across reboots with proper setup

---

## BUILD

Create offline installation packages and images.

### Syntax

```bash
BUILD [OFFLINE|ISO|USB] [options]
```

### Subcommands

| Command        | Description              |
| -------------- | ------------------------ |
| `OFFLINE`      | Create portable archive  |
| `ISO`          | Build bootable ISO image |
| `USB <device>` | Create bootable USB      |

### Examples

```bash
BUILD OFFLINE         # Create udos-offline.tar.gz
BUILD ISO             # Create udos-alpine.iso
BUILD USB /dev/sdb    # Write to USB drive
```

### Output

```
distribution/
├── udos-offline-v1.0.0.64.tar.gz
├── udos-alpine.iso
└── checksums.txt
```

---

## REPAIR

System diagnostics and repair utilities.

### Syntax

```bash
REPAIR [component]
```

### Components

| Component   | Description             |
| ----------- | ----------------------- |
| (none)      | Full system check       |
| `config`    | Reset configuration     |
| `handlers`  | Verify command handlers |
| `knowledge` | Rebuild knowledge index |
| `cache`     | Clear all caches        |

### Examples

```bash
REPAIR                # Full diagnostics
REPAIR config         # Reset to defaults
REPAIR handlers       # Check handler registration
REPAIR knowledge      # Rebuild search index
```

---

## GET / SET

Configuration field access.

### Syntax

```bash
GET [field.path]
SET <field.path> <value>
```

### Examples

```bash
GET                   # Interactive config browser
GET tui.theme         # Get specific value
SET tui.theme dark    # Set value
SET tui.rainbow_splash false
```

### Common Fields

| Field                | Description         |
| -------------------- | ------------------- |
| `tui.theme`          | Color theme         |
| `tui.width`          | Grid width          |
| `tui.rainbow_splash` | Splash animation    |
| `wizard.provider`    | Default AI provider |

---

## Related

- [Wizard Server](../wizard/README.md) - Dev Mode details
- [TinyCore](../tinycore/README.md) - Distribution
- [Maintenance](maintenance.md) - TIDY, CLEAN, BACKUP

---

_Part of the [Command Reference](README.md)_
