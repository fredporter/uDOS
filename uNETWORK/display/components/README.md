# uDOS v1.4 Display Components

## Overview
Frontend components for the uDOS v1.4 three-mode display system, supporting both desktop application and web export interfaces.

## Three-Mode Component Architecture

### 1. CLI Terminal Components
**Purpose**: Enhanced terminal rendering and utilities
- **Terminal Foundation**: UTF-8 enforcement and glyph detection
- **Color System**: Polaroid color theme with tput integration
- **Role Integration**: Command availability based on user permissions

### 2. Desktop Application Components  
**Purpose**: Native desktop app interface built with Tauri
- **Dashboard Widgets**: Real-time system monitoring components
- **Terminal Emulator**: Browser-based terminal with full feature support
- **Memory Browser**: Visual navigation of uMEMORY structure
- **System Tray**: Background operation and quick access controls

### 3. Web Export Components
**Purpose**: Shareable web interfaces for presentations and remote viewing
- **Export Templates**: Clean presentation layouts for different content types
- **Responsive Design**: Mobile-first design with desktop optimization
- **Viewer Interfaces**: Read-only optimized components for shared content

## Component Structure
```
components/
├── README.md                    # This file
├── shared/                      # Components used across modes
│   ├── terminal-foundation/     # UTF-8 and glyph detection utilities
│   ├── polaroid-theme/          # Consistent color theming
│   └── role-management/         # Permission checking and role UI
├── desktop/                     # Desktop application specific
│   ├── dashboard/               # Real-time system dashboard
│   ├── terminal/                # Interactive terminal emulator
│   ├── memory-browser/          # Visual uMEMORY navigation
│   └── system-tray/             # Background app controls
├── web-export/                  # Web export specific
│   ├── dashboard-export/        # Static dashboard presentations
│   ├── terminal-viewer/         # Read-only terminal session sharing
│   ├── memory-export/           # Shared memory browser interface
│   └── responsive-layouts/      # Mobile-optimized presentation
└── templates/                   # HTML templates and base components
    ├── dashboard.html           # System status dashboard
    ├── terminal.html            # Terminal emulator interface
    └── memory.html              # uMEMORY browser template
```

## Role-Based Component Access

### GHOST & TOMB Roles
- **CLI only**: No desktop or web export components available
- **Terminal foundation**: Basic terminal rendering utilities
- **Minimal UI**: Essential system feedback only

### USER Role (DRONE+)
- **Full component access**: All desktop and export components
- **Standard features**: Complete interface appropriate for development
- **Personal workspace**: Project-focused component configuration

### DEV Role (DRONE+)
- **Enhanced components**: Additional development and debugging tools
- **Debug widgets**: Advanced system monitoring and profiling
- **Development export**: Enhanced sharing capabilities for dev work

### WIZARD Role (DRONE+)
- **Administrative components**: System management and control interfaces
- **Full system access**: Complete administrative dashboard and controls
- **Advanced export**: System-wide status and administrative reporting

## Component Guidelines

### Design Principles
- **Mode-Specific**: Each component optimized for its intended display mode
- **Role-Aware**: Components adapt functionality based on user permissions
- **Consistent Theming**: Polaroid color scheme across all interfaces
- **Performance First**: Efficient rendering for both native and web contexts

### Technical Standards
- **Responsive Design**: Mobile-first with desktop enhancement
- **Accessibility**: Full ARIA support and keyboard navigation
- **WebSocket Integration**: Real-time updates where appropriate
- **Cross-Platform**: Components work consistently across operating systems

### Integration Requirements
- **Backend Server**: Flask/SocketIO integration for real-time features
- **Tauri Framework**: Native desktop application compatibility
- **uMEMORY System**: Direct integration with memory system APIs
- **Role System**: Automatic permission checking and UI adaptation

## Development Workflow

### Component Creation
1. **Identify purpose**: Determine which display mode(s) the component serves
2. **Check role requirements**: Ensure appropriate permission handling
3. **Design responsive**: Mobile-first with desktop optimization
4. **Implement real-time**: Add WebSocket support if needed
5. **Test across modes**: Verify component works in intended contexts

### Testing Strategy
- **CLI mode testing**: Ensure terminal components render correctly
- **Desktop app testing**: Verify native app integration and performance
- **Web export testing**: Confirm responsive design and sharing functionality
- **Cross-role testing**: Test component behavior with different user roles

### Integration Points
- **Terminal Foundation**: Use shared UTF-8 and glyph detection utilities
- **Color System**: Integrate with Polaroid theme for consistent appearance
- **Backend APIs**: Connect to display-server.py for data and real-time updates
- **Role Management**: Implement permission checking for all user interactions

---

**Philosophy**: Purpose-built components for three distinct modes - no one-size-fits-all complexity.

*uDOS v1.4 Display Components - Optimized interfaces for CLI, Desktop, and Web Export*
