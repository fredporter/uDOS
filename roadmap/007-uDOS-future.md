# 007-uDOS-future.md
> 📘 uDOS Beta v1.6.1 – Roadmap 006: `uScript` and Visual BASIC-style `uCode`
> Date: 2025-07-13  
> Status: Drafting  
> Author: Otter

---

## 🧭 Overview

This roadmap defines the **planned evolution of the `uCode` command language** and the **`uScript` execution framework** in upcoming releases of `uDOS`. It introduces a unified scripting interface based on readable, Visual Basic–style syntax. All scripts are stored as `.md` files and can be parsed and executed using the `uCode` runtime.

`uScript` is the programmable interface layer of uDOS.

---

## 🎯 Goals

- Replace Bash-only logic with clean, human-readable command files.
- Allow users to automate tasks and define workflows in `uCode`.
- Introduce a basic interpreter layer for Visual Basic–style syntax.
- Support multi-language execution (future: BASH, JS, Python).
- Enable versioning and logging of all `uScript` executions in `uMemory`.

---

## 🗂️ Roadmap Phases

### ✅ Phase 1 – Initial Implementation (`v1.6.1`)

- [x] Define uCode BASIC-style command set.
- [x] Remove line numbers; adopt Visual Basic–style syntax.
- [x] Design `.md`-based `uScript` format (command list in Markdown).
- [x] Define core objects: `MISSION`, `MOVE`, `MILESTONE`, `LEGACY`.
- [x] Introduce shell runner stub: `ucode-runner.sh`.

### 🛠 Phase 2 – uScript Runtime Execution (Target: `v1.7.0`)

- [ ] Implement `ucode.sh run uScript/filename.md`
- [ ] Parse Markdown line-by-line, skipping comment (`'`) lines
- [ ] Validate commands against command map
- [ ] Execute `uCode` commands live via `ucode.sh`
- [ ] Log `uScript` executions to `moves-YYYY-MM-DD.md`

### 🧩 Phase 3 – Dynamic Arguments and Flow Control

- [ ] Introduce runtime variables (e.g. `SET NAME = "test"`)
- [ ] Allow `IF`, `FOR`, and `DO` block syntax
- [ ] Introduce `INCLUDE` directive to import one script into another
- [ ] Add `WAIT`, `SLEEP`, and time-based logic

### 🔁 Phase 4 – Script Scheduling and Events

- [ ] Enable background scheduled `uScript` execution (`cron`-style)
- [ ] Watcher integration: Trigger `uScript` on file/move updates
- [ ] User-defined system boot-up sequences via `uScript`

### 🌐 Phase 5 – Multi-Language Support

- [ ] Add `LANGUAGE:` front-matter tag to select script parser
- [ ] Supported runners:
  - `uCode` (default)
  - `bash`
  - `python`
  - `javascript`
- [ ] Scripts may call other scripts across languages

---

## 📁 Proposed File Structure

uScript/
├── system-setup.md         # Core setup logic
├── launch-mission.md       # Example startup sequence
├── templates/
│   └── base.md             # uScript template
├── test/
│   └── ucode-tests.md      # Syntax and parser test cases

---

## 🔍 Open Questions

- Should scripts be allowed to modify the `uCode` command set (meta-programming)?
- How should nested script execution be traced and logged?
- Should each script maintain its own run history log?

---

## 📌 Summary

The `uScript` system will elevate `uCode` from an interactive shell into a programmable execution environment. This empowers users to define logic flows in plain Markdown and interact with the uDOS system without any external tooling.

---

> Otter will maintain the first `uScript` reference library and help generate templates for common use-cases.