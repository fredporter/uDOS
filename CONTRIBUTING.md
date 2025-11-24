# Contributing to uDOS

Thank you for your interest in contributing to uDOS! This document provides guidelines for contributing to the project.

## Project Overview

uDOS v1.1.2 is a secure, dual-interface CLI framework with:
- **1,062 passing tests** (100% coverage)
- Enterprise security (RBAC, 4-tier encryption)
- Dual interface (Terminal + Web GUI)
- Offline knowledge management
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
│   ├── game-mode/  # Game mode extension
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

5. **Test your changes**
   ```bash
   # Run all tests
   pytest memory/tests/

   # Run specific test suite
   pytest memory/tests/test_v1_1_2_*.py

   # With coverage
   pytest memory/tests/ --cov=core --cov-report=html
   ```

6. **Submit a pull request**
   - Push your branch to your fork
   - Create a pull request with clear description
   - Reference any related issues

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
docs(wiki): Update installation guide for v1.1.2
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

## Testing Guide

### Running Tests
```bash
# All tests
pytest memory/tests/

# Specific milestone
pytest memory/tests/test_v1_1_0_*.py  # v1.1.0 (268 tests)
pytest memory/tests/test_v1_1_1_*.py  # v1.1.1 (327 tests)
pytest memory/tests/test_v1_1_2_*.py  # v1.1.2 (467 tests)

# With coverage
pytest memory/tests/ --cov=core --cov-report=html

# Specific test file
pytest memory/tests/test_v1_1_2_rbac.py -v

# Specific test function
pytest memory/tests/test_v1_1_2_rbac.py::TestRBAC::test_role_creation -v
```

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
- [Release v1.1.2](wiki/Release-v1.1.2.md)
- [Latest Development](wiki/Latest-Development.md)
- [ROADMAP](ROADMAP.MD)

### Development
- [Testing Guide](dev/docs/guides/TESTING.md) (if available)
- [Style Guide](dev/docs/guides/STYLE.md) (if available)

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
