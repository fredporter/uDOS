# Quick Start

Use this page as the thin root entry only. The detailed operator guides live under `docs/`.

## Install

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
./bin/install-udos.sh
```

Manual and profile-specific setup lives in [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Bootstrap

```bash
ucode SETUP
ucode STATUS
ucode UCODE PROFILE LIST
ucode UCODE OPERATOR STATUS
```

## Next Docs

- Public docs: [docs/README.md](docs/README.md)
- Installation: [docs/INSTALLATION.md](docs/INSTALLATION.md)
- Contributor workspace: [dev/docs/README.md](dev/docs/README.md)
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
