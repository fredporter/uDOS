# uDOS Architecture - Core vs Extensions

## Design Principle

**Core CLI**: Minimal, stable, fully-functional command-line interface
**Extensions**: Optional features that enhance but are not required

## Directory Structure

\`\`\`
uDOS/
├── core/                    # Core CLI - Required
│   ├── uDOS_main.py         # Main loop
│   ├── uDOS_parser.py       # Command parsing
│   ├── uDOS_commands.py     # Command execution
│   ├── uDOS_grid.py         # Panel/viewport system
│   ├── commands/            # Command handlers
│   ├── services/            # Core services (user, history, etc)
│   └── utils/               # Core utilities
│
├── extensions/              # Optional Extensions
│   ├── core/                # Bundled extensions
│   │   └── teletext/        # Web GUI (optional)
│   │       ├── api_server.py
│   │       ├── api_server_manager.py
│   │       └── README.md
│   ├── bundled/             # Pre-installed extensions
│   └── setup/               # Extension installers
│
├── knowledge/               # Read-only system content
│   ├── system/              # Commands, themes, configs
│   └── demos/               # Examples
│
└── memory/                  # User workspace
    ├── user/                # User settings/data
    ├── logs/                # Session logs
    └── ...                  # User content
\`\`\`

## Core CLI Requirements

### Minimal Dependencies
- Python 3.8+
- prompt_toolkit (interactive prompts)
- python-dotenv (environment config)
- psutil (system monitoring)
- requests (HTTP client)

### Core Features (Always Available)
✅ Command execution
✅ File operations  
✅ Grid/panel system
✅ History management
✅ User profiles
✅ Theme switching
✅ Knowledge access
✅ Command parsing
✅ Script execution
✅ System health checks

## Extension Architecture

### How Extensions Load

1. **Core starts independently** - No extension dependencies
2. **Extensions check at runtime** - Only if explicitly enabled
3. **Silent fail** - Missing extensions don't break core
4. **User control** - Enable/disable via settings

### Example: Teletext Web GUI

\`\`\`python
# In core/uDOS_main.py
try:
    if user_settings.get('api_server_enabled', False):
        from extensions.core.teletext.api_server_manager import APIServerManager
        # Start if available
except ImportError:
    pass  # Extension not installed - CLI still works
\`\`\`

### Extension Categories

**1. Core Extensions** (\`/extensions/core/\`)
- Bundled with uDOS
- Disabled by default
- Example: Teletext web GUI

**2. Bundled Extensions** (\`/extensions/bundled/\`)
- Pre-installed tools
- Example: micro editor, typo editor

**3. Setup Extensions** (\`/extensions/setup/\`)
- Installation scripts for optional tools

## Startup Flow

\`\`\`
1. Load core modules (/core)
   ├─ Parser
   ├─ Grid
   ├─ Commands
   └─ Services

2. Initialize user environment (/memory)
   ├─ Load user profile
   ├─ Check settings
   └─ Restore session

3. Load knowledge (/knowledge)
   ├─ System commands
   ├─ Themes
   └─ Configurations

4. [Optional] Load extensions (if enabled)
   └─ Check user settings
       └─ Import only if api_server_enabled = true

5. Start CLI prompt
   └─ Fully functional regardless of extensions
\`\`\`

## Clean Startup (v1.0.26)

### What Changed

**Before** (v1.0.25):
\`\`\`
🌐 Starting API server... ❌ API server failed to start (exit code: 2)
⚠️  (continuing without API)
\`\`\`

**After** (v1.0.26):
\`\`\`
# Clean - no API messages unless explicitly enabled
🏥 System health... ⚠️  Warnings
🌳 Generating repository tree... ✓ structure.txt
\`\`\`

### Changes Made

1. **Moved API server to extensions**
   - From: \`core/services/api_server_manager.py\`
   - To: \`extensions/core/teletext/api_server_manager.py\`

2. **Default disabled**
   - \`api_server_enabled = False\` (was True)

3. **Silent import failure**
   - Missing extension doesn't show errors
   - CLI continues normally

## Best Practices

### For Core Development
- ✅ No extension dependencies
- ✅ Fail gracefully if extension missing
- ✅ Complete functionality without extensions
- ✅ Extensions enhance, don't enable

### For Extension Development
- ✅ Self-contained in \`/extensions\`
- ✅ Explicit enable/disable mechanism
- ✅ Document requirements separately
- ✅ Provide README in extension directory

### For Users
- ✅ CLI works immediately after clone
- ✅ Extensions opt-in, not opt-out
- ✅ Clear separation of core vs optional
- ✅ Settings in \`/memory\` (user-owned)

## Testing

### Core Only (Minimal)
\`\`\`bash
python3 test_system.py
# All core tests pass without extensions
\`\`\`

### With Extensions
\`\`\`bash
# Enable in settings first
SETTINGS SET api_server_enabled true
REBOOT
# Now API server starts
\`\`\`

## License Compliance

- **Core**: Personal/educational use
- **Knowledge**: Read-only, bundled content
- **Memory**: User-owned content
- **Extensions**: Per-extension licensing

## Version History

- **v1.0.26**: Moved API server to extensions, clean CLI-focused startup
- **v1.0.25**: Unified server consolidation
- **v1.0.24**: Teletext enhancement phase 3
- **v1.0.19**: Smart prompt with autocomplete

---

**Philosophy**: The CLI should be simple, fast, and fully functional. Extensions add power for those who want it, but never at the expense of core simplicity.
