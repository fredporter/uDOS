# SVG Graphics Guide (v1.2.15)

Complete reference for AI-assisted SVG vector graphics generation in uDOS.

---

## Overview

SVG (Scalable Vector Graphics) provides high-quality vector diagrams with AI-assisted generation via Gemini API. Templates offer offline fallback when AI is unavailable or for simple diagrams.

### Key Features

- **AI-Assisted**: Gemini API for complex diagrams
- **Template-Based**: Offline fallback for common patterns
- **Scalable**: Resolution-independent vector graphics
- **Style Presets**: Technical, simple, detailed
- **Size Limit**: 50KB maximum per file

---

## Style Presets

### 1. Technical (Blueprint Style)

**Use Case**: Engineering diagrams, technical specifications

**Characteristics**:
- Grid background
- Measurements and annotations
- Blues and grays color scheme
- Clean lines, precise geometry
- Blueprint aesthetic

**Example Use**:
```bash
MAKE --format svg --style technical --source "water filter system"
```

**Visual Elements**:
- Background grid (20px spacing)
- Dimension arrows and labels
- Component callouts
- Technical symbols
- Monospace font for measurements

### 2. Simple (Minimalist)

**Use Case**: Clean illustrations, quick diagrams

**Characteristics**:
- Flat colors (pastels)
- Minimal details
- Clean backgrounds
- Simple shapes
- High contrast

**Example Use**:
```bash
MAKE --format svg --style simple --source "shelter types comparison"
```

**Visual Elements**:
- Solid fills, no gradients
- Thin outlines (1-2px)
- Pastel color palette
- Sans-serif fonts
- Minimal shadows

### 3. Detailed (Comprehensive)

**Use Case**: Complex systems, detailed schematics

**Characteristics**:
- Full color palette
- Gradients and shadows
- Depth and dimension
- Detailed annotations
- Professional finish

**Example Use**:
```bash
MAKE --format svg --style detailed --source "complete rainwater harvesting system"
```

**Visual Elements**:
- Linear gradients
- Drop shadows
- Multiple layers
- Rich color scheme
- Serif fonts for labels

---

## AI-Assisted Generation

### Requirements

1. Gemini API key in `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

2. Enable AI flag:
   ```bash
   MAKE --format svg --style detailed --ai-assisted --source "description"
   ```

### When to Use AI

✅ **Good Use Cases**:
- Complex systems (multiple components)
- Unfamiliar subject matter
- Need for creative interpretation
- Detailed technical diagrams

❌ **Avoid AI For**:
- Simple shapes or flowcharts
- Repetitive patterns
- Standard templates (use template-based instead)
- Offline scenarios

### AI Prompts

AI uses admin-managed prompts from `core/data/prompts/graphics/svg/`.

View prompts (requires DEV MODE):
```bash
PROMPT LIST svg
PROMPT SHOW svg_default
```

Edit prompts (admin only):
```bash
CONFIG SET dev_mode true
PROMPT EDIT svg_default
```

---

## Template-Based Generation

### When Templates Work

✅ **Best For**:
- Standard diagrams (flowcharts, org charts)
- Offline scenarios
- Simple illustrations
- Faster generation (no API call)

### Available Templates

```bash
# List templates
MAKE --list svg

# Use template
MAKE --format svg --template flowchart --source "process steps"
```

**Template Library**:
- `flowchart.svg` - Standard flowchart
- `system_diagram.svg` - System architecture
- `network.svg` - Network topology
- `timeline.svg` - Timeline visualization

---

## SVG Structure

### Basic SVG File

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 400 300"
     width="400" 
     height="300">
  <title>Diagram Title</title>
  <desc>Detailed description for accessibility</desc>
  
  <!-- Content here -->
  
</svg>
```

### Essential Elements

**viewBox**: Defines coordinate system
```xml
viewBox="0 0 400 300"  
<!-- minX minY width height -->
```

**Shapes**:
```xml
<rect x="10" y="10" width="100" height="50" />
<circle cx="150" cy="50" r="30" />
<line x1="10" y1="10" x2="100" y2="100" />
<path d="M 10,10 L 100,100 L 200,50 Z" />
```

**Text**:
```xml
<text x="50" y="30" 
      font-family="sans-serif" 
      font-size="14" 
      text-anchor="middle">
  Label Text
</text>
```

**Groups**:
```xml
<g id="component-group">
  <rect ... />
  <text ... />
</g>
```

---

## Color Schemes

### Technical (Blueprint)

```xml
<defs>
  <style>
    .bg { fill: #f8f9fa; }
    .primary { stroke: #2e5c8a; fill: #4a90e2; }
    .secondary { stroke: #555; fill: #d4e6f1; }
    .grid { stroke: #e0e0e0; stroke-width: 0.5; }
    .text { fill: #2e5c8a; font-family: monospace; }
  </style>
</defs>
```

### Simple (Minimalist)

```xml
<defs>
  <style>
    .bg { fill: #ffffff; }
    .primary { stroke: #333; fill: #91d5ff; }
    .secondary { stroke: #333; fill: #d3f261; }
    .accent { fill: #ffd591; }
    .text { fill: #333; font-family: sans-serif; }
  </style>
</defs>
```

### Detailed (Comprehensive)

```xml
<defs>
  <linearGradient id="grad1">
    <stop offset="0%" stop-color="#4a90e2" />
    <stop offset="100%" stop-color="#2e5c8a" />
  </linearGradient>
  
  <filter id="shadow">
    <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
  </filter>
</defs>
```

---

## Command Usage

### Basic Generation

```bash
# AI-assisted
MAKE --format svg --style technical --ai-assisted --source "water filter"

# Template-based
MAKE --format svg --template flowchart --source "process flow"

# Custom output
MAKE --format svg --style simple --source "diagram" --output custom.svg
```

### Options

```bash
--style <technical|simple|detailed>  # Visual style
--ai-assisted                        # Use Gemini API
--template <name>                    # Use template
--source <text>                      # Description/content
--output <path>                      # Save location
```

---

## Best Practices

### 1. Accessibility

Always include title and description:
```xml
<svg ...>
  <title>Water Filter System</title>
  <desc>Diagram showing water flow through sand and charcoal filters</desc>
  ...
</svg>
```

### 2. Proper ViewBox

Set viewBox to match content bounds:
```xml
<!-- Content spans 0,0 to 400,300 -->
<svg viewBox="0 0 400 300" ...>
```

### 3. Semantic Grouping

Group related elements:
```xml
<g id="filter-container">
  <rect id="filter-box" ... />
  <text id="filter-label" ... />
</g>
```

### 4. Optimize File Size

- Remove unnecessary decimal places
- Use CSS classes instead of inline styles
- Combine paths when possible
- Remove comments and whitespace

### 5. Test Rendering

Verify in browsers:
```bash
open memory/drafts/svg/diagram.svg
```

---

## Advanced Techniques

### Gradients

```xml
<defs>
  <linearGradient id="blue-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#4a90e2" />
    <stop offset="100%" stop-color="#2e5c8a" />
  </linearGradient>
</defs>

<rect fill="url(#blue-gradient)" ... />
```

### Shadows

```xml
<defs>
  <filter id="dropshadow">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
    <feOffset dx="2" dy="2"/>
    <feMerge>
      <feMergeNode/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<rect filter="url(#dropshadow)" ... />
```

### Patterns

```xml
<defs>
  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
  </pattern>
</defs>

<rect width="100%" height="100%" fill="url(#grid)"/>
```

### Markers (Arrows)

```xml
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" 
          refX="5" refY="3" orient="auto">
    <path d="M 0 0 L 5 3 L 0 6 Z" fill="#2e5c8a"/>
  </marker>
</defs>

<line x1="10" y1="10" x2="100" y2="100" 
      stroke="#2e5c8a" 
      marker-end="url(#arrow)"/>
```

---

## Sizing Guidelines

### Limits

- **Maximum**: 50KB per file
- **Recommended**: 20KB for simple diagrams
- **Complexity**: Limit to 100 elements

### Optimization

If file exceeds 50KB:

1. **Simplify geometry**:
   - Reduce path points
   - Combine similar shapes
   - Remove fine details

2. **Optimize SVG**:
   ```bash
   # Use SVGO tool
   npm install -g svgo
   svgo diagram.svg
   ```

3. **Split diagram**:
   - Create multiple smaller SVGs
   - Link related diagrams

---

## Troubleshooting

### AI Generation Fails

**Problem**: `AI generation failed, falling back to template`

**Solutions**:
1. Check API key: `cat .env | grep GEMINI`
2. Verify API quota/billing
3. Simplify description
4. Use template-based instead

### SVG Not Rendering

**Problem**: File appears blank in browser

**Solutions**:
1. Check XML syntax (valid tags, quotes)
2. Verify viewBox matches content
3. Inspect browser console for errors

### File Too Large

**Problem**: Exceeds 50KB limit

**Solutions**:
1. Use `--style simple` (less detail)
2. Reduce number of elements
3. Optimize with SVGO
4. Split into multiple files

### Colors Wrong

**Problem**: Colors don't match style

**Solutions**:
1. Verify style preset used
2. Check CSS class definitions
3. Test hex color values

---

## Admin Prompt Management

### View Prompts (DEV MODE)

```bash
CONFIG SET dev_mode true
PROMPT LIST svg
PROMPT SHOW svg_default
```

### Test Prompts

```bash
PROMPT TEST svg_technical "water purification system"
```

### Edit Prompts

```bash
PROMPT EDIT svg_detailed
```

Prompts use YAML frontmatter + Markdown:
```yaml
---
id: svg_detailed
version: 1.0.0
usage_count: 47
success_rate: 0.89
---

Generate detailed SVG for: {subject}

Requirements:
- Style: {style}
- Complexity: {complexity}
...
```

---

## Related Documentation

- [Graphics System](Graphics-System.md) - Overall architecture
- [PROMPT Command](Command-Reference.md#prompt) - Prompt management
- [ASCII Graphics Guide](ASCII-Graphics-Guide.md) - Text alternative

---

**See Also**: `MAKE --help svg`, `PROMPT --help`, AI prompts: `core/data/prompts/graphics/svg/`
