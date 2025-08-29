# uDOS A — uCORE (CLI Only)

**Base:** Tiny Core / CorePure64  
**Role:** Minimal CLI-only distribution, boots directly into **uCORE**.  
**Audience:** Old hardware, embedded appliances, headless systems.

---

## 🚀 Installation

1. Download the image:
   ```
   uDOS-A-<arch>-<version>.iso
   uDOS-A-<arch>-<version>.img
   ```
2. Write to USB with Etcher/Rufus, or boot the ISO in a VM.
3. Default login:  
   ```
   user: tc
   pass: (empty)
   ```

---

## ▶️ Usage

- On boot, system drops straight into the `ushell` (uCORE shell).  
- All colours, registry, and process management are available.  
- Python CLI server is optional (requires `python3` package).

---

## 🔄 Updates

- Replace `uCORE.tcz` in `/tce/optional/` with the new version.
- Run:
  ```sh
  filetool.sh -b
  reboot
  ```

---

## 🛠 Recovery

- Hold **Ctrl+C** during boot to stop autostart, then drop to shell.
- Edit `/home/tc/.profile` to disable auto-launch.
- Run `filetool.sh -r` to restore last backup.

---
