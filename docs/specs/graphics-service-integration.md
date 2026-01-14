# Graphics Service Integration: API → Core → App

**Date:** 2026-01-14  
**Status:** Architecture Documentation  
**Version:** Alpha v1.0.2.0

---

## Overview: Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│ MARKDOWN SOURCE (Knowledge Base)                             │
│ flowchart.js | Mermaid | Marp | Inline in guides           │
└────────┬─────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
    ┌────▼──────────┐               ┌─────────▼────────┐
    │ Core (TUI)    │               │ App (Tauri)      │
    │               │               │                  │
    │ Graphics      │               │ DiagramRenderer  │
    │ Service Client│               │ (SVG processor)  │
    │ (Port 5555)   │               │                  │
    └────┬──────────┘               └─────────┬────────┘
         │                                    │
         │ render_ascii()                     │ render_svg()
         │ render_teletext()                  │
         │                                    │
         └─────────────┬──────────────────────┘
                       │
        ┌──────────────▼───────────────┐
        │ Graphics Service             │
        │ (Node.js on port 5555)       │
        │                              │
        │ ┌──────────────────────────┐ │
        │ │ ASCII/Teletext Renderer  │ │
        │ │ (flowchart.js, mermaid)  │ │
        │ └──────────────────────────┘ │
        │                              │
        │ ┌──────────────────────────┐ │
        │ │ SVG Renderer             │ │
        │ │ (with themes)            │ │
        │ └──────────────────────────┘ │
        └──────────────────────────────┘
```

---

## Component Details

### 1. Core (TUI Context)

**File:** [core/services/graphics_service.py](../../core/services/graphics_service.py)

**Purpose:** Python client to Graphics Service

**Methods:**
```python
service = get_graphics_service(host="localhost", port=5555)

# ASCII rendering (TUI)
ascii_text = service.render_ascii(
    template="flowchart/decision",
    data={"labels": ["Start", "Process", "End"]},
    options={"width": 80}
)

# Teletext rendering with colors
teletext = service.render_teletext(
    content="Your flowchart here",
    palette="classic",  # or "bright", "monochrome"
    options={"colors": True}
)

# Health check
service.health_check()  # Returns service status
service.is_available()  # True/False
```

**Error Handling:**
```python
try:
    result = service.render_ascii(...)
except GraphicsServiceError as e:
    # Fallback to local ASCII generation
    from core.services.diagram_generator import DiagramGenerator
    gen = DiagramGenerator()
    result = gen.generate_from_template("simple_flow")
```

**Fallback:** If service unavailable, uses [core/services/diagram_generator.py](../../core/services/diagram_generator.py)

---

### 2. App (SVG Context)

**File:** [app/src/lib/components/DiagramRenderer.svelte](../../app/src/lib/components/DiagramRenderer.svelte)

**Purpose:** Render SVG diagrams in Tauri app

**Usage:**
```svelte
<script>
  import DiagramRenderer from './DiagramRenderer.svelte';
  
  let markdown_source = `
    flowchart TD
      A[Start] --> B[Process]
      B --> C[End]
  `;
</script>

<DiagramRenderer 
  source={markdown_source}
  theme="kinetic"
  width={600}
  height={400}
  on:loaded
  on:error
/>
```

**Props:**
- `source` - Markdown diagram source
- `theme` - Visual theme (technical | kinetic | classic | handwritten)
- `width/height` - Viewport dimensions
- `format` - Auto-detect or specify (flowchart | mermaid | marp)

**Flow:**
1. Component receives markdown source
2. Parses diagram type (flowchart/mermaid/marp)
3. Sends to Graphics Service (via Tauri command)
4. Service returns SVG markup
5. Component renders with theme styling

---

### 3. Graphics Service (Bridge)

**Location:** Node.js service, port 5555  
**Repo:** `extensions/graphics-renderer/` (assumed)

**Endpoints:**

#### POST /render/ascii
```json
{
  "template": "flowchart/simple",
  "data": {"nodes": [...], "edges": [...]},
  "options": {"width": 80}
}
→
{
  "success": true,
  "output": "ASCII diagram here",
  "format": "ascii"
}
```

#### POST /render/teletext
```json
{
  "content": "flowchart source",
  "palette": "classic",
  "options": {"colors": true, "width": 100}
}
→
{
  "success": true,
  "output": "Unicode + ANSI color codes",
  "format": "teletext"
}
```

#### POST /render/svg
```json
{
  "description": "flowchart source",
  "style": "kinetic",
  "options": {"width": 800, "height": 600}
}
→
{
  "success": true,
  "output": "<svg>...</svg>",
  "format": "svg",
  "width": 800,
  "height": 600
}
```

#### POST /render/sequence
```json
{
  "source": "js-sequence-diagram syntax",
  "options": {"theme": "default"}
}
→
{
  "success": true,
  "output": "<svg>...</svg>",
  "format": "svg"
}
```

#### POST /render/flow
```json
{
  "source": "flowchart.js syntax",
  "options": {"lineWidth": 2}
}
→
{
  "success": true,
  "output": "<svg>...</svg>",
  "format": "svg"
}
```

#### GET /templates/{format}
```
/templates/flowchart
→
{
  "success": true,
  "templates": ["simple", "decision-tree", "swimlane", ...]
}
```

#### GET /catalog
```
{
  "success": true,
  "catalog": {
    "ascii": {...},
    "teletext": {...},
    "svg": {...},
    "sequence": {...},
    "flow": {...}
  }
}
```

---

## Data Flow Examples

### Example 1: DIAGRAM SHOW in TUI

```
User Input
  ↓
DIAGRAM SHOW bowline
  ↓
DiagramHandler.handle()
  ↓
Get markdown source from knowledge/knots/bowline.md
  ↓
graphics_service.render_ascii(
    source="<markdown diagram>",
    width=terminal_width
)
  ↓
Graphics Service processes flowchart.js → ASCII
  ↓
Return ASCII art
  ↓
Display in TUI grid
```

**Result:** Text rendering in terminal, no SVG involved

---

### Example 2: View Diagram in App

```
User clicks diagram in knowledge article
  ↓
App loads markdown source
  ↓
DiagramRenderer component detects diagram type
  ↓
Sends to Tauri command → graphics_service.render_svg(
    source="<markdown diagram>",
    style="kinetic"
)
  ↓
Graphics Service → mermaid.js → SVG generation
  ↓
Returns: <svg width="800" height="600">...</svg>
  ↓
Component embeds SVG in DOM
  ↓
Browser renders with CSS styling/theme
  ↓
User sees high-fidelity diagram in app
```

**Result:** Full-featured SVG rendering with themes

---

### Example 3: Generate Diagram from Description

```
User Input
  ↓
DIAGRAM GENERATE shelter/blueprint-guide.md
  ↓
DiagramGenerator reads markdown
  ↓
Extracts inline diagrams and requests
  ↓
For each diagram:
  - Generate flowchart.js source (from description)
  - Render to ASCII via graphics_service.render_ascii()
  - Render to SVG via graphics_service.render_svg()
  ↓
Save results:
  - source.txt (markdown)
  - output.txt (ASCII)
  - output.svg (SVG)
  ↓
Display ASCII in TUI, link SVG in app
```

**Result:** Single source generates multiple formats

---

## Integration Checklist

### Prerequisites
- [ ] Graphics Service running on port 5555
- [ ] Node.js dependencies installed (flowchart.js, mermaid, etc)
- [ ] [core/services/graphics_service.py](../../core/services/graphics_service.py) imported
- [ ] [app/src/lib/components/DiagramRenderer.svelte](../../app/src/lib/components/DiagramRenderer.svelte) available

### Core Integration
- [ ] Import GraphicsService in handlers needing diagrams
- [ ] Add error handling for service unavailable
- [ ] Test ASCII rendering with various widths
- [ ] Verify color support in terminal

### App Integration
- [ ] Import DiagramRenderer in relevant Svelte pages
- [ ] Wire up markdown source extraction
- [ ] Test theme switching
- [ ] Verify SVG embedding in layouts

### Testing
- [ ] Test same source → ASCII ≈ SVG (semantic alignment)
- [ ] Test offline fallback (service disabled)
- [ ] Test large diagrams (performance)
- [ ] Test all 5 formats (ascii, teletext, svg, sequence, flow)
- [ ] Cross-interface: TUI + App consistency

---

## Semantic Alignment (Critical)

**Rule:** Same markdown source MUST produce diagrams that communicate the same meaning

**Examples:**

Source:
```flowchart
graph TD
  A[Input] --> B{Valid?}
  B -->|Yes| C[Process]
  B -->|No| D[Error]
```

**TUI (ASCII):**
- Shows boxes/diamonds/arrows
- Colors: green for success path, red for error
- Text labels must be readable
- Arrows must show flow direction

**App (SVG):**
- Rounded boxes for input/output
- Diamond for decision
- Green arrow for Yes, red for Error
- Same colors, same meaning
- Additional: shadows, gradients for polish

**Key:** User understands the flow equally well in both contexts.

---

## Port Registration

**File:** [extensions/PORT-REGISTRY.md](../../extensions/PORT-REGISTRY.md)

```
## Graphics Service
- **Port:** 5555
- **Protocol:** HTTP
- **Service:** graphics-renderer (Node.js)
- **Realm:** Local device (private)
- **Status:** Required for diagram rendering
- **Fallback:** Offline ASCII generation (core/services/diagram_generator.py)

### Endpoints
- POST /render/ascii
- POST /render/teletext
- POST /render/svg
- POST /render/sequence
- POST /render/flow
- GET /templates/{format}
- GET /catalog

### Dependencies
- flowchart.js
- mermaid.js
- js-sequence-diagrams
- svg generation libraries

### Startup
```bash
cd extensions/graphics-renderer
npm install && npm start
```

### Health Check
```python
from core.services.graphics_service import get_graphics_service
service = get_graphics_service()
print(service.health_check())
```
```

---

## Troubleshooting

### Service Connection Failed
```python
if not service.is_available():
    # Fallback to local generation
    from core.services.diagram_generator import DiagramGenerator
    gen = DiagramGenerator()
    ascii_output = gen.generate_from_description("Create a simple flowchart")
```

### ASCII Doesn't Fit Terminal
```python
ascii_output = service.render_ascii(
    template="...",
    options={
        "width": min(terminal_width - 4, 120)  # Cap at 120
    }
)
```

### SVG Not Rendering in App
- Check console for errors
- Verify SVG markup is valid XML
- Test with simple shape first
- Check theme CSS is loaded

### Colors Not Showing in TUI
```python
# Check if terminal supports colors
import sys
if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
    teletext = service.render_teletext(..., options={"colors": True})
else:
    teletext = service.render_teletext(..., options={"colors": False})
```

---

## Performance Targets

| Scenario | Target | Notes |
|----------|--------|-------|
| ASCII render (simple) | <100ms | Service call + rendering |
| SVG render (medium) | <300ms | Complex layout |
| Large diagram (100+ nodes) | <1s | May need optimization |
| TUI display | <500ms | ASCII + ANSI codes |
| App display | <1s | SVG + CSS + layout |

---

## Related Documentation

- [Graphics Architecture Spec](graphics-architecture.md) - Complete three-tier system
- [FORMAT-ARCHITECTURE.md](../../app/docs/FORMAT-ARCHITECTURE.md) - App markdown formats
- [PORT-REGISTRY.md](../../extensions/PORT-REGISTRY.md) - Port assignments
- [core/services/graphics_service.py](../../core/services/graphics_service.py) - Python client
- [core/services/diagram_generator.py](../../core/services/diagram_generator.py) - Fallback generator

---

**Status:** Ready for integration  
**Owner:** Core + App teams  
**Version:** Alpha v1.0.2.0
