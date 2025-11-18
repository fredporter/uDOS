# uDOS Core Extensions Server v1.0.25

**Unified Python HTTP server for all web-based extensions**

## Overview

A centralized server system that manages all uDOS web extensions from a single entry point, providing consistent routing, CORS support, health checks, and status monitoring.

## Quick Start

### Launch All Extensions (Status Page)
```bash
cd /Users/fredbook/Code/uDOS/extensions/core
./launch.sh
```

Open: `http://localhost:8888/api/status`

### Launch Specific Extension
```bash
./launch.sh dashboard    # Port 8888
./launch.sh teletext     # Port 9002
./launch.sh terminal     # Port 8889
./launch.sh markdown     # Port 9000
./launch.sh character    # Port 8891
```

### Custom Port
```bash
./launch.sh dashboard 9999
```

## Available Extensions

| Extension | Port | Path | Description |
|-----------|------|------|-------------|
| **Dashboard** | 8888 | `dashboard/` | NES-style customizable dashboard |
| **Teletext** | 9002 | `teletext/` | BBC Teletext with Synthwave DOS styling |
| **Terminal** | 8889 | `terminal/` | Commodore 64 style terminal |
| **Markdown** | 9000 | `markdown/` | Knowledge base markdown viewer |
| **Character** | 8891 | `character/` | Pixel art and character editor |

## API Endpoints

### `/api/extensions`
Returns JSON configuration of all extensions
```bash
curl http://localhost:8888/api/extensions
```

### `/api/health`
Health check endpoint
```bash
curl http://localhost:8888/api/health
```

### `/api/status`
HTML status page showing all extensions
```bash
open http://localhost:8888/api/status
```

## Python API Usage

### Run from Python
```python
from extensions_server import run_server

# Run specific extension
run_server('dashboard', port=8888)

# Run status server
run_server()
```

### Command Line
```bash
# List extensions
python3 extensions_server.py --list

# Run dashboard
python3 extensions_server.py dashboard

# Run with custom port
python3 extensions_server.py teletext --port 8080

# Show help
python3 extensions_server.py --help
```

## Features

### ✨ Unified Management
- Single server script for all extensions
- Consistent configuration
- Centralized logging
- Easy port management

### 🔧 CORS Support
- Cross-origin headers enabled
- OPTIONS preflight handling
- Works with all modern browsers

### 📊 Status Monitoring
- Real-time extension status
- Health check endpoints
- JSON API for automation
- HTML dashboard

### 🎨 Colored Logging
- ANSI color-coded output
- Clear extension identification
- Request/response logging
- Error highlighting

### 🚀 Easy Deployment
- Single command launch
- No dependencies beyond Python 3
- Works on all platforms
- Background daemon support

## Directory Structure

```
extensions/core/
├── extensions_server.py    # Unified server script
├── launch.sh               # Convenient launcher
├── dashboard/              # Dashboard extension
│   ├── index.html
│   ├── dashboard-builder.js
│   └── dashboard-styles.css
├── teletext/               # Teletext extension
│   ├── index.html
│   ├── teletext-core.js
│   └── teletext-synthwave.css
├── terminal/               # Terminal extension
├── markdown/               # Markdown viewer
└── character/              # Character editor
```

## Configuration

Edit `EXTENSIONS` dict in `extensions_server.py`:

```python
EXTENSIONS = {
    'dashboard': {
        'port': 8888,
        'path': 'dashboard',
        'name': 'Dashboard Builder',
        'description': 'NES-style customizable dashboard',
        'enabled': True
    },
    # Add more extensions...
}
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8888

# Kill process
pkill -f 'python.*8888'

# Or use different port
./launch.sh dashboard 9999
```

### Extension Not Found
```bash
# Verify extension path exists
ls -la dashboard/

# Check configuration
python3 extensions_server.py --list
```

### CORS Issues
CORS is enabled by default. If you still have issues:
- Check browser console for errors
- Verify server is running
- Clear browser cache

## Development

### Adding New Extensions

1. Create extension directory:
```bash
mkdir extensions/core/myextension
```

2. Add to `EXTENSIONS` in `extensions_server.py`:
```python
'myextension': {
    'port': 9999,
    'path': 'myextension',
    'name': 'My Extension',
    'description': 'Description here',
    'enabled': True
}
```

3. Launch:
```bash
./launch.sh myextension
```

### Custom Handlers

Extend `ExtensionHandler` class for custom routing:

```python
def do_GET(self):
    if self.path == '/api/myendpoint':
        self.serve_custom_endpoint()
        return
    super().do_GET()

def serve_custom_endpoint(self):
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps({'status': 'ok'}).encode())
```

## Benefits Over Individual Servers

### Before (Individual Scripts)
```bash
cd dashboard && python3 -m http.server 8888 &
cd teletext && python3 -m http.server 9002 &
cd terminal && python3 -m http.server 8889 &
# ... manage multiple processes
```

### After (Unified Server)
```bash
./launch.sh dashboard    # Single command
# Or run status page to see all
./launch.sh
```

**Advantages:**
- ✅ Single process management
- ✅ Consistent configuration
- ✅ Centralized logging
- ✅ Built-in status monitoring
- ✅ CORS support included
- ✅ Easy to extend
- ✅ Better error handling

## Production Deployment

### systemd Service
```ini
[Unit]
Description=uDOS Extensions Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/uDOS/extensions/core
ExecStart=/usr/bin/python3 extensions_server.py dashboard
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker
```dockerfile
FROM python:3-alpine
WORKDIR /app
COPY extensions/core /app
EXPOSE 8888
CMD ["python3", "extensions_server.py", "dashboard"]
```

## Version History

### v1.0.25 (Current)
- ✨ Initial unified server implementation
- 🎮 Support for 5 core extensions
- 📊 Status monitoring and health checks
- 🔧 CORS and custom routing
- 🎨 Colored logging output

## License

MIT License - Part of uDOS v1.0.25

---

**READY.**
