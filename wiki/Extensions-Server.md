# Extensions Server v1.0.25

**Unified Python HTTP server for all uDOS web-based extensions**

## Overview

The Extensions Server is a centralized server system that manages all uDOS web extensions from a single entry point, providing consistent routing, CORS support, health checks, and status monitoring.

## Quick Start

### Launch All Extensions Status Page
```bash
cd /Users/fredbook/Code/uDOS/extensions/core
./launch.sh
```

View at: `http://localhost:8888/api/status`

### Launch Specific Extension
```bash
./launch.sh dashboard    # Port 8888
./launch.sh teletext     # Port 9002
./launch.sh terminal     # Port 8889
./launch.sh markdown     # Port 9000
./launch.sh character    # Port 8891
```

### From Extension Directory
```bash
cd extensions/core/dashboard
./start.sh
```

## Available Extensions

| Extension | Port | Command | Description |
|-----------|------|---------|-------------|
| **Dashboard** | 8888 | `./launch.sh dashboard` | NES-style customizable dashboard |
| **Teletext** | 9002 | `./launch.sh teletext` | BBC Teletext interface |
| **Terminal** | 8889 | `./launch.sh terminal` | C64-style web terminal |
| **Markdown** | 9000 | `./launch.sh markdown` | Knowledge base viewer |
| **Character** | 8891 | `./launch.sh character` | Pixel art editor |

## API Endpoints

### Extension Information
```bash
curl http://localhost:8888/api/extensions
```

Returns JSON with all extension configurations.

### Health Check
```bash
curl http://localhost:8888/api/health
```

Returns server health status.

### Status Page
```bash
open http://localhost:8888/api/status
```

HTML dashboard showing all extensions with links.

## Command Line Usage

### List Extensions
```bash
python3 extensions_server.py --list
```

### Run Extension
```bash
python3 extensions_server.py dashboard
python3 extensions_server.py teletext --port 8080
```

### Help
```bash
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

## Architecture

### Directory Structure
```
extensions/core/
├── extensions_server.py    # Unified server
├── launch.sh               # Launcher script
├── README-SERVER.md        # Documentation
├── CREDITS.md              # Attributions
├── dashboard/
│   ├── start.sh           # Dashboard launcher
│   └── ...
├── teletext/
│   ├── start.sh           # Teletext launcher
│   └── ...
└── [other extensions]/
```

### Configuration

Extensions are configured in `extensions_server.py`:

```python
EXTENSIONS = {
    'dashboard': {
        'port': 8888,
        'path': 'dashboard',
        'name': 'Dashboard Builder',
        'description': 'NES-style customizable dashboard',
        'enabled': True
    },
    # ...
}
```

## Benefits

### Before (Individual Servers)
```bash
cd dashboard && python3 -m http.server 8888 &
cd teletext && python3 -m http.server 9002 &
cd terminal && python3 -m http.server 8889 &
# Multiple processes to manage...
```

### After (Unified Server)
```bash
./launch.sh dashboard    # Single command
```

**Advantages:**
- ✅ Single process management
- ✅ Consistent configuration
- ✅ Centralized logging
- ✅ Built-in status monitoring
- ✅ CORS support included
- ✅ Easy to extend
- ✅ Better error handling

## Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :8888

# Kill process
pkill -f 'python.*8888'

# Or use different port
./launch.sh dashboard 9999
```

### Extension Not Found
```bash
# Verify extension path
ls -la dashboard/

# Check configuration
python3 extensions_server.py --list
```

## Production Deployment

### systemd Service
```ini
[Unit]
Description=uDOS Extensions Server - Dashboard
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

## Related Pages

- [[Extensions-System]] - Overview of extensions architecture
- [[Dashboard-Builder]] - Dashboard extension details
- [[Teletext-Synthwave]] - Teletext extension details
- [[Terminal-Extension]] - Terminal extension details

## Version History

### v1.0.25 (November 2024)
- ✨ Initial unified server implementation
- 🎮 Support for 5 core extensions
- 📊 Status monitoring and health checks
- 🔧 CORS and custom routing
- 🎨 Colored logging output

---

**READY.**
