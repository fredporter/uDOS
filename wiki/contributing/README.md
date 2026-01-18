# Contributing to uDOS

> **Version:** Core v1.0.0.64

Thank you for your interest in contributing to uDOS! This guide covers how to get started.

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
./start_udos.sh
```

---

## Development Setup

### Prerequisites

| Tool | Version | Purpose |
| ---- | ------- | ------- |
| Python | 3.10+ | Core runtime |
| Node.js | 18+ | App development |
| Rust | Latest | Tauri backend |
| Git | 2.x | Version control |

### VS Code Workspace

Open the workspace file:

```bash
code uDOS-Alpha.code-workspace
```

Or for app-focused development:

```bash
code uDOS-Alpha-Tauri.code-workspace
```

### Tasks

Available VS Code tasks:

| Task | Description |
| ---- | ----------- |
| Run uDOS Interactive | Start TUI |
| Run Shakedown Test | Run test suite |
| Check All Versions | Show component versions |
| Tail Session Logs | Follow debug logs |

---

## Code Style

### Python

Follow the [Style Guide](STYLE-GUIDE.md):

```python
# Good
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

### TypeScript (App)

```typescript
// Good
export async function loadDocument(path: string): Promise<Document> {
  const content = await readFile(path);
  return parseDocument(content);
}
```

### Commit Messages

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

Examples:

```
feat(bundle): Add drip delivery scheduling
fix(tui): Resolve pager scroll issue
docs(wiki): Add WELLBEING command docs
```

---

## Project Structure

### Key Directories

```
uDOS/
├── core/               # Core TUI system
│   ├── commands/      # Command handlers
│   ├── services/      # Core services
│   └── ui/            # TUI components
├── extensions/
│   ├── api/           # REST/WebSocket API
│   └── transport/     # Network transports
├── wizard/            # Wizard Server
├── app/               # uCode Markdown App
├── knowledge/         # Knowledge Bank
├── memory/            # User data (gitignored)
└── wiki/              # Documentation
```

### Adding a New Command

1. **Create handler** in `core/commands/`:

```python
# core/commands/example_handler.py
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

2. **Register** in `core/uDOS_commands.py`:

```python
# Add import
from core.commands.example_handler import ExampleHandler

# Add to __init__
self.example_handler = ExampleHandler(**handler_kwargs)

# Add routing
elif module == "EXAMPLE":
    return self.example_handler.handle(command, params, grid, parser)
```

3. **Add to commands.json**:

```json
{
  "NAME": "EXAMPLE",
  "SYNTAX": "EXAMPLE HELLO [name]",
  "DESCRIPTION": "Example command",
  "EXAMPLES": ["EXAMPLE HELLO", "EXAMPLE HELLO uDOS"]
}
```

4. **Document** in wiki:

```markdown
## EXAMPLE

Example command for demonstration.

### Syntax
EXAMPLE HELLO [name]
```

5. **Test**:

```bash
./start_udos.sh -c "EXAMPLE HELLO World"
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

### Writing Tests

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

## Versioning

### Component Versions

Each component is versioned independently:

```bash
# Check versions
python -m core.version check

# Bump version
python -m core.version bump core build
```

### Version Format

`MAJOR.MINOR.PATCH.BUILD`

- **MAJOR**: Breaking changes
- **MINOR**: New features
- **PATCH**: Bug fixes
- **BUILD**: Incremental builds

---

## Pull Requests

### Before Submitting

- [ ] Tests pass: `python -m pytest`
- [ ] Code formatted: Follow style guide
- [ ] Version bumped if needed
- [ ] Documentation updated
- [ ] Commit messages follow format

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
- [ ] Version bumped
```

---

## Getting Help

### Resources

- **Wiki**: This documentation
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

### Debugging

```bash
# Check session logs
tail -f memory/logs/session-commands-$(date +%Y-%m-%d).log

# Enable debug mode
export UDOS_DEBUG=1
./start_udos.sh
```

---

## Code of Conduct

- Be respectful
- Be constructive
- Focus on the code, not the person
- Help newcomers
- Keep it professional

---

## License

uDOS is licensed under [LICENSE.txt](../LICENSE.txt).

By contributing, you agree that your contributions will be licensed under the same license.

---

*Part of the [uDOS Wiki](README.md)*
