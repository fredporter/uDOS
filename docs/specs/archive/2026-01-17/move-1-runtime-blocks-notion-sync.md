# Move 1 Extended: Notion Sync + Runtime Blocks + Database Binding

**Purpose:** Extend Notion sync to handle runtime blocks, state declarations, and external DB bindings  
**Scope:** Move 1 (Notion Integration) implementation  
**Dependencies:** [Notion-Compatible Blocks](notion-compatible-blocks.md) + [TypeScript Runtime Standards](typescript-runtime-database-standards.md)

---

## Overview

When syncing Markdown documents to Notion, we must preserve:

1. **Runtime Block Metadata** — `state`, `set`, `form`, `if/else`, `nav`, `panel`, `map`
2. **State Declarations** — Initial `$variables` + their types
3. **Database Binding Config** — External SQLite/Notion data sources
4. **Variable Interpolation** — `$var` references in text and code

This allows Notion to store the complete document while preserving executable behavior for desktop (Python) and mobile (TypeScript) runtimes.

---

## Notion Sync Strategy for Runtime Blocks

### Mapping: Runtime Blocks → Notion API

#### 1. STATE Block → Code Block + Metadata

**Markdown Source:**

````markdown
```state
$name = "Alice"
$hp = 100
$inventory = []
```
````

````

**Notion API Block:**
```json
{
  "type": "code",
  "code": {
    "language": "typescript",
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "$name = \"Alice\"\n$hp = 100\n$inventory = []"
        }
      }
    ],
    "caption": [
      {
        "type": "text",
        "text": {
          "content": "[uDOS:STATE] Initialize variables"
        }
      }
    ]
  }
}
````

**Metadata Storage** (SQLite):

```sql
-- block_mappings table
INSERT INTO block_mappings (
  notion_block_id,
  notion_page_id,
  local_path,
  block_type,
  block_metadata
) VALUES (
  'xyz...',
  'abc...',
  'memory/ucode/story.md',
  'state',
  JSON('{"variables": ["name", "hp", "inventory"]}'')
);
```

#### 2. FORM Block → Code Block + Metadata

**Markdown Source:**

````markdown
```form
- var: $name
  type: text
  label: "Your name"
  required: true
```
````

````

**Notion API Block:**
```json
{
  "type": "code",
  "code": {
    "language": "typescript",
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "- var: $name\n  type: text\n  label: \"Your name\"\n  required: true"
        }
      }
    ],
    "caption": [
      {
        "type": "text",
        "text": {
          "content": "[uDOS:FORM] Collect user input"
        }
      }
    ]
  }
}
````

#### 3. IF Block → Toggle (Collapsible) Heading

**Markdown Source:**

````markdown
```if $coins >= 10
You can afford it!
```
````

````

**Notion API Block:**
```json
{
  "type": "heading_2",
  "heading_2": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "if $coins >= 10"
        }
      }
    ],
    "color": "default",
    "is_toggleable": true
  },
  "children": [
    {
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "You can afford it!"
            }
          }
        ]
      }
    }
  ]
}
````

#### 4. DB Binding (YAML Frontmatter) → Notion Properties

**Markdown Source:**

```yaml
---
title: "Interactive Story"
data:
  db:
    provider: sqlite
    path: "./data/world.sqlite.db"
    namespace: "$db"
    bind:
      - var: "$db.npc[*].name"
---
```

**Notion Representation:**

- Store in page properties (custom fields):
  - `db_provider` → "sqlite"
  - `db_path` → "./data/world.sqlite.db"
  - `db_namespace` → "$db"
  - `db_bindings` → JSON array

```json
{
  "properties": {
    "title": { "title": [{ "text": { "content": "Interactive Story" } }] },
    "db_provider": { "rich_text": [{ "text": { "content": "sqlite" } }] },
    "db_path": {
      "rich_text": [{ "text": { "content": "./data/world.sqlite.db" } }]
    },
    "db_namespace": { "rich_text": [{ "text": { "content": "$db" } }] },
    "db_bindings": {
      "rich_text": [
        { "text": { "content": "[\"$db.npc[*].name\", \"$db.poi[*]\"]" } }
      ]
    }
  }
}
```

### Bidirectional Sync: Notion → Markdown

When downloading a page from Notion:

1. **Parse page properties** — Extract DB binding config
2. **Parse code blocks** — Identify by caption `[uDOS:*]`
3. **Parse toggles** — Convert to `if/else` blocks
4. **Reconstruct markdown** — With frontmatter + runtime blocks

**Example Conversion:**

Notion blocks:

```json
[
  {
    "type": "code",
    "code": {
      "language": "typescript",
      "rich_text": [...],
      "caption": [{ "text": { "content": "[uDOS:STATE]" } }]
    }
  },
  {
    "type": "paragraph",
    "paragraph": { "rich_text": [...] }
  },
  {
    "type": "heading_2",
    "heading_2": { "is_toggleable": true, ... }
  }
]
```

Reconstructed markdown:

````markdown
---
title: "..."
data:
  db:
    provider: sqlite
    ...
---

```state
$name = "Alice"
...
```
````

Regular paragraph text.

```if condition
Toggle content
```

````

---

## Conflict Resolution for Runtime Blocks

When a runtime block changes in both Notion and locally:

### Scenario 1: STATE Block Modified

**Local Change:** Changed variable type
```markdown
Before: $coins = 0
After:  $coins = 0.0  (float)
````

**Notion Change:** Changed variable name

```markdown
Before: $coins
After: $gold
```

**Resolution Options:**

1. **Last-write-wins** — Later timestamp wins
2. **Local-priority** — Keep local changes
3. **Notion-priority** — Keep Notion changes
4. **Manual** — Flag for user review (UI dialog)

**Recommended:** Last-write-wins (deterministic, predictable)

### Scenario 2: DB Binding Path Changed

**Local:** `./data/world.sqlite.db`  
**Notion:** `./data/new-world.sqlite.db`

**Resolution:** Merge (union) both paths, notify user to select.

---

## SQLite Schema Extensions

### Existing Tables

```sql
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY,
  notion_id TEXT,
  change_type TEXT,
  payload JSON,
  status TEXT,
  created_at DATETIME,
  synced_at DATETIME,
  error_message TEXT
);

CREATE TABLE block_mappings (
  id INTEGER PRIMARY KEY,
  local_path TEXT,
  notion_page_id TEXT,
  notion_block_id TEXT,
  block_type TEXT,
  last_synced DATETIME,
  conflict_resolution TEXT
);
```

### New Columns for Runtime Metadata

```sql
-- Extend block_mappings to track runtime block metadata
ALTER TABLE block_mappings ADD COLUMN (
  block_metadata JSON,        -- Runtime block config (form fields, conditions, etc)
  variable_names TEXT,        -- Comma-separated: $name, $coins, etc
  db_binding JSON,            -- DB connection config
  caption TEXT                -- Notion caption [uDOS:TYPE]
);

-- New table: runtime_variables (for type tracking)
CREATE TABLE runtime_variables (
  id INTEGER PRIMARY KEY,
  block_id TEXT,              -- From block_mappings.id
  var_name TEXT,              -- $coins
  type TEXT,                  -- 'number', 'string', 'boolean', 'object', 'array'
  initial_value TEXT,         -- JSON serialized
  created_at DATETIME,
  updated_at DATETIME
);

-- New table: db_bindings (track external DB connections per document)
CREATE TABLE db_bindings (
  id INTEGER PRIMARY KEY,
  document_path TEXT,         -- memory/ucode/story.md
  provider TEXT,              -- 'sqlite', 'notion', 'mysql'
  connection_path TEXT,       -- ./data/world.sqlite.db
  namespace TEXT,             -- $db
  bind_config JSON,           -- [{"var": "$db.npc[*].name"}]
  last_verified DATETIME,
  status TEXT                 -- 'valid', 'missing', 'error'
);
```

---

## Implementation Checklist for Move 1

### Phase A: Block Mapping (Week 1)

- [x] Design block → Notion mapping
- [ ] Implement `BlockMapper.parse_markdown()`
- [ ] Implement `BlockMapper.to_notion_blocks()` (includes captions)
- [ ] Implement `BlockMapper.from_notion_blocks()` (read captions)
- [ ] Handle DB binding in frontmatter
- [ ] Unit tests for all block types

**Files:**

- `dev/goblin/services/block_mapper.py`
- `dev/goblin/tests/test_block_mapper.py`

### Phase B: Webhook Handler (Week 1-2)

- [ ] Create `/api/v0/notion/webhook` endpoint
- [ ] Verify webhook signatures
- [ ] Queue block changes (sync_queue)
- [ ] Extract block metadata (caption parsing)
- [ ] Unit tests for webhook validation

**Files:**

- `dev/goblin/services/notion_sync_service.py`
- `dev/goblin/routes/notion.py`

### Phase C: Bidirectional Sync (Week 2-3)

- [ ] Implement `sync_to_notion()` (local .md → Notion)
- [ ] Implement `sync_from_notion()` (Notion → local .md)
- [ ] Handle runtime block metadata during sync
- [ ] Preserve DB binding config
- [ ] Conflict resolution for runtime blocks
- [ ] Update SQLite schema (block_metadata, runtime_variables, db_bindings)
- [ ] Integration tests

**Files:**

- `dev/goblin/services/sync_executor.py`
- `dev/goblin/schemas/conflict_resolution.py`

### Phase D: Testing (Week 3)

- [ ] Test all runtime block types (state, set, form, if, nav)
- [ ] Test DB binding (SQLite read, path resolution)
- [ ] Test variable interpolation in text
- [ ] Test conflict resolution scenarios
- [ ] Test with real Notion workspace

**Files:**

- `dev/goblin/tests/test_runtime_blocks.py`
- `dev/goblin/tests/test_db_binding.py`

---

## Example: Complete Sync Workflow

### Step 1: Create Local Document

File: `memory/ucode/adventure.md`

````markdown
---
title: "Adventure Game"
runtime: "udos-ts-runtime"
data:
  db:
    provider: sqlite
    path: "./data/adventure.sqlite.db"
    namespace: "$db"
    bind:
      - var: "$db.npc"
      - var: "$db.poi"
---

# Adventure Game

```state
$name = "Hero"
$hp = 100
$coins = 0
```
````

Welcome, $name!

```form
- var: $name
  type: text
  label: "Your name"
```

```if $coins >= 50
You're rich!
```

````

### Step 2: Sync to Notion

```bash
curl -X POST http://localhost:8767/api/v0/notion/sync/to-notion \
  -H "Content-Type: application/json" \
  -d '{
    "page_id": "abc123...",
    "local_path": "memory/ucode/adventure.md"
  }'
````

**Result in Notion:**

- Page title: "Adventure Game"
- Page properties: db_provider, db_path, db_namespace, db_bindings
- Blocks: CODE (state), PARAGRAPH (welcome), CODE (form), HEADING_2 (if toggle)

### Step 3: Edit in Notion

User changes STATE block variable:

```
$hp = 100  →  $hp = 200
```

### Step 4: Webhook Fires

Notion sends webhook to `POST /api/v0/notion/webhook`:

- Block type: `code`
- Block ID: `xyz...`
- Page ID: `abc123...`
- Content: Updated STATE block

### Step 5: Sync Back to Local

```bash
# Automatic via webhook, or manual:
curl -X POST http://localhost:8767/api/v0/notion/sync/from-notion \
  -H "Content-Type: application/json" \
  -d '{
    "page_id": "abc123...",
    "output_path": "memory/ucode/adventure.md"
  }'
```

**Result:**

- Local `adventure.md` updated with new $hp value
- Metadata in SQLite: block_metadata, runtime_variables, db_bindings

---

## Benefits

✅ **Notion-Native Runtime Blocks** — No special sync layer, blocks are standard code blocks with metadata  
✅ **Type Safety** — Variable types tracked in SQLite  
✅ **DB Binding Preserved** — External data sources sync alongside code  
✅ **Conflict Resolution** — Clear merge strategy  
✅ **Mobile-Ready** — TypeScript runtime can read same metadata from local SQLite  
✅ **Debuggable** — All state changes logged in sync_queue

---

## References

- [Notion-Compatible Blocks](notion-compatible-blocks.md)
- [TypeScript Runtime Standards](typescript-runtime-database-standards.md)
- [Move 1 Quick Start](../../dev/goblin/MOVE-1-QUICK-START.md)
- [BlockMapper Implementation](../../dev/goblin/BLOCK-MAPPER-IMPLEMENTATION.md)

---

_This specification enables Move 1 to seamlessly sync executable runtime blocks with Notion._
