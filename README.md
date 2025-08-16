# uDOS v1.3 - Universal Data Operating System

**A globally-aware, timezone-integrated development platform with AI-enhanced workflows and wizard user capabilities.**

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Data Operating System
    ═══════════════ v1.3 ═══════════════
```

---

## 🚀 What's New in v1.3

### ✨ Key Features

#### 🌍 Global Timezone Integration
- **38 timezone codes** automatically mapped from city dataset
- **Real-time timezone detection** with automatic file timestamping
- **Global compatibility** across all development workflows
- **DST awareness** with automatic daylight saving time handling

#### 🧙‍♂️ Wizard Development Mode (uDEV)
- **Exclusive development environment** for advanced users
- **Automated session logging** with comprehensive activity tracking
- **VS Code integration** with dedicated development workspace
- **Task management** integration with AI-enhanced workflows

#### 🤖 Enhanced ASSIST Mode
- **Sandbox task management** for organized development workflows
- **Natural language processing** for intuitive task creation
- **AI-powered automation** with context-aware assistance
- **Collaborative development** support with team workflows

#### 📁 v1.3 Naming Convention
- **CAPS-NUMERIC-DASH** standard across all system elements
- **Enhanced filename format**: `uTYPE-YYYYMMDD-HHMM-TTZ-MMLLNN.md`
- **Automated migration tools** for existing files
- **Validation systems** ensuring naming compliance

## 🏗️ Directory Structure

```
[00-00-00] uDOS/
├── [10-00-00] uCORE/          # Core system files (read-only in production)
├── [20-00-00] uMEMORY/        # User data & customizations  
├── [30-00-00] uKNOWLEDGE/     # Shared knowledge bank (Wizard managed)
└── [40-00-00] sandbox/        # User workspace & drafts
```

## 🌟 Key Features v1.2

- **🚀 Cross-Platform Launchers**: Native launching for macOS, Windows, Linux
- **🔧 VS Code Integration**: Full development environment support
- **📋 Standardized Documentation**: Consistent markdown standards and location coding
- **💾 User Memory System**: Centralized user data management
- **🤖 Gemini CLI Integration**: Google Gemini assistant capabilities
- **🧪 Sandbox Environment**: Safe experimentation workspace

## 📦 Components

### 🔧 uCORE/ - Core System [10-00-00]
**System files, protected from user modification**
- `code/` - Main uDOS scripts and logic [10-20-00]
- `launcher/` - Cross-platform launching system [10-10-00]  
- `extensions/` - System extensions and modules [10-30-00]
  - `gemini/` - Google Gemini CLI integration [10-30-01]
- `docs/` - System documentation [10-50-00]
- `templates/` - Core template library [10-40-00]
- `development/` - Development tools [10-60-00]
- `installers/` - Installation systems [10-70-00]
- `datasets/` - Core datasets and mappings [10-80-00]

### 💾 uMEMORY/ - User Data [20-00-00]
**Your personal data and customizations**
- `configs/` - User configuration and identity [20-10-00]
- `templates/` - Your custom templates [20-20-00]
- `scripts/` - Your custom scripts [20-30-00]
- `datasets/` - Your personal datasets [20-40-00]
- `projects/` - Your project files [20-50-00]
- `extensions/` - Your personal extensions [20-60-00]

### 📚 uKNOWLEDGE/ - Knowledge Bank [30-00-00]
**Shared public knowledge (Wizard managed)**
- Read-only in production mode
- Editable in development mode
- Contains shared intelligence and reference materials

### 🧪 sandbox/ - User Workspace [40-00-00]
**Your experimentation and draft area**
- `user.md` - Your personal notes and workspace [40-10-00]
- `scripts/` - Experimental scripts [40-20-00]
- `drafts/` - Work-in-progress files [40-30-00]
- `experiments/` - Testing and prototyping area [40-40-00]

## 🚀 Quick Start

### Easy Launch (All Platforms)
```bash
# Universal installer
./uCORE/launcher/install-launcher.sh

# Then use platform-specific launcher:
# • macOS: Double-click uDOS.command
# • Windows: Double-click uDOS.bat  
# • Linux: Use desktop launcher or run uDOS.sh
```

### Development Mode
```bash
# Start with VS Code integration
./uCORE/launcher/universal/start-dev.sh

# Or force terminal development mode
./uCORE/launcher/universal/start-udos.sh --dev
```

### Manual Launch
```bash
# Start uDOS main interface
./uCORE/code/ucode.sh

# Start Gemini assistant (ASSIST mode)
./uCORE/code/ucode.sh assist

# Check system health
./uCORE/code/check.sh all

# Generate live dashboard
./uCORE/code/dash.sh live
```

## 🤖 Gemini Integration

### ASSIST Mode
```bash
./uCORE/scripts/assist
```
Development assistance with project context using Google Gemini

### COMMAND Mode  
```bash
./uCORE/scripts/command
```
Natural language system commands

### Direct Gemini Access
```bash
./uCORE/extensions/gemini/uc-gemini.sh
```
Direct access to Gemini CLI integration

## 🎯 User Roles

- **🧙‍♂️ Wizard**: Full system access and Gemini management
- **🔮 Sorcerer**: Extension development and advanced features  
- **👨‍🎓 Apprentice**: Learning-focused interface with guidance
- **📚 Scholar**: Research tools and knowledge management

## � Documentation & Standards

### 📋 Core Documentation [10-50-00]
- **[Markdown Standard v1.2](uCORE/docs/uDOS-Markdown-Standard.md)** [10-50-01] - Documentation formatting standards
- **[Location Map](uCORE/docs/uDOS-Location-Map.md)** [10-50-04] - Complete system mapping with location codes
- **[Development Guide](uCORE/docs/Development-Guide.md)** [10-50-02] - Developer workflow and best practices
- **[User Manual](uCORE/docs/User-Manual.md)** [10-50-03] - Complete user documentation

### � Implementation Summaries
- **[Cross-Platform Launcher](CROSS_PLATFORM_LAUNCHER_SUMMARY.md)** [00-21-00] - Launcher system implementation
- **[Documentation Standards](DOCUMENTATION_STANDARDS_SUMMARY.md)** [00-22-00] - Standards implementation details

### 📖 Component Documentation
- **[Launcher System](uCORE/launcher/README.md)** [10-10-00] - Cross-platform launching
- **[Core Scripts](uCORE/code/README.md)** [10-20-00] - Main system scripts
- **[User Memory](uMEMORY/README.md)** [20-00-00] - User data management

## 🔧 Development Environment

### VS Code Integration [10-10-05]
```bash
# Setup development environment
./uCORE/launcher/vscode/setup-vscode.sh

# Open workspace
code uDOS.code-workspace
```

### Location Code Navigation
```bash
# Quick component location reference
[10-10-00] Launcher system
[10-20-01] Main ucode.sh script  
[20-10-01] User identity.md
[10-50-01] Documentation standards
```

## 🆘 Support & Contributing

- **📚 Documentation**: [uCORE/docs/](uCORE/docs/) [10-50-00]
- **🐛 Issues**: Use location codes for precise component references
- **💡 Feature Requests**: Follow development guide standards [10-50-02]
- **🤝 Contributing**: See development documentation and standards

## ⚡ Architecture Benefits

- **Clear Separation**: System vs User vs Knowledge vs Workspace
- **Cross-Platform**: Native launchers for macOS, Windows, Linux
- **Standardized**: Consistent documentation and location coding
- **Scalable**: Easy to backup user data separately  
- **Maintainable**: Logical organization with precise component addressing
- **Developer-Friendly**: Full VS Code integration with debugging support

---

**uDOS v1.2** - *Where Data Meets Intelligence* ✨

**Features**: Cross-Platform Launcher | Documentation Standards | Location Coding | VS Code Integration  
**Updated**: August 16, 2025 | **Architecture**: Modern Modular Design
