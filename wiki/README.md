# uDOS Public Wiki

**Version:** v1.0.7.0  
**Last Updated:** 2026-01-24  
**Status:** Active Reference

The uDOS public wiki contains user guides, development documentation, and community resources.

---

## 📚 Core Documentation

### Getting Started
- **[QUICKSTART.md](../QUICKSTART.md)** — Get uDOS running in 5 minutes
- **[INSTALLATION.md](../INSTALLATION.md)** — Detailed installation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design and component organization

### Contributing
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute code and documentation
- **[STYLE-GUIDE.md](STYLE-GUIDE.md)** — Code style and standards
- **[VISION.md](VISION.md)** — Vision and philosophy

---

## 🏗️ Architecture Standards

Core architectural specifications for understanding how uDOS is designed:

- **[Layer Architecture](architecture/LAYER-ARCHITECTURE.md)** — Fractal grid system, 000-799 layers, coordinate precision
- **[Filesystem Architecture](architecture/FILESYSTEM-ARCHITECTURE.md)** — System vs user data, directory structure
- **[Database Architecture](architecture/DATABASE-ARCHITECTURE.md)** — SQLite ecosystem, schema, cross-linking
- **[Knowledge Linking System](architecture/KNOWLEDGE-LINKING-SYSTEM.md)** — Self-indexing documents, frontmatter schema
- **[uDOS.md Format](architecture/UDOS-MD-FORMAT.md)** — Executable document format
- **[uDOS.md Templates](architecture/UDOS-MD-TEMPLATE-SPEC.md)** — Shortcodes, variable interpolation

See **[architecture/README.md](architecture/README.md)** for full architecture index.

---

## 📖 Topics by Category

### Commands & TUI
- [Command Reference](commands/README.md) — All 92+ commands
- [TUI Guide](tui/README.md) — Terminal UI usage

### App Development
- [App Guide](app/README.md) — Tauri/Svelte frontend

### Wizard Server
- [Wizard Guide](wizard/README.md) — Always-on server features


---

## 📋 Directory Structure

```
wiki/
├── README.md                    # This file
├── ARCHITECTURE.md              # Component organization
├── CONTRIBUTING.md              # How to contribute
├── STYLE-GUIDE.md              # Code standards
├── VISION.md                    # Philosophy
├── CONFIGURATION.md            # System configuration
├── CREDITS.md                  # Attribution
├── architecture/               # Architecture standards
│   ├── README.md
│   ├── LAYER-ARCHITECTURE.md
│   ├── FILESYSTEM-ARCHITECTURE.md
│   ├── DATABASE-ARCHITECTURE.md
│   ├── KNOWLEDGE-LINKING-SYSTEM.md
│   ├── UDOS-MD-FORMAT.md
│   └── UDOS-MD-TEMPLATE-SPEC.md
├── commands/                   # Command docs
│   └── README.md
├── app/                        # App development
│   └── README.md
├── tui/                        # TUI guide
│   └── README.md
├── wizard/                     # Wizard Server
│   └── README.md
└── tinycore/                   # Deployment
    └── README.md
```

---

## 🔍 See Also

**Root Repository:**
- [README.md](../README.md) — Project overview
- [AGENTS.md](../AGENTS.md) — How work is done
- [QUICKSTART.md](../QUICKSTART.md) — 5-minute start
- [INSTALLATION.md](../INSTALLATION.md) — Installation guide

**Engineering Documentation:**
- [docs/](../docs/) — Engineering spine
- [docs/development-streams.md](../docs/development-streams.md) — Current roadmap
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) — AI guidelines

**Private Development:**
- [dev/wiki/](../dev/wiki/) — Development wiki
- [dev/roadmap/](../dev/roadmap/) — Detailed roadmap

---

**Status:** Active Wiki  
**Version:** v1.0.7.0  
**Updated:** 2026-01-24  
**Maintained by:** uDOS Community  
**Repository:** https://github.com/fredporter/uDOS  
**License:** [LICENSE.txt](../LICENSE.txt)
- **MeshCore Deployment** - Deploying and running MeshCore
- **Plugin Installation** - Installing and managing plugins
- **Library Management** - Managing local /library integrations

---

## 🔍 Troubleshooting

Common issues, debugging, and recovery procedures.

- **Disk Issues** - Diagnosing and fixing disk-related problems
- **Network Issues** - Troubleshooting network connectivity problems
- **Boot Problems** - Recovering from boot failures
- **System Recovery** - Advanced recovery and repair procedures
- **Getting Help** - Resources for asking questions and reporting issues

---

## 📚 Reference

Technical specifications and reference material.

- **Alpine Packages** - Common Alpine APK packages and their usage
- **Command Reference** - Complete reference of uDOS commands
- **File Structure** - Overview of uDOS file and directory structure
- **Glossary** - Terms and definitions used in uDOS

---

## Contributing

This wiki is provisioned via the **Wizard Server** at `/api/v1/wiki/provision`.

**Content Status:** 📝 All pages are currently stubs and need content

**Wiki Structure:** Auto-generated by WikiProvisioningService
**Last Update:** Auto-managed via Wizard Server API

**To contribute:**

1. Access Wizard Dashboard → Wiki section
2. Use "Provision Wiki" to initialize structure
3. Edit markdown files in `/wiki/pages/`
4. Submit pull requests via GitHub

---

_For engineering documentation and specifications, see the main [docs/](../docs/) directory._
