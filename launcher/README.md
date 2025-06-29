# 💠 uDOS macOS Launcher Guide


**Version:** uDOS Launcher v1.0

This version uses a simplified structure with `.app`-based launch and shutdown automation.

Welcome to the **official v1.0 launcher toolkit** for uDOS. This folder contains native-friendly tools for launching uDOS cleanly from a Mac desktop or Terminal.

---
## 🛠️ First-Time Setup

To install the uDOS Desktop App:

1. Open the `launcher/` folder in Finder.
2. Double-click `Run Launcher Builder.command`.
3. This will generate the native `uDOS.app` and place it in the same folder.
4. You can then drag `uDOS.app` to your Dock or Desktop for easy access.

> 📁 **Note:** On macOS, the `uDOS` folder should be located at `~/uDOS` (your home folder). This ensures the launcher script and Docker environment resolve paths correctly when launched from the `.app` bundle.

> ℹ️ **Requirements:** This launcher toolkit assumes you have [Docker Desktop for macOS](https://www.docker.com/products/docker-desktop/) installed and running. uDOS uses container-based execution, and the launcher will not function unless Docker is available.

👉 [Download Docker Desktop for macOS](https://www.docker.com/products/docker-desktop/)

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

### 🧿 2. `uDOS Launcher.app`

- **Description:** Native `.app` bundle that runs the uDOS launcher script directly, without using Platypus or Automator.
- **Usage:**
  - Drag to Desktop or Dock.
  - Double-click to launch your `~/uDOS/launcher/uDOS_Run.sh` via Terminal.
- **Tech Notes:**
  - Built using standard macOS `.app` structure with an AppleScript wrapper that opens Terminal and runs the launcher.
  - Icon: `assets/diamond.icns` → embedded as `uDOS.icns` in the app bundle.
  - No external dependencies or editors required.
  - The app is created via the included `build-mac-launcher.sh`.

- **File Structure:**
  ```
  uDOS.app/
  └── Contents/
      ├── Info.plist
      ├── MacOS/
      │   └── uDOS_Launcher
      └── Resources/
          └── uDOS.icns
  ```

---

## 🚪 Quit-uDOS.command

- **Stops** the running uDOS container via Docker.
- Now embedded into the `.app` bundle at:
  ```
  uDOS.app/
  └── Contents/
      └── MacOS/
          └── Quit-uDOS.command
  ```
- Automatically invoked after launch (via embedded AppleScript).

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

## 🔐 Permission Fix (Coming Soon)

In some macOS environments, uDOS scripts may lose executable permissions after download or sync. We're adding self-healing logic that auto-checks and repairs script permissions on launch.

Planned logic:
- Detect `.sh` and `.command` files in `~/uDOS/launcher` and `~/uDOS/scripts`
- Automatically apply `chmod +x` if not executable
- Log results to `~/uDOS/logs/permission-check.log`

This will ensure smoother first-run experience and simplify portability across machines.

---

## 📚 Learn More

For full documentation, architecture details, and mission structure, visit the main uDOS project README:

👉 [../README.md](../README.md)