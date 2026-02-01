# STREAM1 Action Plan: TypeScript Markdown Runtime

**Version:** 1.0  
**Date:** 2026-01-31  
**Stream:** Round 1 — Core Runtime  
**Duration:** 14 days (2 weeks)  
**Prerequisites:** TUI Stability Complete

---

## 🎯 Mission

Implement the **TypeScript Markdown Runtime** — a Markdown-first execution engine that turns `.md` files into interactive, stateful experiences.

**Core Principles:**
- Markdown is the source of truth
- Blocks describe behavior, not programs
- State is explicit and inspectable
- Deterministic execution (same input → same output)
- Safe by default (no arbitrary code execution)

---

## 📚 References

- **Spec:** [typescript-markdown-runtime.md](specs/typescript-markdown-runtime.md)
- **Existing:** [core/src/executors/script-executor.ts](core/src/executors/script-executor.ts)
- **Base Executor:** [core/src/executors/base.ts](core/src/executors/base.ts)
- **Types:** [core/src/types.ts](core/src/types.ts)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────┐
│   Markdown Document (.md file)      │
│  ┌──────────────────────────────┐   │
│  │ # Heading                    │   │
│  │ Narrative text with $vars    │   │
│  │                              │   │
│  │ ```state                     │   │
│  │ $name = "Fred"               │   │
│  │ ```                          │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    Markdown Scanner & Parser        │
│  - Extract headings → anchors       │
│  - Identify runtime blocks          │
│  - Parse block content              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       State Store (Runtime)         │
│  - Variable management ($vars)      │
│  - Snapshot/restore                 │
│  - Change detection                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Block Executors (Factory)      │
│  - StateExecutor                    │
│  - SetExecutor                      │
│  - FormExecutor                     │
│  - IfExecutor / ElseExecutor        │
│  - NavExecutor                      │
│  - PanelExecutor                    │
│  - MapExecutor                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Render Tree (Output)           │
│  - markdown nodes (interpolated)    │
│  - form nodes                       │
│  - nav nodes                        │
│  - panel nodes                      │
│  - warning nodes (on error)         │
└─────────────────────────────────────┘
```

---

## 📅 Implementation Phases

### Phase 1A: State Management (Days 1-2)

**Goal:** Implement variable state store with type safety

**Deliverables:**
1. `RuntimeState` class
2. Variable type system (string, number, boolean, null)
3. Get/set/snapshot operations
4. State persistence interface

**Files to Create/Modify:**
- `core/src/state/runtime-state.ts` (NEW)
- `core/src/types.ts` (UPDATE — add state types)

**Implementation:**
```typescript
type Value = string | number | boolean | null

interface RuntimeState {
  get(name: string): Value
  set(name: string, value: Value): void
  has(name: string): boolean
  delete(name: string): void
  snapshot(): Record<string, Value>
  restore(snapshot: Record<string, Value>): void
  clear(): void
}

class StateStore implements RuntimeState {
  private vars: Map<string, Value>
  
  constructor(initial?: Record<string, Value>) {
    this.vars = new Map()
    if (initial) {
      Object.entries(initial).forEach(([k, v]) => this.vars.set(k, v))
    }
  }
  
  get(name: string): Value {
    return this.vars.get(name) ?? null
  }
  
  set(name: string, value: Value): void {
    this.vars.set(name, value)
  }
  
  // ... rest of implementation
}
```

**Tests:**
- Variable CRUD operations
- Type coercion rules
- Snapshot/restore integrity
- Null handling

---

### Phase 1B: Runtime Blocks (Days 3-7)

**Goal:** Implement all 7 block types from spec

#### 1B.1: `state` Block Executor (Day 3)

**Purpose:** Declare default variable values

**File:** `core/src/executors/state-executor.ts`

**Implementation:**
```typescript
export class StateExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    const lines = block.content.trim().split('\n')
    
    for (const line of lines) {
      // Parse: $var = value
      const match = line.match(/^\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$/)
      if (!match) continue
      
      const [, varName, valueStr] = match
      const value = this.parseValue(valueStr.trim())
      
      // Only set if not already defined (preserve mode)
      if (!context.state.has(varName)) {
        context.state.set(varName, value)
      }
    }
    
    return { success: true }
  }
  
  private parseValue(str: string): Value {
    // Parse literals: "string", 123, true, false, null
    if (str.startsWith('"') && str.endsWith('"')) {
      return str.slice(1, -1) // string
    }
    if (str === 'true') return true
    if (str === 'false') return false
    if (str === 'null') return null
    
    const num = parseFloat(str)
    if (!isNaN(num)) return num
    
    return str // fallback
  }
}
```

**Tests:**
- String literals with quotes
- Number literals (int, float)
- Boolean literals
- Null handling
- Preserve vs overwrite mode

#### 1B.2: `set` Block Executor (Day 4)

**Purpose:** Controlled state mutations

**Commands:**
- `set $var value` — Assign value
- `inc $var n` — Increment (default: 1)
- `dec $var n` — Decrement (default: 1)
- `toggle $var` — Boolean toggle

**File:** `core/src/executors/set-executor.ts`

**Tests:**
- All 4 command types
- Missing variable initialization (inc/dec start at 0)
- Toggle on non-boolean (coerce to boolean first)

#### 1B.3: `form` Block Executor (Day 4-5)

**Purpose:** Interactive input definition (YAML)

**File:** `core/src/executors/form-executor.ts`

**Input Types:**
- `text` — String input
- `number` — Numeric input with min/max
- `toggle` — Boolean checkbox
- `choice` — Select from options

**Conditional fields:** `when: "$var == value"`

**Tests:**
- All input types
- Conditional field visibility
- Validation (min/max for numbers)
- YAML parsing errors

#### 1B.4: `if` / `else` Block Executors (Day 5-6)

**Purpose:** Conditional rendering

**Files:**
- `core/src/executors/if-executor.ts`
- `core/src/executors/else-executor.ts`
- `core/src/expressions/parser.ts` (Expression evaluator)

**Expression Language:**
- Variables: `$var`
- Literals: numbers, booleans, `'strings'`, `null`
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Boolean: `and`, `or`, `not`
- Grouping: `( )`

**Tests:**
- Simple comparisons
- Boolean logic (and/or/not)
- Nested expressions
- Missing variable handling (null)

#### 1B.5: `nav` Block Executor (Day 6)

**Purpose:** Navigation choices (YAML)

**File:** `core/src/executors/nav-executor.ts`

**Structure:**
```yaml
- label: Search the garden
  to: "#garden"
  when: "$coins >= 10"  # optional
```

**Tests:**
- Navigation to valid anchors
- Invalid anchor handling
- Conditional navigation (`when`)
- State tracking (`$last_nav`, `$last_anchor`)

#### 1B.6: `panel` Block Executor (Day 7)

**Purpose:** Render-only ASCII graphics

**File:** `core/src/executors/panel-executor.ts`

**Features:**
- Monospaced rendering
- Whitespace preservation
- Variable interpolation

**Tests:**
- Basic ASCII art
- Variable interpolation in panels
- Whitespace preservation

#### 1B.7: `map` Block Executor (Day 7)

**Purpose:** Render-only map placeholder (v0)

**File:** `core/src/executors/map-executor.ts`

**v0 Behavior:**
- Render placeholder panel
- Parse YAML config (center, layer, style)
- No interaction

**Tests:**
- Config parsing
- Placeholder rendering

---

### Phase 1C: Variable Interpolation (Day 8)

**Goal:** Replace `$var` with values in Markdown text

**File:** `core/src/interpolation/interpolator.ts`

**Implementation:**
```typescript
export function interpolate(text: string, state: RuntimeState): string {
  return text.replace(/\$([a-zA-Z_][a-zA-Z0-9_]*)/g, (match, varName) => {
    const value = state.get(varName)
    return value === null ? match : String(value)
  })
}
```

**Tests:**
- Single variable
- Multiple variables in one line
- Missing variables (preserve `$var`)
- Special characters in variable names

---

### Phase 1D: SQLite DB Binding (Day 9-10)

**Goal:** Read-only database queries

**File:** `core/src/database/sqlite-adapter.ts`

**Block Type:** `query`

````markdown
```query db=locations.db
SELECT * FROM places WHERE $filter
```
````

**Implementation:**
```typescript
import sqlite3 from 'better-sqlite3'

export class SQLiteAdapter {
  private db: sqlite3.Database
  
  constructor(dbPath: string) {
    this.db = sqlite3(dbPath, { readonly: true })
  }
  
  query(sql: string, params: Record<string, Value>): any[] {
    const stmt = this.db.prepare(sql)
    return stmt.all(params)
  }
}
```

**Security:**
- Read-only mode enforced
- No `DROP`, `DELETE`, `UPDATE`, `INSERT`
- Parameterized queries only

**Tests:**
- Valid SELECT queries
- Write operation rejection
- SQL injection prevention
- Variable interpolation in WHERE clauses

---

### Phase 1E: Node Runner (Day 11-14)

**Goal:** Parse and execute Markdown documents

**File:** `core/src/runtime/document-runner.ts`

**Lifecycle:**
1. **Scan** Markdown
   - Extract headings → anchors
   - Identify fenced blocks → runtime blocks
   - Extract Markdown text nodes
2. **Initialize** State
   - Load persisted state (if configured)
   - Apply `state` block defaults
3. **Execute** Blocks
   - Evaluate blocks in document order
   - Handle conditionals (`if`/`else`)
   - Collect output nodes
4. **Render** Tree
   - Interpolate variables in text
   - Generate render nodes (forms, nav, panels)
   - Return output tree

**Implementation:**
```typescript
export class DocumentRunner {
  private scanner: MarkdownScanner
  private executorFactory: ExecutorFactory
  private state: RuntimeState
  
  constructor(config: RuntimeConfig) {
    this.scanner = new MarkdownScanner()
    this.executorFactory = new ExecutorFactory()
    this.state = new StateStore()
  }
  
  async run(markdown: string): Promise<RenderTree> {
    // 1. Scan
    const doc = this.scanner.scan(markdown)
    
    // 2. Initialize state
    await this.initializeState(doc)
    
    // 3. Execute blocks
    const renderNodes: RenderNode[] = []
    for (const block of doc.blocks) {
      const executor = this.executorFactory.create(block.type)
      const result = await executor.execute(block, { state: this.state })
      
      if (result.output) {
        renderNodes.push(result.output)
      }
    }
    
    // 4. Interpolate text nodes
    const interpolatedNodes = doc.textNodes.map(node => ({
      type: 'markdown',
      content: interpolate(node.content, this.state)
    }))
    
    return { nodes: [...interpolatedNodes, ...renderNodes] }
  }
}
```

**Components:**
- `MarkdownScanner` — Parse Markdown, extract blocks
- `ExecutorFactory` — Create block executors
- `RenderTree` — Output structure for renderers

**Tests:**
- Complete document execution
- State initialization
- Block execution order
- Error handling (invalid blocks)
- Re-render on state change

---

## 🧪 Testing Strategy

### Unit Tests (Per Component)
- Each executor: `*.test.ts`
- State store: `runtime-state.test.ts`
- Interpolation: `interpolator.test.ts`
- Expression parser: `parser.test.ts`
- Phase 1A/1B mutation tests live in `memory/tests/phase1a_runtime_state.test.ts`, `memory/tests/phase1b_state_executor.test.ts`, and `memory/tests/phase1b_set_executor.test.ts`.

### Integration Tests
- `document-runner.test.ts` — Full document execution
- `state-persistence.test.ts` — Save/restore state
- `conditional-rendering.test.ts` — If/else logic

### Example Documents
- `examples/hello-world.md` — Basic variables
- `examples/quest.md` — Forms + navigation
- `examples/inventory.md` — State mutations
- `examples/database-query.md` — SQLite integration

---

## 📦 File Structure

```
core/src/
├── types.ts                       # Core types (UPDATE)
├── state/
│   ├── runtime-state.ts           # Variable store
│   └── runtime-state.test.ts
├── executors/
│   ├── base.ts                    # Base executor (EXISTS)
│   ├── factory.ts                 # Executor registry (EXISTS)
│   ├── script-executor.ts         # Script blocks (EXISTS)
│   ├── state-executor.ts          # NEW
│   ├── set-executor.ts            # NEW
│   ├── form-executor.ts           # NEW
│   ├── if-executor.ts             # NEW
│   ├── else-executor.ts           # NEW
│   ├── nav-executor.ts            # NEW
│   ├── panel-executor.ts          # NEW
│   └── map-executor.ts            # NEW
├── expressions/
│   ├── parser.ts                  # Expression evaluator
│   ├── ast.ts                     # AST types
│   └── parser.test.ts
├── interpolation/
│   ├── interpolator.ts            # Variable interpolation
│   └── interpolator.test.ts
├── database/
│   ├── sqlite-adapter.ts          # SQLite queries
│   └── sqlite-adapter.test.ts
├── scanner/
│   ├── markdown-scanner.ts        # Parse Markdown
│   └── markdown-scanner.test.ts
└── runtime/
    ├── document-runner.ts         # Main runner
    └── document-runner.test.ts
```

---

## ✅ Success Criteria

### Phase 1A
- [ ] RuntimeState implementation complete
- [ ] All CRUD operations tested
- [ ] Snapshot/restore working
- [ ] Type system enforced

### Phase 1B
- [ ] All 7 block executors implemented
- [ ] Unit tests pass for each executor
- [ ] Expression parser working for `if`/`when`
- [ ] Form YAML parsing validated

### Phase 1C
- [ ] Variable interpolation in Markdown text
- [ ] Edge cases handled (missing vars, special chars)

### Phase 1D
- [ ] SQLite read-only adapter working
- [ ] Security constraints enforced
- [ ] Variable interpolation in queries

### Phase 1E
- [ ] Document runner executes full Markdown files
- [ ] Render tree generated correctly
- [ ] Error handling for invalid blocks
- [ ] Integration tests pass

---

## 🚀 Next Steps After Phase 1

### Phase 2: Renderers
- WebView/Tauri renderer
- Terminal/TUI renderer
- Mobile renderer (future)

### Phase 3: Advanced Features
- Binder support (multi-file documents)
- State persistence (localStorage, iCloud)
- Map interaction (beyond render-only)
- Events (`onEnter`, `onChange`)

---

## 📊 Timeline Summary

| Phase | Days | Focus |
|-------|------|-------|
| **1A: State** | 2 | Variable store, types, persistence |
| **1B: Blocks** | 5 | 7 block executors, expression parser |
| **1C: Interpolation** | 1 | Variable replacement in text |
| **1D: Database** | 2 | SQLite read-only queries |
| **1E: Runner** | 4 | Document scanner, execution pipeline |
| **Total** | **14 days** | Complete TypeScript Markdown Runtime |

---

## 🎯 Ready to Begin?

**Prerequisites:**
1. TUI stability complete (Option B) ✅
2. Review this plan ✅
3. Set up TypeScript environment in `core/src/`

**First Task:** Phase 1A — Implement `RuntimeState` class

Would you like to proceed?
