# uDOS Wiki

**Python-venv OS layer for Tiny Core Linux**  
**Version:** Alpha v1.0.0.68  
**Status:** Active Development (v1.0.1.0 in progress)

---

## 📚 Wiki Structure

This wiki is organized into clear sections for different audiences:

### 🎯 Quick Start
| Document | Audience | Purpose |
|----------|----------|---------|
| [Vision](./VISION.md) | Everyone | What uDOS is and why |
| [Architecture](./ARCHITECTURE.md) | Developers | Directory structure & components |
| [Configuration](./CONFIGURATION.md) | All users | Settings & $variables |
| [Style Guide](./STYLE-GUIDE.md) | Contributors | Code & content standards |

### 🏗️ Architecture
| Document | Audience | Purpose |
|----------|----------|---------|
| [Architecture Docs](./architecture/README.md) | Developers | Database, filesystem, layers |

### 💻 User Guides
| Document | Audience | Purpose |
|----------|----------|---------|
| [TUI Guide](./tui/README.md) | TUI users | Terminal interface |
| [uCode Markdown App](./app/README.md) | Desktop users | Tauri desktop app |
| [Commands](./commands/README.md) | All users | Complete command reference |

### 📝 Content Commands
| Document | Audience | Purpose |
|----------|----------|---------|
| [Content Commands](./commands/content.md) | Users | GUIDE, BUNDLE, CAPTURE |
| [User Commands](./commands/user.md) | Users | WELLBEING, LOCATION |

### 🎨 Audio
| Document | Audience | Purpose |
|----------|----------|---------|
| [Groovebox](./groovebox/README.md) | Musicians | MML audio synthesis |

### 🧙 Wizard & Dev Mode
| Document | Audience | Purpose |
|----------|----------|---------|
| [Wizard Server](./wizard/README.md) | Admins | Always-on AI server, Dev Mode |

### 🔧 Distribution
| Document | Audience | Purpose |
|----------|----------|---------|
| [TinyCore Stack](./tinycore/README.md) | Deployers | Installation & TCZ packages |

### 👥 Contributing
| Document | Audience | Purpose |
|----------|----------|---------|
| [Contributing](./contributing/README.md) | Contributors | How to help |
| [Style Guide](./STYLE-GUIDE.md) | Contributors | Code & content standards |

### 🙏 Credits & Licensing
| Document | Audience | Purpose |
|----------|----------|---------|
| [Credits](./CREDITS.md) | Everyone | Library credits, fonts, licenses |

---

## 🗂️ Directory Structure

```
wiki/
├── README.md              # This file
├── VISION.md              # Core mission & philosophy
├── STYLE-GUIDE.md         # Code & content standards
├── FAQ.md                 # Common questions
├── CHANGELOG.md           # Version history
│
├── getting-started/       # New user onboarding
├── commands/              # Command reference
├── tui/                   # Terminal User Interface
├── app/                   # uCode Markdown App
├── upy/                   # uPY scripting
├── formats/               # File formats
├── bundles/               # Bundle system
├── graphics/              # Graphics system
├── groovebox/             # Audio synthesis
├── wizard/                # Wizard Server
├── architecture/          # System architecture
├── tinycore/              # Distribution
└── contributing/          # Contributor docs
```

---

## 🔄 Migration Notes

This wiki reorganizes content from:
- Previous `wiki/` files (archived to `wiki/.archive/2026-01-07/`)
- `core/docs/` technical specs
- `dev/roadmap/` architecture docs

Legacy files remain accessible but link to updated locations.

---

*Last Updated: 2026-01-07*
