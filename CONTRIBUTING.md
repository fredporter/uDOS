# Contributing to uDOS

## Project Structure

The project follows a clear organization:
```
uDOS/
├── core/           # Core system
├── extensions/     # Extension system
│   ├── bundled/   # Built-in extensions
│   ├── cloned/    # Third-party extensions
│   └── core/      # Shared components
├── knowledge/demos/ # Example scripts & demos
├── extensions/templates/ # Extension scaffolding
├── docs/          # Documentation
├── memory/        # System memory & tests
└── wiki/          # Project wiki
```

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Development Guidelines

### Code Style
- Follow Python style guide (PEP 8)
- Use consistent naming conventions
- Include docstrings and comments
- Keep functions focused and modular

### Testing
- Add tests for new features
- Place tests in `memory/tests/`
- Run full test suite before submitting
- Include example usage

### Documentation
- Update relevant documentation
- Add docstrings to new code
- Include examples where appropriate
- Update wiki if needed

### Extensions
- Use provided templates
- Follow core component guidelines
- Include comprehensive docs
- Add example usage

## Extension Development

### Using Templates
1. Choose appropriate template:
   ```bash
   cp -r extensions/templates/web-extension-template extensions/bundled/web/my-extension
   ```

2. Update manifest.json
3. Implement features
4. Add documentation
5. Include tests

### Core Components
- Use shared components from `extensions/core/`
- Follow theme guidelines
- Use grid system where appropriate
- Implement proper error handling

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Follow code style
4. Update CHANGELOG.md
5. Submit PR with clear description

## Resources

- [Documentation Guide](docs/guides/documentation.md)
- [Testing Guide](docs/guides/testing.md)
- [Style Guide](docs/guides/style.md)

## Questions?

- Open an issue
- Check existing documentation
- Ask in discussions
- Read the wiki
