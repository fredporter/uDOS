# Development Getting Started Guide

Welcome to uDOS + Vibe development! This guide covers setup, project structure, and common workflows.

## Quick Setup (30 seconds)

```bash
# Clone
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Install
uv sync --extra udos-wizard

# Run setup
uv run ./uDOS.py SETUP
```

## What You Get

After setup:
- `~/.vibe/config.toml` — Vibe configuration
- `~/.vibe/.env` — API keys (auto-generated)
- `memory/vault/` — Local knowledge base
- `core/` — uDOS commands ready to call

## Folder Navigation

**Start here:**
- `README.md` — Project overview (you are here)
- `docs/ARCHITECTURE.md` — How everything works
- `docs/INTEGRATION-READINESS.md` — Pre-requisites met
- `AGENTS.md` — Development patterns

**Common workflows:**
- Running tests → `uv run pytest tests/`
- Linting → `uv run ruff check --fix .`
- Building tools → `vibe/core/tools/ucode/*.py`
- Building skills → `vibe/core/skills/ucode/*.md`

**Documentation:**
- User guides → `wiki/Home.md`
- Specifications → `docs/specs/`
- Decisions → `docs/decisions/`
- How-to guides → `docs/howto/`

## First Commands

```bash
# See what vibe can do
vibe --help

# Run interactively
vibe

# Try a quick prompt
vibe --prompt "What tools do you have?"

# Check status
uv run ./uDOS.py STATUS
```

## Python Environment

All commands should use `uv`:

```bash
# Run Python scripts
uv run python script.py

# Run pytest
uv run pytest tests/

# Install dependencies
uv add package_name

# Activate venv (if you prefer)
source venv/bin/activate
```

Vibe-dev workspace auto-activates the venv (`vibe-dev.code-workspace`).

## Project Structure at a Glance

```
uDOS/
├── vibe/               # Mistral Vibe (never modify directly)
├── core/               # uDOS core (main development area)
│   ├── commands/       # 50+ command handlers
│   ├── framework/      # Service layer + base classes
│   └── tests/          # Tests for core/
├── wizard/             # Vibe integration server
├── docs/               # Development documentation
├── tests/              # Integration tests
├── wiki/               # User guides (Obsidian format)
└── vault/              # Knowledge vault template
```

**Golden Rule:** Never modify `vibe/*` directly. All custom code lives in `core/`, `wizard/`, or addon paths (`vibe/core/tools/ucode/`, `vibe/core/skills/ucode/`).

## Common Tasks

### Run Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific file
uv run pytest tests/core/test_commands.py -v

# With coverage
uv run pytest tests/ --cov=core --cov=wizard
```

### Format & Lint

```bash
# Auto-format
uv run ruff format core/ wizard/ tests/

# Lint (with fixes)
uv run ruff check --fix core/ wizard/

# Type check
uv run pyright core/ wizard/
```

### Create a New Command

1. Implement in `core/commands/my_command.py`
2. Register in `core/commands/__init__.py`
3. Add tests in `tests/core/test_my_command.py`
4. Test: `uv run ./uDOS.py MYCMD`

See `docs/PHASE-A-QUICKREF.md` for templates.

### Create a New Tool

1. Scaffold in `vibe/core/tools/ucode/my_tool.py`
2. Inherit from `BaseTool`
3. Implement `run()` method
4. Test: `vibe --enabled-tools "my_tool" --prompt "use my tool"`

### Create a New Skill

1. Create `vibe/core/skills/ucode/my-skill/SKILL.md`
2. Write YAML frontmatter + description
3. Optionally add implementation
4. Test with `vibe` shell

## Debugging

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=debug
vibe --prompt "test"

# Run with debugger
uv run debugpy -- ./uDOS.py SETUP

# Python REPL with full context
uv run python -i -c "from core.commands import CommandDispatcher; cd = CommandDispatcher()"
```

## Editor Setup

### VS Code

Open `vibe-dev.code-workspace`:
```bash
code vibe-dev.code-workspace
```

This auto-activates the venv and sets uDOS environment variables.

### Cursor

Same as VS Code; workspace config works fine.

### CLI Only

Set env vars:
```bash
export UDOS_ROOT="$(pwd)"
export PYTHONPATH="$UDOS_ROOT:$PYTHONPATH"
source venv/bin/activate
```

## Git Workflow

```bash
# Create a feature branch
git checkout -b feature/my-feature

# Make changes, test, commit
git add .
git commit -m "feat: my feature"

# Push and open PR
git push origin feature/my-feature
```

Follow [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Next Steps

- **Learn the architecture** → [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Build your first tool** → [docs/PHASE-A-QUICKREF.md](../docs/PHASE-A-QUICKREF.md)
- **Track active execution plan** → [docs/roadmap.md](../docs/roadmap.md)
- **Read project decisions** → [docs/decisions/](../docs/decisions/)

## Questions?

- Check [wiki/Home.md](../wiki/Home.md) for user guides
- Search [docs/](../docs/) for architecture / design docs
- Open an issue with details

Happy coding! ✨
