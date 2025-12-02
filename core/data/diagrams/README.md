# ASCII Diagram Library

This directory contains 51 pre-built ASCII diagrams in two styles:

## Block Shading Style (25 diagrams)
Located in `blocks/`

Visual hierarchy using block characters: █▓▒░

Examples from `dev/roadmap/graphics1.md`:
- System information panels
- Progress bars and meters
- Decision trees
- Process flows
- Theatre-style layouts

## Plain ASCII Style (26 diagrams)
Located in `plain/`

Maximum compatibility using standard ASCII: +--+ | -

Examples from `dev/roadmap/graphics2.md`:
- Service architecture diagrams
- Data pipelines
- Tables and grids
- Kanban boards
- Network diagrams

## Usage

### In uCODE Scripts
```
LOAD DIAGRAM blocks/system_status.txt
PRINT $DIAGRAM
```

### With GENERATE Command
```
GENERATE ASCII box "My Title" --style blocks --width 60
GENERATE ASCII table --style plain
```

### From Python
```python
from pathlib import Path

diagram = Path("core/data/diagrams/blocks/mission_flow.txt").read_text()
print(diagram)
```

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
