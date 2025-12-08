# Frequently Asked Questions

Common questions about uDOS

---

## General Questions

### What is uDOS?

uDOS is an **offline-first operating system** for survival knowledge, mapping, and text-based computing. Key features:
- **Survival Knowledge**: Water, shelter, fire, medical, navigation guides
- **Grid Mapping**: TILE-based navigation system (AA00-RL269 grid)
- **Workflow Automation**: Mission scripts with checkpoints (uPY runtime)
- **TUI Interface**: Full keyboard navigation (W/C/D/L/T-key panels)
- **Offline-First**: Works without internet/API keys

### Is uDOS production-ready?

uDOS v1.2.20 is **stable and functional** with 96% feature completion:
- ✅ 148 SHAKEDOWN tests passing (95.9% coverage)
- ✅ Workflow management with checkpoints
- ✅ Complete TUI system (8 key bindings)
- ✅ Grid mapping (100-899 layers)
- 🔄 v1.2.21 (AI Assistant) = STABLE RELEASE

### Do I need an API key to use uDOS?

**No!** uDOS works fully without an API key. It has two modes:
- **ONLINE**: Uses Gemini API for AI features (requires key)
- **OFFLINE**: Uses built-in logic engine (no key needed)

The system automatically detects connectivity and switches modes.

---

## Installation & Setup

### What are the system requirements?

**Minimum**:
- Python 3.9+
- 80×24 terminal
- 512 MB RAM
- 50 MB disk space

**Recommended**:
- Python 3.11+
- 120×40 terminal (256-color)
- 1 GB RAM
- 100 MB disk space

### How do I install uDOS?

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./start_udos.sh
```

[Full installation guide →](Quick-Start)

### Why won't my terminal run the start script?

Make it executable:
```bash
chmod +x start_udos.sh
```

Or run directly:
```bash
source .venv/bin/activate && python3 uDOS_main.py
```

### Where do I get a Gemini API key?

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get a free API key.

Add to `.env` file:
```
GEMINI_API_KEY='your_key_here'
```

---

## Features & Usage

### What's the difference between a command and uCODE?

- **Command**: User-facing syntax (`LOAD "file.txt"`)
- **uCODE**: Internal structured format (`[FILE|LOAD*file.txt*main]`)

Users type commands, uDOS translates to uCODE for execution.

[Learn more about uCODE →](uCODE-Language)

### What scripting features exist?

**uPY Runtime** (v1.2.x):
- Variables: `$MISSION.*`, `$WORKFLOW.*`, `$LOCATION.*`
- Flow control: `IF/ELIF/ELSE`, `FOR`, `WHILE`
- Commands: `PRINT`, `SET`, `CHECKPOINT`, `GUIDE`
- TILE integration: Grid location tracking

**Example**:
```python
SET DESTINATION="AB340"  # Sydney
FOR STEP IN RANGE(1, 6):
    PRINT "Step $STEP of 5"
    CHECKPOINT "Step $STEP complete"
END
```

See mission templates in `memory/ucode/adventures/`

---

## TUI Features (v1.2.15+)

### What key bindings are available?

**Panel Keys** (v1.2.20):
- **W-key**: Workflow manager (missions, checkpoints)
- **C-key**: Config & settings browser
- **D-key**: System file browser (dev files)
- **L-key**: Debug/log panel (live logs)
- **T-key**: Testing interface (SHAKEDOWN)
- **S-key**: Server panel (extensions, health)
- **0-key**: File browser (5 workspaces)
- **ESC**: Close current panel

### How do workflows work?

Press **W** to open workflow manager:

```bash
# Create workflow from template
W → T (templates) → Select template → ENTER

# Start mission
W → Select workflow → S (start)

# View checkpoints
W → Select workflow → D (details)
```

**Mission templates**: water, shelter, navigation, medical, fire, food
**Dev workflows**: build, test, deploy, release

### Where is data stored?

```
memory/workflows/          # Workflows and checkpoints
memory/ucode/adventures/   # Mission scripts (.upy)
memory/system/user/        # User settings
memory/logs/               # System logs
```

---

## Scripting & Automation (v1.2.x)

### What is a .upy file?

A **uPY script** for mission automation and workflows:

```python
# water_collection.upy
MISSION_NAME="Water Collection"
STEP=1
TOTAL_STEPS=5

# Step 1: Location check
CURRENT_LOCATION=$LOCATION.TILE_CODE
PRINT "Location: $CURRENT_LOCATION"

# Step 2: Assess water source
IF $CURRENT_LOCATION CONTAINS "WATER" THEN
    SET WATER_SOURCE_AVAILABLE="yes"
END

# Create checkpoint
CHECKPOINT "Location Assessment"
```

Run via workflow manager (W-key) or `RUN "script.upy"`

**Features**:
- TILE location tracking (AA00-RL269)
- Checkpoint system (save/resume)
- GUIDE integration (knowledge access)
- Conditional logic (IF/ELIF/ELSE)
- Variable tracking ($MISSION.*, $WORKFLOW.*)

### What's the difference between workflows and missions?

**Workflows** = Container for mission execution  
**Missions** = uPY script with steps/checkpoints

Example:
```
Workflow: "Water Collection - Dec 8"
  ├─ Mission script: water_collection.upy
  ├─ Status: ACTIVE
  ├─ Progress: 3/5 steps
  └─ Checkpoints: 2 saved
```

### Can I create custom mission templates?

Yes! Place in `memory/ucode/adventures/`:

```python
# my_mission.upy
MISSION_NAME="Custom Mission"
STEP=1
TOTAL_STEPS=3

PRINT "Step 1: Setup"
CHECKPOINT "Setup complete"

PRINT "Step 2: Execute"
CHECKPOINT "Execution complete"

PRINT "Step 3: Verify"
CHECKPOINT "Mission complete"
```

Press **W → T** to see custom templates.

### How long are checkpoints kept?

**Retention policy**:
- Active workflows: All checkpoints kept
- Paused workflows: 30 days
- Completed workflows: Moved to `.archive/` after 7 days

Manual cleanup:
```bash
CLEAN --checkpoints  # Remove old checkpoints
ARCHIVE --workflows  # Archive completed work
```

---

## Installation & Setup

### System requirements?

**Minimum**:
- Python 3.9+
- 100MB disk space
- Terminal emulator (Terminal.app, iTerm2, GNOME Terminal)

**Optional**:
- Gemini API key (AI features)
- Git (version control)

### Installation steps?

```bash
# Clone repository
git clone https://github.com/fredbook/uDOS.git
cd uDOS

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run uDOS
./start_udos.sh
```

### First-time setup?

On first launch, uDOS will:
1. Create `memory/` workspace folders
2. Initialize configuration in `memory/system/user/`
3. Ask for optional Gemini API key
4. Run SHAKEDOWN validation (148 tests)

**No API key?** All core features work offline.

### How do I update?

```bash
cd uDOS
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

Check version: `CONFIG STATUS` command or `W → About`

---

## Development

### How do I contribute?

1. Fork repository on GitHub
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run tests: `pytest memory/ucode/tests/`
5. Submit pull request

See [Contributing Guide](CONTRIBUTING.md)

### Where are the tests?

```
memory/ucode/tests/        # Unit tests
memory/tests/shakedown.uscript  # Integration tests (148 checks)
```

Run all tests:
```bash
pytest memory/ucode/tests/ -v
./start_udos.sh memory/tests/shakedown.uscript
```

### How do I add a command?

1. Create handler in `core/commands/my_handler.py`
2. Register in `core/uDOS_commands.py` routing map
3. Add to `core/data/commands.json` (autocomplete)
4. Write test in `memory/ucode/tests/test_my_feature.py`
5. Update `wiki/Command-Reference.md`

See [Developers Guide](Developers-Guide.md)

### Project structure?

```
core/           # System code (stable, tracked)
extensions/     # Extension system
knowledge/      # Survival guides (read-only)
memory/         # User workspace (gitignored)
wiki/           # Documentation
dev/            # Development files (tracked)
```

See [Architecture](Architecture.md)

---

## Troubleshooting

### Commands not working?

```bash
# Check system health
CONFIG CHECK

# View logs
L  # Opens debug panel (v1.2.20)

# Run diagnostic
SHAKEDOWN  # 148 validation tests
```

### TUI panels not opening?

**Check key bindings**:
- Ensure terminal supports key events
- Try uppercase keys (W not w)
- Close other panels first (ESC)

**Reset TUI**:
```bash
TUI DISABLE
TUI ENABLE
```

### Workflow checkpoints failing?

**Verify paths**:
```bash
memory/workflows/checkpoints/  # Must exist
memory/workflows/state/        # Must exist
```

**Fix**:
```bash
CONFIG FIX  # Auto-creates missing folders
```

### Where are logs?

```
memory/logs/udos.log           # Main log
memory/logs/commands.log       # Command history
memory/logs/errors.log         # Error tracking
```

View live: Press **L** key (debug panel)

---

## More Resources

- [Getting Started](Getting-Started.md) - Installation and first steps
- [Command Reference](Command-Reference.md) - All commands
- [Workflow Guide](Workflow-Management.md) - Mission system
- [TUI Guide](TUI-Guide.md) - Keyboard navigation
- [Mapping System](Mapping-System.md) - TILE grid documentation
- [Developers Guide](Developers-Guide.md) - Contributing code

**Need help?** Open an issue on [GitHub](https://github.com/fredbook/uDOS/issues)
