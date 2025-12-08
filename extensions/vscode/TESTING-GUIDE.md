# 🧪 VS Code Extension Testing Guide

## Quick Test (2 minutes)

This will verify the extension works without crashing.

### Step 1: Launch Extension Development Host

1. **Open Extension Folder**:
   ```bash
   cd /Users/fredbook/Code/uDOS
   code extensions/vscode-udos
   ```

2. **Press F5** or use launch config "Run VS Code Extension"
   - New VS Code window opens (Extension Development Host)
   - Check bottom-right: Should show "$(beaker) uDOS" status icon

3. **Check for Crashes**:
   - If window opens without errors → ✅ Extension activated successfully
   - If crash occurs → Open Developer Tools (Help → Toggle Developer Tools)

### Step 2: Test Basic Features (No API Required)

1. **Create Test File**:
   - In Extension Development Host window
   - New File → Save as `test.upy`

2. **Test Syntax Highlighting**:
   ```upy
   # This should be colored as comment
   GUIDE SEARCH "water"
   SET $location "AA340"

   IF $count > 10 THEN
       ECHO "Large count"
   END
   ```

   ✅ Commands should be highlighted
   ✅ Variables should be colored differently
   ✅ Comments should be gray/green

3. **Test IntelliSense (Autocomplete)**:
   - Type `GUI` → Should show autocomplete dropdown
   - Select `GUIDE SEARCH` → Documentation appears
   - Type `$MIS` → Should suggest `$MISSION`
   - Type `$MISSION.` → Should show properties (ID, NAME, STATUS, etc.)

4. **Test Snippets**:
   - Type `mission` → Press Tab
   - Should expand to mission template
   - Try: `workflow`, `foreach`, `if`, `guide`

5. **Test Hover Documentation**:
   - Hover over `GUIDE` → Should show documentation
   - Hover over `$MISSION` → Should show variable info
   - Hover over `MAP` → Should show map system docs

## Advanced Testing (With uDOS API)

These features require the uDOS API server running on port 5001.

### Step 3: Start uDOS API Server

```bash
cd /Users/fredbook/Code/uDOS
./start_udos.sh

# In uDOS prompt:
POKE API start
```

Verify: http://localhost:5001/health should return `{"status":"healthy"}`

### Step 4: Test Script Execution

1. **Create Test Script** (`test-execution.upy`):
   ```upy
   # Simple execution test
   SET $name "TestUser"
   SET $count 5

   ECHO "Hello from $name"
   ECHO "Count: $count"

   STATUS
   ```

2. **Run Script**:
   - Command Palette (Cmd+Shift+P)
   - Type "uDOS: Run Script"
   - Select command

   ✅ Debug panel opens in second column
   ✅ Output shows script results
   ✅ Variables displayed
   ✅ Execution time shown

3. **Test Sandbox Mode**:
   - Command Palette → "uDOS: Run in Sandbox"
   - Runs in isolated environment
   - Shows comparison with production

### Step 5: Test Knowledge Quality Checker

1. **Run Checker**:
   - Command Palette → "uDOS: Check Knowledge Quality"
   - Scans all 228 knowledge guides

   ✅ Shows quality report
   ✅ Flags outdated content
   ✅ Suggests REGEN commands
   ✅ Displays metrics

### Step 6: Test Image Validation

1. **SVG Preview**:
   - Create/open SVG file in drafts
   - Right-click → "uDOS: Preview SVG"
   - Or Command Palette → "uDOS: Preview SVG"

2. **ASCII Preview**:
   - Create ASCII art file
   - Command Palette → "uDOS: Preview ASCII Art"

3. **Teletext Validation**:
   - Create teletext file (24×40 grid)
   - Command Palette → "uDOS: Validate Teletext"

## What The Extension Does

### ✅ Works Offline (No API Required)

1. **Syntax Highlighting**
   - Keywords: IF, FOREACH, WHILE, SET, GET
   - Commands: GUIDE, MAP, MISSION, WORKFLOW (60+ total)
   - Variables: $MISSION, $WORKFLOW, $CHECKPOINT
   - Comments: # lines
   - Strings: "quoted text"

2. **IntelliSense (Autocomplete)**
   - All 60+ uDOS commands with examples
   - System variables with property completion
   - Context-aware suggestions
   - Inline documentation

3. **Code Snippets**
   - `mission` → Mission template
   - `workflow` → Workflow template
   - `foreach` → Loop template
   - `if` → Conditional template
   - `guide` → Knowledge guide template
   - `map` → Map navigation template
   - `checkpoint` → Checkpoint template
   - 15+ snippets total

4. **Hover Documentation**
   - Command documentation on hover
   - Variable details
   - Usage examples
   - Parameter descriptions

### ⚡ Requires API (Advanced Features)

5. **Script Execution**
   - Run .upy scripts directly from VS Code
   - View output in debug panel
   - See variable values
   - Execution timing

6. **Sandbox Testing**
   - Isolated test environments
   - Safe experimentation
   - Compare sandbox vs production
   - Auto-cleanup

7. **Knowledge Quality Checker**
   - Scan 228 knowledge guides
   - Quality metrics (word count, examples, refs)
   - Flag outdated content
   - Generate REGEN batch commands

8. **Image Validation**
   - SVG diagram preview
   - ASCII art testing
   - Teletext format validation
   - Visual rendering in panels

## Expected Behavior

### ✅ Successful Activation

- Extension Development Host opens
- No console errors in Developer Tools
- Status bar shows "$(beaker) uDOS"
- .upy files recognized with icon
- Syntax highlighting works immediately
- Autocomplete triggers on typing

### ❌ Common Issues

**Issue**: VS Code crashes on F5
- **Cause**: Missing dependencies
- **Fix**: `npm install && npm run compile`

**Issue**: "Cannot find module './out/extension.js'"
- **Cause**: Not compiled
- **Fix**: `npm run compile`

**Issue**: Commands not appearing
- **Cause**: Activation events not triggered
- **Fix**: Open a .upy file or use Command Palette

**Issue**: "API server not responding"
- **Cause**: uDOS not running or POKE API not started
- **Fix**: Start uDOS and run `POKE API start`
- **Note**: Basic features work without API

**Issue**: No syntax highlighting
- **Cause**: File not saved as .upy
- **Fix**: Save file with .upy extension

## Configuration

Extension settings (File → Preferences → Settings → search "uDOS"):

```json
{
  "udos.apiUrl": "http://localhost:5001",
  "udos.showExecutionTime": true,
  "udos.sandboxAutoCleanup": true,
  "udos.debugPanel": "column-two",
  "udos.knowledgePath": "knowledge/"
}
```

## Troubleshooting

### Enable Debug Output

1. View → Output
2. Select "uDOS Language Support" from dropdown
3. Check for activation messages

### Check Developer Tools

1. Help → Toggle Developer Tools
2. Console tab
3. Look for red error messages

### Verify Files

```bash
cd extensions/vscode-udos
ls -la out/extension.js        # Should exist after compile
ls -la syntaxes/               # Syntax files
ls -la snippets/               # Snippet files
```

### Test Minimal Activation

Edit `src/extension.ts`, comment out providers:

```typescript
export function activate(context: vscode.ExtensionContext) {
    console.log('uDOS extension activated!');

    // Comment out providers temporarily to isolate issue
    // const upySelector = ...
    // context.subscriptions.push(...)
}
```

Then: `npm run compile` and test with F5.

## Demo Script

Use this to showcase extension features:

```upy
#!/usr/bin/env udos
# Demo: VS Code Extension Features
# Shows autocomplete, snippets, syntax highlighting

# === Knowledge Management ===
GUIDE SEARCH "water purification"
GUIDE LIST water
GUIDE ADD tier3 guide "Emergency Water Storage"

# === Map Navigation ===
MAP GOTO AA340 100        # Sydney, Australia
MAP ASCEND                # Cloud layer
MAP SEARCH "London"       # Find location
MAP DISTANCE AA340 JF57   # Sydney to London

# === Mission System ===
MISSION CREATE "Water Source Survey"
SET $objective "Find 3 clean water sources within 5km"
MISSION START

IF $MISSION.STATUS == "ACTIVE" THEN
    CHECKPOINT SAVE "mission-start"

    # Loop through locations
    FOREACH $location IN $nearby_tiles
        MAP GOTO $location
        ECHO "Surveying: $location"
    END

    MISSION COMPLETE
END

# === Workflow Automation ===
WORKFLOW START knowledge-expansion
WORKFLOW STATUS

# === File Operations ===
NEW memory/missions/water-survey.upy
COPY knowledge/water/purification.md memory/docs/
BACKUP memory/missions/active.json

# === Graphics ===
GENERATE DIAGRAM water "Solar Still Design"
SPRITE CREATE water-drop 8 8
PANEL RENDER dashboard main

# === System ===
STATUS --detailed
SETTINGS theme galaxy
CLEAN --scan
```

## Success Checklist

After testing, verify:

- [ ] Extension activates without crash
- [ ] Status bar shows "$(beaker) uDOS"
- [ ] .upy files have syntax highlighting
- [ ] Autocomplete works (type `GUI` → suggestions appear)
- [ ] Snippets expand (type `mission` + Tab)
- [ ] Hover documentation displays (hover over `GUIDE`)
- [ ] Variable completion works (`$MISSION.` → properties)
- [ ] Commands appear in Command Palette (search "uDOS:")
- [ ] No errors in Output → "uDOS Language Support"
- [ ] No errors in Developer Tools Console

## Next Steps

If all basic tests pass but API features fail:

1. Verify uDOS is running: `./start_udos.sh`
2. Start API server: `POKE API start` (in uDOS)
3. Test health endpoint: `curl http://localhost:5001/health`
4. Check firewall/port availability
5. Review API logs in uDOS output

The extension is designed to **degrade gracefully** - syntax highlighting, autocomplete, and snippets work without the API. Only advanced features (execution, quality checker, image preview) require the server.
