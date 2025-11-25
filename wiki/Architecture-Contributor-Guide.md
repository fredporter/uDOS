# Contributor Architecture Guide

Complete guide to uDOS v1.4.0 architecture for developers and contributors.

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Directory Structure](#directory-structure)
3. [Core Systems](#core-systems)
4. [Data Flow](#data-flow)
5. [Extension Architecture](#extension-architecture)
6. [Knowledge Bank System](#knowledge-bank-system)
7. [Command Pipeline](#command-pipeline)
8. [Contributing Guidelines](#contributing-guidelines)

---

## System Overview

### Design Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                  uDOS DESIGN PRINCIPLES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. MODULAR ARCHITECTURE                                        │
│     Core → Services → Extensions (clean separation)             │
│                                                                  │
│  2. HUMAN-READABLE CODE                                         │
│     Self-documenting, clear intent, minimal magic               │
│                                                                  │
│  3. OFFLINE-FIRST                                               │
│     Full functionality without internet/API keys                │
│                                                                  │
│  4. EXTENSIBLE BY DEFAULT                                       │
│     Plugin system for community contributions                   │
│                                                                  │
│  5. EDUCATION FOCUSED                                           │
│     Code teaches concepts, clear examples                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────┐     │
│   │  Layer 5: USER INTERFACE                             │     │
│   │  - CLI prompts (prompt_toolkit)                      │     │
│   │  - Web dashboard (Flask extensions)                  │     │
│   │  - Teletext interface (optional)                     │     │
│   └────────────────────┬─────────────────────────────────┘     │
│                        │                                        │
│   ┌────────────────────▼─────────────────────────────────┐     │
│   │  Layer 4: COMMAND PARSER                             │     │
│   │  - uDOS_parser.py (command → uCODE)                  │     │
│   │  - uCODE validator (syntax checking)                 │     │
│   │  - Variable substitution                             │     │
│   └────────────────────┬─────────────────────────────────┘     │
│                        │                                        │
│   ┌────────────────────▼─────────────────────────────────┐     │
│   │  Layer 3: COMMAND EXECUTION                          │     │
│   │  - uDOS_commands.py (command dispatcher)             │     │
│   │  - Command handlers (core/commands/)                 │     │
│   │  - Extension hooks                                   │     │
│   └────────────────────┬─────────────────────────────────┘     │
│                        │                                        │
│   ┌────────────────────▼─────────────────────────────────┐     │
│   │  Layer 2: CORE SERVICES                              │     │
│   │  - Config manager (settings/env)                     │     │
│   │  - Knowledge manager (guides/diagrams)               │     │
│   │  - Extension manager (plugins)                       │     │
│   │  - Theme system (visual customization)               │     │
│   └────────────────────┬─────────────────────────────────┘     │
│                        │                                        │
│   ┌────────────────────▼─────────────────────────────────┐     │
│   │  Layer 1: FOUNDATION                                 │     │
│   │  - File I/O (knowledge/, memory/)                    │     │
│   │  - Logging (structured logging)                      │     │
│   │  - Error handling (exceptions)                       │     │
│   └──────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Complete File Tree

```
uDOS/
├── core/                           # Core system (required)
│   ├── __init__.py
│   ├── config.py                   # Unified configuration manager
│   ├── uDOS_main.py               # Main entry point & event loop
│   ├── uDOS_parser.py             # Command parser (text → uCODE)
│   ├── uDOS_commands.py           # Command dispatcher
│   ├── uDOS_grid.py               # Panel/viewport system
│   ├── uDOS_logger.py             # Logging configuration
│   ├── uDOS_server.py             # HTTP server (optional)
│   ├── uDOS_startup.py            # Initialization sequence
│   │
│   ├── commands/                   # Command handlers
│   │   ├── __init__.py
│   │   ├── generate_commands.py   # GENERATE command family
│   │   ├── convert_commands.py    # CONVERT command family
│   │   ├── refresh_commands.py    # REFRESH command (v1.4.0)
│   │   ├── manage_commands.py     # File/content management
│   │   ├── search_commands.py     # Search & filter
│   │   └── system_commands.py     # System operations
│   │
│   ├── interpreters/               # Language interpreters
│   │   └── ucode_interpreter.py   # uCODE execution engine
│   │
│   ├── services/                   # Core services
│   │   ├── knowledge_manager.py   # Knowledge bank access
│   │   ├── theme_manager.py       # Theme system
│   │   └── session_manager.py     # Session persistence
│   │
│   ├── theme/                      # Theme system
│   │   ├── themes.py              # Theme definitions
│   │   └── system.css             # UI components
│   │
│   ├── ucode/                      # uCODE system (v1.4.0)
│   │   ├── __init__.py
│   │   ├── validator.py           # Syntax validation
│   │   └── parser.py              # uCODE parsing
│   │
│   └── utils/                      # Utilities
│       ├── file_utils.py          # File operations
│       ├── text_utils.py          # Text processing
│       └── diagram_utils.py       # ASCII/diagram helpers
│
├── extensions/                     # Extension system
│   ├── core/                       # Bundled extensions
│   │   ├── ok-assist/             # AI content generation
│   │   │   ├── ok_assist.py       # Main API
│   │   │   ├── enhanced_prompts.py # Prompt engineering (v1.4.0)
│   │   │   ├── ARCHITECTURE.md    # Extension architecture
│   │   │   └── examples/          # Usage examples
│   │   │
│   │   ├── extension_manager.py   # Extension installation
│   │   ├── extension_dev_tools.py # Development tools
│   │   └── extension_metadata_manager.py # Metadata handling
│   │
│   ├── bundled/                    # Pre-installed (git tracked)
│   │   └── web/                   # Web interfaces
│   │       ├── dashboard/         # System dashboard
│   │       ├── teletext/          # Retro interface
│   │       └── system-desktop/    # Classic desktop UI
│   │
│   ├── cloned/                     # External deps (git ignored)
│   │   ├── typo/                  # Markdown editor
│   │   ├── micro/                 # Terminal editor
│   │   └── monaspace-fonts/       # Fonts
│   │
│   ├── templates/                  # Extension templates
│   │   ├── web_extension/
│   │   ├── cli_extension/
│   │   └── service_extension/
│   │
│   └── setup/                      # Installation scripts
│       ├── setup_all.sh
│       ├── setup_typo.sh
│       └── setup_micro.sh
│
├── knowledge/                      # Knowledge bank (read-only system)
│   ├── README.md                   # Master index
│   ├── water/                      # Water (26 guides)
│   ├── fire/                       # Fire (20 guides)
│   ├── shelter/                    # Shelter (20 guides)
│   ├── food/                       # Food (23 guides)
│   ├── navigation/                 # Navigation (20 guides)
│   ├── medical/                    # Medical (27 guides)
│   ├── tools/                      # Tools (15 guides)
│   ├── communication/              # Communication (15 guides)
│   ├── diagrams/                   # Multi-format diagrams
│   │   ├── README.md              # Diagram index
│   │   ├── water/
│   │   ├── fire/
│   │   └── ...
│   ├── system/                     # System knowledge
│   │   ├── commands/              # Command definitions
│   │   ├── themes/                # Theme configs
│   │   └── templates/             # Content templates
│   └── demos/                      # Examples & tutorials
│
├── memory/                         # User workspace (git ignored)
│   ├── user/                       # User-specific data
│   │   ├── user.json              # User settings
│   │   └── profile.json           # User profile
│   ├── config/                     # Runtime configuration
│   │   └── settings.json
│   ├── logs/                       # System logs
│   │   ├── udos.log
│   │   └── command_history.db
│   ├── sessions/                   # Session persistence
│   ├── workflow/                   # uCODE scripts
│   │   ├── startup_options.uscript
│   │   ├── content_generation.uscript
│   │   ├── housekeeping_cleanup.uscript
│   │   └── mission_templates.uscript
│   ├── missions/                   # Mission tracking
│   ├── sandbox/                    # Experimental workspace
│   └── themes/                     # Custom themes
│
├── docs/                           # Documentation
│   ├── UCODE_LANGUAGE.md          # uCODE specification (v1.4.0)
│   ├── REFRESH_COMMAND.md         # REFRESH system docs (v1.4.0)
│   ├── DIAGRAM_CONTROLS.md        # Diagram generation (v1.4.0)
│   └── TELETEXT_COLORS.md         # Teletext system (v1.4.0)
│
├── wiki/                           # Wiki documentation
│   ├── Home.md
│   ├── Getting-Started.md
│   ├── Tutorial-Getting-Started.md # Interactive tutorial (v1.4.0)
│   ├── API-Reference.md           # API docs (v1.4.0)
│   ├── Architecture.md            # This file
│   ├── Command-Reference.md
│   ├── uCODE-Language.md
│   └── ...
│
├── .env                            # Environment variables
├── .gitignore
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── start_udos.sh                   # Launch script
├── ROADMAP.MD                      # Development roadmap
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.MD
```

---

## Core Systems

### 1. Configuration System (config.py)

**Purpose**: Unified configuration management for .env, user.json, and runtime state.

```python
┌─────────────────────────────────────────────────────────────────┐
│                  CONFIGURATION HIERARCHY                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Environment Variables (.env)                                │
│     - API keys (GEMINI_API_KEY, etc.)                          │
│     - System settings (ports, paths)                           │
│     - Auto-loaded on startup                                   │
│                                                                  │
│  2. User Settings (memory/user/user.json)                      │
│     - Preferences (theme, workspace)                           │
│     - User profile data                                        │
│     - Persisted across sessions                                │
│                                                                  │
│  3. Runtime State (in-memory)                                  │
│     - Current session data                                     │
│     - Temporary variables                                      │
│     - Cleared on restart                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Classes:**
- `Config` - Main configuration manager
- Methods: `get()`, `set()`, `get_env()`, `set_env()`, `save()`

### 2. Command System

**Flow:**

```
User Input
    │
    ▼
┌──────────────────┐
│  uDOS_parser.py  │  Parse text → uCODE
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ucode/validator  │  Validate syntax
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│uDOS_commands.py  │  Dispatch to handler
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Command Handler  │  Execute (core/commands/)
└────────┬─────────┘
         │
         ▼
    Response
```

**Command Handler Pattern:**

```python
# core/commands/example_commands.py

def handle_example_command(params, context):
    """
    Handle EXAMPLE command.

    Args:
        params: List of command parameters
        context: Execution context (config, workspace, etc.)

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'data': Any
        }
    """
    # 1. Validate parameters
    if len(params) < 2:
        return {
            'success': False,
            'message': 'EXAMPLE requires at least 2 parameters'
        }

    # 2. Extract parameters
    action = params[0]
    target = params[1]
    options = params[2:] if len(params) > 2 else []

    # 3. Execute logic
    try:
        result = perform_action(action, target, options)
        return {
            'success': True,
            'message': f'✓ {action} completed',
            'data': result
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'✗ Error: {str(e)}'
        }

# Register in uDOS_commands.py
COMMAND_HANDLERS = {
    'EXAMPLE': handle_example_command,
    # ... other commands
}
```

### 3. Knowledge Bank System

**Structure:**

```
knowledge/
├── {category}/          # 8 categories
│   ├── README.md        # Category index
│   ├── guide1.md
│   ├── guide2.md
│   └── ...
├── diagrams/
│   ├── {category}/
│   │   ├── diagram_ascii.txt
│   │   ├── diagram_teletext.html
│   │   ├── diagram_technical.svg
│   │   └── diagram_organic.svg
│   └── README.md
└── README.md            # Master index
```

**Guide Frontmatter:**

```markdown
---
title: "Guide Title"
category: "water"
tags: ["purification", "emergency"]
difficulty: "beginner"
time_required: "15 minutes"
author: "OK Assist"
version: "1.0.0"
generated: "2025-11-25"
---

# Guide Content
...
```

### 4. Extension System

**Extension Lifecycle:**

```
┌─────────────────────────────────────────────────────────────────┐
│                  EXTENSION LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DISCOVERY                                                   │
│     → Scan extensions/ directory                                │
│     → Read extension.json metadata                              │
│     → Check compatibility                                        │
│                                                                  │
│  2. VALIDATION                                                  │
│     → Verify required files exist                               │
│     → Check uDOS version compatibility                          │
│     → Validate dependencies                                     │
│                                                                  │
│  3. INITIALIZATION                                              │
│     → Load extension module                                     │
│     → Call initialize(udos_context)                            │
│     → Register commands/hooks                                   │
│                                                                  │
│  4. EXECUTION                                                   │
│     → Handle registered commands                                │
│     → Respond to system hooks                                   │
│     → Maintain extension state                                  │
│                                                                  │
│  5. CLEANUP                                                     │
│     → Call cleanup() on shutdown                                │
│     → Save extension state                                      │
│     → Release resources                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  COMPLETE REQUEST FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User types: GENERATE|guide|water|filtration                    │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────┐                                               │
│  │ uDOS_main.py │  Read input from prompt                       │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ uDOS_parser  │  Parse: GENERATE|guide|water|filtration       │
│  │              │  →  [GENERATE|guide|water|filtration]         │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ uCODE        │  Validate syntax and parameters               │
│  │ Validator    │  Check: GENERATE exists, params valid         │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ uDOS         │  Dispatch to handler                          │
│  │ Commands     │  → handle_generate_command()                  │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ Generate     │  Execute generation logic                     │
│  │ Handler      │  params: ['guide', 'water', 'filtration']     │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ OK Assist    │  Call AI service (if available)               │
│  │ Extension    │  Generate content for water filtration        │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ Knowledge    │  Save to knowledge/water/filtration.md        │
│  │ Manager      │  Update index and metadata                    │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ Response     │  Return success message                       │
│  │              │  "✓ Generated water filtration guide"         │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  Display to user in CLI                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Contributing Guidelines

### Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/uDOS.git
   cd uDOS
   ```
3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Setup development environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Code Style

**Python Code:**
- PEP 8 compliant
- Type hints where appropriate
- Docstrings for all functions/classes
- Maximum line length: 100 characters

**Example:**

```python
def process_command(command: str, context: dict) -> dict:
    """
    Process a uDOS command and return result.

    Args:
        command: Raw command string from user
        context: Execution context containing config, workspace, etc.

    Returns:
        dict: Result with 'success', 'message', and optional 'data'

    Raises:
        ValueError: If command is malformed
        RuntimeError: If execution fails
    """
    # Implementation
    pass
```

### Adding a New Command

1. **Create handler** in `core/commands/`:

```python
# core/commands/my_commands.py

def handle_my_command(params, context):
    """Handle MY_COMMAND."""
    # Validate
    if not params:
        return {'success': False, 'message': 'Parameters required'}

    # Execute
    result = do_something(params)

    # Return
    return {
        'success': True,
        'message': f'✓ Completed: {result}',
        'data': result
    }
```

2. **Register in dispatcher**:

```python
# core/uDOS_commands.py

from core.commands.my_commands import handle_my_command

COMMAND_HANDLERS = {
    # ... existing commands
    'MY_COMMAND': handle_my_command,
}
```

3. **Add to uCODE validator**:

```python
# core/ucode/validator.py

COMMANDS = {
    # ... existing commands
    'MY_COMMAND': {
        'required': ['param1'],
        'params': ['param1', 'param2', 'options'],
        'description': 'Description of MY_COMMAND'
    },
}
```

4. **Document in wiki**:
   - Add to `wiki/Command-Reference.md`
   - Include examples and use cases
   - Note any dependencies

### Testing

```bash
# Run validator tests
python -m pytest core/ucode/test_validator.py

# Test specific command
python -m core.ucode.validator --lint memory/workflow/test_script.uscript

# Manual testing
./start_udos.sh
# Then test your command
```

### Pull Request Process

1. **Update documentation**
   - Add to CHANGELOG.md
   - Update relevant wiki pages
   - Include code examples

2. **Commit messages**
   ```
   type(scope): brief description

   Longer explanation if needed.

   - Bullet points for details
   - Reference issues: #123
   ```

   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

3. **Submit PR**
   - Clear title and description
   - Link related issues
   - Screenshots if UI changes
   - Request review

### Extension Development

See [API-Reference.md](API-Reference.md) for complete API documentation.

**Quick Start:**

```bash
# Use dev tools to create template
python -m extensions.core.extension_dev_tools create my-extension --type web

# Structure created:
my-extension/
├── extension.json
├── server.py
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
└── templates/
    └── index.html
```

---

## Additional Resources

- **API Reference**: [API-Reference.md](API-Reference.md)
- **Command Reference**: [Command-Reference.md](Command-Reference.md)
- **uCODE Language**: [uCODE-Language.md](uCODE-Language.md)
- **Getting Started**: [Tutorial-Getting-Started.md](Tutorial-Getting-Started.md)
- **Project Roadmap**: [../ROADMAP.MD](../ROADMAP.MD)

---

**Version:** 1.4.0
**Last Updated:** November 25, 2025
**Maintainer:** Fred Porter
