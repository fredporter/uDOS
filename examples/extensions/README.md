# uDOS Extension Templates

Reference templates for creating new uDOS extensions.

## Available Templates

### 1. Web Extension Template
Template for creating web-based extensions with HTML/CSS/JavaScript frontend and Python/Flask backend.
- Location: [web-extension-template/](web-extension-template/)
- Features: Web interface, REST API, WebSocket support, theme integration

### 2. CLI Extension Template
Template for creating command-line extensions that integrate with uDOS core.
- Location: [cli-extension-template/](cli-extension-template/)
- Features: Command-line interface, core integration, help system

## Using the Templates

1. Choose a template based on your needs:
   - Web-based interface → web-extension-template
   - Command-line tool → cli-extension-template

2. Copy the template to your extensions directory:
   ```bash
   # For web extensions:
   cp -r examples/extensions/web-extension-template extensions/my-extension

   # For CLI extensions:
   cp -r examples/extensions/cli-extension-template extensions/my-cli-tool
   ```

3. Follow the README in your chosen template for specific setup instructions.

## Extension Guidelines

### General Guidelines
- Follow uDOS naming conventions
- Include complete documentation
- Implement proper error handling
- Add appropriate tests

### Web Extensions
- Use uDOS grid system
- Support all core themes
- Follow REST API patterns
- Implement WebSocket for real-time features

### CLI Extensions
- Follow command syntax standards
- Implement help system
- Support offline mode
- Include progress indicators

## Development Workflow

1. Copy template
2. Update manifest.json
3. Implement features
4. Add tests
5. Update documentation
6. Submit for review

## Resources

- [Extension Development Guide](../../docs/guides/extension-development.md)
- [API Reference](../../docs/api-reference.md)
- [Theme Guidelines](../../docs/guides/theme-guidelines.md)

## Contributing

To improve these templates:
1. Fork the repository
2. Make your changes
3. Submit a pull request

## License

These templates are part of uDOS, licensed under MIT.
