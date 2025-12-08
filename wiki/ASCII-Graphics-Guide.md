# ASCII Graphics Guide (v1.2.15)

Complete reference for ASCII diagram creation in uDOS.

---

## Overview

ASCII graphics use Unicode box-drawing characters to create terminal-safe diagrams. The uDOS template library provides 25 pre-built templates covering flowcharts, system diagrams, timelines, and more.

### Key Principles

- **Terminal-Safe**: Works in any terminal emulator
- **Monospace Font**: Designed for monospace display
- **Clean Lines**: No diagonals, clear visual hierarchy
- **Size Limit**: 5KB maximum (~100 lines)
- **Offline-First**: No dependencies, instant rendering

---

## Box-Drawing Characters

### Basic Characters

```
Horizontal:  ─ ═
Vertical:    │ ║
Corners:     ┌ ┐ └ ┘ ╔ ╗ ╚ ╝
Intersections: ┼ ╬ ├ ┤ ┬ ┴ ╠ ╣ ╦ ╩
```

### Border Styles

**Single Line**:
```
┌─────────┐
│  Title  │
└─────────┘
```

**Double Line**:
```
╔═════════╗
║  Title  ║
╚═════════╝
```

**Rounded**:
```
╭─────────╮
│  Title  │
╰─────────╯
```

**Mixed** (single horizontal, double vertical):
```
╓─────────╖
║  Title  ║
╙─────────╜
```

### Arrows

```
→ ← ↑ ↓ ↔ ↕   (Simple arrows)
⇒ ⇐ ⇑ ⇓ ⇔ ⇕   (Double arrows)
▶ ◀ ▲ ▼       (Filled triangles)
```

---

## Template Library

### 1. Flowcharts (5 templates)

#### Basic Flowchart
**Use Case**: Simple linear processes

**Template**: `flowchart.txt`

**Example**:
```
┌─────────────┐
│    Start    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Process   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     End     │
└─────────────┘
```

**Command**:
```bash
MAKE --format ascii --template flowchart
```

#### Decision Flowchart
**Use Case**: Processes with branching logic

**Template**: `decision_flow.txt`

**Example**:
```
┌─────────────┐
│    Start    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Condition  │
└──┬───────┬──┘
   │       │
  Yes     No
   │       │
   ▼       ▼
┌────┐  ┌────┐
│ OK │  │Err │
└────┘  └────┘
```

#### Process Flow
**Use Case**: Multi-step workflows

**Template**: `process_flow.txt`

#### Swim Lanes
**Use Case**: Multi-actor processes

**Template**: `swim_lanes.txt`

**Example**:
```
User     │  System   │  Database
─────────┼───────────┼──────────
         │           │
Login ──>│           │
         │ Validate  │
         │ ────────> │
         │           │ Query
         │           │<─────
         │<──────────│
<────────│           │
Success  │           │
```

#### Multi-Branch
**Use Case**: Complex decision trees

**Template**: `multi_branch.txt`

### 2. System Architecture (3 templates)

#### Layered Architecture
**Use Case**: Software architecture diagrams

**Template**: `layered_architecture.txt`

**Example**:
```
┌─────────────────────────────────┐
│     Presentation Layer          │
├─────────────────────────────────┤
│     Business Logic Layer        │
├─────────────────────────────────┤
│     Data Access Layer           │
├─────────────────────────────────┤
│     Database Layer              │
└─────────────────────────────────┘
```

#### Microservices
**Use Case**: Distributed systems

**Template**: `microservices.txt`

**Example**:
```
┌──────┐    ┌──────┐    ┌──────┐
│ API  │───>│ Auth │───>│ Data │
└───┬──┘    └──────┘    └──────┘
    │
    ▼
┌──────┐
│Queue │
└──────┘
```

#### Network Topology
**Use Case**: Network diagrams

**Template**: `network_topology.txt`

### 3. Progress & Status (3 templates)

#### Progress Bar
**Template**: `progress_bar.txt`

**Example**:
```
Progress: [████████████────────] 60%

Water:    [██████████──────────] 50%
Fire:     [████████████████────] 80%
Shelter:  [████████──────────] 40%
```

#### Status Table
**Template**: `status_table.txt`

**Example**:
```
┌────────────┬────────┬─────────┐
│ Component  │ Status │ Version │
├────────────┼────────┼─────────┤
│ Core       │   ✓    │ 1.2.15  │
│ Extensions │   ✓    │ 1.1.0   │
│ Graphics   │   ✓    │ 1.2.15  │
└────────────┴────────┴─────────┘
```

#### Metrics Grid
**Template**: `metrics_grid.txt`

### 4. Data Visualization (4 templates)

#### Funnel
**Template**: `funnel.txt`

**Example**:
```
┌────────────────────────┐
│    1000 Visitors       │
└────────────┬───────────┘
             │
      ┌──────┴──────┐
      │ 500 Signups │
      └──────┬──────┘
             │
        ┌────┴────┐
        │100 Users│
        └─────────┘
```

#### Timeline
**Template**: `timeline.txt`

**Example**:
```
2025-01 ──●── Release 1.0
          │
2025-06 ──●── Release 1.1
          │
2025-12 ──●── Release 1.2.15
          │
2026-01 ──●── Release 1.3
```

#### Comparison Table
**Template**: `comparison_table.txt`

#### Data Tree
**Template**: `data_tree.txt`

**Example**:
```
Root
├── Branch A
│   ├── Leaf 1
│   └── Leaf 2
└── Branch B
    ├── Leaf 3
    └── Leaf 4
```

### 5. Decision Trees (2 templates)

#### Binary Tree
**Template**: `binary_tree.txt`

#### Weighted Tree
**Template**: `weighted_tree.txt`

### 6. Organization Charts (2 templates)

#### Org Chart
**Template**: `org_chart.txt`

**Example**:
```
      ┌───────┐
      │  CEO  │
      └───┬───┘
          │
    ┌─────┴─────┐
    │           │
┌───┴───┐   ┌───┴───┐
│  CTO  │   │  CFO  │
└───────┘   └───────┘
```

#### Hierarchy Diagram
**Template**: `hierarchy.txt`

### 7. Network Diagrams (2 templates)

#### Network Map
**Template**: `network_map.txt`

**Example**:
```
    Internet
        │
    ┌───┴───┐
    │Router │
    └───┬───┘
        │
    ┌───┴───┐
    │Switch │
    └─┬─┬─┬─┘
      │ │ │
    PC1│ │PC3
      PC2
```

#### Dependency Graph
**Template**: `dependency_graph.txt`

### 8. Miscellaneous (2 templates)

#### Gantt Chart
**Template**: `gantt.txt`

**Example**:
```
Task 1  ████████────────
Task 2  ────████████────
Task 3  ────────████████
        Week 1  Week 2
```

#### Kanban Board
**Template**: `kanban.txt`

**Example**:
```
┌──────┬──────┬──────┐
│ TODO │DOING │ DONE │
├──────┼──────┼──────┤
│ [T1] │ [T3] │ [T5] │
│ [T2] │ [T4] │      │
└──────┴──────┴──────┘
```

---

## Command Usage

### List Templates

```bash
MAKE --list ascii
```

### Generate Diagram

```bash
# Use template
MAKE --format ascii --template flowchart

# With options
MAKE --format ascii --template system_architecture --width 100 --border double

# Custom output
MAKE --format ascii --template timeline --output memory/drafts/ascii/project_timeline.txt
```

### Template Options

```bash
--template <name>    # Template name (see list above)
--width <cols>       # Diagram width (default: 80)
--border <style>     # Border style: none | single | double | rounded
--compact            # Minimize whitespace
```

---

## Best Practices

### 1. Keep It Simple

❌ **Avoid**:
```
  ┌─┐
  │ ├──┐
╔═╧═╧══╗
║ Text ║
╚══════╝
```

✅ **Prefer**:
```
┌──────┐
│ Text │
└──────┘
```

### 2. Consistent Alignment

❌ **Avoid**:
```
┌──────┐
│Text  │
│  More Text│
└──────┘
```

✅ **Prefer**:
```
┌───────────┐
│ Text      │
│ More Text │
└───────────┘
```

### 3. Clear Flow Direction

Always use arrows for flow:
```
Step 1
   │
   ▼
Step 2
   │
   ▼
Step 3
```

### 4. Limit Complexity

- Maximum 15 nodes per diagram
- Maximum 80 characters width (for terminal compatibility)
- Maximum 100 lines total
- Use multiple diagrams if needed

### 5. Label Everything

```
┌─────────────┐
│  Component  │  ← Always label boxes
└─────────────┘
```

### 6. Test in Terminal

Always verify rendering in actual terminal:
```bash
cat memory/drafts/ascii/diagram.txt
```

---

## Common Patterns

### Sequential Process
```
A → B → C → D
```

### Parallel Processes
```
       ┌─> B ─┐
A ─────┼─> C ─┼───> E
       └─> D ─┘
```

### Error Handling
```
Process
   │
   ▼
Success? ──No──> Error
   │
  Yes
   │
   ▼
Continue
```

### Grouped Elements
```
┌──────────────────┐
│ Group Name       │
├──────────────────┤
│ ┌──┐  ┌──┐  ┌──┐│
│ │A │  │B │  │C ││
│ └──┘  └──┘  └──┘│
└──────────────────┘
```

---

## Sizing Guidelines

### Size Limits

- **Maximum**: 5KB (~100 lines)
- **Recommended**: 50 lines for readability
- **Width**: 80 columns (terminal standard)

### Example Sizes

- Simple flowchart: ~20 lines (1KB)
- System architecture: ~30 lines (1.5KB)
- Complex network: ~60 lines (3KB)

### Exceeding Limits

If diagram exceeds 5KB:
1. Split into multiple diagrams
2. Simplify structure
3. Remove unnecessary details
4. Use abbreviations

---

## Troubleshooting

### Alignment Issues

**Problem**: Boxes don't line up
**Solution**: Use monospace font (Courier, Monaco, Consolas)

### Character Rendering

**Problem**: Box characters show as �
**Solution**: Ensure UTF-8 encoding:
```bash
export LANG=en_US.UTF-8
```

### Diagram Too Wide

**Problem**: Diagram exceeds terminal width
**Solution**: Use `--width` option:
```bash
MAKE --format ascii --template flowchart --width 60
```

### Template Not Found

**Problem**: Template doesn't exist
**Solution**: List available templates:
```bash
MAKE --list ascii
```

---

## Version Control

### Save Template Variants

```bash
# Save custom version
MAKE --format ascii --template flowchart --output my_flowchart_v1.txt

# Create variations
cp my_flowchart_v1.txt my_flowchart_v2.txt
```

### Archive Old Versions

Use `.archive/` folders:
```bash
mv old_diagram.txt memory/drafts/ascii/.archive/
```

---

## Related Documentation

- [Graphics System](Graphics-System.md) - Overall architecture
- [Command Reference](Command-Reference.md) - MAKE command syntax
- [Teletext Graphics Guide](Teletext-Graphics-Guide.md) - Color alternative

---

**See Also**: `MAKE --help ascii`, Template catalog: `core/data/diagrams/README.md`
