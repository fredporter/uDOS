# uScript

**Role:** Execution Engine for uOS Scripts

**Purpose:** uScript is the execution backend for all shell, Python, and future user-defined scripting languages within the uOS ecosystem. It operates as a single-process containerized runtime, designed to interpret and securely execute user logic on demand via interface calls from `uCode`.

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
6. If marked as persistent, a link is created to `uKnowledge`.

---

## Example: Shell Script Execution

```markdown
:::sh
#!/bin/bash
uname -a
echo "Hello from uScript container!"
:::
```

## Example: Python Logic

```markdown
:::py
from datetime import datetime
print("Current Time:", datetime.now())
:::
```

---

## Script Container Architecture

* Uses Linux namespaces and cgroups for isolation
* Mounted uOS-specific volume for logs and ephemeral memory
* `uos_env.json` config provided per user/session
* Custom syscall guards to prevent unauthorized network/file access

---

## Integration with uCode

* uCode interprets the UI/Markdown layer and translates interactive blocks into calls to uScript.
* Output is returned via rendered block or chat response.
* Shortcodes:

  * `[run:py name="timer"]` links to an existing `.py` file
  * `{uos:mission_tracker}` runs an internal uOS script

---

## Permissions and Safety

Each script is tagged with a permission profile:

* `sandboxed` (default): No external calls
* `network`: Allows outbound-only connections
* `filesystem`: Grants read access to specific dirs

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
* Deep linking between `uScript` containers and `uKnowledge` entries
* Runtime visualisation of script impact per step
