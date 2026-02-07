# uCODE Prompt Spec (v1)

**Date:** 2026-02-04  
**Status:** Implementation-aligned  
**Scope:** uCODE TUI input parsing, command prefixes, shell routing, autocomplete, and auto‑route behavior.

---

## 1. Purpose

uCODE must clearly separate **questions** from **commands** while keeping command entry fast. This spec defines a prompt contract that is Obsidian‑first, vault‑first, and deterministic.

---

## 2. Input Modes and Prefixes

There are three modes, determined by the first non‑whitespace characters.

1. **AI Prompt mode**  
Prefix: `OK ` or `?`  
Example: `OK EXPLAIN core/tui/ucode.py`  
Example: `? summarize this file`

2. **Slash mode**  
Prefix: `/`  
Example: `/help`

3. **Auto route mode**  
Default if no prefix matches.  
Example: `status`

---

## 3. Parsing Rules

1. **Trim left whitespace**, then inspect prefix.
2. **AI Prompt mode** if input starts with `OK` followed by whitespace, or starts with `?`.
- Normalize `OK` or `?` to a single internal prefix `OK`.
3. **Slash mode** if input starts with `/`.
- If the first token matches a **uCODE command** in the registry, route to uCODE.
- Otherwise route to **shell**, if shell routing is enabled.
4. **Auto route mode** if none of the above matches.
- Route order: **uCODE → shell → AI** (local‑first with optional cloud sanity).
5. **Command naming restriction:** uCODE commands must **not** start with digits (`0-9`) or `-`/`=`.  
   - This reserves numeric‑first input for menu selection (see section 7).

---

## 4. Slash Commands

Slash commands are resolved against the **uCODE command registry**.

**Rule:**  
If input starts with `/` and the first token equals a known uCODE command, route to uCODE. Otherwise route to shell (if enabled).

---

## 5. Autocomplete (Dynamic Suggestions)

Autocomplete is **dynamic** and context‑aware. It pulls from:

1. **Command registry** (all uCODE commands)
2. **Subcommands/options** for the active command
3. **Workspace paths** (`@sandbox`, `@bank`, `@public`, `@private`, etc.)
4. **Vault file paths** (recent + indexed)
5. **Tags** (frontmatter `tags` + inline `#tags`)
6. **Containers** (from `/library/*` manifests)
7. **Recent history** (last N commands)

**Priority rules:**
1. Context‑matched candidates first (subcommands, options).
2. Recently used matches second.
3. Global registry last.

---

## 6. Keybindings and UX

1. `Tab`  
   - Cycle forward through suggestions.
2. `Shift+Tab`  
   - Cycle backward.
3. `↑/↓`  
   - Navigate history when no suggestion list is active.
4. `→`  
   - Accept current suggestion (explicit accept only).
5. `Esc`  
   - Clear suggestions.

**Autocomplete rules (non‑intrusive):**
1. Suggestions are **visual only** until explicitly accepted.
2. `Enter` **never** accepts a suggestion; it submits the current input as‑typed.
3. Suggestions **must not** take over the input buffer.
4. Provide clear visual signaling when suggestions are available and when one is selected.

**Suggestion display:**
1. Show top 6 candidates inline or as a drop‑down.
2. Highlight the currently selected candidate.
3. Show brief command help when a command is selected.

---

## 7. Menu Input Router (Non‑Blocking)

When an interactive menu is visible, the first keypress determines routing.

**Menu capture keys (first keypress):**
- `0-9`, `-`, `=` → select the corresponding menu option (if available)
- `↑/↓` → move highlight
- `Enter` → select highlighted option

**Typing keys:**
- Any letter or other printable character **dismisses menu focus** and begins normal prompt input.

**Design intent:**
- Menus are **helpful**, not sticky.
- Users can select from menus quickly or just keep typing.

---

## 8. Safety Rules (Shell Mode)

Shell mode is powerful and must be explicit.

1. `/` commands are logged via the logging API (`memory/logs/udos`).
2. Detect destructive patterns (`rm`, `mv`, `>`, `|`, `sudo`) and require confirmation.
3. Reject shell commands that target outside the repo root unless explicitly allowed.

---

## 9. Examples

```text
OK MAKE svg sandbox:tree.svg
```
Creates an SVG file at `vault/sandbox/tree.svg`.

```text
?SETUP
```
Runs the TUI setup story (AI prompt routed to uCODE).

```text
 /ls -la
```
Shell command (no uCODE registry match).

```text
How do I publish to the public lane?
```
Auto route mode (uCODE → shell → AI).

---

## 10. Implementation Notes

1. **Prefix detection** must run before any runtime command routing.
2. **TS runtime** remains script‑only and does not own the prompt.
3. **Obsidian‑first** tagging: inline `#tags` and frontmatter `tags` are indexed for autocomplete.

---

## 11. Acceptance Criteria

1. `OK` and `?` reliably route to the same AI prompt handler.
2. `/help` routes to uCODE if registered; `/ls` routes to shell when shell is enabled.
3. Auto route mode attempts uCODE → shell → AI in that order.
4. Autocomplete suggestions update based on command context.
5. Autocomplete never takes over input; suggestions require explicit accept.
6. Shell commands are logged and destructive operations prompt for confirmation.
7. When a menu is visible, numeric‑first input routes to menu selection.
