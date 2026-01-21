# uDOS Lean TypeScript Runtime

**Version:** 1.0.0-lean  
**Status:** Development (MVP Complete)  
**Purpose:** Parse and execute uDOS markdown scripts (example-script.md, movement-demo-script.md)

A minimal, focused TypeScript runtime for executing interactive markdown documents. No frameworks, no TUI overhead—just parsing, state management, and block execution.

---

## 🎯 What It Does

Parses markdown scripts with frontmatter and executes runtime blocks:

````markdown
---
title: Adventure Game
---

## Start

```state
$player = { "name": "Alice", "coins": 100 }
```
````

Welcome to the adventure, $player.name!

```nav
choice: "Go west"
  when: $player.coins >= 50
choice: "Rest"
```

````

**Supported Blocks:**
- `state` — Initialize variables
- `set` — Mutations (set, inc, dec, toggle)
- `form` — User input → state binding
- `if/else` — Conditional execution
- `nav` — Navigation choices with gates
- `panel` — ASCII rendering with interpolation
- `map` — Viewport with sprites (optional)
- `script` — Sandboxed code execution (disabled by default)

---

## 📦 Installation

```bash
cd core/
npm install
npm run build
npm test
````

---

## 🚀 Quick Start

```typescript
import { Runtime } from "@udos/runtime";

const runtime = new Runtime();

// Load markdown script
runtime.load(fs.readFileSync("example-script.md", "utf8"));

// Execute first section
const doc = runtime.getDocument();
if (doc) {
  const result = await runtime.execute(doc.sections[0].id);
  console.log(result.output);
}

// Get/set state
const state = runtime.getState(); // { player: { name: 'Alice', ... }, ... }
runtime.setState({
  /* new state */
});
```

---

## 📖 API Reference

### `Runtime` Class

**Constructor:**

```typescript
new Runtime(config?: RuntimeConfig)
```

**Options:**

```typescript
interface RuntimeConfig {
  allowScripts?: boolean; // Enable script block execution (default: false)
  maxDepth?: number; // Max execution depth (default: 100)
  timeout?: number; // Execution timeout in ms (default: 5000)
}
```

**Methods:**

```typescript
// Load markdown document
load(markdown: string): void

// Execute a section by ID
execute(sectionId: string): Promise<ExecutorResult>

// Get current state
getState(): any

// Set state
setState(state: any): void

// Get parsed document
getDocument(): Document | null
```

### `StateManager` Class

```typescript
// Set/get with dot notation
state.set("player.name", "Alice");
state.get("player.name"); // 'Alice'

// Array access
state.get("inventory[0].name");

// Numeric operations
state.increment("coins", 10);
state.decrement("health", 5);
state.toggle("flag");

// String interpolation
state.interpolate("Hello $player.name"); // "Hello Alice"

// Watchers
state.watch("coins", (newValue) => {
  console.log("Coins changed to:", newValue);
});

// Bulk operations
state.setAll({ x: 1, y: 2 });
state.merge({ z: 3 }); // x:1, y:2, z:3
```

### `MarkdownParser` Class

````typescript
const doc = MarkdownParser.parse(markdown);

// Document structure:
interface Document {
  frontmatter: Frontmatter; // title, id, version, etc.
  sections: Section[]; // ## headers become sections
}

interface Section {
  id: string; // generated from title
  title: string;
  content: string; // markdown content
  blocks: RuntimeBlock[]; // ```state, ```form, etc.
}

interface RuntimeBlock {
  type: "state" | "set" | "form" | "if" | "nav" | "panel" | "map" | "script";
  content: string; // block body
  meta?: Record<string, any>; // optional metadata
}
````

---

## 🧪 Testing

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

**Test Files:**

- `__tests__/runtime.test.ts` — State, parser, runtime integration

**Example Test Cases:**

- State: get/set, nested access, arrays, mutations, watchers
- Parser: frontmatter, sections, blocks, multiple formats
- Runtime: state init, set operations, panels, interpolation

---

## 💾 Block Types Reference

### `state` Block

Initialize variables (YAML-like):

````markdown
```state
$player = { "name": "Alice", "coins": 100 }
$world = { "time": "morning" }
```
````

````

Executed once per section. Replaces existing state.

### `set` Block

Mutations (set, inc, dec, toggle):

```markdown
```set
set $player.coins 50
inc $coins 10
dec $health 5
toggle $has_key
````

````

### `form` Block

Collect user input (planned):

```markdown
```form
name: "What is your name?"
  type: text
coins: "How many coins?"
  type: number
  min: 0
  max: 1000
````

````

Binds form fields to state: `$name`, `$coins`, etc.

### `if/else` Block

Conditional execution (planned):

```markdown
```if
$player.coins >= 100
You are rich!
````

```if
$player.coins < 50
You are poor!
```

````

### `nav` Block

Navigation choices:

```markdown
```nav
choice: "Go west"
  when: $player.coins >= 50
choice: "Go east"
choice: "Rest"
  when: true
````

````

Returns `{ nextSection: "west-section" }` based on choice.

### `panel` Block

ASCII rendering with interpolation:

```markdown
```panel
┌────────────────────┐
│ Player: $player.name
│ Coins: $player.coins
│ Time: $world.time
└────────────────────┘
````

````

Supports Unicode box drawing, variable interpolation.

### `map` Block

Viewport with sprites (planned):

```markdown
```map
width: 20
height: 10
viewport: [10, 10]
sprite: "@"
  x: $player.pos.x
  y: $player.pos.y
````

````

### `script` Block

Sandboxed code (optional):

```markdown
```script
$coins = $coins + 10
$has_key = true
````

````

Requires `allowScripts: true` in config.

---

## 🔧 Development

**Build:**
```bash
npm run build          # Compile TypeScript
npm run dev            # Watch mode
````

**Project Structure:**

```
core/
├── src/
│   ├── index.ts            # Runtime orchestrator
│   ├── types.ts            # Type definitions
│   ├── parser/
│   │   └── markdown.ts     # Markdown parser
│   ├── state/
│   │   └── manager.ts      # State management
│   ├── executors/          # Block executors (future)
│   └── utils/              # Utilities (future)
├── __tests__/
│   └── runtime.test.ts     # Test suite
├── package.json
├── tsconfig.json
├── jest.config.js
└── version.json
```

---

## 🎓 Examples

See attached markdown scripts for comprehensive examples:

- `example-script.md` — Full feature demo
- `movement-demo-script.md` — Sprite movement example

---

## 📊 Feature Matrix

| Feature                | Status         | Notes                    |
| ---------------------- | -------------- | ------------------------ |
| State initialization   | ✅ Complete    | set/get/merge/watch      |
| Variable interpolation | ✅ Complete    | $var, $a.b.c, $arr[0]    |
| Dot notation access    | ✅ Complete    | Deep nesting             |
| Set operations         | ✅ Complete    | set, inc, dec, toggle    |
| Form rendering         | 🔄 In Progress | Field types defined      |
| Navigation             | 🔄 In Progress | Choice routing defined   |
| Panels                 | ✅ Complete    | ASCII + interpolation    |
| Maps                   | 🔄 In Progress | Viewport system designed |
| Conditionals           | 🔄 In Progress | if/else logic designed   |
| Script execution       | ⏸️ Deferred    | Sandboxed, optional      |
| SQLite binding         | ⏸️ Optional    | Read-only DB access      |

---

## 🚀 Next Steps (Phase 3)

1. **Complete block executors** - Form, nav, conditional, map
2. **Test with example scripts** - Verify all features work
3. **Optional: SQLite binding** - $db namespace for read-only queries
4. **Integration:** Mount runtime in Goblin Dev Server (HTTP APIs)
5. **Deploy:** Browser-based execution (no TUI required)

---

## 📝 Version

- **Current:** v1.0.0-lean (development)
- **Status:** MVP complete, executor expansion in progress
- **Last Updated:** 2026-01-16

---

## 📚 References

- [uDOS AGENTS.md](../../AGENTS.md) — Project architecture
- [docs/\_index.md](../../docs/_index.md) — Engineering entry point
- [docs/roadmap.md](../../docs/roadmap.md) — Project roadmap
- [example-script.md](../../example-script.md) — Feature demo
- [movement-demo-script.md](../../movement-demo-script.md) — Sprite example

---

**uDOS Alpha v1.0.2.0** | Lean TypeScript Runtime | Build fresh, keep it simple
