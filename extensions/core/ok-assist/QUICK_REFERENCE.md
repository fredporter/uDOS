# OK Assist Quick Reference

## Three Formats, One System

```python
from extensions.core.ok_assist.api.gemini import OKAssist
ok = OKAssist()  # Loads GEMINI_API_KEY from .env
```

## Generate ASCII Art

**Terminal/CLI diagrams using C64 PetMe character set**

```python
ascii_art = ok.generate_ascii(
    subject="water filter",
    description="Multi-layer gravel/sand/charcoal",
    width=80,      # Characters wide
    height=24,     # Lines tall
    style="petme"  # C64 character set
)
# Output: .txt file for terminal
```

**Characters**: `┌─┐│└┘█▓▒░▀▄▌▐♥★→←⚠✓`

## Generate Teletext Graphics

**Colorful web graphics using mosaic blocks**

```python
teletext_html = ok.generate_teletext(
    subject="forest map",
    description="Trees, water, elevation",
    width=40,      # Teletext columns
    height=25,     # Teletext rows
    colors=["GREEN", "BLUE", "BROWN"],  # WST palette
    style="mosaic" # Block mode
)
# Output: .html file for web
```

**Colors**: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE

## Generate SVG Diagrams

**Scalable vector graphics in two styles**

### Technical-Kinetic (Tools, Systems)
```python
svg_tech = ok.generate_svg(
    subject="bow saw",
    style="technical-kinetic",
    description="Frame, blade, tension",
    complexity="moderate"  # simple|moderate|detailed|complex
)
# Output: .svg with CoreUI icons + Mac patterns
```

### Hand-Illustrative (Anatomy, Nature)
```python
svg_organic = ok.generate_svg(
    subject="oak leaf",
    style="hand-illustrative",
    description="Veins, petiole, blade",
    complexity="detailed"
)
# Output: .svg with engraving aesthetic
```

## Auto-Style Detection

```python
# Automatically chooses best style
svg = ok.generate(
    subject="human heart",   # → hand-illustrative
    format="svg"
)

svg = ok.generate(
    subject="water pump",    # → technical-kinetic
    format="svg"
)
```

## Generate All Formats

**One subject → all four variations**

```python
all_formats = ok.generate_all_formats(
    subject="campfire structure",
    description="Log cabin fire lay"
)

# Returns dict:
all_formats["ascii"]          # → .txt (80×24 terminal)
all_formats["teletext"]       # → .html (40×25 web)
all_formats["svg_technical"]  # → .svg (geometric)
all_formats["svg_organic"]    # → .svg (hand-drawn)
```

## Asset Mappings

### Icons
```python
from extensions.core.ok_assist.assets.design_assets import DesignAssets

icon = DesignAssets.get_icon("tool", "ascii")     # → ⚒
icon = DesignAssets.get_icon("tool", "teletext")  # → &#xE23F;
icon = DesignAssets.get_icon("tool", "svg")       # → cil-wrench
```

### Patterns
```python
pattern = DesignAssets.get_pattern("metal", "ascii")      # → ▓▓▓▓
pattern = DesignAssets.get_pattern("metal", "svg_tech")   # → crosshatch
pattern = DesignAssets.get_pattern("metal", "svg_organic") # → parallel-lines
```

### Conversions
```python
# ASCII → Teletext
teletext = DesignAssets.ascii_to_teletext("█")  # → &#xE23F;

# Color → Greyscale
grey = DesignAssets.color_to_greyscale("RED")   # → #555555
```

## Command Line

```bash
# ASCII
python -m extensions.core.ok_assist.api.gemini "fire triangle" ascii petme

# Teletext
python -m extensions.core.ok_assist.api.gemini "forest map" teletext mosaic

# SVG (auto-detect)
python -m extensions.core.ok_assist.api.gemini "human heart" svg auto
```

## Demo Script

```bash
cd /Users/fredbook/Code/uDOS
python extensions/core/ok-assist/examples/generate_multi_format.py
```

**Generates**:
- Water filter (ASCII, Teletext, SVG)
- Heart anatomy (ASCII, Teletext, SVG)
- Fire triangle (all 4 variations)

## Format Comparison

| Feature | ASCII | Teletext | SVG |
|---------|-------|----------|-----|
| **Display** | Terminal | Web | Web/Print |
| **Colors** | Mono | 8-color | Mono/Grey |
| **Size** | 80×24 | 40×25 | Scalable |
| **Output** | `.txt` | `.html` | `.svg` |
| **Use** | CLI docs | Maps | Documentation |

## Style Selection Guide

### Use Technical-Kinetic for:
- ✓ Tools and machinery
- ✓ Systems and flowcharts
- ✓ UI mockups
- ✓ Structural diagrams
- ✓ Knots and techniques

### Use Hand-Illustrative for:
- ✓ Human anatomy
- ✓ Plants and leaves
- ✓ Animals
- ✓ Natural landscapes
- ✓ Food cross-sections
- ✓ Rope and materials

## Quality Targets

- **ASCII**: <10KB, 80×24 chars, UTF-8
- **Teletext**: <50KB, valid HTML5
- **SVG**: <50KB, editable text, accessible

## File Locations

```
knowledge/diagrams/
├── ascii/           # Terminal graphics (.txt)
├── teletext/        # Web graphics (.html)
├── medical/         # SVG medical diagrams
├── water/           # SVG water diagrams
├── tools/           # SVG tool diagrams
└── {category}/      # Category-specific SVGs
```

## Troubleshooting

**API Key Error**:
```bash
# Add to .env
echo "GEMINI_API_KEY=your-key" >> .env
```

**Import Error**:
```bash
pip install google-generativeai python-dotenv
```

**Large Files**:
- Reduce complexity level
- Simplify description
- Use "simple" or "moderate"

---

**Reference**: C64 PetMe character set
**Asset Library**: `/extensions/assets/`
**Documentation**: `assets/DESIGN_SYSTEM.md`
