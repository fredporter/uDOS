# uScript.md

uScript is the execution backbone of uOS, designed to safely and flexibly run logic, automation, and tooling through containerized shell and Python scripts. It is the runtime counterpart to uBASIC, which handles the user-facing scripting syntax. uScript executes securely in isolated environments, guided by markdown-driven configurations and shortcodes.

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

- Scripts are sandboxed in Docker or Podman containers.
- Read-only file systems by default.
- Only whitelisted paths and variables are exposed.
- Execution logs are recorded in uOS Markdown format.

---

## 🔗 Integration with uBASIC

uBASIC calls uScript using shortcodes embedded in Markdown:

```markdown
[RUN:greet_lifeform name="World"]
```

When rendered or parsed by the uOS engine, this triggers the corresponding container logic.

Use ASCII output for visual returns (see `ascii-engine`).

---

## 📘 Directory Structure

```text
/usr/lib/utos/
├── scripts/
│   ├── greet_lifeform.usr.yaml
│   ├── greet.py
│   └── math_tool.usr.yaml
└── engines/
    ├── python:3.10-slim
    └── bash:5
```

---

## 📥 Future Extensions

- `return:` key to support structured outputs (JSON, Markdown, etc.)
- Smart caching and pre-compilation of common scripts
- Interactive script debugger via uBASIC console

---

## 🧩 Sample Shortcode Index

| Shortcode | Action |
|-----------|--------|
| `[RUN:script]` | Execute uScript with optional params |
| `[INPUT:x]` | Inject user input (linked to script param) |
| `[OUTPUT:x]` | Display script return values visually |

Use these patterns to build rich, logic-driven workflows with lightweight containers.

---

✨ uScript transforms uBASIC input into live, isolated logic executions while respecting the simplicity of Markdown and the charm of ASCII.
