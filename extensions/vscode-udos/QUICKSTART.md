# VS Code Extension Quick Start

**5-Minute Setup Guide** for the uDOS VS Code Extension

---

## Step 1: Install Dependencies (30 seconds)

```bash
cd /Users/fredbook/Code/uDOS/extensions/vscode-udos
npm install
```

---

## Step 2: Compile Extension (30 seconds)

```bash
npm run compile
```

Or use watch mode for development:
```bash
npm run watch
```

---

## Step 3: Launch Extension Development Host (10 seconds)

**In VS Code:**

1. Open `/Users/fredbook/Code/uDOS` workspace
2. Navigate to `extensions/vscode-udos/` folder
3. Press **F5** (or Run → Start Debugging)
4. A new VS Code window opens with extension loaded

---

## Step 4: Test the Extension (2 minutes)

### Test 1: Syntax Highlighting

1. In the Extension Development Host window, create a test file:
   ```
   File → New File → Save As: test.upy
   ```

2. Type this code:
   ```upy
   # Test Mission
   MISSION CREATE "Water Filter Construction"
   SET priority "high"

   GUIDE ADD tier3 guide "DIY Water Filter"
   MAP GOTO AA340 100

   IF $MISSION.STATUS == "ACTIVE" THEN
       CHECKPOINT SAVE "mission-start"
   END IF

   MISSION COMPLETE
   ```

3. **Verify**: Keywords should be color-coded, commands highlighted

### Test 2: IntelliSense

1. Type `GUI` → Press **Ctrl+Space**
2. **Verify**: See autocomplete suggestions (GUIDE, etc.)
3. Select `GUIDE` → See documentation popup

### Test 3: Hover Documentation

1. Hover over `MISSION CREATE`
2. **Verify**: See documentation with example

### Test 4: Code Snippets

1. New line, type `mission` → Press **Tab**
2. **Verify**: Mission template expands
3. Navigate placeholders with **Tab**

### Test 5: Run Script (requires uDOS API)

**First, start uDOS API server** (in uDOS terminal):
```bash
cd /Users/fredbook/Code/uDOS
./start_udos.sh
# Then in uDOS:
POKE API start
```

**Then in VS Code Extension Host:**
1. Open your `test.upy` file
2. Press **Ctrl+Shift+P** → Type "uDOS: Run Script"
3. **Verify**: Debug panel opens with execution results

---

## Step 5: Try Advanced Features (3 minutes)

### Knowledge Quality Checker

```
Ctrl+Shift+P → "uDOS: Check Knowledge Quality"
```

- Scans 228+ guides
- Shows quality report
- Flags guides for REGEN

### Sandbox Testing

```
Ctrl+Shift+P → "uDOS: Run in Sandbox"
```

- Creates isolated environment
- Safe testing
- Auto-cleanup

### Image Validation

Create test SVG:
```svg
<!-- test.svg -->
<svg width="100" height="100" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="blue"/>
</svg>
```

Right-click → **"uDOS: Preview SVG"**

---

## Configuration

**Settings** (File → Preferences → Settings → Search "uDOS"):

```json
{
  "udos.apiUrl": "http://localhost:5001",
  "udos.autoRunOnSave": false,
  "udos.sandboxAutoCleanup": true,
  "udos.showExecutionTime": true
}
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| IntelliSense | `Ctrl+Space` |
| Command Palette | `Ctrl+Shift+P` |
| Run Script | `Ctrl+Shift+P` → "Run Script" |
| Run in Sandbox | `Ctrl+Shift+P` → "Run in Sandbox" |
| Quick Open | `Ctrl+P` |

---

## Common Issues

### "Extension not found"
- Make sure you're in Extension Development Host (launched via F5)
- Check extension activated: Extensions panel → uDOS Language Support

### "API connection failed"
- Start uDOS: `./start_udos.sh`
- Start API: `POKE API start` (in uDOS)
- Verify: `curl http://localhost:5001/api/status`

### "Syntax highlighting not working"
- Check file extension is `.upy` (lowercase)
- Reload window: `Ctrl+Shift+P` → "Reload Window"

---

## What's Next?

### Explore Features

1. **Write Workflows**: Use snippets to create missions/workflows
2. **Test Knowledge**: Run quality checker on knowledge base
3. **Debug Scripts**: Use debug panel to inspect execution
4. **Validate Content**: Check SVG diagrams and ASCII art

### Development Workflow

```bash
# Terminal 1: Watch mode (auto-compile)
cd extensions/vscode-udos
npm run watch

# Terminal 2: uDOS API server
cd /Users/fredbook/Code/uDOS
./start_udos.sh
# Then: POKE API start

# Terminal 3: VS Code
# Press F5 to launch Extension Host
# Edit code → Save → Reload Extension Host (Ctrl+R)
```

### Read Documentation

- **Full README**: `extensions/vscode-udos/README.md`
- **uDOS Wiki**: https://github.com/fredporter/uDOS/wiki
- **Extension Dev Guide**: https://github.com/fredporter/uDOS/wiki/Extension-Development

---

## Next Steps After Setup

1. **Test All Commands**: Try each command in the Command Palette
2. **Check Knowledge Quality**: Run quality checker on full knowledge base
3. **Create Test Scripts**: Write .upy scripts and execute them
4. **Validate Images**: Test SVG/ASCII/teletext validators
5. **Report Issues**: File bugs on GitHub if you find any

---

**Status**: Ready to use! 🚀

**Need Help?** Check the full README or open an issue on GitHub.
