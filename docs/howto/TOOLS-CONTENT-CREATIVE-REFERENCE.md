# Tools: Content and Creative

Updated: 2026-03-03
Status: active how-to reference

## Scope

Use these tools for reading, stories, games, drawing, sound, formatting, and destructive recovery operations.

Vibe Dev Mode exposes only `ucode_read` from this category. Story, play, draw, audio, empire, undo, print, format, and destructive operations remain part of the full TUI/operator surface.

## Tools

### `ucode_story`

Read and manage story-style content.

```python
ucode_story(action="list")
ucode_story(action="read", story_id="adventure-1")
ucode_story(action="resume", story_id="adventure-1")
ucode_story(action="status")
```

### `ucode_talk`

Interact with characters or NPC-style prompts.

```python
ucode_talk(target="guide")
ucode_talk(target="merchant", message="What do you have?")
```

### `ucode_read`

Read markdown or text content from the workspace or vault.

```python
ucode_read(path="docs/guide.md")
ucode_read(path="vault/notes/project", section="Installation")
```

### `ucode_play`

Start, resume, or inspect interactive games.

```python
ucode_play()
ucode_play(game="adventure", action="start")
ucode_play(game="roguelike", action="continue")
ucode_play(game="puzzle", action="status")
```

### `ucode_draw`

Render ASCII or panel-style output.

```python
ucode_draw(panel="map")
ucode_draw(panel="hud")
ucode_draw(panel="")
```

### `ucode_sonic`

Control sound and ambient audio.

```python
ucode_sonic(action="status")
ucode_sonic(action="play", track="ambient")
ucode_sonic(action="stop")
ucode_sonic(action="list")
```

### `ucode_music`

Manage music playback and playlists.

```python
ucode_music(action="status")
ucode_music(action="play", playlist="focus")
ucode_music(action="next")
ucode_music(action="list")
```

### `ucode_empire`

Inspect or manage the multi-node Wizard network.

```python
ucode_empire(action="status")
ucode_empire(action="build", node="node-1")
ucode_empire(action="expand")
ucode_empire(action="report")
```

### `ucode_destroy`

Dangerous destructive cleanup operation.

```python
ucode_destroy(target="cache")
ucode_destroy(target="logs")
ucode_destroy(target="--all", confirm=True)
```

### `ucode_undo`

Undo recent actions from backup state.

```python
ucode_undo(steps=1)
ucode_undo(steps=5)
```

### `ucode_print`

Pretty-print files or data structures.

```python
ucode_print(content="file.md", format="markdown")
ucode_print(content="data.json", format="json")
ucode_print(content="table.csv", format="table")
```

### `ucode_format`

Convert between data formats.

```python
ucode_format(input="config.json", style="yaml")
ucode_format(input="data.yaml", style="toml")
ucode_format(input="old-format.csv", style="json")
```

## Common Uses

- discover or resume content workflows
- render maps or HUD-style views
- control sound and music
- print or transform structured content
- recover from mistakes with undo or destructive cleanup when necessary
- inspect docs and repo assets from Vibe with `ucode_read` when working in the Dev extension lane
