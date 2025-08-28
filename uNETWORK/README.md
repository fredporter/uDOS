# uNETWORK - Display Services & Network Infrastructure

**Three-mode display system and network services for uDOS with foundation for future networking capabilities**

*Universal Device Operating System*

## Overview

uNETWORK provides the display and network infrastructure for uDOS v1.0.4.1, featuring a foundational three-mode display architecture and core network services. This module is designed with clean simplicity for the current development stage.

## Foundational Display System

### Three Core Display Modes

**1. CLI Terminal (Core Interface)**
- **Purpose**: Direct system control, automation, core uDOS operations
- **Users**: All roles (Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer, Wizard)
- **Access**: `udos terminal`, core `ucode` commands
- **Features**: Full terminal interface, scriptable, automation-friendly

**2. Desktop Application (Enhanced Roles)**
- **Purpose**: Development interface with enhanced capabilities
- **Users**: Enhanced roles with expanded permissions
- **Access**: `udos app` (via `./udos-display.sh app`)
- **Features**: Native desktop app, system tray, window management, professional UI

**3. Web Export (DRONE+ Roles)**
- **Purpose**: Share uDOS state, remote viewing, presentations
- **Users**: DRONE+ roles for sharing with others
- **Access**: `udos export` (via `./udos-display.sh export`)
- **Features**: Dashboard export, terminal session sharing, memory browser

## Directory Structure

```
uNETWORK/
├── display/                    # uDOS Display System
│   ├── udos-display.sh        # Main display mode launcher
│   ├── setup-display-system.sh # Setup script for all display modes
│   ├── server/                # Backend server for desktop app and web export
│   │   └── display-server.py  # Flask/SocketIO server with WebSocket support
│   ├── static/                # Web assets (CSS, JS, images)
│   │   ├── css/              # Polaroid-themed stylesheets
│   │   └── js/               # Real-time dashboard and terminal JS
│   ├── templates/             # HTML templates for web export
│   │   ├── dashboard.html    # System status dashboard
│   │   ├── terminal.html     # Terminal emulator interface
│   │   └── memory.html       # uMEMORY browser interface
│   ├── tauri-template/        # Native desktop app configuration
│   │   ├── tauri.conf.json   # Tauri configuration
│   │   ├── Cargo.toml        # Rust dependencies
│   │   ├── main.rs           # Rust main process
│   │   └── package.json      # Node.js build configuration
│   └── README.md              # Display system documentation
├── server/                     # Legacy web server (maintained for compatibility)
│   ├── server.py              # Original Flask server
│   ├── start-server.sh        # Legacy server startup
│   └── README.md              # Server-specific documentation
└── README.md                  # This file
```

## Quick Start

### Check Display Mode Status
```bash
./uNETWORK/display/udos-display.sh status
```

### Use CLI Mode (Always Available)
```bash
udos                    # Main uDOS interface
udos terminal           # Force CLI mode
./uNETWORK/display/udos-display.sh cli    # Show CLI information
```

### Setup Desktop Application
```bash
# Install dependencies (Node.js, Rust, Tauri)
./uNETWORK/display/setup-display-system.sh setup

# Build the desktop app
./uNETWORK/display/udos-display.sh build

# Launch desktop application
./uNETWORK/display/udos-display.sh app
```

### Use Web Export
```bash
# Export system dashboard
./uNETWORK/display/udos-display.sh export dashboard --open

# Share terminal session
./uNETWORK/display/udos-display.sh export terminal

# Browse uMEMORY via web
./uNETWORK/display/udos-display.sh export memory --open
```

## Role-Based Access Control

### CLI Terminal (All Roles)
- **GHOST**: Minimal command-line access for basic operations
- **TOMB**: Extended CLI for archive and recovery operations
- **USER**: Full CLI access for standard development work
- **DEV**: Advanced CLI with development tools and debugging
- **WIZARD**: Complete CLI access with system administration

### Desktop Application (DRONE+ Only)
- **USER**: Standard desktop interface with project management
- **DEV**: Enhanced interface with debugging and profiling tools
- **WIZARD**: Full administrative interface with system controls

### Web Export (DRONE+ Only)
- **USER**: Can export personal dashboards and session data
- **DEV**: Can share development environments and debug sessions
- **WIZARD**: Can export system status and administrative reports

## Display System Philosophy

### Simplicity First
- **No complexity**: Each mode serves a distinct, clear purpose
- **No fallbacks**: No confusing auto-detection or failure modes
- **Right tool for the job**: CLI for control, Desktop for work, Web for sharing

### Role-Appropriate Access
- **GHOST/TOMB**: CLI-only for security and simplicity
- **DRONE+**: All modes available based on needs
- **Professional focus**: Desktop app provides native OS integration

### Clear Mental Model
- **Work Locally**: CLI (direct) or Desktop App (professional)
- **Share Results**: Web Export (present to others)
- **No Overlap**: Each mode optimized for its specific use case

## Technical Architecture

### Backend Server
- **Flask + SocketIO**: Real-time web interface with WebSocket support
- **Terminal sessions**: Browser-based terminal emulation with role permissions
- **System monitoring**: CPU, memory, disk usage with live updates
- **uMEMORY integration**: Browse and manage memory system via web
- **API endpoints**: RESTful interface for system status and operations

### Desktop Application (Tauri)
- **Native WebView**: Platform-optimized rendering
- **System tray**: Background operation with quick access
- **Window management**: Professional desktop integration
- **Process management**: Automatic backend server lifecycle
- **Cross-platform**: macOS, Windows, Linux from single codebase

### Web Export Engine
- **Dashboard export**: System status as shareable web page
- **Terminal sharing**: Live terminal sessions via web interface
- **Memory browser**: uMEMORY navigation and visualization
- **Presentation mode**: Clean interfaces for sharing with others

### Integration Points
- **UTF-8 foundation**: Consistent text rendering across all modes
- **Polaroid colors**: Unified visual theme matching terminal interface
- **Role system**: Integrated permission checking across all display modes
- **uMEMORY persistence**: Display preferences saved to user memory

### Vision
uNETWORK is designed to evolve into a comprehensive peer-to-peer networking system for uDOS instances, enabling:

#### Distributed uDOS Network
- **Node discovery**: Automatic detection of other uDOS instances on local networks
- **Mesh networking**: Direct peer-to-peer communication between uDOS systems
- **Distributed computing**: Shared processing across multiple uDOS instances
- **Synchronized data**: Real-time synchronization of uMEMORY data across nodes

#### Network Services (Future)
- **Resource sharing**: Share uSCRIPT libraries, templates, and tools across network
- **Collaborative editing**: Multiple users working on shared uDOS projects
- **Distributed storage**: Redundant backup across peer network
- **Command propagation**: Execute commands across multiple uDOS instances

#### Security Model (Future)
- **Encrypted communication**: All peer-to-peer traffic encrypted by default
- **Identity verification**: Role-based authentication across network
- **Sandboxed execution**: Safe execution of remote scripts and commands
- **Permission system**: Fine-grained control over network access and operations

### Development Phases

#### Phase 1: Local Network Discovery (Future)
- Implement local network scanning for uDOS instances
- Basic handshake and capability exchange
- Simple file sharing between local uDOS nodes

#### Phase 2: Secure P2P Communication (Future)
- Implement encryption for all network traffic
- Role-based authentication system
- Secure command execution across network

#### Phase 3: Distributed Services (Future)
- Distributed uMEMORY synchronization
- Network-wide uSCRIPT library sharing
- Collaborative workspace features

#### Phase 4: Advanced Networking (Future)
- Internet-based peer discovery (with proper security)
- Advanced mesh networking capabilities
- Distributed computing framework

### Technical Foundation

The current architecture provides the foundation for P2P development:

#### Modular Design
- **Service abstraction**: Current web server can be extended to support P2P protocols
- **Configuration management**: Flexible configuration system ready for network settings
- **Error handling**: Robust error handling suitable for network environments
- **Logging system**: Comprehensive logging for network troubleshooting

#### Network Stack Ready
- **WebSocket support**: Real-time communication infrastructure already in place
- **API framework**: RESTful API design easily extensible to P2P protocols
- **Process management**: Server management suitable for network service daemons
- **Virtual environment**: Isolated Python environment for secure network operations

## Development Roadmap

### Current (v1.0.4.1)
- Three-mode display system foundation
- CLI terminal interface (all roles)
- Basic web export functionality
- Core network services infrastructure

### Near Term (v1.1.x)
- Desktop application implementation
- Enhanced role-based display features
- Improved web export capabilities
- Network connectivity optimization

### Medium Term (v1.2.x)

### Long Term (v2.x)
- 📋 Full peer-to-peer networking implementation
- 📋 Distributed uDOS ecosystem
- 📋 Advanced collaborative features

---

**Note**: The peer-to-peer networking features are planned for future development. Current focus is on robust local services and display components. The architecture is being designed with P2P capabilities in mind to ensure smooth future expansion.

---

*uNETWORK v1.0.4.1 - Building the foundation for uDOS networking*
