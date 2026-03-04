# How to Use Vibe Skills in uDOS-Vibe

Vibe in the Dev extension lane exposes a small contributor-facing `ucode` subset. It is not the full uDOS operator command surface.

You have **4 uDOS skills** available in this lane:

## 1. **ucode-help** — Documentation & Command Lookup
```
Type in Vibe:
/ucode-help COMMAND_NAME

Examples:
/ucode-help health     → Learn about the health check command
/ucode-help setup      → How to initialize the environment
/ucode-help repair     → Fix broken configurations
```

## 2. **ucode-setup** — Interactive First-Run Wizard
```
/ucode-setup

This will:
- Ask for your username
- Set your timezone
- Configure location
- Initialize vault structure
```

## 3. **ucode-dev** — Developer Mode & Debugging
```
/ucode-dev

Shows:
- Available tools
- Skill status
- Configuration details
- System diagnostics
- Recent log and health guidance
```

---

## How to Invoke Tools Directly

If you want tools (not skills), use natural language prompts like:

```
"Check the system health"
→ Will use ucode_health tool

"Run the backup script"
→ Will use ucode_run tool

"Help me set up"
→ Will use ucode_setup tool
```

---

## Troubleshooting

### Tools Not Showing Up?
1. Make sure the wizard MCP server is running:
   ```bash
   uv run --project . wizard/mcp/mcp_server.py --tools
   ```

2. Then run vibe:
   ```bash
   vibe trust && vibe
   ```

   Only do this inside the active Dev Mode contributor lane. Standard users should stay on `ucode`.

### Skills Asking for Input?
Just type what they ask for. Skills are interactive and guide you through workflows.

### Want to See All Available Tools?
Ask Vibe:
```
"What tools are available?"
```

Expect the contributor subset only, not the full TUI command inventory.

---

## Quick Start Guide

### Option A: Use Skills (Recommended for First Time)
```bash
vibe trust && vibe
# Then type: /ucode-help

# Or try the setup:
# Type: /ucode-setup
```

Use this only when the `dev` profile and the `@dev` workspace lane at `/dev` are active.

### Option B: Use Tools via Natural Language
```bash
vibe trust && vibe
# Then ask: "Check my system health"
# Or: "List available commands"
```

### Option C: Use Raw Commands (Advanced)
```bash
vibe trust && vibe
# Ask: "Run ucode_health with check='system'"
# Or: "Call ucode_run with script='backup'"
```

---

## What Tools Are Available?

You have 10 Vibe-exposed uDOS tools in the Dev extension lane:

### Health and Repair (5)
- Health checks, verification, repair, tokens, command help

### Setup and State (3)
- Seed, config, setup

### Repo and Asset Operations (2)
- Run, read

For binder, story, spatial, gameplay, media, and destructive commands, use the full uDOS TUI instead of Vibe.

---

## Next Steps

1. **Try a skill first:**
   ```
   /ucode-help
   ```

2. **Ask for system status:**
   ```
   "Check my health"
   ```

3. **Set up your environment:**
   ```
   /ucode-setup
   ```

4. **Use the full TUI for story/operator workflows:**
   ```
   ucode
   ```
