# 🎯 VS Code Extension - Quick Start Card

## 🚀 Launch (30 seconds)

1. Open VS Code
2. Press **F5** (or Run & Debug → "Run VS Code Extension")
3. New window opens
4. Look for "$(beaker) uDOS" in status bar → ✅ Working!

## 🧪 Test (2 minutes)

### Create Test File
File → New → Save as `test.upy`

### Try These:

```upy
# 1. Type this and watch colors appear (syntax highlighting)
GUIDE SEARCH "water"

# 2. Type GUI and autocomplete appears (IntelliSense)
GUI

# 3. Type $MIS and see variable suggestions
$MIS

# 4. Type mission then Tab (snippet expansion)
mission

# 5. Hover over GUIDE (documentation popup)
GUIDE
```

## ✅ Success Signs

- Commands are colored (GUIDE, MAP, SET)
- Variables are highlighted ($mission, $count)
- Typing `GUI` shows dropdown menu
- Typing `mission` + Tab expands template
- Hovering shows documentation
- No crashes, no errors

## 🎨 What It Does

### Works Offline (Always Available)
- **Syntax Highlighting** - Colors for commands, variables, comments
- **Autocomplete** - 60+ commands, all variables, properties
- **Snippets** - 15 templates (mission, workflow, foreach, if, etc.)
- **Hover Docs** - Documentation on every command

### Needs API (Start with: POKE API start)
- **Run Scripts** - Execute .upy files, see debug output
- **Sandbox** - Test safely in isolated environment
- **Quality Check** - Scan 228 knowledge guides
- **Image Tools** - Preview SVG, validate ASCII/teletext

## 🎮 Commands (Cmd+Shift+P)

- `uDOS: Run Script` - Execute current file
- `uDOS: Run in Sandbox` - Safe testing
- `uDOS: Check Knowledge Quality` - Scan guides

## 📝 Snippets (Type + Tab)

| Type | Get |
|------|-----|
| `mission` | Mission template |
| `workflow` | Workflow template |
| `foreach` | Loop template |
| `if` | Conditional |
| `guide` | Knowledge guide |

## 🐛 If Crashed

```bash
cd extensions/vscode-udos
npm install
npm run compile
# Then press F5 again
```

## 📖 Full Docs

- **DEMO.md** - Feature showcase (what extension does)
- **TESTING-GUIDE.md** - Detailed testing steps
- **FIXED-AND-READY.md** - What was fixed, how to test
- **TROUBLESHOOTING.md** - Debug guide

## 🎯 Quick Test Script

Copy this to `test.upy`:

```upy
#!/usr/bin/env udos
# Quick Feature Test

# Test 1: Autocomplete (type GUI and see dropdown)
GUIDE SEARCH "water"

# Test 2: Variable completion (type $MIS)
SET $mission "Test"

# Test 3: Property completion (type $MISSION.)
GET $MISSION.STATUS

# Test 4: Snippet (type mission + Tab)

# Test 5: Hover (hover over GUIDE)
GUIDE LIST

# If you see colors, autocomplete, and docs → ✅ Working!
```

---

**Now press F5 and test!** 🚀

**Still crashing?** Check Developer Tools (Help → Toggle Developer Tools → Console)
