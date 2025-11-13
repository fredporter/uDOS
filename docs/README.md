# uDOS Documentation

> **📚 The wiki is now the single source of truth for all uDOS documentation.**

---

## 🎯 Quick Links

### For Users
- **[Wiki Home](../wiki/Home.md)** - Start here
- **[Quick Start](../wiki/Quick-Start.md)** - Get up and running
- **[Command Reference](../wiki/Command-Reference.md)** - All commands
- **[Philosophy](../wiki/Philosophy.md)** - Why uDOS exists

### For Developers
- **[Contributing](../wiki/Contributing.md)** - How to contribute
- **[Dev Rounds Workflow](../wiki/Dev-Rounds-Workflow.md)** - Development process
- **[Architecture](../wiki/Architecture.md)** - System design
- **[Style Guide](../wiki/Style-Guide.md)** - Code standards

### For Everyone
- **[FAQ](../wiki/FAQ.md)** - Common questions
- **[ROADMAP](../ROADMAP.MD)** - Development roadmap
- **[Wiki README](../wiki/README.md)** - Complete documentation index

---

## 📁 This Directory (docs/)

This directory now contains:

- **archive/** - Historical refactoring documents (v1.0.0-v1.0.3)
- **development/** - Session summaries and development logs
- **releases/** - Release notes and changelogs
- **guides/** - Legacy guides (being migrated to wiki)
- **planning/** - Internal planning documents

**For current documentation, always use the wiki.**

---

## 🔄 Migration Status

All active documentation has been migrated to the wiki:
- ✅ User guides → wiki/
- ✅ Command references → wiki/Command-Reference.md
- ✅ Philosophy & rationale → wiki/Philosophy.md, wiki/Why-uDOS.md
- ✅ Development workflow → wiki/Dev-Rounds-Workflow.md
- ✅ Contributing guidelines → wiki/Contributing.md

Historical documents remain in docs/ for reference only.
3. **v1.0.3** - Grid System (GRID, NEW GRID, GRID LIST, SHOW GRID)
4. **v1.0.4** - Navigation (MAP, GOTO, MOVE, LEVEL, GODOWN, GOUP)
5. **v1.0.5** - Assisted Task (OK, READ)
6. **v1.0.6** - Automation (RUN)
7. **v1.0.7** - History (UNDO, REDO, RESTORE)
8. **v1.0.8** - Utilities (HELP enhancements, CLEAR, SETUP)

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
