# Contributing to uDOS

Thank you for your interest in contributing to uDOS! This document provides guidelines for contributing to the project.

## Project Overview

uDOS v1.2.4 is a secure, offline-first operating system for survival knowledge with:
- **Extension Hot Reload System** (v1.2.4) - No full restarts needed
- **GitHub Browser Integration** - Direct feedback via browser
- **Visual Mode Indicators** - Color-coded prompts (regular/dev/assist)
- **1,810+ passing tests** (100% coverage)
- Sandbox architecture with 4-tier knowledge system
- DEV MODE with authentication and permissions
- Offline knowledge management (136+ guides)
- Cross-platform support (macOS/Linux/Windows)

## Project Structure

```
uDOS/
├── core/           # Core system (Python)
│   ├── commands/   # Command handlers (60+ commands)
│   ├── services/   # Core services (security, AI, analytics)
│   ├── input/      # Input handling
│   ├── output/     # Output formatting
│   ├── knowledge/  # Knowledge management
│   ├── network/    # API services
│   ├── ui/         # UI components
│   ├── theme/      # Theme system
│   └── utils/      # Utilities
├── extensions/     # Extension system
│   ├── core/       # Core extensions (terminal, web GUI)
│   ├── play/       # Play extension (game mechanics)
│   └── templates/  # Extension scaffolding
├── knowledge/      # Knowledge library (8 categories, 74+ guides)
├── memory/         # User workspace
│   ├── tests/      # Test suites (1,062 tests)
│   └── [tiers]/    # 4-tier memory system
├── wiki/           # Project wiki
└── dev/            # Development workspace
```

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/uDOS.git
   cd uDOS
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**
   - Write code following our style guide
   - Add tests for new features
   - Update documentation
   - **Use hot reload** for faster development (v1.2.4)

5. **Test your changes**
   ```bash
   # Run all tests
   pytest memory/tests/

   # Run SHAKEDOWN comprehensive validation
   ./start_udos.sh
   > SHAKEDOWN

   # With coverage
   pytest memory/tests/ --cov=core --cov-report=html
   ```

6. **Submit feedback or pull request**
   ```bash
   # Quick GitHub feedback (v1.2.4)
   > FEEDBACK --github --feature --open

   # Or traditional PR workflow
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where applicable
- Keep functions focused and modular (single responsibility)
- Use descriptive variable and function names
- Add docstrings to classes and functions

### Testing Requirements
- **100% test coverage required** for new features
- Place tests in `memory/tests/`
- Follow existing test patterns (see `test_v1_1_*.py`)
- Tests must pass on all platforms (macOS/Linux/Windows)
- Include edge case testing

### Documentation
- Update relevant documentation for changes
- Add docstrings to new code (Google style)
- Include usage examples where appropriate
- Update CHANGELOG.md with your changes
- Update wiki pages if needed

### Commit Messages
Use clear, descriptive commit messages:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(security): Add RBAC permission validation
fix(web): Correct WebSocket reconnection logic
docs(wiki): Update installation guide for v1.1.0
test(memory): Add 4-tier encryption test suite
```

## Extension Development

### Using Templates
1. **Choose appropriate template:**
   ```bash
   # CLI extension
   cp -r extensions/templates/cli-extension-template extensions/your-extension

   # Web extension
   cp -r extensions/templates/web-extension-template extensions/core/your-web-ext
   ```

2. **Update manifest/config**
3. **Implement features**
4. **Add comprehensive tests**
5. **Document usage**

### Extension Guidelines
- Use shared components from `extensions/core/`
- Follow theme system guidelines
- Implement proper error handling
- Include example usage in README
- Add tests (minimum 90% coverage)

## Hot Reload Workflow (v1.2.4)

### Development with Hot Reload

**No more full restarts!** Use hot reload for faster extension development:

```bash
# Reload a single extension after code changes
> REBOOT --extension assistant

# Reload all extensions
> REBOOT --extensions

# Validate changes without reloading (dry-run)
> REBOOT --extension assistant --validate

# Full system restart (if needed)
> REBOOT
```

### Hot Reload Features

1. **Targeted Reload** - Reload only the extension you're working on
2. **State Preservation** - Session variables and config preserved
3. **Automatic Rollback** - Reverts on import errors
4. **Dependency Validation** - Checks manifest and dependencies
5. **Health Checks** - Validates extension after reload

### Best Practices for Hot Reload

```python
# 1. Design for reloadability
class MyExtension:
    def __init__(self):
        # Initialize state here
        self.session_vars = {}

    def cleanup(self):
        # Clean up resources before reload
        pass

# 2. Use module-level state carefully
# Avoid global state that persists across reloads
# Use extension.session_vars instead

# 3. Test reload behavior
def test_extension_reload():
    # Load extension
    ext = load_extension('my-extension')

    # Modify code
    # ...

    # Reload and verify
    reload_extension('my-extension')
    ext = load_extension('my-extension')
    assert ext is not None
```

### When to Use Full Restart

Use `REBOOT` (full restart) when:
- Core system files changed (`core/uDOS_main.py`, `core/config.py`)
- Command routing changed (`core/uDOS_commands.py`)
- Major dependency updates
- Virtual environment changes

Use `REBOOT --extension` (hot reload) when:
- Extension code changed
- Extension commands changed
- Extension handlers modified
- Extension configuration updated

## Pull Request Process

1. **Update documentation**
   - README if user-facing changes
   - CHANGELOG.md with entry
   - Wiki pages if needed
   - Docstrings for new code

2. **Add/update tests**
   - New features require tests
   - Bug fixes require regression tests
   - All tests must pass

3. **Follow code style**
   - Run `flake8` or `pylint`
   - Format with `black` (optional)
   - Type check with `mypy` (recommended)

4. **Update CHANGELOG.md**
   - Add entry under "Unreleased" section
   - Follow Keep a Changelog format
   - Link to issues/PRs

5. **Submit PR with clear description**
   - What does this change?
   - Why is it needed?
   - How was it tested?
   - Any breaking changes?
   - Related issues?

## GitHub Feedback Integration (v1.2.4)

### Quick Feedback via Browser

**New in v1.2.4**: Submit feedback directly through GitHub without leaving uDOS:

```bash
# Report a bug (opens pre-filled GitHub Issue)
> FEEDBACK --github --bug --open

# Request a feature (opens pre-filled GitHub Issue)
> FEEDBACK --github --feature --open

# Ask a question (opens pre-filled GitHub Discussion)
> FEEDBACK --github --question --open

# Share an idea (opens pre-filled GitHub Discussion)
> FEEDBACK --github --idea --open

# Preview URL before opening
> FEEDBACK --github --bug  # Shows URL, requires --open to launch
```

### What Data is Sent?

**Minimal, non-sensitive data only:**
- uDOS version (e.g., "1.2.4")
- Operating system (e.g., "macOS 14.1")
- Python version (e.g., "3.11.5")
- Mode (e.g., "interactive")

**No API tokens required** - Everything stays local until you manually submit via browser.

### Local Feedback (Alternative)

Prefer to keep feedback local? Use the traditional command:

```bash
# Saves to memory/logs/user_feedback.jsonl
> FEEDBACK "Your feedback message here"
```

## Testing Guide

### Running Tests
```bash
# All tests
pytest memory/tests/

# SHAKEDOWN comprehensive validation (v1.2.4+)
./start_udos.sh
> SHAKEDOWN                    # Run all tests
> SHAKEDOWN --verbose          # Detailed output
> SHAKEDOWN --quick            # Core tests only
> SHAKEDOWN --report           # Generate JSON report

# Specific milestone
pytest memory/tests/test_v1_1_0_*.py  # v1.1.0 (268 tests)
pytest memory/tests/test_v1_1_1_*.py  # v1.1.1 (327 tests)

# With coverage
pytest memory/tests/ --cov=core --cov-report=html

# Specific test file
pytest memory/tests/test_v1_1_2_rbac.py -v

# Specific test function
pytest memory/tests/test_v1_1_2_rbac.py::TestRBAC::test_role_creation -v
```

### SHAKEDOWN Test Coverage (v1.2.4)

The SHAKEDOWN command provides comprehensive system validation:

- **Core Architecture** - Project structure, file organization
- **Planet System** - Workspace management
- **Asset Management** - Centralized library
- **DEV MODE** - Security system validation
- **Memory Structure** - 4-tier system
- **Database Locations** - Sandbox/user paths
- **Variable System** - SPRITE/OBJECT with JSON schemas
- **Handler Architecture** - Command routing
- **Play Extension** - STORY command, adventures
- **GENERATE System** - Offline-first AI
- **Performance** - Metrics, success criteria
- **Logging** - Unified logging system
- **Hot Reload** (v1.2.4) - Extension lifecycle, REBOOT variants
- **GitHub Feedback** (v1.2.4) - Browser integration, URL generation
- **Prompt Modes** (v1.2.4) - Visual indicators, color codes

**Total**: 100+ validation tests across 15+ subsystems

### Writing Tests
```python
import unittest
from core.services.rbac_manager import RBACManager

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.manager = RBACManager()

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_basic_functionality(self):
        """Test basic feature operation"""
        result = self.manager.some_method()
        self.assertTrue(result)

    def test_edge_case(self):
        """Test edge case handling"""
        with self.assertRaises(ValueError):
            self.manager.invalid_operation()

if __name__ == '__main__':
    unittest.main()
```

## Security Considerations

### Reporting Vulnerabilities
- **Do NOT create public issues for security vulnerabilities**
- Email security concerns privately to maintainers
- Include detailed description and reproduction steps
- Allow reasonable time for fix before disclosure

### Security Best Practices
- Never commit API keys or secrets
- Use environment variables for sensitive data
- Follow principle of least privilege
- Validate all user input
- Use parameterized queries (no SQL injection)
- Implement proper error handling (don't leak sensitive info)

## Code Review Process

All submissions require code review:
1. **Automated checks** must pass (tests, linting)
2. **Manual review** by maintainer
3. **Documentation** must be updated
4. **Tests** must have good coverage
5. **No breaking changes** without major version bump

## Resources

### Documentation
- [Architecture Overview](wiki/Architecture.md)
- [Developers Guide](wiki/Developers-Guide.md)
- [Extension Development](wiki/Extension-Development.md)
- [Hot Reload System](wiki/Hot-Reload.md) (v1.2.4)
- [GitHub Feedback Guide](wiki/GitHub-Feedback.md) (v1.2.4)
- [ROADMAP](dev/roadmap/ROADMAP.MD)

### Developer Experience (v1.2.4)

**Visual Mode Indicators** - Color-coded prompts:
- `›` - Regular mode (default color)
- `🔧 DEV›` - DEV mode (yellow)
- `🤖 OK›` - Assist mode (cyan)

**Hot Reload Workflow:**
```bash
# Edit extension code...
> REBOOT --extension my-extension  # Reload in <1 second
# Test changes immediately, no full restart!
```

**GitHub Integration:**
```bash
> FEEDBACK --github --bug --open   # Report bugs instantly
> FEEDBACK --github --feature      # Request features
```

**Comprehensive Testing:**
```bash
> SHAKEDOWN                        # 100+ validation tests
> SHAKEDOWN --verbose              # Detailed diagnostics
```

### Development Tips

1. **Use Hot Reload** - Save 10-30 seconds per test cycle
2. **Run SHAKEDOWN** - Catch integration issues early
3. **GitHub Feedback** - Share ideas/bugs without context switching
4. **Watch Modes** - Visual prompts prevent mistakes (DEV mode warnings)
5. **Iterate Fast** - Hot reload + SHAKEDOWN = rapid development

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the Code of Conduct
- Ask questions in Discussions
- Report bugs in Issues

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/fredporter/uDOS/issues)
- **Security issues**: Email maintainers privately
- **Documentation**: Check [wiki](wiki/) first

---

**Thank you for contributing to uDOS!**

We appreciate your time and effort in making uDOS better for everyone.
