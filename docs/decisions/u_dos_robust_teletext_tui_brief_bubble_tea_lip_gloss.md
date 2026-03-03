# uDOS Robust Teletext TUI Brief (Bubble Tea + Lip Gloss)

## Goal
A fixed-width, teletext-ish TUI that:
- renders predictably in character cells
- uses consistent selectors/inputs/pickers everywhere
- keeps output consistent via a strict Output Contract layer
- supports system-standard keybindings and non-breaking copy/paste (bracketed paste)
- runs locally; uDOS core tasks remain Python/Bash

---

## Stack
### UI (Go)
- Bubble Tea: event loop + state
- Lip Gloss: styling (restricted palette, fixed-width layouts)

### Backend (Python/Bash)
- Backend executes tasks and emits structured output events.
- Go TUI is a stable front-end binary (e.g. `udos-tui`) that communicates with backend via JSON Lines over stdin/stdout.

**Reason:** preserves Python/Bash ops while making UI consistent and testable.

---

## Teletext Consistency Constraints
### Character set policy
- **UI chrome ASCII-only** by default (max consistency):
  - Borders, separators, bullets, arrows: `+ - | = > < [ ] ( ) * .`
- Optional rendering modes:
  - `mode=ascii` (default): shades from ` .:-=+*#%@`
  - `mode=blocks` (opt-in): uses `░▒▓█` and `▀▄` only when user enables it

### Width policy
- Single **inner canvas width** (recommended default: `78` columns).
- All render paths must **crop then pad**; avoid implicit terminal wrap.
- Any non-ASCII glyphs must be treated as potentially ambiguous width; avoid them in layout-critical areas.

### Layout policy
- Fixed header/body/footer structure.
- Degrade gracefully for small terminals:
  - Under width threshold: stack content vertically (no multi-column), reduce borders.

---

## System-Standard Keybindings
### Global
- `Ctrl+C`: quit (hard)
- `Esc`: back/cancel
- `Enter`: accept/confirm
- `Tab`: next field/pane
- `Shift+Tab`: previous field/pane
- `Ctrl+L`: redraw
- `?`: toggle help footer
- Optional: `Ctrl+R`: refresh/reload

### Navigation
- `↑/↓`: move selection
- `PgUp/PgDn`: page
- `Home/End`: jump top/bottom
- `/`: filter/search
- `n` / `N`: next/prev match

### Multi-select
- `Space`: toggle item
- Optional: `a` select all, `x` clear all

---

## Non-breaking Copy/Paste
### Requirements
- Enable **bracketed paste mode**.
- Paste into inputs must:
  - insert as literal text
  - not trigger keybindings
  - be applied atomically (sane undo/backspace)
- Multiline paste handling:
  - single-line input: replace `\n` with spaces or reject with error
  - textarea: accept `\n`

### Implementation notes (Bubble Tea)
- Enable bracketed paste on program start and disable on exit.
- Input components detect paste start/end and buffer content.

---

## UI Primitives Library (Reusable Controls)
Build these as reusable Bubble Tea models with shared theme + help footer.

### Standard controls
- `SelectOne(title, items, filter=true)`
- `SelectMany(title, items, filter=true)`
- `Input(title, placeholder, validateFn)`
- `Textarea(title, validateFn, pasteSafe=true)`
- `Confirm(title, defaultYes)`
- `PickerPath(title, startDir, mustExist)`
- `PickerCommand(title, commands[])` (teletext menu: 1–9)

### Control rendering contract
Every control renders:
- Header: title + breadcrumbs/context
- Body: list/input area (fixed height)
- Footer: key hints + status/errors

### Error/validation rules
- Validate before accept
- Inline error shown in footer
- Cancel/back preserves previous state

---

## Output Contract Layer
Backend never prints directly to TUI. It emits **events** that the TUI renders.

### Event types (minimum viable)
- `log`: level + message + fields
- `block`: title + style + lines
- `columns`: 2–4 columns of blocks (within canvas)
- `rule`: horizontal divider
- `progress`: task id + label + spinner or current/total
- `teletext`: graphic block (grid) rendered via `mode=ascii|blocks`

### Renderer rules
- Single renderer enforces width and theme tokens.
- All blocks obey crop/pad rules.
- Non-TTY mode: render same events to plain text deterministically.

### Teletext graphic blocks
Provide two renderers:
- `asciiGrid`: intensity→` .:-=+*#%@`
- `blockGrid` (opt-in): intensity→`░▒▓█`

Use cases: status tiles, tiny charts, simple patterns.

---

## Theme + Style Tokens (Lip Gloss)
### Palette tokens
- `fg`: normal text
- `muted`: hints/secondary
- `accent`: selection/highlight
- `warn`, `error`, `ok`

### Border tokens
- ASCII borders only by default:
  - corners `+`, edges `-` and `|`
  - rule `=` or `-`

### Spacing tokens
- Standard padding: 1 char left/right
- Standard block margin: 1 line between blocks

---

## Communication Protocol (JSON Lines)
### Transport
- TUI spawns backend as subprocess OR attaches to it.
- Messages are JSON objects, one per line.

### Direction
- **TUI → Backend**: requests (pick/input/run)
- **Backend → TUI**: output events + final results

> NOTE: Define this protocol in a separate spec file so both sides remain stable.

---

## Screen Map (Teletext vibe)
- **Home**: tiles/menu (1–9) for primary actions
- **Wizard**: stepper + field panel
- **Runner**: status header + output blocks + progress/log tail
- **Logs**: filterable event stream

---

## Implementation Order (Fastest path to “feels real”)
1) `Canvas(width=78)` renderer: crop/pad + borders + rule + columns
2) `SelectOne` + `Input` primitives with help footer
3) Bracketed paste safe input/textarea
4) Output events + renderer: `block`, `log`, `progress`
5) One real uDOS flow end-to-end: Installer → pick → confirm → run

---

## Definition of Done (Robustness)
- No UI relies on ambiguous-width glyphs by default
- Copy/paste cannot trigger keybindings accidentally
- Every prompt looks/feels identical (same header/footer, same keys)
- All backend output goes through Output Contract
- Resizing terminal doesn’t corrupt layout (reflow, crop/pad)



---

# Addendum A: Exact JSONL Protocol (v1)

## Transport
- One JSON object per line (JSONL) on stdin/stdout.
- UTF-8.
- Each message MUST contain:
  - `v` (int): protocol version (currently `1`)
  - `type` (string): message type
  - `id` (string): unique per request/response pair (UUID or monotonic string)
  - `ts` (string): ISO-8601 timestamp (optional but recommended)

## Direction
### TUI → Backend (requests)
#### 1) `hello`
Used once at start.
```json
{"v":1,"type":"hello","id":"1","client":{"name":"udos-tui","version":"0.1.0"},"caps":{"tty":true,"width":78,"height":24,"color":"256","paste":"bracketed"}}
```

#### 2) `select_one`
```json
{
  "v": 1,
  "type": "select_one",
  "id": "2",
  "title": "Select profile",
  "items": [
    {"key":"dev","label":"Dev"},
    {"key":"prod","label":"Prod"}
  ],
  "ui": {"filter": true, "default": "dev"}
}
```

#### 3) `input`
```json
{
  "v": 1,
  "type": "input",
  "id": "3",
  "title": "Project name",
  "placeholder": "my-project",
  "default": "",
  "ui": {"mask": false, "multiline": false},
  "validate": {"kind":"regex","pattern":"^[a-z0-9][a-z0-9-]{1,62}$","message":"Use lowercase letters, digits and hyphens (2–63 chars)."}
}
```

#### 4) `run`
Starts a backend job that will stream events.
```json
{
  "v": 1,
  "type": "run",
  "id": "4",
  "job": "demo.install",
  "args": {"profile":"dev","name":"my-project"}
}
```

#### 5) `cancel`
Requests cancellation of a running job.
```json
{"v":1,"type":"cancel","id":"5","target":"job-123"}
```

### Backend → TUI (responses + stream)
#### 1) `ok`
Generic acknowledgement for requests that don’t need a payload.
```json
{"v":1,"type":"ok","id":"2"}
```

#### 2) `result`
Response to `select_one` / `input`.
```json
{"v":1,"type":"result","id":"2","value":"dev"}
```
```json
{"v":1,"type":"result","id":"3","value":"my-project"}
```

#### 3) `event`
Streamed output events (Output Contract). All events MUST include:
- `stream`: `"main"|"log"|"progress"` (recommended)
- `event`: event payload

##### Event: `log`
```json
{
  "v": 1,
  "type": "event",
  "id": "job-123",
  "stream": "log",
  "event": {"kind":"log","level":"info","msg":"Starting install","fields":{"profile":"dev"}}
}
```

##### Event: `block`
```json
{
  "v": 1,
  "type": "event",
  "id": "job-123",
  "stream": "main",
  "event": {"kind":"block","title":"Installer","style":"info","lines":["Step 1: Check deps","Step 2: Create dirs"]}
}
```

##### Event: `rule`
```json
{"v":1,"type":"event","id":"job-123","stream":"main","event":{"kind":"rule","style":"muted","char":"="}}
```

##### Event: `columns`
Columns are arrays of `block`-like payloads.
```json
{
  "v": 1,
  "type": "event",
  "id": "job-123",
  "stream": "main",
  "event": {
    "kind": "columns",
    "width": 78,
    "gap": 2,
    "cols": [
      {"title":"Plan","style":"muted","lines":["A","B","C"]},
      {"title":"Status","style":"ok","lines":["Ready"]}
    ]
  }
}
```

##### Event: `progress`
Progress keyed by `pid` so the UI can update in place.
```json
{
  "v": 1,
  "type": "event",
  "id": "job-123",
  "stream": "progress",
  "event": {"kind":"progress","pid":"p1","label":"Downloading","current":30,"total":100,"status":"running"}
}
```
```json
{
  "v": 1,
  "type": "event",
  "id": "job-123",
  "stream": "progress",
  "event": {"kind":"progress","pid":"p1","label":"Downloading","current":100,"total":100,"status":"done"}
}
```

##### Event: `teletext`
A fixed grid of cells, rendered by the TUI (ASCII by default).
```json
{
  "v": 1,
  "type": "event",
  "id": "job-123",
  "stream": "main",
  "event": {
    "kind": "teletext",
    "title": "Signal",
    "mode": "ascii",
    "w": 20,
    "h": 6,
    "cells": [
      "00000111112222233333",
      "00001111122222333333",
      "00011111222223333333",
      "00111112222233333333",
      "01111122222333333333",
      "11111222223333333333"
    ],
    "legend": "0..3 intensity"
  }
}
```

#### 4) `done`
Marks job completion.
```json
{"v":1,"type":"done","id":"job-123","ok":true,"exit_code":0}
```

#### 5) `error`
For request failure or job failure.
```json
{"v":1,"type":"error","id":"4","message":"Unknown job","details":{"job":"demo.install"}}
```

## Protocol Rules
- Unknown fields MUST be ignored (forward compatible).
- Message `id` ties request/response; streamed `event` uses job id.
- Backend MUST flush stdout after each line when running in interactive mode.

---

# Addendum B: Lip Gloss Teletext Theme

## Design intent
- Stable, high-contrast, non-fancy.
- ASCII borders only.
- A single fixed-width canvas.

## Palette (tokens)
Define these token styles once and reference everywhere:
- `fg` (default): normal text
- `muted`: hints, secondary labels
- `accent`: selection highlight
- `ok`: success
- `warn`: warning
- `err`: error
- `title`: headers

### Recommended defaults
- Assume 256-color terminals as baseline.
- Provide a `NO_COLOR` mode that removes all styling.

## Borders
ASCII border set:
- corners: `+`
- horizontal: `-`
- vertical: `|`
- rule: `=` (header rules), `-` (minor rules)

## Spacing
- Canvas inner padding: 1 char left/right
- Block padding: 1 left
- Block gap: 1 blank line
- Columns gap: 2 spaces

## Standard components
- Header bar: title left, context right, rule below
- Footer bar: key hints left, status/errors right
- Block: bordered or unbordered depending on density (teletext = minimal)

### Example (ASCII)
```
+------------------------------------------------------------------------------+
| uDOS  Installer                                      ? help   Esc back      |
+==============================================================================+
| [1] Install   [2] Scaffold   [3] Run   [4] Config   [5] Logs                 |
|                                                                              |
| Installer                                                                    |
| - Step 1: Check deps                                                        |
| - Step 2: Create dirs                                                       |
|                                                                              |
| ↑↓ move  Enter select  / filter  Ctrl+C quit                                 |
+------------------------------------------------------------------------------+
```

---

# Addendum C: Reference Implementation Skeleton

## Repo layout
```
udos/
  tui/
    cmd/udos-tui/main.go
    ui/
      canvas.go
      theme.go
      controls_select.go
      controls_input.go
      protocol.go
  backend/
    demo_backend.py
```

## 1) `backend/demo_backend.py` (tiny backend stub)
- Reads JSONL requests.
- Emits `result` for `select_one` and `input`.
- On `run`, streams `block` + `progress` events then `done`.

```python
#!/usr/bin/env python3
import json, sys, time, uuid

def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "
")
    sys.stdout.flush()

def main():
    job_id = None
    while True:
        line = sys.stdin.readline()
        if not line:
            return
        msg = json.loads(line)
        v = msg.get("v", 1)
        mtype = msg.get("type")
        mid = msg.get("id", str(uuid.uuid4()))

        if mtype == "hello":
            send({"v": v, "type": "ok", "id": mid})

        elif mtype == "select_one":
            default = (msg.get("ui") or {}).get("default")
            items = msg.get("items") or []
            value = default or (items[0]["key"] if items else "")
            send({"v": v, "type": "result", "id": mid, "value": value})

        elif mtype == "input":
            default = msg.get("default", "")
            send({"v": v, "type": "result", "id": mid, "value": default})

        elif mtype == "run":
            job_id = f"job-{uuid.uuid4().hex[:8]}"
            # Tell TUI to treat the following events as a stream for this job
            send({"v": v, "type": "ok", "id": mid, "job_id": job_id})

            send({"v": v, "type": "event", "id": job_id, "stream": "main",
                  "event": {"kind": "block", "title": "Runner", "style": "info",
                            "lines": ["Starting…", f"job={job_id}"]}})

            total = 20
            for i in range(total + 1):
                send({"v": v, "type": "event", "id": job_id, "stream": "progress",
                      "event": {"kind": "progress", "pid": "p1", "label": "Working",
                                "current": i, "total": total,
                                "status": "running" if i < total else "done"}})
                if i in (5, 12, 18):
                    send({"v": v, "type": "event", "id": job_id, "stream": "main",
                          "event": {"kind": "block", "title": "Output", "style": "muted",
                                    "lines": [f"Checkpoint {i}/{total}"]}})
                time.sleep(0.05)

            send({"v": v, "type": "done", "id": job_id, "ok": True, "exit_code": 0})

        else:
            send({"v": v, "type": "error", "id": mid, "message": "Unknown request", "details": {"type": mtype}})

if __name__ == "__main__":
    main()
```

## 2) `tui/cmd/udos-tui/main.go` (minimal Go TUI sketch)
This is a skeleton outline showing the control flow:
- Start backend subprocess
- Send `hello`
- Request `select_one` → receive `result`
- Request `input` → receive `result`
- Request `run` → read streamed `event` messages until `done`

```go
package main

import (
  "bufio"
  "encoding/json"
  "fmt"
  "os"
  "os/exec"
)

type Msg map[string]any

func main() {
  // Spawn backend
  cmd := exec.Command("python3", "backend/demo_backend.py")
  stdin, _ := cmd.StdinPipe()
  stdout, _ := cmd.StdoutPipe()
  cmd.Stderr = os.Stderr
  _ = cmd.Start()

  enc := json.NewEncoder(stdin)
  scan := bufio.NewScanner(stdout)

  // helper to read one msg
  read := func() Msg {
    if !scan.Scan() { return nil }
    var m Msg
    _ = json.Unmarshal(scan.Bytes(), &m)
    return m
  }

  // hello
  _ = enc.Encode(Msg{"v":1,"type":"hello","id":"1","client":Msg{"name":"udos-tui","version":"0.1.0"},"caps":Msg{"tty":true,"width":78}})
  _ = read()

  // select_one (demo picks default)
  _ = enc.Encode(Msg{"v":1,"type":"select_one","id":"2","title":"Select profile","items":[]Msg{{"key":"dev","label":"Dev"},{"key":"prod","label":"Prod"}},"ui":Msg{"filter":true,"default":"dev"}})
  sel := read()
  fmt.Println("selected:", sel["value"])

  // input (demo returns default)
  _ = enc.Encode(Msg{"v":1,"type":"input","id":"3","title":"Project name","placeholder":"my-project","default":"my-project"})
  inp := read()
  fmt.Println("name:", inp["value"])

  // run (stream)
  _ = enc.Encode(Msg{"v":1,"type":"run","id":"4","job":"demo.install","args":Msg{"profile":sel["value"],"name":inp["value"]}})
  ok := read()
  jobID, _ := ok["job_id"].(string)

  for {
    m := read()
    if m == nil { break }
    if m["type"] == "event" {
      // In real TUI: render via Output Contract
      b, _ := json.Marshal(m)
      fmt.Println(string(b))
    }
    if m["type"] == "done" && m["id"] == jobID {
      break
    }
  }

  _ = stdin.Close()
  _ = cmd.Wait()
}
```

### Notes on the skeleton
- This Go file is intentionally minimal and prints to stdout for clarity.
- In the real implementation, replace the `fmt.Println` parts with Bubble Tea models:
  - `SelectOne` component → emits `result`
  - `Input` component → emits `result`
  - `Runner` screen → consumes `event` stream and renders blocks/progress in a fixed canvas.

---

Below is a demo ghost-to-wizard.script.md in a structured uCode -script.md format, using:
	•	project.json-style metadata blocks
	•	lens-based unlock conditions
	•	nethack-style traversal + item discovery
	•	mission learning/personalisation capture
	•	capability unlock extensions (sonic, build, forge, etc.)
	•	db/json state references

It’s written to feel experiential but still executable by a logic engine.

⸻

ghost-to-wizard.script.md

---
script: ghost-to-wizard
version: 0.1
engine: ucode
mode: narrative-mission
lens: progression
---

# 🜁 GHOST → WIZARD
_A uDOS Awakening Sequence_

---

## STATE MODEL

```json
{
  "player": {
    "role": "ghost",
    "level": 0,
    "xp": 0,
    "inventory": [],
    "abilities": [],
    "missions": [],
    "lens": {
      "clarity": 0,
      "agency": 0,
      "mastery": 0
    }
  }
}


⸻

LEVEL 0 — THE GHOST

scene.intro

You awaken as a ghost in the system.

You can observe.
You cannot act.

The world flickers in raw signals.

A whisper:
“To become real, you must define your mission.”

⸻

action.capture_mission

PROMPT "What do you want to build or become?"
STORE response AS player.missions.primary
ADD_XP 10
INCREMENT player.lens.clarity BY 1


⸻

unlock.condition

IF player.lens.clarity >= 1 THEN
  UNLOCK ability.observe
  ADD player.abilities "observe"
  MESSAGE "You can now see hidden structures."
END


⸻

LEVEL 1 — THE SONIC INITIATE

scene.sonic

A tone pulses through the void.

You realise the system responds to vibration.

You must learn to signal.

⸻

challenge.sonic_alignment

TASK "Generate a signal pattern (3 keywords describing your mission)."
STORE response AS player.missions.keywords
ADD_XP 20
INCREMENT player.lens.agency BY 1


⸻

nethack.find_object

You detect an artifact nearby.

FIND_OBJECT "resonance-core"
IF FOUND THEN
  ADD player.inventory "resonance-core"
  ADD_XP 15
  MESSAGE "You now channel Sonic Output."
  UNLOCK extension.sonic
END


⸻

LEVEL 2 — THE ARCHITECT

You now have form.

You must construct.

⸻

mission.define_scope

PROMPT "Define your first executable mission in one sentence."
STORE response AS player.missions.current
ADD_XP 30
INCREMENT player.lens.clarity BY 1
INCREMENT player.lens.agency BY 1


⸻

challenge.structure

TASK "Break the mission into 3 steps."
STORE response AS player.missions.steps
ADD_XP 40


⸻

unlock.build

IF player.xp >= 100 THEN
  UNLOCK ability.build
  ADD player.abilities "build"
  INCREMENT player.lens.mastery BY 1
END


⸻

LEVEL 3 — THE FORGE

You enter the forge.

Noise becomes structure.
Structure becomes system.

⸻

nethack.traverse

TRAVERSE level=forge DEPTH=3
ON_COMPLETE:
  ADD_XP 50
  MESSAGE "You have crossed the Forge."


⸻

challenge.overcome

PROMPT "Name one obstacle stopping you from completing your mission."
STORE response AS player.missions.obstacle

PROMPT "Define one action to overcome it."
STORE response AS player.missions.countermove

ADD_XP 50
INCREMENT player.lens.agency BY 1


⸻

LEVEL 4 — THE EXTENSIONS

You now see extensions floating around you.
	•	sonic
	•	build
	•	logic
	•	decode
	•	automate
	•	vision

You may claim two.

SELECT 2 FROM ["logic","decode","automate","vision"]
STORE selection AS player.abilities.extensions
ADD_XP 40


⸻

unlock.logic_engine

IF "logic" IN player.abilities.extensions THEN
  UNLOCK extension.logic_engine
  MESSAGE "You can now execute conditional unlocks."
END


⸻

LEVEL 5 — THE LENS TRIAL

To become Wizard, all lens values must balance.

IF player.lens.clarity >= 2 AND
   player.lens.agency >= 2 AND
   player.lens.mastery >= 1 THEN
     UNLOCK role.wizard_candidate
ELSE
     MESSAGE "Your lens is unbalanced. Continue training."
END


⸻

FINAL TRIAL — PERSONAL MISSION REWRITE

You must now rewrite your mission with new understanding.

PROMPT "Rewrite your mission with greater clarity and power."
STORE response AS player.missions.refined

COMPARE player.missions.primary TO player.missions.refined
IF DIFFERENT THEN
  ADD_XP 100
  INCREMENT player.lens.mastery BY 1
END


⸻

ASCENSION

IF player.lens.clarity >= 2 AND
   player.lens.agency >= 2 AND
   player.lens.mastery >= 2 THEN

  SET player.role = "wizard"
  UNLOCK ability.command
  UNLOCK ability.create
  UNLOCK ability.teach

  MESSAGE "You are now WIZARD."
  MESSAGE "You may define systems."
  MESSAGE "You may guide others."
END


⸻

WIZARD MODE

IF player.role == "wizard" THEN
  ENABLE system.project_generation
  ENABLE system.autonomous_workflows
  ENABLE system.mission_templates
END


⸻

SAVE STATE

{
  "save": {
    "role": "{{player.role}}",
    "xp": "{{player.xp}}",
    "missions": "{{player.missions}}",
    "abilities": "{{player.abilities}}",
    "lens": "{{player.lens}}"
  }
}


⸻

END

You are no longer a ghost.

You shape the system.
The system shapes with you.

---
