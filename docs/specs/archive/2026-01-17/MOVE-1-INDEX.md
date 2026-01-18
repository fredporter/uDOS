# Move 1 Specifications Index

**Mission:** Notion-Compatible Blocks + Database Integration  
**Status:** Architecture complete, implementation ready  
**Timeline:** 26-34 hours over 3-4 weeks

---

## Core Documents (Read in Order)

### 1. **[Notion-Compatible Block Architecture](notion-compatible-blocks.md)**

- Block type mapping (standard + runtime)
- Markdown syntax examples
- Notion API JSON payloads
- Implementation strategy overview
- **Read first:** Design foundation

### 2. **[Move 1: Runtime Blocks + Notion Sync](move-1-runtime-blocks-notion-sync.md)**

- How runtime blocks (state, form, if, etc.) map to Notion
- Database binding config storage
- Bidirectional sync strategy
- Conflict resolution for executable blocks
- SQLite schema extensions
- Implementation checklist
- **Read second:** Execution details

### 3. **[TypeScript Runtime Database Standards](typescript-runtime-database-standards.md)**

- State model ($variables, types, paths)
- External DB binding (SQLite, Notion providers)
- Runtime block specifications (state, set, form, if, nav, panel, map)
- Variable interpolation rules
- Execution flow
- Example workflows
- **Read third:** Runtime behavior

---

## Implementation Guides

### 4. **[Move 1 Quick Start](../../dev/goblin/MOVE-1-QUICK-START.md)**

- Notion integration setup (API key, webhook)
- Phase-by-phase implementation plan (A-D)
- Test workflow
- **Use during:** Phase A-D implementation

### 5. **[BlockMapper Implementation Plan](../../dev/goblin/BLOCK-MAPPER-IMPLEMENTATION.md)**

- Complete Python code scaffold
- Data classes (BlockType, RichText, Block, DBBinding)
- Parser logic (markdown → Block objects)
- Converter logic (Block → Notion API, Notion → markdown)
- Unit tests
- **Use for:** Phase A coding

---

## Example Scripts

### 6. **[Example Interactive Script](../../dev/roadmap/example-script.md)**

- Complete demonstration of all features
- State initialization
- Forms, conditionals, navigation
- Panel ASCII graphics
- Map viewport rendering
- External SQLite DB binding
- **Study:** Design patterns

### 7. **[Example SQLite Schema](../../dev/roadmap/example-sqlite.db.md)**

- Complete schema (facts, npc, poi, tile_edges)
- Seed data
- Movement demo script
- **Reference:** DB structure

---

## Architecture Decisions

### 8. **[ADR-0002: TypeScript Runtime for Mobile/iPad](../../docs/decisions/ADR-0002-typescript-runtime-for-mobile.md)**

- Why TypeScript runtime is required
- Platform strategy (desktop Python vs mobile TS)
- Rationale and trade-offs
- **Context:** Why we're building this way

---

## Integration Points

### With Core

When TypeScript runtime is created in v1.0.3.0, create documentation in `/core/docs/`:

```
core/docs/
  TYPESCRIPT-RUNTIME.md          # Main spec
  BLOCKS.md                       # Block reference
  STATE-MODEL.md                  # Variables + types
  DATABASE-BINDING.md             # DB connection
  EXAMPLES.md                     # Example scripts
  TESTING.md                      # Test strategy
  MIGRATION.md                    # Python → TypeScript
```

### With App

The Tauri app (`app-beta/`) will:

- Parse markdown documents with runtime blocks
- Call Goblin server (port 8767) for complex execution
- Display interactive elements (forms, buttons, maps)
- Store state locally (SQLite)

### With Notion

- Sync markdown ↔ Notion pages
- Preserve runtime block metadata
- Support external DB binding
- Conflict resolution for concurrent edits

---

## Phase Breakdown

### Phase A: Block Mapping (Week 1)

**Output:** `BlockMapper` class can parse/convert all block types

**Key Files:**

- `dev/goblin/services/block_mapper.py`
- `dev/goblin/tests/test_block_mapper.py`

**Reference:** [BlockMapper Implementation](../../dev/goblin/BLOCK-MAPPER-IMPLEMENTATION.md)

**Checkpoint:** All block types parse ↔ convert ↔ parse (roundtrip)

### Phase B: Webhook Handler (Week 1-2)

**Output:** Notion webhooks received, queued, ready for sync

**Key Files:**

- `dev/goblin/routes/notion.py`
- `dev/goblin/services/notion_sync_service.py`

**Reference:** [Move 1 Quick Start — Phase B](../../dev/goblin/MOVE-1-QUICK-START.md#phase-b-webhook-handler-week-1-2)

**Checkpoint:** Webhook signatures verified, queue stores changes

### Phase C: Bidirectional Sync (Week 2-3)

**Output:** Sync local .md ↔ Notion, conflict resolution

**Key Files:**

- `dev/goblin/services/sync_executor.py`
- `dev/goblin/schemas/conflict_resolution.py`

**Reference:** [Move 1: Runtime Blocks + Notion Sync](move-1-runtime-blocks-notion-sync.md#phase-c-bidirectional-sync-week-2-3)

**Checkpoint:** Bidirectional sync works, conflicts resolved

### Phase D: Testing (Week 3)

**Output:** All block types tested with real Notion workspace

**Test Coverage:**

- Standard blocks (h1-h3, p, lists, quotes)
- Runtime blocks (state, form, if, nav)
- DB binding (SQLite read, path resolution)
- Variable interpolation
- Conflict scenarios

**Reference:** [Move 1 Quick Start — Phase D](../../dev/goblin/MOVE-1-QUICK-START.md#phase-d-testing-week-3)

**Checkpoint:** Zero critical bugs, all tests passing

---

## Data Model Summary

### Runtime Variables

```typescript
type RuntimeValue =
  | string
  | number
  | boolean
  | null
  | { [key: string]: RuntimeValue }
  | RuntimeValue[];

interface RuntimeState {
  [varName: string]: RuntimeValue;
}
```

### Runtime Blocks

| Block     | Purpose         | Notion Maps To       |
| --------- | --------------- | -------------------- |
| `state`   | Init variables  | `code` (w/ caption)  |
| `set`     | Mutate state    | `code` (w/ caption)  |
| `form`    | Collect input   | `code` (w/ caption)  |
| `if/else` | Conditional     | `toggle` (h2)        |
| `nav`     | Navigation      | `callout` (buttons)  |
| `panel`   | ASCII graphics  | `code` + `paragraph` |
| `map`     | Sprite viewport | `code` (special)     |

### DB Binding (YAML)

```yaml
data:
  db:
    provider: sqlite # or 'notion', 'mysql'
    path: "./data/world.sqlite.db"
    namespace: "$db"
    bind:
      - var: "$db.fact.weather"
      - var: "$db.npc[*].name"
```

---

## SQLite Schema (Move 1)

### Existing Tables

- `sync_queue` — Queued Notion changes
- `block_mappings` — Local ↔ Notion mapping

### New Tables

- `runtime_variables` — Track variable types + initial values
- `db_bindings` — External data source config per document

### New Columns

- `block_mappings.block_metadata` — Runtime block config
- `block_mappings.variable_names` — Comma-separated variable list
- `block_mappings.db_binding` — DB connection info
- `block_mappings.caption` — Notion caption (`[uDOS:TYPE]`)

---

## Testing Strategy

### Unit Tests

```python
# Markdown parsing
test_parse_heading
test_parse_paragraph
test_parse_code_block
test_parse_state_block
test_parse_form_block
test_parse_if_block

# Notion conversion
test_to_notion_heading
test_to_notion_state_block
test_to_notion_form_block
test_to_notion_if_toggle

# Roundtrip
test_markdown_notion_markdown_roundtrip
test_variable_interpolation
test_db_binding_config_parse
```

### Integration Tests

```python
# Full document sync
test_sync_to_notion_complete_document
test_sync_from_notion_complete_document
test_conflict_resolution_state_block
test_conflict_resolution_form_block
test_db_binding_preserved_during_sync
```

### Manual Testing

1. Create test Notion workspace
2. Create test .md file with all block types
3. Sync to Notion
4. Edit in Notion
5. Verify webhook
6. Sync back
7. Verify no data loss

---

## Success Criteria

✅ All block types parse ↔ convert ↔ parse (Phase A)  
✅ Webhooks received, signatures verified (Phase B)  
✅ Bidirectional sync works, no data loss (Phase C)  
✅ All tests passing, 0 critical bugs (Phase D)  
✅ Works with real Notion workspace  
✅ Runtime variables tracked in SQLite  
✅ DB binding config preserved during sync  
✅ Conflict resolution deterministic

---

## Next Steps

1. **Review** [Notion-Compatible Block Architecture](notion-compatible-blocks.md)
2. **Review** [Move 1: Runtime Blocks + Notion Sync](move-1-runtime-blocks-notion-sync.md)
3. **Create Notion Integration** — https://www.notion.so/my-integrations
4. **Configure Goblin** — `dev/goblin/config/goblin.json`
5. **Start Phase A** — Implement `BlockMapper` using [code scaffold](../../dev/goblin/BLOCK-MAPPER-IMPLEMENTATION.md)

---

## References

- **Roadmap:** [v1.0.2.0 Plan](../../docs/roadmap.md#move-1-notion-sync-integration-python-based)
- **Dev Log:** [2026-01-15 Entry](../../docs/devlog/2026-01.md)
- **Notion API:** https://developers.notion.com/reference/block

---

_Move 1 bridges desktop (Python) and mobile (TypeScript) runtimes via Notion-compatible blocks and external database binding._
