# uCode: The User Interface Layer for uOS

`uCode` is the primary **input/output interface layer** for uOS. It is a Markdown-based environment that interprets user input, presents system output, and serves as the bridge between the user and the execution containers in `uScript`. It uses lightweight, expressive syntax to represent commands, objects, and virtual environments within the single-process uOS system.

---

## 🎯 Purpose

* Provide a human-friendly, expressive, and extensible front-end for interaction.
* Enable script invocation, virtual navigation, and data queries via Markdown-enhanced syntax.
* Maintain consistency across all devices by enforcing a pure text-based interface (input/output only).

---

## 🔧 Core Responsibilities

* Format and render Markdown content enhanced with:

  * **ASCII blocks** for visual interface elements.
  * **Shortcodes** to trigger `uScript` containers.
  * **Anchors and Tags** for referencing `uKnowledge` data.
* Translate these expressions into actionable instructions for `uScript`.
* Maintain context during interactions without storing persistent memory directly.

---

## 🧱 Interface Elements

### 1. Shortcodes

Used to call `uScript` containers:

```markdown
{{ python:weather_today }}
{{ bash:daily_summary }}
```

* These map to `/scripts/python/weather_today.py` or `/scripts/shell/daily_summary.sh`.
* Execution returns output in Markdown and is rendered inline.

### 2. ASCII UI Blocks

Used for visualizing dashboards, maps, or data panels:

```ascii
+------------------------+
| [STEPS]     0231/1000 |
| [MISSION]   📦 Archive |
| [LEGACY]   ✨ Pending  |
+------------------------+
```

* Can be embedded in reports, map tiles, or story flows.

### 3. Interactive Anchors

Used to connect to `uKnowledge` references:

```markdown
[📘 Entry: Reboot Protocol](uKnowledge://system/reboot)
```

* Translates into a query to `uKnowledge` and fetches the associated Markdown fragment.

---

## 🔁 Communication Flow

```text
User -> uCode -> uScript -> Execution -> uCode -> Output to User
```

* All processing is single-threaded and event-based.
* uCode receives input, parses shortcodes or interactions, routes logic to `uScript`, then renders results.

---

## 🚀 Planned Enhancements

* [ ] Expression templating (`{{py:...}}` with inline parameters)
* [ ] Thematic color macros for ASCII
* [ ] `@mention` style queries to reference Accounts, Missions, or uKnowledge docs
* [ ] Visual editors for dashboard blocks using only text syntax

---

## 🤖 Relationship to Other Modules

* **uScript**: Executes code; uCode sends it commands.
* **uKnowledge**: Data warehouse; uCode presents queries visually.
* **uWorld/Map**: Renders interactive elements as blocks.
* **uLegacy/uMission**: Tracked and shown via uCode dashboard panels.

---

## 📌 Example

```markdown
> Welcome Wizard. You have {{steps:231}} steps left before this installation reaches potential EOL.
> Current mission: "Preserve all family documents to secure vault"

{{ ascii:dashboard_main }}
{{ python:calculate_remaining_lifespan }}
```

This would output a user-friendly interface containing:

* Steps remaining (from local metrics)
* ASCII dashboard with real-time stats
* Calculated lifespan from uScript container

---

## 📁 File System Example

```
/uOS/
 ├── uCode/
 │    └── ui_blocks/
 │         └── dashboard_main.txt
 ├── uScript/
 │    └── python/
 │         └── calculate_remaining_lifespan.py
 └── uKnowledge/
      └── system/
           └── reboot.md
```

---

## 🌟 Philosophy

* **No memory retention in interface**.
* **Stateless rendering and stateless inputs**.
* **Markdown is the OS**: every command, interaction, or expression is ultimately just a Markdown file.

---

Next: Define interactive `dashboard_main.txt` for use within the ASCII layer.

---



# 🧠 uCode – Markdown-Based Interface

uCode is the interactive front-end of the uOS. It is written entirely in Markdown, designed for clear, readable I/O communication in a single-process environment. It interfaces with `uScript` containers to execute all real logic.

---

## 📌 Core Principles

* **Markdown Driven:** All UI is written using standard Markdown.
* **ASCII Visual Language:** Dashboard tiles, borders, progress bars use ASCII and Unicode for retro-futuristic appeal.
* **Single-Process Flow:** Input/Output only—like ChatGPT.
* **Shortcode Logic:** Interactions defined using embedded shortcodes (e.g., `[run:health_check]`).
* **Separation of Logic:** No computation happens in `uCode`. All execution is passed to `uScript`.

---

## ⚙️ Shortcode Syntax

Shortcodes are parsed and routed to the corresponding container in `uScript`.

```markdown
[run:health_check]
[load:map_dungeon.json]
[input:user_name]
```

Each shortcode can:

* Trigger a script in `uScript`
* Retrieve data from the uKnowledge bank
* Accept user input

---

## 🧩 UI Components

### ASCII Dashboard Block

```text
╔══════════════════════╗
║  uOS SYSTEM STATUS   ║
╠══════════════════════╣
║ Steps:      ███████░░║
║ Missions:   3 Active ║
║ Legacy:     Not Set  ║
╚══════════════════════╝
```

### Tile Grid Example

```text
╭────────────╮╭────────────╮╭────────────╮
│  [map:01]  ││ [map:02]* ││  [map:03]  │
│  MISSION   ││ IN PROGRESS││  LEGACY    │
╰────────────╯╰────────────╯╰────────────╯
```

### Input/Output Example

```markdown
**[input:user_name]** ➜ prompts user for name
**[run:generate_map]** ➜ calls container script in uScript
```

---

## 🔗 Bridge to `uScript`

Every `[run:*]`, `[input:*]`, `[load:*]` command is forwarded to `uScript`, which executes the relevant script or data load in a secure container.

The interaction is:

1. `uCode` receives user input or event.
2. Parses shortcode.
3. Sends request to `uScript`
4. Receives stdout and updates Markdown display.

---

## 🔄 Example Interactive Loop

```markdown
**Welcome, [input:user_name]!**

To begin:
[run:scan_environment]
[load:dungeon_map]
```

* `input:user_name` prompts for terminal input.
* `run:scan_environment` triggers `scan_environment.py` in `uScript`.
* Result is printed inline into the Markdown.

---

## 🔮 Future Extensions

* Auto-refresh Markdown blocks
* Advanced shortcode filters
* Contextual help (`[help:*]`)
* Error tracing via `[trace:run:*]`

---

## ✅ Summary

uCode is the user-friendly Markdown interface of uOS. It lets users interact with uScript containers using simple, readable blocks and shortcodes—all in a retro ASCII UI style.

---

See also: \[uScript.md], \[uKnowledge.md], \[Legacy.md], \[Steps.md], \[Missions.md]
