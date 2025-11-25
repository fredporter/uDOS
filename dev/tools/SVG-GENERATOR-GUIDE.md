# SVG Diagram Generator (Gemini API)

Automated generation of Technical-Kinetic compliant SVG diagrams using Google's Gemini API.

## Features

- ✅ **Full Gemini API Integration** - Generates complete SVG diagrams from text descriptions
- ✅ **Technical-Kinetic Compliance** - Enforces monochrome, pattern-based styling
- ✅ **Mallard Font Embedding** - Auto-includes custom uDOS font
- ✅ **Pattern Library** - 12 pre-defined patterns (grayscale + textures)
- ✅ **Automatic Validation** - Checks compliance with uDOS standards
- ✅ **Material Detection** - Smart pattern assignment based on content

## Quick Start

### 0. Setup (First Time Only)

1. **Create `.env` file in project root:**

```bash
cd /Users/fredbook/Code/uDOS

# Create .env file with your Gemini API key
echo 'GEMINI_API_KEY=your_actual_api_key_here' > .env
```

2. **Get Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create/copy your API key
   - Replace `your_actual_api_key_here` in .env file

3. **Verify setup:**

```bash
# Check .env file exists
ls -la .env

# Check key is set (should show GEMINI_API_KEY=...)
cat .env | grep GEMINI
```

### 1. Generate a Diagram

```bash
cd /Users/fredbook/Code/uDOS

# Activate virtual environment
source .venv/bin/activate

# Basic usage
python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical

# OR use full path without activation
.venv/bin/python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical

# Custom size
python dev/tools/generate_svg_diagram.py "bow drill assembly" tools --size 1200x800

# Custom filename
python dev/tools/generate_svg_diagram.py "water filter" water -o advanced-filter.svg
```

### 2. Output Location

Generated diagrams are saved to:
```
knowledge/diagrams/{category}/{auto-generated-name}.svg
```

Example:
```
knowledge/diagrams/medical/tourniquet-application-6-steps.svg
knowledge/diagrams/tools/bow-drill-assembly.svg
knowledge/diagrams/water/advanced-filter.svg
```

## Command-Line Options

```bash
python dev/tools/generate_svg_diagram.py [OPTIONS] DESCRIPTION CATEGORY

Arguments:
  DESCRIPTION    What to draw (e.g., "CPR hand placement adult")
  CATEGORY       water | fire | shelter | food | navigation | medical | tools | communication

Options:
  --size, -s     Diagram dimensions (default: 800x600)
                 Format: WIDTHxHEIGHT (e.g., 1200x800, 800x600)

  --output, -o   Custom filename (auto-generated if omitted)
                 Example: my-custom-diagram.svg

  --env          Path to .env file with GEMINI_API_KEY
                 Default: auto-detects from project root

  --help, -h     Show help message
```

## Examples

### Medical Diagrams

```bash
# Tourniquet application
python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps with pressure points" medical

# CPR positioning
python dev/tools/generate_svg_diagram.py "CPR hand placement adult child infant comparison" medical --size 1200x600

# First aid kit layout
python dev/tools/generate_svg_diagram.py "first aid kit organization 72 hour emergency" medical
```

### Water Diagrams

```bash
# Filtration system
python dev/tools/generate_svg_diagram.py "DIY water filter layers sand charcoal gravel" water

# Purification methods
python dev/tools/generate_svg_diagram.py "water purification comparison boiling chemical UV" water --size 1200x800

# Collection techniques
python dev/tools/generate_svg_diagram.py "rainwater catchment system rooftop gutters storage" water
```

### Fire Diagrams

```bash
# Fire structures
python dev/tools/generate_svg_diagram.py "fire lay types teepee log cabin lean-to comparison" fire

# Bow drill mechanics
python dev/tools/generate_svg_diagram.py "bow drill assembly exploded view with parts labeled" fire

# Safety zones
python dev/tools/generate_svg_diagram.py "campfire safety zones clearance distance wind direction" fire
```

### Shelter Diagrams

```bash
# Construction sequence
python dev/tools/generate_svg_diagram.py "debris hut construction 5 phases framework to completion" shelter

# Knot techniques
python dev/tools/generate_svg_diagram.py "essential 8 knots bowline clove hitch square knot" shelter --size 1200x800

# Lashing methods
python dev/tools/generate_svg_diagram.py "tripod lashing step by step 3D view" shelter
```

## Technical-Kinetic Standards

The generator enforces these requirements:

### ✅ Required Elements

- Monochrome only (black #000, white #FFF)
- Pattern-based grayscale (gray-10 through gray-90)
- Mallard font with @font-face embedding
- Material-appropriate patterns:
  - Metal/tools → `hatch` or `cross-hatch`
  - Skin/fabric → `stipple`
  - Wood/organic → `waves`
  - Water/terrain → `topo`
  - Backgrounds → `gray-10` to `gray-90`
- Editable `<text>` elements (not paths)
- `<title>` and `<desc>` for accessibility
- File size under 50KB

### ❌ Forbidden

- Solid gray fills (#808080, #999999, etc.)
- Opacity manipulation for toning
- Colors beyond black/white
- Arial/Helvetica without Mallard fallback
- Text converted to paths
- Embedded raster images
- File size over 50KB

## Validation

After generation, the script automatically validates:

1. **Pattern Usage** - Checks for forbidden solid grays
2. **Opacity** - Ensures no opacity manipulation
3. **Colors** - Validates monochrome compliance
4. **Font** - Confirms Mallard font usage
5. **Accessibility** - Checks for title/desc elements
6. **Structure** - Validates viewBox attribute

Example validation output:
```
🔍 Validating Technical-Kinetic compliance...
   ✅ All compliance checks passed!
```

Or with issues:
```
🔍 Validating Technical-Kinetic compliance...

❌ COMPLIANCE ISSUES FOUND (2):
   ❌ Found solid gray fills (e.g., #808080) - use pattern fills instead
   ❌ Missing Mallard font - add font-family="Mallard, Arial, sans-serif"

💡 Fix these issues before using in production
   Review: knowledge/diagrams/medical/tourniquet-application-6-steps.svg
```

## Pattern Library Reference

### Grayscale Patterns (Density-Based)
- `gray-10` - 10% black (very light stipple)
- `gray-25` - 25% black (light stipple)
- `gray-40` - 40% black (medium stipple)
- `gray-50` - 50% black (cross-hatch)
- `gray-60` - 60% black (dense stipple)
- `gray-75` - 75% black (very dense cross-hatch)
- `gray-90` - 90% black (near-black reverse stipple)

### Texture Patterns (Material-Based)
- `hatch` - Diagonal lines (metal/mechanical)
- `cross-hatch` - Crossed lines (dense materials)
- `stipple` - Dots (soft/atmospheric)
- `waves` - Wavy lines (organic/natural)
- `topo` - Undulating lines (water/terrain)

### Solid Fills
- `#000` or `solid-black` - High contrast elements
- `#FFF` - Background/negative space

## Workflow Integration

### 1. Generate Batch Diagrams

Create a batch script:

```bash
#!/bin/bash
# generate_medical_diagrams.sh

python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical
python dev/tools/generate_svg_diagram.py "CPR hand placement adult" medical
python dev/tools/generate_svg_diagram.py "recovery position sequence" medical
python dev/tools/generate_svg_diagram.py "bleeding control pressure points" medical
python dev/tools/generate_svg_diagram.py "shock treatment positioning" medical
```

### 2. Update Progress Tracking

After generating diagrams, update `knowledge/diagrams/README.md`:

```markdown
### Medical Procedures (Target: 80 diagrams, Current: 20, 25.0%)
**Location:** `knowledge/diagrams/medical/`

**Completed:**
- Tourniquet application (6 steps)
- CPR hand placement (adult)
- Recovery position sequence
- Bleeding control pressure points
- Shock treatment positioning
```

### 3. Link from Guides

Reference diagrams in relevant guides:

```markdown
## Tourniquet Application

See diagram: [Tourniquet Application (6 Steps)](../diagrams/medical/tourniquet-application-6-steps.svg)

1. **Position the tourniquet** 2-3 inches above the wound...
```

## Troubleshooting

### Error: "GEMINI_API_KEY not found"

Create `.env` file in **project root** (not in core/ or dev/):

```bash
cd /Users/fredbook/Code/uDOS

# Create .env in project root
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env

# Verify location (should show: /Users/fredbook/Code/uDOS/.env)
pwd
ls -la .env
```

Get API key from: https://makersuite.google.com/app/apikey

**Note:** The .env file must be in the uDOS project root directory, not in subdirectories.

### Error: "Invalid size format"

Use WIDTHxHEIGHT format:
```bash
# ✅ Correct
--size 800x600
--size 1200x800

# ❌ Wrong
--size 800,600
--size 800 600
```

### Warning: "File size exceeds 50KB"

The diagram is too complex. Simplify by:
1. Reducing detail/annotations
2. Using fewer pattern variations
3. Simplifying shapes/paths
4. Removing unnecessary groups

### Validation Issues

If compliance checks fail:
1. Review the generated SVG file
2. Manually fix issues (replace solid grays with patterns)
3. Re-run validation or regenerate with more specific prompt

## Advanced Usage

### Custom Prompts

For more control, modify the description:

```bash
# Specify exact layout
python dev/tools/generate_svg_diagram.py \
  "tourniquet application: 2 rows of 3 panels each, numbered 1-6, with arrows showing sequence, include anatomical cross-section showing artery compression" \
  medical --size 1200x600

# Specify pattern usage
python dev/tools/generate_svg_diagram.py \
  "bow drill: exploded view with hatching pattern for wooden components, stipple for cordage, label all 5 parts" \
  tools
```

### Multiple Sizes

Generate the same diagram at different sizes:

```bash
# Standard 4:3
python dev/tools/generate_svg_diagram.py "fire triangle diagram" fire --size 800x600 -o fire-triangle-standard.svg

# Wide 16:9
python dev/tools/generate_svg_diagram.py "fire triangle diagram" fire --size 1200x675 -o fire-triangle-wide.svg

# Square
python dev/tools/generate_svg_diagram.py "fire triangle diagram" fire --size 800x800 -o fire-triangle-square.svg
```

## Next Steps

After generating diagrams:

1. **Review Quality** - Check technical accuracy and clarity
2. **Fix Compliance** - Address any validation warnings
3. **Optimize Size** - Minify if over 50KB
4. **Link Content** - Reference from guides
5. **Update Tracking** - Increment progress counters in README
6. **Commit Changes** - Add to git repository

## Resources

- **Style Guide**: `knowledge/diagrams/README.md`
- **Pattern Examples**: `knowledge/diagrams/water/water-purification-multi-barrier-monochrome.svg`
- **Gemini Service**: `core/services/gemini_service.py`
- **Mallard Fonts**: `extensions/assets/fonts/mallard/`

## Support

For issues or questions:
1. Check validation output for specific errors
2. Review Technical-Kinetic guidelines in diagram README
3. Examine existing compliant diagrams for reference
4. Regenerate with more specific description
