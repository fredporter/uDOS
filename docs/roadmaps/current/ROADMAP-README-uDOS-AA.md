# uDOS AA — uCORE + uSCRIPT + uNETWORK (Runtime)

**Base:** dCore-x86_64  
**Role:** Full runtime edition, with scripting and Tauri-based UI.  
**Audience:** End users who need both CLI and graphical interface.  
**Note:** No developer toolchains. This is *runtime only*.

---

## 🚀 Installation

1. Download the image:
   ```
   uDOS-AA-<arch>-<version>.iso
   uDOS-AA-<arch>-<version>.img
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
- **uCORE** services and CLI available on TTY2+ (`Ctrl+Alt+F2`).  
- **uSCRIPT** runtime (Python venv) is preconfigured and shared with both CLI and UI.

---

## 🔄 Updates

- To update **uNETWORK (Tauri app):**
  ```sh
  uupdate uNETWORK-<ver>.tar.gz
  reboot
  ```
- To update **uSCRIPT**, replace its runtime tree and re-run bootstrap:
  ```sh
  /home/tc/uSCRIPT/setup-environment.sh
  filetool.sh -b
  reboot
  ```

---

## 🛠 Recovery

- Switch to TTY2 (`Ctrl+Alt+F2`) to access CLI if GUI misbehaves.  
- Remove or rename `/home/tc/.xsession` to disable kiosk mode.  
- Run `filetool.sh -r` to roll back to last backup.

---
