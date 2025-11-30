# SVG Generator Extension

**Version**: 1.0.0
**Status**: Active
**Category**: Core Extension
**Author**: uDOS Core Team

## Overview

AI-powered SVG diagram generation with multiple artistic styles. Generate beautiful, scalable vector graphics from text descriptions.

## Features

- 🎨 **4 Artistic Styles**: lineart, blueprint, sketch, isometric
- 🤖 **AI-Powered**: Uses Gemini for intelligent diagram generation
- ✅ **SVG Validation**: Ensures well-formed XML output
- 🔄 **Post-Processing**: Cleans and optimizes generated SVG
- 👁️ **ASCII Preview**: View diagram structure in terminal
- 💾 **Auto-Save**: Exports to `sandbox/drafts/svg/`

## Installation

```bash
# Load extension
EXTENSION LOAD svg-generator

# Verify loaded
EXTENSION LIST
```

## Quick Start

### Basic Usage

```bash
# Generate simple line art
GENERATE SVG "water filter diagram"

# Use specific style
GENERATE SVG "fire starting methods" --style blueprint

# Save to file
GENERATE SVG "shelter construction" --style isometric --save shelter.svg
```

### Artistic Styles

#### 1. Line Art (Default)
Clean, minimal black lines on white background. Perfect for simple diagrams.

```bash
GENERATE SVG "first aid kit contents" --style lineart
```

**Characteristics**:
- Black (#000000) lines only
- No fills
- Stroke width: 2
- Minimal detail
- Professional, clean look

#### 2. Blueprint
Technical blueprint style with blue background and white/light blue lines.

```bash
GENERATE SVG "tent setup steps" --style blueprint
```

**Characteristics**:
- Blue background (#003366)
- White/light blue lines (#4A90E2)
- Grid background
- Technical drawing aesthetic
- Measurement indicators

#### 3. Sketch
Hand-drawn sketch style with rough, organic lines.

```bash
GENERATE SVG "campfire layout" --style sketch
```

**Characteristics**:
- Hand-drawn appearance
- Gray tones (#333, #666)
- Slightly rough lines
- Natural, informal feel
- Organic variations

#### 4. Isometric
3D isometric projection with depth and multiple colors.

```bash
GENERATE SVG "water collection system" --style isometric
```

**Characteristics**:
- 3D isometric projection (30° angles)
- Multiple colors (reds, blues, teals)
- Solid fills with outlines
- Depth and dimensionality
- Layered elements

## Command Reference

### GENERATE SVG

**Syntax**:
```
GENERATE SVG <description> [--style <style>] [--save <file>]
```

**Arguments**:
- `<description>`: Text description of what to diagram (required)
- `--style`: Artistic style: lineart, blueprint, sketch, isometric (default: lineart)
- `--save`: Save to file (optional, default: auto-generate filename)

**Examples**:
```bash
# Basic generation
GENERATE SVG "solar still water purifier"

# Specify style
GENERATE SVG "bow drill fire starter" --style sketch

# Save to specific file
GENERATE SVG "debris shelter" --style isometric --save shelters/debris.svg

# Blueprint style for technical diagrams
GENERATE SVG "water filtration system diagram" --style blueprint --save filter.svg
```

## Python API

```python
from extensions.core.svg_generator import SVGGenerator, generate_svg, quick_svg

# Using generator instance
generator = SVGGenerator()
svg = generator.generate("fire triangle diagram", style="lineart")
generator._save_svg(svg, "fire-triangle.svg")

# Using helper functions
svg = generate_svg("water purification", style="blueprint", save_path="purify.svg")

# Quick generation (lineart)
svg = quick_svg("shelter types")
```

## Output

Generated SVG files are saved to:
```
sandbox/drafts/svg/
├── water-filter-diagram.svg
├── fire-starting-methods.svg
└── shelter-construction.svg
```

Auto-generated filenames use:
- Description (sanitized)
- Timestamp (YYYY-MM-DD-HHMMSS)
- Style suffix (optional)

Example: `water-filter-lineart-2025-11-28-143022.svg`

## Requirements

### API Key (Required)

Gemini API key required for AI generation:

```bash
# Set in .env
echo 'GEMINI_API_KEY=your_key_here' >> .env

# Or via command
CONFIG SET GEMINI_API_KEY your_key_here
```

### Fallback Mode

If Gemini API unavailable, extension uses template fallback:
- Simple geometric shapes
- Basic layout
- Style-appropriate colors
- Still valid SVG

## Technical Details

### SVG Specifications

- **Format**: SVG 1.1 XML
- **ViewBox**: 0 0 800 600 (default)
- **Validation**: Well-formed XML check
- **Self-Contained**: No external dependencies
- **Semantic**: Clean, readable markup

### AI Prompting

Extension uses detailed prompts for each style:
- Style-specific guidelines
- Color palettes
- Technical requirements
- Example structure
- Best practices

### Post-Processing

Generated SVGs are automatically:
- Validated (XML parsing)
- Namespace-corrected
- ViewBox-normalized
- Pretty-printed
- Metadata-enriched

## Use Cases

### Survival Knowledge

```bash
# Water purification methods
GENERATE SVG "water purification: boiling, tablets, filter, UV" --style blueprint

# Fire starting techniques
GENERATE SVG "fire triangle: heat, fuel, oxygen" --style lineart

# Shelter types comparison
GENERATE SVG "shelters: lean-to, A-frame, debris hut" --style isometric
```

### Technical Diagrams

```bash
# System architecture
GENERATE SVG "uDOS architecture: core, extensions, knowledge" --style blueprint

# Workflow visualization
GENERATE SVG "content generation workflow" --style lineart
```

### Educational Content

```bash
# Instructional diagrams
GENERATE SVG "knot tying steps: bowline" --style sketch

# Concept illustration
GENERATE SVG "photosynthesis process" --style lineart
```

## Troubleshooting

### Common Issues

**Issue**: "Gemini API key not found"
**Solution**: Set `GEMINI_API_KEY` in `.env` or via CONFIG

**Issue**: "Generated SVG invalid"
**Solution**: Check AI response, use fallback template

**Issue**: "File not saved"
**Solution**: Check `sandbox/drafts/svg/` permissions

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Limitations

- **AI Dependency**: Requires Gemini API for best results
- **Complexity**: Complex diagrams may need manual refinement
- **Preview**: ASCII preview is basic (structure only)
- **Export**: SVG only (no PNG/PDF without external tools)

## Future Enhancements

- [ ] More artistic styles (watercolor, comic, technical)
- [ ] Interactive editing (modify generated SVG)
- [ ] Export to PNG/PDF (via extension)
- [ ] Animation support
- [ ] Custom style templates
- [ ] Batch generation
- [ ] Style mixing

## Related

- **DRAW Command**: ASCII diagram generation (v1.1.4)
- **DIAGRAM**: ASCII art library browser
- **GENERATE**: Content generation system
- **OK Assist**: AI assistant integration

## Credits

**Development**: uDOS Core Team
**AI Integration**: Google Gemini API
**SVG Standards**: W3C SVG 1.1 Specification

## License

MIT License - See LICENSE.txt

---

**Version**: 1.0.0
**Last Updated**: November 28, 2025
**Status**: Production Ready
