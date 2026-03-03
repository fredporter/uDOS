# uDOS Installation Guide

## Overview

The uDOS installer provides a comprehensive, cross-platform setup experience for macOS and Linux. It handles all dependencies, environment configuration, and optional components automatically.

Contributor-only Dev Mode guidance now lives under `dev/docs/`. Root `docs/` keeps runtime and operator installation material.

## Quick Install

### macOS

**Option 1: Double-click installer (easiest)**
1. Navigate to `bin/install-udos-vibe.command` in Finder
2. Double-click the file
3. Follow the prompts

**Option 2: Terminal**
```bash
cd /path/to/uDOS
./bin/install-udos-vibe.sh
```

### Linux (Ubuntu/Alpine)

```bash
cd /path/to/uDOS
./bin/install-udos-vibe.sh
```

## Installation Modes

### Full Installation (Default)
Installs both core uDOS and wizard components:
```bash
./bin/install-udos-vibe.sh
```

### Core Only
Install only the standard `ucode` runtime path without wizard services:
```bash
./bin/install-udos-vibe.sh --core
```

### Wizard Only
Add wizard components to an existing core installation:
```bash
./bin/install-udos-vibe.sh --wizard
```

### Update Existing Installation
Update the installed runtime and dependencies:
```bash
./bin/install-udos-vibe.sh --update
```

## v1.4 to v1.5 Migration

Use the active migration framework in [docs/examples/udos_v1_5_deliverables/docs/migration-v1.4-to-v1.5.md](/Users/fredbook/Code/uDOS/docs/examples/udos_v1_5_deliverables/docs/migration-v1.4-to-v1.5.md) as the canonical upgrade checklist.

Current v1.5 migration requirements:
- remove retired local-model default runtime assumptions
- standardize on GPT4All as the local assist layer
- treat Wizard as the exclusive online routing and budget-control layer
- update project/task/workflow artifacts to the v1.5 deliverables schema family under [docs/examples/udos_v1_5_deliverables/schemas](/Users/fredbook/Code/uDOS/docs/examples/udos_v1_5_deliverables/schemas)

Recommended upgrade sequence:
```bash
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev
uv run ./uDOS.py SETUP
./scripts/run_pytest_core_stdlib.sh
```

### Preflight Capability Check (No Install)
Run capability detection and tier gating without installing:
```bash
./bin/install-udos-vibe.sh --preflight-json --tier auto
```
Use `--tier 1|2|3` to test hardline gating for a requested tier.

## What the Installer Does

### 1. System Detection & Analysis
- **OS Detection**: Identifies macOS, Ubuntu, Alpine, or generic Linux
- **Hardware Specs**: Detects CPU cores, RAM, architecture (Intel/ARM)
- **GPU/VRAM Detection**: Checks GPU presence and probes VRAM when local-model tiers are evaluated
- **Requirements Check**: Verifies curl, git, and other essentials
- **Tier Hardlines**: Forces cloud-only tier when OS/kernel is legacy or resources are below local-model requirements

### 2. Package Manager Setup
- **uv Installation**: installs [uv](https://github.com/astral-sh/uv) if not present
- standard repo-local runtime path is `/.venv`
- all active Python install/update flows use `uv`

### 3. Environment Configuration
- **Creates .env file**: Copies from `.env.example` and auto-configures:
  - `UDOS_ROOT` → Repository path
  - `VAULT_ROOT` → Vault location
  - `OS_TYPE` → Detected OS
  - `WIZARD_ADMIN_TOKEN` → Auto-generated security token
  - `WIZARD_KEY` → Auto-generated encryption key
- **User Setup**: Prompts for:
  - Username (or enter Ghost mode)
  - provider configuration only for lanes that require it

### 4. Editor & Vault Setup
- **micro editor**: Optional TUI-friendly text editor
- **Obsidian check**: Detects and optionally guides installation
- **Vault structure**: Creates `memory/vault/` and seeds from template
- **Directory structure**: Sets up logs, cache, and runtime directories

### 5. Dev Mode Tooling Installation
- **Install global vibe runtime**: Only when the `dev` profile is selected
- **Wizard-managed extension lane**: Dev Mode is installed and removed through Wizard GUI lifecycle controls
- **Framework gate**: Requires `/dev/` plus `/dev/extension.json`
- **Workspace contract**: tracked contributor docs and Goblin fixtures now live under `dev/docs/` and `dev/goblin/`
- **uDOS integration**: Creates `.vibe/` symlinks for contributor tools/skills
- **Standard runtime**: `ucode` remains the primary entry point
- **Core dependencies**: Installs Python packages from `pyproject.toml`
- **Logic assist prep**: runs the v1.5 GPT4All contributor setup helper when the selected tier permits local assist

### 6. Wizard Server Setup (if not --core)
- **Wizard dependencies**: Installs FastAPI, uvicorn, Flask, etc.
- **Config template**: Creates wizard config from template
- **Secret storage**: Prepares encrypted identity store
- **API endpoints**: Sets up REST API and WebSocket servers

### 7. Optional Components
- **GPT4All local assist**: standard local offline assist layer for v1.5
  - advisory only; never execution authority
  - optimized for summarization, drafting, and operator guidance
  - pairs with deterministic `uLogic` execution and Wizard online escalation policy
- **udos-tui build**:
  - built automatically when `go` is available
  - provides the Bubble Tea + Lip Gloss v1.5 shell frontend
  - remains optional; `./bin/ucode` continues to work without it
- **Wizard budget control**:
  - handles all online model routing and daily spend policy
  - keeps offline-first behavior when budgets or policy thresholds block escalation

### 8. Health Check & Summary
- **Component verification**: Checks all installed tools
- **Configuration summary**: Shows paths, settings, status
- **Next steps**: Provides clear guidance on what to do next

## Environment Variables

### Auto-Configured
These are set automatically by the installer:
- `UDOS_ROOT` - Repository root path
- `VAULT_ROOT` - Vault directory path
- `VAULT_MD_ROOT` - Markdown vault alias
- `OS_TYPE` - Operating system (mac, ubuntu, alpine, linux)
- `WIZARD_ADMIN_TOKEN` - Admin authentication token
- `WIZARD_KEY` - Encryption key (64-char hex)

### User-Provided
You'll be prompted to set:
- `USER_USERNAME` - Your username (or "Ghost" for demo mode)
- `MISTRAL_API_KEY` - optional Dev Mode provider key when that lane is enabled

### Optional (can be set manually later)
- `UDOS_TIMEZONE` - Your timezone (e.g., "America/New_York")
- `UDOS_LOCATION` - Your location
- GPT4All/Wizard-specific runtime settings as introduced by the active v1.5 logic-assist migration path
- `UDOS_LOGIC_INSTALL_TIER` - installer-selected logic-assist tier
- `UDOS_LOGIC_RECOMMENDED_MODELS` - advisory list of local GPT4All model names for the selected tier

## Directory Structure After Install

```
uDOS/
├── .env                      # Your configuration (DO NOT COMMIT)
├── .vibe/
│   ├── tools -> ../vibe/core/tools/ucode
│   └── skills -> ../vibe/core/skills/ucode   # Dev extension contributor subset only
├── dev/                      # Dev Mode extension framework/template root
│   ├── extension.json
│   ├── AGENTS.md
│   ├── DEVLOG.md
│   ├── project.json
│   ├── tasks.md
│   ├── completed.json
│   ├── docs/
│   └── goblin/
├── memory/
│   ├── vault/               # Your personal vault (seeded from template)
│   ├── logs/                # Runtime logs
│   └── .secrets.tomb        # Encrypted user data (created on first run)
├── wizard/
│   └── config/.env          # Wizard secrets (DO NOT COMMIT)
└── bin/
    ├── install-udos-vibe.command  # macOS clickable installer
    └── install-udos-vibe.sh       # Cross-platform installer
```

## Core vs Wizard Components

### Core Components
**Always installed** (except with `--wizard` flag):
- `ucode` runtime and command surface
- core uDOS tools and scaffolds
- Core Python dependencies (minimal)
- Vault structure and templates
- Basic TUI and command system

**Use core-only for**:
- CLI-only workflows
- Minimal installations
- Offline-first usage
- Resource-constrained systems

### Wizard Components
**Installed with full or `--wizard` mode**:
- FastAPI/Flask web servers
- WebSocket support for real-time features
- Multi-provider OK routing (OpenAI, Anthropic, Google)
- QR code generation
- Extended web admin interface
- Gmail/Google Drive integration

**Use wizard for**:
- Web-based access
- Multiple OK providers
- Team/shared usage
- Advanced integrations

## Vibe Dev Extension

The Vibe lane is intentionally small and contributor-only.

- It is enabled only for the `dev` profile with the `/dev/` extension installed and active.
- It is not a second full operator runtime.
- It exposes only a reduced skill set for development work: `ucode`, `ucode-help`, `ucode-setup`, and `ucode-dev`.
- Binder, story, spatial, gameplay, media, and destructive flows stay in the standard `ucode` TUI.
- LAN gateway features
- Dev Mode extension install/uninstall and activation lifecycle

Contributor setup details:
- `dev/docs/howto/VIBE-Setup-Guide.md`
- `dev/docs/specs/DEV-WORKSPACE-SPEC.md`

### Lazy Loading
The wizard is **not required** for core functionality:
1. Install core: `./bin/install-udos-vibe.sh --core`
2. Use `ucode` normally
3. When you need wizard features: `./bin/install-udos-vibe.sh --wizard`

This approach saves disk space and keeps installations minimal.

## After Installation

### 1. Test Core Installation
```bash
cd /path/to/uDOS
./bin/ucode STATUS
```

You should see the standard `ucode` runtime respond successfully.

### 2. Run Setup Story
In the standard runtime, run:
```
ucode SETUP
```

This completes the user configuration:
- Sets username and identity
- Configures timezone and location
- Initializes vault
- Creates encrypted secret storage

### 3. Start Wizard (if installed)
```bash
./bin/ucode WIZARD start
```

Access the web interface at: http://localhost:8765

### 4. Configure Additional Settings
Edit your `.env` file:
```bash
micro .env
# or
nano .env
# or use your preferred editor
```

Key settings to review:
- `UDOS_TIMEZONE` - Set your timezone
- `UDOS_LOCATION` - Set your location
- Logging preferences
- TUI display options

## Troubleshooting

### "uv: command not found"
The installer installs uv to `~/.local/bin/` or `~/.cargo/bin/`. Add to your PATH:
```bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

Make permanent by adding to `~/.zshrc` or `~/.bashrc`.

### "vibe: command not found"
After running the official vibe installer, ensure your PATH includes the installer location:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Permission denied on .command file
Make it executable:
```bash
chmod +x bin/install-udos-vibe.command
```

### Obsidian not detected
**macOS**: Install from https://obsidian.md/download
**Linux**: `snap install obsidian --classic`

### GPT4All local model is not ready
1. Run `SETUP dev` to install the GPT4All package and contributor tooling
2. Check the configured model path in `core/framework/seed/bank/typo-workspace/settings/logic-assist.md`
3. Place the configured `.gguf` model file in the expected local model directory

### Wizard won't start
1. Check wizard dependencies: `./bin/install-udos-vibe.sh --wizard`
2. Check `.env` has `WIZARD_ADMIN_TOKEN` and `WIZARD_KEY`
3. Check logs: `tail -f memory/logs/udos.log`

### Import errors after install
Reinstall dependencies by profile:
```bash
cd /path/to/uDOS
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos          # Core profile only
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard   # Wizard web/API profile (includes FastAPI)
# uv sync --extra udos-full   # Optional full profile with extra providers
```

## Updating

### Update runtime install
```bash
./bin/install-udos-vibe.sh --update
```

### Update dependencies only
```bash
cd /path/to/uDOS
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos
# If you use Wizard web/API features:
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard
```

### Update local GPT4All model selection
Update the local model contract in `logic-assist.md`, then replace the local `.gguf` file in the configured model directory.

## Advanced Options

### Custom Python Environment
uDOS v1.5 standardizes on `/.venv`:
```bash
uv venv .venv --python 3.12
UV_PROJECT_ENVIRONMENT=.venv uv run python --version
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos
# Add Wizard profile only when needed:
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard
```

### Skip Interactive Prompts
Set environment variables before running:
```bash
export UDOS_SKIP_PROMPTS=1
export USER_NAME="myname"
export MISTRAL_API_KEY="your-key-here"
./bin/install-udos-vibe.sh
```

### CI/Automation Mode
```bash
export UDOS_AUTOMATION=1
./bin/install-udos-vibe.sh --core
```

## Uninstallation

### Remove Dev Mode tooling
Use Wizard GUI to uninstall or deactivate the Dev Mode extension first. Remove global `vibe` tooling only after the `dev-mode` extension lane has been disabled.

```bash
uv tool uninstall mistral-vibe
```

### Clean up repo artifacts
```bash
rm -rf .env
rm -rf memory/
rm -rf .vibe/
rm -rf .venv/
rm -rf tui/bin/
```

### Remove uv
```bash
rm -rf ~/.cargo/bin/uv ~/.local/bin/uv
```

## Getting Help

- **Documentation**: See `docs/` directory
- **Quick Start**: See `QUICK-START.md`
- **Issues**: https://github.com/mistralai/mistral-vibe/issues
- **Community**: Join the discussion

## Next Steps

After successful installation:
1. Read [QUICK-START.md](QUICK-START.md) for usage examples
2. Explore [HOW-TO-USE-SKILLS.md](howto/HOW-TO-USE-SKILLS.md) for skill guides
3. Check [howto/TOOLS-REFERENCE.md](howto/TOOLS-REFERENCE.md) for available tools
4. Review [docs/README.md](docs/README.md) for architecture details

Happy coding with uDOS! 🚀
