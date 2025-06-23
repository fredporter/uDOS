# 🌀 uOS macOS Launch Guide

Welcome to the **macOS launch toolkit** for uOS. This folder contains native-friendly tools for launching uOS cleanly from a Mac desktop or Terminal.

---

## 🧭 Launch Options (macOS)

### ✅ 1. `Launch-uOS.command`

- **Description:** Recommended method for developers and terminal users.
- **Usage:**
  - Double-click `Launch-uOS.command` OR
  - Run it from Terminal:
    ```bash
    bash macos/Launch-uOS.command
    ```
- **Behavior:** Resizes terminal, checks Docker, cleans previous containers, starts fresh uOS CLI.

---

### 🌀 2. `Launch🌀uOS.app`

- **Description:** Automator-based `.app` launcher for desktop use.
- **Usage:**
  - Drag to Dock or Desktop.
  - Double-click to launch uOS via terminal.
- **Note:** Launching the `.app` may cause macOS to generate system files in:
  - `Contents/`
  - `_CodeSignature/`
  - `Resources/`
  - `document.wflow`, etc.

These are ignored by `.gitignore` and **should not be committed** unless packaging a release.

---

## 🚪 `Quit-uOS.command`

- **Stops** the running uOS container.
- Useful if you're done with a session or need a manual shutdown.

```bash
bash macos/Quit-uOS.command