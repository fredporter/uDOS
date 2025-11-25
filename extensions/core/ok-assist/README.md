# OK Assist - AI Content Generation Extension

**System-wide AI content generation using Gemini API**

## ✅ v1.4.0 - Multi-Format Generation System (November 2025)

**NEW**: Unified design system linking ASCII art, Teletext graphics, and SVG diagrams with C64 PetMe as the foundational reference. All formats tested and working.

📄 **[Success Report](SUCCESS_REPORT.md)** | 📚 **[Complete Documentation](INDEX.md)**

---

## Overview

OK Assist integrates Google's Gemini API for automated content generation across uDOS, with specialized support for survival guides, multi-format diagrams, and knowledge conversion. Available system-wide (not dev-only).

**Key Integration**: Uses centralized `/extensions/assets/` for fonts, icons, and CSS frameworks.

## Features

### Multi-Format Generation (NEW v1.4.0)
- **ASCII Art**: C64 PetMe/PETSCII character set for terminal/CLI diagrams
- **Teletext Graphics**: WST mosaic blocks for retro web display (40×25)
- **SVG Diagrams**: Technical-Kinetic and Hand-Illustrative styles
- **Unified Design System**: Cross-format consistency with C64 foundation

### Content Generation
- **Text Generation**: Survival guides, reference materials, checklists
- **Format Conversion**: External resources to uDOS markdown
- **Image Analysis**: Raster to vector conversion with style constraints

### Visual Format Styles

#### ASCII Art (Terminal/CLI)
Text-based diagrams using C64 PetMe character set:
- **Dimensions**: 80×24 (standard terminal) or custom
- **Characters**: Box-drawing (┌┐└┘├┤┬┴┼─│), shading (░▒▓), symbols (≈∙·○●)
- **Output**: Plain text `.txt` files
- **Use Cases**: CLI help, terminal documentation, quick reference

#### Teletext Graphics (Web)
Mosaic block graphics for retro web display:
- **Dimensions**: 40×25 (Teletext standard)
- **Format**: HTML with colored mosaic blocks (2×3 pixel cells)
- **Colors**: WST 8-color palette (RGBCMYW + Black)
- **Output**: `.html` files with inline CSS
- **Use Cases**: Retro web maps, chunky icons, nostalgic UI

#### SVG Technical-Kinetic (Technical Subjects)
Monochrome vector diagrams for technical/mechanical subjects:
- **Icons**: CoreUI system icons (1500+ from `/assets/icons/coreui/`)
- **Line Weight**: Primary 1.5px, detail 0.5px, texture 0.3px, bold 2.5px
- **Patterns**: Mac OS System 1 bitmap patterns (8×8 pixel perfect)
- **Shading**: Crosshatch, stipple, parallel lines, gradient simulation
- **Typography**: Chicago 12pt (titles), Geneva 9pt (body) from `/assets/fonts/`
- **Subjects**: Tools, machinery, structures, systems, diagrams, UI, knots

#### Hand-Illustrative Line-Art (Organic Subjects)
Traditional engraving/woodcut style for natural/physical subjects:
- **Line Style**: Variable weight (0.8px fine, 1.5px medium, 2.5px bold), organic curves
- **Shading**: Wavy parallel lines, circular concentric patterns, cross-contour
- **Textures**: Woodgrain, stone, water ripples, cloud fields, fabric weave
- **Typography**: Geneva 14pt italic bold (titles), 10pt (body), 8pt italic (captions)
- **Detail**: Form-following contours, stipple density, topographical precision
- **Subjects**: Anatomy, plants, animals, landscapes, food, rope, natural materials

---

## Quick Start

### Generate ASCII Art
```python
from api.gemini import model

prompt = """Generate ASCII art using C64 PetMe characters.
SUBJECT: Water filter
DIMENSIONS: 60×20
Use: ┌┐└┘├┤┬┴┼─│ (boxes), ░▒▓ (shading)"""

response = model.generate_content(prompt)
print(response.text)
```

### Generate Teletext Graphics
```python
prompt = """Generate Teletext HTML with mosaic blocks.
SUBJECT: Heart icon
DIMENSIONS: 30×15
Colors: Red (#ff0000) on black (#000000)
Use █ for solid blocks"""

response = model.generate_content(prompt)
# Outputs complete HTML with inline CSS
```

### Generate SVG Diagrams
```python
prompt = """Generate SVG in Technical-Kinetic style.
SUBJECT: Fire triangle
STYLE: Geometric, monochrome, 2px lines
DIMENSIONS: 400×400px"""

response = model.generate_content(prompt)
# Outputs complete <svg>...</svg>
```

**See:** [examples/demo_simple.py](examples/demo_simple.py) for complete working examples.

---

## Directory Structure

```
ok-assist/
├── README.md              # This file
├── SUCCESS_REPORT.md      # v1.4.0 completion report
├── INDEX.md               # Documentation navigation
├── api/
│   ├── gemini.py         # Gemini API wrapper (multi-format generation)
│   └── prompts/          # Detailed style-specific prompts
│       ├── style_definitions.json
│       ├── technical_kinetic_prompt.md
│       └── hand_illustrative_prompt.md
├── assets/
│   ├── DESIGN_SYSTEM.md  # Complete unified design system
│   └── design_assets.py  # Asset management utilities
├── docs/
│   ├── STYLE_GUIDE.md    # Comprehensive style guide
│   ├── INTEGRATION.md    # Integration documentation
│   └── EXAMPLES.md       # Usage examples
├── examples/
│   ├── demo_simple.py    # ✅ Multi-format generation demo (WORKING)
│   ├── test_gemini.py    # API connectivity test
│   └── test_quick.py     # Quick API validation
├── css/
│   ├── technical-kinetic.css      # Technical diagram styles
│   ├── hand-illustrative.css      # Organic illustration styles
│   ├── svg-common.css             # Shared SVG styles
│   └── diagram-viewer.css         # Diagram display component
├── docs/
│   ├── STYLE_GUIDE.md            # Complete style specifications
│   └── EXAMPLES.md               # Generated examples
├── templates/
│   ├── svg-technical.template     # Technical diagram scaffold
│   ├── svg-organic.template       # Organic illustration scaffold
│   └── pattern-library.svg        # Reusable SVG patterns
└── docs/
    ├── STYLE_GUIDE.md             # Complete style specification
    ├── API_USAGE.md               # Gemini API integration
    └── EXAMPLES.md                # Generated examples gallery
```

## Installation

```bash
# Install from uDOS root
cd /Users/fredbook/Code/uDOS
pip install google-generativeai

# Configure API key
export GEMINI_API_KEY="your-key-here"

# Or add to .env
echo "GEMINI_API_KEY=your-key-here" >> .env
```

## Usage

### Command Line (uDOS Commands)

```bash
# Generate survival guide
GENERATE medical/hypothermia-treatment --style=reference

# Generate technical diagram (CoreUI icons + bitmap patterns)
SVG tools/axe-safety --style=technical-kinetic

# Generate organic illustration (hand-drawn line-art)
SVG medical/human-circulatory-system --style=hand-illustrative

# Convert external resource
CONVERT https://example.com/survival-guide.pdf --output=knowledge/water/
```

### Python API

```python
from extensions.core.ok_assist.api.gemini import OKAssist

# Initialize
ok = OKAssist(api_key="your-key-here")

# Generate technical diagram
svg = ok.generate_svg(
    subject="water filtration system",
    style="technical-kinetic",
    complexity="detailed"
)

# Generate organic illustration
svg = ok.generate_svg(
    subject="edible plant anatomy",
    style="hand-illustrative",
    detail_level="high"
)

# Generate text guide
guide = ok.generate_guide(
    topic="fire-starting-methods",
    category="fire",
    length="comprehensive"
)
```

### Web Extensions

```html
<!-- Include OK Assist styles -->
<link rel="stylesheet" href="../ok-assist/css/technical-kinetic.css">
<link rel="stylesheet" href="../ok-assist/css/hand-illustrative.css">
<link rel="stylesheet" href="../ok-assist/css/svg-common.css">

<!-- CoreUI icons for technical diagrams -->
<link rel="stylesheet" href="../../assets/icons/coreui/css/free.min.css">

<!-- System fonts (already in assets) -->
<link rel="stylesheet" href="../../assets/css/typography-system.css">
```

## Style Guidelines

### When to Use Technical-Kinetic
- Tools and equipment
- Mechanical systems
- UI diagrams and flowcharts
- Structural blueprints
- System architecture
- Knots and lashings (geometric)
- Navigation instruments

**Visual Characteristics**:
- Sharp, clean lines (1.5px primary)
- CoreUI system icons for UI elements
- Mac OS bitmap patterns for fills
- Geometric precision
- Crosshatch/stipple shading
- Monospace fonts (Chicago 12pt, Geneva 9pt)

### When to Use Hand-Illustrative
- Human anatomy and organs
- Plants and botanical subjects
- Animals and wildlife
- Landscapes and terrain
- Food and cooking
- Natural materials (wood, stone, rope)
- Weather and atmospheric effects

**Visual Characteristics**:
- Variable line weight (0.8-2.5px)
- Flowing, organic curves
- Wavy/circular shading patterns
- Topographical detail
- Engraving/woodcut aesthetic
- Hand-drawn feel with precision

## Pattern Library

### Technical Patterns (8×8 bitmap)
```xml
<!-- Mac OS System 1 patterns -->
<pattern id="gray-50">...</pattern>
<pattern id="crosshatch">...</pattern>
<pattern id="diagonal">...</pattern>
<pattern id="dots">...</pattern>
```

### Organic Patterns (vector)
```xml
<!-- Hand-illustrative textures -->
<pattern id="woodgrain">...</pattern>
<pattern id="water-ripple">...</pattern>
<pattern id="cloud-field">...</pattern>
<pattern id="stone-texture">...</pattern>
```

## API Integration

### Gemini Image Generation Prompts

**Technical-Kinetic Prompt**:
```
Create a monochrome SVG technical diagram of {subject} using:
- Clean vector lines (1.5px weight for primary, 0.5px for detail)
- CoreUI icon style for UI elements and controls
- Mac OS System 1 bitmap patterns (8×8 grid) for fills
- Crosshatch or stipple shading
- Geometric precision and measurement clarity
- Labels using monospace font (Geneva 9pt style)
Output pure SVG code optimized for scalability.
```

**Hand-Illustrative Prompt**:
```
Create a monochrome SVG illustration of {subject} in woodcut/engraving style:
- Variable line weight (0.8-2.5px) following organic forms
- Wavy parallel lines for shading fields
- Circular/concentric patterns for atmospheric effects
- Topographical detail and natural texture
- Hand-drawn aesthetic with precision
- Flowing curves and natural proportions
Output pure SVG code with editable text elements.
```

## File Size Targets

- **Simple diagrams**: 5-10KB
- **Detailed illustrations**: 10-25KB
- **Complex technical**: 15-35KB
- **Maximum**: 50KB (enforced)

All SVGs must be minified and optimized.

## Integration Points

### With Existing Systems
- `/dev/tools/diagram_templates.py` - Template library
- `/dev/tools/macos_ui_components.py` - UI components
- `/knowledge/diagrams/` - Diagram storage
- `/extensions/assets/` - Shared CSS, fonts, icons

### With Commands
- `GENERATE` - Text content generation
- `SVG` - Diagram generation (new)
- `CONVERT` - External resource conversion
- `DIAGRAM` - Display/search diagrams

## Credits

- **Gemini API**: Google AI
- **CoreUI Icons**: CoreUI.io (MIT License)
- **Mac OS Patterns**: system.css by @sakofchit (MIT)
- **Typography**: system.css fonts by @blogmywiki (MIT)
- **Style Development**: uDOS Project

## Version History

**v1.0.0** (November 25, 2025)
- Initial release
- Technical-Kinetic and Hand-Illustrative styles
- Gemini API integration
- CoreUI icon integration
- Pattern library

---

**Location**: `/extensions/core/ok-assist/`
**Maintained by**: uDOS Project
**License**: MIT (see individual component licenses)
