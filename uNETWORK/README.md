# uNETWORK v1.3.3 - Network Services & Future P2P Infrastructure

**Centralized network services for uDOS with foundation for future peer-to-peer networking**

## Overview

uNETWORK provides the network infrastructure for uDOS, currently focused on local web services and API endpoints. This module is designed with extensibility in mind to support future peer-to-peer networking capabilities.

## Current Services (v1.3.3)

### Web Server (`server/`)
- **Flask-based HTTP server** for uDOS web interface
- **WebSocket support** for real-time communication
- **API endpoints** for system integration
- **uSCRIPT venv integration** for isolated Python environment
- **Error handling & logging** with comprehensive crash detection

### Features
- **Port**: Default 8080 (configurable via `USERVER_PORT`)
- **Host**: 127.0.0.1 (configurable via `USERVER_HOST`)
- **Static file serving** for uDOS web interface
- **JSON API endpoints** for system status and commands
- **Auto-restart capabilities** with loop detection
- **Process management** with PID tracking

## Directory Structure

```
uNETWORK/
├── server/                     # Current web server implementation
│   ├── server.py              # Main Flask server (v1.3.3)
│   ├── ui_server.py           # UI-specific server components
│   ├── start-server.sh        # Server startup script with venv support
│   ├── setup-check.py         # Environment validation
│   ├── requirements.txt       # Python dependencies
│   ├── config/                # Server configuration files
│   ├── endpoints/             # API endpoint definitions
│   ├── middleware/            # Request/response middleware
│   └── README.md              # Server-specific documentation
├── display/                    # Display & UI components (NEW v1.3.3)
│   └── [Future development area]
└── README.md                  # This file
```

## Integration

### uSCRIPT Virtual Environment
uNETWORK services automatically integrate with the uSCRIPT virtual environment:

```bash
# Server automatically uses uSCRIPT venv if available
cd uNETWORK/server
./start-server.sh

# Setup uSCRIPT environment first (recommended)
cd ../../uSCRIPT
./setup-environment.sh
```

### System Integration
- **uCORE compatibility**: Integrates with uCORE error handling and system management
- **uMEMORY access**: Can read system configuration and user data
- **uSCRIPT execution**: Supports running scripts through network API calls
- **Logging integration**: Uses uDOS logging infrastructure

## Usage

### Start Web Server
```bash
# From uNETWORK/server directory
./start-server.sh

# Or from uDOS root
./uNETWORK/server/start-server.sh
```

### Check Server Status
```bash
# View server logs
tail -f uNETWORK/server/server.log

# Check if server is running
ps aux | grep "server.py"

# Test connection
curl http://localhost:8080/api/status
```

### Stop Server
```bash
# From server directory
pkill -f "server.py"

# Or use the built-in stop functionality
curl -X POST http://localhost:8080/api/shutdown
```

## Future Development: Peer-to-Peer Network

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

### Current (v1.3.3)
- ✅ Enhanced web server with uSCRIPT venv integration
- ✅ Improved error handling and process management
- ✅ Foundation for display components

### Near Term (v1.4.x)
- 🔄 Display component development in `uNETWORK/display/`
- 🔄 Enhanced API endpoints for system integration
- 🔄 WebSocket-based real-time communication improvements

### Medium Term (v1.5.x)
- 📋 Local network discovery implementation
- 📋 Basic peer-to-peer communication protocols
- 📋 Security framework for network operations

### Long Term (v2.x)
- 📋 Full peer-to-peer networking implementation
- 📋 Distributed uDOS ecosystem
- 📋 Advanced collaborative features

---

**Note**: The peer-to-peer networking features are planned for future development. Current focus is on robust local services and display components. The architecture is being designed with P2P capabilities in mind to ensure smooth future expansion.

---

*uNETWORK v1.3.3 - Building the foundation for distributed uDOS networking*
