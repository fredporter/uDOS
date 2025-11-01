# Welcome to uDOS Wiki

**uDOS v1.0.4** - A Human-Readable CLI Framework with AI Integration and Teletext Visualization

> 🔮 *Building a better command-line experience, one spell at a time.*

---

## 🚀 Quick Links

| Getting Started | Reference | Advanced |
|:----------------|:----------|:---------|
| [Quick Start](Quick-Start) | [Command Reference](Command-Reference) | [uCODE Manual](uCODE-Language) |
| [Installation](Installation) | [Architecture](Architecture) | [Mapping System](Mapping-System) |
| [First Steps](First-Steps) | [API Documentation](API-Documentation) | [Script Automation](Script-Automation) |
| [Tutorials](Tutorials) | [Configuration](Configuration) | [Extension Development](Extensions) |

---

## 📖 What is uDOS?

uDOS is an **educational CLI framework** that demonstrates:

- **Human-Readable Commands**: Natural language-style syntax (`LOAD "file.txt" TO "panel"`)
- **AI Integration**: Gemini API for intelligent assistance with offline fallback
- **Integrated Mapping System**: APAC-centered 480×270 cell grid with global navigation
- **Teletext Visualization**: Retro mosaic block art with modern web interface
- **TIZO Location Codes**: Global city positioning with 20 major locations
- **Multi-Panel System**: Organize data in multiple named text buffers
- **Connection Awareness**: Automatic online/offline mode detection
- **Viewport Detection**: Adapts to terminal size and device type
- **Session Logging**: Complete interaction history
- **Script Automation**: Execute batch operations with `.uscript` files
- **Theming System**: Customizable lexicon (Dungeon Crawler, Cyberpunk, etc.)
- **Color Palette**: Professional Polaroid color system with accessibility
- **Web Extensions**: Interactive browser-based interfaces

---

## 🆕 What's New in v1.0.4

### 🖥️ Teletext Web Extension
- **Mosaic Block Art**: 64 2×3 pixel character combinations
- **WST Color Palette**: Classic teletext colors (8 colors)
- **Interactive Web Interface**: http://localhost:8080
- **Mobile-Responsive Design**: Touch-optimized controls
- **Export Functionality**: Save maps as standalone HTML

### 🗺️ Enhanced Mapping System
- **Global Cell Grid**: 480×270 APAC-centered reference system
- **TIZO Location Codes**: 20 major cities worldwide (MEL, SYD, LON, NYC, etc.)
- **Real-time Navigation**: Distance and bearing calculations
- **ASCII Map Generation**: Visual maps with position markers
- **Multi-layer Access**: Connection quality and layer systems

### 📋 New Commands
```bash
MAP STATUS              # Current location and system status
MAP VIEW [width height] # Generate ASCII map (40×20 default)
MAP TELETEXT [w h]      # Generate teletext-style map
MAP WEB [server]        # Open map in browser or start server
MAP NAVIGATE <from to>  # Calculate routes between locations
MAP CITIES [cell radius] # List cities globally or regionally
```

---

## 🎯 Who Is This For?

### 🎓 Learners
- **New Developers**: Learn CLI development, parsing, and AI integration
- **Python Students**: Study modular architecture and design patterns
- **DevOps Trainees**: Understand automation and scripting

### 🛠️ Builders
- **Tool Creators**: Use uDOS as a framework for custom CLIs
- **Educators**: Teaching material for systems programming
- **Researchers**: Experiment with AI-powered interfaces

### 🎮 Enthusiasts
- **Retro Computing Fans**: Enjoy the 8-bit aesthetic
- **Terminal Lovers**: Appreciate a well-crafted CLI
- **Game Developers**: Explore text-based navigation systems

---

## 🗺️ Learning Paths

### 🌱 Beginner Path
1. [Installation Guide](Installation)
2. [Quick Start Tutorial](Quick-Start)
3. [Basic Commands](Command-Reference#basic-commands)
4. [Creating Panels](Panels-Tutorial)
5. [First Script](Your-First-Script)

### 🌿 Intermediate Path
1. [Architecture Overview](Architecture)
2. [uCODE Language](uCODE-Language)
3. [Script Automation](Script-Automation)
4. [Theming System](Theming)
5. [Offline Engine](Offline-Engine)

### 🌳 Advanced Path
1. [Extension Development](Extensions)
2. [Custom Commands](Custom-Commands)
3. [Parser Internals](Parser-Internals)
4. [Mapping System](Mapping-System)
5. [Contributing Code](Contributing)

---

## 📚 Documentation Sections

### Core Concepts
- [Architecture](Architecture) - System design and components
- [uCODE Language](uCODE-Language) - Internal command format
- [Grid System](Grid-System) - Multi-panel management
- [Session Logging](Session-Logging) - History and recovery

### Features
- [AI Integration](AI-Integration) - Gemini API and offline fallback
- [Connection Awareness](Connection-Awareness) - Online/offline modes
- [Viewport System](Viewport-System) - Terminal adaptation
- [Mapping System](Mapping-System) - NetHack-style navigation
- [Color Palette](Color-Palette) - Polaroid color system

### Development
- [Contributing Guide](Contributing) - How to contribute
- [Development Workflow](Development-Workflow) - Dev process
- [Testing Strategy](Testing) - Quality assurance
- [API Reference](API-Documentation) - Complete API docs

### Tutorials
- [Quick Start](Quick-Start) - Get running in 5 minutes
- [Your First Script](Your-First-Script) - Automation basics
- [Building Extensions](Extension-Tutorial) - Add custom features
- [Theming Tutorial](Theming-Tutorial) - Customize the experience

---

## 🎨 Visual Features

### Polaroid Color Palette
uDOS uses a professional 8-color system optimized for terminal visibility:

🔴 **Red** (196) - Errors, alerts
🟢 **Green** (46) - Success, confirmations
🟡 **Yellow** (226) - Warnings, highlights
🔵 **Blue** (21) - Information, links
🟣 **Purple** (201) - Magic, special events
🔷 **Cyan** (51) - Technology, data
⚪ **White** (15) - Default text
⚫ **Black** (16) - Backgrounds

[Learn more about the color system →](Color-Palette)

### ASCII Art & Visualization
- Unicode box-drawing logo
- Viewport splash screen
- Grayscale gradients
- Map rendering

---

## 🤝 Community

### Get Help
- 💬 [Discussions](https://github.com/fredporter/uDOS/discussions) - Ask questions
- 🐛 [Issues](https://github.com/fredporter/uDOS/issues) - Report bugs
- 📧 Contact - [Your contact info]

### Contribute
- 🔧 [Contributing Guide](Contributing) - How to help
- 🎯 [Good First Issues](https://github.com/fredporter/uDOS/labels/good%20first%20issue)
- 🗺️ [Roadmap](Roadmap) - Project direction

### Resources
- 📦 [GitHub Repository](https://github.com/fredporter/uDOS)
- 📝 [Changelog](Changelog) - Version history
- 🚀 [Roadmap](Roadmap) - Future plans

---

## 🏆 Project Status

**Current Version**: v1.0.0 (November 2025)

**Key Features**:
- ✅ Modular command handler architecture
- ✅ JSON-based data structure
- ✅ Assistant integration (Gemini 2.5 Flash)
- ✅ Offline fallback engine
- ✅ Connection awareness
- ✅ Viewport detection
- ✅ Session logging
- ✅ UNDO/REDO system
- ✅ Script automation
- ✅ Smart completion
- ✅ Mapping system
- ✅ Color palette system

**Coming Soon**:
- 🔜 Plugin system
- 🔜 Advanced theming
- 🔜 Network integration
- 🔜 Enhanced AI features

[View full roadmap →](Roadmap)

---

## 📄 License

uDOS is open source software. See [LICENSE](https://github.com/fredporter/uDOS/blob/main/LICENSE) for details.

---

**Ready to begin?** Start with the [Quick Start Guide](Quick-Start) or dive into the [Architecture](Architecture)!

🔮 *May your terminals be colorful and your commands clear.*
