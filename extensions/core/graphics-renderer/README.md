# Graphics Renderer Service

**Version:** 1.2.15  
**Port:** 5555  
**Type:** Node.js Service Extension

## Overview

The Graphics Renderer Service is a Node.js-based rendering engine that provides backend support for all 5 uDOS graphics formats:

1. **ASCII** - Template-based ASCII art with variable substitution
2. **Teletext** - 8-color teletext pages with palette support
3. **SVG** - AI-assisted SVG generation with style templates
4. **Sequence** - Sequence diagrams using js-sequence-diagrams
5. **Flow** - Flowcharts using flowchart.js

## Architecture

```
┌─────────────────────────────────────────────────┐
│         uDOS Core (Python)                      │
│  ┌──────────────────────────────────┐           │
│  │  core/services/graphics_service  │           │
│  │  (Python Bridge)                 │           │
│  └──────────────┬───────────────────┘           │
│                 │ HTTP/JSON                     │
│                 ▼                                │
│  ┌──────────────────────────────────┐           │
│  │  extensions/core/graphics-renderer│          │
│  │  (Node.js Service - Port 5555)   │          │
│  │                                   │          │
│  │  ┌──────────────────────────┐    │          │
│  │  │  Express Server          │    │          │
│  │  └──────┬───────────────────┘    │          │
│  │         │                         │          │
│  │    ┌────┴─────┬─────┬─────┬─────┤          │
│  │    │          │     │     │     │           │
│  │  ASCII   Teletext SVG  Seq  Flow│          │
│  │  Renderer Renderer  │  Diagram  │          │
│  │                      │  Renderer │          │
│  └──────────────────────┴───────────┘          │
└─────────────────────────────────────────────────┘
                 │
                 ▼
         core/data/diagrams/
         (Template Library)
```

## Installation

```bash
cd extensions/core/graphics-renderer
npm install
```

## Usage

### Start Service

```bash
# Production
npm start

# Development (with auto-reload)
npm run dev
```

### Health Check

```bash
curl http://localhost:5555/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.2.15",
  "service": "uDOS Graphics Renderer",
  "formats": ["ascii", "teletext", "svg", "sequence", "flow"],
  "port": 5555,
  "uptime": 123.45
}
```

## API Endpoints

### ASCII Rendering

```bash
POST /render/ascii
Content-Type: application/json

{
  "template": "flowchart_vertical",
  "data": {
    "title": "My Process"
  },
  "options": {
    "width": 80,
    "border": true
  }
}
```

### Teletext Rendering

```bash
POST /render/teletext
Content-Type: application/json

{
  "content": "{green}Welcome{/green} to {cyan}uDOS{/cyan}",
  "palette": "earth",
  "options": {
    "width": 40,
    "height": 24,
    "background": true
  }
}
```

### SVG Rendering

```bash
POST /render/svg
Content-Type: application/json

{
  "description": "system architecture with 3 layers",
  "style": "technical",
  "options": {
    "width": 800,
    "height": 600
  }
}
```

### Sequence Diagram

```bash
POST /render/sequence
Content-Type: application/json

{
  "source": "message_flow",
  "options": {
    "theme": "simple"
  }
}
```

### Flowchart

```bash
POST /render/flow
Content-Type: application/json

{
  "source": "decision_flow",
  "options": {
    "lineWidth": 2,
    "fontSize": 14
  }
}
```

### List Templates

```bash
GET /templates/ascii
GET /templates/sequence
GET /templates/flow
```

## Python Integration

```python
from core.services.graphics_service import get_graphics_service

# Get service instance
graphics = get_graphics_service()

# Check availability
if graphics.is_available():
    # Render ASCII
    ascii_diagram = graphics.render_ascii("flowchart_vertical")
    
    # Render teletext
    teletext = graphics.render_teletext(
        content="{green}Status: OK{/green}",
        palette="terminal"
    )
    
    # Render sequence diagram
    sequence_svg = graphics.render_sequence("api_request")
    
    # Render flowchart
    flow_svg = graphics.render_flow("login_process")
```

## Renderers

### ASCII Renderer (`renderers/ascii.js`)
- Loads templates from `core/data/diagrams/ascii/`
- Variable substitution: `{variable_name}`
- Options: width, border
- Returns: Plain text ASCII art

### Teletext Renderer (`renderers/teletext.js`)
- Loads palettes from `core/data/diagrams/teletext/`
- Color tags: `{red}text{/red}`, `{green}text{/green}`, etc.
- 8-color standard: black, red, green, yellow, blue, magenta, cyan, white
- Returns: ANSI-colored text

### SVG Renderer (`renderers/svg.js`)
- Loads styles from `core/data/diagrams/svg/`
- AI-assisted generation (placeholder in v1.2.15)
- Styles: technical, simple, detailed
- Returns: SVG markup

### Sequence Renderer (`renderers/sequence.js`)
- Uses js-sequence-diagrams library
- Loads templates from `core/data/diagrams/sequence/`
- Syntax: `Actor1->Actor2: Message`
- Returns: SVG markup

### Flow Renderer (`renderers/flow.js`)
- Uses flowchart.js library
- Loads templates from `core/data/diagrams/flow/`
- Syntax: `st=>start: Start\nst->end`
- Returns: SVG markup

## Configuration

### Environment Variables

- `GRAPHICS_PORT` - Service port (default: 5555)
- `NODE_ENV` - Environment (development, production)

### Extension Manager Integration

The service is registered in the extension manager and can be controlled via:

```python
from extensions.server_manager import get_server_manager

mgr = get_server_manager()
mgr.start_extension("graphics-renderer")
mgr.stop_extension("graphics-renderer")
mgr.get_status("graphics-renderer")
```

## Dependencies

- **express** - Web framework
- **body-parser** - JSON parsing
- **cors** - Cross-origin support
- **js-sequence-diagrams** - Sequence diagram rendering
- **flowchart.js** - Flowchart rendering
- **canvas** - Canvas API for Node.js
- **puppeteer** - Headless browser (for complex rendering)

## Development

### Adding New Templates

1. Add template file to `core/data/diagrams/<format>/`
2. Update `core/data/diagrams/catalog.json`
3. Restart service (auto-reload in dev mode)

### Adding New Renderers

1. Create `renderers/new_format.js`
2. Implement `render()` and `listTemplates()` methods
3. Add endpoint in `server.js`
4. Update `extension.json` and `catalog.json`

### Testing

```bash
npm test
```

## Troubleshooting

### Service won't start
- Check Node.js version: `node --version` (need 18+)
- Check port availability: `lsof -i :5555`
- Check logs in console output

### Connection refused
- Ensure service is running: `curl http://localhost:5555/health`
- Check firewall settings
- Verify port in Python bridge matches service port

### Rendering errors
- Check template exists: `GET /templates/<format>`
- Validate syntax (sequence/flow formats)
- Check service logs for detailed errors

## Credits

**v1.2.15 Graphics Renderer** (December 2025)
- Node.js service architecture
- 5-format rendering system
- Python bridge integration
- Template library foundation

**Built on v1.2.12:**
- PATHS constants
- Folder structure standardization
- Extension manager integration

## See Also

- `core/services/graphics_service.py` - Python bridge
- `core/data/diagrams/README.md` - Template library
- `wiki/Graphics-System.md` - Complete documentation
- `extensions/PORT-REGISTRY.md` - Port assignments
