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

### Configuration & Deployment
- [Configuration](CONFIGURATION.md) — System settings
- [Tiny Core Linux](tinycore/README.md) — Installation media

### Community & Credits
- [Credits](CREDITS.md) — Attribution and contributors

---

## 🔗 Quick Links

| Need | Resource |
|------|----------|
| **Installation** | [INSTALLATION.md](../INSTALLATION.md) |
| **Getting Started** | [QUICKSTART.md](../QUICKSTART.md) |
| **System Design** | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Code Style** | [STYLE-GUIDE.md](STYLE-GUIDE.md) |
| **All Commands** | [commands/README.md](commands/README.md) |
| **Architecture** | [architecture/](architecture/) |
| **License** | [LICENSE.txt](../LICENSE.txt) |

---

## 🚀 Common Tasks

### I want to...

**...start using uDOS**
→ Read [QUICKSTART.md](../QUICKSTART.md) then [INSTALLATION.md](../INSTALLATION.md)

**...understand the architecture**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) then [architecture/](architecture/)

**...contribute code**
→ Read [CONTRIBUTING.md](CONTRIBUTING.md) and [STYLE-GUIDE.md](STYLE-GUIDE.md)

**...learn a command**
→ See [commands/README.md](commands/README.md)

**...use the TUI**
→ See [tui/README.md](tui/README.md)

**...develop the app**
→ See [app/README.md](app/README.md)

**...deploy on Tiny Core**
→ See [tinycore/README.md](tinycore/README.md)
- **MeshCore Networking** - Setting up peer-to-peer mesh networks

---

## 🔧 Device Integration

Sonic devices, Bluetooth, NFC, and hardware flashing guides.

- **Sonic Device Setup** - Initial Sonic device configuration
- **Sonic Firmware Flashing** - Flashing custom firmware to Sonic devices
- **Bluetooth Pairing** - Pairing Bluetooth devices and peripherals
- **NFC Setup** - Setting up NFC readers and configuration
- **Device Discovery** - Finding and discovering network devices

---

## 🔌 Integrations & Plugins

Third-party services, containers, and library management.

- **Ollama Local AI** - Setting up Ollama for local AI models
- **Mistral Vibe Setup** - Configuring Mistral Vibe for offline AI
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
