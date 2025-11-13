# ⚠️ Documentation Moved

> **This file has been superseded by the wiki.**

For current testing documentation, see:
- **[Contributing](../../wiki/Contributing.md)** - Testing standards
- **[Dev Rounds Workflow](../../wiki/Dev-Rounds-Workflow.md)** - Development cycle including testing

---

# uDOS v1.0.0 Command Testing Routine (LEGACY)

This document outlines the manual testing procedure for each command in uDOS v1.0.0 to ensure stability and functionality for the deversioned release.

**Tester:** ____________________
**Date:** ____________________

## Testing Instructions

For each command listed below:
1.  Run the command in the uDOS terminal.
2.  Observe the output and behavior.
3.  Note any errors, unexpected behavior, or suggestions for improvement.
4.  Mark the command as "Pass" or "Fail".

---

## AI Commands

### ASK
- **Syntax:** `ASK "<question>" [FROM "<panel>"]`
- **Test:**
    1. `ASK "What is uDOS?"`
    2. Create a panel with text and run `ASK "Summarize this" FROM "panel_name"`
- **Expected:** Returns a relevant answer from the AI.
- **Result:** Pass / Fail
- **Notes:**

### EXPLAIN
- **Syntax:** `EXPLAIN "<command>"`
- **Test:** `EXPLAIN "ls -l"`
- **Expected:** Explains the shell command.
- **Result:** Pass / Fail
- **Notes:**

### GENERATE
- **Syntax:** `GENERATE "<description>"`
- **Test:** `GENERATE "a script to list files in the sandbox"`
- **Expected:** Generates a uDOS script.
- **Result:** Pass / Fail
- **Notes:**

### DEBUG
- **Syntax:** `DEBUG "<error message>"`
- **Test:** `DEBUG "FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.txt'"`
- **Expected:** Provides debugging help for the error.
- **Result:** Pass / Fail
- **Notes:**

### AI CLEAR
- **Syntax:** `AI CLEAR`
- **Test:** `AI CLEAR`
- **Expected:** Clears the AI conversation history.
- **Result:** Pass / Fail
- **Notes:**

---

## System Commands

### CONFIG
- **Syntax:** `CONFIG <list|get|set|validate> [key] [value]`
- **Test:**
    1. `CONFIG list`
    2. `CONFIG get UDOS_USERNAME`
    3. `CONFIG set UDOS_USERNAME test_user`
    4. `CONFIG get UDOS_USERNAME` (verify change)
    5. `CONFIG validate`
- **Expected:** Manages configuration correctly.
- **Result:** Pass / Fail
- **Notes:**

### BLANK
- **Syntax:** `BLANK`
- **Test:** `BLANK`
- **Expected:** Clears the terminal screen.
- **Result:** Pass / Fail
- **Notes:**

### SPLASH
- **Syntax:** `SPLASH [<text>|FILE <path>|LOGO]`
- **Test:**
    1. `SPLASH` (should default to LOGO)
    2. `SPLASH "TESTING"`
    3. `SPLASH LOGO`
    4. `SPLASH FILE README.MD`
- **Expected:** Displays splash screens correctly.
- **Result:** Pass / Fail
- **Notes:**

### HELP
- **Syntax:** `HELP [<command_name>]`
- **Test:**
    1. `HELP`
    2. `HELP ASK`
    3. `HELP NONEXISTENT_COMMAND`
- **Expected:** Shows general help, specific help, and an error for a nonexistent command.
- **Result:** Pass / Fail
- **Notes:**

### SHOW
- **Syntax:** `SHOW [file_path]`
- **Test:**
    1. `SHOW README.MD`
    2. `SHOW --web README.MD`
- **Expected:** Displays file content in the terminal and in the web viewer.
- **Result:** Pass / Fail
- **Notes:**

### RUN
- **Syntax:** `RUN "<script_file>"`
- **Test:** `RUN examples/simple-setup.uscript`
- **Expected:** Executes the script successfully.
- **Result:** Pass / Fail
- **Notes:**

### EDIT
- **Syntax:** `EDIT "<file>"`
- **Test:**
    1. `EDIT new_test_file.txt` (should offer to create)
    2. `EDIT README.MD`
- **Expected:** Opens the file in the configured editor.
- **Result:** Pass / Fail
- **Notes:**

### REPAIR
- **Syntax:** `REPAIR [--check|--auto|--report|--pull|--upgrade-pip]`
- **Test:**
    1. `REPAIR`
    2. `REPAIR --check`
    3. `REPAIR --report`
- **Expected:** Runs health checks and reports status without errors.
- **Result:** Pass / Fail
- **Notes:**

### UNDO / REDO
- **Syntax:** `UNDO`, `REDO`
- **Test:**
    1. Run a reversible command (e.g., `BLANK`).
    2. `UNDO`
    3. `REDO`
- **Expected:** `UNDO` reverts the action, `REDO` reapplies it.
- **Result:** Pass / Fail
- **Notes:**

### REBOOT
- **Syntax:** `REBOOT`
- **Test:** `REBOOT`
- **Expected:** Restarts the uDOS session gracefully.
- **Result:** Pass / Fail
- **Notes:**

### STATUS
- **Syntax:** `STATUS [--live]`
- **Test:**
    1. `STATUS`
    2. `STATUS --live` (let it run for a few cycles)
- **Expected:** Displays system status. Live mode should update automatically.
- **Result:** Pass / Fail
- **Notes:**

### VIEWPORT
- **Syntax:** `VIEWPORT`
- **Test:** `VIEWPORT`
- **Expected:** Displays the current terminal dimensions and grid layout.
- **Result:** Pass / Fail
- **Notes:**

### PALETTE
- **Syntax:** `PALETTE`
- **Test:** `PALETTE`
- **Expected:** Displays the color palette reference.
- **Result:** Pass / Fail
- **Notes:**

### DASH
- **Syntax:** `DASH [WEB]`
- **Test:**
    1. `DASH`
    2. `DASH WEB`
- **Expected:** Displays the CLI dashboard and opens the web dashboard.
- **Result:** Pass / Fail
- **Notes:**

### TREE
- **Syntax:** `TREE [<folder>|--depth=N]`
- **Test:**
    1. `TREE`
    2. `TREE core --depth=1`
- **Expected:** Generates and displays the repository structure.
- **Result:** Pass / Fail
- **Notes:**

### OUTPUT
- **Syntax:** `OUTPUT <START|STOP|STATUS|LIST> [output_name]`
- **Test:**
    1. `OUTPUT LIST`
    2. `OUTPUT START dashboard`
    3. `OUTPUT STATUS dashboard`
    4. `OUTPUT STOP dashboard`
- **Expected:** Manages web output servers correctly.
- **Result:** Pass / Fail
- **Notes:**

### THEME
- **Syntax:** `THEME [<name>|LIST|SET <name>|STATUS]`
- **Test:**
    1. `THEME LIST`
    2. `THEME SET GALAXY`
    3. `THEME STATUS`
- **Expected:** Manages and displays themes.
- **Result:** Pass / Fail
- **Notes:**

---

## File Commands

### NEW
- **Syntax:** `NEW [<filename>]`
- **Test:**
    1. `NEW` (interactive mode)
    2. `NEW my_new_file.md`
- **Expected:** Creates a new file from a template.
- **Result:** Pass / Fail
- **Notes:**

### DELETE
- **Syntax:** `DELETE [<filename>]`
- **Test:** `DELETE my_new_file.md`
- **Expected:** Deletes the specified file after confirmation.
- **Result:** Pass / Fail
- **Notes:**

### COPY
- **Syntax:** `COPY <source> [<destination>]`
- **Test:** `COPY README.MD README.bak`
- **Expected:** Copies the file.
- **Result:** Pass / Fail
- **Notes:**

### MOVE
- **Syntax:** `MOVE <source> [<destination>]`
- **Test:** `MOVE README.bak sandbox/README.bak`
- **Expected:** Moves the file.
- **Result:** Pass / Fail
- **Notes:**

### RENAME
- **Syntax:** `RENAME <old_name> [<new_name>]`
- **Test:** `RENAME sandbox/README.bak sandbox/README.backup`
- **Expected:** Renames the file.
- **Result:** Pass / Fail
- **Notes:**

---

## Map Commands

### MAP
- **Syntax:** `MAP [STATUS|VIEW|LAYER]`
- **Test:** `MAP`
- **Expected:** Shows current map status.
- **Result:** Pass / Fail
- **Notes:**

### GOTO
- **Syntax:** `GOTO <x> <y>`
- **Test:** `GOTO 10 10`
- **Expected:** Changes map coordinates.
- **Result:** Pass / Fail
- **Notes:**

### MOVE (Map)
- **Syntax:** `MOVE <dx> <dy>`
- **Test:** `MOVE 1 0`
- **Expected:** Moves the map position relatively.
- **Result:** Pass / Fail
- **Notes:**

### LAYER
- **Syntax:** `LAYER [<layer_name>]`
- **Test:**
    1. `LAYER` (lists layers)
    2. `LAYER SURFACE`
- **Expected:** Lists and switches map layers.
- **Result:** Pass / Fail
- **Notes:**
