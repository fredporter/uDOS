# uDOS Graphics Template Library

**Version:** 1.2.15  
**Date:** December 2025  
**Format Support:** ASCII, Teletext, SVG, Sequence, Flow

## Overview

This directory contains the complete template library for uDOS graphics system. All templates are designed for offline use and optimized for terminal/text-based rendering.

## Directory Structure

```
diagrams/
├── ascii/          # 25 ASCII art templates
├── teletext/       # 4 color palettes (8-color system)
├── svg/            # 3 base styles (technical, simple, detailed)
├── sequence/       # 5 sequence diagram templates (js-sequence)
└── flow/           # 5 flowchart templates (flowchart.js)
```

## Format Details

### ASCII Templates (25 files)

**Flowcharts (2):**
- `flowchart_vertical.txt` - Vertical decision flow
- `flowchart_horizontal.txt` - Linear process flow

**System Diagrams (2):**
- `system_components.txt` - Component architecture
- `system_layers.txt` - Layered architecture

**Progress Indicators (2):**
- `progress_bar.txt` - Visual progress bars
- `progress_steps.txt` - Step-by-step progress

**Funnels (2):**
- `funnel_conversion.txt` - Conversion funnel
- `funnel_sales.txt` - Sales funnel

**Timelines (3):**
- `timeline_horizontal.txt` - Horizontal timeline
- `timeline_vertical.txt` - Vertical timeline
- `timeline_gantt.txt` - Gantt chart style

**Decision Trees (2):**
- `decision_tree.txt` - Hierarchical tree
- `decision_binary.txt` - Binary decision

**Organization Charts (2):**
- `org_chart.txt` - Hierarchical org chart
- `org_flat.txt` - Flat organization

**Network Diagrams (3):**
- `network_star.txt` - Star topology
- `network_mesh.txt` - Mesh network
- `network_hierarchy.txt` - Hierarchical network

**Data Visualization (2):**
- `table_simple.txt` - Basic table
- `matrix_grid.txt` - Matrix/grid layout

**UI Elements (3):**
- `box_callout.txt` - Callout boxes
- `banner_header.txt` - Headers/banners
- `icon_symbols.txt` - Common symbols

**Process Diagrams (2):**
- `cycle_process.txt` - Cyclical process
- `arrow_process.txt` - Linear process with arrows

### Teletext Palettes (4 files)

All palettes use 8-color teletext standard:

- `palette_classic.json` - High-contrast primary colors
- `palette_earth.json` - Warm earthy tones for survival content
- `palette_terminal.json` - Classic green phosphor CRT
- `palette_amber.json` - Vintage amber CRT aesthetic

Each palette defines: background, foreground, and 8 standard colors (black, red, green, yellow, blue, magenta, cyan, white).

### SVG Styles (3 files)

- `style_technical.json` - Clean technical diagrams, precise lines, blue/orange accents
- `style_simple.json` - Minimalist black/white, print-friendly
- `style_detailed.json` - Rich colors, gradients, presentation-quality

Each style defines: fonts, colors, shapes, line widths, spacing.

### Sequence Diagrams (5 files)

Uses js-sequence syntax for actor-based message flows:

- `message_flow.txt` - Basic sequential messaging
- `api_request.txt` - REST API request/response
- `error_handling.txt` - Error conditions and fallbacks
- `multi_system.txt` - Complex multi-service interactions
- `async_process.txt` - Asynchronous job processing

### Flowcharts (5 files)

Uses flowchart.js syntax for decision trees and logic flows:

- `decision_flow.txt` - Simple branching logic
- `login_process.txt` - User authentication flow
- `data_pipeline.txt` - Multi-stage data processing
- `business_logic.txt` - Complex multi-branch decisions
- `error_recovery.txt` - Retry logic with fallbacks

## Usage with MAKE Command

```bash
# ASCII diagrams (direct rendering)
MAKE --format ascii --template flowchart_vertical --output my_flow.txt

# Teletext pages (with color palette)
MAKE --format teletext --palette earth --output survival_guide.txt

# SVG diagrams (AI-assisted with style)
MAKE --format svg --style technical "system architecture diagram"

# Sequence diagrams (js-sequence rendering)
MAKE --format sequence --template api_request --output login_flow.svg

# Flowcharts (flowchart.js rendering)
MAKE --format flow --template decision_flow --output process.svg
```

## Template Modification

Templates can be edited directly:
- ASCII templates: Plain text files with box-drawing characters
- Teletext palettes: JSON files with hex color codes
- SVG styles: JSON files with style definitions
- Sequence/Flow: Text files with domain-specific syntax

All modifications are immediately available to the MAKE command.

## Size Limits (Schema v1.2.15)

- ASCII: 5KB max
- Teletext: 10KB max
- SVG: 50KB max
- Sequence: 5KB max
- Flow: 5KB max

Enforced by config system to ensure terminal compatibility.

## Credits

**v1.2.15 Template Library** (December 2025)
- 25 ASCII templates from graphics2.md specification
- 4 teletext palettes (8-color standard)
- 3 SVG base styles (technical/simple/detailed)
- 5 sequence templates (js-sequence)
- 5 flowchart templates (flowchart.js)

**Built on v1.2.12 Foundation:**
- PATHS constants for reliable path resolution
- Standardized folder structure
- .archive/ backup system integration

## See Also

- `wiki/Graphics-System.md` - Complete graphics system documentation
- `wiki/ASCII-Graphics-Guide.md` - ASCII template syntax
- `wiki/Teletext-Graphics-Guide.md` - Teletext specification
- `wiki/SVG-Graphics-Guide.md` - SVG generation guide
- `wiki/Sequence-Diagrams-Guide.md` - js-sequence syntax reference
- `wiki/Flowchart-Guide.md` - flowchart.js syntax reference

## Creating New Diagrams

Use the ASCII generator service:

```python
from core.services.ascii_generator import get_ascii_generator

gen = get_ascii_generator(style="unicode")
box = gen.generate_box(width=50, height=8, title="New Diagram")
gen.save(box, "my_diagram", Path("core/data/diagrams/blocks"))
```

## Styles

- **blocks**: Visual hierarchy with █▓▒░ characters
- **plain**: Maximum compatibility with +--+ | -
- **unicode**: Refined box-drawing with ┌─┐ │ └─┘

Generated: 51 diagrams
Version: uDOS v1.1.15
