# uCODE Prompt Spec (v1)

**Date:** 2026-02-04  
**Status:** Draft (implementation-ready)  
**Scope:** uCODE TUI input parsing, command prefixes, shell routing, and autocomplete.

---

## 1. Purpose

uCODE must clearly separate **questions** from **commands** while keeping command entry fast. This spec defines a prompt contract that is Obsidian‑first, vault‑first, and deterministic.

---

## 2. Input Modes and Prefixes

There are three modes, determined by the first non‑whitespace characters.

1. **Command mode**  
   Prefix: `OK ` or `:`  
   Example: `OK MAKE svg sandbox:tree.svg`

2. **Shell mode**  
   Prefix: `/`  
   Example: `/ls -la`

3. **Question mode**  
   Default if no prefix matches.  
   Example: `How do I export my vault?`

---

## 3. Parsing Rules

1. **Trim left whitespace**, then inspect prefix.
2. **Command mode** if input starts with `OK` followed by whitespace, or starts with `:`.  
   - Normalize `OK` or `:` to a single internal prefix `OK`.
3. **Slash mode** if input starts with `/`.  
   - If the first token matches a **slash command** (see section 4), treat as uCODE command.  
   - Otherwise treat as **shell**.
4. **Question mode** if none of the above matches.
5. **Command naming restriction:** uCODE commands must **not** start with digits (`0-9`) or `-`/`=`.  
   - This reserves numeric‑first input for menu selection (see section 7).

---

## 4. Slash Commands

Slash commands are a **small, explicit list** reserved for uCODE. Everything else after `/` is shell.

**Initial slash commands (v1):**
1. `/render` → alias for `OK RENDER`
2. `/help` → alias for `OK HELP`
3. `/whoami` → alias for `OK WHOAMI`

**Rule:**  
If input starts with `/` and the first token equals a known slash command, route to uCODE. Otherwise route to shell.

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

1. `/` commands are logged to `vault/07_LOGS/`.
2. Detect destructive patterns (`rm`, `mv`, `>`, `|`, `sudo`) and require confirmation.
3. Reject shell commands that target outside the repo root unless explicitly allowed.

---

## 9. Examples

```text
OK MAKE svg sandbox:tree.svg
```
Creates an SVG file at `vault/sandbox/tree.svg`.

```text
:SETUP
```
Runs the TUI setup story.

```text
/render prose
```
Routes to uCODE `/render` slash command (alias of `OK RENDER prose`).

```text
/ls -la
```
Shell command (no slash match).

```text
How do I publish to the public lane?
```
Question mode (no prefix).

---

## 10. Implementation Notes

1. **Prefix detection** must run before any runtime command routing.
2. **TS runtime** remains script‑only and does not own the prompt.
3. **Obsidian‑first** tagging: inline `#tags` and frontmatter `tags` are indexed for autocomplete.

---

## 11. Acceptance Criteria

1. `OK` and `:` reliably route to the same uCODE command parser.
2. `/render` routes to uCODE, `/ls` routes to shell.
3. Autocomplete suggestions update based on command context.
4. Autocomplete never takes over input; suggestions require explicit accept.
5. Shell commands are logged and destructive operations prompt for confirmation.
6. When a menu is visible, numeric‑first input routes to menu selection.
