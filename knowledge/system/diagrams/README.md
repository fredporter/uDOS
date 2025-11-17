# uDOS ASCII/Teletext Diagram Library

**Location**: `data/system/diagrams/`
**Format**: Markdown (`.md`) with ASCII graphics in code blocks
**Compatibility**: All screen tiers (0-14)

---

## 📁 Directory Structure

```
diagrams/
├── README.md              # This file
├── programming/           # Code-related diagrams
│   ├── syntax-trees/
│   ├── control-flow/
│   └── algorithms/
├── flowcharts/            # Process flowcharts
│   ├── decision-trees/
│   └── workflows/
├── data-structures/       # Data visualization
│   ├── trees/
│   ├── graphs/
│   └── arrays/
├── systems/               # System architecture
│   ├── uDOS-architecture/
│   ├── memory-tiers/
│   └── command-flow/
└── survival/              # Practical diagrams
    ├── knots/
    ├── shelters/
    └── tools/
```

---

## 🎨 Diagram Categories

### 1. Programming (50+ diagrams)
- Syntax trees for uCODE constructs
- Control flow diagrams
- Algorithm visualizations
- Function call stacks
- Variable scope chains

### 2. Flowcharts (40+ diagrams)
- Decision trees
- Workflow processes
- State machines
- Error handling paths
- User interaction flows

### 3. Data Structures (30+ diagrams)
- Binary trees
- Linked lists
- Hash tables
- Stacks and queues
- Graph representations

### 4. Systems (40+ diagrams)
- uDOS architecture
- Command handler flow
- Memory tier structure
- File system layout
- Network diagrams

### 5. Survival (40+ diagrams)
- Knot tying steps
- Shelter construction
- Tool usage
- Water purification
- Fire building

---

## 📝 Diagram Format Standards

### Markdown + ASCII Graphics

All diagrams use **Markdown (`.md`)** format with ASCII graphics in code blocks.

**Benefits:**
- ✅ Better structure (headers, lists, tables)
- ✅ Enhanced readability (bold, italic, links)
- ✅ Preserved ASCII graphics (in fenced code blocks)
- ✅ Professional documentation format
- ✅ Easy navigation (table of contents, anchors)

**Example Structure:**
````markdown
# Diagram Title

Brief description of the diagram's purpose.

## Section 1: Explanation

Text with **bold** and *italic* for emphasis.

```
┌─────────────┐
│   Diagram   │  ← ASCII graphics in code block
└─────────────┘
```

More explanation with [links](#related) and lists.
````

### ASCII Box Drawing Characters

Use inside code blocks for diagrams:
```
Single Line: ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
Double Line: ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
Arrows: → ← ↑ ↓ ↔ ⇒ ⇐ ⇑ ⇓ ▲ ▼ ◄ ►
Symbols: ● ○ ◆ ◇ ■ □ ▲ △ ▼ ▽
```

### Teletext Block Graphics

For filled areas (use in code blocks):
```
Blocks: ░ ▒ ▓ █ ▀ ▄ ▌ ▐
Patterns: ┃ ━ ┏ ┓ ┗ ┛
Mosaic: 2×3 character blocks for terrain/maps
```

---

## 🔧 Usage

### In Knowledge Guides
```markdown
See diagram: [programming/control-flow/if-else.md](../../data/system/diagrams/programming/control-flow/if-else.md)
```

### With DIAGRAM Command
```ucode
[DIAGRAM|SEARCH|knot]
[DIAGRAM|SHOW|survival/knots/bowline.md]
```

### Embedded in Scripts
```ucode
# Load and display
SET diagram = [FILE|LOAD|data/system/diagrams/flowcharts/workflow.md]
PRINT $diagram
```

---

## 📐 Size Guidelines

| Tier | Max Width | Max Height | Use Case |
|------|-----------|------------|----------|
| 0-3  | 20 chars  | 10 lines   | Watch/Phone |
| 4-6  | 40 chars  | 20 lines   | Tablet |
| 7-9  | 80 chars  | 40 lines   | Desktop |
| 10-14| 120 chars | 60 lines   | Large displays |

### Responsive Diagrams
Provide multiple versions for different tiers:
- `diagram-small.md` (20×10 code blocks)
- `diagram-medium.md` (40×20 code blocks)
- `diagram-large.md` (80×40 code blocks)
- `diagram-xlarge.md` (120×60 code blocks)

---

## 🎯 Naming Conventions

```
category/subcategory/name-tier.md

Examples:
programming/syntax-trees/function-call-medium.md
survival/knots/bowline-small.md
systems/architecture/4-tier-memory-large.md
```

**File Extension**: Always use `.md` (Markdown)

---

## ✅ Quality Standards

### All Diagrams Must:
- [ ] Render correctly in plain text editor
- [ ] Use only ASCII or standard Unicode characters
- [ ] Include title/label
- [ ] Provide legend if needed
- [ ] Work in monospace fonts
- [ ] Be version controlled (in git)

### Testing Checklist:
- [ ] Test in vim/nano
- [ ] Test in uDOS terminal
- [ ] Test in web interface
- [ ] Test on smallest tier (watch)
- [ ] Test on largest tier (8K)

---

## 🔗 Integration Points

### Knowledge Guides
All guides in `knowledge/` can reference diagrams:
```markdown
See: [Variable Scope Diagram](../../data/system/diagrams/programming/syntax-trees/variable-scope-medium.md)
```

### Commands
- `DIAGRAM` - Browse and display
- `GUIDE` - Auto-load referenced diagrams
- `KB` - Search includes diagram descriptions

### Scripts
Include diagrams in automation output:
```ucode
PRINT "Workflow Diagram:"
[DIAGRAM|SHOW|flowcharts/daily-routine.md]
```

---

## 📊 Statistics

**Target**: 200+ diagrams total
**Current**: 5 (v1.0.21 in progress)
**Completed**:
- Programming: 3 (if-else, while-loop, variable-scope)
- Systems: 1 (memory-tiers)
- Survival: 1 (square-knot)

**By Category Goal**:
- Programming: 50
- Flowcharts: 40
- Data Structures: 30
- Systems: 40
- Survival: 40

---

## 🚀 Next Steps

1. Create programming diagrams for uCODE guides
2. Build survival skill visualizations
3. Implement DIAGRAM command
4. Add search/browse functionality
5. Create responsive versions for all tiers

---

**Format**: Markdown (.md), UTF-8 encoded
**Storage**: Git version controlled
**Access**: Read-only system data
**Updates**: Ship with uDOS releases
