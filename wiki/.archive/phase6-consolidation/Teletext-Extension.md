# uDOS Teletext Extension

**Complete guide to the Teletext web extension for uDOS**

> **📺 Classic BBC Ceefax Mode 7 Graphics** - Authentic 40×25 character grid with synthwave colors

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Theming](#theming)
5. [Assets](#assets)
6. [Credits](#credits)

---

## Overview

The Teletext extension recreates the classic BBC Ceefax broadcast information system with modern enhancements. It provides a web-based interface for uDOS with authentic teletext rendering and the Synthwave DOS color palette.

### Features

- **Authentic Rendering**: 40×25 character grid
- **Mode 7 Graphics**: Classic block graphics and control codes
- **Mallard Fonts**: 6 authentic BBC Teletext font variants
- **Synthwave Colors**: Modern color palette integration
- **REST API**: 61+ endpoints for command execution
- **Real-time Updates**: WebSocket support for live data

### Technical Specs

- **Character Set**: 40×25 character grid
- **Fonts**: Mallard family (6 variants) + MODE7GX3
- **Colors**: 8 colors (black, red, green, yellow, blue, magenta, cyan, white)
- **Graphics**: Mode 7 block characters
- **Refresh**: Automatic page cycling

---

## Quick Start

### Starting the Extension

```bash
# Using POKE command
POKE START teletext

# Direct launch
python extensions/core/extensions_server.py teletext

# With custom port
PORT=8080 python extensions/core/extensions_server.py teletext
```

### Accessing the Interface

Open browser to: `http://localhost:8888`

### Basic Navigation

- **Arrow Keys**: Navigate pages
- **Number Keys**: Direct page access (100-999)
- **Index**: Press `i` for main index
- **Hold**: Space to pause cycling

---

## API Reference

**Base URL**: `http://localhost:5000` (when API server running)

### Core Endpoints

#### Health Check
```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "udos_available": true,
  "timestamp": "2025-11-26T10:30:00"
}
```

#### Execute Command
```bash
POST /api/command
Content-Type: application/json

{
  "command": "STATUS"
}
```

Response:
```json
{
  "status": "success",
  "command": "STATUS",
  "output": "✅ System ready",
  "timestamp": "2025-11-26T10:30:00"
}
```

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

### File Operations (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/files/list` | List files in directory |
| GET | `/api/files/read` | Read file content |
| POST | `/api/files/write` | Write file content |
| POST | `/api/files/delete` | Delete file |
| POST | `/api/files/copy` | Copy file |
| POST | `/api/files/move` | Move/rename file |
| POST | `/api/files/mkdir` | Create directory |
| GET | `/api/files/tree` | Directory tree |

### Knowledge Bank (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/knowledge/list` | List knowledge files |
| GET | `/api/knowledge/search` | Search knowledge |
| GET | `/api/knowledge/read` | Read knowledge file |
| GET | `/api/knowledge/categories` | List categories |
| GET | `/api/knowledge/recent` | Recent updates |
| GET | `/api/knowledge/stats` | Knowledge stats |

### AI Integration (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/ask` | Ask AI question |
| GET | `/api/ai/history` | Conversation history |
| POST | `/api/ai/clear` | Clear history |
| GET | `/api/ai/prompts/list` | List prompts |
| GET | `/api/ai/prompts/get/<name>` | Get prompt |

### Additional Categories

- **Panel Commands** (7 endpoints): Display management
- **Grid Commands** (5 endpoints): Grid operations
- **Theme Commands** (6 endpoints): Theme management
- **Navigation** (4 endpoints): Map/location
- **Barter** (3 endpoints): Trading system
- **Diagrams** (3 endpoints): Visualization
- **Utilities** (5 endpoints): Tools and helpers

**Complete API Documentation**: See `/extensions/web/teletext/API.md`

---

## Theming

The Teletext extension uses the **Synthwave DOS** color palette for authentic retro aesthetics with modern visibility.

### Default Theme

```css
:root {
  --teletext-bg: #000000;          /* Black background */
  --teletext-fg: #FFFFFF;          /* White text */
  --teletext-red: #FF1744;         /* Synthwave Red */
  --teletext-green: #00E676;       /* Synthwave Green */
  --teletext-yellow: #FFEB3B;      /* Synthwave Yellow */
  --teletext-blue: #2196F3;        /* Synthwave Blue */
  --teletext-magenta: #E91E63;     /* Synthwave Purple */
  --teletext-cyan: #00E5FF;        /* Synthwave Cyan */
}
```

### Classic BBC Theme

```css
:root {
  --teletext-bg: #000000;
  --teletext-fg: #FFFFFF;
  --teletext-red: #FF0000;
  --teletext-green: #00FF00;
  --teletext-yellow: #FFFF00;
  --teletext-blue: #0000FF;
  --teletext-magenta: #FF00FF;
  --teletext-cyan: #00FFFF;
}
```

### Customization

Edit `extensions/web/teletext/styles/teletext.css` and modify CSS variables.

---

## Assets

### Fonts

**Mallard Family** (6 variants) - CC BY-SA 3.0
- `Mallard` - Standard Mode 7
- `Mallard-Bold` - Bold weight
- `Mallard-Italic` - Italic style
- `Mallard-BoldItalic` - Bold italic
- `Mallard-Narrow` - Condensed
- `Mallard-Wide` - Extended

**Fallback**: MODE7GX3 (BBC Micro Mode 7)

**Location**: `extensions/assets/fonts/mallard/`

**Loading**:
```python
from core.services.asset_manager import get_asset_manager

mgr = get_asset_manager()
font = mgr.load_font('mallard')
```

### Graphics

**Control Codes**:
- **Color Control**: Set foreground/background colors
- **Graphics Mode**: Enable block graphics
- **Flash**: Flashing text
- **Double Height**: 2× height characters
- **Hold Graphics**: Maintain graphic state
- **Release Graphics**: Return to text mode

**Block Characters**:
```
▀ ▄ █ ▌ ▐ ░ ▒ ▓
```

Used for Mode 7 graphics rendering.

---

## Credits

### Teletext Standard

**BBC Ceefax** - British Broadcasting Corporation
- Original broadcast teletext service (1974-2012)
- Mode 7 character set specification
- 40×25 character grid format

### Fonts

**Mallard Font Family** - CC BY-SA 3.0
- **Author**: "gid" (FontStruct.com)
- **License**: Creative Commons Attribution-ShareAlike 3.0
- **Location**: `extensions/assets/fonts/mallard/`
- **Full License**: `extensions/assets/fonts/mallard/LICENSE.txt`

### Color Palette

**Synthwave DOS Colors**
- **Creator**: Fred Porter
- **Purpose**: Modern high-contrast palette for retro terminals
- **Integration**: BBC Teletext standards with Synthwave aesthetics

### Technical Implementation

**CSS3 Features**:
- Mode 7 graphics emulation
- Block character rendering
- Grid layout (40×25)
- Teletext control codes

**HTML5 Canvas**:
- Character rendering
- Graphics mode switching
- Real-time updates

### Design References

**Historical Accuracy**:
- BBC Engineering Information Dept. (1976)
- Mode 7 Display Standards
- Ceefax Technical Specifications
- Teletext Control Code Documentation

**Modern Enhancements**:
- Responsive design
- WebSocket communication
- REST API integration
- Asset management system

---

## Development

### File Structure

```
extensions/web/teletext/
├── index.html           # Main teletext page
├── teletext.html        # Teletext viewer
├── styles/
│   └── teletext.css     # Teletext styling
├── scripts/
│   └── teletext.js      # Client-side logic
└── API.md              # Complete API docs
```

### Integration

**Server**: `extensions/core/extensions_server.py`
**Port**: 8888 (default)
**Protocol**: HTTP + WebSocket

### Testing

```bash
# Start extension
POKE START teletext

# Test API
curl http://localhost:5000/api/health

# View in browser
open http://localhost:8888
```

---

## Version History

- **v1.0.19** - Synthwave DOS color integration
- **v1.0.0** - Initial stable release with 61+ API endpoints

---

## Additional Resources

- **[Style Guide](Style-Guide.md)** - Design conventions
- **[ASSETS-GUIDE](ASSETS-GUIDE.md)** - Asset management
- **[Extensions System](Extensions-System.md)** - Extension development

---

**Teletext Extension** - Bringing BBC Ceefax to the modern age with synthwave style.
