# 🚀 uDOS macOS Distribution System v1.3.1

**Complete macOS distribution with desktop app launcher, role-based access, and VS Code integration**

## 🌟 Features

### 🍎 Native macOS Integration
- **Desktop App Bundle**: `uDOS.app` with native macOS integration
- **Terminal Profile**: Custom `uDOS.terminal` with retro styling
- **Applications Folder**: Installable to `/Applications/`
- **Desktop Shortcut**: Quick access from desktop

### 🎭 Role-Based Access System
- **👻 Ghost** (Level 10) - Demo & Evaluation
- **⚰️ Tomb** (Level 20) - Archive Management  
- **🤖 Drone** (Level 40) - Task Automation
- **👹 Imp** (Level 60) - Development Tools
- **🔮 Sorcerer** (Level 80) - Advanced User
- **🧙‍♂️ Wizard** (Level 100) - Full Development

### 🧙‍♂️ VS Code Development Mode (Wizard Only)
- **Full IDE Integration**: Complete development environment
- **Git Operations**: Built-in version control
- **Task Automation**: Pre-configured VS Code tasks
- **Extension Support**: Recommended development extensions

### 🖥️ CLI/UI Separation
- **CLI Reserved**: For uSERVER operations and system administration
- **UI Omniview**: Browser-based interface for user interactions
- **Dual Mode**: Server operations + user interface simultaneously

## 🚀 Quick Start

### Installation
```bash
# Automatic installation
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/main/uCORE/launcher/platform/macos/install-udos.sh | bash

# Or manual installation
git clone https://github.com/fredporter/uDOS.git ~/uDOS
cd ~/uDOS
./uCORE/launcher/platform/macos/install-udos.sh
```

### Launch Options

#### 🍎 Desktop App (Recommended)
1. Double-click `uDOS.app` on desktop or in Applications
2. Choose your launch mode from the startup menu
3. Select role and features based on your needs

#### 🖥️ Command Line
```bash
# Quick launch
udos

# Direct launcher
~/uDOS/uCORE/launcher/universal/start-udos.sh [role]

# VS Code development (wizard only)
~/uDOS/uCORE/launcher/universal/start-dev.sh
```

## 🎯 Launch Modes

### 🧙‍♂️ VS Code DEV Mode (Wizard Only)
- **Complete Development Environment**: Full VS Code workspace
- **Git Integration**: Version control and collaboration
- **Task Automation**: Pre-configured development tasks
- **Extension Support**: Recommended extensions auto-installed
- **Server Operations**: CLI reserved for uSERVER management

### 🎭 Role Modes
Each role provides appropriate capabilities:
- **Role-specific CLI**: Tailored command sets
- **Permission System**: Access control based on role level
- **Session Management**: Isolated work environments
- **UI Integration**: Role-aware web interface

### 🔧 System Operations
- **Status Monitoring**: Real-time system status
- **Log Management**: Centralized logging system
- **Update System**: Git-based update mechanism
- **Repair Tools**: Automated system repair

## 🛠️ Technical Architecture

### 📱 App Bundle Structure
```
uDOS.app/
├── Contents/
│   ├── Info.plist          # App bundle configuration
│   └── MacOS/
│       └── uDOS            # Main launcher executable
```

### 🖥️ Terminal Integration
- **Custom Profile**: `uDOS.terminal` with retro styling
- **Font Configuration**: Monaco monospace for authenticity
- **Color Scheme**: Dark theme with cyan accents
- **Window Settings**: Optimized dimensions and behavior

### 🔄 Update System
- **Git-Based**: Direct repository synchronization
- **Backup System**: Automatic backup before updates
- **Conflict Resolution**: Smart handling of local changes
- **Version Control**: Branching for safe updates

## 📋 System Requirements

### ✅ Minimum Requirements
- **macOS**: 10.15 (Catalina) or later
- **Storage**: 100MB free space
- **Network**: Internet connection for installation/updates

### 🚀 Recommended
- **macOS**: 12.0 (Monterey) or later
- **VS Code**: Latest version for development mode
- **Git**: Latest version for optimal experience
- **Terminal**: macOS Terminal or iTerm2

## 🔧 Configuration

### 🎨 Terminal Profile Installation
1. Double-click `Desktop/uDOS.terminal`
2. Choose "Import" in Terminal preferences
3. Set as default profile (optional)

### 🧙‍♂️ VS Code Setup (Wizard)
1. Install VS Code from https://code.visualstudio.com/
2. Add `code` command to PATH:
   - Open VS Code
   - Press `Cmd+Shift+P`
   - Type "Shell Command: Install 'code' command in PATH"
   - Run the command
3. Launch uDOS → Choose "VS Code DEV Mode"

### 🔐 Role Configuration
Roles are automatically configured during installation based on:
- **Permission Files**: `[role]/permissions.json`
- **Capability Sets**: Defined access levels
- **Session Isolation**: Independent work environments

## 🚨 Troubleshooting

### Common Issues

#### App Won't Launch
```bash
# Check permissions
chmod +x ~/uDOS/uDOS.app/Contents/MacOS/uDOS

# Check installation
ls -la ~/uDOS/uDOS.app/Contents/MacOS/
```

#### VS Code Not Detected
```bash
# Verify VS Code installation
code --version

# Add to PATH if needed
export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"
```

#### Git Issues
```bash
# Install/update Git
xcode-select --install

# Verify Git
git --version
```

### Support
- **Documentation**: `~/uDOS/docs/`
- **Logs**: Check role-specific log directories
- **System Repair**: Use built-in repair tools
- **Community**: GitHub Issues and Discussions

## 🔄 Updates

### Automatic Updates
- Launch uDOS → System Update
- Checks GitHub repository for updates
- Backup and apply updates safely

### Manual Updates
```bash
cd ~/uDOS
git pull origin main
```

---

**uDOS v1.3.1** - Universal Development Operating System  
*macOS Distribution with Native App Integration*
