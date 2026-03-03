---
name: ucode-help
description: >
  Show the Vibe-exposed uDOS Dev Mode command reference. Lists the approved
  contributor `ucode` subset with descriptions and usage examples.
allowed-tools: ucode_health
user-invocable: true
---

# ucode-help

You are helping the user understand the uDOS Dev Mode commands available in this Vibe session.

## What to do

1. Use the `ucode_health` tool to confirm uDOS is reachable and healthy.
2. Present the following command groups clearly. Make it explicit that this is
the Vibe contributor subset, not the full operator command surface.

### Health and Repair
| Command | Description |
|---------|-------------|
| `ucode_health` | Full system health report |
| `ucode_verify` | Verify installation integrity |
| `ucode_repair` | Self-heal dependencies and config |
| `ucode_token` | Manage API access tokens |
| `ucode_help` | Show the Dev Mode command subset and usage guidance |

### Contributor Setup and State
| Command | Description |
|---------|-------------|
| `ucode_seed` | Install or reset framework seed data |
| `ucode_config` | Read or write configuration values |
| `ucode_setup` | Run setup validation and contributor bootstrap flows |

### Repo and Asset Operations
| Command | Description |
|---------|-------------|
| `ucode_run` | Execute contributor scripts and repo maintenance tasks |
| `ucode_read` | Inspect repo files, docs, and development assets |

3. If the user asks about commands outside this subset, direct them to the TUI
operator docs instead of implying they are callable through Vibe.
4. Ask if the user wants to dive into any specific command or group.
