# 🎯 VS Code Extension Demo & Capabilities

## What This Extension Does

The uDOS VS Code extension provides **full language support** for .upy (uDOS Python) script files with advanced editing, debugging, and quality tools.

---

## 🎨 1. Syntax Highlighting (Offline, Always On)

**What it does**: Colors different parts of your code for readability

**Try it**:
1. Open `test-examples/feature-test.upy`
2. Notice the colors:
   - **Commands** (GUIDE, MAP, MISSION) - bright/bold
   - **Variables** ($MISSION, $count) - different color
   - **Comments** (# lines) - gray/green
   - **Strings** ("text") - orange/yellow
   - **Keywords** (IF, FOREACH, WHILE) - purple/blue

**How it works**: Uses `syntaxes/upy.tmLanguage.json` to tokenize code

---

## 💡 2. IntelliSense Autocomplete (Offline, Always On)

**What it does**: Smart suggestions while typing with documentation

### Test Command Completion

1. Type `GUI` → See dropdown with GUIDE commands
2. Select `GUIDE SEARCH` → Inserts command with docs
3. Type `MAP` → See all map navigation commands
4. Type `MIS` → See MISSION commands

### Test Variable Completion

1. Type `$` → See all system variables:
   - `$MISSION` - Mission context
   - `$WORKFLOW` - Workflow state
   - `$CHECKPOINT` - Checkpoint data
   - `$GUIDE` - Guide information
   - `$LOCATION` - Current location

2. Type `$MISSION.` → See properties:
   - `ID`, `NAME`, `STATUS`, `PROGRESS`
   - `START_TIME`, `OBJECTIVE`, etc.

3. Type `$WORKFLOW.` → See workflow properties:
   - `NAME`, `PHASE`, `ITERATION`
   - `ERRORS`, `ELAPSED_TIME`, etc.

### What You Get

- 60+ uDOS commands with examples
- All system variables with descriptions
- Property completion for complex variables
- Parameter hints and usage docs

**Triggers**:
- Space bar → Command completion
- Dot (.) → Property completion
- $ symbol → Variable completion

---

## 📝 3. Code Snippets (Offline, Always On)

**What it does**: Type shortcuts that expand to code templates

### Available Snippets

Type these and press **Tab** to expand:

| Shortcut | Expands To | Use Case |
|----------|------------|----------|
| `mission` | Full mission template | Quick mission creation |
| `workflow` | Workflow template | Workflow script structure |
| `foreach` | For-each loop | Iterate over items |
| `while` | While loop | Conditional looping |
| `if` | If-then-else | Conditional logic |
| `guide` | Guide creation | Add knowledge guide |
| `map` | Map navigation | Location navigation |
| `checkpoint` | Checkpoint save/load | State management |
| `gen-guide` | AI guide generation | Generate knowledge with AI |
| `gen-diagram` | AI diagram generation | Create SVG diagrams |
| `try` | Error handling | Try-catch block |
| `batch` | Batch processing | Process multiple items |
| `header` | File header | Add metadata header |
| `debug` | Debug output | Debug logging |
| `cleanup` | Cleanup handler | Resource cleanup |

### Try It

1. New line in .upy file
2. Type `mission`
3. Press **Tab**
4. Full mission template appears with placeholders
5. **Tab** moves between placeholders

**Result**:
```upy
MISSION CREATE "Mission Name"
SET $objective "Objective description"
SET $priority "medium"
SET $location "TILE-CODE"

MISSION START

# Mission steps
CHECKPOINT SAVE "step-1"

# Your code here

MISSION COMPLETE
```

---

## 📖 4. Hover Documentation (Offline, Always On)

**What it does**: Shows docs when you hover over code

### Try It

1. Hover over `GUIDE` → See knowledge system documentation
2. Hover over `MAP` → See mapping system docs with examples
3. Hover over `MISSION` → See mission management commands
4. Hover over `$MISSION` → See variable details and properties
5. Hover over `WORKFLOW` → See workflow automation docs

### What You See

- Command description and purpose
- All subcommands and syntax
- Real usage examples
- Parameter details
- Categories and tiers (for knowledge)
- Tile codes and layers (for maps)

---

## 🐛 5. Script Execution (Requires API Server)

**What it does**: Run .upy scripts directly from VS Code with debug output

### Prerequisites

```bash
# Start uDOS
./start_udos.sh

# In uDOS, start API server:
POKE API start

# Verify running:
curl http://localhost:5001/health
```

### Run Script

1. Open any .upy file
2. **Command Palette** (Cmd+Shift+P or Ctrl+Shift+P)
3. Type "uDOS: Run Script"
4. Press Enter

### What Happens

1. **Debug panel** opens in second column
2. Shows:
   - **Output**: Script execution results
   - **Variables**: All variable values
   - **Execution Time**: How long it took
   - **Errors**: Any errors that occurred
3. **Status message**: Success or failure notification
4. **Live results**: See output as script runs

### Example

Running `feature-test.upy`:
```
✅ Script executed successfully (0.23s)

OUTPUT:
-------
Hello uDOS
Counter: 42
Processing: item1
Processing: item2
...

VARIABLES:
----------
$test_var = "Hello uDOS"
$counter = 100
$MISSION.STATUS = "ACTIVE"

EXECUTION TIME: 0.23 seconds
```

---

## 🧪 6. Sandbox Testing (Requires API Server)

**What it does**: Run scripts in isolated environments without affecting production data

### Why Use Sandbox

- Test dangerous operations safely
- Experiment without consequences
- Compare sandbox vs production results
- Auto-cleanup after testing

### Run in Sandbox

1. Open .upy file
2. **Command Palette** → "uDOS: Run in Sandbox"
3. Script runs in isolated uDOS instance
4. Results shown in debug panel
5. Sandbox automatically cleaned up

### Use Cases

- Testing new workflows
- Experimenting with missions
- Validating complex scripts
- Learning uDOS commands

---

## 📚 7. Knowledge Quality Checker (Requires API Server)

**What it does**: Scans all 228 knowledge guides and reports quality issues

### Run Quality Check

1. **Command Palette** → "uDOS: Check Knowledge Quality"
2. Extension scans knowledge bank:
   - `knowledge/water/` (26 guides)
   - `knowledge/fire/` (20 guides)
   - `knowledge/shelter/` (20 guides)
   - `knowledge/food/` (23 guides)
   - `knowledge/navigation/` (20 guides)
   - `knowledge/medical/` (27 guides)

### What It Reports

**Quality Metrics**:
- Word count (flags <200 words)
- Example count (flags if <2 examples)
- Cross-reference count
- Last updated date

**Issues Flagged**:
- Outdated content (>6 months old)
- Missing frontmatter metadata
- Broken internal links
- Insufficient examples
- Too brief content

**Recommendations**:
- Generates batch REGEN commands
- Suggests content improvements
- Prioritizes critical fixes

### Example Output

```
📊 Knowledge Quality Report
═══════════════════════════

Total Guides: 228
High Quality: 186 (82%)
Needs Update: 32 (14%)
Critical: 10 (4%)

🚨 Critical Issues:
- water/emergency-sources.md (outdated 12 months)
- fire/waterproof-matches.md (missing examples)

💡 Recommendations:
REGEN water/emergency-sources.md
REGEN fire/waterproof-matches.md
...

Run batch fix:
GUIDE REGEN --batch critical-fixes.txt
```

---

## 🎨 8. Image Format Validation (Requires API Server)

**What it does**: Preview and validate SVG, ASCII art, and teletext files

### SVG Preview

1. Open SVG file in `memory/drafts/svg/`
2. **Right-click** → "uDOS: Preview SVG"
3. Or **Command Palette** → "uDOS: Preview SVG"

**Shows**:
- Visual rendering
- SVG structure validation
- Dimension check
- Element count
- Style analysis

### ASCII Art Testing

1. Create ASCII art file
2. **Command Palette** → "uDOS: Preview ASCII Art"

**Validates**:
- Line length consistency
- Character set compatibility
- Box drawing characters
- Rendering preview

### Teletext Validation

1. Create teletext page (24 rows × 40 columns)
2. **Command Palette** → "uDOS: Validate Teletext"

**Checks**:
- Grid dimensions (24×40)
- Control codes
- Color sequences
- Format compliance

---

## 🚀 Quick Demo (2 Minutes)

### Test Without API (Offline Features)

1. **Open**: `test-examples/feature-test.upy`

2. **Syntax Highlighting**: See colored code

3. **Autocomplete**:
   - Type `GUI` → Dropdown appears
   - Type `$MIS` → Variable suggestions

4. **Hover Docs**:
   - Hover over `GUIDE` → Documentation
   - Hover over `MAP` → Map system docs

5. **Snippets**:
   - Type `mission` + Tab → Template expands
   - Type `foreach` + Tab → Loop template

### Test With API (Advanced Features)

1. **Start API**:
   ```bash
   ./start_udos.sh
   # In uDOS:
   POKE API start
   ```

2. **Run Script**:
   - Cmd+Shift+P → "uDOS: Run Script"
   - See debug panel with results

3. **Quality Check**:
   - Cmd+Shift+P → "uDOS: Check Knowledge Quality"
   - View report

---

## 📊 Feature Comparison

| Feature | Offline | Requires API |
|---------|---------|--------------|
| Syntax Highlighting | ✅ | - |
| Autocomplete | ✅ | - |
| Snippets | ✅ | - |
| Hover Docs | ✅ | - |
| Script Execution | - | ✅ |
| Sandbox Testing | - | ✅ |
| Quality Checker | - | ✅ |
| Image Validation | - | ✅ |

---

## 🎓 Learning Path

### Beginner (No API)
1. Install extension
2. Open test file
3. Explore syntax highlighting
4. Try autocomplete
5. Use snippets

### Intermediate (With API)
6. Start API server
7. Run simple scripts
8. Use sandbox mode
9. Check variable values

### Advanced
10. Run quality checker
11. Validate custom diagrams
12. Debug complex workflows
13. Optimize mission scripts

---

## 💪 Power User Tips

### 1. Keyboard Shortcuts

- **Cmd/Ctrl + Shift + P** → Command Palette
- **Tab** → Expand snippet
- **Cmd/Ctrl + Space** → Trigger autocomplete
- **F5** → Launch extension (dev mode)

### 2. Multi-Cursor Editing

Select multiple lines and bulk-edit commands:
1. Cmd/Ctrl + D → Select next occurrence
2. Edit all at once

### 3. Snippet Customization

Add custom snippets in `snippets/upy.json`:
```json
"my-template": {
  "prefix": "mytemp",
  "body": [
    "# Custom template",
    "$1"
  ]
}
```

### 4. Workspace Settings

`.vscode/settings.json`:
```json
{
  "udos.apiUrl": "http://localhost:5001",
  "udos.showExecutionTime": true,
  "udos.sandboxAutoCleanup": true
}
```

---

## 🔧 Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `udos.apiUrl` | `http://localhost:5001` | uDOS API server URL |
| `udos.showExecutionTime` | `true` | Show script execution time |
| `udos.sandboxAutoCleanup` | `true` | Auto-delete sandbox files |
| `udos.debugPanel` | `column-two` | Where to show debug output |
| `udos.knowledgePath` | `knowledge/` | Knowledge bank path |

---

## 🎯 What Makes This Extension Powerful

### 1. **Context-Aware Intelligence**
- Knows uDOS command structure
- Understands system variables
- Suggests based on cursor position

### 2. **Offline-First Design**
- Core features work without internet
- No external dependencies for basic use
- API features degrade gracefully

### 3. **Real-World Integration**
- Executes actual uDOS scripts
- Works with live knowledge bank
- Integrates with map system

### 4. **Quality Tools**
- 228-guide scanner
- Automated quality metrics
- Batch fix generation

### 5. **Safe Testing**
- Isolated sandbox environments
- No production data impact
- Easy experimentation

---

## 🐛 Troubleshooting

### Extension Won't Activate

```bash
cd extensions/vscode-udos
npm install
npm run compile
```

### Autocomplete Not Working

1. File saved as `.upy`?
2. Try triggering: Cmd/Ctrl + Space

### API Features Failing

1. Is uDOS running? `./start_udos.sh`
2. Is API started? `POKE API start`
3. Test: `curl http://localhost:5001/health`

### No Syntax Highlighting

1. File extension is `.upy`
2. Language mode set to "uPY"
3. Restart VS Code

---

## 📝 Example Workflows

### Workflow 1: Create Knowledge Guide

```upy
# Type and autocomplete guides you:
GUIDE ADD tier3 guide "Solar Water Disinfection"
GUIDE TAG <guide-id> water,solar,purification,tier3
GUIDE UPDATE <guide-id> complexity detailed
```

### Workflow 2: Map Exploration

```upy
# Autocomplete shows all MAP commands:
MAP GOTO AA340 100
MAP NEARBY 50
MAP SEARCH "water source"
MAP ROUTE AA340 AB345
```

### Workflow 3: Mission Automation

```upy
# Use mission snippet:
mission<TAB>

# Expands to full template
# Fill in placeholders with autocomplete
```

---

## 🎉 Success Metrics

After setup, you should have:

- ✅ Syntax highlighting in .upy files
- ✅ Autocomplete when typing commands
- ✅ Snippets expanding with Tab
- ✅ Hover documentation on commands
- ✅ Status bar showing "$(beaker) uDOS"
- ✅ No errors in Output panel
- ✅ Commands in Command Palette (search "uDOS:")

**With API running**:
- ✅ Scripts execute with debug output
- ✅ Quality checker scans knowledge
- ✅ Sandbox mode creates isolated tests

---

## 🚀 Next Steps

1. **Try the demo file**: Open `test-examples/feature-test.upy`
2. **Explore snippets**: Type snippet names + Tab
3. **Test autocomplete**: Type partial commands
4. **Read hover docs**: Hover over any command
5. **Start API**: Enable advanced features
6. **Run scripts**: Test execution panel
7. **Check quality**: Scan knowledge guides

The extension is designed to make uDOS scripting **faster**, **safer**, and **easier** with intelligent assistance at every step. 🎯
