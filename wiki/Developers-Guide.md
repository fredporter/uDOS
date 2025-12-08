# Developers Guide

Complete guide for uDOS developers and contributors covering architecture, APIs, workflows, and best practices.

**Version:** v1.2.20 (Workflow Management System)
**Status:** Production Ready
**Last Updated:** December 2025

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Organization](#project-organization)
3. [Architecture Overview](#architecture-overview)
4. [Development Workflow](#development-workflow)
5. [DEV MODE](#dev-mode)
6. [API Reference](#api-reference)
7. [Extension Development](#extension-development)
8. [Best Practices](#best-practices)
9. [Contributing Guidelines](#contributing-guidelines)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv)
- VS Code (recommended)

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Launch uDOS
./start_udos.sh
```

### VS Code Workspace

Open `uDOS.code-workspace` in VS Code for:
- Integrated task runner
- Automated testing
- Development logging
- Extension debugging

**Key Tasks:**
- `Check Virtual Environment` - Verify venv active
- `Run uDOS Interactive` - Launch main application
- `Run Shakedown Test` - Core functionality tests
- `Run Pytest` - Full test suite

---

## Project Organization

The uDOS project follows a structured organization that promotes modularity, clarity, and ease of maintenance.

### Directory Structure

#### Core System
```
core/                           # Core system (required)
├── __init__.py
├── config.py                   # Unified configuration manager
├── uDOS_main.py               # Main entry point & event loop
├── uDOS_parser.py             # Command parser (text → uCODE)
├── uDOS_commands.py           # Command dispatcher
├── uDOS_grid.py               # Panel/viewport system
├── uDOS_logger.py             # Logging configuration
├── uDOS_startup.py            # Initialization sequence
├── commands/                   # Command handlers
│   ├── generate_commands.py   # GENERATE command family
│   ├── convert_commands.py    # CONVERT command family
│   ├── manage_commands.py     # File/content management
│   ├── search_commands.py     # Search & filter
│   └── system_commands.py     # System operations
├── interpreters/               # Language interpreters
│   └── ucode_interpreter.py   # uCODE execution engine
├── services/                   # Core services
│   ├── knowledge_manager.py   # Knowledge bank access
│   ├── theme_manager.py       # Theme system
│   └── session_manager.py     # Session persistence
└── utils/                      # Utilities
    ├── file_utils.py          # File operations
    ├── text_utils.py          # Text processing
    └── diagram_utils.py       # ASCII/diagram helpers
```

#### Data & Graphics
```
core/data/                      # Core data files
├── graphics/                   # Graphics system (v1.1.1+)
│   ├── blocks/                # Teletext block library
│   │   ├── teletext.json      # Core blocks (solid, arrows, etc.)
│   │   ├── borders.json       # Border styles (heavy, chunky, etc.)
│   │   ├── patterns.json      # Fill patterns
│   │   └── maps.json          # Map terrain patterns
│   ├── templates/             # Diagram templates
│   │   ├── flow_diagram.json  # Vertical process flows
│   │   ├── tree_diagram.json  # Hierarchical structures
│   │   └── grid_diagram.json  # Comparison tables
│   ├── compositions/          # Example diagrams
│   │   ├── water_purification_flow.txt
│   │   ├── shelter_hierarchy_tree.txt
│   │   └── fire_methods_grid.txt
│   └── README.md              # Graphics system docs
├── themes/                     # Theme definitions
├── templates/                  # Content templates
└── config/                     # System configuration
```

#### Extensions
```
extensions/                     # Extension system
├── assistant/                  # AI assistant (Gemini integration)
│   ├── assistant_handler.py   # Main handler
│   └── prompts/               # Prompt templates
├── assets/                     # Shared assets
│   ├── fonts/                 # Font files (Mallard, etc.)
│   ├── icons/                 # Icon sets
│   └── data/                  # Shared data files
├── core/                       # Core extensions
│   ├── dashboard/             # System dashboard (web UI)
│   ├── extension_manager.py   # Extension installation
│   └── server_manager.py      # Server management
├── play/                       # Gameplay extensions
│   ├── map_engine/            # Map rendering & TILE system
│   ├── xp_system/             # XP tracking
│   └── data/                  # Geography data (cities, etc.)
├── web/                        # Web interfaces
│   ├── teletext/              # Teletext rendering
│   └── terminal/              # Terminal UI
├── bundled/                    # Pre-installed extensions
├── cloned/                     # External deps (git ignored)
└── setup/                      # Installation scripts
```

#### Knowledge & Documentation
```
knowledge/                      # Knowledge bank (read-only system)
├── water/                      # Water (25 guides with diagrams)
├── fire/                       # Fire (20 guides with diagrams)
├── shelter/                    # Shelter (20 guides with diagrams)
├── food/                       # Food (22 guides with diagrams)
├── navigation/                 # Navigation (20 guides with diagrams)
├── medical/                    # Medical (26 guides with diagrams)
├── skills/                     # Skills & techniques
├── making/                     # Crafting & tools
├── checklists/                 # Reference checklists
├── reference/                  # Reference materials
└── demos/                      # Examples & tutorials
# Note: All diagrams are now embedded as ASCII/teletext in .md files

wiki/                           # Wiki documentation
├── Home.md
├── Getting-Started.md
├── Tutorial-Getting-Started.md
├── Command-Reference.md
├── Architecture.md
└── ...

docs/                           # Technical documentation
├── UCODE_LANGUAGE.md
├── REFRESH_COMMAND.md
└── DIAGRAM_CONTROLS.md
```

#### User Workspace
```
memory/                         # User workspace (git ignored)
├── user/                       # User-specific data
├── config/                     # Runtime configuration
├── logs/                       # System logs
├── sessions/                   # Session persistence
├── workflow/                   # uCODE scripts
├── missions/                   # Mission tracking
├── sandbox/                    # Experimental workspace
└── themes/                     # Custom themes
```

### Organization Principles

#### 1. Modularity
- Each directory serves a specific purpose
- Clear separation of concerns
- Minimal dependencies between components

#### 2. Documentation
- Documentation lives close to code
- Multiple formats for different needs
- Comprehensive examples

#### 3. Testing
- Centralized test suite in `memory/tests/`
- Integration with CI/CD
- Example-driven development

#### 4. Extension System
- Clear extension template structure
- Shared core components in `extensions/core/`
- Easy third-party integration

---

## Architecture Overview

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

### Command Processing Flow

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
│ uDOS_commands.py │  Dispatch to handler
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Command Handler  │  Execute command
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Core Services    │  Knowledge, Config, etc.
└────────┬─────────┘
         │
         ▼
    Result
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Input                                                     │
│      ↓                                                          │
│  Parser (validate, normalize)                                  │
│      ↓                                                          │
│  Command Dispatcher                                            │
│      ↓                                                          │
│  ┌─────────────┬──────────────┬──────────────┐               │
│  │ Config      │ Knowledge    │ Extensions   │               │
│  │ Manager     │ Manager      │ Manager      │               │
│  └─────────────┴──────────────┴──────────────┘               │
│      ↓              ↓               ↓                          │
│  ┌─────────────┬──────────────┬──────────────┐               │
│  │ .env        │ knowledge/   │ extensions/  │               │
│  │ user.json   │ memory/      │ cloned/      │               │
│  └─────────────┴──────────────┴──────────────┘               │
│      ↓                                                          │
│  Result (formatted output)                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Development Workflow

### Development Process

#### 1. Setup Development Environment
```bash
# Open workspace
code uDOS.code-workspace

# Check virtual environment
# Task: "Check Virtual Environment"

# Run shakedown tests
# Task: "Run Shakedown Test"
```

#### 2. Development Phase
- Implement features incrementally
- Follow `/dev/` workspace conventions (see `.github/copilot-instructions.md`)
- Run tests frequently: `pytest memory/ucode/ -v`
- Use structured logging via `core/uDOS_logger.py`
- Update ROADMAP.md in `dev/roadmap/` as work progresses

#### 3. Testing & Validation

**Core Tests:**
```bash
# Run full test suite
pytest memory/ucode/ -v

# Run shakedown test
./start_udos.sh memory/tests/shakedown.upy

# Check for errors
# In uDOS: STATUS
```

**Manual Testing:**
- Test new commands interactively
- Verify file operations
- Check extension integration
- Validate uPY script execution

#### 4. Documentation Updates

**Required updates:**
1. Update `wiki/Command-Reference.md` if new commands added
2. Update relevant wiki pages for feature changes
3. Add examples to `memory/ucode/examples/` if applicable
4. Update `CHANGELOG.md` with version notes
5. Keep `dev/roadmap/ROADMAP.md` current

### Testing Integration

#### Fast Shakedowns
```bash
# Core functionality
# Task: "Shakedown Terminal Core"

# APAC mapping
# Task: "Map APAC Center Sanity"

# Full pytest suite
# Task: "Run Pytest"
```

#### Manual Testing
After automated tests, perform manual verification:
1. Launch uDOS interactive: `./start_udos.sh`
2. Test new features manually
3. Verify error handling
4. Check output formatting

### Logging & Documentation

#### Dev Logger Usage
```python
from core.dev_logger import quick_dev_log

# Log development progress
quick_dev_log("AUS-BNE", 3, "FEATURE implement", 0, 150,
              "added MAP CELL command", with_user_ctx=True)
```

#### Copilot Summaries
```bash
# Generate summary for current work
python -m core.copilot_summary \
  "core/commands/map_handler.py: add CELL lookup functionality" \
  150 0 AUS-BNE 3
```

#### Log Format
```
2025-11-02T13:47:19Z | AUS-BNE | Z3 | FEATURE implement | 0 | 150 |
  added MAP CELL command | ctx: workspace=default theme=FOUNDATION
```

### Operator Responsibilities

#### During Development
- Monitor dev logs: `tail -f sandbox/logs/dev-*.log`
- Review automated test results
- Validate feature completeness against round goals

#### At Round Completion
1. **Run all round checklist tasks**
2. **Manual feature verification**
3. **Wiki documentation update**
4. **Final quality review**
5. **Sign off on round completion**

#### Quality Checkpoints
- Are all planned features implemented?
- Do automated tests pass?
- Is documentation updated?
- Are any edge cases uncovered?
- Does the user experience feel polished?

### VS Code Task Reference

| Task Name | Purpose | When to Use |
|-----------|---------|-------------|
| Check Virtual Environment | Verify venv active | Before any Python commands |
| Shakedown Terminal Core | Test core commands | After major changes |
| Map APAC Center Sanity | Test mapping system | After map-related changes |
| Run Pytest | Full test suite | Before round completion |
| Dev Round: v1.0.x Check | Round completion checklist | At end of each round |
| Update Wiki: Current Dev Round | Documentation reminder | After round completion |
| Copilot: Stamp Summary Line | Generate dev summary | After significant work |

### Success Criteria

A dev round is considered **complete** when:
- ✅ All planned features implemented
- ✅ Automated tests pass
- ✅ Manual testing validates functionality
- ✅ Operator checklist completed
- ✅ Wiki documentation updated
- ✅ Dev logs show clean feature implementation
- ✅ No blocking bugs identified

---

## DEV MODE

### Overview

DEV MODE is a secure development environment for uDOS master users. It provides:

- **Master User Authentication** - Password-based access control
- **Dangerous Command Protection** - Whitelisting system for risky operations
- **Session Management** - Auto-save, restore, timeout (1 hour)
- **Activity Logging** - Comprehensive audit trail (text + JSON)
- **Development Tools** - Hot reload, debugging, system access

### When to Use DEV MODE

✅ **Use DEV MODE for:**
- System configuration changes
- Database operations (DELETE, WIPE, RESET)
- Direct code execution (EXECUTE, SHELL, EVAL)
- Extension development and testing
- Advanced troubleshooting

❌ **Don't Use DEV MODE for:**
- Regular daily usage
- Learning uDOS commands
- Creating content (guides, diagrams, checklists)
- Standard knowledge bank operations

### Quick Start

**1. Enable DEV MODE**
```
uDOS> DEV MODE ON
🔐 Master user password: ********
✅ DEV MODE activated
🔧 DEV>
```

**2. Check Status**
```
🔧 DEV> DEV MODE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DEV MODE Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:           ✅ ACTIVE
User:             fred (master)
Session Started:  2025-11-25 14:30:22
Commands Run:     42
Session File:     sandbox/logs/dev_mode_session.json

⚠️  Dangerous commands are ENABLED. Use caution.
```

**3. Disable DEV MODE**
```
🔧 DEV> DEV MODE OFF
✅ DEV MODE deactivated
Session saved to: sandbox/logs/dev_mode_session.json
uDOS>
```

### Master User Setup

#### Configuration (.env)

Add these lines to your `.env` file:

```bash
# Master User Configuration (DEV MODE)
UDOS_MASTER_USER=your_username
UDOS_MASTER_PASSWORD=your_secure_password
```

**Important:**
- Use a **strong password** (12+ characters, mixed case, numbers, symbols)
- Keep `.env` secure and **never commit to git** (already in .gitignore)
- Password is hashed with SHA256 before storage

#### Verification

Test your master user configuration:

```bash
# In uDOS
uDOS> DEV MODE ON
🔐 Master user password: ********

# If successful:
✅ DEV MODE activated
🔧 DEV>

# If failed:
❌ Authentication failed. Incorrect password or not configured as master user.
```

### Commands

#### DEV MODE ON

**Description:** Enable DEV MODE (master user only)

**Syntax:** `DEV MODE ON`

**Behavior:**
- Prompts for master user password
- Verifies credentials against .env configuration
- Activates session with 1-hour timeout
- Changes prompt to `🔧 DEV>`
- Enables dangerous commands

#### DEV MODE OFF

**Description:** Disable DEV MODE and save session

**Syntax:** `DEV MODE OFF`

**Behavior:**
- Saves current session to disk
- Logs activity summary
- Resets prompt to `uDOS>`
- Blocks dangerous commands

#### DEV MODE STATUS

**Description:** Show current DEV MODE status

**Syntax:** `DEV MODE STATUS`

**Output:** Displays session info, uptime, command count, enabled dangerous commands

#### DEV MODE HELP

**Description:** Show DEV MODE help information

**Syntax:** `DEV MODE HELP`

### Permission System

#### Dangerous Commands

These commands require DEV MODE to be active:

| Command | Risk Level | Description |
|---------|-----------|-------------|
| `DELETE` | 🔴 HIGH | Permanently delete files/data |
| `DESTROY` | 🔴 HIGH | Remove database records |
| `REPAIR` | 🟡 MEDIUM | Auto-repair system (can overwrite) |
| `RESET` | 🔴 HIGH | Reset configuration to defaults |
| `WIPE` | 🔴 HIGH | Clear entire memory/database |
| `EXECUTE` | 🔴 HIGH | Run arbitrary code |
| `SHELL` | 🔴 HIGH | Execute shell commands |
| `EVAL` | 🔴 HIGH | Evaluate Python expressions |
| `IMPORT` | 🟡 MEDIUM | Load external modules |
| `LOAD` | 🟡 MEDIUM | Load and execute scripts |

#### Permission Checks

When DEV MODE is **OFF:**
```
uDOS> DELETE knowledge/test.md
❌ Permission denied: DELETE requires DEV MODE
   Use 'DEV MODE ON' to enable (master user only)
```

When DEV MODE is **ON:**
```
🔧 DEV> DELETE knowledge/test.md
⚠️  DANGEROUS OPERATION: DELETE
Continue? (yes/no): yes
✅ Deleted: knowledge/test.md
```

### Session Management

#### Session Lifecycle

1. **Activation** - `DEV MODE ON` creates new session
2. **Activity** - Commands logged, timeout refreshed
3. **Persistence** - Auto-saved to `dev_mode_session.json`
4. **Timeout** - 1 hour inactivity = auto-disable
5. **Deactivation** - `DEV MODE OFF` saves and exits

#### Session File

**Location:** `sandbox/logs/dev_mode_session.json`

**Format:**
```json
{
  "is_active": true,
  "user": "fred",
  "session_start": "2025-11-25T14:30:22Z",
  "commands_run": 42,
  "last_activity": "2025-11-25T14:58:10Z",
  "timeout_minutes": 60
}
```

#### Timeout Behavior

**Default:** 1 hour (60 minutes)

**Configurable Timeout:**
```bash
# In .env
UDOS_DEV_MODE_TIMEOUT=120  # 2 hours

# Or disable timeout (not recommended)
UDOS_DEV_MODE_TIMEOUT=0
```

### Security

#### Authentication

**Method:** Password-based with SHA256 hashing

**Process:**
1. User enters password
2. System hashes input with SHA256
3. Compares hash against `UDOS_MASTER_PASSWORD` in .env
4. Grants access only on exact match

#### Best Practices

✅ **DO:**
- Use strong passwords (12+ characters)
- Keep `.env` secure and private
- Log out when finished (`DEV MODE OFF`)
- Review activity logs regularly
- Limit DEV MODE sessions to necessary operations

❌ **DON'T:**
- Share master password
- Commit `.env` to version control
- Leave DEV MODE active unattended
- Use simple/common passwords
- Run untrusted code in DEV MODE

### Activity Logging

#### Log Files

**Text Log:** `sandbox/logs/dev_mode.log`
```
[2025-11-25 14:30:22] DEV MODE ACTIVATED - User: fred
[2025-11-25 14:32:15] COMMAND: DELETE knowledge/test.md
[2025-11-25 14:35:08] COMMAND: RESET config --force
[2025-11-25 14:58:10] DEV MODE DEACTIVATED - Session: 42 commands, 28 min
```

**JSON Log:** `sandbox/logs/dev_mode.json`
```json
[
  {
    "timestamp": "2025-11-25T14:30:22Z",
    "event": "DEV_MODE_ACTIVATED",
    "user": "fred",
    "session_id": "session-123"
  }
]
```

---

## API Reference

### Core APIs

#### Config - Unified Configuration Manager

```python
from core.config import Config

# Initialize configuration
config = Config()

# Environment variables (.env)
api_key = config.get_env('GEMINI_API_KEY')
config.set_env('CUSTOM_KEY', 'value')
config.save_env()

# User settings (user.json)
username = config.get('username', 'default')
config.set('theme', 'synthwave')
config.save()

# Runtime state
config.runtime['current_session'] = 'session-123'
```

**Key Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `get_env(key, default=None)` | Get environment variable | str/None |
| `set_env(key, value)` | Set environment variable | None |
| `save_env()` | Save .env file | bool |
| `get(key, default=None)` | Get user setting | Any |
| `set(key, value)` | Set user setting | None |
| `save()` | Save user.json | bool |
| `get_all_config()` | Get complete config | dict |

**Environment Keys:**

```python
ENV_KEYS = {
    'GEMINI_API_KEY': 'Gemini AI API Key',
    'OPENROUTER_API_KEY': 'OpenRouter API Key',
    'ANTHROPIC_API_KEY': 'Anthropic API Key',
    'OPENAI_API_KEY': 'OpenAI API Key',
    'UDOS_INSTALLATION_ID': 'Installation ID',
    'DEFAULT_WORKSPACE': 'Default workspace',
    'DEFAULT_MODEL': 'Default AI model',
    'AUTO_START_WEB': 'Auto-start web dashboard',
    'AUTO_START_SERVER': 'Auto-start HTTP server',
    'HTTP_SERVER_PORT': 'HTTP server port',
    'THEME': 'Color theme',
    'MAX_SESSION_HISTORY': 'Max session history',
    'AUTO_SAVE_SESSION': 'Auto-save session',
}
```

**Note**: `UDOS_USERNAME` was removed in v1.1.6 - username now lives ONLY in `user.json` (`USER_PROFILE.NAME`).

### Extension System

#### ExtensionManager - Install & Verify Extensions

```python
from extensions.core.extension_manager import ExtensionManager

# Initialize manager
manager = ExtensionManager()

# Check installation status
is_installed = manager.check_extension_installed('typo')

# Install extension
success, message = manager.install_extension('micro', quiet=True)

# Get all extension statuses
statuses = manager.get_extension_status()
# Returns: {'typo': True, 'micro': False, ...}

# Install missing extensions
results = manager.install_missing_extensions(quiet=True)

# Verify all extensions
all_ok, details = manager.verify_all_extensions()

# Get extension info
info = manager.get_extension_info('typo')
```

**Extension Types:**
- `typo` - Web markdown editor
- `micro` - Terminal text editor
- `monaspace` - Monaspace fonts
- `cmd` - Web terminal interface

#### ExtensionDevTools - Create Extensions

```python
from extensions.core.extension_dev_tools import ExtensionDevTools

# Initialize dev tools
dev = ExtensionDevTools()

# Create new extension from template
success = dev.create_extension_template(
    name="my-extension",
    ext_type="web",
    description="My custom extension",
    author="Your Name"
)

# Validate extension
is_valid, errors = dev.validate_extension("my-extension")

# Package extension for distribution
success = dev.package_extension("my-extension")

# Test extension
results = dev.test_extension("my-extension")
```

**Extension Template Structure (Web):**

```
my-extension/
├── extension.json          # Metadata
├── server.py              # HTTP server
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── assets/
└── templates/
    └── index.html
```

**extension.json Schema:**

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "type": "web",
  "author": "Your Name",
  "description": "Extension description",
  "entry_point": "server.py",
  "dependencies": [],
  "permissions": ["read", "write"],
  "config": {
    "port": 8080,
    "auto_start": false
  }
}
```

### Knowledge Bank API

#### Generating Content

```python
from extensions.core.ok_assist.ok_assist import OKAssist

# Initialize OK Assist
assistant = OKAssist()

# Generate survival guide
guide = assistant.generate_guide(
    topic="water purification",
    category="water",
    complexity="detailed",
    format="markdown"
)

# Generate diagram (multi-format)
diagrams = assistant.generate_diagram(
    topic="fire triangle",
    style="technical",
    perspective="isometric",
    formats=["ascii", "teletext", "svg-technical", "svg-organic"]
)

# Batch generation
results = assistant.batch_generate(
    topics=["topic1", "topic2", "topic3"],
    category="water",
    complexity="simple",
    template="guide_template.md"
)
```

#### Knowledge Organization

```python
from core.knowledge.knowledge_manager import KnowledgeManager

# Initialize knowledge manager
km = KnowledgeManager()

# Search knowledge bank
results = km.search(
    query="water filtration",
    category="water",
    complexity="detailed",
    tags=["purification", "treatment"]
)

# Get guide metadata
metadata = km.get_guide_metadata("water/boiling.md")

# List all guides in category
guides = km.list_category_guides("water")

# Get cross-references
refs = km.get_cross_references("water/boiling.md")

# Add guide to knowledge bank
km.add_guide(
    content=guide_content,
    metadata={
        "title": "Water Purification",
        "category": "water",
        "tags": ["purification", "safety"],
        "complexity": "detailed"
    }
)
```

### uCODE Scripting API

#### UCodeValidator - Syntax Validation

```python
from core.ucode.validator import UCodeValidator

# Initialize validator
validator = UCodeValidator()

# Validate script file
is_valid, errors = validator.validate_file("script.upy")

# Lint script with details
stats = validator.lint("script.upy")
# Returns: {
#   'lines': 100,
#   'commands': 25,
#   'variables': 5,
#   'comments': 10,
#   'errors': [],
#   'warnings': []
# }

# Validate script content
script_content = "PRINT('Hello world')"
is_valid, errors = validator.validate_script(script_content)

# Strict mode (warnings as errors)
is_valid, errors = validator.validate_file("script.upy", strict=True)
```

#### UCodeParser - Parse Scripts

```python
from core.ucode.parser import UCodeParser

# Initialize parser
parser = UCodeParser()

# Parse script file
commands = parser.parse_file("script.upy")

# Parse individual command
command = parser.parse_command("GENERATE SVG water purification")
# Returns: {
#   'command': 'GENERATE',
#   'subcommand': 'SVG',
#   'params': ['water', 'purification'],
#   'line': 1
# }

# Extract variables
variables = parser.extract_variables(script_content)

# Get YAML frontmatter
metadata = parser.parse_frontmatter("script.upy")
```

### OK Assist (AI) API

#### OKAssist - AI Content Generation

```python
from extensions.core.ok_assist.ok_assist import OKAssist

# Initialize with API key
assistant = OKAssist(api_key="your-gemini-key")

# Generate text content
response = assistant.generate_text(
    prompt="Explain water purification",
    max_tokens=2000,
    temperature=0.7
)

# Generate with enhanced prompts
response = assistant.generate_enhanced(
    topic="fire starting",
    category="fire",
    style="technical",
    perspective="isometric",
    annotations=["labels", "dimensions"]
)

# Multi-format diagram generation
diagrams = assistant.generate_multi_format(
    topic="shelter construction",
    formats=["ascii", "teletext", "svg-technical"]
)

# Batch processing
results = assistant.batch_process(
    items=["topic1", "topic2", "topic3"],
    operation="generate_guide",
    category="water",
    parallel=True
)
```

**Enhanced Prompt Controls:**

```python
# Complexity levels
complexity_options = ["simple", "detailed", "technical"]

# Style variations
style_options = ["technical", "hand-drawn", "hybrid", "minimalist"]

# Perspective options
perspective_options = ["isometric", "top-down", "side-view", "3d-perspective"]

# Annotation layers
annotation_options = ["labels", "dimensions", "callouts", "notes", "warnings"]

# Category-specific templates
categories = [
    "water", "fire", "shelter", "food",
    "navigation", "medical", "tools", "communication"
]
```

### Theme System API

#### Theme Manager

```python
from core.theme.theme_manager import ThemeManager

# Initialize theme manager
themes = ThemeManager()

# Get available themes
available = themes.list_themes()

# Load theme
theme_data = themes.load_theme("synthwave")

# Apply theme
themes.apply_theme("synthwave")

# Get current theme
current = themes.get_current_theme()

# Create custom theme
themes.create_theme(
    name="my-theme",
    colors={
        "primary": "#FF6B6B",
        "secondary": "#4ECDC4",
        "background": "#1A1A2E",
        "text": "#EAEAEA"
    }
)
```

**Built-in Themes:**
- `c64` - Commodore 64 (blue/purple)
- `nes` - 8-bit Nintendo (red/white)
- `synthwave` - Cyberpunk (pink/cyan)
- `teletext` - Broadcast TV (8 colors)
- `mac-os` - Classic Mac (monochrome)
- `terminal` - Green phosphor
- `amber` - Amber monitor

### Graphics System API (v1.1.1+)

#### GraphicsCompositor - ASCII/Teletext Diagram Generation

```python
from core.services.graphics_compositor import GraphicsCompositor

# Initialize compositor
gc = GraphicsCompositor()

# Create flow diagram (vertical process)
flow = gc.create_flow(
    steps=['Collect water', 'Filter', 'Boil', 'Cool', 'Store'],
    style='chunky',  # chunky, heavy, light
    width=40
)
print(flow)
# Output:
# ▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
# ▐           Collect water              ▌
# ▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
#                    ┃
#                    ▼
# ▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
# ▐              Filter                  ▌
# ▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
# ... etc

# Create tree diagram (hierarchy)
tree = gc.create_tree(
    root='Shelter Types',
    branches={
        'Natural': ['Cave', 'Rock overhang', 'Tree hollow'],
        'Constructed': ['Lean-to', 'A-frame', 'Debris hut'],
        'Improvised': ['Tarp shelter', 'Snow cave']
    },
    style='chunky',
    width=50
)

# Create grid diagram (comparison table)
grid = gc.create_grid(
    headers=['Method', 'Time', 'Difficulty', 'Tools'],
    rows=[
        ['Boiling', '10 min', 'Easy', 'Pot, fire'],
        ['Chemical', '30 min', 'Easy', 'Tablets'],
        ['UV Light', '15 min', 'Medium', 'UV device'],
        ['Filter', '5 min', 'Easy', 'Filter']
    ],
    style='chunky'
)

# Create simple box
box = gc.create_box(
    width=30,
    height=5,
    label='Water Storage',
    style='heavy'  # heavy, light, double, rounded
)

# Create chunky teletext box
chunky_box = gc.create_chunky_box(
    width=35,
    label='⚠ SAFETY WARNING'
)

# Create label with connector
label = gc.create_label('Start here', width=20)

# Create arrow connector
arrow = gc.create_arrow_connector(direction='down')  # down, up, right, left
```

**Convenience Functions:**

```python
from core.services.graphics_compositor import (
    create_flow,
    create_tree,
    create_grid,
    create_box
)

# Direct function calls (same as using GraphicsCompositor)
diagram = create_flow(['Step 1', 'Step 2', 'Step 3'], style='chunky')
```

**Block Library Structure:**

```python
# Located at: core/data/graphics/blocks/

teletext.json       # Core teletext blocks
├── solid_blocks    # █, ▓, ▒, ░
├── box_drawing     # ┌─┐ ╔═╗ ╭─╮
├── arrows          # ↑ ↓ ← → ▲ ▼
├── icons           # ● ○ ■ □ ▪ ▫
├── geometric       # △ ▽ ◇ ◆
├── terrain         # ≈ ∩ ▲ ♠ ♣
├── special         # ☀ ☁ ❄ 🌧
└── mosaic_2x3      # Chunky teletext blocks

borders.json        # Border styles
├── heavy           # ▐ ▀ ▄
├── double          # ╔ ═ ╗
├── light           # ┌ ─ ┐
├── rounded         # ╭ ─ ╮
├── block           # █ (solid)
└── chunky          # ▐ ▀ ▄ (teletext)

patterns.json       # Fill patterns
├── solid           # Full blocks
├── gradient        # █ ▓ ▒ ░
├── checkerboard    # Alternating
└── dots            # Sparse fill

maps.json           # Map-specific patterns
├── terrain_chars   # Ocean, land, mountains
├── gradient_sequences
├── biome_patterns
└── map_legends
```

**Diagram Templates:**

```python
# Located at: core/data/graphics/templates/

flow_diagram.json   # Vertical process flows
tree_diagram.json   # Hierarchical structures
grid_diagram.json   # Comparison tables
```

**See Also:**
- `core/data/graphics/README.md` - Complete graphics system documentation
- `sandbox/docs/teletext-patterns-reference.md` - Pattern examples
- `sandbox/scripts/generate_diagram.py` - CLI diagram generator

### Content Generation Workflow

#### Knowledge Guide Generator

```python
# Use the guide generator script
# Located at: sandbox/scripts/generate_knowledge_guide.py

# Generate guide with flow diagram
.venv/bin/python sandbox/scripts/generate_knowledge_guide.py \
    --category water \
    --title "Boiling Water Purification" \
    --type flow \
    --complexity beginner \
    --output knowledge/water/boiling_water.md

# Generate guide with tree diagram
.venv/bin/python sandbox/scripts/generate_knowledge_guide.py \
    --category shelter \
    --title "Shelter Type Selection" \
    --type tree \
    --complexity intermediate

# Generate guide with grid diagram
.venv/bin/python sandbox/scripts/generate_knowledge_guide.py \
    --category fire \
    --title "Fire Starting Methods Comparison" \
    --type grid \
    --complexity beginner
```

**Programmatic Generation:**

```python
from core.services.graphics_compositor import create_flow

# Generate guide content
guide_content = f"""# Water Purification: Boiling Method

**Category:** Water
**Complexity:** Beginner
**Time Required:** 15-30 minutes

## Overview

Boiling is the most reliable method of water purification in survival situations.

## Step-by-Step Instructions

### 1. Pre-Filter
Remove large debris and sediment from water.

### 2. Boil
Heat water to rolling boil for 1-3 minutes.

### 3. Cool
Allow water to cool to safe drinking temperature.

### 4. Store
Store in clean, covered container.

## Diagram

```
{create_flow(['Pre-Filter', 'Boil', 'Cool', 'Store'], style='chunky', width=40)}
```

## Key Points

- Kills 99.9% of pathogens
- No special equipment needed
- Works at any altitude (adjust time)
- Does not remove chemicals

## Sources

- WHO Water Treatment Guidelines (2022)
- Wilderness Medicine Handbook
"""

# Save to file
with open('knowledge/water/boiling_purification.md', 'w') as f:
    f.write(guide_content)
```

#### Diagram Refresh Script

```python
# Use the refresh script to add diagrams to existing guides
# Located at: sandbox/scripts/refresh_knowledge_diagrams.py

# Refresh single category
.venv/bin/python sandbox/scripts/refresh_knowledge_diagrams.py knowledge/water/

# Refresh all categories
.venv/bin/python sandbox/scripts/refresh_knowledge_diagrams.py --all

# Dry run (preview changes)
.venv/bin/python sandbox/scripts/refresh_knowledge_diagrams.py --all --dry-run
```

#### Content Validator

```python
# Validate knowledge content
# Located at: sandbox/scripts/validate_knowledge_content.py

# Validate single category
.venv/bin/python sandbox/scripts/validate_knowledge_content.py knowledge/water/

# Validate all categories
.venv/bin/python sandbox/scripts/validate_knowledge_content.py --all

# Check for:
# - Missing required sections
# - Placeholder text ([FILL IN])
# - Missing sources/citations
# - Safety warnings
# - Formatting issues
```

**Content Generation Best Practices:**

1. **Use Templates** - Start with generated template, fill in details
2. **Add Diagrams Early** - Create diagram while writing steps
3. **Validate Often** - Run validator frequently during development
4. **Cross-Reference** - Link related guides
5. **Cite Sources** - Always include source citations
6. **Test Rendering** - View in terminal to check ASCII rendering

**Knowledge Bank Organization:**

```
knowledge/
├── water/          # 25 guides, 17 with diagrams
├── fire/           # 20 guides, 12 with diagrams
├── shelter/        # 20 guides, 13 with diagrams
├── food/           # 22 guides, 12 with diagrams
├── medical/        # 26 guides, 12 with diagrams
├── navigation/     # 20 guides, 10 with diagrams
├── skills/         # Expandable category
└── making/         # Expandable category

# Current: 133 guides total, 78 with embedded diagrams (59%)
# Target: 500+ guides, 100% diagram coverage
```
- `paper` - White/sepia

### Command System API

#### Command Registration

```python
from core.commands.command_registry import CommandRegistry

# Register custom command
@CommandRegistry.register('CUSTOM')
def custom_command(params, context):
    """Custom command implementation."""
    # Process params
    # Return result
    return result

# Unregister command
CommandRegistry.unregister('CUSTOM')

# Get command handler
handler = CommandRegistry.get_handler('GENERATE')

# Execute command
result = CommandRegistry.execute('GENERATE', ['guide', 'water'])
```

#### Command Context

```python
# Command context structure
context = {
    'workspace': '/path/to/workspace',
    'user': 'username',
    'theme': 'synthwave',
    'config': config_object,
    'session': session_object,
    'verbose': True
}

# Access in command handler
def my_command(params, context):
    workspace = context['workspace']
    user = context['user']
    config = context['config']
    # Process command...
```

---

## Extension Development

### Creating a New Extension

#### 1. Use Extension Template

```bash
# Create from template
python -m extensions.core.extension_dev_tools create \
  --name my-extension \
  --type web \
  --author "Your Name"

# Generated structure:
# extensions/cloned/my-extension/
# ├── extension.json
# ├── server.py
# ├── static/
# └── templates/
```

#### 2. Define Extension Metadata

**extension.json:**
```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "type": "web",
  "author": "Your Name",
  "description": "My custom extension",
  "entry_point": "server.py",
  "dependencies": ["flask"],
  "permissions": ["read", "write"],
  "config": {
    "port": 8081,
    "auto_start": false
  }
}
```

#### 3. Implement Extension

**server.py:**
```python
from flask import Flask, render_template
from core.config import Config

app = Flask(__name__)
config = Config()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # Access uDOS systems
    user = config.get('username')
    return {'user': user}

if __name__ == '__main__':
    port = config.get('my_extension_port', 8081)
    app.run(port=port, debug=True)
```

#### 4. Test Extension

```bash
# Validate extension
python -m extensions.core.extension_dev_tools validate my-extension

# Test extension
python -m extensions.core.extension_dev_tools test my-extension

# Package extension
python -m extensions.core.extension_dev_tools package my-extension
```

### Extension Best Practices

#### 1. Follow Extension Structure

```
my-extension/
├── extension.json          # Required metadata
├── server.py              # Entry point
├── README.md              # Documentation
├── requirements.txt       # Python dependencies
├── static/                # Static assets
│   ├── css/
│   ├── js/
│   └── assets/
├── templates/             # HTML templates
└── tests/                 # Test files
```

#### 2. Use Core Services

```python
# Always use Config for settings
from core.config import Config
config = Config()

# Use Knowledge Manager for content
from core.knowledge.knowledge_manager import KnowledgeManager
km = KnowledgeManager()

# Use Theme System for styling
from core.theme.theme_manager import ThemeManager
themes = ThemeManager()
```

#### 3. Handle Errors Gracefully

```python
from core.exceptions import UDOSError, ValidationError

try:
    result = risky_operation()
except ValidationError as e:
    # Handle validation errors
    return {"error": str(e)}, 400
except UDOSError as e:
    # Handle system errors
    return {"error": str(e)}, 500
except Exception as e:
    # Handle unexpected errors
    return {"error": "Internal error"}, 500
```

#### 4. Log Activity

**v1.1.6+ (Recommended)**:
```python
from core.services.logging_manager import get_logger

logger = get_logger('my-extension')

logger.info("Extension started")
logger.warning("Potential issue detected")
logger.error("Operation failed", exc_info=True)
logger.debug("Debug information", extra={'data': debug_data})
```

**See**: [Logging System](Logging-System.md) for complete logging API documentation.

**Backward compatible** (Session logging):
```python
from core.services.session_logger import SessionLogger

logger = SessionLogger()
logger.log("Extension started")
logger.error("Operation failed")
logger.close()  # Optional - automatic cleanup
```

---

## Best Practices

### Code Organization

#### 1. File Organization
- Place files in appropriate directories
- Follow naming conventions (`snake_case` for Python)
- Keep related files together
- Update documentation when moving files

#### 2. Code Structure
- Use modular design (single responsibility principle)
- Follow PEP 8 style guidelines
- Include docstrings for all functions/classes
- Add type hints where appropriate

#### 3. Documentation
- Document all public APIs
- Include usage examples
- Keep README files up to date
- Add inline comments for complex logic

#### 4. Testing
- Write tests for new features
- Maintain high test coverage (>80%)
- Use descriptive test names
- Test edge cases and error conditions

### Configuration Management

```python
# ✅ Good: Use Config for all settings
from core.config import Config
config = Config()
api_key = config.get_env('GEMINI_API_KEY')

# ❌ Bad: Hardcode values
api_key = "hardcoded-key"

# ✅ Good: Use environment variables for secrets
password = config.get_env('UDOS_MASTER_PASSWORD')

# ❌ Bad: Store secrets in code
password = "my-password"
```

### Error Handling

```python
# ✅ Good: Specific exception handling
try:
    result = process_data(data)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return None
except UDOSError as e:
    logger.error(f"System error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# ❌ Bad: Bare except
try:
    result = process_data(data)
except:
    pass
```

### Logging

```python
# ✅ Good: Structured logging with context
logger.info("Processing file", extra={
    'filename': filename,
    'size': file_size,
    'user': username
})

# ❌ Bad: Print statements
print(f"Processing {filename}")

# ✅ Good: Appropriate log levels
logger.debug("Detailed debugging info")
logger.info("Normal operation")
logger.warning("Potential issue")
logger.error("Error occurred", exc_info=True)

# ❌ Bad: Everything as error
logger.error("File processed successfully")
```

### Security

```python
# ✅ Good: Validate user input
def process_command(command):
    if not is_valid_command(command):
        raise ValidationError("Invalid command")
    return execute(command)

# ❌ Bad: Execute without validation
def process_command(command):
    return eval(command)  # Never do this!

# ✅ Good: Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ Bad: String concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

---

## Contributing Guidelines

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes**
4. **Write/update tests**
5. **Update documentation**
6. **Submit a pull request**

### Code Review Process

1. **Automated Checks**
   - All tests must pass
   - Code must pass linting
   - Coverage must not decrease

2. **Peer Review**
   - At least one approval required
   - Address all review comments
   - Maintain clean commit history

3. **Documentation**
   - Update relevant wiki pages
   - Add/update docstrings
   - Include usage examples

### Commit Guidelines

```bash
# Good commit messages
git commit -m "feat: Add water purification guide generator"
git commit -m "fix: Correct teletext color rendering"
git commit -m "docs: Update API reference for Config class"
git commit -m "test: Add integration tests for MAP commands"

# Commit message format
# <type>: <description>
#
# Types: feat, fix, docs, test, refactor, style, chore
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Documentation
- [ ] Wiki updated
- [ ] API docs updated
- [ ] Code comments added

## Related Issues
Fixes #123
Related to #456
```

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions
- Follow community guidelines

---

## Related Documentation

- [Command Reference](Command-Reference) - All available commands
- [Extensions System](Extensions-System) - Extension documentation
- [Knowledge System](Knowledge-System) - Knowledge bank architecture
- [Philosophy](Philosophy) - Project philosophy and vision
- [Contributing](../CONTRIBUTING.md) - Contributing guidelines
- [ROADMAP](../dev/roadmap/ROADMAP.md) - Future development plans

---

**Last Updated:** November 27, 2025
**Version:** v1.1.1

🔧 *This guide provides everything developers need to contribute to uDOS, from architecture understanding to practical API usage and extension development.*
