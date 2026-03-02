# Tools: Navigation and Spatial

Updated: 2026-03-03
Status: active how-to reference

## Scope

Use these tools for navigation, grid awareness, file-space mapping, and bookmark-style movement.

## Tools

### `ucode_map`

Show the spatial file tree or a focused area.

Example calls:
```python
ucode_map(area="")
ucode_map(area="vault")
ucode_map(area="workspace")
```

### `ucode_grid`

Show or toggle the grid coordinate system.

Example calls:
```python
ucode_grid(mode="show")
ucode_grid(mode="toggle")
```

### `ucode_anchor`

Manage named bookmarks or anchors.

Example calls:
```python
ucode_anchor(action="list")
ucode_anchor(action="add", name="inbox")
ucode_anchor(action="delete", name="inbox")
```

### `ucode_goto`

Jump to named locations or direct coordinates.

Example calls:
```python
ucode_goto(location="inbox")
ucode_goto(location="0,5")
```

### `ucode_find`

Search files, logs, or content across the workspace.

Example calls:
```python
ucode_find(query="backup")
ucode_find(query="python", type_="file")
ucode_find(query="error", type_="log")
```

## Common Uses

- inspect workspace or vault layout
- jump between named working locations
- search content before editing or cleanup
- coordinate spatial rendering with grid-aware workflows

