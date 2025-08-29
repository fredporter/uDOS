# uDOS B — Full Dev + Runtime (uCORE + uSCRIPT + uNETWORK + Toolchains)

**Base:** dCore-x86_64 (or Ubuntu minimal, depending on release)  
**Role:** Developer workstation image.  
**Audience:** Contributors, testers, and advanced users.

---

## 🚀 Installation

1. Download the image:
   ```
   uDOS-B-<arch>-<version>.iso
   uDOS-B-<arch>-<version>.img
   ```
2. Write to USB or boot in VM.
3. Default login:  
   ```
   user: tc
   pass: (empty)
   ```

---

## ▶️ Usage

- On boot, Xorg launches **uNETWORK** full-screen.  
- **uCORE** CLI is available on TTY2+.  
- **uSCRIPT** runtime is present and extendable.  
- Dev toolchains preinstalled:
  - Rust + Cargo
  - Node.js + npm/pnpm
  - Python + pip/venv
  - build-essential + WebKitGTK dev headers

---

## 🔄 Updates

- Runtime updates same as AA.  
- Dev updates via:
  ```sh
  sudo apt update && sudo apt upgrade     # if Ubuntu base
  sce-update <package>                    # if dCore base
  ```
- Tauri app rebuild possible directly on the machine.

---

## 🛠 Recovery

- If kiosk UI breaks, switch to TTY2 (`Ctrl+Alt+F2`).  
- Disable autostart by editing `/home/tc/.xsession`.  
- For dCore builds: `sce-load` can be used to re-import missing packages.

---
