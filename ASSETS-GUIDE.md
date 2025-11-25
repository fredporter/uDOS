# uDOS Assets System Guide (v1.5.3+)

**Comprehensive guide to the uDOS asset management system**

## Table of Contents

1. [Overview](#overview)
2. [Asset Types](#asset-types)
3. [Using the ASSETS Command](#using-the-assets-command)
4. [Programming with AssetManager](#programming-with-assetmanager)
5. [Creating New Assets](#creating-new-assets)
6. [Pattern Format Specification](#pattern-format-specification)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The uDOS Asset Management System provides centralized access to shared resources across all extensions. Assets are automatically discovered, cataloged, and made available through both command-line and programmatic interfaces.

### Key Features

- **Automatic Discovery**: Assets are scanned from `extensions/assets/` on startup
- **Multiple Types**: Supports fonts, icons, patterns, CSS, and JavaScript
- **Smart Caching**: Loaded assets are cached in memory for performance
- **Hot Reload**: Update assets without restarting uDOS
- **Search & Filter**: Regex-powered search across names and metadata
- **Metadata Support**: Companion `.meta.json` files for rich metadata

### Directory Structure

```
extensions/assets/
├── fonts/          # Font files (WOFF2, TTF, WOFF)
├── icons/          # Icon sets (SVG, PNG)
├── patterns/       # Pattern library (JSON)
├── css/            # Shared CSS frameworks
├── js/             # Shared JavaScript libraries
└── README.md       # Asset library documentation
```

---

## Asset Types

### Fonts

Located in `extensions/assets/fonts/`

**Available Fonts**:
- **chicago** - Classic Macintosh System 6 font (multiple formats)
- **monaco** - Monospace terminal font
- **C64_User_Mono** - Commodore 64 style
- **giana** - Retro gaming style
- **FindersKeepers** (Geneva_9) - Small text font

**Formats**: WOFF2 (primary), WOFF (fallback), TTF

**Usage Example**:
```python
from core.services.asset_manager import get_asset_manager

mgr = get_asset_manager()
font = mgr.load_font('chicago', format='woff2')
if font:
    font_data = font.load()
```

### Icons

Located in `extensions/assets/icons/`

**Collections**:
- **System Icons**: Classic Mac System 6 UI elements (buttons, checkboxes, etc.)
- **CoreUI Icons**: 1500+ icons (free, brand, flag sets)
- **Survival Icons**: Water, fire, shelter, food, navigation, medical (coming soon)

**Formats**: SVG (primary), PNG (bitmap)

**Usage Example**:
```python
icon = mgr.load_icon('water-drop', format='svg')
if icon:
    svg_content = icon.load()
```

### Patterns

Located in `extensions/assets/patterns/`

**22 Built-in Patterns**:

#### Borders (7 patterns)
- `teletext-single` - Single-line box drawing
- `teletext-double` - Double-line box drawing
- `teletext-rounded` - Rounded corners
- `ascii-simple` - Classic ASCII border (+, -, |)
- `ascii-double` - Bold ASCII border (#, =)
- `ascii-stars` - Decorative star border (*)
- `block-thick` - Thick solid block border (█)
- `block-thin` - Thin block border (▄, ▀, ▐)

#### Backgrounds (8 patterns)
- `mac-checkerboard` - Classic Mac checkerboard (8x8)
- `grid-small` - Small 2x2 grid
- `grid-medium` - Medium 4x4 grid
- `grid-large` - Large 8x8 grid
- `dos-gradient` - DOS-style gradient
- `dots-sparse` - Scattered dots
- `dots-dense` - Dense dot pattern
- `crosshatch` - Diagonal crosshatch
- `waves` - Flowing wave pattern

#### Textures (5 patterns)
- `brick` - Brick wall texture
- `wood-grain` - Wood grain texture
- `stone` - Stone/rock texture
- `fabric` - Fabric weave texture
- `metal-mesh` - Metal mesh texture

**Usage Example**:
```python
pattern = mgr.load_pattern('teletext-single')
if pattern:
    pattern_data = pattern.load()
    components = pattern_data['components']
    # Use components['top_left'], components['horizontal'], etc.
```

### CSS & JavaScript

- **CSS**: Shared frameworks (system.css, synthwave-dos-colors.css, etc.)
- **JavaScript**: UI components (controls, panels, file picker, etc.)

---

## Using the ASSETS Command

### Basic Commands

#### List All Assets
```
ASSETS LIST
```
Shows all available assets grouped by type.

#### List by Type
```
ASSETS LIST fonts
ASSETS LIST icons
ASSETS LIST patterns
ASSETS LIST css
ASSETS LIST js
```

#### Search Assets
```
ASSETS SEARCH water
ASSETS SEARCH teletext
ASSETS SEARCH chi.*go        # Regex: matches 'chicago'
```

#### View Asset Info
```
ASSETS INFO teletext-single
ASSETS INFO chicago
```

Shows detailed information including:
- Type and version
- File path and size
- Metadata (author, license, tags, description)
- Load status

#### Preview Asset
```
ASSETS PREVIEW mac-checkerboard
ASSETS PREVIEW teletext-double
```

Shows asset contents:
- Patterns: Display example or pattern array
- Text files: First 50 lines
- JSON: Pretty-printed structure

#### Load Asset
```
ASSETS LOAD chicago
ASSETS LOAD water-drop
```

Loads asset into memory cache for faster access.

#### View Statistics
```
ASSETS STATS
```

Shows:
- Total assets count
- Assets by type
- Total size (MB)
- Loaded assets count
- Assets root path

#### Hot Reload
```
ASSETS RELOAD pattern-name
```

Reloads an asset from disk, updating the cached copy.

### Command Examples

```bash
# Find all water-related icons
ASSETS SEARCH water

# Preview a border pattern
ASSETS PREVIEW teletext-single

# Load chicago font
ASSETS LOAD chicago

# Get detailed font info
ASSETS INFO fonts/chicago

# Show asset statistics
ASSETS STATS
```

---

## Programming with AssetManager

### Basic Usage

```python
from core.services.asset_manager import get_asset_manager

# Get global instance
mgr = get_asset_manager()

# Load a font
font = mgr.load_font('chicago', format='woff2')
if font:
    font_data = font.load()  # Binary data
    print(f"Font size: {len(font_data)} bytes")

# Load an icon
icon = mgr.load_icon('water-drop', format='svg')
if icon:
    svg_content = icon.load()  # String (SVG XML)
    print(svg_content)

# Load a pattern
pattern = mgr.load_pattern('teletext-single')
if pattern:
    data = pattern.load()  # Dict (parsed JSON)
    print(f"Components: {data['components']}")
```

### Advanced Features

#### List and Filter
```python
# List all fonts
fonts = mgr.list_assets('fonts')
print(f"Available fonts: {len(fonts)}")

# Search with regex
results = mgr.search_assets(r'tele.*', asset_type='patterns')
for name, asset in results:
    print(f"Found: {name}")
```

#### Asset Information
```python
# Get detailed info
info = mgr.get_asset_info('patterns/teletext-single')
print(f"Type: {info['type']}")
print(f"Size: {info['size']} bytes")
print(f"Tags: {info['metadata']['tags']}")
```

#### Hot Reload
```python
# Reload asset from disk
success = mgr.reload_asset('patterns/custom-pattern')
if success:
    print("Pattern reloaded successfully")
```

#### Statistics
```python
stats = mgr.get_stats()
print(f"Total assets: {stats['total_assets']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"By type: {stats['by_type']}")
```

### Caching Behavior

Assets are cached after first load:

```python
# First load: reads from disk
pattern = mgr.load_pattern('grid-small')
data1 = pattern.load()  # Disk read

# Second load: uses cache
data2 = pattern.load()  # Cache hit

# Force reload from disk
data3 = pattern.reload()  # Disk read
```

---

## Creating New Assets

### Creating a Pattern

1. **Create JSON file** in `extensions/assets/patterns/`

```json
{
  "name": "my-pattern",
  "version": "1.0.0",
  "type": "border",
  "charset": "ascii",
  "dimensions": {
    "width": 80,
    "height": 24
  },
  "components": {
    "top_left": "+",
    "top_right": "+",
    "bottom_left": "+",
    "bottom_right": "+",
    "horizontal": "-",
    "vertical": "|"
  },
  "example": [
    "+-----------------+",
    "|                 |",
    "|     Content     |",
    "|                 |",
    "+-----------------+"
  ],
  "metadata": {
    "author": "Your Name",
    "license": "MIT",
    "tags": ["border", "custom"],
    "description": "My custom border pattern"
  }
}
```

2. **Test with ASSETS command**:
```
ASSETS LIST patterns
ASSETS PREVIEW my-pattern
```

3. **Use in code**:
```python
pattern = mgr.load_pattern('my-pattern')
data = pattern.load()
```

### Adding Metadata

Create a companion `.meta.json` file:

**File**: `chicago.woff2.meta.json`
```json
{
  "author": "Susan Kare",
  "license": "MIT",
  "year": 1984,
  "tags": ["mac", "system", "retro", "bitmap"],
  "description": "Classic Macintosh System 6 font",
  "variants": ["chicago_12", "chicago_14"]
}
```

The metadata is automatically loaded and merged with asset info.

---

## Pattern Format Specification

### Border Patterns

**Required Fields**:
- `name`: Unique identifier
- `version`: Semantic version (e.g., "1.0.0")
- `type`: "border"
- `charset`: "ascii" | "teletext" | "unicode"
- `components`: Object with border characters
- `metadata`: Author, license, tags, description

**Components Object**:
```json
{
  "top_left": "┌",
  "top_right": "┐",
  "bottom_left": "└",
  "bottom_right": "┘",
  "horizontal": "─",
  "vertical": "│",
  "t_down": "┬",      // Optional
  "t_up": "┴",        // Optional
  "t_right": "├",     // Optional
  "t_left": "┤",      // Optional
  "cross": "┼"        // Optional
}
```

### Background/Texture Patterns

**Required Fields**:
- `name`: Unique identifier
- `version`: Semantic version
- `type`: "background" | "texture"
- `charset`: Character set
- `pattern`: Array of strings (pattern lines)
- `metadata`: Author info

**Pattern Array**:
```json
{
  "pattern": [
    "░▒░▒░▒░▒",
    "▒░▒░▒░▒░",
    "░▒░▒░▒░▒",
    "▒░▒░▒░▒░"
  ]
}
```

The pattern repeats/tiles to fill the desired area.

---

## Best Practices

### Asset Organization

✅ **DO**:
- Use descriptive names (`teletext-rounded`, not `border1`)
- Include version in metadata
- Tag assets appropriately for searchability
- Provide clear descriptions
- Use consistent naming conventions

❌ **DON'T**:
- Create duplicate assets with different names
- Mix character sets in a single pattern
- Use generic names without context

### Performance

✅ **DO**:
- Use `load_font()`, `load_icon()`, etc. for type-specific loading
- Leverage caching for frequently-used assets
- Reload only when assets actually change

❌ **DON'T**:
- Call `load()` repeatedly in loops
- Reload assets unnecessarily
- Load all assets upfront (lazy loading is better)

### Extension Development

When building extensions:

```python
from core.services.asset_manager import get_asset_manager

class MyExtension:
    def __init__(self):
        self.assets = get_asset_manager()

    def render_border(self):
        pattern = self.assets.load_pattern('teletext-single')
        if pattern:
            data = pattern.load()
            return self._build_border(data['components'])
        return None
```

---

## Troubleshooting

### Asset Not Found

**Symptom**: `load_font()` returns `None`

**Solutions**:
1. Verify asset exists: `ASSETS LIST fonts`
2. Check exact name (case-sensitive)
3. Ensure file is in correct directory
4. Restart to rebuild catalog

### Pattern Not Loading

**Symptom**: JSON parse error

**Solutions**:
1. Validate JSON syntax: `ASSETS PREVIEW pattern-name`
2. Check required fields are present
3. Ensure proper escaping in strings
4. Verify file encoding is UTF-8

### Metadata Not Showing

**Symptom**: Asset has no metadata

**Solutions**:
1. Check companion file name matches exactly
2. Verify `.meta.json` is valid JSON
3. Ensure file is in same directory as asset
4. Reload asset: `ASSETS RELOAD asset-name`

### Performance Issues

**Symptom**: Slow asset loading

**Solutions**:
1. Use caching (assets auto-cache after first load)
2. Check asset file size: `ASSETS INFO asset-name`
3. Consider lazy loading for large collections
4. Use `ASSETS STATS` to check memory usage

---

## API Reference

### AssetManager Methods

```python
# Loading
load_font(name: str, format: str = 'woff2') -> Optional[Asset]
load_icon(name: str, format: str = 'svg') -> Optional[Asset]
load_pattern(name: str) -> Optional[Asset]
load_css(name: str) -> Optional[Asset]
load_js(name: str) -> Optional[Asset]

# Discovery
list_assets(asset_type: Optional[str] = None) -> List[str]
search_assets(query: str, asset_type: Optional[str] = None) -> List[Tuple[str, Asset]]

# Information
get_asset_info(name: str) -> Optional[Dict[str, Any]]
get_stats() -> Dict[str, Any]

# Management
reload_asset(name: str) -> bool
```

### Asset Methods

```python
# Data access
load() -> Any                    # Load and cache
reload() -> Any                  # Force reload from disk
get_info() -> Dict[str, Any]     # Get asset information

# Properties
asset.name: str                  # Asset name
asset.type: str                  # Asset type
asset.path: Path                 # File path
asset.version: str               # Version
asset.metadata: Dict             # Metadata
asset.loaded_at: datetime        # Load timestamp
```

---

## Examples

### Border Drawing

```python
def draw_border(width: int, height: int, pattern_name: str = 'teletext-single'):
    """Draw a border using a pattern."""
    mgr = get_asset_manager()
    pattern = mgr.load_pattern(pattern_name)

    if not pattern:
        return None

    data = pattern.load()
    c = data['components']

    lines = []
    lines.append(c['top_left'] + c['horizontal'] * (width - 2) + c['top_right'])

    for _ in range(height - 2):
        lines.append(c['vertical'] + ' ' * (width - 2) + c['vertical'])

    lines.append(c['bottom_left'] + c['horizontal'] * (width - 2) + c['bottom_right'])

    return '\n'.join(lines)

# Usage
print(draw_border(40, 10, 'teletext-double'))
```

### Background Tiling

```python
def tile_background(width: int, height: int, pattern_name: str):
    """Tile a background pattern to fill area."""
    mgr = get_asset_manager()
    pattern = mgr.load_pattern(pattern_name)

    if not pattern:
        return None

    data = pattern.load()
    pattern_lines = data['pattern']
    pattern_height = len(pattern_lines)
    pattern_width = len(pattern_lines[0])

    output = []
    for y in range(height):
        line = ''
        pattern_line = pattern_lines[y % pattern_height]
        for x in range(0, width, pattern_width):
            line += pattern_line[:width - x]
        output.append(line)

    return '\n'.join(output)

# Usage
print(tile_background(80, 24, 'dots-sparse'))
```

---

## Version History

- **v1.5.3** (2025-11-25) - Initial release
  - AssetManager service with auto-discovery
  - ASSETS command suite
  - 22 built-in patterns
  - Comprehensive test coverage (22 tests)

---

## Contributing

To contribute new assets:

1. Create asset file(s) in appropriate directory
2. Follow format specifications
3. Include metadata
4. Test with `ASSETS` commands
5. Submit pull request with description

For questions or issues:
- GitHub Issues: https://github.com/fredporter/uDOS/issues
- Wiki: https://github.com/fredporter/uDOS/wiki

---

**Next**: See [Pattern Gallery](PATTERN-GALLERY.md) for visual examples of all patterns.
