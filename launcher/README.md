# 💠 uDOS macOS Launcher Guide

**Version:** uDOS Launcher v1.0

Welcome to the **official v1.0 launcher toolkit** for uDOS. This folder contains native-friendly tools for launching uDOS cleanly from a Mac desktop or Terminal.

> ℹ️ **Requirements:** This launcher toolkit assumes you have [Docker Desktop for macOS](https://www.docker.com/products/docker-desktop) installed and running. uDOS uses container-based execution, and the launcher will not function unless Docker is available.

The `Dockerfile` and `docker-compose.yml` required to build and run uDOS are located in the root `uDOS/` folder. These files define the environment, dependencies, and CLI entry point for your containerized uDOS shell. This launcher simply wraps those definitions into a repeatable local experience.

---

## 🧭 Launch Options (macOS)

### ✅ 1. `Launch-uDOS.command`

- **Description:** Primary launcher script. Recommended for developers and terminal users.
- **Usage:**
  - Double-click `Launch-uDOS.command` OR
  - Run it from Terminal:
    ```bash
    bash launcher/Launch-uDOS.command
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
bash launcher/Quit-uDOS.command
```

---

## 🗺️ uDOS Launcher Flow (ASCII Diagram)

```text
[Launch-uDOS.command]
          │
          ▼
  [Resize Terminal Window]
          │
          ▼
[Check if Docker is Running] ──► [Start Docker if Needed]
          │
          ▼
  [docker compose down]
          │
          ▼
  [docker compose build]
          │
          ▼
[docker compose run --rm udos]
          │
          ▼
[uDOS Interactive Shell Starts]
```

This flow outlines the steps taken by `Launch-uDOS.command` during execution. It ensures a clean and consistent shell session each time you launch uDOS.