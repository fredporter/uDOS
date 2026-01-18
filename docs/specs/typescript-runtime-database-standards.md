# TypeScript Runtime Database Standards

**Purpose:** Define how the TypeScript runtime (v1.0.3.0+) handles state management, variable binding, and external database integration.

**Scope:** Mobile/iPad offline execution with same markdown format as Python desktop runtime

**Status:** Complete specification (implementation begins v1.0.3.0)

---

## Table of Contents

1. [State Model](#state-model)
2. [Variable Naming & Access](#variable-naming--access)
3. [Database Binding](#database-binding)
4. [Runtime Blocks](#runtime-blocks)
5. [Execution Flow](#execution-flow)
6. [Interpolation Rules](#interpolation-rules)
7. [Example: Complete Interactive Story](#example-complete-interactive-story)
8. [Testing Strategy](#testing-strategy)
9. [Standards for /core/docs](#standards-for-coredocs)
10. [Future Extensions](#future-extensions)

---

## State Model

### RuntimeValue Type Definition

All variables in the runtime are strongly typed:

```typescript
type RuntimeValue =
  | string
  | number
  | boolean
  | null
  | RuntimeObject
  | RuntimeArray;

interface RuntimeObject {
  [key: string]: RuntimeValue;
}

type RuntimeArray = RuntimeValue[];
```

### RuntimeState Interface

The runtime maintains a global state object:

```typescript
interface RuntimeState {
  variables: Map<string, RuntimeValue>;
  modified: Set<string>; // Track which vars changed
  timestamp: number; // Last modification time
}
```

### Variable Naming Conventions

**Rules:**

- **User variables** start with `$` (e.g., `$gold`, `$player`, `$inventory`)
- **Database variables** start with `$db` (e.g., `$db.npc`, `$db.fact`)
- **Reserved:** `$runtime`, `$config`, `$time` (system variables)
- **Case-sensitive:** `$Gold` ≠ `$gold`
- **Valid chars:** `[a-zA-Z0-9_]` (no spaces, no hyphens)

---

## Variable Naming & Access

### Path Access Notation

Variables support nested access via **dot notation** and **bracket notation**:

```
$player.hp              // Object property access
$inventory[0]           // Array index access
$inventory[0].name      // Nested: array → property
$party[1].skills[2]     // Deep nesting: array → prop → array
$db.npc[*].name         // Wildcard: all NPCs' names (returns array)
```

### Wildcard Operator (`[*]`)

Used in database queries to select multiple items:

```
$db.npc[*].name         // Array of all NPC names
$db.fact[*].when        // Array of all fact timestamps
$db.poi[*].type         // Array of all POI types
```

### Type Coercion Rules

When accessing undefined properties:

```
$undefined_var → null
$player.missing_prop → null
$inventory[99] → null
$db.npc[*] where npc is missing → []
```

---

## Database Binding

### Configuration Format (YAML Frontmatter)

```yaml
---
title: "The Lost Treasure"
data:
  db:
    provider: sqlite # or "notion", "mysql"
    path: "./data/world.sqlite.db"
    namespace: "$db" # Variable namespace (always $db)
    bind:
      - "$db.npc[*]" # Bind all NPCs
      - "$db.fact[*]" # Bind all facts
      - "$db.poi[*]" # Bind all points of interest
      - "$db.tile_edges[*]" # Bind movement graph
---
# Document Content...
```

### SQLite Provider (v0 — Read-Only)

**Schema Requirements:**

```sql
CREATE TABLE npc (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  location TEXT,
  hp INTEGER DEFAULT 100,
  items JSON,          -- ["sword", "shield"]
  flags JSON,          -- {"hostile": false, "questgiver": true}
  data JSON            -- Custom fields
);

CREATE TABLE fact (
  id INTEGER PRIMARY KEY,
  category TEXT,
  statement TEXT,
  when INTEGER,        -- Timestamp
  data JSON
);

CREATE TABLE poi (
  id INTEGER PRIMARY KEY,
  name TEXT,
  type TEXT,           -- "town", "dungeon", "npc"
  x INTEGER,
  y INTEGER,
  description TEXT
);

CREATE TABLE tile_edges (
  from_id INTEGER,
  to_id INTEGER,
  distance INTEGER,
  blocked BOOLEAN DEFAULT FALSE,
  PRIMARY KEY(from_id, to_id)
);
```

**Read Semantics:**

- `$db.npc[*]` → Select all rows from npc table (array of objects)
- `$db.npc[0]` → First NPC (by row order)
- `$db.npc[*].name` → Array of all NPC names
- `$db.fact.category` → Does NOT work (fact is singular, must use [*])
- `$db.poi[*] WHERE type="town"` → Does NOT work (no SQL syntax)

**Future (v1.0.4.0+):**

- Write support for `SET` operations on bound variables
- Notion database provider (CRUD via Notion API)
- MySQL provider support
- Filter expressions in variable paths

### Notion Provider (Future v1.0.4.0+)

**Configuration:**

```yaml
data:
  db:
    provider: notion
    database_id: "a1b2c3d4e5f6g7h8i9j0"
    api_key: "$NOTION_KEY" # From environment
    namespace: "$db"
    bind:
      - "$db.characters[*]"
      - "$db.locations[*]"
      - "$db.quests[*]"
```

**Design:** Notion database columns map to object properties; rows are array elements.

---

## Runtime Blocks

### STATE Block — Initialize Variables

**Purpose:** Declare and initialize variables at document load

**Syntax:**

````markdown
```state
$gold = 100
$player = {
  name: "Hero",
  hp: 50,
  skills: ["sword", "magic"]
}
$inventory = []
$current_location = "starting_village"
```
````

**Semantics:**

- Executed once when document loads
- Variables persist across user interactions
- Objects and arrays supported
- String literals use double quotes: `"value"`
- Number literals: `100`, `3.14`, `-5`
- Boolean: `true`, `false`
- Null: `null`

**Example:**

```state
$party = []
$round = 1
$npc_met = { tavern_keeper: false, elder: false }
```

### SET Block — Modify State

**Purpose:** Update variables based on user actions or conditions

**Supported Operations:**

```typescript
// Increment/Decrement
$gold += 10;
$hp -= 5;
$round += 1;

// Assign
$player.name = "NewName";
$current_location = "forest";

// Toggle
$npc_met.tavern_keeper = true;

// Array operations
$inventory.push("sword");
$inventory.pop();
$inventory[0] = "new_item";

// Object operations
$player.skills[2] = "flying";
$player.level = 5;
```

**Rules:**

- Executed when triggered by `NAV` action or `FORM` submission
- Always mutates state (return value is new state)
- Type must match original (can't assign string to number var)
- Array push/pop: `$arr.push(value)`, `$arr.pop()`

**Example:**

```set
$gold -= 10
$player.hp += 20
$inventory.push("healing_potion")
$current_location = "forest"
```

### FORM Block — Collect User Input

**Purpose:** Interactive form for collecting typed user data

**Syntax:**

````markdown
```form
name: text
age: number
agreed: toggle
class: choice(warrior|mage|rogue)
interests: checkbox(combat|magic|stealth|diplomacy)
```
````

**Field Types:**

| Type                | Input                  | Result            |
| ------------------- | ---------------------- | ----------------- |
| `text`              | Text input             | String            |
| `number`            | Number input           | Number            |
| `toggle`            | Checkbox               | Boolean           |
| `choice(a\|b\|c)`   | Radio buttons/dropdown | One value         |
| `checkbox(a\|b\|c)` | Multiple checkboxes    | Array of selected |

**Submission:**

When user submits form, each field updates a variable with same name (prefixed `$`):

```
Form field "name" → $name = "user_input"
Form field "age" → $age = 25
Form field "agreed" → $agreed = true
Form field "class" → $class = "mage"
Form field "interests" → $interests = ["magic", "diplomacy"]
```

**Example:**

```form
player_name: text
starting_gold: number
enable_hardcore: toggle
difficulty: choice(easy|normal|hard)
```

User fills form → `$player_name`, `$starting_gold`, `$enable_hardcore`, `$difficulty` updated

### IF/ELSE Block — Conditional Rendering

**Purpose:** Show/hide content based on state conditions

**Syntax:**

````markdown
```if $gold >= 100
You have enough gold to buy a sword.
```

```else
You need more gold. Current: $gold
```
````

**Conditions:**

| Operator | Example                              | Meaning          |
| -------- | ------------------------------------ | ---------------- |
| `==`     | `$hp == 50`                          | Equals           |
| `!=`     | `$status != "alive"`                 | Not equals       |
| `>`      | `$level > 5`                         | Greater than     |
| `<`      | `$gold < 10`                         | Less than        |
| `>=`     | `$round >= 3`                        | Greater or equal |
| `<=`     | `$hp <= 25`                          | Less or equal    |
| `&&`     | `$hp > 0 && $gold >= 10`             | AND              |
| `\|\|`   | `$status == "alive" \|\| $round > 1` | OR               |

**Rendering:**

- If condition is true, render the block content
- If false, render `else` block if present
- Nested conditions supported

**Example:**

```if $gold >= 50 && $player.has_map
You can afford the horse.
```

```else if $gold >= 20
You can afford basic supplies.
```

### NAV Block — Navigation/Choices

**Purpose:** Present user choices that trigger SET operations

**Syntax:**

````markdown
```nav
- "Buy sword" → $gold -= 50; $inventory.push("sword")
- "Buy shield" → $gold -= 30; $inventory.push("shield")
- "Save and leave" → $current_location = "town"
```
````

**Structure:**

- Each line is a choice (button)
- Format: `"Display Text" → SET_OPERATION[; SET_OPERATION]*`
- Multiple operations separated by `;`

**With Conditions (Gates):**

````markdown
```nav
- "Attack" [when: $player.hp > 0] → $round += 1
- "Flee" [when: $gold > 0] → $current_location = "escape_route"
- "Surrender" [when: always] → $status = "captured"
```
````

- `[when: CONDITION]` shows choice only if condition is true
- Omit `when` to always show

**Example:**

```nav
- "Enter tavern" → $current_location = "tavern"; $npc_met.tavern_keeper = true
- "Go to forest" → $current_location = "forest"
- "Check inventory" → (navigate to inventory panel)
```

### PANEL Block — ASCII Graphics / Rich Layout

**Purpose:** Render fixed-width ASCII art or structured layout

**Syntax:**

````markdown
```panel
┌─────────────────┐
│    Inn Room     │
│                 │
│  *   •   *      │
│                 │
│ Door  Table  NPC│
└─────────────────┘
```
````

**Features:**

- Box drawing characters preserved
- Fixed-width font rendering
- Can be conditional (wrap in `if` block)
- No interactivity (use `NAV` for choices)

**Example:**

```panel
INVENTORY:
━━━━━━━━━━━━━━━━━
Gold: $gold  GP
━━━━━━━━━━━━━━━━━
Items:
 • Sword
 • Shield
 • Potion
```

### MAP Block — Sprite Viewport

**Purpose:** Render a scrollable/pannable map with sprite at center

**Syntax:**

````markdown
```map
provider: sprite_sheet.json
viewport: 5x5
player_x: $player.x
player_y: $player.y
tile_source: $db.tile_edges[*]
```
````

**Configuration:**

- `provider` — JSON file path with sprite definitions
- `viewport` — Grid size (WxH), player always centered
- `player_x`, `player_y` — Current position (integer coords)
- `tile_source` — Array of tile nodes from database

**Interaction:**

- Arrow keys to move player
- Each move: `$player.x += 1` etc, persist to state
- Can be gated by conditions (MAP shows only if `$has_compass`)

**Example:**

```map
provider: world_sprites.json
viewport: 7x7
player_x: $player.location_x
player_y: $player.location_y
tile_source: $db.poi[*]
```

---

## Execution Flow

### Document Load Sequence

```
1. Parse markdown into blocks
2. Extract frontmatter (data.db binding, title, etc)
3. Initialize DB connection (SQLite/Notion)
4. Execute STATE block(s)
   - Initialize variables
   - Bind external DB tables
5. Render document
   - Evaluate IF/ELSE conditions
   - Show/hide content
   - Render PANEL blocks as-is
   - Render FORM, NAV, MAP blocks as interactive
6. Ready for user input
```

### User Action Sequence

```
User clicks button/submits form
→ Extract action (SET operations or navigation)
→ Execute SET block operations
→ Update runtime state
→ Re-evaluate IF/ELSE conditions
→ Re-render document
→ Return to waiting for input
```

### Database Binding Sequence

On document load:

```typescript
// 1. Parse frontmatter
const config = parseFrontmatter(doc);

// 2. Connect to database
const db = await Database.connect(config.data.db.provider, config.data.db.path);

// 3. Load bound tables
for (const binding of config.data.db.bind) {
  const table = extractTableName(binding); // "$db.npc[*]" → "npc"
  const data = await db.select(table);
  state.set(`db.${table}`, data);
}

// 4. STATE block then has access to $db.npc, $db.fact, etc.
```

---

## Interpolation Rules

### Text Interpolation

Variables in text blocks are interpolated with `$` prefix:

```markdown
You have $gold gold pieces and $inventory.length items.

Current location: $current_location
Player: $player.name (Level $player.level)

Party members:

- $party[0].name (HP: $party[0].hp)
- $party[1].name (HP: $party[1].hp)
```

**Rules:**

- `$variable` expands to variable value
- `$var.prop` expands to property value
- `$arr[i]` expands to array element
- Undefined variables → empty string
- Numbers and booleans → string representation

### Code Block Interpolation

Within runtime blocks, variables are evaluated:

```
SET: $gold = $player.reward_amount
IF: $party.length > 3
FORM submission: updates $form_field with user input
```

**Type Safety:**

- SET operations check type compatibility
- IF conditions evaluate booleans
- FORM defaults from existing variable types

### Implementation Pseudocode

```typescript
function interpolateText(text: string, state: RuntimeState): string {
  return text.replace(
    /\$([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*|\[\d+\])*)/g,
    (match, path) => {
      const value = resolvePath(path, state);
      return value === null ? "" : String(value);
    }
  );
}

function resolvePath(path: string, state: RuntimeState): RuntimeValue {
  const parts = path.split(/\.|\[|\]/).filter((p) => p);
  let current = state.variables.get(parts[0]);

  for (let i = 1; i < parts.length; i++) {
    if (current === null || current === undefined) return null;
    if (typeof current === "object") {
      current = Array.isArray(current)
        ? current[parseInt(parts[i])]
        : current[parts[i]];
    } else {
      return null;
    }
  }

  return current;
}
```

---

## Example: Complete Interactive Story

### File: adventure.md

````markdown
---
title: "The Merchant's Quest"
data:
  db:
    provider: sqlite
    path: "./data/merchants.sqlite.db"
    namespace: "$db"
    bind:
      - "$db.npc[*]"
      - "$db.quest[*]"
      - "$db.item[*]"
---

# The Merchant's Quest

You wake in your merchant's stall at the market.

```state
$gold = 500
$inventory = []
$reputation = { blacksmith: 0, mage: 0, guard: 0 }
$quest_active = false
$quest_id = null
$current_location = "market"
```

## Market

````if $current_location == "market"
You are in the bustling market square.

```panel
┌──────────────────┐
│   Market Square  │
│                  │
│ [B]  [M]  [G]   │
│ lack mage uard   │
└──────────────────┘
````

**NPCs here:**

```if $quest_active
A hooded figure watches you carefully.
```

````if !$quest_active
```nav
- "Talk to blacksmith" → $current_location = "blacksmith"
- "Visit mage's tower" → $current_location = "mage"
- "Speak to guard" → $current_location = "guard"
````
````

````

## Blacksmith's Forge

```if $current_location == "blacksmith"
You enter the blacksmith's forge, thick with smoke.

**"Welcome, merchant!"** the blacksmith calls out.

```if $reputation.blacksmith >= 3
"Old friend! Great to see you. I have a special job..."

```form
offer_price: number
accept_job: toggle
````

```else
"Hmph. Haven't seen you in ages. What do you want?"
```

```nav
- "Sell inventory" → (process sale)
- "Leave" → $current_location = "market"
```

````

## Quests

**Available quests from database:**

```if !$quest_active
$db.quest[*].title:

```nav
- "Quest: $db.quest[0].title" [when: $gold >= $db.quest[0].cost] → $quest_active = true; $quest_id = 0
- "Quest: $db.quest[1].title" [when: $gold >= $db.quest[1].cost] → $quest_active = true; $quest_id = 1
- "Decline quests" → $current_location = "market"
````

````

```if $quest_active
**Active Quest:** $db.quest[$quest_id].title
Reward: $db.quest[$quest_id].reward gold

```nav
- "Return to market" → $current_location = "market"
````

```

---

## End

Thank you for playing.

```

**Key Features Demonstrated:**

✅ STATE: Initialize game variables  
✅ IF/ELSE: Conditional rendering (location, quest status, reputation)  
✅ FORM: Collect player input (offer price, job acceptance)  
✅ NAV: Present choices with SET operations  
✅ Database binding: Read NPC and quest data from SQLite  
✅ Text interpolation: Display variable values inline  
✅ PANEL: Render ASCII map

---

## Testing Strategy

### Unit Tests

```typescript
describe("RuntimeState", () => {
  test("Parse STATE block", () => {
    const state = parseState(`$gold = 100\n$player = {name: "Hero"}`);
    expect(state.get("gold")).toBe(100);
    expect(state.get("player")).toEqual({ name: "Hero" });
  });

  test("Resolve variable paths", () => {
    state.set("player", { name: "Hero", skills: ["sword"] });
    expect(resolvePath("player.name", state)).toBe("Hero");
    expect(resolvePath("player.skills[0]", state)).toBe("sword");
    expect(resolvePath("missing", state)).toBe(null);
  });

  test("Evaluate IF conditions", () => {
    state.set("gold", 100);
    expect(evalCondition("$gold >= 100", state)).toBe(true);
    expect(evalCondition("$gold < 50", state)).toBe(false);
  });

  test("Execute SET operations", () => {
    state.set("gold", 100);
    executeSet("$gold -= 10", state);
    expect(state.get("gold")).toBe(90);
  });
});
```

### Integration Tests

```typescript
describe("Document Execution", () => {
  test("Load document with STATE and database binding", async () => {
    const doc = parseMarkdown(adventureMarkdown);
    const state = await executeDocument(doc);

    expect(state.get("gold")).toBe(500);
    expect(state.get("db.npc")).toBeDefined(); // Database loaded
    expect(Array.isArray(state.get("db.npc"))).toBe(true);
  });

  test("Handle user navigation action", () => {
    const doc = parseMarkdown(adventureMarkdown);
    state.executeAction('current_location = "blacksmith"');

    const rendered = renderDocument(doc, state);
    expect(rendered).toContain("blacksmith's forge");
  });

  test("FORM submission updates state", () => {
    const form = parseForm("price: number\naccept: toggle");
    const input = { price: 100, accept: true };
    applyFormSubmission(form, input, state);

    expect(state.get("price")).toBe(100);
    expect(state.get("accept")).toBe(true);
  });
});
```

### Manual Test Workflows

1. **Complete story playthrough:**

   - Load adventure.md
   - Verify STATE initializes correctly
   - Navigate through all locations
   - Verify IF/ELSE conditions show/hide content
   - Submit forms and verify state changes
   - Check variable interpolation in text

2. **Database binding:**

   - Load document with SQLite binding
   - Verify $db.\* variables populated
   - Test array access $db.npc[*].name
   - Test wildcard operator

3. **Edge cases:**
   - Missing variable reference → renders as empty
   - Type mismatch in SET → error message
   - Undefined condition in IF → treated as false
   - Array out of bounds → null

---

## Standards for /core/docs

When TypeScript runtime is implemented (v1.0.3.0), create these 8 files in `/core/docs/`:

### 1. TYPESCRIPT-RUNTIME.md

**Content:** Overview of TypeScript runtime architecture, design decisions, offline-first execution, comparison with Python runtime.

### 2. BLOCKS.md

**Content:** Reference for all 7 runtime block types (STATE, SET, FORM, IF/ELSE, NAV, PANEL, MAP). Copy from "Runtime Blocks" section above.

### 3. STATE-MODEL.md

**Content:** Variable types, naming conventions, path access notation, type coercion. Copy from "State Model" and "Variable Naming & Access" sections above.

### 4. DATABASE-BINDING.md

**Content:** Configuration format, SQLite schema, Notion provider (future), read-only semantics, migration from Python. Extended from "Database Binding" section above.

### 5. EXAMPLES.md

**Content:** Complete working stories, tutorials, common patterns. Include adventure.md + 2-3 additional examples.

### 6. TESTING.md

**Content:** Unit test examples, integration test examples, manual workflows. Copy from "Testing Strategy" section above.

### 7. MIGRATION.md

**Content:** How to migrate .md files from Python runtime to TypeScript runtime (should be compatible, but document any differences).

### 8. FAQB.md

**Content:** Frequently asked questions, troubleshooting, performance tips.

---

## Future Extensions

### Loops (v1.0.4.0)

```
for($item in $inventory) {
  Name: $item.name
  Cost: $item.cost
}
```

### Computed Properties (v1.0.4.0)

```state
$total_gold = computed(() => sum($db.coins[*].value))
$party_level = computed(() => avg($party[*].level))
```

### Operators & Functions (v1.0.4.0)

```
$damage = $weapon.base + $player.strength / 2
$full_name = concat($player.first, " ", $player.last)
$items_count = count($inventory)
$max_hp = max($party[*].hp)
```

### Persistent State (v1.0.4.0)

```yaml
persistent:
  - "$player.name"
  - "$reputation.*"
  - "$completed_quests"
```

Variables marked as persistent survive document close/reopen.

### Write Support for Databases (v1.0.4.0)

```set
$db.npc[0].hp -= 10  // Update NPC record
INSERT $db.item[*] = { name: "new_item", cost: 50 }
```

---

## References

- [Move 1: Runtime Blocks + Notion Sync](move-1-runtime-blocks-notion-sync.md) — Implementation plan
- [TypeScript Runtime Specification](typescript-runtime-database-standards.md) — This file
- [Example Scripts](../../dev/roadmap/) — example-script.md, example-sqlite.db.md, movement-demo-script.md
- [AGENTS.md](../../AGENTS.md) — Architecture overview
- [Roadmap](roadmap.md) — v1.0.3.0 timeline

---

_Last Updated: 2026-01-15_  
_For v1.0.3.0+ implementation_
