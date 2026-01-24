# Contributing to uDOS

**Version:** Core v1.0.0.65
**Last Updated:** 2026-01-24
**Status:** Active Guidelines

Thank you for your interest in contributing to uDOS! This guide covers how to get started, from setup to submitting pull requests.

---

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/udos.git
cd udos

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run tests
python -m pytest

# 5. Start TUI
./bin/start_udos.sh
```

---

## Development Setup

### Prerequisites

| Tool    | Version | Purpose         |
| ------- | ------- | --------------- |
| Python  | 3.10+   | Core runtime    |
| Node.js | 18+     | App development |
| Rust    | Latest  | Tauri backend   |
| Git     | 2.x     | Version control |

### VS Code Workspace

Open the main workspace:

```bash
code uDOS.code-workspace
```

### Available Tasks

| Task                    | Description                |
| ----------------------- | -------------------------- |
| 🏠 Run uDOS Interactive | Start TUI                  |
| 🧙 Start Wizard Server  | Run Wizard on port 8765    |
| 🖥️ App: Tauri Dev       | Launch app dev mode        |
| 🧪 Run Shakedown Test   | Run 47-test suite          |
| 📊 Check All Versions   | Display component versions |
| 📝 Tail Session Logs    | Follow debug logs          |

---

## Code Style

### Python

Follow [STYLE-GUIDE.md](STYLE-GUIDE.md):

```python
# Good: Clear purpose, proper logging
def handle_command(self, command: str, params: list) -> dict:
    """Handle a command with the given parameters."""
    logger = get_logger('command-handler')
    logger.info(f"[LOCAL] Processing: {command}")

    try:
        result = self._process(command, params)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[ERROR] {command} failed: {e}")
        return {"status": "error", "message": str(e)}
```

**Key Rules:**

- Use type hints
- Log with proper tags: `[LOCAL]`, `[MESH]`, `[WIZ]`, etc.
- No hardcoded version strings (use version manager)
- Follow PEP 8 with 4-space indentation

### TypeScript (App)

```typescript
// Good
export async function loadDocument(path: string): Promise<Document> {
  const content = await readFile(path);
  return parseDocument(content);
}
```

**Key Rules:**

- Use TypeScript strict mode
- Export types from `$lib/types/`
- Test with Vitest

### Commit Messages

Format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**

- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `refactor` — Code refactoring
- `test` — Adding tests
- `chore` — Maintenance

**Examples:**

```
feat(bundle): Add drip delivery scheduling
fix(tui): Resolve pager scroll issue
docs(wiki): Add WELLBEING command documentation
refactor(api): Simplify file route handlers
```

---

## Project Structure

### Key Directories

```
uDOS/
├── core/               # Core TUI system
│   ├── commands/      # 92+ command handlers
│   ├── services/      # 140+ services
│   ├── ui/            # TUI components
│   └── version.json
├── extensions/
│   ├── api/           # REST/WebSocket API
│   └── transport/     # MeshCore, audio, QR
├── wizard/            # Wizard Server
├── app/               # Desktop app (Tauri)
├── knowledge/         # 240+ knowledge articles
├── memory/            # User data (gitignored)
├── wiki/              # Public documentation
└── docs/              # Engineering spine
```

---

## Adding a New Command

### 1. Create Handler

Create `core/commands/example_handler.py`:

```python
from core.commands.base_handler import BaseCommandHandler

class ExampleHandler(BaseCommandHandler):
    def handle(self, command, params, grid, parser):
        if command == "HELLO":
            return self._handle_hello(params)
        return {"status": "error", "message": "Unknown command"}

    def _handle_hello(self, params):
        name = params[0] if params else "World"
        return {"status": "success", "message": f"Hello, {name}!"}
```

### 2. Register in Router

Edit `core/uDOS_commands.py`:

```python
from core.commands.example_handler import ExampleHandler

# In __init__:
self.example_handler = ExampleHandler(**handler_kwargs)

# In routing:
elif module == "EXAMPLE":
    return self.example_handler.handle(command, params, grid, parser)
```

### 3. Add to Commands Index

Edit `core/commands.json`:

```json
{
  "NAME": "EXAMPLE",
  "SYNTAX": "EXAMPLE HELLO [name]",
  "DESCRIPTION": "Example greeting command",
  "EXAMPLES": ["EXAMPLE HELLO", "EXAMPLE HELLO uDOS"]
}
```

### 4. Document

Edit `wiki/commands/README.md`:

```markdown
## EXAMPLE

Example command for demonstration.

### Syntax

EXAMPLE HELLO [name]

### Examples

EXAMPLE HELLO World
```

### 5. Test

```bash
./bin/start_udos.sh
> EXAMPLE HELLO World
Hello, World!
```

---

## Testing

### Run All Tests

```bash
source .venv/bin/activate
python -m pytest
```

### Run Specific Tests

```bash
# By file
python -m pytest core/tests/test_commands.py

# By marker
python -m pytest -m integration

# With coverage
python -m pytest --cov=core
```

### Write Tests

```python
# tests/test_example.py
import pytest
from core.commands.example_handler import ExampleHandler

class TestExampleHandler:
    def setup_method(self):
        self.handler = ExampleHandler()

    def test_hello_default(self):
        result = self.handler.handle("HELLO", [], None, None)
        assert result["status"] == "success"
        assert "Hello, World" in result["message"]

    def test_hello_with_name(self):
        result = self.handler.handle("HELLO", ["uDOS"], None, None)
        assert "Hello, uDOS" in result["message"]
```

---

## Version Management

### Check Versions

```bash
python -m core.version check    # All components
python -m core.version show     # Dashboard
```

### Bump Version

```bash
python -m core.version bump core build    # Build: v1.0.0.65 → v1.0.0.66
python -m core.version bump api patch     # Patch: v1.0.0.0 → v1.0.1.0
python -m core.version bump app minor     # Minor: v1.0.6.1 → v1.1.0.0
```

**Format:** `MAJOR.MINOR.PATCH.BUILD`

---

## Pull Request Process

### Before Submitting

- [ ] Tests pass: `python -m pytest`
- [ ] Code follows style guide
- [ ] Version bumped (if needed)
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] Logging uses proper tags

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing

How was this tested?

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Version bumped (if needed)
- [ ] Code follows style guide
- [ ] Commit messages formatted
```

### Review Process

1. **Automated checks** run first (tests, linting)
2. **Code review** by maintainers
3. **Approval** required to merge
4. **Squash and merge** to main

---

## Debugging

### Check Session Logs

```bash
# Follow real-time logs
tail -f memory/logs/session-commands-$(date +%Y-%m-%d).log

# Check API logs
tail -f memory/logs/api_server.log

# Check system logs
tail -f memory/logs/system-$(date +%Y-%m-%d).log
```

### Enable Debug Mode

```bash
export UDOS_DEBUG=1
./bin/start_udos.sh
```

### Common Issues

| Issue              | Solution                                            |
| ------------------ | --------------------------------------------------- |
| Import errors      | Activate venv: `source .venv/bin/activate`          |
| Version conflicts  | Run: `python -m core.version check`                 |
| TUI not responsive | Check `session-commands-*.log`                      |
| API not responding | Verify Wizard running: `curl localhost:8765/health` |

---

## Getting Help

### Resources

| Resource                           | Purpose           |
| ---------------------------------- | ----------------- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design     |
| [STYLE-GUIDE.md](STYLE-GUIDE.md)   | Code standards    |
| [wiki/commands/](commands/)        | Command reference |
| [docs/](../docs/)                  | Engineering spine |
| [AGENTS.md](../AGENTS.md)          | Development rules |

### Community

- **Issues** — GitHub Issues for bugs/features
- **Discussions** — GitHub Discussions for questions
- **Wiki** — This documentation

---

## Code of Conduct

- ✅ Be respectful and constructive
- ✅ Focus on the code, not the person
- ✅ Help newcomers learn
- ✅ Keep it professional
- ❌ No harassment, discrimination, or abuse

---

## License

uDOS is licensed under [LICENSE.txt](../LICENSE.txt).

By contributing, you agree that your contributions will be licensed under the same license.

---

## What's Next?

- Review [STYLE-GUIDE.md](STYLE-GUIDE.md) for code standards
- Explore [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Check [open issues](https://github.com/fredporter/udos/issues) for tasks
- Read [VISION.md](VISION.md) to understand the philosophy

Welcome to the uDOS community! 🚀

---

**Status:** Active Guidelines
**Maintained by:** uDOS Engineering
**Repository:** https://github.com/fredporter/uDOS
