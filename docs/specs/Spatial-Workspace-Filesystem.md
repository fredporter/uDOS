# Workspace Filesystem Architecture

**Status:** v1.0.7.0 — v1.3-aligned (coordinates required)
**Date:** 2026-01-30
**Author:** uDOS Development Team

---

## Overview

The **Spatial Workspace Filesystem** bridges filesystem organisation with grid-based spatial computing. It enables:

- **Workspace hierarchy** with role-based access control (RBAC)
- **Grid location tagging** (L###-Cell → file mapping)
- **Content-tag indexing** (metadata extraction & discovery)
- **Binder integration** (folder-based multi-chapter projects)
- **Front-matter standardization** (YAML metadata in .md files)

### Vault Contract Context

The workspace layer operates on runtime paths under `memory/`. Keep this split:

- `vault/` = distributable template scaffold (tracked)
- `core/framework/seed/vault/` = canonical starter seed source (tracked)
- `memory/vault/` = active runtime workspace used by `@vault`

---

## Workspace Hierarchy

Vault-first workspaces, accessed via `@workspace` syntax:

| Workspace      | Path                   | Access Level | Purpose                    |
| -------------- | ---------------------- | ------------ | -------------------------- |
| `@user/sandbox`     | `memory/vault/@user/sandbox`        | User / Admin | Drafts & experimentation   |
| `@binders`     | `memory/vault/@binders` | User / Admin | Binder roots + local sandboxes |
| `@vault`       | `memory/vault`          | User / Admin | Primary knowledge store    |
| `@inbox`       | `memory/inbox`          | User / Admin | Intake/imports             |
| `@public`      | `memory/contributions`  | User / Admin | Public/open/published      |
| `@submissions` | `memory/submissions`    | User / Admin | Submission intake          |
| `@personal`    | `memory/private`        | User / Admin | Explicit private shares    |
| `@shared`      | `memory/sharing`        | User / Admin | Proximity-verified sharing |
| `@wizard`      | `memory/wizard`         | Admin only   | Wizard service (internal)  |
| `@knowledge`   | `/knowledge`            | Admin only   | Knowledge base (curated)   |
| `@dev`         | `/dev`                  | Admin only   | Development workspace      |

v1.5 note:
- `@sandbox` is deprecated as a dedicated workspace.
- Use `@user/sandbox/` for personal drafts.
- Use binder-local sandbox paths under `@binders/<binder_id>/sandbox/` for mission work-in-progress.

**Role Hierarchy:**
- **Guest**: Read-only access to @public/@shared
- **User**: Read/write vault workspaces; read /knowledge
- **Admin**: All workspaces, all operations

---

**TUI Commands (canonical):**
```
PLACE LIST @user/sandbox                      # List all files
PLACE READ @user/sandbox/story.md             # Show file content
PLACE DELETE @user/sandbox/old.md             # Delete file
PLACE INFO                               # Show workspace config
```

---

### 2. Grid Location Tagging

Connect files to spatial grid coordinates (`L###-Cell[-Zz]` format):

```python
# Tag file with location (implied z=0)
fs.tag_location('@user/sandbox/story.md', 'L300-AB15')

# Find files at location
files = fs.find_by_location('L300-AB15')

# Multiple locations per file (explicit z plane)
fs.tag_location('@user/sandbox/story.md', 'L300-AC20-Z2')
```

**TUI Commands (canonical):**
```
PLACE TAG @user/sandbox/story.md L300-AB15        # Tag file with location
PLACE FIND L300-AB15                          # Find files at location
PLACE TAG @user/sandbox/story.md L300-AC20-Z2      # Tag file with z-axis
```

**Front-matter Example:**
```yaml
---
title: Forest Entrance
grid_locations:
  - L300-AB15
  - L300-AC20
coordinates:
  system: WGS84
  lat: 37.7749
  lon: -122.4194
---
```


---

### 3. Content-Tag Indexing

Extract and search by tags:

```python
# Extract tags from file
tags = fs.extract_tags('@user/sandbox/story.md')
# → ['forest', 'adventure', 'npc']

# Find files by tags
files = fs.find_by_tags(['forest', 'adventure'])
# → All files tagged with either tag
```

**TUI Commands (canonical):**
```
PLACE TAGS @user/sandbox                  # Show all tags in workspace
PLACE SEARCH forest adventure quest  # Find files with any tag
```

**Front-matter Example:**
```yaml
---
title: Forest Story
tags:
  - forest
  - adventure
  - quest
---
```

---

### 4. Metadata & Front-Matter

All files support standardized YAML front-matter:

```yaml
---
# Essential
title: Story Title
description: A brief description
tags: [tag1, tag2]

# Spatial
grid_locations:
  - L300-AB15
  - L300-AC20

# Binder
binder_id: my-project
chapter: 1

# Metadata
created_at: 2026-01-30T10:00:00Z
updated_at: 2026-01-30T14:30:00Z
author: username

# Custom
custom_field: custom_value
---

# Content
```

**Extracted Automatically:**
```python
metadata = fs._extract_metadata(file_path)
# → ContentMetadata(
#     title='Story Title',
#     tags=['tag1', 'tag2'],
#     grid_locations=['L300-AB15', 'L300-AC20'],
#     ...
#   )
```

---

### 5. Binder Integration

Organize multi-chapter projects in folders:

```python
# Open binder-local sandbox
binder = fs.open_binder('@binders/my-novel/sandbox')

# Add chapters
binder.add_chapter('intro.md', '# Introduction', chapter_num=1, title='Intro')
binder.add_chapter('ch1.md', '# Chapter 1', chapter_num=2, title='The Journey Begins')

# List chapters
chapters = binder.list_chapters()
# → [
#     {'path': Path(...), 'filename': 'intro.md', 'chapter': 1, 'title': 'Intro'},
#     {'path': Path(...), 'filename': 'ch1.md', 'chapter': 2, 'title': 'The Journey Begins'},
#   ]
```

**TUI Commands:**
```
BINDER open @binders/my-novel/sandbox           # Open binder
BINDER list @binders/my-novel/sandbox           # List chapters (same as open)
BINDER add @binders/my-novel/sandbox ch2.md     # Add chapter
```

**Directory Structure:**
```
memory/vault/@binders/my-novel/sandbox/
├── intro.md              # Chapter 1
├── ch1.md                # Chapter 2
├── ch2.md                # Chapter 3
├── epilogue.md           # Chapter N
└── metadata.json         # Optional binder config
```

---

## Architecture

### Index System

Three in-memory indexes for fast lookup:

1. **Location Index** — `L###-Cell → {file_paths}`
   - Fast spatial queries
   - Multi-file locations supported

2. **Tag Index** — `tag_name → {file_paths}`
   - Case-insensitive matching
   - Multi-tag queries (OR logic)

3. **Binder Index** — `binder_id → [chapter_paths]`
   - Chapter ordering
   - Multi-chapter projects

4. **Metadata Cache** — `file_path → ContentMetadata`
   - Lazy parsing on first access
   - TTL invalidation on file change

### Access Control Flow

```
User Request
  ↓
Resolve @workspace reference
  ↓
Check user.role in workspace.roles
  ↓ Allowed: proceed
  ↓ Denied: raise PermissionError
  ↓
Get workspace absolute path
  ↓
Perform file operation
  ↓
Update indexes (if write)
  ↓
Return result
```

---

## Integration with Stream 1

### TS Markdown Runtime

Connect script state to spatial locations:

```markdown
---
title: My Interactive Story
grid_locations:
  - L300-AB15
tags: [interactive, story]
binder_id: adventure-series
chapter: 3
---

## Start

$player = { pos: "L300-AB15", name: "Alice" }

You are in the forest at L300-AB15.
```

**Runtime can:**
- Read location from front-matter
- Track player position spatially
- Query nearby files by location
- Multi-chapter story progression via binder

### Grid Runtime

Files tagged with locations appear on map:

```typescript
// Grid rendering with spatial files
const files_here = fs.find_by_location('L300-AB15');
// → Render as sprites/markers on viewport

const nearby = fs.find_by_location('L300-AC20');
// → Render adjacent cells
```

### File Parsers

Integrate file operations with parsers:

```python
# Write parsed CSV as spatial file
fs.write_file('@user/sandbox/data.table.md', csv_to_markdown(data))
fs.tag_location('@user/sandbox/data.table.md', 'L300-DB50')

# Find all data files in knowledge base
data_files = fs.find_by_tags(['data', 'reference'])
```

---

## Usage Examples

### Example 1: Story Project with Locations

```python
fs = SpatialFilesystem(user_role=UserRole.USER)

# Create multi-chapter story
binder = fs.open_binder('@binders/the-quest/sandbox')

# Chapter 1: Tavern
content1 = '''---
title: The Tavern
grid_locations: [L300-AA10]
tags: [tavern, meeting, intro]
---

You enter a dimly lit tavern...
'''
binder.add_chapter('ch1_tavern.md', content1, 1, 'The Tavern')

# Chapter 2: Forest
content2 = '''---
title: Forest Path
grid_locations: [L300-AB15, L300-AC16]
tags: [forest, danger, quest]
---

The path winds through ancient trees...
'''
binder.add_chapter('ch2_forest.md', content2, 2, 'Forest Path')

# Query
forest_stories = fs.find_by_tags(['forest'])
tavern_locations = fs.find_by_location('L300-AA10')
```

### Example 2: Knowledge Base Organization

```python
# Admin populates knowledge base
fs = SpatialFilesystem(user_role=UserRole.ADMIN)

# Add skill guides at locations
fs.write_file('@knowledge/fire-making.md', '# Fire Making\n...')
fs.tag_location('@knowledge/fire-making.md', 'L300-DB20')
fs.write_file('@user/sandbox/my-fire-notes.md', 'My notes...')
fs.tag_location('@user/sandbox/my-fire-notes.md', 'L300-DB20')

# Users can query by skill or location
users_fs = SpatialFilesystem(user_role=UserRole.USER)
survival_guides = users_fs.find_by_tags(['survival', 'skill'])
location_guides = users_fs.find_by_location('L300-DB20')
```

### Example 3: TUI Workflow

```
[uCODE] > PLACE LIST @user/sandbox
📁 Files in @user/sandbox:
  📄 story.md [forest, adventure] @ L300-AB15
  📄 notes.md [personal]
  📄 quest-log.md [quest, tracking]

[uCODE] > PLACE SEARCH quest
🔍 Files tagged with: quest
  📄 @user/sandbox/quest-log.md
     My Quest Log
     Tags: quest, tracking

[uCODE] > PLACE TAG @user/sandbox/story.md L300-AC20
✅ Tagged @user/sandbox/story.md → L300-AC20

[uCODE] > PLACE FIND L300-AB15
📍 Files at L300-AB15:
  📄 @user/sandbox/story.md
     My Adventure Story

[uCODE] > BINDER open @binders/the-novel/sandbox
📚 Binder: @binders/the-novel/sandbox
   Chapters: 3
  Ch 1: Prologue
  Ch 2: Act One
  Ch 3: Climax
```

---

## Security Model

### Access Levels

```
┌─────────────────────────────────────────────────┐
│ Admin                                           │
│  ├─ memory/vault/@user/sandbox (own)                        │
│  ├─ memory/vault (own)                          │
│  ├─ memory/inbox (read/write)                   │
│  ├─ memory/contributions (read/write)           │
│  ├─ memory/private (read/write)                 │
│  ├─ memory/sharing (read/write)                 │
│  ├─ memory/wizard (read/write) [admin workspace]│
│  ├─ /knowledge (curate/manage)                  │
│  └─ /dev (development)                          │
├─────────────────────────────────────────────────┤
│ User                                            │
│  ├─ memory/vault/@user/sandbox (read/write own)             │
│  ├─ memory/vault (read/write own)               │
│  ├─ memory/inbox (read/write)                   │
│  ├─ memory/contributions (read/write)           │
│  ├─ memory/private (read/write)                 │
│  ├─ memory/sharing (read/write)                 │
│  ├─ memory/wizard (denied)                      │
│  ├─ /knowledge (read only)                      │
│  └─ /dev (denied)                               │
├─────────────────────────────────────────────────┤
│ Guest                                           │
│  ├─ memory/vault/@user/sandbox (denied)                     │
│  ├─ memory/vault (denied)                       │
│  ├─ memory/inbox (denied)                       │
│  ├─ memory/contributions (read only)            │
│  ├─ memory/private (denied)                     │
│  ├─ memory/sharing (read only)                  │
│  ├─ memory/wizard (denied)                      │
│  ├─ /knowledge (read only)                      │
│  └─ /dev (denied)                               │
└─────────────────────────────────────────────────┘
```

### Best Practices

1. **Always initialize with user role** — defaults to USER
2. **Call ensure_access()** before admin operations
3. **Front-matter is metadata only** — validate in application logic
4. **Grid locations are application-defined** — no enforcement of format
5. **Tags are case-insensitive** — normalize to lowercase for queries
6. **Seed data sync** — Migration/seeder services now import `memory/spatial/anchors.json` + `memory/spatial/places.json` into the spatial SQLite (via `.udos/state.db` or `05_DATA/sqlite/udos.db`), ensuring new anchor/place refs are available to `/api/renderer/spatial/*`.

---

## Testing

Run comprehensive test suite:

```bash
pytest core/tests/test_spatial_filesystem.py -v

# Output:
# test_spatial_filesystem.py::TestSpatialFilesystem::test_user_access_to_workspace PASSED
# test_spatial_filesystem.py::TestSpatialFilesystem::test_user_denied_admin_workspace PASSED
# test_spatial_filesystem.py::TestSpatialFilesystem::test_write_and_read_file PASSED
# ... (25+ tests)
```

**Test Coverage:**
- ✅ Access control (RBAC)
- ✅ File operations (CRUD)
- ✅ Workspace resolution
- ✅ Metadata extraction
- ✅ Grid location tagging
- ✅ Content-tag indexing
- ✅ Binder operations
- ✅ Front-matter updates
- ✅ Error handling
- ✅ TUI command dispatch

---

## Future Enhancements

- [ ] File versioning (history, rollback)
- [ ] Collaboration features (comments, locking)
- [ ] Full-text search integration
- [ ] Template system for front-matter
- [ ] Auto-index rebuild on filesystem changes
- [ ] Cache persistence (SQLite backend)
- [ ] Performance optimization (lazy loading)
- [ ] Multi-user workspace with permissions
- [ ] File sync with cloud storage
- [ ] Tagging suggestions (ML-based)

---

**Status:** Production v1.0.7.0
**Maintained by:** uDOS Engineering
**Last Updated:** 2026-01-30
