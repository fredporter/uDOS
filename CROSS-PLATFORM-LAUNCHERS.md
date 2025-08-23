# 🌀 uDOS Cross-Platform Launchers v1.3.3

**Simple one-click launchers for macOS, Windows, and Ubuntu 22**

## 🚀 Quick Launch

### 🍎 macOS
Double-click: `🌀-Launch-uDOS-macOS.command`

### 🪟 Windows  
Double-click: `🌀-Launch-uDOS-Windows.bat`

### 🐧 Ubuntu 22
Double-click: `🌀-Launch-uDOS-Ubuntu.sh` (or run from terminal)

## 🌟 Features

### � Cross-Platform Support
- **�🍎 macOS**: Native .command launcher with Terminal integration
- **🪟 Windows**: .bat launcher with Git Bash/WSL support  
- **🐧 Ubuntu 22**: Shell script with dependency auto-installation

### 🎯 Simplified Launch
- **One-Click**: No complex installation or configuration
- **Self-Contained**: Launchers detect and start uDOS automatically
- **Error Handling**: Clear messages if dependencies are missing

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

### �️ Installation Options

#### 🚀 One-Command Install
```bash
# Clone and launch
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# macOS
open "🌀-Launch-uDOS-macOS.command"

# Ubuntu 22  
chmod +x "🌀-Launch-uDOS-Ubuntu.sh"
./"🌀-Launch-uDOS-Ubuntu.sh"

# Windows (double-click or from Command Prompt)
"🌀-Launch-uDOS-Windows.bat"
```

#### 🍎 macOS Quick Start
1. `git clone https://github.com/fredporter/uDOS.git`
2. Double-click `🌀-Launch-uDOS-macOS.command`
3. Choose your preferred mode (Terminal/VS Code)

#### 🪟 Windows Quick Start  
1. Install Git for Windows (if not installed)
2. `git clone https://github.com/fredporter/uDOS.git`
3. Double-click `🌀-Launch-uDOS-Windows.bat`

#### � Ubuntu 22 Quick Start
1. `git clone https://github.com/fredporter/uDOS.git`
2. `cd uDOS && chmod +x "🌀-Launch-uDOS-Ubuntu.sh"`
3. `./"🌀-Launch-uDOS-Ubuntu.sh"` (auto-installs dependencies)

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

### 🍎 macOS
- **Version**: macOS 10.15+ (Catalina or later)
- **Dependencies**: Terminal (built-in), Python3 (auto-detected)
- **Optional**: VS Code for development mode

### 🪟 Windows  
- **Version**: Windows 10+ 
- **Dependencies**: Git for Windows (with Git Bash) OR WSL
- **Download Git**: https://git-scm.com/download/win

### 🐧 Ubuntu 22
- **Version**: Ubuntu 22.04+
- **Dependencies**: Auto-installed (bash, python3, git)
- **Privileges**: sudo access for dependency installation

## 🔧 Platform-Specific Notes

### � macOS
- Launcher opens in Terminal with uDOS interface
- VS Code integration auto-detected if installed
- Terminal profile customization available

### � Windows
- Requires Git Bash or WSL for shell compatibility
- Launcher automatically detects available bash environment
- PowerShell support planned for future versions

### � Ubuntu 22
- Auto-installs missing dependencies (requires sudo)
- Native shell integration
- Desktop shortcuts can be created manually

## 🚨 Troubleshooting

### 🍎 macOS Issues

#### Launcher Won't Open
```bash
# Make executable
chmod +x "🌀-Launch-uDOS-macOS.command"

# Check permissions
ls -la "🌀-Launch-uDOS-macOS.command"
```

#### Security Warning
- macOS may block unsigned scripts
- Right-click → Open → Open anyway
- Or: System Preferences → Security & Privacy → Allow

### 🪟 Windows Issues

#### "Bash not found"  
```bash
# Install Git for Windows
# Download: https://git-scm.com/download/win
# Or install WSL: wsl --install
```

#### Permission Denied
```cmd
# Run as Administrator
# Right-click → "Run as administrator"
```

### 🐧 Ubuntu Issues

#### Permission Issues
```bash
# Make executable
chmod +x "🌀-Launch-uDOS-Ubuntu.sh"

# If sudo issues
sudo apt update && sudo apt install python3 git
```

#### Missing Dependencies
The launcher auto-installs dependencies but may need:
```bash
sudo apt update
sudo apt install python3 python3-pip git bash curl
```

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

**uDOS v1.3.3** - Universal Device Operating System  
*Cross-Platform Launchers for macOS, Windows & Ubuntu*
