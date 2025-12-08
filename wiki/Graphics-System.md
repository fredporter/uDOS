# Graphics System (v1.2.15)

**Status**: ✅ Complete (v1.2.15)
**Test Coverage**: 120+ tests (100% passing)
**Commands**: `MAKE` (unified), `DRAW` (deprecated)

## Overview

The uDOS Graphics System provides a comprehensive 5-format graphics generation platform with offline-first template libraries, Node.js rendering service, and unified `MAKE` command interface. Version 1.2.15 introduces native Markdown diagram support (sequence, flowchart) alongside traditional ASCII, Teletext, and SVG formats.

### Key Features (v1.2.15)

- **5 Graphics Formats**: ASCII (25 templates), Teletext (4 palettes), SVG (3 styles), Sequence diagrams (5 templates), Flowcharts (5 templates)
- **Template Library**: 42 pre-built templates for immediate offline use
- **Node.js Renderer**: Dedicated service on port 5555 with specialized renderers
- **Unified Command**: `MAKE --format <type>` replaces GENERATE/DIAGRAM
- **AI Integration**: Optional AI-assisted SVG generation (requires API key)
- **Offline-First**: Full functionality without internet connection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MAKE Command (v1.2.15)                     │
│         Unified --format interface for 5 types              │
│     ascii | teletext | svg | sequence | flow                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Graphics Service Bridge (Python)                 │
│    core/services/graphics_service.py                        │
│    - HTTP client to Node.js renderer                        │
│    - Health checking & availability detection               │
│    - Error handling with graceful degradation               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│        Graphics Renderer (Node.js - Port 5555)              │
│    extensions/core/graphics-renderer/                       │
│    - Express server with 8 REST endpoints                   │
│    - 5 specialized renderers (ascii/tele/svg/seq/flow)     │
│    - Template loading & variable substitution               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Template Library (Offline)                     │
│    core/data/diagrams/                                      │
│    - 25 ASCII templates (.txt files)                        │
│    - 4 Teletext palettes (8-color JSON)                     │
│    - 3 SVG style definitions (JSON)                         │
│    - 5 Sequence diagram templates (.seq)                    │
│    - 5 Flowchart templates (.flow)                          │
│    - catalog.json (programmatic access)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Output Destinations                         │
│    memory/drafts/ascii/      (ASCII diagrams)               │
│    memory/drafts/teletext/   (ANSI color pages)             │
│    memory/drafts/svg/        (SVG graphics)                 │
│    memory/drafts/sequence/   (Sequence diagrams)            │
│    memory/drafts/flow/       (Flowcharts)                   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. MAKE Command Handler (`core/commands/make_handler_v1_2_15.py`)

**Purpose**: Unified interface for all graphics generation

**Key Features**:
- Single `--format` parameter for all 5 types
- Template browsing with `--list`
- Session statistics with `--status`
- Format-specific help modes
- Automatic output file management

**Common Options**:
```bash
--format <type>      # ascii | teletext | svg | sequence | flow
--output <file>      # Custom output filename
--list               # List available templates/palettes/styles
--status             # Show session statistics
--help [format]      # General or format-specific help
```

**Format-Specific Options**:
- **ASCII**: `--template`, `--width`, `--border`
- **Teletext**: `--palette`, `--source`
- **SVG**: `--style`, `--ai-assisted`, `--source`
- **Sequence**: `--template`, `--source`
- **Flow**: `--template`, `--source`

**Test Suite**: 35+ integration tests (100% passing)

### 2. Graphics Service Bridge (`core/services/graphics_service.py`)

**Purpose**: Python HTTP client for Node.js renderer

**Key Features**:
- Health checking before render requests
- Graceful degradation on service unavailability
- 5 dedicated render methods (render_ascii, render_teletext, render_svg, render_sequence, render_flow)
- Session statistics tracking
- Template listing and validation

**API Methods**:
```python
from core.services.graphics_service import GraphicsService

service = GraphicsService()

# Check service health
if service.is_healthy():
    # Render ASCII diagram
    result = service.render_ascii(
        template='flowchart',
        variables={'title': 'Process Flow'},
        width=80,
        border='double'
    )
    
    # Render Teletext page
    result = service.render_teletext(
        palette='classic',
        source='Welcome Screen Text'
    )
    
    # Render SVG graphic
    result = service.render_svg(
        style='technical',
        ai_assisted=True,
        source='water filter system'
    )
```

**Test Suite**: 28 unit tests (100% passing)

### 3. Graphics Renderer Service (`extensions/core/graphics-renderer/`)

**Purpose**: Node.js-based rendering microservice

**Server**: `server.js` (Express on port 5555)

**Endpoints**:
- `POST /render/ascii` - ASCII diagram generation
- `POST /render/teletext` - Teletext ANSI color rendering
- `POST /render/svg` - SVG graphic generation
- `POST /render/sequence` - Sequence diagram rendering
- `POST /render/flow` - Flowchart rendering
- `GET /templates/:format` - List available templates
- `GET /health` - Health check endpoint
- `GET /stats` - Service statistics

**Renderers**:
1. `renderers/ascii.js` (83 lines) - Template loader with variable substitution
2. `renderers/teletext.js` (104 lines) - 8-color ANSI renderer with palette support
3. `renderers/svg.js` (105 lines) - SVG generator with style templates
4. `renderers/sequence.js` (67 lines) - js-sequence-diagrams integration
5. `renderers/flow.js` (88 lines) - flowchart.js integration

**Dependencies** (package.json):
- express - HTTP server framework
- body-parser - Request parsing
- cors - Cross-origin support
- js-sequence-diagrams - Sequence diagram rendering
- flowchart.js - Flowchart rendering
- canvas - Canvas rendering for export
- puppeteer - Headless browser for complex renders

**Test Suite**: 42 integration tests (100% passing)

### 4. Template Library (`core/data/diagrams/`)

**Purpose**: Offline-first template collection

**Structure**:
```
core/data/diagrams/
├── README.md          # Template documentation (169 lines)
├── catalog.json       # Programmatic catalog (133 lines)
├── ascii/             # 25 ASCII templates (.txt)
│   ├── flowchart.txt
│   ├── system_architecture.txt
│   ├── progress_bar.txt
│   ├── funnel.txt
│   ├── timeline.txt
│   ├── decision_tree.txt
│   └── ... (19 more)
├── teletext/          # 4 color palettes (JSON)
│   ├── classic.json   # Standard 8-color ANSI
│   ├── earth.json     # Earth tones
│   ├── terminal.json  # Green terminal theme
│   └── amber.json     # Amber monochrome
├── svg/               # 3 style definitions (JSON)
│   ├── technical.json # Blueprint style
│   ├── simple.json    # Minimalist clean
│   └── detailed.json  # Comprehensive style
├── sequence/          # 5 sequence templates (.seq)
│   ├── message_flow.seq
│   ├── api_request.seq
│   ├── error_handling.seq
│   ├── multi_system.seq
│   └── async_process.seq
└── flow/              # 5 flowchart templates (.flow)
    ├── decision_flow.flow
    ├── login_process.flow
    ├── data_pipeline.flow
    ├── business_logic.flow
    └── error_recovery.flow
```

**Template Documentation**: See `core/data/diagrams/README.md`
**Programmatic Access**: Use `core/data/diagrams/catalog.json`

## Graphics Formats

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


### 1. ASCII Graphics (25 Templates)

**Purpose**: Terminal-safe diagrams with box-drawing characters

**Templates Available**:
- **Flowcharts** (5): Basic flow, decision flow, process flow, swim lanes, multi-branch
- **System Architecture** (3): Layered, microservices, network topology
- **Progress/Status** (3): Progress bar, status table, metrics grid
- **Data Visualization** (4): Funnel, timeline, comparison table, data tree
- **Decision Trees** (2): Binary tree, weighted tree
- **Organization** (2): Org chart, hierarchy diagram
- **Networks** (2): Network map, dependency graph
- **Data Flow** (2): Pipeline, transformation
- **UI Mockups** (2): Form layout, dashboard

**Usage**:
```bash
# List templates
MAKE --list ascii

# Use template with variables
MAKE --format ascii --template flowchart --width 80 --border double

# Custom border styles: none, single, double, rounded
MAKE --format ascii --template system_architecture --border rounded
```

**Output**: `memory/drafts/ascii/<filename>.txt`

**Size Limits**: 5KB per diagram (configurable)

### 2. Teletext Graphics (4 Palettes)

**Purpose**: ANSI color pages with 8-color system

**Palettes Available**:
- **classic**: Standard ANSI colors (black, red, green, yellow, blue, magenta, cyan, white)
- **earth**: Earth tones (brown, green, blue, sand)
- **terminal**: Green monochrome terminal aesthetic
- **amber**: Amber monochrome (retro CRT)

**Color Tags**:
```
{0}black{/}   {1}red{/}     {2}green{/}   {3}yellow{/}
{4}blue{/}    {5}magenta{/} {6}cyan{/}    {7}white{/}
```

**Usage**:
```bash
# List palettes
MAKE --list teletext

# Render with palette
MAKE --format teletext --palette classic --source "Welcome to {1}uDOS{/}"

# Multi-line source
MAKE --format teletext --palette earth --source "
{2}Forest Green{/}
{3}Sandy Beach{/}
{4}Ocean Blue{/}
"
```

**Output**: `memory/drafts/teletext/<filename>.ans` (ANSI escape codes)

**Size Limits**: 10KB per page (configurable)

### 3. SVG Graphics (3 Styles)

**Purpose**: Scalable vector graphics with AI integration

**Styles Available**:
- **technical**: Blueprint style with grid, measurements, annotations
- **simple**: Minimalist clean design with flat colors
- **detailed**: Comprehensive style with gradients, shadows, depth

**AI Integration**:
- Requires `GEMINI_API_KEY` in `.env`
- Optional `--ai-assisted` flag for complex diagrams
- Graceful fallback to template rendering

**Usage**:
```bash
# List styles
MAKE --list svg

# Simple template-based
MAKE --format svg --style simple --source "water filter system"

# AI-assisted (requires API key)
MAKE --format svg --style detailed --ai-assisted --source "complete water purification process with UV and carbon filters"

# Technical blueprint
MAKE --format svg --style technical --source "tent shelter with guy lines"
```

**Output**: `memory/drafts/svg/<filename>.svg`

**Size Limits**: 50KB per file (configurable)

### 4. Sequence Diagrams (5 Templates)

**Purpose**: Message flows and interaction diagrams

**Templates Available**:
- **message_flow**: Basic actor-to-actor communication
- **api_request**: HTTP request/response patterns
- **error_handling**: Error propagation through systems
- **multi_system**: Complex multi-component interactions
- **async_process**: Asynchronous message passing

**Syntax** (js-sequence-diagrams):
```
Actor->Object: Message
Object-->Actor: Response
Note right of Actor: Comment
```

**Usage**:
```bash
# List templates
MAKE --list sequence

# Use template
MAKE --format sequence --template message_flow

# Custom sequence from source
MAKE --format sequence --source "
User->API: Login Request
API->Database: Validate Credentials
Database-->API: Success
API-->User: Session Token
"
```

**Output**: `memory/drafts/sequence/<filename>.svg`

**Size Limits**: 5KB source text (configurable)

### 5. Flow Diagrams (5 Templates)

**Purpose**: Flowcharts with native Markdown integration

**Templates Available**:
- **decision_flow**: Binary decision trees
- **login_process**: Authentication workflows
- **data_pipeline**: Data transformation pipelines
- **business_logic**: Business rule flowcharts
- **error_recovery**: Error handling and recovery flows

**Syntax** (flowchart.js):
```
start=>start: Start
op=>operation: Process
cond=>condition: Decision?
end=>end: End

start->op->cond
cond(yes)->end
cond(no)->op
```

**Usage**:
```bash
# List templates
MAKE --list flow

# Use template
MAKE --format flow --template decision_flow

# Custom flowchart from source
MAKE --format flow --source "
start=>start: User Login
check=>condition: Valid?
success=>end: Dashboard
fail=>end: Error

start->check
check(yes)->success
check(no)->fail
"
```

**Output**: `memory/drafts/flow/<filename>.svg`

**Size Limits**: 5KB source text (configurable)

## Usage Examples

### Quick Start

```bash
# List all available templates for a format
MAKE --list ascii
MAKE --list teletext
MAKE --list svg
MAKE --list sequence
MAKE --list flow

# Create simple ASCII flowchart
MAKE --format ascii --template flowchart --width 80

# Create Teletext welcome screen
MAKE --format teletext --palette classic --source "Welcome to {1}uDOS{/}"

# Generate SVG water filter diagram
MAKE --format svg --style technical --source "water filter system"

# Create sequence diagram for login
MAKE --format sequence --template api_request --source "User->API: Login"

# Build flowchart for error handling
MAKE --format flow --template error_recovery
```

### Advanced Workflows

**ASCII System Architecture**:
```bash
MAKE --format ascii --template system_architecture --border double --width 100
```

**Teletext Multi-Color Page**:
```bash
MAKE --format teletext --palette earth --source "
{2}╔═══════════════════╗{/}
{2}║{/}  {3}SURVIVAL GUIDE{/}  {2}║{/}
{2}╠═══════════════════╣{/}
{2}║{/}  {4}Water{/}  {2}|{/}  {1}Fire{/}   {2}║{/}
{2}╚═══════════════════╝{/}
"
```

**AI-Assisted SVG Diagram**:
```bash
MAKE --format svg --style detailed --ai-assisted --source "complete rainwater harvesting system with gutters, first flush, filter, and storage tank"
```

**Complex Sequence Diagram**:
```bash
MAKE --format sequence --source "
User->Frontend: Submit Form
Frontend->API: POST /data
API->Validator: Check Input
Validator-->API: Valid
API->Database: INSERT
Database-->API: Success
API-->Frontend: 201 Created
Frontend-->User: Confirmation
"
```

**Business Logic Flowchart**:
```bash
MAKE --format flow --source "
start=>start: Order Received
check_stock=>condition: In Stock?
process_payment=>operation: Process Payment
ship=>operation: Ship Order
backorder=>operation: Create Backorder
notify=>operation: Notify Customer
end=>end: Complete

start->check_stock
check_stock(yes)->process_payment->ship->end
check_stock(no)->backorder->notify->end
"
```

### Session Management

```bash
# View current session statistics
MAKE --status

# Example output:
# Graphics Session Stats:
#   ASCII: 15 diagrams (420KB)
#   Teletext: 8 pages (85KB)
#   SVG: 12 graphics (560KB)
#   Sequence: 5 diagrams (42KB)
#   Flow: 7 flowcharts (63KB)
#   Total: 47 files, 1.17MB
```

## Troubleshooting

### Graphics Service Not Running

**Issue**: `MAKE` commands fail with "Service unavailable"
**Solution**:
```bash
# Start Node.js renderer service
cd extensions/core/graphics-renderer
npm install
npm start

# Verify service health
curl http://localhost:5555/health
```

### Template Not Found

**Issue**: `Template 'xyz' not found for format 'ascii'`
**Solution**:
```bash
# List available templates
MAKE --list ascii

# Check catalog
cat core/data/diagrams/catalog.json
```

### AI-Assisted SVG Failing

**Issue**: `AI generation failed, falling back to template`
**Solution**:
1. Verify `.env` has valid `GEMINI_API_KEY`
2. Check API quota/billing
3. Use `--style simple` for template-only rendering

### Color Not Rendering in Teletext

**Issue**: Color tags `{0}` showing as literal text
**Solution**:
- Terminal must support ANSI color codes
- Use `cat` to view .ans files, not text editor
- Check palette exists: `MAKE --list teletext`

### Output File Too Large

**Issue**: `Output exceeds 50KB size limit`
**Solution**:
- Simplify diagram content
- Use more compact templates
- Adjust size limits in config (DEV MODE only):
  ```python
  from core.services.graphics_service import GraphicsService
  service = GraphicsService()
  service.size_limits['svg'] = 100_000  # 100KB
  ```

## Related Documentation

- [Command Reference](Command-Reference.md) - MAKE command syntax
- [Content Generation](Content-Generation.md) - AI-assisted workflows
- [Extension Development](Extension-Development.md) - Custom renderers
- [Developer Guide](Developers-Guide.md) - Graphics Service API

## Version History

**v1.2.15** (December 2025)
- 5-format unified system (ASCII, Teletext, SVG, Sequence, Flow)
- Node.js rendering service on port 5555
- 42 template library (25 ASCII, 4 Teletext, 3 SVG, 5 Sequence, 5 Flow)
- MAKE command with `--format` syntax
- Offline-first template library
- AI-assisted SVG generation
- Python graphics service bridge
- Comprehensive format documentation

**v1.1.4** (November 2025)
- Initial graphics system release
- 4 diagram types (flow, tree, grid, hierarchy)
- AI-assisted generation with fallback
- 120 tests (100% passing)
- DRAW command integration (deprecated in v1.2.15)

## Credits

**Development**: uDOS Core Team
**Node.js Renderer**: Built on Express, js-sequence-diagrams, flowchart.js
**Template Library**: Community-contributed templates
**Graphics Architecture**: Inspired by Graphviz, PlantUML, Mermaid
**AI Integration**: Google Gemini API

---

**See Also**: 
- `MAKE --help` - Command help
- `MAKE --help ascii|teletext|svg|sequence|flow` - Format-specific help
- Node.js renderer docs: `extensions/core/graphics-renderer/README.md`
- Template catalog: `core/data/diagrams/README.md`
