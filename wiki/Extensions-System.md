# Extensions System

**Complete guide to uDOS extensions: bundled extensions, external dependencies, and unified server management**

> **💡 Quick Start**: Launch extensions with `./launch.sh dashboard` or install external tools with `./extensions/setup/setup_all.sh`

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Extensions Server](#extensions-server)
4. [Bundled Web Extensions](#bundled-web-extensions)
5. [External Dependencies](#external-dependencies)
6. [Quick Start Guide](#quick-start-guide)
7. [API & Configuration](#api--configuration)
8. [Development Guidelines](#development-guidelines)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The uDOS Extensions System provides a clean separation between bundled native extensions and external dependencies, ensuring legal compliance and maintainable development. It includes a unified server for managing all web-based extensions from a single entry point.

### Key Features

- 🎮 **Unified Server**: Single entry point for all web extensions
- 📦 **Bundled Extensions**: Native uDOS extensions (git tracked)
- 🔌 **External Dependencies**: Optional third-party tools (git ignored)
- 🔧 **CORS Support**: Cross-origin headers enabled
- 📊 **Status Monitoring**: Real-time extension status
- ⚖️ **Legal Compliance**: Proper licensing for all bundled assets

---

## Directory Structure

```
extensions/
├── core/                       # Unified server system
│   ├── extensions_server.py   # Unified Python HTTP server
│   ├── launch.sh              # Launcher script
│   ├── README-SERVER.md       # Server documentation
│   └── CREDITS.md             # Attributions
├── bundled/                   # uDOS-native extensions (git tracked)
│   └── web/                   # Web-based UI extensions
│       ├── dashboard/        # System dashboard interface
│       ├── font-editor/      # Web-based font editing tools
│       ├── shared/           # Shared CSS/JS libraries
│       ├── system-desktop/   # System 7 desktop environment
│       ├── system-style/     # OS styling frameworks
│       └── teletext/         # Broadcast TV interface
├── cloned/                    # External repositories (git ignored)
│   ├── micro/                # Modern terminal editor
│   ├── typo/                 # Web-based markdown editor
│   ├── monaspace-fonts/      # GitHub Next monospace fonts
│   ├── classicy-desktop/     # Mac OS 8 Platinum interface
│   ├── c64css3/              # Commodore 64 CSS framework
│   ├── nes-css/              # 8-bit Nintendo CSS framework
│   └── cmd/                  # Web terminal (optional)
├── fonts/                     # Font assets with licensing
└── setup/                     # Installation scripts
```

---

## Extensions Server

### Unified Server (v1.0.25)

The Extensions Server is a centralized system that manages all uDOS web extensions from a single entry point, providing consistent routing, CORS support, health checks, and status monitoring.

### Launch Server

#### All Extensions Status Page
```bash
cd /Users/fredbook/Code/uDOS/extensions/core
./launch.sh
```

View at: `http://localhost:8888/api/status`

#### Launch Specific Extension
```bash
./launch.sh dashboard    # Port 8888
./launch.sh teletext     # Port 9002
./launch.sh terminal     # Port 8889
./launch.sh markdown     # Port 9000
./launch.sh character    # Port 8891
```

#### From Extension Directory
```bash
cd extensions/core/dashboard
./start.sh
```

### Available Extensions

| Extension | Port | Command | Description |
|-----------|------|---------|-------------|
| **Dashboard** | 8888 | `./launch.sh dashboard` | NES-style customizable dashboard |
| **Teletext** | 9002 | `./launch.sh teletext` | BBC Teletext interface |
| **Terminal** | 8889 | `./launch.sh terminal` | C64-style web terminal |
| **Markdown** | 9000 | `./launch.sh markdown` | Knowledge base viewer |
| **Character** | 8891 | `./launch.sh character` | Pixel art editor |

### Server Features

#### ✨ Unified Management
- Single server script for all extensions
- Consistent configuration
- Centralized logging
- Easy port management

#### 🔧 CORS Support
- Cross-origin headers enabled
- OPTIONS preflight handling
- Works with all modern browsers

#### 📊 Status Monitoring
- Real-time extension status
- Health check endpoints
- JSON API for automation
- HTML dashboard

#### 🎨 Colored Logging
- ANSI color-coded output
- Clear extension identification
- Request/response logging

### Architecture

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

### Benefits Over Individual Servers

**Before (Individual Servers)**:
```bash
cd dashboard && python3 -m http.server 8888 &
cd teletext && python3 -m http.server 9002 &
cd terminal && python3 -m http.server 8889 &
# Multiple processes to manage...
```

**After (Unified Server)**:
```bash
./launch.sh dashboard    # Single command
```

**Advantages**:
- ✅ Single process management
- ✅ Consistent configuration
- ✅ Centralized logging
- ✅ Built-in status monitoring
- ✅ CORS support included
- ✅ Easy to extend
- ✅ Better error handling

---

## Bundled Web Extensions

### Dashboard
- **Purpose**: Multi-theme system dashboard interface
- **Technology**: HTML5 + CSS3 + JavaScript
- **Features**: Real-time metrics, file browser integration
- **Port**: 8080 (default) / 8888 (unified server)
- **Status**: ✅ Tested & Working

### System Desktop
- **Purpose**: System 7 desktop environment recreation
- **Technology**: Pure CSS3 + JavaScript
- **Features**: Classic Mac window management
- **Port**: 8082 (default)
- **Status**: ✅ Tested & Working

### Teletext
- **Purpose**: Broadcast television teletext interface
- **Technology**: CSS + JavaScript with block characters
- **Features**: Mosaic mode, classic TV styling
- **Port**: 8081 (default) / 9002 (unified server)
- **Status**: ✅ Tested & Working

### Terminal
- **Purpose**: C64-style web terminal
- **Technology**: HTML5 + JavaScript
- **Features**: Command execution, retro styling
- **Port**: 8889 (unified server)
- **Status**: ✅ Tested & Working

### Markdown Viewer
- **Purpose**: Knowledge base viewer
- **Technology**: JavaScript markdown parser
- **Features**: Real-time rendering, syntax highlighting
- **Port**: 9000 (unified server)
- **Status**: ✅ Tested & Working

### Font Editor
- **Purpose**: Web-based font editing tools
- **Technology**: Canvas API + JavaScript
- **Features**: Pixel-level editing, export formats
- **Status**: 🚧 In Development

### Shared Libraries
- **Purpose**: Common CSS/JS frameworks for all extensions
- **Components**: Typography system, UI components, grid system
- **Usage**: Foundation for all uDOS web interfaces

---

## External Dependencies

### Classicy Desktop
- **Repository**: https://github.com/robbiebyrd/classicy
- **Description**: Authentic Mac OS 8 Platinum interface
- **Features**: React-based, window management, classic styling
- **Setup**: `./extensions/setup/setup_classicy.sh`

### C64 CSS3
- **Repository**: https://github.com/RoelN/c64css3
- **Description**: Commodore 64 styling framework
- **Features**: Pixel-perfect C64 colors, fonts, interface elements
- **Setup**: `./extensions/setup/setup_c64css3.sh`

### NES.css
- **Repository**: https://github.com/nostalgic-css/NES.css
- **Description**: 8-bit Nintendo Entertainment System CSS framework
- **Features**: Authentic NES styling, 8-bit fonts, pixel art support
- **Setup**: `./extensions/setup/setup_nes.sh`

### micro Editor
- **Repository**: https://github.com/zyedidia/micro
- **Description**: Modern terminal-based text editor
- **Features**: Syntax highlighting, plugin system, modern keybindings
- **Setup**: `./extensions/setup/setup_micro.sh`

### typo Editor
- **Repository**: https://github.com/rossrobino/typo
- **Description**: Minimalist web-based markdown editor
- **Features**: Real-time preview, clean interface, export options
- **Setup**: `./extensions/setup/setup_typo.sh`

---

## Quick Start Guide

### Install All External Dependencies
```bash
# Install all essential external tools
./extensions/setup/setup_all.sh

# Or install individually
./extensions/setup/setup_micro.sh       # Modern terminal editor
./extensions/setup/setup_typo.sh        # Web markdown editor
./extensions/setup/setup_classicy.sh    # Mac OS 8 interface
./extensions/setup/setup_c64css3.sh     # C64 styling framework
./extensions/setup/setup_nes.sh         # NES styling framework
```

### Launch Bundled Extensions

#### Using Unified Server (Recommended)
```bash
cd extensions/core
./launch.sh dashboard    # Launch dashboard on port 8888
./launch.sh teletext     # Launch teletext on port 9002
./launch.sh terminal     # Launch terminal on port 8889
```

#### Using Individual Servers
```bash
cd extensions/core/dashboard && ./start.sh
cd extensions/bundled/web/system-desktop && python3 -m http.server 8082
cd extensions/bundled/web/teletext && python3 -m http.server 8081
```

---

## API & Configuration

### API Endpoints

#### Extension Information
```bash
curl http://localhost:8888/api/extensions
```

Returns JSON with all extension configurations.

#### Health Check
```bash
curl http://localhost:8888/api/health
```

Returns server health status.

#### Status Page
```bash
open http://localhost:8888/api/status
```

HTML dashboard showing all extensions with links.

### Command Line Usage

#### List Extensions
```bash
python3 extensions_server.py --list
```

#### Run Extension
```bash
python3 extensions_server.py dashboard
python3 extensions_server.py teletext --port 8080
```

#### Help
```bash
python3 extensions_server.py --help
```

### Production Deployment

#### systemd Service
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

#### Docker
```dockerfile
FROM python:3-alpine
WORKDIR /app
COPY extensions/core /app
EXPOSE 8888
CMD ["python3", "extensions_server.py", "dashboard"]
```

---

## Development Guidelines

### Adding Bundled Extensions

1. Create extension in `bundled/web/[extension-name]/`
2. Include README.md with description and usage
3. Add launch script if needed
4. Update server configuration in `extensions_server.py`
5. Update main README with extension details
6. Commit to git repository

**Example Server Configuration**:
```python
EXTENSIONS = {
    'myextension': {
        'port': 9999,
        'path': 'myextension',
        'name': 'My Extension',
        'description': 'Description of extension',
        'enabled': True
    }
}
```

### Adding External Dependencies

1. Create setup script in `setup/setup_[name].sh`
2. Configure to clone into `cloned/[name]/`
3. Update `setup_all.sh` to include new dependency
4. Test installation process
5. Update documentation

**Example Setup Script**:
```bash
#!/bin/bash
CLONE_DIR="extensions/cloned/myextension"

if [ -d "$CLONE_DIR" ]; then
    echo "✅ myextension already installed"
else
    git clone https://github.com/user/repo.git "$CLONE_DIR"
    echo "✅ myextension installed"
fi
```

---

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

### CORS Issues
The unified server includes CORS headers by default. If you still experience issues:

```python
# Verify CORS headers in response
curl -I http://localhost:8888/
# Should include: Access-Control-Allow-Origin: *
```

### Server Won't Start
```bash
# Check Python version (requires 3.6+)
python3 --version

# Check for syntax errors
python3 -m py_compile extensions_server.py

# Run with verbose logging
python3 extensions_server.py dashboard --verbose
```

---

## Legal Compliance

### Bundled Font Licenses

All bundled fonts are legally distributable:
- **ChicagoFLF**: Public domain
- **Chicago 12.1**: CC BY-SA 3.0
- **Mallard family**: CC BY-SA 3.0
- **sysfont**: SIL Open Font License 1.1

See `extensions/fonts/LICENSE_ASSESSMENT.md` for complete legal analysis.

### External Dependencies

External dependencies maintain their original licenses:
- Classicy Desktop: Check repository license
- C64 CSS3: MIT License
- NES.css: MIT License
- micro: MIT License
- typo: MIT License

---

## Platform Support

### Tested Platforms
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Arch)
- ✅ Windows (WSL2 recommended)

### Browser Compatibility
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## Version History

### v1.0.25 (November 2024)
- ✨ Initial unified server implementation
- 🎮 Support for 5 core extensions
- 📊 Status monitoring and health checks
- 🔧 CORS and custom routing
- 🎨 Colored logging output
- 📦 Clean bundled/cloned separation
- ⚖️ Legal compliance verification

---

## Related Documentation

- [Dashboard Builder](Dashboard-Builder.md) - Dashboard extension details
- [Teletext](Teletext-Synthwave.md) - Teletext extension details
- [Terminal Extension](Terminal-Extension.md) - Terminal extension details
- [Command Reference](Command-Reference.md) - uDOS commands

---

**The uDOS Extensions system provides a clean separation between bundled content and external dependencies, with unified server management for all web extensions.**

**READY.**
