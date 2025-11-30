# Graphics System (v1.1.4)

**Status**: ✅ Complete (v1.1.4)
**Test Coverage**: 120 tests (100% passing)
**Commands**: `DRAW`

## Overview

The uDOS Graphics System enables creation of ASCII and teletext-style diagrams directly from text descriptions. It supports four diagram types with AI-assisted generation and fallback to simple text parsing.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DRAW Command (CLI)                       │
│          Text descriptions → Visual diagrams                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Diagram Generator (AI/Parser)                 │
│     - Auto type detection from keywords                     │
│     - Text-to-data parsing (4 types)                       │
│     - AI integration with fallback                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Diagram Compositor (Assembly)                    │
│     - Template-based creation                               │
│     - Canvas rendering (ASCII)                              │
│     - Export (ASCII/ANSI/Unicode)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Graphics Library (Components)                      │
│     - Box-drawing characters (Unicode)                      │
│     - Diagram templates (4 types)                           │
│     - Color support (teletext + ANSI)                       │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Graphics Library (`core/services/graphics_library.py`)

Foundation layer providing:
- **Box-Drawing Characters**: Unicode characters for diagrams (─│┌┐└┘├┤etc.)
- **Component Library**: Reusable boxes, shapes, connectors, markers
- **Diagram Templates**: Preconfigured templates for 4 diagram types
- **Color Support**: Teletext (0-7) and ANSI color codes

**Test Suite**: 32 tests (100% passing)

### 2. Diagram Compositor (`core/services/diagram_compositor.py`)

Assembly and rendering layer:
- **Canvas System**: 2D array for flexible diagram composition
- **Template Engine**: Creates diagrams from templates + data
- **Node/Connection Model**: Diagram elements with positioning
- **Export Formats**: ASCII, ANSI, Unicode

**Test Suite**: 25 tests (100% passing)

### 3. Diagram Generator (`core/services/diagram_generator.py`)

Intelligent text-to-diagram conversion:
- **Auto Type Detection**: Identifies diagram type from keywords
- **Text Parsing**: Converts descriptions to structured data
- **AI Integration**: Optional AI-assisted generation with fallback
- **Helper Functions**: Quick diagram creation utilities

**Test Suite**: 35 tests (100% passing)

### 4. DRAW Command Handler (`core/commands/draw_handler.py`)

CLI integration:
- **Command Parsing**: Handles DRAW commands with options
- **File I/O**: Read descriptions, save diagrams
- **JSON Support**: Structured data input
- **Error Handling**: Graceful fallbacks

**Test Suite**: 28 integration tests (100% passing)

## Diagram Types

### FLOW (Flowchart)

Process workflows, decision trees, step-by-step procedures.

**Components**:
- Process boxes (rectangles)
- Decision diamonds (conditions)
- Start/End markers (rounded)
- Arrows and connectors

**Example**:
```
DRAW FLOW "Start → Get input → Valid? → Process → End"
```

**Output**:
```
╭─────────╮
│  Start  │
╰─────────╯
     │
     ▼
┌───────────┐
│ Get input │
└───────────┘
     │
     ▼
   Valid?
   /   \
  Y     N
  │     │
  ▼     ▼
Process Error
```

### TREE (Tree Diagram)

Hierarchical structures, file systems, taxonomies.

**Components**:
- Root node (top level)
- Parent nodes (branches)
- Child nodes (leaves)
- Tree connectors (├─, └─)

**Example**:
```
DRAW TREE "System\nUsers\nData\nConfig"
```

**Output**:
```
System
├─ Users
├─ Data
└─ Config
```

### GRID (Table/Grid)

Tabular data, comparisons, structured lists.

**Components**:
- Header row (bold borders)
- Data rows (content cells)
- Fixed column widths
- Grid borders

**Example**:
```
DRAW GRID "Name,Age,City\nAlice,30,NYC\nBob,25,SF"
```

**Output**:
```
┏━━━━━━━┳━━━━━┳━━━━━━┓
┃ Name  ┃ Age ┃ City ┃
┣━━━━━━━╋━━━━━╋━━━━━━┫
│ Alice │  30 │ NYC  │
│ Bob   │  25 │ SF   │
┗━━━━━━━┻━━━━━┻━━━━━━┛
```

### HIERARCHY (Org Chart)

Organization charts, team structures, reporting lines.

**Components**:
- Executive level (double border)
- Manager level (single border)
- Worker level (light border)
- Vertical connectors

**Example**:
```
DRAW HIERARCHY "CEO\n  CTO\n    Dev Lead\n  CFO"
```

**Output**:
```
╔═══════╗
║  CEO  ║
╚═══════╝
    │
    ├─ CTO
    │   └─ Dev Lead
    └─ CFO
```

## Usage

### Basic Commands

```bash
# Show help
DRAW HELP

# List diagram types
DRAW TYPES

# Create flowchart
DRAW FLOW "Start → Process → End"

# Create tree
DRAW TREE "Root\nChild1\nChild2"

# Create grid/table
DRAW GRID "Col1,Col2\nVal1,Val2"

# Create org chart
DRAW HIERARCHY "Manager\n  Worker1\n  Worker2"

# Auto-detect type
DRAW "Process workflow steps"
```

### File I/O

```bash
# Read description from file
DRAW FLOW --file workflow.txt

# Save output to file
DRAW TREE "System" --save diagram.txt

# Read JSON data
DRAW FLOW --data data.json

# Combine options
DRAW GRID --file data.csv --save table.txt --format unicode
```

### Description Formats

**FLOW (Flowchart)**:
```
Start
Get user input
Valid?
Process data
End
```
- One step per line
- Use "?" or "if" for decisions
- Use "start" and "end" keywords

**TREE (Tree Diagram)**:
```
Root Node
Child 1
Child 2
  Grandchild 1
  Grandchild 2
```
- First line is root
- Indentation shows nesting

**GRID (Table)**:
```
Header1,Header2,Header3
Row1Col1,Row1Col2,Row1Col3
Row2Col1,Row2Col2,Row2Col3
```
- First line: column headers
- Remaining lines: data rows
- Supports comma, pipe, or tab separation

**HIERARCHY (Org Chart)**:
```
CEO
  CTO
    Engineering Lead
    Product Lead
  CFO
    Finance Manager
```
- Use indentation for levels
- First line: top level

## Advanced Features

### Auto Type Detection

The system automatically detects diagram type from keywords:

```bash
DRAW "Process workflow: validate → process → complete"  # → FLOW
DRAW "System hierarchy: root, child1, child2"           # → TREE
DRAW "Table: Name,Age | Alice,30 | Bob,25"             # → GRID
DRAW "Organization chart: CEO, managers, teams"         # → HIERARCHY
```

**Detection Keywords**:
- **Flow**: process, workflow, steps, decision, if, then
- **Tree**: tree, hierarchy, parent, child, branch
- **Grid**: table, grid, rows, columns, matrix
- **Hierarchy**: organization, org chart, levels, manager, team

### JSON Data Input

For complex diagrams, provide structured JSON data:

**Flowchart Data**:
```json
{
  "nodes": [
    {"id": "start", "text": "Start", "type": "start_end"},
    {"id": "process", "text": "Process", "type": "process"},
    {"id": "end", "text": "End", "type": "start_end"}
  ],
  "connections": [
    {"from": "start", "to": "process"},
    {"from": "process", "to": "end"}
  ]
}
```

**Tree Data**:
```json
{
  "root": "System",
  "children": [
    {"name": "Users"},
    {"name": "Data", "children": [
      {"name": "Cache"},
      {"name": "Storage"}
    ]}
  ]
}
```

Usage:
```bash
DRAW FLOW --data diagram_data.json
```

### Export Formats

```bash
# ASCII (default) - Basic ASCII characters
DRAW FLOW "Process" --format ascii

# ANSI - With color codes
DRAW TREE "System" --format ansi

# Unicode - Full Unicode box-drawing
DRAW GRID "Data" --format unicode
```

## Integration Examples

### Knowledge-to-Diagram

Create diagrams from knowledge guides:

```bash
# Water purification workflow
DRAW FLOW "Collect water → Filter debris → Boil 10 min → Cool → Safe"

# Shelter types hierarchy
DRAW HIERARCHY "Shelters\n  Natural\n    Cave\n    Tree\n  Built\n    Lean-to\n    A-frame"

# Tool comparison table
DRAW GRID "Tool,Weight,Durability,Use\nKnife,Light,High,All\nAxe,Heavy,High,Wood\nSaw,Medium,Medium,Cutting"
```

### Mission Workflow

Visualize mission steps:

```bash
# Mission: Setup Camp
DRAW FLOW "Find location → Clear ground → Setup shelter → Arrange fire pit → Store supplies → Complete"
```

### Team Organization

Create org charts:

```bash
DRAW HIERARCHY "Expedition Leader\n  Navigation\n  Supplies\n  Medical\n  Communications"
```

## Python API

### Quick Generation

```python
from core.services.diagram_generator import quick_diagram, flowchart, tree, table

# Quick diagram with auto-detection
diagram = quick_diagram("Process workflow steps")

# Specific type helpers
flow = flowchart("Start → Process → End")
tree_diagram = tree("Root\nChild1\nChild2")
grid = table("Name,Age\nAlice,30\nBob,25")
```

### Advanced Usage

```python
from core.services.diagram_generator import DiagramGenerator
from core.services.diagram_compositor import DiagramCompositor

# Create generator
generator = DiagramGenerator()

# Generate from description
diagram = generator.generate_from_description(
    "User login workflow",
    diagram_type="flow"
)

# Or create from structured data
compositor = DiagramCompositor()
compositor.create_from_template('tree', {
    'root': 'System',
    'children': [
        {'name': 'Users'},
        {'name': 'Data'}
    ]
})
output = compositor.render()
```

## Data Files

### Graphics Resources

```
core/data/graphics/
├── blocks/
│   └── box_drawing.json       # Unicode box-drawing characters
├── components.json             # Reusable diagram components
└── templates/
    ├── flowchart.json          # Flowchart template
    ├── tree.json               # Tree diagram template
    ├── grid.json               # Grid/table template
    └── hierarchy.json          # Org chart template
```

### Box-Drawing Characters

**Character Sets**:
- `light`: ─│┌┐└┘├┤┬┴┼ (standard)
- `heavy`: ━┃┏┓┗┛┣┫┳┻╋ (bold)
- `double`: ═║╔╗╚╝╠╣╦╩╬ (double-line)
- `rounded`: ╭╮╰╯ (curved corners)
- `blocks`: █▓▒░▀▄▌▐▔▁ (shading)
- `arrows`: ↑↓←→↔↕↗↘↙↖⬆⬇⬅➡
- `bullets`: ●○■□◆◇▲▼▶◀
- `misc`: ✓✗★☆◉◎

**Color Schemes**:
- Teletext: 0-7 (black, red, green, yellow, blue, magenta, cyan, white)
- ANSI Basic: 30-37 (foreground)
- ANSI Bright: 90-97 (bright variants)

## Testing

### Test Suite Organization

```
sandbox/tests/
├── test_graphics_library.py        # 32 tests - Graphics foundation
├── test_diagram_compositor.py      # 25 tests - Diagram assembly
├── test_diagram_generator.py       # 35 tests - Text-to-diagram
└── test_graphics_integration.py    # 28 tests - End-to-end integration
```

**Total**: 120 tests (100% passing)

### Run Tests

```bash
# All graphics tests
pytest sandbox/tests/test_graphics*.py -v

# Specific component
pytest sandbox/tests/test_graphics_library.py -v

# Integration tests only
pytest sandbox/tests/test_graphics_integration.py -v

# With coverage
pytest sandbox/tests/test_graphics*.py --cov=core/services --cov=core/commands
```

### Test Script

Run interactive test:
```bash
./start_udos.sh sandbox/ucode/test_draw_command.uscript
```

## Performance

### Benchmarks

- **Small diagrams** (5-10 nodes): <10ms
- **Medium diagrams** (20-50 nodes): <50ms
- **Large diagrams** (100+ nodes): <200ms
- **Wide tables** (10+ columns): <100ms

### Limits

- **Max canvas size**: 200x100 characters
- **Max nodes**: 500 per diagram
- **Max text per node**: 100 characters
- **Max columns (grid)**: 20

## Error Handling

The graphics system uses graceful fallbacks:

1. **Unknown diagram type** → Defaults to flowchart
2. **Empty description** → Returns error with help text
3. **Invalid JSON** → Returns parse error
4. **File not found** → Returns file error
5. **Malformed data** → Creates minimal diagram

## Future Enhancements

### v1.2.0 (Planned)

- [ ] Animation support (frame-by-frame)
- [ ] Interactive editing (modify existing diagrams)
- [ ] Custom templates (user-defined)
- [ ] Diagram diff/merge
- [ ] Export to SVG/PNG (via extension)

### AI Integration (Optional)

Currently supports AI-assisted generation with fallback:
- Set AI service in generator: `DiagramGenerator(ai_service=my_ai)`
- Fallback to text parsing if AI unavailable
- Zero dependencies for offline use

## Troubleshooting

### Common Issues

**Issue**: Boxes don't render correctly
**Solution**: Ensure terminal supports Unicode (UTF-8)

**Issue**: Diagrams too wide
**Solution**: Use `--format ascii` for narrower output

**Issue**: Empty diagram output
**Solution**: Check description format (see examples above)

**Issue**: Command not found
**Solution**: Ensure v1.1.4 installed and handlers registered

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Related Documentation

- [Command Reference](Command-Reference.md) - All uDOS commands
- [Workflows](Workflows.md) - Diagram workflow examples
- [Extensions System](Extensions-System.md) - Extending graphics
- [Developer Guide](Developers-Guide.md) - API reference

## Version History

**v1.1.4** (Nov 2025)
- Initial graphics system release
- 4 diagram types (flow, tree, grid, hierarchy)
- AI-assisted generation with fallback
- 120 tests (100% passing)
- DRAW command integration

## Credits

**Development**: uDOS Core Team
**Testing**: Community contributors
**Graphics Library**: Based on Unicode Consortium box-drawing chars
**Architecture**: Inspired by Graphviz, PlantUML, Mermaid

---

**See Also**: `DIAGRAM` (ASCII art library browser), `PANEL` (teletext display), `GENERATE` (AI content)
