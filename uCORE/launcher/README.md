# uDOS Cross-Platform Launcher System v1.2
**Universal Launch Solutions for uDOS Across All Platforms**  
**Location**: [10-10-00] uCORE/launcher/

## 📋 Overview

The uDOS launcher system provides multiple ways to start uDOS across different platforms and environments, with proper separation between development and production modes.

## 🌟 Platform Support

### 🍎 macOS
- **Finder Integration**: `.command` files for double-click launching
- **macOS App Bundle**: Native application wrapper  
- **Terminal Integration**: Direct terminal launching
- **VS Code Integration**: Development environment launching
- **Location**: [10-10-01] platform/macos/

### 🪟 Windows
- **Windows Executable**: `.exe` launcher via PowerShell
- **Batch Files**: `.bat` scripts for command prompt
- **Windows Terminal**: Modern terminal integration
- **VS Code Integration**: Cross-platform development
- **Location**: [10-10-02] platform/windows/

### 🐧 Linux/Ubuntu
- **Desktop Integration**: `.desktop` files for GUI launchers
- **Shell Scripts**: Direct bash execution
- **Terminal Emulator**: Various terminal support
- **VS Code Integration**: Development environment
- **Location**: [10-10-03] platform/linux/

## 🎯 Launch Modes

### Production Mode
- **Terminal Interface**: Clean terminal-based uDOS experience
- **No Dependencies**: Works without VS Code or development tools
- **Standalone**: Self-contained execution
- **User-Friendly**: Simple interface for end users

### Development Mode
- **VS Code Integration**: Full IDE experience with extensions
- **Debug Support**: Debugging and development tools
- **Extension Development**: uDOS extension support
- **Advanced Features**: Developer-specific functionality
- **Location**: [10-10-05] vscode/

## 🏗️ Directory Structure

```
[10-10-00] uCORE/launcher/
├── [10-10-00] README.md                 # This file
├── [10-10-00] install-launcher.sh       # Universal installer
├── [10-10-01] platform/
│   ├── [10-10-01] macos/               # macOS-specific launchers
│   │   ├── uDOS.command                # Finder double-click launcher
│   │   └── install.sh                  # macOS installation script
│   ├── [10-10-02] windows/             # Windows-specific launchers
│   │   ├── uDOS.bat                    # Batch file launcher
│   │   ├── uDOS.ps1                    # PowerShell launcher
│   │   └── install.ps1                 # PowerShell installation
│   └── [10-10-03] linux/               # Linux-specific launchers
│       ├── uDOS.sh                     # Shell script launcher
│       ├── uDOS.desktop                # Desktop environment launcher
│       └── install.sh                  # Linux installation script
├── [10-10-04] universal/
│   ├── start-udos.sh                   # Universal startup script
│   ├── start-dev.sh                    # Development mode startup
│   └── detect-platform.sh             # Platform detection
├── [10-10-05] vscode/
│   ├── settings.json                   # VS Code workspace settings
│   ├── tasks.json                      # VS Code tasks for uDOS
│   └── launch.json                     # VS Code debugging config
└── [10-10-06] assets/
    └── README.md                       # Icon and asset guidelines
```

## Installation

### Quick Install (All Platforms)
```bash
./uCORE/launcher/install-launcher.sh
```

### Platform-Specific
```bash
# macOS
./uCORE/launcher/platform/macos/install.sh

# Windows (PowerShell)
./uCORE/launcher/platform/windows/install.ps1

# Linux
./uCORE/launcher/platform/linux/install.sh
```

## Usage

### End Users (Production)
- **macOS**: Double-click `uDOS.command` or `uDOS.app`
- **Windows**: Double-click `uDOS.exe` or `uDOS.bat`
- **Linux**: Click desktop launcher or run `./uDOS.sh`

### Developers (Development Mode)
- **Any Platform**: Open in VS Code and use tasks
- **VS Code Command**: `Ctrl+Shift+P` → "uDOS: Start Development"
- **Terminal**: `./start-dev.sh` for development mode

## Features

### Smart Platform Detection
- Automatically detects operating system
- Chooses appropriate launcher method
- Fallback to universal scripts

### Environment Detection
- Checks for VS Code availability
- Detects development tools
- Offers appropriate launch options

### Clean Separation
- Production mode: Terminal-only, no dependencies
- Development mode: Full VS Code integration
- Clear mode indicators and switching

### User Experience
- Native platform integration
- Familiar launch methods per platform
- Error handling and user guidance
