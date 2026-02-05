# SVG Graphics Generation via AI

**Scope:** Generate stylized SVG vector graphics from natural language descriptions  
**Offline:** Local Mistral Small (3.7GB) via Ollama  
**Cloud:** OpenRouter → Claude 3 Opus for high-quality output  
**Use Cases:** Architecture diagrams, flowcharts, line art, UI mockups, documentation illustrations

---

## Architecture

```
User Request (English description)
         │
         ▼
┌─────────────────────────────────────┐
│   AI Graphics Service               │
│   (wizard/services/graphics.py)     │
└──────┬──────────────────────────────┘
       │
       ├──► Ollama (Local) ──► SVG Output
       │    [Fast, Free]
       │
       └──► OpenRouter (Cloud) ──► SVG Output
            [Slower, Better Quality, Paid]
```

---

## Quick Start

### Local SVG Generation (Free)

```python
from wizard.services.graphics_service import SVGGenerator

# Create generator
gen = SVGGenerator()

# Generate diagram
svg = await gen.generate_diagram(
    description="A distributed system with 3 nodes and message flow",
    style="minimalist",  # minimalist | technical | artistic | cartoon
    size="800x600"
)

# Save
with open("diagram.svg", "w") as f:
    f.write(svg)
```

### Cloud SVG Generation (Better Quality, ~$0.02 per image)

```python
svg = await gen.generate_diagram(
    description="A distributed system with 3 nodes and message flow",
    style="minimalist",
    provider="openrouter",  # Force cloud
    model="anthropic/claude-3-opus"
)
```

---

## Supported Styles

### 1. Minimalist

```
Features:
- Black lines only, no fills
- Clean strokes (1-2px)
- Minimal text labels
- High contrast

Best for:
- Technical documentation
- System architecture
- Flow diagrams
```

### 2. Technical

```
Features:
- Precise geometry
- Numbered elements
- Grid reference
- Annotations

Best for:
- Engineering drawings
- Schematic diagrams
- Data structures
```

### 3. Artistic

```
Features:
- Varied line widths
- Organic curves
- Stylized elements
- Color gradients (optional)

Best for:
- Illustrations
- Presentation slides
- Book covers
```

### 4. Cartoon

```
Features:
- Rounded shapes
- Playful expressions
- Speech bubbles
- Comic-style

Best for:
- Educational content
- User guides
- Fun diagrams
```

---

## Usage Examples

### Example 1: Architecture Diagram

**Request:**

```python
description = """
Diagram of uDOS system architecture:
- Core Runtime (TUI) on left
- App (GUI) on top-right
- Wizard Server (center)
- Extensions (bottom)
- Arrows showing data flow

Labels:
- Alpine Linux
- Tauri + Svelte
- FastAPI port 8765
- Transport layer
"""

svg = await gen.generate_diagram(description, style="technical")
```

**Output:**

```xml
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <!-- Core Runtime (left box) -->
  <rect x="50" y="100" width="150" height="200" stroke="black" fill="none"/>
  <text x="75" y="130">Core Runtime</text>
    <text x="60" y="200">Alpine Linux</text>

  <!-- Wizard Server (center) -->
  <circle cx="400" cy="300" r="80" stroke="black" fill="none"/>
  <text x="360" y="310">Wizard</text>
  <text x="350" y="330">Port 8765</text>

  <!-- App (top-right) -->
  <rect x="600" y="50" width="150" height="150" stroke="black" fill="none"/>
  <text x="625" y="85">App (Tauri)</text>
  <text x="610" y="155">Svelte GUI</text>

  <!-- Arrows -->
  <line x1="200" y1="200" x2="320" y2="280" stroke="black"/>
  <polygon points="320,280 310,275 315,290"/>
  <!-- ... more arrows ... -->
</svg>
```

### Example 2: Flowchart

**Request:**

```python
description = """
Flowchart for AI request routing:

START → Is offline?
  ├─ YES → Use local Ollama (end)
  └─ NO → Is "burst" tag?
    ├─ YES → Use OpenRouter (end)
    └─ NO → No AI available (error)
"""

svg = await gen.generate_diagram(description, style="minimalist")
```

### Example 3: Data Structure

**Request:**

```python
description = """
Tree structure for filesystem:
- Root (/)
  - /core (python files)
  - /app (svelte files)
  - /wizard (fastapi files)
  - /extensions (optional)

Use boxes for directories, files inside
"""

svg = await gen.generate_diagram(description, style="technical")
```

---

## Prompt Engineering Tips

### Good Prompts

❌ **Too Vague:**

```
"Draw a graph"
```

✅ **Clear & Specific:**

```
"Create an SVG with:
- 4 boxes (25x100px) labeled A, B, C, D
- Arranged in a 2x2 grid with 20px spacing
- Lines connecting A→B, B→C, C→D
- Black strokes, 2px width, no fills
- Minimalist style
- viewBox='0 0 300 300'"
```

### Critical Keywords

Include these in your prompts:

**Dimensions:**

- "800x600", "viewBox='0 0 800 600'"
- "25px width", "100pt height"

**Style:**

- "minimalist", "black lines only"
- "no fills", "thin strokes"
- "clean", "technical", "artistic"

**Elements:**

- "boxes", "circles", "arrows", "lines"
- "labels", "annotations", "titles"
- "grid", "measurements", "coordinates"

**Output:**

- "Return ONLY the SVG code"
- "No markdown, no explanation"
- "Valid SVG XML"

---

## Integration with uDOS

### Handler Integration

```python
# core/commands/graphics_handler.py
from wizard.services.graphics_service import SVGGenerator

class GraphicsHandler(BaseCommandHandler):
    def handle(self, command, params, grid, parser):
        if command == "DIAGRAM":
            return self._handle_diagram(params)
        elif command == "CHART":
            return self._handle_chart(params)

    async def _handle_diagram(self, params):
        """DIAGRAM <description>"""
        gen = SVGGenerator()
        description = " ".join(params)

        svg = await gen.generate_diagram(
            description=description,
            style=params.get("--style", "minimalist"),
            size=params.get("--size", "800x600")
        )

        # Save to ucode/generated_diagrams/
        path = save_svg(svg)
        return f"✓ Diagram saved: {path}"
```

### TUI Command Usage

```bash
uDOS> DIAGRAM A system with 3 nodes (A, B, C) and message flow between them
✓ Diagram saved: memory/ucode/diagram-2026-01-17-001.svg

uDOS> DIAGRAM --style=technical --size=1024x768 Filesystem hierarchy with /core, /app, /wizard
✓ Diagram saved: memory/ucode/diagram-2026-01-17-002.svg
```

### Markdown Integration

**In uCode documents:**

```markdown
---
title: "System Architecture"
---

## Architecture Diagram

!DIAGRAM
A distributed system with:

- 3 nodes (A, B, C)
- Gossip protocol arrows
- Consensus mechanism

Style: technical
Size: 800x600
!DIAGRAM
```

---

## Quality Optimization

### Local Model (Mistral Small)

**Best for:**

- Simple diagrams (boxes, arrows, text)
- System overviews
- Quick iterations

**Tips:**

- Keep descriptions short & specific
- Use simple geometric shapes
- Avoid complex styling
- Focus on structure, not aesthetics

**Performance:**

```
Size: ~1KB → Output: ~5KB SVG
Speed: ~100ms latency
Cost: $0
```

### Cloud Model (Claude 3 Opus)

**Best for:**

- Complex styling & gradients
- Artistic illustrations
- Precise technical specs
- High-quality output

**Tips:**

- Include detailed styling instructions
- Request specific colors/fonts
- Ask for multiple variations
- Optimize for print/web

**Performance:**

```
Size: ~1KB → Output: ~10KB SVG
Speed: ~3-4s latency
Cost: ~$0.02 per request
```

---

## SVG Validation

```python
# Validate generated SVG
import xml.etree.ElementTree as ET

def validate_svg(svg_string: str) -> bool:
    try:
        ET.fromstring(svg_string)
        return True
    except ET.ParseError as e:
        print(f"Invalid SVG: {e}")
        return False

# Use in service
svg = await gen.generate_diagram(description)
if not validate_svg(svg):
    # Fallback to Graphviz or cached template
    svg = fallback_diagram()
```

---

## Caching & Performance

### Cache Generated Diagrams

```python
# wizard/services/graphics_cache.py
import hashlib
from pathlib import Path

CACHE_DIR = Path("memory/wizard/svg_cache")

def cache_svg(description: str, svg: str) -> str:
    """Cache SVG by content hash"""
    key = hashlib.md5(description.encode()).hexdigest()
    path = CACHE_DIR / f"{key}.svg"

    if path.exists():
        return path.read_text()  # Return cached

    path.write_text(svg)
    return svg
```

### Batch Generation

```python
# Generate multiple diagrams efficiently
descriptions = [
    "Node architecture diagram",
    "Message flow diagram",
    "Data structure tree"
]

svgs = await gen.generate_batch(
    descriptions=descriptions,
    style="minimalist",
    parallel=3  # Generate 3 in parallel
)
```

---

## Troubleshooting

### Issue: "Invalid SVG output"

**Solution:** Validate with stricter prompt:

```python
prompt = """Generate a valid SVG diagram:
- Valid XML syntax
- Proper namespaces
- Closed tags only
- Return ONLY <svg>...</svg>"""
```

### Issue: "Too slow (waiting for cloud)"

**Solution:** Use local model first:

```python
svg = await gen.generate_diagram(
    description,
    provider="ollama",  # Force local
    timeout=2.0
)
```

### Issue: "Model refuses (safety filter)"

**Solution:** Rephrase non-controversial description:

```
# ❌ Bad (flagged):
"Show how to hack a system"

# ✅ Good (accepted):
"Show common attack vectors in security architecture diagram"
```

---

## Examples Gallery

### Example Diagrams

1. **Distributed System**

   ```
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ Node A  │◄──►│ Node B  │◄──►│ Node C  │
   │ Port 80 │    │ Port 81 │    │ Port 82 │
   └─────────┘    └─────────┘    └─────────┘
        ▲              ▲              ▲
        └──────────────┴──────────────┘
            Gossip Protocol
   ```

2. **Command Routing**

   ```
   User Input
      │
      ▼
   SmartPrompt
      │
      ▼
   Parser ◄──┐
      │      │
      ├──────► Specialized Handler
      │
      ▼
   Shared Services
   ```

3. **AI Routing**
   ```
   Request
      │
      ├─ Offline? ────► Ollama ──► Result
      │      (yes)
      │
      ├─ Budget? ────► OpenRouter ──► Result
      │      (yes)
      │
      └─ Error (no AI available)
   ```

---

## Future Enhancements

- [ ] SVG template library (premade diagrams)
- [ ] Interactive diagram editor (edit + regenerate)
- [ ] Export to PDF/PNG (via headless browser)
- [ ] Animation generation (CSS + SVG animate)
- [ ] Batch import (CSV → diagram)

---

## See Also

- [Ollama + OpenRouter Setup](OFFLINE-AI-SETUP.md)
- [AI Gateway Architecture](../../wizard/services/ai_gateway.py)
- [Graphics Service Implementation](../../wizard/services/graphics_service.py)

---

_Last Updated: 2026-01-17_  
_v1.0.4.0 SVG Graphics Complete_
