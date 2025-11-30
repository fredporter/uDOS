# Nano Banana Integration Guide

**Version:** 1.1.6
**Status:** Production Ready
**Last Updated:** November 30, 2025

## Overview

The **Nano Banana Integration** transforms uDOS's SVG generation system by replacing unreliable text-based prompting with a robust **PNG → SVG pipeline** powered by Gemini 2.5 Flash Image (Nano Banana).

> **"INSANE at generating LINE ART"** — Gemini 2.5 Flash Image excels at creating precise monochrome line art perfect for Technical-Kinetic diagrams.

## Table of Contents

1. [Architecture](#architecture)
2. [Pipeline Stages](#pipeline-stages)
3. [Commands](#commands)
4. [Style Guide System](#style-guide-system)
5. [Diagram Types](#diagram-types)
6. [Workflow Examples](#workflow-examples)
7. [Troubleshooting](#troubleshooting)
8. [Performance](#performance)

---

## Architecture

### Pipeline Overview

```
User Request
    │
    ├─→ 1. Load Style Guide (0-14 reference PNGs)
    │
    ├─→ 2. Generate PNG (Gemini 2.5 Flash Image - Nano Banana)
    │
    ├─→ 3. Vectorize (potrace/vtracer → SVG)
    │
    ├─→ 4. Validate (Technical-Kinetic compliance)
    │
    ├─→ 5. Save (Editable SVG file)
    │
    └─→ 6. Output (Success message + file path)
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Style Guide Loader** | Load reference images (max 14) | File system + caching |
| **Nano Banana** | Generate monochrome PNG | Gemini 2.5 Flash Image API |
| **Vectorizer** | Convert PNG to SVG | potrace (primary), vtracer (fallback) |
| **Validator** | Check Technical-Kinetic rules | XML parsing + custom rules |
| **File Manager** | Save and organize outputs | Path handling |

---

## Pipeline Stages

### Stage 1: Load Style Guide

**Purpose:** Provide visual references to guide Nano Banana's generation.

**Process:**
1. Check cache for previously loaded style
2. Scan `extensions/assets/styles/{style}/references/` for PNG files
3. Load up to 14 reference images
4. Cache file paths for future requests

**Code:**
```python
from core.services.gemini_generator import GeminiGenerator

gen = GeminiGenerator()
refs = gen.load_style_guide("technical-kinetic")
print(f"Loaded {len(refs)} reference images")
```

**Progressive Enhancement:**
- **0 images:** Text-based prompting (fallback)
- **1-4 images:** Basic style guidance
- **5-10 images:** Strong style consistency
- **11-14 images:** Maximum style fidelity

### Stage 2: Generate PNG

**Purpose:** Create high-quality monochrome line art PNG.

**Model Selection:**
- **Standard:** `gemini-2.0-flash-exp` (Nano Banana) — Fast, high quality
- **Pro:** `gemini-exp-1206` (Nano Banana Pro) — Multi-turn refinement, slower

**Process:**
1. Build prompt from subject + diagram type + style requirements
2. Upload reference images (if any)
3. Call Gemini API with image generation config
4. Extract PNG bytes from response
5. Return PNG data + metadata

**Code:**
```python
png_bytes, metadata = gen.generate_image_svg(
    subject="water purification filter",
    diagram_type="flowchart",
    style="technical-kinetic",
    use_pro=False  # or True for Nano Banana Pro
)
```

### Stage 3: Vectorize

**Purpose:** Convert raster PNG to editable vector SVG.

**Vectorizers:**
1. **potrace** (primary) — Industry standard, excellent quality
   - Installation: `brew install potrace` (macOS)
   - Best corner detection and path simplification
2. **vtracer** (fallback) — Python library (Rust-based)
   - Installation: `pip install vtracer>=0.6.0`
   - No system dependencies

**Process:**
1. Try potrace vectorization
2. If unavailable/fails, use vtracer
3. Apply stroke width normalization (default: 2.5px)
4. Simplify paths (reduce nodes)
5. Return SVG content + method used

**Code:**
```python
from core.services.vectorizer import get_vectorizer_service

vectorizer = get_vectorizer_service()
result = vectorizer.vectorize(
    png_bytes,
    stroke_width=2.5,
    simplify=True,
    validate_compliance=True
)

print(f"Method: {result.method}")
print(f"Paths: {result.metadata['path_count']}")
```

### Stage 4: Validate

**Purpose:** Ensure Technical-Kinetic aesthetic compliance.

**Validation Rules:**
- ✅ Valid XML (well-formed SVG)
- ✅ Monochrome only (black #000000, white #FFFFFF)
- ✅ No gradients (`<linearGradient>`, `<radialGradient>`)
- ✅ No filters (`<filter>`)
- ✅ No patterns (complex `<pattern>`)
- ✅ No raster images (`<image>`)
- ✅ Consistent stroke widths (2-3px range)

**Validation Modes:**
- **Standard:** Accept warnings, block only errors
- **Strict (`--strict`):** Block both warnings and errors

**Code:**
```python
validation = result.validation

if validation['compliant']:
    print("✅ Technical-Kinetic compliant")
else:
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")
```

### Stage 5: Save

**Purpose:** Write SVG to file system with organized naming.

**File Naming:**
```
{subject}-{style}-{timestamp}.svg
```

**Example:**
```
water-purification-filter-technical-kinetic-20251130-143022.svg
```

**Output Directory:**
```
sandbox/drafts/svg/
```

**Code:**
```python
from pathlib import Path

output_path = Path("sandbox/drafts/svg") / filename
output_path.write_text(result.svg_content, encoding='utf-8')
```

### Stage 6: Output

**Purpose:** Provide user feedback and next steps.

**Success Message Example:**
```
✅ SVG diagram generated: water purification filter
   Style: technical-kinetic
   Type: flowchart
   Vectorizer: potrace
   Time: 18.3s
   Saved: sandbox/drafts/svg/water-purification-filter-technical-kinetic-20251130-143022.svg
   Validation: ✅ Technical-Kinetic compliant

🔧 Next Steps:
   - Edit: open -a 'Inkscape' sandbox/drafts/svg/water-purification-filter-technical-kinetic-20251130-143022.svg
   - Regenerate: GENERATE SVG water purification filter --style hand-illustrative
   - Refine: GENERATE SVG water purification filter --pro --strict
```

---

## Commands

### GENERATE SVG

Generate vector diagram via Nano Banana pipeline.

**Syntax:**
```bash
GENERATE SVG <description> [options]
```

**Options:**
- `--style <style>` — Visual style (default: `technical-kinetic`)
- `--type <type>` — Diagram type (default: `flowchart`)
- `--save <file>` — Custom filename (optional)
- `--pro` — Use Nano Banana Pro (slower, higher quality)
- `--strict` — Enforce strict validation (block warnings)
- `--no-preview` — Skip preview hints

**Examples:**
```bash
# Basic generation
GENERATE SVG water filter

# Custom style
GENERATE SVG fire triangle --style hand-illustrative

# Specific type with save
GENERATE SVG shelter construction --type architecture --save shelter.svg

# Pro mode with strict validation
GENERATE DIAGRAM gear mechanism --type kinetic-flow --pro --strict
```

### GENERATE DIAGRAM

Alias for `GENERATE SVG` (identical functionality).

### GENERATE ASCII

Generate ASCII art diagram (offline, instant).

**Syntax:**
```bash
GENERATE ASCII <description> [--width <chars>] [--save <file>]
```

**Example:**
```bash
GENERATE ASCII water cycle --width 100 --save water-cycle.txt
```

### GENERATE TELETEXT

*(Not yet implemented — shows migration message to DRAW command)*

---

## Style Guide System

### Styles

| Style | Description | Use Case |
|-------|-------------|----------|
| **technical-kinetic** | MCM geometry, 2-3px strokes, monochrome | Knowledge base diagrams |
| **hand-illustrative** | Organic lines, hand-drawn feel | Educational materials |
| **hybrid** | Mix of technical + hand-drawn | Versatile applications |

### Reference Images

**Location:** `extensions/assets/styles/{style}/references/`

**Requirements:**
- **Format:** PNG
- **Resolution:** 1200×900 minimum, 300 DPI
- **Colors:** ONLY black (#000000) and white (#FFFFFF)
- **Strokes:** 2-3px consistent
- **Count:** 1-14 images (progressive enhancement)

**Technical-Kinetic Examples:**
1. `01-flowchart-clean.png` — Curved conduits, kinetic flow
2. `02-architecture-mcm.png` — MCM geometry, perfect shapes
3. `03-kinetic-flow.png` — Gears, levers, motion indicators
4. `04-hatching-pattern.png` — Vector shading patterns
5. `05-typography.png` — Sans-serif font examples
6. `06-curved-conduits.png` — Flow elements
7. `07-gears-cogs.png` — Mechanical components

**Creating Reference Images:**
1. Use vector tools (Inkscape, Illustrator)
2. Follow style constraints strictly
3. Export at 1200×900, 300 DPI
4. Save to appropriate references/ directory
5. Clear cache: Restart uDOS

---

## Diagram Types

### Flowchart

**Purpose:** Process flows, decision trees, sequential steps

**Characteristics:**
- Curved conduits (not straight lines)
- Decision diamonds
- Process rectangles
- Flow direction indicators

**Example:**
```bash
GENERATE SVG water purification process --type flowchart
```

### Architecture

**Purpose:** System architecture, MCM structures, component relationships

**Characteristics:**
- Perfect geometric shapes
- Modular components
- Clean connections
- Hierarchical layout

**Example:**
```bash
GENERATE SVG shelter frame structure --type architecture
```

### Kinetic Flow

**Purpose:** Mechanical systems, motion indicators, energy flow

**Characteristics:**
- Gears and cogs
- Levers and pivots
- Motion arrows
- Mechanical linkages

**Example:**
```bash
GENERATE SVG hand crank water pump --type kinetic-flow
```

### Schematic

**Purpose:** Technical schematics, wiring diagrams, circuit-like layouts

**Characteristics:**
- Symbolic representations
- Connection points
- Technical annotations
- Grid-based layout

**Example:**
```bash
GENERATE SVG solar still system --type schematic
```

### Additional Types

- **hatching-pattern** — Shading and texture demonstrations
- **typography** — Text layout examples
- **curved-conduits** — Pipe and flow systems
- **gears-cogs** — Mechanical component libraries

---

## Workflow Examples

### Basic Batch Generation

```uscript
# File: sandbox/workflow/batch_svg_generation.uscript

$topics = ["water purification", "fire triangle", "shelter types"]

for $topic in $topics
  PRINT "Generating: $topic"
  GENERATE SVG $topic --style technical-kinetic --no-preview
  SLEEP 3  # API rate limiting
done

PRINT "✅ Batch complete!"
```

### Quality-Validated Generation

```uscript
# Generate with validation and retry

$subject = "water filter"
$max_retries = 3
$attempt = 0
$success = false

while $attempt < $max_retries and not $success
  $attempt = $attempt + 1
  PRINT "Attempt $attempt/$max_retries"

  $result = GENERATE SVG $subject --strict --no-preview

  if $result contains "✅"
    $success = true
    PRINT "✅ Generation successful"
  else
    PRINT "⚠️ Validation failed, retrying..."
    SLEEP 5
  endif
done
```

### Knowledge Base Generation

```uscript
# File: sandbox/workflow/knowledge_diagram_generation.uscript

$categories = ["water", "fire", "shelter", "food"]

for $category in $categories
  PRINT "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  PRINT "Category: $category"

  # Generate overview
  GENERATE SVG "$category overview" --type architecture --strict

  # Generate specific diagrams
  # (category-specific logic here)

  SLEEP 5
done
```

---

## Troubleshooting

### PNG Generation Fails

**Symptom:** `❌ Failed to generate PNG from Nano Banana`

**Causes:**
1. No Gemini API key
2. Invalid API key
3. API quota exceeded
4. Network connectivity

**Solutions:**
1. Check `.env` file: `GEMINI_API_KEY=your_key_here`
2. Verify key validity in Google AI Studio
3. Check quota usage
4. Test network: `curl https://google.com`

### Vectorization Fails

**Symptom:** `❌ Failed to vectorize PNG to SVG`

**Causes:**
1. potrace not installed
2. vtracer not installed
3. Invalid PNG data
4. Corrupted image

**Solutions:**
```bash
# Install potrace
brew install potrace  # macOS
sudo apt install potrace  # Linux

# Install vtracer
pip install vtracer>=0.6.0

# Verify installation
which potrace
python -c "import vtracer"
```

### Validation Failures

**Symptom:** `❌ SVG validation failed (strict mode)`

**Causes:**
1. Non-monochrome colors
2. Gradient elements
3. Complex filters
4. Inconsistent strokes

**Solutions:**
1. Remove `--strict` flag (accept warnings)
2. Try different style: `--style hand-illustrative`
3. Regenerate with `--pro` flag
4. Manually edit SVG in Inkscape

### Slow Generation

**Symptom:** Takes >30 seconds per diagram

**Causes:**
1. Using `--pro` mode (slower but higher quality)
2. Network latency
3. API throttling

**Solutions:**
1. Remove `--pro` flag for faster generation
2. Check network speed
3. Add delays between batch requests
4. Use caching for repeated generations

---

## Performance

### Generation Time Targets

| Mode | Target | Typical |
|------|--------|---------|
| Standard | <30s | 15-20s |
| Pro (`--pro`) | <60s | 30-45s |
| ASCII | Instant | <1s |

### Optimization Tips

1. **Use Standard Mode** — Pro mode 2-3x slower
2. **Batch with Delays** — Avoid API rate limits (2-3s between)
3. **Cache Style Guides** — Loaded once, reused
4. **Install potrace** — Faster than vtracer
5. **Monitor API Quota** — Daily limits apply

### File Size Guidelines

| Diagram Complexity | SVG Size |
|-------------------|----------|
| Simple (5-10 paths) | 2-5 KB |
| Medium (10-50 paths) | 5-20 KB |
| Complex (50+ paths) | 20-100 KB |

**Optimization:**
- Simplify paths: `--simplify` (default: enabled)
- Remove metadata: Post-process with `svgo`
- Compress: `gzip` for web delivery

---

## Advanced Topics

### Custom Style Guides

**Create your own style:**

1. Create directory: `extensions/assets/styles/my-style/`
2. Add metadata: `style.json`
3. Create references: `references/*.png` (1-14 images)
4. Document: `README.md`
5. Use: `GENERATE SVG test --style my-style`

**Example `style.json`:**
```json
{
  "name": "my-style",
  "version": "1.0.0",
  "description": "Custom style description",
  "constraints": {
    "monochrome_only": true,
    "forbid_gradients": true,
    "stroke_width": 2.5,
    "resolution": "1200x900"
  }
}
```

### API Configuration

**Environment Variables:**
```bash
# .env file
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp  # Nano Banana
GEMINI_PRO_MODEL=gemini-exp-1206    # Nano Banana Pro
```

### Mission Integration

**Use in Mission Templates:**
```json
{
  "title": "Generate Knowledge Diagrams",
  "moves": [
    {
      "title": "Generate Water Diagrams",
      "steps": [
        {
          "command": "GENERATE SVG water purification --strict",
          "validation": "check for ✅"
        }
      ]
    }
  ]
}
```

---

## See Also

- [GENERATE Command Reference](SVG-Command-Reference.md)
- [Content Generation Guide](Content-Generation.md)
- [Style Guide System](Style-Guide.md)
- [uCODE Workflows](Workflows.md)
- [Graphics System](Graphics-System.md)

---

**Document Version:** 1.1.6
**Last Updated:** November 30, 2025
**Status:** Production Ready ✅
