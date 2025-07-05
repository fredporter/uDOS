---
title: "uDOS Execution Model — uCode & uScript"
version: "Beta v1.6.1"
id: "003"
tags: ["execution", "uCode", "uScript", "shell", "task", "automation"]
created: 2025-07-05
updated: 2025-07-05
---

# 🧮 uDOS Execution Model

This document defines the operational logic of the uDOS runtime system, including user input/output via `uCode` and programmable automation via `uScript`.

---

## 📘 Contents

1. [uCode — The uDOS Shell](#ucode--the-udos-shell)
2. [uScript — Lightweight Automation Engine](#uscript--lightweight-automation-engine)
3. [uScript Format Specification](#uscript-format-specification)
4. [uScript Examples](#uscript-examples)

---

## 🌀 uCode — The uDOS Shell
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

Each interaction is part of a linear single-process loop. The flow is:
→ receive input → parse → run script → log output → return Markdown.
Logging always occurs at the **end** of the cycle, once the full output is rendered.

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

uCode is the user-friendly Markdown interface of uDOS. It lets users interact with uScript containers using simple, readable blocks and shortcodes—all in a retro ASCII UI style.
This execution is always stateless and Markdown-first, respecting the purity of input/output in uDOS.

---

## 📜 uScript — Lightweight Automation Engine
# uScript

**Role:** Execution Engine for uDOS Scripts

**Purpose:** uScript is the execution backend for all shell, Python, and future user-defined scripting languages within the uDOS ecosystem. It operates as a single-process containerized runtime, designed to interpret and securely execute user logic on demand via interface calls from `uCode`.

---

## Core Responsibilities

* Execute containerized scripts triggered by `uCode` shortcodes.
* Manage runtime environment variables, user sessions, and script metadata.
* Log inputs, outputs, and step usage per execution.
* Enforce sandboxed, permission-based script execution.
* Allow self-modifying behavior for long-lived scripts (e.g., missions).

---

## Script Types Supported

| Type  | Description                         |
| ----- | ----------------------------------- |
| `sh`  | Standard Linux shell scripts        |
| `py`  | Python 3.x scripts                  |
| `mdx` | Markdown logic blocks (interpreted) |
| `uos` | uOS-defined future script syntax    |

---

## Execution Flow

1. `uCode` sends a `shortcode` or `{code}` block to uScript.
2. uScript parses metadata (e.g., script type, permissions, context).
3. A container is spun up with isolated environment.
4. Script executes, output is streamed back to `uCode`.
5. Step count is incremented and logged against mission or legacy.
6. If marked as persistent, a link is created to `uMemory`.


## Permissions and Safety

Each script is tagged with a permission profile:

* `sandboxed` (default): No external calls
* `network`: Allows outbound-only connections
* `filesystem`: Grants read access to specific dirs

All executions are logged as atomic entries and timestamped. No session IDs or usernames are recorded.

Permission must be granted by Wizard (Parent Account).

---

## Mission Integration

Scripts may register as supporting tools or logic processors for:

* In-progress Missions
* uKnowledge logging
* Map triggers (e.g., tile executes logic when visited)

---

## Legacy and Final Execution

Scripts marked as `final` may auto-execute as part of Legacy ritual:

```markdown
:::uos final=true legacy="wanderer"
print("The Wanderer leaves behind their final log...")
:::
```

---

## Roadmap

* Add support for compiled languages (Rust, Zig) with limited IO
* Introduce stateful containers per mission
* Deep linking between `uScript` containers and `uMemory` entries
* Runtime visualisation of script impact per step

---

## 🔣 uScript Format Specification
# uScript.md

uScript is the execution backbone of uDOS, designed to safely and flexibly run logic, automation, and tooling through containerized shell and Python scripts. It is the runtime counterpart to uBASIC, which handles the user-facing scripting syntax. uScript executes securely in isolated environments, guided by markdown-driven configurations and shortcodes.

## 🧱 Structure

uScript scripts are designed to be modular, declarative, and human-readable. They follow a structure composed of:

- **Shortcodes**: Markdown-compatible command calls (e.g., `[RUN:example_script]`)
- **YAML Configuration**: Script metadata and requirements.
- **Python / Shell Backends**: Isolated logic scripts executed in containers.

---

## 📂 Script Format

```yaml
# example.usr.yaml
name: greet_lifeform
engine: python
inputs:
  - name: name
    type: string
    default: Friend
container:
  image: "python:3.10-slim"
  entry: "greet.py"
```

```python
# greet.py
import os
name = os.environ.get("NAME", "Lifeform")
print(f"Hello {name}! Welcome to uOS.")
```

This example will be called by uBASIC using:

```markdown
[RUN:greet_lifeform name="Allegra"]
```

Which triggers the container to run with input parameters set via environment variables.

---

## 🔄 Chaining Logic

Scripts can return exit codes and outputs which are piped forward:

```yaml
name: chain_start
engine: python
entry: "start.py"
outputs:
  - result
```

```python
# start.py
print("Boot sequence initiated.")
```

```yaml
name: follow_up
engine: shell
entry: "echo 'Follow-up task complete.'"
requires:
  - chain_start
```

uScript will chain the execution, storing context per session.

---

## 🧪 Example: Math Assistant

```yaml
name: math_tool
engine: python
inputs:
  - x: int
  - y: int
  - op: string
entry: math.py
```

```python
# math.py
import os
x = int(os.getenv("X", 0))
y = int(os.getenv("Y", 0))
op = os.getenv("OP", "+")

if op == "+":
    print(x + y)
elif op == "-":
    print(x - y)
else:
    print("Unsupported operation")
```

Trigger:
```markdown
[RUN:math_tool x=4 y=3 op="+"]
```

---

## 🤖 Special Containers

Pre-built service containers can be used:

- `code-runner`: Evaluates short Python code snippets.
- `data-translator`: Converts between Markdown, CSV, and JSON.
- `ascii-engine`: Powers ASCII-based visual elements.

---

## 🛡️ Security

- Scripts are sandboxed in containers.
- Read-only file systems by default.
- Only whitelisted paths and variables are exposed.
- Execution logs are recorded in uMemory Markdown format.

---

## 🔗 Integration with uCode

uCode calls uScript using shortcodes embedded in Markdown:

```markdown
[RUN:greet_lifeform name="World"]
```

When rendered or parsed by the uOS engine, this triggers the corresponding container logic.

Use ASCII output for visual returns (see `ascii-engine`).


## 🧩 Sample Shortcode Index

| Shortcode | Action |
|-----------|--------|
| `[RUN:script]` | Execute uScript with optional params |
| `[INPUT:x]` | Inject user input (linked to script param) |
| `[OUTPUT:x]` | Display script return values visually |

Use these patterns to build rich, logic-driven workflows with lightweight containers.

---

✨ uScript transforms uCode input into live, isolated logic executions while respecting the simplicity of Markdown and the charm of ASCII.

---

## 🧪 uScript Examples
# uScript: uDOS Native Scripting Language

## \[Overview]

`uScript` is the native scripting language of uDOS, built to extend and evolve user interaction beyond uCode. Inspired by Markdown, Visual BASIC, and modern scripting paradigms, it is designed for clarity, power, and seamless container integration.

* **No line numbers**, modern syntax
* **Fully Markdown-compatible**
* **Support for ASCII I/O and graphical overlays**
* **Embedded container calls** to Python, Bash, etc.
* **Anchor-linkable code**, reusable macros

## \[Philosophy]

* Empower the user to create, learn, and modify with minimal friction.
* Promote clear, modular logic for educational and creative coding.
* Bridge play and logic: netHack-style events, BASIC-style logic, Python-style execution.

---

## \[Syntax Basics]

### (Code) Blocks

All code is wrapped in `(code)` blocks:

```
(code)
print "Hello, World!"
(code)
```

### Comments

Use `#` for single-line comments:

```
(code)
# This is a comment
print "Run"
(code)
```

### Variables

Auto-typed at runtime. Declare simply:

```
(code)
name = "Wizard"
level = 3
(code)
```

### Conditionals

```
(code)
if level > 2:
    print "Access granted"
else:
    print "Access denied"
(code)
```

### Loops

```
(code)
for i in range(1, 6):
    print "Potion #" + str(i)
(code)
```

---

## \[Interactive Logic Examples]

### \[Dice Roll Game]

```
(code)
import random
roll = random.randint(1,6)
print "You rolled a ", roll
if roll == 6:
    print "Critical hit!"
(code)
```

### \[Inventory Loop]

```
(code)
inventory = ["Sword", "Shield", "Potion"]
for item in inventory:
    print "You carry: ", item
(code)
```

---

## \[Containers]

uScript integrates with containers using the `call` keyword. Arguments can be passed directly as Markdown-safe arrays or dicts.

### Call a Python Container:

```
(code)
call python:
  script: "/scripts/generate_poem.py"
  args:
    theme: "stars"
    lines: 4
(code)
```

### Return Handling

Returned content can be used in uScript as plain text or ASCII renderings:

```
(code)
result = call python:
  script: "/scripts/get_weather.py"
  args:
    city: "Sydney"
print result
(code)
```

---

## \[Macro Commands]

Macros let you define reusable blocks with parameters.

```
(code)
macro greet(name):
    print "Hello, " + name + "!"
end

call greet("Master")
(code)
```

---

## \[ASCII and UI Layer Support]

Use `draw` or `ascii` to send content to visual layers.

```
(code)
ascii:
  text: "YOU DIED"
  style: red-blink
  pos: [40,12]
(code)
```

```
(code)
draw map:
  source: "/maps/temple.txt"
  layer: 2
(code)
```

---

## \[uScript Goals]

* Expand from uCode with structured logic and interactive storytelling
* Enable integration with containerized AI, agents, or automation
* Act as the core scripting interface for uDOS modules and maps

## \[Next]

* Define `uScript Standard Library`
* Enable runtime debugging view
* Embed macros into Markdown for cross-scripting

> "A good spell is a script you understand."

---
