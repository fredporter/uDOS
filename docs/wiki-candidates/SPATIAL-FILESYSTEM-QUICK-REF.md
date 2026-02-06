# Spatial Filesystem Quick Reference

**Status:** v1.0.7.1  
**Implementation:** Complete  
**TUI Integration:** Ready

---

## @Workspace Syntax

Access workspaces with `@name/path` notation:

```
@sandbox/file.md      → memory/sandbox/file.md (user writable)
@bank/data.db         → vault-md/bank/data.db (user writable)
@shared/docs          → memory/shared/docs (collaborative)
@wizard/config.json   → memory/wizard/config.json (admin only)
@knowledge/guide.md   → /knowledge/guide.md (admin curated)
@dev/script.py        → /dev/script.py (admin development)
```

---

## TUI Commands

### Workspace Management

```
WORKSPACE list @sandbox              # List all files
WORKSPACE read @sandbox/story.md     # Read file content
WORKSPACE write @sandbox/new.md      # Create/write file (interactive)
WORKSPACE delete @sandbox/old.md     # Delete file
WORKSPACE INFO                       # Show access levels & config
WORKSPACE HELP                       # Show help
```

### Location Tagging

```
LOCATION tag @sandbox/story.md L300-AB15    # Tag file with grid location
LOCATION find L300-AB15                      # Find all files at location
LOCATION find L300-AC20                      # Find files at another location
```

**Format:** `L{layer}-{cell}` where:
- Layer: L300–L305 (surface), L299–L294 (caves), L293+ (deep)
- Cell: AA10–DC39 (80×30 grid)

Examples:
- `L300-AA10` (top-left surface)
- `L300-DC39` (bottom-right surface)
- `L299-BA25` (caves)
- `L293-AA01` (deep substrate)

### Content Discovery

```
TAG list @sandbox                    # Show all tags in workspace
TAG find forest adventure            # Find files with any of these tags
TAG find quest danger                # OR logic: quest OR danger
```

### Binder (Multi-Chapter Projects)

```
BINDER open @sandbox/my-project      # Open binder, show chapters
BINDER list @sandbox/my-novel        # List chapters (same as open)
BINDER add @sandbox/project ch1.md   # Add chapter to binder
```

---

## Front-Matter Format

All markdown files support YAML front-matter:

```yaml
---
# Basic
title: Story Title
description: A brief summary
tags: [forest, adventure, quest]

# Spatial
grid_locations:
  - L300-AB15
  - L300-AC20

# Binder
binder_id: my-novel
chapter: 1

# Metadata
created_at: 2026-01-30T10:00:00Z
updated_at: 2026-01-30T14:30:00Z
author: username

# Custom fields
custom_key: custom_value
another_field: value
---

# Your content here
```

---

## Python API

### Initialize

```python
from core.services.spatial_filesystem import SpatialFilesystem, UserRole

# User access level
fs = SpatialFilesystem(user_role=UserRole.USER)

# Admin access
fs = SpatialFilesystem(user_role=UserRole.ADMIN)

# Guest access (read-only)
fs = SpatialFilesystem(user_role=UserRole.GUEST)
```

### File Operations

```python
# Write
location = fs.write_file('@sandbox/story.md', '# Story\n\nContent')

# Read
content = fs.read_file('@sandbox/story.md')

# Delete
fs.delete_file('@sandbox/story.md')

# List
files = fs.list_workspace('@sandbox')
for file in files:
    print(file.relative_path, file.metadata.tags)
```

### Location Tagging

```python
# Tag file with location
fs.tag_location('@sandbox/story.md', 'L300-AB15')

# Add another location
fs.tag_location('@sandbox/story.md', 'L300-AC20')

# Find files at location
files = fs.find_by_location('L300-AB15')
for file in files:
    print(f"  {file.relative_path}")
```

### Content Tags

```python
# Extract tags from file
tags = fs.extract_tags('@sandbox/story.md')
# → ['forest', 'adventure']

# Find files by tags
files = fs.find_by_tags(['forest', 'adventure'])
for file in files:
    print(f"  {file.relative_path} - {file.metadata.title}")

# OR logic: returns files with ANY of the tags
files = fs.find_by_tags(['quest', 'danger'])
```

### Binders

```python
# Open binder
binder = fs.open_binder('@sandbox/my-novel')

# Add chapters
binder.add_chapter('intro.md', '# Introduction', chapter_num=1, title='Prologue')
binder.add_chapter('ch1.md', '# Chapter 1', chapter_num=2, title='The Journey')

# List chapters
chapters = binder.list_chapters()
for ch in chapters:
    print(f"  Ch {ch['chapter']}: {ch['title']}")

# Access file
content = fs.read_file('@sandbox/my-novel/intro.md')
```

### Metadata

```python
# Extract metadata from file
metadata = fs._extract_metadata(file_path)
print(metadata.title)
print(metadata.tags)
print(metadata.grid_locations)
print(metadata.binder_id)

# Update front-matter
new_metadata = ContentMetadata(
    title='Updated Title',
    tags=['new', 'tags'],
    grid_locations=['L300-AB15']
)
updated_content = fs._update_frontmatter(content, new_metadata)
```

### Access Control

```python
# Check if user can access workspace
if fs.has_access(WorkspaceType.KNOWLEDGE):
    print("Can read knowledge base")

# Ensure access (raises PermissionError if denied)
fs.ensure_access(WorkspaceType.WIZARD)

# Get path for workspace
path = fs.get_workspace_path(WorkspaceType.SANDBOX)
```

---

## Handler API

### Initialize

```python
from core.commands.spatial_filesystem_handler import SpatialFilesystemHandler

handler = SpatialFilesystemHandler()
```

### Commands

```python
# Workspace
result = handler.workspace_list('@sandbox')
result = handler.workspace_read('@sandbox/story.md')
result = handler.workspace_write('@sandbox/new.md', 'content')
result = handler.workspace_delete('@sandbox/old.md')
result = handler.get_workspace_info()

# Location
result = handler.location_tag('@sandbox/story.md', 'L300-AB15')
result = handler.location_find('L300-AB15')

# Tags
result = handler.tag_list('@sandbox')
result = handler.tag_find('forest', 'adventure')

# Binder
result = handler.binder_open('@sandbox/my-novel')
result = handler.binder_add('@sandbox/my-novel', 'ch1.md', title='Chapter One')
```

### Dispatch

```python
from core.commands.spatial_filesystem_handler import dispatch_spatial_command

result = dispatch_spatial_command(handler, ['WORKSPACE', 'list', '@sandbox'])
result = dispatch_spatial_command(handler, ['LOCATION', 'tag', '@sandbox/story.md', 'L300-AB15'])
result = dispatch_spatial_command(handler, ['HELP'])
```

---

## Examples

### Example: Create Interactive Story

```python
fs = SpatialFilesystem(user_role=UserRole.USER)

# Create binder
binder = fs.open_binder('@sandbox/adventure')

# Chapter 1: Tavern (location L300-AA10)
ch1 = '''---
title: The Tavern
grid_locations: [L300-AA10]
tags: [start, tavern, meeting]
binder_id: adventure
chapter: 1
---

You enter a dimly lit tavern. An old man sits in the corner.
'''
binder.add_chapter('ch1_tavern.md', ch1, 1, 'The Tavern')

# Chapter 2: Forest (locations L300-AB15, L300-AC20)
ch2 = '''---
title: Forest Path
grid_locations: [L300-AB15, L300-AC20]
tags: [forest, danger, quest]
binder_id: adventure
chapter: 2
---

The forest is dark and mysterious.
'''
binder.add_chapter('ch2_forest.md', ch2, 2, 'Forest Path')

# Query
tavern_stories = fs.find_by_tags(['tavern'])
forest_files = fs.find_by_location('L300-AB15')
```

### Example: Knowledge Base Search

```python
# Admin creates knowledge
admin_fs = SpatialFilesystem(user_role=UserRole.ADMIN)
admin_fs.write_file('@knowledge/fire-making.md', '# Fire Making\nSteps...')
admin_fs.tag_location('@knowledge/fire-making.md', 'L300-DB20')

# User discovers knowledge
user_fs = SpatialFilesystem(user_role=UserRole.USER)
survival_guides = user_fs.find_by_tags(['survival', 'skill'])
location_guides = user_fs.find_by_location('L300-DB20')
```

### Example: TUI Session

```
[uCODE] > WORKSPACE INFO
📊 Workspace Configuration:
   User Role: user

  ✅ @sandbox  (memory/sandbox)
      Personal sandbox for experimentation
  ✅ @bank     (vault-md/bank)
      Personal data vault
  ✅ @shared   (memory/shared)
      Shared workspace for collaboration
  ❌ @wizard   (memory/wizard)
      Wizard service workspace (internal)
  ✅ @knowledge (knowledge)
      Knowledge base (read-only)
  ❌ @dev      (dev)
      Development workspace (admin only)

[uCODE] > WORKSPACE list @sandbox
📁 Files in @sandbox:
  📄 story.md [forest, adventure] @ L300-AB15
  📄 notes.md [personal]
  📄 quest-log.md [quest, tracking]

[uCODE] > BINDER open @sandbox/the-novel
📚 Binder: @sandbox/the-novel
   Chapters: 2
  Ch 1: The Tavern
  Ch 2: Forest Path

[uCODE] > TAG find forest
🔍 Files tagged with: forest
  📄 @sandbox/story.md
     My Adventure Story
     Tags: forest, adventure
  📄 @sandbox/quest-log.md
     Quest Log
     Tags: quest, tracking

[uCODE] > LOCATION find L300-AB15
📍 Files at L300-AB15:
  📄 @sandbox/story.md
     My Adventure Story
```

---

## Architecture

### Indexes

1. **Location Index** — Fast spatial queries
   - Key: `L300-AB15`
   - Value: Set of file paths

2. **Tag Index** — Content discovery
   - Key: `forest` (lowercase)
   - Value: Set of file paths

3. **Binder Index** — Project organization
   - Key: `my-novel`
   - Value: Ordered list of chapter paths

4. **Metadata Cache** — Performance
   - Key: File path
   - Value: ContentMetadata object

### Workspace Security

```
User Role          @sandbox @bank @shared @wizard @knowledge @dev
─────────────────────────────────────────────────────────────────
Admin              RW       RW     RW      RW      RW         RW
User               RW       RW     RW      ✗       RO         ✗
Guest              ✗        ✗      RO      ✗       RO         ✗

RW = Read/Write
RO = Read-Only
✗  = Denied
```

---

## Integration Points

### TS Markdown Runtime

Read location from file → track state spatially

```markdown
---
grid_locations: [L300-AB15]
---

$player.location = "L300-AB15"
```

### Grid Runtime

Render files at location → show on map as sprites

```typescript
const files = fs.find_by_location('L300-AB15');
// Render as map markers
```

### File Parsers

Parse files → write spatially → tag with location

```python
fs.write_file('@sandbox/data.table.md', csv_to_markdown(data))
fs.tag_location('@sandbox/data.table.md', 'L300-DB50')
```

### Binders

Organize chapters → compile → generate docs

```python
binder = fs.open_binder('@sandbox/my-book')
# Chapters auto-ordered by chapter number
```

---

## Testing

Run full test suite:

```bash
pytest core/tests/test_spatial_filesystem.py -v

# Coverage:
# - Access control (RBAC)
# - File operations (CRUD)
# - Workspace resolution
# - Metadata extraction
# - Grid location tagging
# - Content-tag indexing
# - Binder operations
# - Front-matter updates
# - Error handling
# - TUI command dispatch
```

---

**See Also:**
- [SPATIAL-FILESYSTEM.md](SPATIAL-FILESYSTEM.md) — Full documentation
- [ROADMAP.md](ROADMAP.md) — Development roadmap
- `core/services/spatial_filesystem.py` — Implementation
- `core/commands/spatial_filesystem_handler.py` — TUI handler
