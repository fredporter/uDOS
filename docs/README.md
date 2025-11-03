# uDOS Development Documentation

**Version**: v1.0.7
**Last Updated**: November 2, 2025

Welcome to the uDOS development documentation hub. All development, planning, and guide documents are organized here.

---

## 📁 Documentation Structure

```
dev/docs/
├── README.md (this file)
├── guides/           # User and developer guides
├── planning/         # Development planning documents
└── archive/          # Historical refactoring documents
```

---

## 📖 User Guides

### Getting Started
- [`CONTRIBUTING.md`](guides/CONTRIBUTING.md) - How to contribute to uDOS
- [`TESTING.md`](guides/TESTING.md) - Testing procedures and standards
- [Quick Start Guide](../../wiki/Quick-Start.md) - Get up and running quickly

### Core Features
- [`DEVELOPMENT.md`](guides/DEVELOPMENT.md) - Development setup and workflow
- [Command Reference](../../wiki/Command-Reference.md) - Complete command documentation
- [uCODE Language](../../wiki/uCODE-Language.md) - Scripting language guide

### Advanced Topics
- [Architecture](../../wiki/Architecture.md) - System architecture overview
- [Mapping System](../../wiki/Mapping-System.md) - NetHack-style navigation
- [Style Guide](../../wiki/Style-Guide.md) - Code and design standards

---

## 🗺️ Planning Documents

### Current Development
- [`uDOS Dev Plan.md`](planning/uDOS%20Dev%20Plan.md) - Core v1.0.0 development plan
- [`../../ROADMAP.MD`](../../ROADMAP.MD) - **v1.0.x systematic development roadmap**

### Development Rounds (v1.0.x)
Each round focuses on one component with complete cycle:
1. **v1.0.1** - System Commands
2. **v1.0.2** - File Operations
3. **v1.0.3** - Assistant Integration
4. **v1.0.4** - Map System
5. **v1.0.5** - Web Server Infrastructure
6. **v1.0.6** - CLI Terminal Features
7. **v1.0.7** - Web Dashboard
8. **v1.0.8** - Web Terminal
9. **v1.0.9** - Markdown Viewer
10. **v1.0.10** - Font Editor
11. **v1.0.11** - Typo Editor
12. **v1.0.12** - Knowledge System
13. **v1.0.13** - Theme System
14. **v1.0.14** - Extension System
15. **v1.0.15** - uCODE Language
16. **v1.0.16** - Security & Permissions
17. **v1.1.0** - Stable Release

See [ROADMAP.MD](../../ROADMAP.MD) for detailed breakdown of each round.

---

## 📚 Archive

Historical documents and refactoring notes:
- [`REFACTORING-v1.0.0.md`](archive/REFACTORING-v1.0.0.md) - Major command system refactoring

---

## 🔧 Additional Resources

### Wiki
Complete documentation in [`/wiki`](../../wiki/):
- [Home](../../wiki/Home.md)
- [FAQ](../../wiki/FAQ.md)
- [Command Reference](../../wiki/Command-Reference.md)

### Examples
Sample scripts and configurations in [`/examples`](../../examples/)

### Extensions
Web and native extensions in [`/extensions`](../../extensions/)

---

## 🎯 Development Workflow

### Testing Each Round
```bash
# 1. Start uDOS
./start_udos.sh

# 2. Test component commands
[SYSTEM|HELP]
[FILE|NEW]
[ASSISTANT|ASK*feedback]

# 3. Document findings
# Log to memory/research/
# Update wiki as needed

# 4. Iterate and improve
```

### Using Assistant for Feedback
```bash
[ASSISTANT|ANALYZE*current_feature]
[ASSISTANT|EXPLAIN*what could be improved]
[ASSISTANT|DEBUG*error_message]
```

---

## 📝 Contributing

See [`CONTRIBUTING.md`](guides/CONTRIBUTING.md) for:
- Code style guidelines
- Pull request process
- Testing requirements
- Documentation standards

---

## 📧 Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions
- **Wiki**: Browse detailed documentation at `/wiki`

---

**Last Updated**: November 2, 2025
**Version**: v1.0.7
