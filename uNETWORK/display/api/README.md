# Browser-UI API Endpoints

## Overview
REST API and WebSocket endpoints for the uDOS Browser-UI system.

## API Structure
```
api/
├── README.md           # This file
├── terminal.py         # Terminal API endpoints
├── memory.py           # Memory system API
├── role.py             # Role management API
├── session.py          # Session management API
└── dev.py              # DEV mode API (Wizard + DEV only)
```

## Endpoint Categories

### Terminal API (`terminal.py`)
- `GET /api/terminal/status` - Terminal session status
- `POST /api/terminal/command` - Execute terminal command
- `WebSocket /ws/terminal` - Real-time terminal interaction

### Memory API (`memory.py`)
- `GET /api/memory/role` - Browse role memory archives
- `GET /api/memory/user` - Browse user memory archives
- `POST /api/memory/search` - Search memory archives
- `GET /api/memory/session/{id}` - Get session data

### Role API (`role.py`)
- `GET /api/role/current` - Get current active role
- `POST /api/role/switch` - Switch to different role
- `GET /api/role/capabilities` - Get role capabilities

### Session API (`session.py`)
- `GET /api/session/current` - Current session status
- `POST /api/session/archive` - Archive session data
- `POST /api/session/flush` - Flush sandbox (future)

### DEV API (`dev.py`) - Wizard + DEV Mode Only
- `GET /api/dev/workspace` - Access `/dev/` workspace
- `POST /api/dev/build` - Build/test core system
- `GET /api/dev/logs` - Core development logs

## Security & Access Control
- **Role-based access** - Endpoints respect role capabilities
- **DEV mode protection** - `/api/dev/*` requires Wizard + DEV mode
- **Session validation** - All requests validate active session
- **CORS handling** - Proper cross-origin configuration

---
**Development Phase**: v1.4 scaffolding complete, ready for implementation.
