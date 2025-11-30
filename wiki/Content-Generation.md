# Content Generation Guide

**uDOS v1.1.6** - Automated content generation using Google Gemini (OK Assist + Nano Banana)

> **💡 Quick Start**: Generate SVG diagrams with `GENERATE SVG <description>` or guides with `OK <task>`

---

## Overview

The Content Generation system includes two powerful subsystems:

1. **GENERATE Command** (v1.1.6) - PNG→SVG pipeline for Technical-Kinetic diagrams via Nano Banana
2. **OK Assist** (v1.0.0) - Text-based content creation using Gemini API

Together they create high-quality survival guides, technical diagrams, and reference materials in multiple formats.

### Features

**GENERATE Command (v1.1.6):**
- ✅ **PNG→SVG Pipeline** - Nano Banana image generation + vectorization
- ✅ **Technical-Kinetic Diagrams** - MCM geometry, monochrome, 2-3px strokes
- ✅ **8 Diagram Types** - Flowchart, architecture, kinetic-flow, schematic, etc.
- ✅ **3 Visual Styles** - technical-kinetic, hand-illustrative, hybrid
- ✅ **Style Guide System** - 0-14 reference images for consistency
- ✅ **Dual Vectorization** - potrace (primary) + vtracer (fallback)
- ✅ **Strict Validation** - Technical-Kinetic compliance checking
- ✅ **Fast Generation** - <30s standard, <60s Pro mode

**OK Assist (v1.0.0):**
- ✅ **Content Generation** - Guides, diagrams, checklists, reference materials
- ✅ **Multi-Format Support** - Markdown, SVG, ASCII, Teletext
- ✅ **Smart Fallback** - Automatically uses placeholders when offline
- ✅ **Rate Limiting** - Prevents API quota issues (0.5s delays)
- ✅ **Quality Validation** - Ensures generated content meets standards
- ✅ **Batch Processing** - Generate multiple items efficiently

---

## Setup

### 1. Get API Key

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

## GENERATE Command (v1.1.6 - Nano Banana)

> **⚡ New in v1.1.6**: Unified generation system with PNG→SVG pipeline for production-quality diagrams.

### Quick Start

```bash
# Generate Technical-Kinetic SVG diagram
GENERATE SVG water purification filter

# Generate diagram with specific type
GENERATE DIAGRAM gear mechanism --type kinetic-flow

# Generate ASCII art (offline, instant)
GENERATE ASCII water cycle --width 100

# Pro mode (higher quality, slower)
GENERATE SVG fire triangle --pro --strict
```

### Complete Reference

**See:** [Nano Banana Integration Guide](Nano-Banana-Integration.md) for comprehensive documentation.

**Key Features:**
- **Nano Banana** - Gemini 2.5 Flash Image ("INSANE at generating LINE ART")
- **PNG→SVG Pipeline** - Style Guide → Generate PNG → Vectorize → Validate → Save
- **Technical-Kinetic** - MCM geometry, monochrome, 2-3px strokes, perfect for knowledge base
- **Style Guide System** - Load 0-14 reference PNGs for consistent style
- **Dual Vectorization** - potrace (primary) or vtracer (fallback)
- **8 Diagram Types** - flowchart, architecture, kinetic-flow, schematic, hatching-pattern, typography, curved-conduits, gears-cogs
- **3 Visual Styles** - technical-kinetic, hand-illustrative, hybrid
- **Fast** - <30s generation (standard), <60s (Pro mode)

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `GENERATE SVG <desc>` | Generate vector diagram | `GENERATE SVG water filter` |
| `GENERATE DIAGRAM <desc>` | Alias for SVG | `GENERATE DIAGRAM fire triangle` |
| `GENERATE ASCII <desc>` | ASCII art (offline) | `GENERATE ASCII water cycle --width 100` |
| `GENERATE TELETEXT` | *(Not implemented)* | Redirects to DRAW |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--style <style>` | Visual style | `technical-kinetic` |
| `--type <type>` | Diagram type | `flowchart` |
| `--save <file>` | Custom filename | Auto-generated |
| `--pro` | Use Nano Banana Pro | `false` |
| `--strict` | Enforce strict validation | `false` |
| `--no-preview` | Skip preview hints | `false` |

### Workflow Examples

**Basic Generation:**
```bash
GENERATE SVG water purification methods
GENERATE DIAGRAM shelter construction --style hand-illustrative
GENERATE SVG gear mechanism --type kinetic-flow --pro
```

**Batch Generation with Quality Validation:**
```uscript
# File: sandbox/workflow/batch_svg_generation.uscript
$topics = ["water filter", "fire triangle", "shelter types"]

for $topic in $topics
  PRINT "Generating: $topic"
  GENERATE SVG $topic --strict --no-preview
  SLEEP 3  # API rate limiting
done

PRINT "✅ Batch complete!"
```

**Knowledge Base Generation:**
```uscript
# Generate all water category diagrams
GENERATE SVG water purification overview --type architecture --strict
GENERATE SVG water collection methods --type flowchart --strict
GENERATE SVG water filter construction --type kinetic-flow --strict
GENERATE SVG water storage systems --type schematic --strict
```

### Testing

Run comprehensive test suite:

```bash
# Run all tests with coverage
python sandbox/tests/run_generate_tests.py --coverage

# Unit tests only (fast, no API)
python sandbox/tests/run_generate_tests.py --unit

# Integration tests (requires API key)
python sandbox/tests/run_generate_tests.py --integration

# Quick tests (skip slow/network tests)
python sandbox/tests/run_generate_tests.py --quick
```

### See Also

- **[Nano Banana Integration Guide](Nano-Banana-Integration.md)** - Complete pipeline documentation
- **[SVG Command Reference](SVG-Command-Reference.md)** - Legacy SVG command (deprecated in v1.1.6)
- **[Workflows](Workflows.md)** - uCODE automation examples

---

## OK Assist (v1.0.0 - Text Content)

### Content Generation

### Interactive Commands

```bash
# General task with OK Assist
OK create a water purification guide

# Ask a question
OK ASK how to start fire without matches

# Generate specific content
GENERATE guide water/purification
GENERATE diagram fire/triangle
GENERATE checklist emergency/evacuation

# Development help
OK DEV explain this code

# Read content for context
READ water-guide.md
OK ASK summarize this
```

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `OK <task>` | General AI task | `OK create shelter guide` |
| `OK ASK <question>` | Ask AI question | `OK ASK how to purify water` |
| `OK DEV <task>` | Development help | `OK DEV explain this code` |
| `READ <file>` | Load content | `READ README.md` |
| `GENERATE guide <topic>` | Create guide | `GENERATE guide water/purification` |
| `GENERATE diagram <topic>` | Create diagram | `GENERATE diagram fire/triangle` |

### Guides

OK Assist creates comprehensive survival guides (800-1200 words):

```bash
# Generate via uDOS command
GENERATE guide water/purification

# Generate via Python script
python dev/tools/generate_content_v1_4_0.py --category water --count 5 --guides-only
```

**Guide Structure:**
- Detailed step-by-step instructions
- Safety warnings and considerations
- Materials lists
- Common mistakes to avoid
- Related topics for cross-referencing
- Proper markdown formatting

**Example Output:**
```markdown
# Water Purification Methods

## Overview
Water purification is essential for survival...

## Methods

### 1. Boiling
Boiling water is the most reliable method...

**Materials Needed:**
- Heat source
- Container
- Time: 1-5 minutes

**Steps:**
1. Collect water source
2. Bring to rolling boil
3. Boil for 1 minute (3 minutes at altitude)
...
```

### Diagrams

OK Assist generates Technical-Kinetic compliant SVG diagrams:

```bash
# Generate SVG diagram
python dev/tools/generate_svg_diagram.py "water filter 3 stages" water

# Batch generate diagrams
python dev/tools/generate_content_v1_4_0.py --category fire --count 3 --diagrams-only
```

**Diagram Features:**
- Technical-Kinetic style (monochrome + patterns)
- Polaroid 8-color palette
- Clear labels and annotations
- Step-by-step visual process
- 800x600 viewBox (standard)
- Mallard font embedded

### Batch Generation

```bash
# Generate guides and diagrams for category
python dev/tools/generate_content_v1_4_0.py --category water --count 10

# Generate all categories
python dev/tools/generate_content_v1_4_0.py --all

# Dry run (preview without generating)
python dev/tools/generate_content_v1_4_0.py --category shelter --count 5 --dry-run

# Force placeholder mode (no API)
python dev/tools/generate_content_v1_4_0.py --category food --count 5 --no-ai
```

---

## SVG Diagram Generation

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

### Examples

**Medical Diagrams:**
```bash
# Basic tourniquet application
python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical

# CPR technique
python dev/tools/generate_svg_diagram.py "CPR hand placement adult" medical --size 1000x800

# Custom filename
python dev/tools/generate_svg_diagram.py "wound dressing steps" medical -o wound-care.svg
```

**Water Diagrams:**
```bash
# Water purification
python dev/tools/generate_svg_diagram.py "water filter charcoal sand gravel" water

# Advanced filter
python dev/tools/generate_svg_diagram.py "solar still water collection" water -o solar-still.svg
```

**Fire Diagrams:**
```bash
# Fire triangle
python dev/tools/generate_svg_diagram.py "fire triangle heat fuel oxygen" fire

# Bow drill
python dev/tools/generate_svg_diagram.py "bow drill fire starting assembly" fire --size 1200x900
```

### Output Location

Generated diagrams are saved to:
```
knowledge/diagrams/{category}/{auto-generated-name}.svg
```

**Examples:**
```
knowledge/diagrams/medical/tourniquet-application-6-steps.svg
knowledge/diagrams/water/water-filter-charcoal-sand-gravel.svg
knowledge/diagrams/fire/fire-triangle-heat-fuel-oxygen.svg
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

## Content Quality

### OK Assist Generated Content

**Guides:**
- 800-1200 word target length
- Practical, survival-focused
- Step-by-step instructions
- Safety warnings included
- Related topics linked
- Proper markdown formatting

**Diagrams:**
- Technical-Kinetic compliance
- Polaroid palette only
- Clear visual hierarchy
- Annotated components
- Standard 800x600 size
- Embedded custom font

### Quality Validation

The system automatically validates:

1. **Content length** - Meets word count targets
2. **Formatting** - Proper markdown structure
3. **Completeness** - All sections present
4. **Style compliance** - Follows uDOS standards
5. **SVG validity** - Well-formed XML for diagrams

---

## Operating Modes

### OK Assist Mode (Default)

Uses Gemini API when key is configured:

```bash
# Check mode
python dev/tools/generate_content_v1_4_0.py --category water --count 1

# Output shows:
# ✅ OK Assistant initialized for content generation
```

**Features:**
- High-quality content
- Natural language understanding
- Context-aware generation
- Multi-format support
- Rate limiting (0.5s delays)

### Placeholder Mode

Automatically activates when no API key:

```bash
# Force placeholder mode
python dev/tools/generate_content_v1_4_0.py --category shelter --count 10 --no-ai
```

**Features:**
- Structure-only content
- Placeholder text
- Proper formatting
- Quick generation
- No API quota usage

**Use cases:**
- Testing structure
- Offline development
- Template creation
- Architecture verification

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

The SVG generator uses OK Assist directly:

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
cat sandbox/logs/udos.log | tail -50
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

### Gemini API Costs

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

## Rate Limiting

OK Assist implements automatic rate limiting to prevent quota issues:

### Default Delays

- **Between API calls**: 0.5 seconds
- **After rate limit error**: 60 seconds
- **Batch generation**: Automatic pacing

### Configuration

```python
# Adjust delay (in code)
from extensions.core.ok-assist.ok_assistant import OKAssistant

ok = OKAssistant(
    api_key=GEMINI_API_KEY,
    delay_between_calls=0.5  # Seconds between API calls
)
```

### Quota Management

**Free tier limits (Gemini):**
- 60 requests per minute
- 1,500 requests per day
- Input: Free
- Output: Free

**Best practices:**
- Use batch generation with delays
- Monitor quota at [Google Cloud Console](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)
- Implement exponential backoff for errors

---

## Statistics Tracking

The content generation tool tracks:

```bash
# Generate with statistics
python dev/tools/generate_content_v1_4_0.py --category water --count 10

# Output:
# ============================================================
# CONTENT GENERATION SUMMARY
# ============================================================
#
# Guides Generated:     10
# Diagrams Generated:   10
# Total API Calls:      20
# Errors:               0
# Skipped (exist):      0
# Mode:                 OK Assist
#
# Time Elapsed:         45.3 seconds
# Average per item:     2.27 seconds
# ============================================================
```

---

## Advanced Usage

### Custom Prompts

```python
from extensions.core.ok-assist.ok_assistant import OKAssistant

ok = OKAssistant(api_key=GEMINI_API_KEY)

# Custom guide generation
guide = ok.generate_guide(
    topic="Advanced water purification",
    style="technical",
    context="survival",
    word_count=1500
)

# Custom diagram generation
diagram = ok.generate_diagram(
    description="Solar still construction 8 steps",
    style="technical-kinetic",
    format="svg",
    size="1200x800"
)
```

### Integration with uCODE

```uscript
---
title: Content Generation Workflow
version: 1.0.0
---

# Generate water content
[GENERATE|guide|water/purification]
[GENERATE|diagram|water/filter|format=svg]

# Generate fire content
[GENERATE|guide|fire/starting]
[GENERATE|diagram|fire/triangle|format=svg]

# Validate generated content
[REFRESH|--check|all]
```

### Batch Processing

```bash
# Generate all categories sequentially
for cat in water fire shelter food medical navigation tools communication; do
  python dev/tools/generate_content_v1_4_0.py --category $cat --count 5
  sleep 10  # Pause between categories
done

# Generate from topic list
cat topics.txt | while read topic category; do
  python dev/tools/generate_svg_diagram.py "$topic" "$category"
  sleep 1
done
```

---

## Performance

### Generation Times

**Guides:**
- Simple (500 words): ~3-5 seconds
- Medium (800 words): ~5-8 seconds
- Complex (1200+ words): ~8-12 seconds

**Diagrams:**
- Simple (1-2 elements): ~5-10 seconds
- Medium (3-5 elements): ~10-20 seconds
- Complex (6+ elements): ~20-40 seconds

### API Costs

Gemini API pricing (as of Nov 2025):

- **Free tier**: 60 requests/minute
- **Input**: $0.00 per 1M chars (free)
- **Output**: $0.00 per 1M chars (free for SVG)

### File Sizes

**Guides:**
- Simple: 5-15 KB
- Medium: 15-40 KB
- Complex: 40-80 KB

**Diagrams:**
- Simple: 10-30 KB
- Medium: 30-80 KB
- Complex: 80-150 KB
- Maximum: ~200 KB (typical)

### Optimization Tips

1. **Batch generation** - More efficient than individual calls
2. **Appropriate delays** - 0.5s prevents rate limiting
3. **Parallel categories** - Generate different categories concurrently
4. **Cache results** - Store generated content for reuse
5. **Dry run first** - Preview before generating

---

## Error Handling

### Common Errors

**API Key Not Found:**
```
ERROR: GEMINI_API_KEY not found in environment
```

**Solution:**
```bash
# Check .env file
cat .env | grep GEMINI_API_KEY

# Set via command
CONFIG SET GEMINI_API_KEY your_key_here

# Verify
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Rate Limit Exceeded:**
```
ERROR: Rate limit exceeded. Please wait.
```

**Solution:**
```bash
# Wait 60 seconds
sleep 60

# Use batch generation (automatic delays)
python dev/tools/generate_content_v1_4_0.py --category water --count 5

# Monitor quota usage
# Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
```

**Invalid API Response:**
```
ERROR: Failed to generate content
```

**Solution:**
```bash
# Check API key validity
python extensions/core/ok-assist/examples/test_quick.py

# Try simpler prompt
OK ASK test

# Check logs
cat sandbox/logs/udos.log | tail -50
```

---

## Validation

### Automatic Checks

The generator validates:

1. **Content syntax** - Well-formed markdown/SVG
2. **Pattern definitions** - All patterns defined in `<defs>` (SVG)
3. **Font embedding** - Mallard font included (SVG)
4. **Dimensions** - Correct viewBox and size (SVG)
5. **Style compliance** - Monochrome, pattern-based (SVG)
6. **Word count** - Meets targets (guides)

### Manual Inspection

**For Guides:**
```bash
# View generated guide
cat knowledge/water/purification-methods.md

# Check word count
wc -w knowledge/water/purification-methods.md
```

**For Diagrams:**
```bash
# View generated SVG
cat knowledge/diagrams/water/water-filter.svg

# Validate XML syntax
xmllint --noout knowledge/diagrams/water/water-filter.svg

# Check file size
ls -lh knowledge/diagrams/water/water-filter.svg
```

---

## Testing

### Unit Tests

```bash
# Test OK Assist integration
pytest extensions/core/ok-assist/tests/

# Test content generation
pytest dev/tools/tests/test_content_generation.py

# Test SVG generation
pytest dev/tools/tests/test_svg_generator.py
```

### Integration Tests

```bash
# Quick test
python extensions/core/ok-assist/examples/test_quick.py

# Generate single guide
python dev/tools/generate_content_v1_4_0.py --category water --count 1 --guides-only

# Generate single diagram
python dev/tools/generate_svg_diagram.py "simple test" water
```

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
# Generate content
python dev/tools/generate_content_v1_4_0.py --category water --count 5

# Review changes
git diff knowledge/

# Commit
git add knowledge/water/ knowledge/diagrams/water/
git commit -m "Add water purification guides and diagrams"
```

---

## Design Patterns & Templates

This section contains ASCII diagram templates, UI mockups, and system architecture patterns to guide content generation. Use these as references when creating new diagrams, documentation, or interface designs.

### UI Mockup Templates

#### Viewport Tier Adaptation

uDOS adapts to 15 screen tiers (0-14). Here are example layouts:

**Tier 0: Minimal Terminal (40×12)**
```
┌──────────────────────────────────────┐
│uDOS v1.0.0            [TIER 0]    OK│
├──────────────────────────────────────┤
│> GUIDE LIST                          │
│                                      │
│Guides (12):                          │
│1. Water Purification                 │
│2. Knot Tying                         │
│3. Fire Starting                      │
│                                      │
│Use: GUIDE START <name>               │
└──────────────────────────────────────┘
```

**Tier 5: Standard Terminal (80×24)**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│  uDOS v1.0.0 - Offline-First Operating System              [Tier 5] [80×24]  │
├──────────────────────────────────────────────────────────────────────────────┤
│  > GUIDE LIST                                                                │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  Available Guides (12)                                               ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  1. Water Purification Methods          [Survival] [Beginner]       ║   │
│  ║  2. Knot Tying Techniques                [Skills]   [Beginner]      ║   │
│  ║  3. Fire Starting Without Matches        [Survival] [Intermediate]  ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  Commands: GUIDE START <name> | GUIDE SEARCH <query> | HELP GUIDE           │
├──────────────────────────────────────────────────────────────────────────────┤
│  [HELP] [BACK] [QUIT]                                              [Grid:--] │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Tier 10: Wide Terminal (120×40)** - Split-pane layouts with previews, progress tracking, and rich metadata.

#### Common Interface Patterns

**Command Palette**
```
┌──────────────────────────────────────────────────────────────┐
│  Command Palette                             [Ctrl+P]        │
├──────────────────────────────────────────────────────────────┤
│  > gui_                                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ GUIDE                Interactive guide viewer          │ │
│  │ GUIDE LIST           List all available guides         │ │
│  │ GUIDE SEARCH         Search guides by keyword          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Recent Commands:                                            │
│    • GUIDE START water-purification                          │
│    • DOC configuration                                       │
├──────────────────────────────────────────────────────────────┤
│  [ESC] Close  [↑↓] Navigate  [ENTER] Execute                 │
└──────────────────────────────────────────────────────────────┘
```

**Progress Indicators**
```
1. Linear Progress Bar (Determinate)
   Loading knowledge base...
   [████████████████░░░░░░░░░░░░] 60% (300/500 guides)

2. Multi-stage Progress
   ┌────────────────────────────────────────────────────────┐
   │ Stage 1: Scanning files    [████████████████████] 100% │
   │ Stage 2: Building index    [████████░░░░░░░░░░░░]  45% │
   │ Stage 3: Validating data   [░░░░░░░░░░░░░░░░░░░░]   0% │
   └────────────────────────────────────────────────────────┘

3. Step Progress
   Installation: Step 3 of 5
   ● Validate → ● Extract → ◉ Configure → ○ Test → ○ Complete
```

**Status Bar Variations**
```
1. Minimal (Tier 0-4)
   [OK] [Tier2]

2. Standard (Tier 5-9)
   [HELP] [BACK] [QUIT]                    [Grid: AA001] [Tier5]

3. Informational (Tier 10+)
   [F1:Help] [F2:Save] [F3:Load] [Esc:Quit]  Grid:AA001  Time:14:30  OK
```

### ASCII Diagram Templates

#### Survival Diagrams

**Fire Triangle**
```
              OXYGEN
                 △
                ╱ ╲
               ╱   ╲
              ╱     ╲
             ╱  FIRE ╲
            ╱    🔥   ╲
           ╱___________╲
        HEAT          FUEL
```

**Water Filter (3-Stage)**
```
    ┌─────────────┐
    │   INPUT     │  ← Dirty water
    │   WATER     │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  CHARCOAL   │  ← Stage 1: Remove odor
    │  LAYER      │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   SAND      │  ← Stage 2: Filter particles
    │   LAYER     │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   GRAVEL    │  ← Stage 3: Final filtration
    │   LAYER     │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   CLEAN     │  ← Potable water
    │   WATER     │
    └─────────────┘
```

**Knot Diagrams**
```
BOWLINE (King of Knots)        SQUARE KNOT
    ╭─────╮                       ═══╮   ╭═══
    │     │                          ╰─X─╯
    │  ⌒  │                          ╭─X─╮
════╰─────╯                       ═══╯   ╰═══
```

#### System Architecture Patterns

**Command Pipeline Flow**
```
User Input
    ↓
┌─────────────┐
│   Parser    │  Tokenize + validate
└──────┬──────┘
       ↓
┌─────────────┐
│   Router    │  Find handler
└──────┬──────┘
       ↓
┌─────────────┐
│  Handler    │  Execute logic
└──────┬──────┘
       ↓
┌─────────────┐
│  Viewport   │  Format output
└──────┬──────┘
       ↓
Terminal Output
```

**Hierarchy Trees**
```
uDOS Commands (80+)
│
├── File Management
│   ├── LOAD          Load files
│   ├── SAVE          Save files
│   └── FILES         List directory
│
├── Knowledge Access
│   ├── GUIDE         Interactive guides
│   ├── DIAGRAM       ASCII diagrams
│   └── DOC           Documentation
│
└── System & Configuration
    ├── CONFIG        Settings
    └── STATUS        System info
```

**Data Flow Diagrams**
```
┌────────────────────────────────────────┐
│ 1. PARSE COMMAND                       │
│    ┌───────────────────────────────┐  │
│    │ Command: LOAD                 │  │
│    │ Args: ["data/guide.md"]       │  │
│    └───────────────────────────────┘  │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ 2. EXECUTE                             │
│    ┌───────────────────────────────┐  │
│    │ Read file                     │  │
│    │ Process content               │  │
│    └───────────────────────────────┘  │
└──────────────────┬─────────────────────┘
                   │
                   ▼
              [Output]
```

### Concept Map Templates

**Learning Paths**
```
                    Beginner
                    ┌──────┐
                    │ Start│
                    └───┬──┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    Terminal        Knowledge       Scripting
    ┌──────┐        ┌──────┐        ┌──────┐
    │ HELP │        │GUIDE │        │ RUN  │
    └───┬──┘        └───┬──┘        └───┬──┘
        │               │               │
        ▼               ▼               ▼
    Intermediate    Intermediate    Intermediate
```

**Feature Dependencies**
```
Core Features
┌─────────────────────────────────┐
│  File System + Command Parser   │
└───────────┬─────────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌─────────┐
│Viewport │   │ Theme   │
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            │
            ▼
    ┌──────────────┐
    │   Graphics   │
    └──────────────┘
```

### Design Principles

When creating diagrams and interfaces:

1. **Clarity**: Information hierarchy should be obvious
2. **Consistency**: Similar functions use similar layouts
3. **Adaptability**: Works across viewport tiers (0-14)
4. **Efficiency**: Minimal keystrokes to common actions
5. **Accessibility**: ASCII-only, works on any terminal

**Box Drawing Characters**: Use Unicode box-drawing for borders
- `┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼` for single lines
- `╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬` for double lines
- `│ ─ ═ ║` for lines

**Block Characters**: Use for visual elements
- `█ ▓ ▒ ░` for shading/terrain
- `▀ ▄ ▌ ▐` for partial blocks
- `▘ ▝ ▖ ▗ ▚ ▞` for patterns

**Arrows & Symbols**:
- `→ ← ↑ ↓ ↔ ↕` for directional flow
- `▶ ◀ ▲ ▼` for playback/navigation
- `● ○ ◉ ◎` for bullets/states
- `✓ ✗ ⚠ ⚡` for status indicators

---

## See Also

- [Command Reference](Command-Reference.md) - All uDOS commands
- [uCODE Language](uCODE-Language.md) - Scripting and automation
- [Content Curation](Content-Curation.md) - Knowledge management
- [Developers Guide](Developers-Guide.md) - Complete developer documentation

---

**Last Updated**: November 26, 2025
**Version**: v1.0.0
**Maintainer**: @fredporter
