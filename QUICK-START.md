# Quick Start: uDOS v1.5 Rebaseline

`ucode` is now the standard runtime entry point. Use `vibe` only when Dev Mode is explicitly enabled.

## 📦 Installation

### First Time Setup

**macOS (easiest):**
1. Double-click `bin/install-udos-vibe.command` in Finder
2. Follow the prompts

**macOS/Linux (terminal):**
```bash
cd /path/to/uDOS-vibe
./bin/install-udos-vibe.sh
```

The installer will:
- ✓ Detect your OS and hardware
- ✓ Install uv (Python package manager)
- ✓ Set up your `.env` configuration
- ✓ Install Dev Mode tooling only when the `dev` profile is selected
- ✓ Optionally install micro editor, Obsidian, and Ollama
- ✓ Create vault structure and symlinks

**Installation options:**
```bash
./bin/install-udos-vibe.sh           # Full install (core + wizard)
./bin/install-udos-vibe.sh --core    # Core only (minimal)
./bin/install-udos-vibe.sh --wizard  # Add wizard to existing
./bin/install-udos-vibe.sh --update  # Update existing install
```

📚 **Detailed installation guide**: [docs/INSTALLATION.md](docs/INSTALLATION.md)

---

## 🚀 Start ucode

After installation:
```bash
cd /path/to/uDOS
./bin/ucode
```

First time? Run the setup story:
```
SETUP
```

Then inspect the supported release lanes:
```
UCODE PROFILE LIST
UCODE OPERATOR STATUS
```

---

## 🎯 What You Can Do Right Now

### 1️⃣ **Check System Health**
In Vibe chat, type:
```
Check the system health
```

Or use the skills:
```
/ucode-help health
```

### 2️⃣ **Get Help with Commands**
```
What commands are available?
```

Or use the help skill directly:
```
/ucode-help
```

### 3️⃣ **Set Up Your Environment**
```
/ucode-setup
```

This will ask you for:
- Username
- Timezone
- Location
- And initialize your vault

### 4️⃣ **Run a Script**
```
Run the backup script
```

Or ask:
```
Execute my custom script
```

### 5️⃣ **Read Files from Vault**
```
Read the mission notes
```

Or:
```
Show me the content from vault
```

### 6️⃣ **See Your Status**
```
What's the current system status?
```

---

## 📚 Available Slash Commands (Skills)

Use these like `/help` in chat:

```
/ucode-help        → Get documentation
/ucode-setup       → Run interactive setup
/ucode-story       → Read narrative content
/ucode-dev         → Developer tools & info
/ucode-logs        → View system logs
```

---

## 🔧 Available Tools (42 Total)

### Core System Commands
- **health** — `Check the system health`
- **verify** — `Verify everything is installed correctly`
- **repair** — `Fix any broken configurations`
- **setup** — `Run the setup wizard`
- **help** — `Get documentation`
- **config** — `Manage configuration`

### File & Data Commands
- **read** — `Read a file` / `Show me the vault content`
- **save** — `Save to vault`
- **load** — `Load from vault`
- **find** — `Search for something`
- **import** — `Import data`
- **export** — `Export data`

### Script & Automation Commands
- **run** — `Execute a script`
- **script** — `Manage scripts`
- **scheduler** — `Schedule tasks`
- **watch** — `Monitor a file or process`

### Creative & Expression Commands
- **draw** — `Create ASCII art`
- **story** — `Read a story`
- **talk** — `Chat with a character`
- **play** — `Play a game`
- **music** — `Play music`
- **sonic** — `Audio / USB boot`

### Navigation Commands
- **map** — `Show spatial map`
- **goto** — `Navigate to location`
- **anchor** — `Bookmark a location`

### User & Identity Commands
- **user** — `Manage user profile`
- **uid** — `Manage user/device ID`
- **token** — `Generate auth tokens`

### System Management
- **binder** — `Manage knowledge binders`
- **destroy** — `Clean up/delete things`
- **undo** — `Undo recent changes`
- **migrate** — `Run data migrations`
- **notify** — `Send notifications`
- **bench** — `Performance benchmarks`

---

## 🎮 Natural Language Examples

### Just ask in chat:
```
"What is the health of my system?"
→ Uses ucode_health tool

"Show me the available commands with examples"
→ Uses ucode_help tool

"Run my backup script with full backup"
→ Uses ucode_run tool with arguments

"What's in my vault?"
→ Uses ucode_read and ucode_binder tools

"I need to initialize everything"
→ Uses ucode_setup tool

"Create a scheduled task for every day"
→ Uses ucode_scheduler tool

"What happened recently?"
→ Uses ucode_logs tool

"Help me understand uDOS"
→ Uses ucode_story and ucode_help tools
```

---

## 💡 Pro Tips

1. **Use natural language** — You don't need to memorize exact command names
2. **Use skills for guided workflows** — `/ucode-setup`, `/ucode-help`
3. **Use prompts for quick facts** — "Check my health", "What tools are available?"
4. **Combine with context** — Vibe will use multiple tools intelligently
5. **Ask for help** — "How do I..." questions work great

---

## 🚀 Common Workflows

### First Time Setup
1. Start Vibe: `vibe trust && vibe`
2. Type: `/ucode-setup`
3. Follow the interactive prompts
4. Type: `/ucode-help` to learn commands

### Daily Checkup
1. Type: `Check my system status`
2. Type: `What's my user profile?`
3. Type: `Show me recent logs`

### Run Automation
1. Type: `What scripts are available?`
2. Type: `Run the backup script`
3. Type: `Check if it succeeded`

### Learn More
1. Type: `/ucode-help` or ask "How do I..."
2. Type: `/ucode-story intro` for the tutorial
3. Type: `What are the available commands?` for a list

---

## ⚙️ Troubleshooting

### Tools not appearing?
The MCP server needs to be running. Vibe handles this automatically, but if issues occur:
```bash
# In another terminal:
uv run wizard/mcp/mcp_server.py
```

### Skills not working?
Make sure you used `/` at the start:
```
✗ ucode-help
✓ /ucode-help
```

### Don't see any response?
- Type `/help` to see keyboard shortcuts
- Wait a moment for tools to initialize
- Check that you're in the input box at the bottom

### Want to run a bash command directly?
Prefix with `!`:
```
!ls -la vibe/core/tools/ucode/
!uv run python --version
```

---

## 📖 Next Actions

1. **Start Vibe now:**
   ```bash
   vibe trust && vibe
   ```

2. **Type this first:**
   ```
   /ucode-help
   ```

3. **Or try this:**
   ```
   Check my system health
   ```

4. **Then explore:**
   Ask any question like:
   - "What can I do?"
   - "How do I set up?"
   - "Show me examples"
   - "What's available?"

---

**You're all set!** The 42 uDOS tools are now available through Vibe. 🎉
