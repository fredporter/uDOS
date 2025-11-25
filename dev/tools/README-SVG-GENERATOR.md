# SVG Diagram Generator - Quick Reference

## One-Line Setup

```bash
cd /Users/fredbook/Code/uDOS && echo 'GEMINI_API_KEY=your_key' > .env
```

## One-Line Usage

```bash
.venv/bin/python dev/tools/generate_svg_diagram.py "DESCRIPTION" CATEGORY
```

## Examples

```bash
# Medical
.venv/bin/python dev/tools/generate_svg_diagram.py "tourniquet application 6 steps" medical

# Water
.venv/bin/python dev/tools/generate_svg_diagram.py "multi-stage water filter" water

# Fire
.venv/bin/python dev/tools/generate_svg_diagram.py "bow drill assembly" tools

# Custom size
.venv/bin/python dev/tools/generate_svg_diagram.py "CPR positioning" medical --size 1200x800
```

## Categories

- `water` - Water procurement, purification, storage
- `fire` - Fire starting, structures, safety
- `shelter` - Shelter building, knots, lashing
- `food` - Food foraging, preservation, cooking
- `navigation` - Maps, compasses, signaling
- `medical` - First aid, procedures, anatomy
- `tools` - Tool usage, maintenance, construction
- `communication` - Signals, radio, messaging

## Output Location

```
knowledge/diagrams/{category}/{auto-generated-filename}.svg
```

## Full Documentation

See: `dev/tools/SVG-GENERATOR-GUIDE.md`
