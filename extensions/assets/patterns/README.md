# uDOS Patterns Library

**ASCII and Teletext patterns for backgrounds, borders, and textures**

## Pattern Categories

### Borders & Frames
- **teletext-single** - Single-line box drawing
- **teletext-double** - Double-line box drawing
- **teletext-rounded** - Rounded corners
- **mac-checkerboard** - Classic Mac pattern
- **dos-gradient** - DOS-style gradient

### Backgrounds
- **grid-small** - Small grid pattern (2x2)
- **grid-medium** - Medium grid pattern (4x4)
- **grid-large** - Large grid pattern (8x8)
- **dots-sparse** - Scattered dots
- **dots-dense** - Dense dot pattern

### Textures
- **brick** - Brick wall texture
- **wood-grain** - Wood texture
- **stone** - Stone texture
- **fabric** - Fabric weave
- **metal-mesh** - Metal mesh

## Pattern Format

Patterns are stored as JSON files with the following structure:

```json
{
  "name": "pattern-name",
  "version": "1.0.0",
  "type": "border|background|texture",
  "charset": "ascii|teletext|unicode",
  "dimensions": {
    "width": 80,
    "height": 24
  },
  "data": [
    "line 1 of pattern",
    "line 2 of pattern"
  ],
  "metadata": {
    "author": "uDOS Team",
    "license": "MIT",
    "tags": ["border", "classic", "mac"],
    "description": "Pattern description"
  }
}
```

## Usage

```python
from core.services.asset_manager import get_asset_manager

asset_mgr = get_asset_manager()
pattern = asset_mgr.load_pattern('teletext-single')
if pattern:
    data = pattern.load()
    print(data)
```

## Adding New Patterns

1. Create a `.json` file in this directory
2. Follow the pattern format above
3. Add appropriate metadata (tags, description)
4. Test with AssetManager

## Credits

See `CREDITS.md` for pattern sources and attributions.
