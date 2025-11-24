# uDOS v1.0.19 - Teletext API Documentation

## Overview
Comprehensive REST API for uDOS command execution via Teletext GUI. Provides 61+ endpoints organized by category.

**Base URL**: `http://localhost:5000`

## Quick Start

### Start Server
```bash
./start_api.sh

# Or with custom port
PORT=8080 python api_server.py

# With debug mode
DEBUG=true python api_server.py
```

### Test API
```bash
# Health check
curl http://localhost:5000/api/health

# Execute command
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "HELP"}'

# List files
curl http://localhost:5000/api/files/list

# Get system status
curl http://localhost:5000/api/system/status
```

## API Endpoints

### Core (3 endpoints)

#### GET /
Serve Teletext HTML interface

#### GET /api/health
Server health check
```json
{
  "status": "healthy",
  "version": "1.0.19",
  "udos_available": true,
  "systems_initialized": true,
  "timestamp": "2024-12-15T10:30:00"
}
```

#### POST /api/command
Execute any uDOS command
```json
// Request
{"command": "THEME SET midnight"}

// Response
{
  "status": "success",
  "command": "THEME SET midnight",
  "output": "✅ Theme set to midnight",
  "timestamp": "2024-12-15T10:30:00"
}
```

---

### System Commands (10 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/help` | Get help information |
| GET | `/api/system/status` | System status |
| GET | `/api/system/config/list` | List all config |
| GET | `/api/system/config/get/<key>` | Get config value |
| POST | `/api/system/config/set` | Set config value |
| GET | `/api/system/repair` | Run system repair |
| POST | `/api/system/reboot` | Reboot uDOS |
| GET | `/api/system/version` | Get version info |
| GET | `/api/system/usage` | Usage statistics |
| POST | `/api/system/debug` | Toggle debug mode |

**Examples:**
```bash
# Get system status
curl http://localhost:5000/api/system/status

# Set config
curl -X POST http://localhost:5000/api/system/config/set \
  -H "Content-Type: application/json" \
  -d '{"key": "auto_save", "value": "true"}'

# Get version
curl http://localhost:5000/api/system/version
```

---

### File Commands (15 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/files/list?path=<path>` | List files |
| GET | `/api/files/recent?count=<n>` | Recent files |
| GET | `/api/files/search?q=<query>` | Search files |
| GET | `/api/files/info/<filepath>` | File info |
| GET | `/api/files/content/<filepath>` | Get file content |
| POST | `/api/files/create` | Create new file |
| POST | `/api/files/edit` | Edit file |
| DELETE | `/api/files/delete` | Delete file |
| POST | `/api/files/copy` | Copy file |
| POST | `/api/files/move` | Move/rename file |
| POST | `/api/files/run` | Run script |
| POST | `/api/files/bookmark/add` | Add bookmark |
| GET | `/api/files/bookmark/list` | List bookmarks |
| GET | `/api/files/stats` | File statistics |
| GET | `/api/files/tree` | Directory tree |

**Examples:**
```bash
# List files
curl http://localhost:5000/api/files/list

# Get recent files
curl http://localhost:5000/api/files/recent?count=5

# Create file
curl -X POST http://localhost:5000/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"path": "test.md", "content": "# Test"}'

# Run script
curl -X POST http://localhost:5000/api/files/run \
  -H "Content-Type: application/json" \
  -d '{"path": "examples/hello.uscript"}'
```

---

### Map Commands (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/map/show` | Show current map |
| GET | `/api/map/status` | Map status/position |
| POST | `/api/map/goto` | Go to location |
| POST | `/api/map/move` | Move in direction |
| POST | `/api/map/zoom` | Zoom map |
| GET | `/api/map/find?q=<query>` | Find location |
| GET | `/api/map/legend` | Get map legend |
| POST | `/api/map/save` | Save map |
| POST | `/api/map/load` | Load map |
| POST | `/api/map/export` | Export map data |
| GET | `/api/map/nearby` | Nearby locations |
| GET | `/api/map/distance?from=<loc1>&to=<loc2>` | Calculate distance |

**Examples:**
```bash
# Show map
curl http://localhost:5000/api/map/show

# Go to location
curl -X POST http://localhost:5000/api/map/goto \
  -H "Content-Type: application/json" \
  -d '{"location": "Melbourne"}'

# Zoom in
curl -X POST http://localhost:5000/api/map/zoom \
  -H "Content-Type: application/json" \
  -d '{"level": "in"}'
```

---

### Theme Commands (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/theme/list` | List themes |
| GET | `/api/theme/current` | Current theme |
| POST | `/api/theme/set` | Set theme |
| GET | `/api/theme/info/<name>` | Theme info |
| GET | `/api/theme/preview/<name>` | Preview theme |
| POST | `/api/theme/random` | Random theme |
| GET | `/api/theme/export/<name>` | Export theme |
| POST | `/api/theme/import` | Import theme |

**Examples:**
```bash
# List themes
curl http://localhost:5000/api/theme/list

# Set theme
curl -X POST http://localhost:5000/api/theme/set \
  -H "Content-Type: application/json" \
  -d '{"theme": "midnight"}'

# Get theme info
curl http://localhost:5000/api/theme/info/midnight
```

---

### Grid Commands (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/grid/view` | View grid layout |
| GET | `/api/grid/status` | Grid status |
| POST | `/api/grid/focus` | Focus panel |
| POST | `/api/grid/split` | Split panel |
| POST | `/api/grid/merge` | Merge panels |
| POST | `/api/grid/resize` | Resize panel |
| POST | `/api/grid/clear` | Clear panel |
| POST | `/api/grid/swap` | Swap panels |

**Examples:**
```bash
# View grid
curl http://localhost:5000/api/grid/view

# Focus panel
curl -X POST http://localhost:5000/api/grid/focus \
  -H "Content-Type: application/json" \
  -d '{"panel": "MAIN"}'

# Split panel
curl -X POST http://localhost:5000/api/grid/split \
  -H "Content-Type: application/json" \
  -d '{"direction": "horizontal"}'
```

---

### Assist Commands (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/assist/ask` | Ask OK assistant |
| POST | `/api/assist/explain` | Get explanation |
| POST | `/api/assist/debug` | Debug assistance |
| GET | `/api/assist/suggest?context=<ctx>` | Get suggestions |
| GET | `/api/assist/history?limit=<n>` | Command history |
| POST | `/api/assist/mode` | Toggle assist mode |

**Examples:**
```bash
# Ask assistant
curl -X POST http://localhost:5000/api/assist/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a map?"}'

# Get command history
curl http://localhost:5000/api/assist/history?limit=10
```

---

## WebSocket Events

### Connect
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to uDOS API');
});

socket.on('status', (data) => {
  console.log('Server status:', data);
});
```

### Execute Command
```javascript
socket.emit('execute_command', {
  command: 'FILE LIST'
});

socket.on('command_result', (result) => {
  console.log('Command result:', result);
});
```

### Subscribe to Updates
```javascript
socket.emit('subscribe_updates');

socket.on('subscribed', (data) => {
  console.log('Subscribed to updates');
});
```

---

## Response Format

### Success Response
```json
{
  "status": "success",
  "command": "FILE LIST",
  "output": "📁 Files:\n  - example.md\n  - test.uscript",
  "timestamp": "2024-12-15T10:30:00"
}
```

### Error Response
```json
{
  "status": "error",
  "command": "INVALID COMMAND",
  "message": "Unknown command",
  "output": ""
}
```

---

## CORS

CORS is enabled for all origins (`*`). For production, configure specific origins in `api_server.py`.

---

## Authentication

Currently no authentication. For production deployments, implement:
- JWT tokens
- API keys
- OAuth integration

---

## Rate Limiting

No rate limiting currently. Consider implementing for production:
- Flask-Limiter
- Request throttling
- Per-user quotas

---

## Testing

### Manual Testing
```bash
# Test all endpoints
./test_api.sh

# Test specific endpoint
curl -v http://localhost:5000/api/health
```

### Automated Testing
```bash
python test_api_endpoints.py
```

---

## Deployment

### Development
```bash
./start_api.sh
```

### Production
```bash
# With gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet api_server:app

# With systemd
sudo cp teletext-api.service /etc/systemd/system/
sudo systemctl enable teletext-api
sudo systemctl start teletext-api
```

---

## Total Endpoints

- **Core**: 3
- **System**: 10
- **Files**: 15
- **Map**: 12
- **Theme**: 8
- **Grid**: 8
- **Assist**: 6
- **Total**: 62 endpoints

---

## Version History

- **v1.0.19** (2024-12): Initial release with 62 endpoints
- WebSocket support
- CORS enabled
- Flask-SocketIO integration
