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
  * **Anchors and Tags** for referencing data.
* Translate these expressions into actionable instructions for `uScript`.
* Maintain context during interactions without storing persistent memory directly.

---

## 🧱 Interface Elements

### 1. Shortcodes

Used to call `uScript` containers.

* Execution returns output in Markdown and is rendered inline.

### 2. ASCII UI Blocks

Used for visualizing dashboards, maps, or data panels:

```ascii
+------------------------+
| [MOVE]     0231/1000 |
| [MISSION]   📦 Archive |
| [LEGACY]   ✨ Pending  |
+------------------------+
```

* Can be embedded in reports, map tiles, or uMemory

### 3. Interactive Anchors

Used to connect to references.
Translates into a query and fetches the associated Markdown fragment.

---

## 🔁 Communication Flow


* All processing is single-threaded and event-based.
* uCode receives input, parses shortcodes or interactions, routes logic to `uScript`, then renders results.

---

## 🚀 Planned Enhancements

* [ ] Thematic color macros for ASCII
* [ ] `@mention` style queries to reference Milestones, Missions, or uKnowledge docs
* [ ] Visual editors for dashboard blocks using only text syntax

---

## 🤖 Relationship to Other Modules

* **uScript**: Executes code; uCode sends it commands.
* **uMemory**: User data warehouse; uCode presents queries visually.
* **uMaps**: Renders interactive elements as blocks.
* **uMission**: Tracked and shown via uCode dashboard panels.

---

## 🌟 Philosophy

* **No memory retention in interface**.
* **Stateless rendering and stateless inputs**.
* **Markdown is the OS**: every command, interaction, or expression is ultimately just a Markdown file.


# 🧠 uCode – Markdown-Based Interface

uCode is the interactive front-end of the uOS. It is written entirely in Markdown, designed for clear, readable I/O communication in a single-process environment. It interfaces with `uScript` containers to execute all real logic.

---

## 📌 Core Principles

* **Markdown Driven:** All UI is written using standard Markdown.
* **ASCII Visual Language:** Dashboard tiles, borders, progress bars use ASCII and Unicode for retro-futuristic appeal.
* **Single-Process Flow:** Input/Output only—like ChatGPT.
* **Shortcode Logic:** Interactions defined using embedded shortcodes
* **Separation of Logic:** No computation happens in `uCode`. All execution is passed to `uScript`.

---

## ⚙️ Shortcode Syntax

Shortcodes are parsed and routed to the corresponding container in `uScript`.

Each shortcode can:

* Trigger a script in `uScript`
* Retrieve data from the uKnowledge or UMemory banks
* Accept user input

---

## 🧩 UI Components

### ASCII Dashboard Block

```text
╔══════════════════════╗
║  uOS SYSTEM STATUS   ║
╠══════════════════════╣
║ Moves:      ███████░░║
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
