# uDOS × TinyCore Roadmap

## 1. Vision
uDOS is a **layered operating environment** built on TinyCore Linux.  
It provides:

- **uCORE** → keyboard-centric CLI foundation, script containers, variable/data handling.  
- **uDOS Desktop** → point-and-click grid-based UI bridging CLI and touch/mobile.  
- **uSCRIPT** → extensible script runtime and BASIC-style interpreter.  
- **uNETWORK** → optional connected UI, future desktop + web integrations.  

TinyCore brings minimalism, persistence, and modular extensions.  
uDOS brings structure, UX, and its own model for variables, data, templates, and users.

---

## 2. Distribution Strategy

### Phase 1 — Extensions
- **`uDOS-core.tcz`**  
  - CLI tools, uVAR/uDATA/uTEMPLATE, user/session layer.  
  - Dependencies: `bash`, `coreutils`, `util-linux`, `git`, `curl`, `tmux`, `htop`.  
- **`uDOS-desktop.tcz`**  
  - Openbox, tint2, rofi, fonts, configs (themes, .xsession).  
  - Dependencies: `Xorg-7.7`, `xorg-server`, `openbox`, `tint2`, `rofi`, `xterm`, `dejavu-ttf`.  
- **`uDOS-extra.tcz`** (future)  
  - uSCRIPT containers, uNETWORK, dev mode.  

### Phase 2 — Installer Script
- Single command to fetch `.tcz` files from GitHub Releases into `/tce/optional/`.  
- Adds them to `/tce/onboot.lst` and activates immediately.  
- Example:  
  ```bash
  curl -sL https://udos.sh/install | sh
  ```

### Phase 3 — Remastered ISO
- **uDOS-TinyCore Edition**: ISO with both `uDOS-core` and `uDOS-desktop` pre-bundled.  
- Branding: ASCII boot splash, MOTD, hostnames.  
- Best path for newcomers and demos.

---

## 3. uDOS Features (Integration Details)

### 3.1 Users & Security
- **Yes** → uDOS users map to **real Linux users**.  
- uCORE integrated into login sessions.  
- Benefits:  
  - Multi-login supported (tty, ssh, GUI).  
  - uVAR, uDATA, templates scoped per user.  
  - Permissions respected by Linux itself.  

### 3.2 uVAR (Variables)
- Unified variable store for CLI + Desktop.  
- Backed by `~/.udos/vars/` JSON or key=value files.  
- Accessible via:  
  - CLI: `udos var set KEY=VAL`, `udos var get KEY`.  
  - Desktop: config panes, GUI widgets.  

### 3.3 uDATA (Data Layers)
- Structured storage at `~/.udos/data/`.  
- Supports JSON, TSV, YAML.  
- Used for state persistence, history, logs.  
- Accessible via CLI (`udos data query`) or GUI dashboards.  

### 3.4 uTEMPLATE (Templates)
- Live at `~/.udos/templates/`.  
- CLI: `udos tpl render template.tpl`.  
- Desktop: “New File” dialogues seeded by templates.  

### 3.5 uSCRIPT Containers
- Scripts run inside lightweight “containers”:  
  - Namespaced variables.  
  - Separate scratch data dirs.  
  - No heavy Docker overhead.  
- Languages supported: Bash, Python, BASIC-style (uCODE).  

### 3.6 uDOS Desktop
- Grid discipline (16×16).  
- Flat retro palette (8 colours).  
- Click-first UI (large 32 px panels, 64 px tiles).  
- Rofi grid menu + tint2 panel.  
- Window manager: Openbox (flat theme, big buttons).  

---

## 4. Persistence, Housekeeping & Logging

### Persistence
- Primary = `/opt/.filetool.lst` (TinyCore standard).  
- Ensures configs and user data in `~/.udos/` are backed up.  
- Extensions’ install scripts (`/usr/local/tce.installed/uDOS-*`) will automatically add files.  

### Housekeeping
- `udos-clean`: clears caches, temp containers, old backups.  
- Option to prune unused extensions or old logs.  

### Logging
- Centralised log directory: `~/.udos/logs/`.  
- Commands/services log to files here.  
- Rotation: keep last N logs per tool.  
- Hook into TinyCore’s syslog if available.  

---

## 5. Publishing Strategy

### Option A — TinyCore Official Repo
- Pros: discoverable via Apps browser.  
- Cons: requires upstream approval, slower release cycle, must follow strict conventions.  

### Option B — GitHub Releases (Private Channel)
- Pros: full control, rapid iteration, branding freedom.  
- Cons: users must trust external source.  

### Recommendation  
Start with **GitHub Releases** for speed and iteration.  
When stable, **submit to TinyCore repo** for visibility.  
We can maintain both: official “stable” vs GitHub “edge/nightly”.

---

## 6. Technical Milestones

### M1 — Core Extension
- Build `uDOS-core.tcz` with:  
  - CLI tools: `udos`, `uvar`, `udata`, `utpl`.  
  - Data dirs: `~/.udos/{vars,data,templates,logs}`.  
  - Post-install hook for persistence.  
- Deliver `.dep` + `.info`.

### M2 — Desktop Extension
- Build `uDOS-desktop.tcz` with:  
  - Config pack (Xresources, xsession, rofi, tint2, openbox).  
  - Post-install hook for persistence + startx autologin.  
- Deliver `.dep` + `.info`.

### M3 — One-liner Installer
- `udos-install.sh` downloads both extensions + deps from GitHub.  
- Places into `/tce/optional/` and adds to `onboot.lst`.  

### M4 — ISO Remaster
- Use `ezremaster.tcz`.  
- Create `uDOS-TinyCore.iso` with:  
  - uDOS core + desktop onboot.  
  - Branded bootloader/MOTD.  

### M5 — Advanced Features
- uSCRIPT containers.  
- Multi-user integration.  
- GUI template integration.  
- Logging dashboards.  
- uNETWORK (UI connectivity).  

---

## 7. Open Questions
- How far should uDOS diverge from TinyCore’s “tiny” ethos vs shipping more batteries-included?  
- How to define the **baseline for supported users**: VMs only? bare metal? Raspberry Pi (ARM)?  
- Should uNETWORK tie into a **browser-based UI** (served from uDOS), or remain local-only?  

---

## ✅ Next Actions
1. Build prototype `uDOS-core.tcz`.  
2. Build prototype `uDOS-desktop.tcz`.  
3. Host both on GitHub Release.  
4. Test one-liner installer inside VM.  
5. Draft `uDOS-TinyCore.iso` branding and bootloader.  
6. Extend feature set: variables → templates → scripts → desktop → network.  

---

This roadmap makes uDOS a **first-class citizen inside TinyCore**:  
- Lean and modular.  
- Adds its unique philosophy (grid UI, variables, templates, users).  
- Flexible distribution (extensions first, remastered ISO later).  
