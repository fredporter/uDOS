# uNETWORK Server Examples

This directory contains example scripts and utilities for testing and managing the uDOS network server.

## Example Scripts

### 🔧 `manage-server.sh`
**Server management utility**

```bash
# Show server status
./manage-server.sh status

# Start the server
./manage-server.sh start

# Stop the server
./manage-server.sh stop

# Restart the server
./manage-server.sh restart

# View recent logs (default: 50 lines)
./manage-server.sh logs
./manage-server.sh logs 100

# Test server API
./manage-server.sh test
```

### 🌐 `test-api.py`
**HTTP API endpoint testing**

Tests common REST API endpoints for basic functionality:
- `/api/status` - System status
- `/api/system/info` - System information
- `/api/system/health` - Health check
- `/api/ucode/commands` - Available commands
- `/api/memory/stats` - Memory statistics

```bash
# Run API tests
./test-api.py

# Or via server manager
./manage-server.sh test
```

### 🔌 `test-websocket.py`
**WebSocket connectivity testing**

Tests real-time WebSocket features:
- Connection establishment
- Ping/pong functionality
- Echo testing
- System status updates

```bash
# Run WebSocket tests
./test-websocket.py
```

**Note**: Requires `python-socketio[client]` package:
```bash
pip install python-socketio[client]
```

## Usage Examples

### Quick Server Status Check
```bash
cd /Users/agentdigital/uDOS/uNETWORK/server/examples
./manage-server.sh status
```

### Full Server Testing Workflow
```bash
# Start server
./manage-server.sh start

# Test HTTP API
./test-api.py

# Test WebSocket connectivity
./test-websocket.py

# View recent activity
./manage-server.sh logs 20

# Stop server
./manage-server.sh stop
```

### Development Workflow
```bash
# During development, restart server and test
./manage-server.sh restart
sleep 2
./test-api.py
```

## Integration with uSCRIPT

These scripts work with the uSCRIPT virtual environment when available:

```bash
# Activate uSCRIPT environment first (optional)
cd ../../../uSCRIPT
source activate-venv.sh

# Then run tests
cd ../uNETWORK/server/examples
./test-api.py
./test-websocket.py
```

## Configuration

The scripts use these default settings:
- **Server URL**: `http://127.0.0.1:8080`
- **Timeout**: 5 seconds for API calls
- **PID file**: `/tmp/udos-server.pid`
- **Log file**: `../server.log`

Modify the configuration variables at the top of each script to customize behavior.

## Troubleshooting

### Server Not Starting
1. Check if port 8080 is available: `lsof -i :8080`
2. Check Python dependencies: `cd .. && python3 -c "import flask"`
3. Check uSCRIPT virtual environment: `cd ../../../uSCRIPT && ./uscript.sh env`

### API Tests Failing
1. Verify server is running: `./manage-server.sh status`
2. Check server logs: `./manage-server.sh logs`
3. Test basic connectivity: `curl http://127.0.0.1:8080`

### WebSocket Tests Failing
1. Install required package: `pip install python-socketio[client]`
2. Check if WebSocket is enabled in server config
3. Verify no firewall blocking WebSocket connections

## Development Notes

These examples demonstrate:
- **HTTP REST API** testing patterns
- **WebSocket** real-time communication
- **Process management** for server lifecycle
- **Error handling** and connectivity testing
- **Integration** with uDOS ecosystem components

Use these scripts as templates for building your own uNETWORK client applications and testing tools.
