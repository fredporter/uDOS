# uDOS v1.4 Display System APIs

## Overview
Backend APIs supporting the three-mode uDOS v1.4 display system with Flask/SocketIO real-time capabilities.

## Three-Mode API Architecture

### 1. CLI Terminal APIs
**Purpose**: Backend support for enhanced terminal functionality
- **Role validation**: Permission checking for terminal commands
- **UTF-8 support**: Consistent text encoding across all operations
- **Color integration**: Polaroid theme support for terminal output

### 2. Desktop Application APIs
**Purpose**: Real-time data for native desktop application
- **System monitoring**: Live metrics via WebSocket streams
- **Terminal sessions**: Interactive terminal management
- **Memory browser**: uMEMORY navigation and file operations
- **Real-time updates**: Continuous data streams for desktop UI

### 3. Web Export APIs
**Purpose**: Data generation for shareable web interfaces
- **Dashboard export**: System status for presentation sharing
- **Terminal snapshots**: Session state for sharing and viewing
- **Memory exports**: Read-only memory browsing for remote access

## API Endpoint Structure
```
api/
├── README.md                    # This file
├── shared/                      # APIs used across all modes
│   ├── auth.py                  # Role authentication and validation
│   ├── system.py                # Core system status and information
│   └── memory.py                # uMEMORY access and navigation
├── desktop/                     # Desktop application specific APIs
│   ├── realtime.py              # WebSocket streams for live updates
│   ├── terminal-session.py     # Interactive terminal management
│   ├── dashboard.py             # Real-time system dashboard data
│   └── system-tray.py           # Background application control
├── export/                      # Web export specific APIs
│   ├── dashboard-export.py     # Static dashboard generation
│   ├── terminal-export.py      # Terminal session sharing
│   ├── memory-export.py        # Shared memory browser data
│   └── presentation.py         # Clean presentation interfaces
└── legacy/                      # Compatibility endpoints
    └── browser-ui.py            # Legacy browser-only endpoints
```

## Role-Based API Access

### GHOST & TOMB Roles
- **CLI support only**: Basic terminal validation and UTF-8 support
- **No desktop/export APIs**: Desktop and web export endpoints return 403
- **Minimal system info**: Essential status information only

### USER Role (DRONE+)
- **Full API access**: All desktop and export endpoints available
- **Standard features**: Complete system monitoring and management
- **Personal data**: User-specific memory and session access

### DEV Role (DRONE+)
- **Enhanced APIs**: Additional development and debugging endpoints
- **Debug data**: Extended system information and profiling data
- **Development export**: Enhanced sharing capabilities for dev environments

### WIZARD Role (DRONE+)
- **Administrative APIs**: System management and control endpoints
- **Full system access**: Complete administrative data and controls
- **Advanced export**: System-wide status and administrative reporting

## Core API Endpoints

### System Status API
```
GET /api/system/status
Returns: System metrics, uDOS version, role info

GET /api/system/health
Returns: System health check and component status

WebSocket /ws/system
Streams: Real-time system metrics and status updates
```

### Terminal Management API
```
POST /api/terminal/create
Body: {"role": "current|user|dev|wizard"}
Returns: Terminal session ID and WebSocket endpoint

GET /api/terminal/{session_id}/status
Returns: Session status, command history, output buffer

WebSocket /ws/terminal/{session_id}
Streams: Real-time terminal I/O and session management

DELETE /api/terminal/{session_id}
Returns: Session cleanup confirmation
```

### Memory System API
```
GET /api/memory/browse?path={path}&role={role}
Returns: Directory structure and file metadata

GET /api/memory/read?path={path}
Returns: File content with permission checking

POST /api/memory/search
Body: {"query": "search_term", "scope": "user|role|system"}
Returns: Search results with file paths and snippets

WebSocket /ws/memory
Streams: File system change notifications
```

### Dashboard API
```
GET /api/dashboard/metrics
Returns: Current system metrics for dashboard display

GET /api/dashboard/activities
Returns: Recent system activities and user actions

WebSocket /ws/dashboard
Streams: Real-time dashboard updates and notifications
```

### Export Generation API
```
POST /api/export/dashboard
Body: {"type": "status|metrics|full", "format": "html|json"}
Returns: Generated export content or file path

POST /api/export/terminal
Body: {"session_id": "...", "format": "html|text"}
Returns: Terminal session export for sharing

POST /api/export/memory
Body: {"path": "...", "recursive": true|false}
Returns: Memory browser export for remote viewing
```

## WebSocket Streams

### Real-Time System Monitoring
- **System metrics**: CPU, memory, disk usage with 1-second updates
- **Process monitoring**: uDOS component status and resource usage
- **Activity logs**: Live system events and user actions

### Terminal Session Streaming
- **Character-level I/O**: Real-time terminal input/output streaming
- **Session state**: Command history and terminal buffer synchronization
- **Multi-user support**: Shared terminal sessions with proper permissions

### Memory System Updates
- **File change notifications**: Real-time updates when files are modified
- **Directory monitoring**: Live updates to file and folder listings
- **Search result streaming**: Progressive search results for large datasets

## Security and Permissions

### Authentication Flow
1. **Role detection**: Automatic role identification from uDOS session
2. **Permission validation**: Endpoint access checking based on role capabilities
3. **Session management**: Secure session handling with automatic cleanup

### API Security
- **Role-based access control**: All endpoints check user permissions
- **Input validation**: Comprehensive input sanitization and validation
- **Rate limiting**: Protection against API abuse and resource exhaustion
- **CORS configuration**: Proper cross-origin request handling

### Data Protection
- **Memory isolation**: Role-appropriate access to memory areas
- **Terminal security**: Command execution within role permissions
- **Export sanitization**: Clean data export with sensitive information filtering

## Integration Points

### Backend Server Integration
- **Flask application**: Main web framework with RESTful endpoint design
- **SocketIO support**: WebSocket integration for real-time features
- **Process management**: Subprocess execution for terminal sessions
- **System monitoring**: Integration with psutil for system metrics

### uDOS Core Integration
- **uMEMORY system**: Direct access to memory APIs and file operations
- **Role system**: Integration with uDOS role management and permissions
- **UTF-8 foundation**: Consistent text encoding using ensure-utf8.sh
- **Color system**: Polaroid theme integration for consistent styling

### Frontend Integration
- **Desktop application**: Native Tauri app with WebView communication
- **Web export**: Static HTML generation with embedded data
- **Real-time updates**: WebSocket client integration for live features
- **Mobile responsive**: API design supporting responsive web interfaces

---

**Philosophy**: Purpose-driven APIs for three distinct modes - optimized for their specific use cases.

*uDOS v1.4 Display APIs - Backend support for CLI, Desktop, and Web Export modes*
