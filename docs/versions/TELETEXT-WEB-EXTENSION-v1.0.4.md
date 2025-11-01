# 🖥️ uDOS v1.0.4 - Teletext Web Extension

## Overview

The uDOS Teletext Web Extension brings retro teletext-style visualization to the integrated mapping system, combining the aesthetic of 1980s teletext with modern web technologies. Inspired by [galax.xyz/TELETEXT/](https://galax.xyz/TELETEXT/) and built on the teletext mono starter framework.

## Features

### 🎨 Visual Features
- **Mosaic Block Art**: 2×3 pixel block characters (64 combinations)
- **WST Color Palette**: Classic teletext colors (8 colors)
- **Contiguous/Separated Modes**: Toggle between mosaic styles
- **Interactive Scaling**: 1×, 2×, 3×, 4× zoom levels
- **Flashing Elements**: Animated current position markers
- **Responsive Design**: Mobile and desktop optimized

### 🗺️ Mapping Integration
- **Real-time Map Generation**: Convert ASCII maps to teletext
- **Cell Reference Display**: APAC grid integration
- **TIZO Location Support**: Global city positioning
- **Multi-layer Visualization**: Different map layers
- **Navigation Controls**: Interactive map movement

### 🌐 Web Interface
- **Standalone Web Server**: HTTP server for teletext maps
- **Interactive Controls**: Live map manipulation
- **Export Functionality**: Save maps as HTML files
- **Mobile Responsive**: Touch-friendly navigation
- **Real-time Updates**: Dynamic map refreshing

## Components

### Core Renderer
**File**: `core/services/teletext_renderer.py`
**Class**: `TeletextMosaicRenderer`

```python
from core.services.teletext_renderer import TeletextMosaicRenderer

renderer = TeletextMosaicRenderer()
html_output = renderer.generate_map_html(map_data, "Map Title", 40, 24)
```

### Map Integration
**File**: `core/services/teletext_renderer.py`
**Class**: `TeletextMapIntegration`

```python
from core.services.teletext_renderer import TeletextMapIntegration

integration = TeletextMapIntegration()
html_content = integration.render_map_as_teletext(map_engine, "JN196", 40, 20)
filepath = integration.save_teletext_map(html_content)
```

### Web Extension
**File**: `extensions/web/teletext_extension.py`
**Class**: `TeletextWebExtension`

```python
from extensions.web.teletext_extension import TeletextWebExtension

extension = TeletextWebExtension(port=8080)
server_url = extension.start_server()
```

## MAP Command Integration

### New Commands

#### `MAP TELETEXT [width] [height]`
Generate teletext-style map:
```bash
MAP TELETEXT           # Default 40×20 map
MAP TELETEXT 60 30     # Large 60×30 map
MAP TELETEXT 25 12     # Compact mobile map
```

Output:
```
🖥️  Teletext Map Generated
===================================
Location: Melbourne, Australia
Cell: JN196
Size: 40×20 characters
Style: Mosaic block art

📄 File saved: output/teletext/udos_teletext_map_20251102_031935.html
🌐 Open in web browser to view
💡 Use MAP WEB to start local server
```

#### `MAP WEB [server]`
Open teletext maps in browser:
```bash
MAP WEB               # Open latest map file
MAP WEB SERVER        # Start HTTP server
```

Server mode output:
```
🚀 Teletext Web Server Started
==============================
Server URL: http://localhost:8080
Port: 8080
Directory: /path/to/output/teletext

🌐 Browser should open automatically
📁 All teletext maps available at server root
🛑 Press Ctrl+C in terminal to stop server
```

## Teletext Character System

### Mosaic Characters
The system uses Unicode Private Use Area (E200-E3FF) for mosaic characters:

| Pattern | Code | Description |
|---------|------|-------------|
| `000000` | `&#xE200;` | Empty block |
| `111111` | `&#xE23F;` | Full block |
| `110000` | `&#xE203;` | Top half |
| `001100` | `&#xE20C;` | Bottom half |
| `101010` | `&#xE215;` | Left half |
| `010101` | `&#xE22A;` | Right half |

### Color Mapping
Character types mapped to teletext colors:

| Symbol | Type | Color | Animation |
|--------|------|-------|-----------|
| `◉` | Current Position | Yellow | Flashing |
| `M` | MEGA City | Red | Static |
| `C` | MAJOR City | Green | Static |
| `•` | Minor Settlement | Cyan | Static |
| `~` | Water/Ocean | Blue | Pattern |
| `.` | Land/Terrain | Green | Pattern |

### Pattern Generation
- **Water**: Animated wave patterns using position-based algorithms
- **Terrain**: Randomized mosaic patterns for natural appearance
- **Cities**: Distinct block patterns based on population size
- **Position**: Flashing full block with yellow color

## Web Interface

### Interactive Features

#### Map Controls
- **Location Selector**: Choose from TIZO cities
- **Size Options**: Standard, Large, Extra Large, Compact
- **Scale Controls**: 1×, 2×, 3×, 4× zoom
- **Mode Toggle**: Contiguous/Separated mosaics
- **Export Function**: Save as standalone HTML

#### Navigation
- **Directional Pad**: 8-way navigation control
- **Auto-refresh**: Optional periodic map updates
- **Real-time Status**: Connection and loading indicators

#### Mobile Support
- **Touch Navigation**: Gesture-based map control
- **Responsive Layout**: Adaptive to screen sizes
- **Performance Optimized**: Efficient rendering

### File Structure
```
extensions/web/teletext/
├── index.html              # Main web interface
├── teletext-web.css        # Enhanced teletext styling
├── teletext-api.js         # Interactive JavaScript API
├── fonts/                  # Teletext font files
└── mosaic_codepoints_E200-E3FF.csv
```

## Installation & Setup

### 1. Copy Teletext Assets
```bash
# Copy from teletext mono starter
cp -r examples/teletext_mono_starter/fonts extensions/web/teletext/
cp examples/teletext_mono_starter/mosaic_codepoints_E200-E3FF.csv extensions/web/teletext/
```

### 2. Generate Web Interface
```python
from extensions.web.teletext_extension import TeletextWebExtension

extension = TeletextWebExtension()
extension.setup_web_files()
```

### 3. Start Web Server
```bash
# Method 1: Through MAP commands
MAP WEB SERVER

# Method 2: Direct execution
python3 extensions/web/teletext_extension.py

# Method 3: Programmatic
from extensions.web.teletext_extension import TeletextWebExtension
extension = TeletextWebExtension(port=8080)
server_url = extension.start_server()
```

## Usage Examples

### Basic Map Generation
```python
from core.commands.map_handler import MapCommandHandler

handler = MapCommandHandler()
result = handler.handle("TELETEXT", "40 20", None)
print(result)
```

### Custom Map Rendering
```python
from core.services.teletext_renderer import TeletextMosaicRenderer

renderer = TeletextMosaicRenderer()
map_data = [
    "~..~..~..~..~",
    ".     ◉     .",
    "~           ~",
    ".           .",
    "~..~..~..~..~"
]

html = renderer.generate_map_html(map_data, "Custom Map", 15, 5)
```

### Web Extension Server
```python
from extensions.web.teletext_extension import TeletextWebExtension

# Start server with custom port
extension = TeletextWebExtension(port=8081)
server_url = extension.start_server(open_browser=True)

print(f"Server running at: {server_url}")

# Keep running until interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    extension.stop_server()
```

## Technical Implementation

### Mosaic Rendering Algorithm
```python
def _char_to_teletext_cell(self, char: str, row: int, col: int) -> str:
    """Convert ASCII character to teletext mosaic."""

    # Determine character type and color
    if char == '◉':  # Current position
        color_class = "tt-fg-yel tt-flash"
        mosaic_pattern = self.MOSAIC_CHARS['FULL'][1]
    elif char == '~':  # Water
        color_class = "tt-fg-blu"
        # Generate wave pattern based on position
        wave_pattern = (col + row) % 4
        mosaic_pattern = wave_patterns[wave_pattern]
    # ... etc

    return f'<span class="cell {color_class} tt-con">{mosaic_pattern}</span>'
```

### CSS Grid System
```css
.teletext {
    --cols: 40;
    --rows: 24;
    --cell: 1ch;
    --lhpx: 16px;
    display: grid;
    grid-template-columns: repeat(var(--cols), var(--cell));
    grid-auto-rows: var(--lhpx);
    font-family: "TT-Mosaic", monospace;
}
```

### WebSocket Integration (Future)
```javascript
// Planned for real-time updates
class TeletextWebSocket {
    constructor(url) {
        this.ws = new WebSocket(url);
        this.ws.onmessage = this.handleMapUpdate.bind(this);
    }

    handleMapUpdate(event) {
        const mapData = JSON.parse(event.data);
        this.updateTeletextGrid(mapData);
    }
}
```

## Performance Considerations

### Optimization Strategies
- **Lazy Loading**: Web extension components loaded on demand
- **Efficient Rendering**: Minimal DOM manipulation
- **Caching**: Generated maps cached for reuse
- **Compression**: Optimized HTML/CSS output
- **Memory Management**: Cleanup of unused resources

### Browser Compatibility
- **Modern Browsers**: Full feature support
- **Mobile Browsers**: Touch-optimized interface
- **Legacy Support**: Graceful degradation
- **Font Fallbacks**: Monospace alternatives when teletext font unavailable

## Integration with uDOS Core

### Command Routing
```python
# In core/commands/map_handler.py
elif command == "TELETEXT":
    return self._handle_teletext(params)
elif command == "WEB":
    return self._handle_web(params)
```

### Configuration Integration
```json
{
  "extensions": {
    "teletext": {
      "enabled": true,
      "default_size": [40, 20],
      "web_port": 8080,
      "auto_open_browser": true
    }
  }
}
```

### File Organization
```
output/teletext/                    # Generated teletext maps
extensions/web/teletext/            # Web interface files
core/services/teletext_renderer.py  # Core rendering engine
tests/test_teletext_integration.py  # Test suite
```

## Future Enhancements

### Planned Features (v1.0.5+)
- [ ] **Real-time Updates**: WebSocket-based live map updates
- [ ] **Interactive Editing**: Click-to-modify map elements
- [ ] **Animation System**: Smooth transitions between map states
- [ ] **Sound Integration**: Retro teletext sound effects
- [ ] **Multi-user Support**: Collaborative map viewing
- [ ] **API Extensions**: RESTful API for external integrations

### Advanced Visualization
- [ ] **3D Layering**: Depth-based mosaic rendering
- [ ] **Weather Overlay**: Environmental data visualization
- [ ] **Time-based Changes**: Dynamic map evolution
- [ ] **Custom Palettes**: User-defined color schemes
- [ ] **High-res Mode**: Sub-character precision

### Performance Improvements
- [ ] **GPU Acceleration**: Hardware-accelerated rendering
- [ ] **Progressive Loading**: Chunked map delivery
- [ ] **Compression**: Better output optimization
- [ ] **Caching**: Intelligent map caching system

## Troubleshooting

### Common Issues

#### Font Not Loading
```
⚠️ If teletext characters appear as boxes:
1. Ensure fonts/ directory exists in web root
2. Copy from examples/teletext_mono_starter/fonts/
3. Check browser console for font loading errors
```

#### Server Won't Start
```
⚠️ If web server fails to start:
1. Check if port is already in use
2. Try different port: TeletextWebExtension(port=8081)
3. Ensure write permissions for web directory
```

#### Maps Not Generating
```
⚠️ If MAP TELETEXT fails:
1. Check user configuration exists (sandbox/user.json)
2. Verify TIZO location data available
3. Ensure output/teletext directory writable
```

---

## 🎉 Ready for Use!

The uDOS Teletext Web Extension is fully integrated and ready for retro-style map visualization. The system provides:

- ✅ **Complete MAP command integration** (TELETEXT, WEB)
- ✅ **Standalone web server** with interactive interface
- ✅ **Mobile-responsive design** for all devices
- ✅ **Export functionality** for offline viewing
- ✅ **Real-time map generation** from ASCII data
- ✅ **Authentic teletext aesthetics** with modern UX

Experience the nostalgia of 1980s teletext combined with the power of modern mapping technology! 🖥️✨

---

*uDOS v1.0.4 - Teletext Web Extension Documentation*
*Integration Complete: November 2, 2025*
