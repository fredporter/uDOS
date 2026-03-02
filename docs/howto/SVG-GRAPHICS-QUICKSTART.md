# SVG Graphics Quickstart

Updated: 2026-03-03
Status: active how-to

## Purpose

Use this guide to generate SVG graphics from OK model prompts with the fastest path.

## Quick Start

### Local generation

```python
from wizard.services.graphics_service import SVGGenerator

gen = SVGGenerator()
svg = await gen.generate_diagram(
    description="A distributed system with 3 nodes and message flow",
    style="minimalist",
    size="800x600",
)
```

### Cloud generation

```python
svg = await gen.generate_diagram(
    description="A distributed system with 3 nodes and message flow",
    style="minimalist",
    provider="openrouter",
    model="anthropic/claude-3-opus",
)
```

## Recommended Styles

- `minimalist` for docs and architecture diagrams
- `technical` for structured diagrams and data layouts
- `artistic` for presentation-style visuals
- `cartoon` for educational or playful diagrams

## Prompt Tips

Be explicit about:
- dimensions
- line/fill constraints
- labels
- shape types
- viewBox

## Companion Guides

- [SVG Graphics Reference](/Users/fredbook/Code/uDOS/docs/howto/SVG-GRAPHICS-REFERENCE.md)
- [Offline OK Setup Quickstart](/Users/fredbook/Code/uDOS/docs/howto/OFFLINE-OK-SETUP-QUICKSTART.md)

