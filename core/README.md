# uDOS Core System

The core system contains all Python modules that power uDOS v1.2.21.

## Architecture Overview

```
core/
├── commands/         # Command handlers (60+ commands)
├── services/         # Core services
├── input/            # Input handling and prompts
├── output/           # Output formatting and rendering
├── knowledge/        # Knowledge management
├── network/          # Networking and API services
├── ui/               # UI components (selectors, prompts)
├── theme/            # Theme system
├── utils/            # Utility functions
├── interpreters/     # uCODE interpreter
├── tests/            # Core system tests
├── config.py         # Configuration management
├── uDOS_main.py      # Main application loop
├── uDOS_parser.py    # CLI to uCODE parser
├── uDOS_logger.py    # Logging system
├── uDOS_startup.py   # Startup sequence
└── __init__.py       # Package initialization
```

## Key Modules

### Command Handlers (`/commands`)

60+ specialized command handlers organized by function:

- **`assistant_handler.py`** - AI assistant (ASK, ASSIST commands)
- **`file_handler.py`** - File operations (FILE, EDIT, SHOW, etc.)
- **`knowledge_handler.py`** - Knowledge access (GUIDE, LEARN, DOCS)
- **`memory_handler.py`** - Memory tier management
- **`security_handler.py`** - RBAC and security commands
- **`web_handler.py`** - Web GUI commands (WEB START/STOP/OPEN)
- **`system_handler.py`** - System commands (STATUS, VERSION, REPAIR)
- **`config_handler.py`** - Configuration (CONFIG ROLE/INSTALL/etc.)

### Core Services (`/services`)

Essential services that power uDOS features:

**Security (v1.1.2)**
- **`rbac_manager.py`** - Role-based access control (User/Power/Wizard/Root)
- **`security_layer.py`** - Centralized security enforcement
- **`installation_manager.py`** - Installation type management (CLONE/SPAWN/HYBRID)
- **`integrity_checker.py`** - SHA-256 file integrity verification

**Knowledge Management (v1.1.2)**
- **`knowledge_library.py`** - Offline knowledge library (8 categories)
- **`knowledge_validator.py`** - Content validation and quality scoring
- **`citation_manager.py`** - Citation extraction and bibliography
- **`diagram_generator.py`** - SVG diagram generation

**AI & Analytics (v1.1.0)**
- **`ai_assistant.py`** - AI integration with offline fallback
- **`session_analytics.py`** - Command tracing and session logging
- **`intelligent_error_handler.py`** - Error classification and suggestions

**Web Infrastructure (v1.1.1)**
- **`web_server.py`** - Production Flask server
- **`state_sync.py`** - CLI↔Web state synchronization
- **`websocket_manager.py`** - Real-time WebSocket streaming

**UI & Input (v1.1.0)**
- **`input_manager.py`** - Unified input handling
- **`session_replay.py`** - Session recording and playback
- **`smart_prompt.py`** - Autocomplete and suggestions

### Input System (`/input`)

Terminal input handling and prompt management:

- **`prompt_manager.py`** - Dynamic prompt generation
- **`autocomplete.py`** - Command autocomplete
- **`input_validator.py`** - Input validation and sanitization

### Output System (`/output`)

Output formatting and rendering:

- **`formatter.py`** - Output formatting (tables, lists, trees)
- **`teletext_renderer.py`** - Teletext/retro graphics rendering
- **`color_manager.py`** - Color theme management
- **`panel_manager.py`** - Panel system for UI layout

### Knowledge Management (`/knowledge`)

Knowledge library access and management:

- **`library_manager.py`** - Knowledge library access
- **`search_engine.py`** - Full-text search across knowledge base
- **`guide_system.py`** - Interactive guide playback

### Network Services (`/network`)

API and network functionality:

- **`api_client.py`** - HTTP API client
- **`api_audit.py`** - API usage tracking and logging
- **`websocket_client.py`** - WebSocket client for web GUI

### UI Components (`/ui`)

Reusable UI components:

- **`universal_selector.py`** - Unified file/option selector (v1.1.0)
- **`picker.py`** - Generic picker component
- **`teletext_prompt.py`** - Teletext-style prompts (v1.0.30)
- **`progress_bar.py`** - Progress indicators

### Theme System (`/theme`)

Theme management and rendering:

- **`theme_manager.py`** - Theme loading and switching
- **`color_schemes.py`** - Color scheme definitions
- **`retro_graphics.py`** - Retro graphics system (v1.1.0)

### Utilities (`/utils`)

Shared utility functions:

- **`file_utils.py`** - File operations
- **`crypto_utils.py`** - Encryption helpers (v1.1.2)
- **`validation_utils.py`** - Data validation
- **`path_utils.py`** - Path manipulation

### Interpreters (`/interpreters`)

uCODE scripting language:

- **`ucode_interpreter.py`** - uCODE execution engine
- **`ucode_debugger.py`** - Interactive debugger (v1.0.17)
- **`ucode_parser.py`** - uCODE parser

## Main Application Files

### `uDOS_main.py`
Main application loop and entry point. Handles:
- Command dispatch
- Interactive mode
- Script execution
- Error handling

### `uDOS_parser.py`
CLI to uCODE parser. Converts human-readable commands to structured data.

### `uDOS_startup.py`
Startup sequence. Handles:
- Environment initialization
- Configuration loading
- Health checks
- First-run setup

### `uDOS_logger.py`
Centralized logging system with:
- File logging (`sandbox/logs/`)
- Session logging
- Error tracking

### `config.py`
Configuration management:
- User settings
- Role configuration
- Installation type
- Feature flags

## v1.1.2 Architecture Reorganization

The v1.1.2 release reorganized core modules for better separation of concerns:

**Before v1.1.0:**
```
core/
├── uDOS_*.py (monolithic files)
└── commands/
```

**After v1.1.2:**
```
core/
├── commands/      # Specialized command handlers
├── services/      # Business logic and services
├── input/         # Input handling
├── output/        # Output formatting
├── knowledge/     # Knowledge management
├── network/       # API and networking
├── ui/            # UI components
├── theme/         # Theme system
├── utils/         # Utilities
└── interpreters/  # uCODE interpreter
```

This reorganization:
- ✅ Improved modularity and testability
- ✅ Clear separation of concerns
- ✅ Easier to navigate and maintain
- ✅ Better code reuse
- ✅ Supports dual-interface architecture (TUI + Web)

## Testing

Core system tests are located in `/memory/tests/`:

```bash
# All core tests
pytest memory/tests/test_v1_1_*.py

# Specific component tests
pytest memory/tests/test_v1_1_2_rbac.py           # RBAC system
pytest memory/tests/test_v1_1_2_command_security.py  # Security
pytest memory/tests/test_v1_1_1_server_hardening.py  # Web server
pytest memory/tests/test_v1_1_0_ai_assistant.py   # AI assistant
```

Total: 1,062 tests (100% passing)

## Development

### Adding a New Command

1. Create handler in `commands/`
2. Register in `commands/__init__.py`
3. Add tests in `memory/tests/`
4. Update documentation

Example:
```python
# core/commands/my_command_handler.py
def handle_my_command(args, context):
    """Handle MY COMMAND"""
    # Implementation
    return {"status": "success", "data": result}
```

### Adding a New Service

1. Create service in `services/`
2. Import in `services/__init__.py`
3. Add tests
4. Document API

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep functions focused (<50 lines)
- Use descriptive names

## Performance

Core system performance (v1.0.27):
- Command P90: 1.70ms
- Command P99: 5.43ms
- Startup time: 38ms
- Memory usage: <20MB

## Security

Core implements multiple security layers:

1. **RBAC** (`services/rbac_manager.py`)
   - 4 user roles
   - Permission inheritance
   - Command-level access control

2. **Encryption** (`utils/crypto_utils.py`)
   - AES-256 for Private tier
   - AES-128 for Shared tier
   - Fernet key management

3. **Installation Integrity** (`services/integrity_checker.py`)
   - SHA-256 verification
   - Core/extensions read-only in production
   - Sandbox mode for testing

4. **Command Security** (`services/security_layer.py`)
   - Explicit API/web access controls
   - Offline-first enforcement for User role
   - Command whitelist/blacklist per role

## License

See [LICENSE.txt](../LICENSE.txt) for details.

---

**Core system is the foundation of uDOS v1.1.2 with 1,062 tests ensuring reliability and security.**
