# 🧰 `map_editor.md` – uOS ASCII Map Creator

A terminal-first tool for building ASCII-based interactive maps. Users can visually design dungeons, worlds, and zones while linking elements to uOS objects like memory, missions, and legacy.

---

## 🎯 Purpose

Create rich, explorable spaces that:

* Use ASCII characters
* Link tiles to real-time data (memory, mission, legacy)
* Launch uScript containers
* Enable Markdown-based storytelling

---

## 🧱 Tile Legend (Extended)

| Symbol | Meaning                    | Data Binding      |
| ------ | -------------------------- | ----------------- |
| ☼      | Location Marker            | Any data point    |
| ≡      | Pathway or Floor           | None              |
| ┼      | Door / Trigger Gate        | uScript           |
| ∩      | Knowledge Node             | Memory (present)  |
| ▓      | Crypt / Archive            | Legacy (past)     |
| ⛧      | Mission Beacon / Objective | Mission (future)  |
| ░      | Fog of War                 | Hidden until seen |

---

## ✍️ Editor Syntax (uBASIC Shortcodes)

````markdown
```ascii-map name="wizard_tower"
 ☼ ≡ ≡ ≡ ∩
 ≡ ▓ ≡ ⛧ ≡
````

@bind("☼", type="location", id="home")
@bind("∩", type="memory", id="remember.42")
@bind("⛧", type="mission", id="quest.04")
@bind("▓", type="legacy", id="ancestor.father")
@link("┼", script="entry\_trigger.uscript")

````

---

## 🔗 Shortcodes Reference

| Shortcode         | Purpose                             |
|------------------|-------------------------------------|
| `@bind(tile)`    | Attach a memory/mission/legacy      |
| `@link(tile)`    | Link to a `.uscript` container      |
| `@move(dir)`     | Simulate directional movement       |
| `@interact()`    | Trigger interaction event           |
| `@teleport(loc)` | Jump to location by ID              |

---

## 🧪 Live Preview Logic
Maps rendered in the terminal or UI auto-preview bound objects:
- Hover `∩` shows the memory snippet
- Interact with `⛧` triggers mission preview
- Walk on `▓` reads legacy artifact

---

## 🧠 Advanced Binding Logic

```markdown
@bind("⛧", type="mission", id="mission.003", trigger="onStep")
@bind("∩", type="memory", id="note.last_entry", access="onInteract")
````

These allow delayed or context-aware activation of logic containers.

---

## 📁 File Output

Each custom map becomes:

* `.md` for layout and lore
* `.ascii` for raw rendering
* `.meta.json` to define triggers and bindings

---

## 🛠️ Coming Tools

* ASCII Map GUI overlay
* Multi-layer support (`Z-depth`)
* Map Templates Gallery
* Memory auto-tethering

---

> Next: Should we start with a sample zone pack (like "Wizard's Tower") and bundle a few memory tiles and legacy crypts?
