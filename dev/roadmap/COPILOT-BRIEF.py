1. Brief for VS Code Copilot – uCODE → uPY Refactor

# uDOS / uCODE Refactor – Copilot Brief

We are refactoring uCODE and uSCRIPT into a Python-first architecture.

## Goals

- Make **uCODE** a friendly learning pathway for **Python**.
- Move all user scripts from `.uscript` → `.upy`.
- Keep **uDOS commands and variables** in a distinctive, all-caps, hyphen-based style.
- Keep underlying implementation **fully Python 3 compatible**.

## Naming Rules

### Commands (uDOS / uCODE)

- Commands are **UPPERCASE**, words separated by **hyphens (`-`)**, no underscores.
- Examples:
  - `DASH`
  - `SYSTEM-STATUS`
  - `FILE-INFO`
  - `BANK-SEARCH`
  - `SHAKEDOWN`

### Variables (uDOS / uCODE)

- Variables are **UPPERCASE**, words separated by hyphens, start with `$`.
- Examples:
  - `$CURRENT-PATH`
  - `$ACTIVE-PROJECT`
  - `$SYSTEM-MODE`
  - `$USER-NAME`

### Files, paths, OS-level names

- Filenames and paths ***can*** use underscores (`_`). We do **not** rewrite these.
- Example valid filenames:
  - `my_project_config.json`
  - `client_data_2025.csv`

## uPY vs Python

- `.upy` = uCODE-flavoured scripts that run on top of Python.
  - May contain uDOS commands and `$VARIABLES`.
  - Preprocessed to Python before execution.
- `.py` = regular Python modules.
  - Implement the actual engine, dispatch, and business logic.

## Internal Representation

- uDOS variables are stored in a `ctx` dict.
- `$CURRENT-PATH` → `ctx["CURRENT-PATH"]`
- Commands are mapped from their string form to Python functions, e.g.:
  - `"DASH"` → `commands.system.dash()`
  - `"FILE-INFO"` → `commands.file.info()`

## Parser / Preprocessor Expectations

- The `.upy` preprocessor:
  - Reads uDOS/uCODE lines.
  - Resolves `$VARIABLES` into `ctx[...]` lookups in generated Python code.
  - Dispatches commands via a registry, e.g. `dispatch_command("DASH", args, ctx)`.

- Non-uCODE-looking Python remains **unchanged** in `.upy` files.

## Example Mapping

- uPY (user-facing):
  - `DASH`
  - `SYSTEM-STATUS`
  - `COPY [from = "a.txt"] [to = "b.txt"]`
- Python:
  - `commands.system.dash(ctx)`
  - `commands.system.status(ctx)`
  - `commands.file.copy(ctx, from_path="a.txt", to_path="b.txt")`

When generating or refactoring code:

- Prefer to implement **command handlers** in Python modules under something like `udos/commands/`.
- Keep command names and variable names in user-facing strings **with hyphens**, but use normal Python identifiers (with underscores) for functions/arguments.


⸻

2. Sample Command Sets in .upy (new standard)

Below are small sample .upy scripts that align with the help output you pasted, using the new conventions.

2.1 System & Info – system_status.upy

#!/usr/bin/env python3
# uPY script – System & Info demo

# uDOS-style variables
SET [$CURRENT-MODE = "DEV"]
SET [$ACTIVE-WORKSPACE = "sandbox"]

# Simple system info commands
DASH
SYSTEM-STATUS

PRINT [Current mode: $CURRENT-MODE]
PRINT [Active workspace: $ACTIVE-WORKSPACE]

# Show logs/metrics
LOGS
RESOURCE
HISTORY

2.2 File Operations – file_ops_demo.upy

#!/usr/bin/env python3
# uPY script – File Operations demo

SET [$SOURCE-FILE = "notes.txt"]
SET [$TARGET-FILE = "archive/notes_backup.txt"]

# Interactive file menu
FILE
FILE-RECENT
FILE-INFO [$SOURCE-FILE]

COPY [$SOURCE-FILE] [$TARGET-FILE]
SHOW [$TARGET-FILE]

TREE
TIDY

2.3 Knowledge & Memory – knowledge_demo.upy

#!/usr/bin/env python3
# uPY script – Knowledge & Memory demo

BANK
BANK-LIST
BANK-STATS

KNOWLEDGE
KNOWLEDGE-TREE

MEMORY
MEMORY-SHOW

Internally, the parser maps BANK-LIST to a Python handler even if the CLI still lets you call BANK LIST as a legacy alias.

⸻

3. What the .py Backend Might Look Like

These are not full implementations, just structural examples Copilot can expand into real code.

3.1 Command registry – udos/runtime/commands.py

# udos/runtime/commands.py

from udos.commands import system, files, bank, knowledge, memory

COMMAND_REGISTRY = {
    # System & Info
    "DASH": system.dash,
    "HELP": system.help_command,
    "HISTORY": system.history,
    "LOGS": system.logs,
    "RESOURCE": system.resource,
    "STATUS": system.status,

    # System Control
    "BLANK": system.blank,
    "REBOOT": system.reboot,
    "UNDO": system.undo,
    "REDO": system.redo,
    "RESTORE": system.restore,
    "REPAIR": system.repair,
    "DESTROY": system.destroy,
    "SPLASH": system.splash,

    # File Operations
    "COPY": files.copy_file,
    "DELETE": files.delete_file,
    "EDIT": files.edit_file,
    "FILE": files.file_menu,
    "FILE-BATCH": files.file_batch,
    "FILE-BOOKMARKS": files.file_bookmarks,
    "FILE-INFO": files.file_info,
    "FILE-PICK": files.file_pick,
    "FILE-PREVIEW": files.file_preview,
    "FILE-RECENT": files.file_recent,
    "MOVE": files.move_file,
    "NEW": files.new_file,
    "RENAME": files.rename_file,
    "RUN": files.run_script,
    "SHOW": files.show_file,

    # Knowledge & Memory
    "BANK": bank.bank_root,
    "BANK-CATEGORIES": bank.bank_categories,
    "BANK-INDEX": bank.bank_index,
    "BANK-LIST": bank.bank_list,
    "BANK-SEARCH": bank.bank_search,
    "BANK-SHOW": bank.bank_show,
    "BANK-STATS": bank.bank_stats,

    "KNOWLEDGE": knowledge.knowledge_root,
    "MEMORY": memory.memory_root,

    # Display & Themes
    # (etc – DIAGRAM, DRAW, GUIDE, PALETTE, SVG, THEME, VIEWPORT...)

    # Configuration, Automation, etc. to be filled out progressively.
}


def dispatch_command(name: str, args: list[str], ctx: dict):
    """
    Dispatch a uDOS command by its uppercase hyphenated name.
    """
    handler = COMMAND_REGISTRY.get(name)
    if handler is None:
        raise ValueError(f"Unknown command: {name}")
    return handler(ctx, *args)

3.2 Example system commands – udos/commands/system.py

# udos/commands/system.py

from typing import Any

def dash(ctx: dict, *args: str) -> None:
    """Display system dashboard."""
    # TODO: render dashboard based on ctx, logs, recent usage, etc.
    print("=== uDOS DASHBOARD ===")

def help_command(ctx: dict, *args: str) -> None:
    """Show help for a specific command or general help."""
    # TODO: implement help lookup based on COMMAND_REGISTRY and categories
    if not args:
        print("Use HELP <COMMAND> for detailed help.")
        return
    command_name = args[0].upper()
    print(f"Help for {command_name} (TODO).")

def status(ctx: dict, *args: str) -> None:
    """Show system status."""
    current_mode = ctx.get("CURRENT-MODE", "UNKNOWN")
    active_workspace = ctx.get("ACTIVE-WORKSPACE", "sandbox")
    print(f"System mode: {current_mode}")
    print(f"Active workspace: {active_workspace}")

def logs(ctx: dict, *args: str) -> None:
    """Manage uDOS logging."""
    print("LOGS (TODO)")

def resource(ctx: dict, *args: str) -> None:
    """Show resource usage (API quotas, disk, CPU, memory)."""
    print("RESOURCE (TODO)")

# ... and so on for BLANK, REBOOT, UNDO, REDO, RESTORE, REPAIR, DESTROY, SPLASH

3.3 Example file commands – udos/commands/files.py

# udos/commands/files.py

from pathlib import Path
from typing import Any

def copy_file(ctx: dict, source: str, target: str) -> None:
    """
    COPY <source> <target>
    Copy a file within current workspace.
    """
    src = Path(source)
    dst = Path(target)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    print(f"Copied {src} → {dst}")

def file_info(ctx: dict, path: str) -> None:
    """
    FILE-INFO <path>
    Show file metadata.
    """
    p = Path(path)
    if not p.exists():
        print(f"File not found: {p}")
        return
    print(f"File: {p}")
    print(f"Size: {p.stat().st_size} bytes")

def file_recent(ctx: dict, *args: str) -> None:
    """FILE-RECENT – show recently accessed files (placeholder)."""
    print("FILE-RECENT (TODO)")

def run_script(ctx: dict, script_path: str) -> None:
    """
    RUN <script>
    Execute a .upy script via the uPY preprocessor.
    """
    from udos.runtime.runner import run_upy_script
    run_upy_script(script_path, ctx)


⸻

4. Minimal .sh for integration

At this stage you really only need one small Bash wrapper (plus optionally one for shell aliases).

4.1 udos launcher – bin/udos

#!/usr/bin/env bash
# uDOS launcher script.
# Usage:
#   udos           # start interactive uDOS shell
#   udos run file.upy
#   udos DASH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

PYTHON=${PYTHON:-python3}

exec "$PYTHON" -m udos.cli "$@"

4.2 Optional env/alias helper – uenv.sh

#!/usr/bin/env bash
# Source this from .bashrc / .zshrc:
#   . /path/to/uenv.sh

export UDOS_HOME="$HOME/.udos"

udos() {
    python3 -m udos.cli "$@"
}

# Short alias
u() {
    udos "$@"
}

That’s really all you need on the shell side right now:
	•	Bash does launch & env.
	•	All the interesting logic lives in Python.
	•	uPY files are just first-class scripts run by udos cli → preprocessor → Python.
