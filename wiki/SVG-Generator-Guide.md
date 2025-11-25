# Developer Tools - SVG Diagram Generator

**uDOS v1.4.0** - Automated SVG diagram generation using OK Assist (Gemini API)

> **💡 Quick Start**: Generate diagrams with `python dev/tools/generate_svg_diagram.py "description" category`

---

## Overview

The SVG Diagram Generator creates Technical-Kinetic compliant diagrams using Google's Gemini API. It automatically generates complete SVG files with proper styling, patterns, and the Mallard custom font.

### Features

- ✅ **Full Gemini API Integration** - Generates complete SVG diagrams from text descriptions
- ✅ **Technical-Kinetic Compliance** - Enforces monochrome, pattern-based styling
- ✅ **Mallard Font Embedding** - Auto-includes custom uDOS font
- ✅ **Pattern Library** - 12 pre-defined patterns (grayscale + textures)
- ✅ **Automatic Validation** - Checks compliance with uDOS standards
- ✅ **Material Detection** - Smart pattern assignment based on content

---

## Setup

### 1. Get Gemini API Key

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get a free API key.

### 2. Configure API Key

```bash
cd /Users/fredbook/Code/uDOS

# Create .env file with your Gemini API key
echo 'GEMINI_API_KEY=your_actual_api_key_here' > .env

# Or set via uDOS command
CONFIG SET GEMINI_API_KEY your_key_here
```

### 3. Verify Setup

```bash
# Check .env file exists
ls -la .env

# Check key is set
cat .env | grep GEMINI

# Test generation (requires activation)
source .venv/bin/activate
python dev/tools/generate_svg_diagram.py "test diagram" water
```

---

## Usage

### Basic Command

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate

# Generate a diagram
python dev/tools/generate_svg_diagram.py "description" category

# Example
python dev/tools/generate_svg_diagram.py "water filter 3 stages" water
```

### Command-Line Options

```bash
python dev/tools/generate_svg_diagram.py [OPTIONS] DESCRIPTION CATEGORY

Arguments:
  DESCRIPTION    What to draw (e.g., "CPR hand placement adult")
  CATEGORY       water | fire | shelter | food | navigation | medical | tools | communication

Options:
  --size, -s     Diagram dimensions (default: 800x600)
                 Format: WIDTHxHEIGHT (e.g., 1200x800)

  --output, -o   Custom filename (auto-generated if omitted)
                 Example: my-custom-diagram.svg

  --env          Path to .env file with GEMINI_API_KEY
                 Default: auto-detects from project root

  --help, -h     Show help message
```

---

## Examples

### Medical Diagrams

```bash
# Basic tourniquet application
python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical

# CPR technique
python dev/tools/generate_svg_diagram.py "CPR hand placement adult" medical --size 1000x800

# Custom filename
python dev/tools/generate_svg_diagram.py "wound dressing steps" medical -o wound-care.svg
```

### Water Diagrams

```bash
# Water purification
python dev/tools/generate_svg_diagram.py "water filter charcoal sand gravel" water

# Advanced filter
python dev/tools/generate_svg_diagram.py "solar still water collection" water -o solar-still.svg
```

### Fire Diagrams

```bash
# Fire triangle
python dev/tools/generate_svg_diagram.py "fire triangle heat fuel oxygen" fire

# Bow drill
python dev/tools/generate_svg_diagram.py "bow drill fire starting assembly" fire --size 1200x900
```

### Tools Diagrams

```bash
# Knife sharpening
python dev/tools/generate_svg_diagram.py "knife sharpening angle guide" tools

# Shelter construction
python dev/tools/generate_svg_diagram.py "A-frame shelter construction" shelter
```

---

## Output Location

Generated diagrams are saved to:
```
knowledge/diagrams/{category}/{auto-generated-name}.svg
```

**Examples:**
```
knowledge/diagrams/medical/tourniquet-application-6-steps.svg
knowledge/diagrams/water/water-filter-charcoal-sand-gravel.svg
knowledge/diagrams/fire/fire-triangle-heat-fuel-oxygen.svg
knowledge/diagrams/tools/knife-sharpening-angle-guide.svg
```

---

## Technical-Kinetic Compliance

### Style Requirements

All generated SVGs follow Technical-Kinetic standards:

1. **Monochrome** - Black lines on white background
2. **Patterns** - Textures for material differentiation
3. **Clear Labels** - Text annotations for clarity
4. **Step Numbers** - Sequential visual process
5. **Mallard Font** - Custom embedded font
6. **800x600 viewBox** - Standard dimensions (unless custom size)

### Pattern Library

The generator includes 12 pre-defined patterns:

**Grayscale Patterns:**
- `gray-light` - 10% fill
- `gray-25` - 25% fill
- `gray-medium` - 50% fill
- `gray-75` - 75% fill
- `gray-dark` - 90% fill

**Texture Patterns:**
- `dots` - Dotted texture
- `lines-diagonal` - Diagonal hatching
- `lines-horizontal` - Horizontal lines
- `lines-vertical` - Vertical lines
- `crosshatch` - Cross-hatched
- `grid` - Grid pattern
- `circles` - Circular texture

### Material Detection

The AI automatically assigns patterns based on content:

- **Metal** → Gray-dark, crosshatch
- **Wood** → Lines-vertical, gray-medium
- **Fabric** → Lines-diagonal, gray-light
- **Liquid** → Lines-horizontal, gray-25
- **Stone** → Dots, gray-75

---

## Integration with Content Generation

### Batch Diagram Generation

Use the content generation tool for bulk creation:

```bash
# Generate 10 water diagrams
python dev/tools/generate_content_v1_4_0.py --category water --count 10 --diagrams-only

# Generate all categories
python dev/tools/generate_content_v1_4_0.py --all --diagrams-only
```

### OK Assist Integration

The SVG generator uses OK Assist API directly:

```python
from extensions.core.ok-assist.ok_assistant import OKAssistant

ok = OKAssistant(api_key=GEMINI_API_KEY)
svg_content = ok.generate_diagram(
    description="water filter 3 stages",
    style="technical-kinetic",
    format="svg"
)
```

---

## Validation

### Automatic Checks

The generator validates:

1. **SVG syntax** - Well-formed XML
2. **Pattern definitions** - All patterns defined in `<defs>`
3. **Font embedding** - Mallard font included
4. **Dimensions** - Correct viewBox and size
5. **Style compliance** - Monochrome, pattern-based

### Manual Inspection

```bash
# View generated SVG
cat knowledge/diagrams/water/water-filter.svg

# Validate XML syntax
xmllint --noout knowledge/diagrams/water/water-filter.svg

# Check file size (should be < 200KB)
ls -lh knowledge/diagrams/water/water-filter.svg
```

---

## Troubleshooting

### API Key Errors

**Problem:** `GEMINI_API_KEY not found` or `Invalid API key`

**Solutions:**

```bash
# Check .env file exists
ls -la .env

# Verify key is set
cat .env | grep GEMINI_API_KEY

# Set key via command
echo 'GEMINI_API_KEY=your_actual_key_here' > .env

# Test with Python
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

### Generation Failures

**Problem:** SVG generation fails or produces invalid output

**Solutions:**

```bash
# Check API quota
# Visit: https://makersuite.google.com/app/apikey

# Try simpler description
python dev/tools/generate_svg_diagram.py "simple water filter" water

# Check logs
cat memory/logs/udos.log | tail -50
```

### Rate Limiting

**Problem:** `Rate limit exceeded` or `Quota exceeded`

**Solutions:**

```bash
# Wait and retry (Gemini has rate limits)
sleep 60 && python dev/tools/generate_svg_diagram.py "..." water

# Use batch generation with delays (0.5s between calls)
python dev/tools/generate_content_v1_4_0.py --category water --count 5

# Check quota status
# Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
```

---

## Advanced Usage

### Custom Prompts

Modify the SVG generation prompt for specific needs:

```python
# Edit: dev/tools/generate_svg_diagram.py
# Find: DIAGRAM_PROMPT template
# Customize: Add specific instructions

DIAGRAM_PROMPT = """
Create a Technical-Kinetic SVG diagram showing: {description}

Additional requirements:
- Isometric perspective
- Exploded view
- Detailed annotations
...
"""
```

### Batch Processing

```bash
# Generate multiple diagrams from list
cat topics.txt | while read topic category; do
  python dev/tools/generate_svg_diagram.py "$topic" "$category"
  sleep 1  # Rate limiting
done
```

### Integration with uCODE

```uscript
# .uscript automation
[SYSTEM|RUN|python dev/tools/generate_svg_diagram.py "water filter" water]
[SYSTEM|RUN|python dev/tools/generate_svg_diagram.py "fire triangle" fire]
```

---

## Performance

### Generation Time

- **Simple diagram** (1-2 elements): ~5-10 seconds
- **Medium diagram** (3-5 elements): ~10-20 seconds
- **Complex diagram** (6+ elements): ~20-40 seconds

### API Costs

Gemini API pricing (as of Nov 2025):

- **Free tier**: 60 requests/minute
- **Input**: $0.00 per 1M chars (free)
- **Output**: $0.00 per 1M chars (free for SVG)

### File Sizes

- **Simple**: 10-30 KB
- **Medium**: 30-80 KB
- **Complex**: 80-150 KB
- **Maximum**: ~200 KB (typical)

---

## Best Practices

### 1. Descriptive Names

```bash
# Good - Specific description
python dev/tools/generate_svg_diagram.py "water filter 3 stage charcoal sand gravel" water

# Bad - Too vague
python dev/tools/generate_svg_diagram.py "water thing" water
```

### 2. Appropriate Categories

Match description to category for better organization:

- Water: purification, collection, storage
- Fire: starting, management, safety
- Medical: first aid, procedures, anatomy
- Tools: assembly, usage, maintenance

### 3. Size Considerations

```bash
# Standard (800x600) - Most diagrams
python dev/tools/generate_svg_diagram.py "water filter" water

# Large (1200x800) - Complex processes
python dev/tools/generate_svg_diagram.py "shelter construction 8 steps" shelter --size 1200x800

# Square (1000x1000) - Isometric views
python dev/tools/generate_svg_diagram.py "fire triangle" fire --size 1000x1000
```

### 4. Version Control

```bash
# Generate diagram
python dev/tools/generate_svg_diagram.py "updated water filter" water

# Review changes
git diff knowledge/diagrams/water/

# Commit
git add knowledge/diagrams/water/updated-water-filter.svg
git commit -m "Add updated water filter diagram"
```

---

## See Also

- [OK Assist Integration Guide](OK-Assist-Integration.md)
- [Content Generation Guide](Content-Generation.md)
- [Technical-Kinetic Style Guide](../dev/PATTERNS-QUICK-REF.md)
- [API Reference](API-Reference.md)

---

**Last Updated**: November 25, 2025
**Version**: v1.4.0
**Maintainer**: @fredporter
