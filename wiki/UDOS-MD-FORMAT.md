# uDOS.md Document Format (v1.0.0.52)

**Last Updated:** 2026-01-24
**Status:** Active Standard
**Author:** uDOS Engineering

`.udos.md` is the primary executable document format for uDOS. It combines:

- **Human-readable Markdown** for documentation
- **YAML frontmatter** for metadata
- **Embedded uPY scripts** for automation
- **State blocks** for persistent data

This single-file format enables offline-first, privacy-preserving workflows that work across TUI, Tauri, and mobile interfaces.

---

## File Structure

````markdown
---
title: Document Title
version: 1.0.0
author: username
created: 2026-01-05
tags: [survival, knowledge]
permissions:
  execute: true
  network: false
  file_write: false
---

# Human-Readable Content

Regular Markdown content here...

```upy
# Executable uPY script block
if location.distance_to(target) < 100:
    notify("You're close!")
```
````

```json udos:state
{
  "counter": 0,
  "last_run": null,
  "checkpoints": []
}
```

More Markdown content...

````

---

## YAML Frontmatter

Required metadata block at the start:

```yaml
---
title: string          # Document title (required)
version: string        # Semver version (required)
author: string         # Author username
created: date          # ISO 8601 date
modified: date         # Last modified date
tags: [string]         # Categorization tags
description: string    # Brief description

# Permissions (default: all false except execute)
permissions:
  execute: true        # Allow uPY execution
  network: false       # Allow network access (Wizard only)
  file_write: false    # Allow file system writes
  file_read: true      # Allow file system reads
  mesh: false          # Allow MeshCore operations

# Optional: Spatial data
location:
  latitude: number
  longitude: number
  tile_code: string
  radius_m: number     # Geofence radius
---
````

---

## Markdown Content

Standard Markdown with extensions:

- **Headers:** `#`, `##`, `###`, etc.
- **Lists:** `-`, `*`, `1.`, etc.
- **Code blocks:** ` ``` ` with syntax highlighting
- **Links:** `[text](url)` or `[text](file.md)`
- **Images:** `![alt](path)` (local paths preferred)
- **Tables:** Standard Markdown tables
- **Blockquotes:** `>` for callouts

---

## uPY Script Blocks

Executable Python-subset code:

````markdown
```upy
# Variables and conditionals
count = state.counter + 1
if count > 10:
    result = "Complete!"
else:
    result = f"Step {count} of 10"

# Update state
state.counter = count
state.last_run = now()
```
````

**Supported uPY 0.2 Features:**

- Variables (`SET`, `GET`, assignments)
- Conditionals (`if`, `elif`, `else`)
- Loops (`for`, `while`, `break`, `continue`)
- Functions (user-defined)
- Math operations
- String operations
- State manipulation

**Not Supported (requires API):**

- File I/O (`FILE.READ`, `FILE.WRITE`)
- Network operations
- MeshCore commands
- System commands

---

## State Blocks

Persistent JSON state within the document:

````markdown
```json udos:state
{
  "counter": 0,
  "checkpoints": ["start"],
  "user_data": {
    "name": "",
    "progress": 0
  }
}
```
````

**State Rules:**

- One state block per document
- JSON format only
- Automatically saved on script execution
- Accessible in uPY as `state.key`

---

## Execution Model

### Client-Side (No Python Required)

Runs in JavaScript runtime (Tauri/browser):

```
.udos.md → Parser → AST → Transpile to JS → Sandboxed Execution
```

**Available:**

- All uPY 0.2 features
- State manipulation
- UI interactions

### API-Based (Python Required)

Runs via uDOS API server:

```
.udos.md → API Request → Python Runtime → Response
```

**Required for:**

- File operations
- MeshCore commands
- Knowledge search
- System commands

### Hybrid Routing

The runtime automatically routes:

```python
# Client-side (instant)
count = state.counter + 1

# API-routed (requires server)
files = FILE.LIST("*.md")
```

---

## Examples

### Simple Counter

````markdown
---
title: Click Counter
version: 1.0.0
permissions:
  execute: true
---

# Counter

Click the button to increment.

Current count: **{state.count}**

```upy
state.count = state.count + 1
notify(f"Count is now {state.count}")
```
````

```json udos:state
{ "count": 0 }
```

````

### Checklist Workflow

```markdown
---
title: Morning Routine
version: 1.0.0
tags: [routine, daily]
---

# Morning Routine Checklist

- [ ] Wake up at 6:00
- [ ] Drink water
- [ ] Exercise (30 min)
- [ ] Shower
- [ ] Breakfast

```upy
completed = sum(1 for item in state.items if item.done)
total = len(state.items)
state.progress = completed / total * 100
notify(f"Progress: {state.progress:.0f}%")
````

```json udos:state
{
  "items": [
    { "task": "Wake up", "done": false },
    { "task": "Water", "done": false },
    { "task": "Exercise", "done": false },
    { "task": "Shower", "done": false },
    { "task": "Breakfast", "done": false }
  ],
  "progress": 0
}
```

```

---

## File Naming

- **Extension:** `.udos.md` (required for execution)
- **Convention:** `kebab-case-name.udos.md`
- **Location:** `memory/` directory tree

**Examples:**
- `morning-routine.udos.md`
- `project-tracker.udos.md`
- `location-sydney-cbd.udos.md`

---

## Security

### Permissions Model

| Permission | Default | Description |
|------------|---------|-------------|
| `execute` | `true` | Run uPY scripts |
| `file_read` | `true` | Read local files |
| `file_write` | `false` | Write local files |
| `network` | `false` | Network access |
| `mesh` | `false` | MeshCore operations |

### Sandbox Rules

1. **No DOM access** in client-side execution
2. **No arbitrary code** - uPY subset only
3. **Timeout limits** - Prevent infinite loops
4. **State isolation** - Each document's state is separate
5. **Permission prompts** - User confirms elevated operations

---

## Related Documentation

- [KNOWLEDGE-LINKING-SYSTEM.md](KNOWLEDGE-LINKING-SYSTEM.md) — Document frontmatter
- [UDOS-MD-TEMPLATE-SPEC.md](UDOS-MD-TEMPLATE-SPEC.md) — Templates and shortcodes
- [../../docs/development-streams.md](../../docs/development-streams.md) — Implementation roadmap

---

**Status:** Active Architecture Standard
**Repository:** https://github.com/fredporter/uDOS
```
