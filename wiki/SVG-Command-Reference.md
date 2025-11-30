# SVG Command Reference

**⚠️ DEPRECATED in v1.1.6** - Use `GENERATE SVG` for new projects (see [Nano Banana Integration](Nano-Banana-Integration.md))

**Command**: `SVG`
**Category**: Graphics
**Version**: 1.1.5
**Status**: Legacy (maintained for compatibility)
**Location**: `extensions/core/svg_generator/`

> **Migration Note**: The `SVG` command continues to work but uses text-based prompting instead of the superior PNG→SVG pipeline. For production-quality Technical-Kinetic diagrams, use **`GENERATE SVG`** instead.

---

## Migration to GENERATE Command

### Why Migrate?

| Old (SVG) | New (GENERATE SVG) |
|-----------|-------------------|
| Text-based prompting (unreliable) | PNG→SVG pipeline (robust) |
| 4 artistic styles | Technical-Kinetic + 2 alternatives |
| Template fallback | Nano Banana image generation |
| No style consistency | Style guide system (0-14 refs) |
| No validation | Strict compliance checking |
| Variable quality | Production-ready quality |

### Quick Migration

**Old Syntax:**
```bash
SVG "water filter diagram" --style lineart
SVG "fire triangle" --style blueprint
SVG "shelter construction" --style sketch
SVG "survival camp layout" --style isometric
```

**New Syntax:**
```bash
GENERATE SVG water filter diagram --style technical-kinetic
GENERATE DIAGRAM fire triangle --type flowchart
GENERATE SVG shelter construction --style hand-illustrative
GENERATE SVG survival camp layout --type architecture
```

**Style Mapping:**

| Old Style | New Style |
|-----------|-----------|
| `lineart` | `technical-kinetic` |
| `blueprint` | `technical-kinetic` (use `--type architecture`) |
| `sketch` | `hand-illustrative` |
| `isometric` | `technical-kinetic` (use `--type architecture`) |

### Migration Steps

1. **Update commands**: Replace `SVG` with `GENERATE SVG`
2. **Update styles**: Map old styles to new (see table above)
3. **Add types**: Specify diagram type (`--type flowchart`, etc.)
4. **Test output**: Verify quality meets requirements
5. **Update workflows**: Replace in `.uscript` files
6. **Update docs**: Reference new command in documentation

**Example Migration:**

```diff
- SVG "water purification methods" --style lineart
+ GENERATE SVG water purification methods --type flowchart

- SVG "solar still construction" --style blueprint
+ GENERATE SVG solar still construction --type architecture

- SVG "campfire layout" --style sketch
+ GENERATE SVG campfire layout --style hand-illustrative
```

---

## Legacy Documentation (v1.1.5)

> **⚠️ This section documents the legacy SVG command for reference only.**

## Overview

Generate scalable vector graphics (SVG) diagrams from text descriptions using AI or template fallback. Supports 4 artistic styles optimized for survival knowledge and technical documentation.

## Syntax

```bash
SVG <description> [--style <style>] [--save <file>] [--no-preview]
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `<description>` | string | Yes | - | Text description of diagram to generate |
| `--style` | string | No | `lineart` | Artistic style (see Styles below) |
| `--save` | path | No | auto | Save path (relative to `sandbox/drafts/svg/`) |
| `--no-preview` | flag | No | false | Skip ASCII preview in terminal |

## Artistic Styles

### lineart (Default)
**Best for**: Simple diagrams, quick reference, clean documentation

- Clean black lines on white background
- Minimal detail, focus on essentials
- Professional, uncluttered appearance
- Stroke width: 2px
- No fills, outline only

**Example**:
```bash
SVG "water purification methods"
```

### blueprint
**Best for**: Technical plans, construction diagrams, measurements

- Blue background (#003366)
- White/light blue lines (#4A90E2, #E8F4F8)
- Grid background for measurement reference
- Technical drawing aesthetic
- Stroke width: 1px

**Example**:
```bash
SVG "solar still construction" --style blueprint
```

### sketch
**Best for**: Field notes, informal guides, hand-drawn feel

- Hand-drawn appearance
- Gray tones (#333333, #666666)
- Slightly rough, organic lines
- Natural, informal aesthetic
- Stroke width: 2px

**Example**:
```bash
SVG "campfire layout" --style sketch
```

### isometric
**Best for**: 3D views, spatial relationships, system architecture

- 3D isometric projection (30° angles)
- Multiple colors (reds, blues, teals)
- Solid fills with outlines
- Shows depth and dimensionality
- Stroke width: 2px

**Example**:
```bash
SVG "water collection system" --style isometric
```

## Examples

### Basic Usage

```bash
# Simple line art (default)
SVG water filter diagram

# Technical blueprint
SVG fire starting methods --style blueprint

# Hand-drawn sketch
SVG shelter construction --style sketch

# 3D isometric view
SVG survival camp layout --style isometric
```

### Saving Files

```bash
# Auto-save with timestamp
SVG "first aid kit contents"
# Saves to: sandbox/drafts/svg/first-aid-kit-contents-lineart-20251128-143022.svg

# Custom filename
SVG "fire triangle" --save fire-basics.svg

# Save to subfolder
SVG "water purification" --save water/purify-methods.svg

# Absolute path
SVG "shelter types" --save /path/to/diagrams/shelters.svg
```

### Advanced Usage

```bash
# Process flow
SVG "water purification: collect, filter, purify, store" --style blueprint

# System diagram
SVG "survival camp: shelter, fire, water source, signal area" --style isometric

# Comparison diagram
SVG "knot types: bowline, square knot, clove hitch" --style sketch

# Skip preview for batch generation
SVG "diagram 1" --no-preview
SVG "diagram 2" --no-preview
SVG "diagram 3" --no-preview
```

## Output

Generated SVGs are:
- **Format**: Valid SVG 1.1 XML
- **ViewBox**: 0 0 800 600 (scalable)
- **Namespace**: xmlns="http://www.w3.org/2000/svg"
- **Self-Contained**: No external dependencies
- **Browser-Compatible**: Opens in any modern browser
- **Editor-Compatible**: Works with Inkscape, Illustrator, etc.

### Default Output Location
```
sandbox/drafts/svg/
├── <description>-<style>-<timestamp>.svg
└── custom-filename.svg
```

### File Naming
Auto-generated filenames use:
- Description (sanitized, max 30 chars)
- Style name
- Timestamp (YYYY-MM-DD-HHMMSS)

Example: `water-filter-diagram-blueprint-20251128-143022.svg`

## AI Integration

### With Gemini API

When `GEMINI_API_KEY` is configured:
- Uses Google Gemini for intelligent diagram generation
- Interprets descriptions contextually
- Applies style-specific rendering
- Typically 2-5 seconds generation time

### Fallback Mode

Without API key or on API failure:
- Uses template-based generation
- Simple geometric shapes
- Style-appropriate colors and layouts
- Sub-millisecond generation
- Fully functional offline

## Integration with Other Commands

### With DRAW

```bash
# Quick ASCII preview
DRAW flowchart "water purification process"

# Then generate polished SVG
SVG "water purification process flow" --style blueprint
```

### With GUIDE

```bash
# Read knowledge guide
GUIDE water/purification

# Generate diagram from guide content
SVG "water purification methods: boiling, chemical, filtering" --style lineart
```

### With BANK

```bash
# Search knowledge
BANK SEARCH "fire starting"

# Generate overview diagram
SVG "fire starting methods overview" --style sketch
```

## Use Cases

### Survival Knowledge

```bash
# Water
SVG "water sources: streams, springs, rainwater, dew" --style blueprint
SVG "water filter construction layers" --style isometric

# Fire
SVG "fire triangle components" --style lineart
SVG "bow drill fire starter parts" --style sketch

# Shelter
SVG "debris hut construction steps" --style blueprint
SVG "shelter types comparison" --style isometric

# Food
SVG "edible plant identification" --style lineart
SVG "fish trap design" --style blueprint

# Navigation
SVG "shadow stick direction finding" --style sketch
SVG "compass parts and usage" --style blueprint

# Medical
SVG "first aid kit essentials" --style lineart
SVG "CPR steps sequence" --style isometric
```

### Technical Documentation

```bash
# System architecture
SVG "uDOS architecture: core, extensions, knowledge" --style blueprint

# Workflow diagrams
SVG "content generation workflow" --style lineart

# Data structures
SVG "knowledge bank organization" --style isometric
```

## Tips for Best Results

### Description Guidelines

1. **Be Specific**: "water filter with 3 layers: gravel, sand, charcoal" vs "water filter"
2. **List Components**: Include key elements or steps
3. **Use Colons**: Separate main topic from details
4. **Keep Concise**: 5-15 words optimal

### Style Selection

- **lineart**: Simple concepts, definitions, quick reference
- **blueprint**: Construction, measurements, technical specs
- **sketch**: Field notes, casual guides, brainstorming
- **isometric**: Spatial relationships, system views, architecture

### Performance

- Template mode: < 1ms per diagram
- AI mode: 2-5 seconds per diagram
- Use `--no-preview` for batch generation
- AI generation may fail (safety filters) → fallback works

## Requirements

### Optional (Recommended)
- **Gemini API Key**: For AI-powered generation
  - Set in `.env`: `GEMINI_API_KEY=your_key_here`
  - Or: `CONFIG SET GEMINI_API_KEY your_key_here`

### System
- Python 3.10+
- uDOS v1.1.5+
- svg_generator extension (auto-loaded)

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Unknown style" | Invalid `--style` value | Use: lineart, blueprint, sketch, or isometric |
| "Generated SVG is not well-formed XML" | Invalid SVG output | Report bug with description used |
| "AI generation failed" | Gemini API error | Check API key, quota; fallback used automatically |

## Technical Details

### File Format
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <title>Description</title>
  <desc>Generated by uDOS SVG Generator</desc>
  <!-- Diagram elements -->
</svg>
```

### Validation
- XML well-formedness checked
- xmlns attribute ensured
- viewBox attribute added if missing
- Element structure validated

### Post-Processing
- Adds missing xmlns
- Adds missing viewBox
- Ensures valid XML structure
- String-based (no namespace prefixes)

## See Also

- **DRAW** - ASCII diagram generation (offline)
- **DIAGRAM** - ASCII art library browser
- **GUIDE** - Knowledge guide viewer
- **BANK** - Knowledge search
- **GENERATE** - AI script generation

## Version History

- **v1.1.5** - Initial release with 4 artistic styles
- Extension location: `extensions/core/svg_generator/`
- Command handler: `core/commands/svg_handler.py`

---

**Last Updated**: November 28, 2025
**Status**: Production Ready
**License**: MIT
