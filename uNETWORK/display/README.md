# uDOS v1.4 Display System

**Three-mode display architecture: CLI Terminal, Desktop Application, and Web Export**

## Overview
The uDOS v1.4 Display System provides three distinct, purpose-driven interfaces for different use cases and user roles. Each mode is optimized for its specific purpose, with no complexity or fallback confusion.

## Three Display Modes

### 1. CLI Terminal (Always Available)
**Purpose**: Direct system control, automation, and core uDOS operations
- **Users**: All roles (GHOST, TOMB, DRONE+)
- **Access**: `udos`, `udos terminal`
- **Features**: 
  - Full terminal interface with Polaroid color theme
  - Scriptable and automation-friendly
  - Headless server compatible
  - UTF-8 foundation with Unicode/ASCII fallback
  - Role-based command availability

### 2. Desktop Application (DRONE+ Roles)
**Purpose**: Professional development interface with native OS integration
- **Users**: DRONE+ roles (USER, DEV, WIZARD)
- **Access**: `./udos-display.sh app`
- **Features**:
  - Native desktop application built with Tauri
  - System tray integration for background operation
  - Professional window management and sizing controls
  - Real-time system monitoring dashboard
  - Integrated terminal emulator with session management
  - uMEMORY browser with visual navigation

### 3. Web Export (DRONE+ Roles)  
**Purpose**: Share uDOS state, create presentations, and enable remote viewing
- **Users**: DRONE+ roles for sharing with others
- **Access**: `./udos-display.sh export [type] [--open]`
- **Features**:
  - Dashboard export for system status sharing
  - Terminal session sharing via web interface
  - uMEMORY browser for remote memory exploration
  - Clean presentation interfaces optimized for viewing
  - Mobile-responsive design for universal access

## Quick Start

### Check System Status
```bash
./udos-display.sh status
```
Shows availability of each display mode and current user role.

### Launch Desktop Application
```bash
# Setup dependencies (first time only)
./setup-display-system.sh setup

# Build the application (first time only)  
./udos-display.sh build

# Launch the desktop app
./udos-display.sh app
```

### Export for Sharing
```bash
# Export system dashboard
./udos-display.sh export dashboard --open

# Share live terminal session
./udos-display.sh export terminal

# Browse memory via web interface
./udos-display.sh export memory --open
```

### Get Help
```bash
./udos-display.sh help
```
Shows complete usage guide with examples.

## Desktop Application Features

### System Dashboard
- **Real-time metrics**: CPU, memory, and disk usage with live updates
- **uDOS status**: Active sessions, memory system status, version info
- **Quick actions**: Launch terminal, browse memory, view logs
- **Activity log**: Recent system activities and status changes

### Terminal Emulator  
- **Full terminal**: Interactive bash sessions with command history
- **Role-based access**: Different capabilities based on user role
- **Session management**: Multiple concurrent terminal sessions
- **Quick commands**: Preset buttons for common operations
- **Color themes**: Polaroid color scheme with customization options

### Memory Browser
- **Visual navigation**: Browse uMEMORY structure with file/folder interface
- **File operations**: View, edit, and manage memory files
- **Search capabilities**: Find content across memory system
- **Role permissions**: Access control based on user role

### System Tray Integration
- **Background operation**: App runs in system tray when minimized
- **Quick access**: Right-click menu for common operations
- **Status indicator**: Visual indication of uDOS system health
- **Native integration**: Platform-appropriate behavior on each OS

## Web Export Capabilities

### Dashboard Export
Creates shareable web pages showing:
- Current system status and metrics
- Active processes and resource usage
- uDOS configuration and role information
- Recent activity and system logs

### Terminal Session Sharing
Provides web-based access to:
- Live terminal sessions with real-time updates
- Command history and session state
- Read-only viewing for observers
- Interactive access for authorized users

### Memory Browser Web Interface
Enables remote access to:
- uMEMORY structure and content
- File browsing with download capabilities
- Search functionality across memory system
- Role-based access control for remote users

## Architecture Details

### Backend Server (`server/display-server.py`)
- **Flask + SocketIO**: Real-time web framework with WebSocket support
- **Terminal sessions**: Managed subprocess execution with streaming output
- **System monitoring**: Live metrics collection using psutil
- **uMEMORY integration**: Direct access to memory system APIs
- **Role management**: Permission checking for all operations

### Frontend Assets (`static/` and `templates/`)
- **Responsive CSS**: Mobile-first design with Polaroid color theme
- **Real-time JavaScript**: WebSocket integration for live updates
- **Terminal emulation**: Browser-based terminal with full feature support
- **Dashboard components**: Modular widgets for system information

### Native Application (`tauri-template/`)
- **Tauri framework**: Rust backend with native WebView frontend
- **Cross-platform**: Single codebase for macOS, Windows, and Linux
- **System integration**: Native window management and tray support
- **Process management**: Automatic backend server lifecycle control

### Launcher Scripts
- **udos-display.sh**: Main launcher with mode selection and help
- **setup-display-system.sh**: Dependency installation and environment setup
- **launch-display-server.sh**: Legacy browser-only launcher (maintained for compatibility)

## Role-Based Permissions

### GHOST Role
- **CLI only**: Terminal interface access
- **No display modes**: Desktop app and web export not available
- **Basic operations**: Core uDOS functionality only

### TOMB Role  
- **CLI only**: Extended terminal access for archive operations
- **No display modes**: Desktop app and web export not available
- **Archive focus**: Recovery and backup operations

### USER Role (DRONE+)
- **All modes available**: CLI, desktop app, and web export
- **Standard interface**: Full feature access appropriate for development work
- **Project focus**: Personal workspace and project management

### DEV Role (DRONE+)
- **All modes available**: Enhanced interfaces with development tools
- **Debug capabilities**: Advanced debugging and profiling features
- **Enhanced export**: Development environment sharing capabilities

### WIZARD Role (DRONE+)
- **All modes available**: Administrative interfaces and system controls
- **System management**: Full administrative access across all modes
- **Advanced export**: System-wide status and administrative reporting

## File Structure

```
display/
├── udos-display.sh              # Main launcher script
├── setup-display-system.sh     # Setup and installation script
├── launch-display-server.sh    # Legacy browser launcher
├── server/
│   └── display-server.py       # Backend server with WebSocket support
├── static/
│   ├── css/
│   │   ├── dashboard.css        # Dashboard styling with Polaroid theme
│   │   └── terminal.css         # Terminal emulator styling
│   └── js/
│       ├── dashboard.js         # Real-time dashboard functionality
│       └── terminal.js          # Terminal emulator with WebSocket
├── templates/
│   ├── dashboard.html           # System status dashboard template
│   ├── terminal.html            # Terminal emulator interface
│   └── memory.html              # uMEMORY browser template
├── tauri-template/
│   ├── tauri.conf.json          # Tauri application configuration
│   ├── Cargo.toml               # Rust dependencies and build config
│   ├── main.rs                  # Rust main process for desktop app
│   └── package.json             # Node.js build configuration
└── README.md                    # This file
```

## Development and Building

### Prerequisites
- **Python 3.8+**: For backend server
- **Node.js 16+**: For Tauri build system
- **Rust**: For native application compilation
- **Platform tools**: Xcode (macOS), Visual Studio (Windows), build-essential (Linux)

### Setup Development Environment
```bash
# Install all dependencies
./setup-display-system.sh setup

# This installs:
# - Node.js and npm
# - Rust and Cargo
# - Python dependencies (Flask, SocketIO, psutil)
# - Tauri CLI tools
```

### Build Desktop Application
```bash
# Development build (faster, larger)
./udos-display.sh dev

# Production build (optimized, smaller)
./udos-display.sh build

# Build creates platform-specific installers:
# - macOS: .app bundle and .dmg installer
# - Windows: .exe installer and .msi package  
# - Linux: .AppImage portable and .deb package
```

### Testing
```bash
# Test CLI mode (always available)
./udos-display.sh cli

# Test web export without building desktop app
./udos-display.sh export dashboard --open

# Check system status
./udos-display.sh status
```

## Integration with uDOS Core

### UTF-8 Foundation
- Integrates with `uSCRIPT/library/shell/ensure-utf8.sh`
- Consistent text rendering across all display modes
- Automatic locale detection and fallback handling

### Polaroid Color System
- Uses `uCORE/system/polaroid-colors.sh` for consistent theming
- Terminal and web interfaces share color palette
- Role-appropriate color coding for different interface elements

### uMEMORY Integration
- Direct access to user and system memory
- Display preferences persist in `uMEMORY/user/display-config.env`
- Memory browser provides visual navigation of memory structure

### Role System Integration
- Automatic role detection and permission enforcement
- Display mode availability based on user role
- Consistent role-based feature access across all modes

---

**Philosophy**: Three tools, three purposes. No complexity, no fallbacks - just the right interface for each job.

*uDOS v1.4 Display System - Simple, powerful, role-appropriate interfaces*
