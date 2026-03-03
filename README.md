# uDOS v1.5 Rebaseline

```
████████████████████████████████████████████████████████████
██                                                        ██
██   ██████████████████████████████████████████████████   ██
██   ██  ████  ███      ███      ███       ███       ██   ██
██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██
██   ██  ████  ██  ███████  ████  ██  ████  ██      ███   ██
██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██
██   ███      ████      ███      ███       ███       ██   ██
██   ██████████████████████████████████████████████████   ██
██   ███████████████    ███████████    ████████████████   ██
██   █████████████████  uDOS v1.4.5  ██████████████████   ██
██   ██████████████████████████████████████████████████   ██
██                                                        ██
████████████████████████████████████████████████████████████
```

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

</div>

## What is This?

uDOS v1.5 is being rebaselined around one runtime rule:

- `ucode` is the primary user entry point
- the v1.5 `ucode` TUI is the standard interactive user experience
- Wizard is the browser/service layer that hangs off `ucode`
- `vibe` is a Dev Mode surface only
- Mistral-backed contributor flows are treated as Dev Mode operations
- Sonic remains independently distributable, but installed-system control routes through `ucode`

The active release-control surface is now:

- `UCODE PROFILE LIST`
- `UCODE PROFILE SHOW <profile>`
- `UCODE PROFILE INSTALL <profile>`
- `UCODE OPERATOR STATUS`
- `UCODE OPERATOR PLAN <prompt>`
- `UCODE EXTENSION LIST`
- `UCODE PACKAGE LIST`

Authoritative release planning now lives in:

- [docs/roadmap.md](docs/roadmap.md)
- [distribution/profiles/certified-profiles.json](distribution/profiles/certified-profiles.json)

### Key Differences from Stock Vibe

| Feature | Stock Vibe | uDOS v1.4.5 +Vibe |
|---------|-----------|------------|
| Installation | Global `vibe` via official installer | Repo install with `ucode` as the standard runtime |
| Commands | Read/write/bash/git tools | `ucode` standard runtime plus optional Dev Mode tooling |
| Workspace | Project folder | Project + vault + memory + Obsidian |
| Knowledge | Code only | Markdown vault (offline) |
| Extensibility | Skills/MCP | Skills + uDOS Wizard server |
| Setup | Interactive key entry | Auto-generates identity + keys |

> [!WARNING]
> Dev Mode tooling works on Windows, but we officially support and target UNIX environments.

---

## Quick Start

### Prerequisites
- Python 3.12+
- Git
- macOS or Linux (Ubuntu/Alpine recommended)

### Installation

Current direction:
- use `ucode` as the standard runtime shell after install
- treat `vibe` as contributor tooling gated behind Dev Mode
- treat Mistral-backed contributor flows as Dev Mode operations rather than the default runtime
- verify release lanes through `UCODE PROFILE ...`

**Option 1: Automated installer (recommended)**

macOS:
```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Run installer (double-click in Finder, or from terminal)
./bin/install-udos-vibe.sh
```

Linux:
```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Run installer
./bin/install-udos-vibe.sh
```

The installer automatically handles:
- ✓ uv package manager installation
- ✓ `.venv` runtime setup
- ✓ Environment configuration (.env)
- ✓ standard runtime installation
- ✓ Vault structure setup
- ✓ Optional components (micro, Obsidian, Wizard-managed logic-assist, `udos-tui` when Go is available)

**Option 2: Manual installation**

```bash
# Clone and navigate
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the v1.5 runtime contract
uv venv .venv --python 3.12
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev

# Copy and configure .env
cp .env.example .env
# Edit `.env` with your identity and optional Wizard provider settings

# Run setup story
UV_PROJECT_ENVIRONMENT=.venv uv run ./uDOS.py SETUP
```

📚 **Full installation guide**: [docs/INSTALLATION.md](docs/INSTALLATION.md)

### First Commands

After installation, start with the `ucode` surface:

```bash
ucode HELP
ucode SETUP
ucode STATUS
ucode UCODE PROFILE LIST
ucode UCODE OPERATOR STATUS
```

Use `vibe` only when you explicitly want the Dev Mode contributor surface.

## Project Structure

```
uDOS/
├── vibe/                          # Dev Mode contributor runtime (read-only base)
│   ├── cli/                       # Entry point
│   ├── core/
│   │   ├── tools/                 # Built-in tools
│   │   │   └── ucode/             # uDOS tools (addon)
│   │   └── skills/                # Built-in skills
│   │       └── ucode/             # uDOS skills (addon)
│   └── ...vibe/
│
├── core/                          # uDOS core (runtime, framework)
│   ├── commands/                  # Command handlers (50+)
│   ├── framework/                 # Service framework
│   ├── memory/                    # In-memory data structures
│   ├── parsers/                   # Config/spec parsing
│   └── tests/
│
├── wizard/                        # Wizard API gateway
│   ├── mcp_server.py              # MCP interface
│   ├── services/                  # Web/routing services
│   └── tests/
│
├── docs/                          # Runtime, operator, and product documentation
│   ├── ARCHITECTURE.md            # Architecture overview
│   ├── INTEGRATION-READINESS.md   # Audit results
│   ├── roadmap.md                 # Active milestone and execution plan
│   ├── specs/                     # Format/interface specs
│   ├── howto/                     # Procedures and guides
│   └── decisions/                 # ADRs and design decisions
├── dev/                           # `@dev` contributor workspace
│   ├── docs/                      # Contributor-only Dev Mode docs
│   └── goblin/                    # Distributable dev scaffold
│
├── tests/                         # Test suite
├── ext/                           # Extensions / plugins
├── memory/                        # Runtime state (git-ignored)
├── vault/                         # Knowledge vault (git-template)
├── wiki/                          # User documentation
│
├── .vibe/config.toml              # Vibe integration config
├── .env.example                   # Environment template
├── pyproject.toml                 # Root deps (Vibe + uDOS)
└── uDOS.py                        # Command dispatcher
```

### Key Files

**`.vibe/config.toml`**
- Integration point for Vibe
- Declares uDOS tool/skill paths
- MCP server configs
- Auto-discovered on startup

**`pyproject.toml`**
- Project metadata
- Vibe + uDOS dependencies
- Optional groups: `[udos]`, `[udos-wizard]`, `[udos-full]`

**`core/commands/`**
- 50+ command implementations
- CommandDispatcher router
- Test fixtures

**`vibe/core/tools/ucode/` & `vibe/core/skills/ucode/`**
- Addon modules managed by this repo overlay
- Custom tools/skills for uDOS
- Safely coexist with Vibe built-ins

---

## Documentation

Use [docs/README.md](docs/README.md) as the canonical documentation front door.

Recommended entrypoints:
- [docs/roadmap.md](docs/roadmap.md) for active v1.5 work
- [docs/decisions/v1-5-workflow.md](docs/decisions/v1-5-workflow.md) for workflow ownership and lane split
- [docs/specs/README.md](docs/specs/README.md) for active contracts
- [docs/howto/](docs/howto/) for operator procedures
- [docs/examples/](docs/examples/) for sample assets and packs
- [dev/docs/README.md](dev/docs/README.md) for contributor-only `@dev` workspace guidance

---

## Installation & Setup

For installation, configuration, and environment setup, use:
- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [dev/docs/howto/VIBE-Setup-Guide.md](dev/docs/howto/VIBE-Setup-Guide.md)
- [docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md](docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md)

### Minimum Spec (`ucode` Runtime Path)

| Component | Requirement |
|---------|-------------|
| OS | Linux/macOS/Windows 10+ (x86/ARM) |
| CPU | 2 cores (x86/ARM) |
| RAM | 4 GB |
| Storage | 5 GB free (SSD recommended) |
| Network | Optional (online/offline pathways supported) |
| Dependencies | Python 3.12+, uDOS runtime, optional Wizard/Dev Mode layers |

Operational pathways:
- `With network`: `UCODE` + cloud provider fallback + full command/docs surface.
- `Without network`: `UCODE` + local demo/docs/system-introspection fallback.

See full brief: [`docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md`](docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md).

## Features

### Dev Mode Features

- **Interactive Chat**: A conversational OK Assistant that understands your requests
- **Powerful Tools**: Read/write/patch files, execute shell commands, search code, manage todos
- **Project-Aware**: Scans file structure and Git status for context
- **Multiple Agents**: Default, plan, accept-edits, auto-approve profiles
- **Subagents**: Delegate work for parallel processing
- **Skills System**: Extend with custom skills and slash commands
- **MCP Support**: Model Context Protocol servers for additional tools
- **Highly Configurable**: Customize via `~/.vibe/config.toml`

### Standard Runtime Features

- **50+ Commands**: Extensive CLI command suite
- **Vault-Based**: Offline Obsidian-compatible knowledge system
- **Auto-Setup**: Identity + API key auto-generation
- **Self-Healing**: SETUP, REPAIR, SEED commands
- **Wizard Server**: LAN gateway and extension routing
- **Non-Fork**: Addon architecture integrates with optional Dev Mode tooling without divergence

---

## Usage

### Standard Runtime

```bash
ucode HELP
ucode STATUS
ucode WORKFLOW LIST
ucode UCODE PROFILE SHOW core
ucode UCODE OPERATOR PLAN "review current workspace state"
```

### Dev Mode

```bash
# Start the Dev Mode contributor surface
vibe

# Example Dev Mode prompts
vibe --prompt "Refactor the main function"
vibe --enabled-tools "bash*,read_file" --prompt "List files in src/"
```

### Command Reference

**Core commands** (handled by uDOS CommandDispatcher):
- `STATUS` — Show system status
- `SETUP` — Initialize identity + keys
- `REPAIR` — Check/fix configuration
- `HELP` — Get command help
- `WIZARD start` — Launch Wizard server

See [docs/howto/UCODE-COMMAND-REFERENCE.md](docs/howto/UCODE-COMMAND-REFERENCE.md) for complete command list.

### Keyboard Shortcuts

- **`Ctrl+J` / `Shift+Enter`** — Multi-line input
- **`Ctrl+G`** — Edit input in external editor
- **`Ctrl+O`** — Toggle tool output
- **`Ctrl+T`** — Toggle todo list
- **`Shift+Tab`** — Toggle auto-approve
- **`/`** — Slash commands
- **`@`** — File path autocompletion

---

## Development

### Running Tests

```bash
# Run all tests
./scripts/run_pytest.sh tests

# With coverage
./scripts/run_pytest.sh tests --cov=core --cov=wizard

# Specific test
./scripts/run_pytest.sh tests/core/test_commands.py::test_help_handler
```

### Running Linters

```bash
# Format code
uv run ruff format core/ wizard/ tests/

# Check types
uv run pyright core/ wizard/

# Lint
uv run ruff check --fix core/ wizard/
```

### Building Extensions

Tools and Skills are scaffolded in:
- `vibe/core/tools/ucode/*.py` — Tool implementations
- `vibe/core/skills/ucode/*.md` — Skill definitions

See [docs/PHASE-A-QUICKREF.md](docs/PHASE-A-QUICKREF.md) for scaffolding templates.

### Debugging

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=debug
ucode STATUS

# Attach debugger
uv run debugpy -- bin/vibe SETUP
```

---

## Contributing

We welcome contributions! Please see:

- [CONTRIBUTING.md](CONTRIBUTING.md) — Guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community standards
- [docs/decisions/](docs/decisions/) — Design rationale
- [AGENTS.md](AGENTS.md) — Development agents & patterns

---

## Architecture

uDOS uses a boundary-first architecture:
- `core` for deterministic local behavior
- `wizard` for networked and managed behavior
- explicit integration surfaces instead of upstream runtime forking

Start here:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/ARCHITECTURE-INTEGRATION-REFERENCE.md](docs/ARCHITECTURE-INTEGRATION-REFERENCE.md)
- [docs/decisions/OK-GOVERNANCE-POLICY.md](docs/decisions/OK-GOVERNANCE-POLICY.md)

---

## Troubleshooting

**Dev Mode tooling not finding uDOS tools?**
```bash
# Check tool discovery
uv run python -c "from vibe.core.tools.tool_manager import ToolManager; print(ToolManager().resolve_local_tools_dir('vibe/core/tools/ucode'))"

# Verify config
cat .vibe/config.toml
```

**OK provider API errors?**
```bash
# Check your configured provider key and endpoint values
grep -E 'API_KEY|API_BASE_URL' .env ~/.vibe/.env 2>/dev/null
```

**Python runtime issues?**
```bash
# Rebuild the canonical .venv
rm -rf .venv
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev
```

See [docs/troubleshooting/](docs/troubleshooting/) for more.

---

## Resources

- **uDOS v1.5 rebaseline** — https://github.com/fredporter/uDOS
- **MCP Spec** — https://modelcontextprotocol.io
- **Credits** — [wiki/credits.md](wiki/credits.md)
- **Agent Skills** — https://agentskills.io

---

## License

This project integrates Dev Mode contributor tooling with uDOS (Apache 2.0).

All code is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

## Data & Privacy

Dev Mode tooling can send code and conversations to your configured OK provider endpoint.
- Review your provider's privacy policy and data terms.
- Disable telemetry: `enable_telemetry = false` in `~/.vibe/config.toml`

uDOS stores runtime data locally in `memory/` (git-ignored).

---

<div align="center">

**Questions?** Open an issue or visit [wiki/Home.md](wiki/Home.md)

Made with ❤️ for developers who want OK models + local knowledge

</div>
