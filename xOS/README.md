# 🌀 uDOS macOS Launch Guide

Welcome to the **macOS launch toolkit** for uDOS. This folder contains native-friendly tools for launching uDOS cleanly from a Mac desktop or Terminal.

---

## 🧭 Launch Options (macOS)

### ✅ 1. `Launch-uDOS.command`

- **Description:** Recommended method for developers and terminal users.
- **Usage:**
  - Double-click `Launch-uDOS.command` OR
  - Run it from Terminal:
    ```bash
    bash xOS/Launch-uDOS.command
    ```
- **Behavior:** Resizes terminal, checks Docker, cleans previous containers, starts fresh uDOS CLI.

---

### 🌀 2. `🌀 uDOS Docker Launch.app`

- **Description:** Automator-based `.app` launcher for desktop use.
- **Usage:**
  - Drag to Dock or Desktop.
  - Double-click to launch uDOS via terminal.
- **Note:** Launching the `.app` may cause macOS to generate system files in:
  - `Contents/`
  - `_CodeSignature/`
  - `Resources/`
  - `document.wflow`, etc.

These are ignored by `.gitignore` and **should not be committed** unless packaging a release.

---

## 🚪 `Quit-uDOS.command`

- **Stops** the running uDOS container.
- Useful if you're done with a session or need a manual shutdown.

```bash
bash xOS/Quit-uDOS.command```