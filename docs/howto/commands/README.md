# uDOS Command Reference

> **Version:** Core v1.1.0.0 | **Updated:** 2026-01-10

uDOS commands follow a consistent `MODULE SUBCOMMAND [params] [--flags]` pattern.

---

## Command Categories

### 🗺️ Navigation & Files

| Command | Purpose | Example |
|---------|---------|---------|
| [TILE](navigation.md#tile) | Navigate content tiles | `TILE 100` |
| [FILE](navigation.md#file) | File operations | `FILE LIST memory/` |
| [EDIT](navigation.md#edit) | Edit files | `EDIT readme.md` |
| [SEARCH](navigation.md#search) | Search content | `SEARCH water` |
| [HELP](navigation.md#help) | Get help | `HELP TILE` |

### 📚 Content & Knowledge

| Command | Purpose | Example |
|---------|---------|---------|
| [GUIDE](content.md#guide) | Knowledge system | `GUIDE AI LIST` |
| [BUNDLE](content.md#bundle) | Content packages | `BUNDLE START fire-101` |
| [CAPTURE](content.md#capture) | Web capture | `CAPTURE https://...` |

### 🎨 Interface

| Command | Purpose | Example |
|---------|---------|---------|
| [COLOR](interface.md#color) | Color themes | `COLOR rainbow` |
| [PALETTE](interface.md#palette) | Palette editor | `PALETTE SHOW retro` |
| [MODE](interface.md#mode) | Prompt modes | `MODE GHOST` |
| [SOUND](interface.md#sound) | System sounds | `SOUND success` |

### 🔧 System

| Command | Purpose | Example |
|---------|---------|---------|
| [SYSTEM](system.md#system) | System management | `SYSTEM STATUS` |
| [DEV](system.md#dev) | Dev mode | `DEV MODE ON` |
| [STACK](system.md#stack) | Capability install | `STACK ADD meshcore` |
| [INSTALL](system.md#install) | TCZ packages | `INSTALL nano` |
| [BUILD](system.md#build) | Create images | `BUILD ISO` |

### 🧙 Wizard Server (Realm B)

| Command | Purpose | Example |
|---------|---------|---------|
| [OK](howto/commands/wizard.md#ok) | AI assistant | `OK MAKE SEQUENCE "..."` |
| [QUOTA](howto/commands/wizard.md#quota) | API quotas | `QUOTA STATUS` |
| [AI](howto/commands/wizard.md#ai) | AI testing | `AI TEST mistral` |
| [GMAIL](howto/commands/wizard.md#gmail) | Gmail relay | `GMAIL LIST` |

### 📡 Transport & Mesh

| Command | Purpose | Example |
|---------|---------|---------|
| [NETWORK](transport.md#network) | Network management | `NETWORK STATUS` |
| [MESH](transport.md#mesh) | MeshCore P2P | `MESH PEERS` |
| [PAIR](transport.md#pair) | Device pairing | `PAIR CONSOLE` |
| [TRANSPORT](transport.md#transport) | Low-level transport | `TRANSPORT AUDIO ON` |

### 👤 User & Wellbeing

| Command | Purpose | Example |
|---------|---------|---------|
| [WELLBEING](user.md#wellbeing) | Energy tracking | `WELLBEING STATUS` |
| [LOCATION](user.md#location) | Privacy-first location | `LOCATION SKY` |

### 🛠️ Maintenance

| Command | Purpose | Example |
|---------|---------|---------|
| [TIDY](maintenance.md#tidy) | Organize files | `TIDY workspace` |
| [CLEAN](maintenance.md#clean) | Delete old files | `CLEAN --archives` |
| [UNDO](maintenance.md#undo) | Version history | `UNDO` |
| [BACKUP](maintenance.md#backup) | Create backup | `BACKUP file.py` |
| [ARCHIVE](maintenance.md#archive) | Manage archives | `ARCHIVE LIST` |

---

## Command Syntax

### Standard Format

```
MODULE SUBCOMMAND [required] [optional] [--flag] [--key=value]
```

### uCODE Format

Commands can also be expressed as uCODE tiles:

```
[MODULE|SUBCOMMAND*PARAM1*PARAM2]
```

### Examples

```bash
# Standard
TILE 100
FILE LIST memory/ucode/
GUIDE AI SHOW fix-errors

# uCODE equivalent
[TILE|100]
[FILE|LIST*memory/ucode/]
[GUIDE|AI*SHOW*fix-errors]
```

---

## Getting Help

```bash
# General help
HELP

# Command-specific help
HELP TILE
HELP BUNDLE

# Interactive guide
GUIDE
```

---

## Quick Reference

### Most Used Commands

```bash
TILE 100               # Go to tile 100
FILE EDIT readme.md    # Edit file
GUIDE                  # Browse knowledge
OK ASK "how do I..."   # Ask AI
SYSTEM STATUS          # Check system
```

### Dev Mode Commands

```bash
DEV MODE ON            # Enter dev mode
DEV MODE OFF           # Exit dev mode
DEV BREAK              # Set breakpoint
DEV STEP               # Step through code
```

---

*See individual category pages for detailed command documentation.*
