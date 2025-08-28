# uDOS Omni-Device uCODE Window – Implementation Roadmap
Version: 2025-08  
Target: uDOS v1.3 Repository

---

## 1. Cross-Platform Core (CLI Foundation)
- [ ] Standardise all launch commands under `uCORE/bin/udos`.
- [ ] Enforce POSIX-compatible shell scripting (`uSCRIPT/library/shell/`).
- [ ] Use `#!/usr/bin/env bash` and `python3` for maximum Mac/PC/Unix portability.
- [ ] Create wrapper shims only when OS-specific behaviour is unavoidable.
- [ ] Add UTF-8 enforcement script (`uSCRIPT/library/shell/ensure_utf8.sh`) and source it from every entry point.

---

## 2. Omni-Device Window = Browser UI
- [ ] **Backend**  
  - Add `uSERVER/endpoints/ucode/` REST + WebSocket routes:  
    - `GET /ucode` → serve SPA  
    - `WS /ucode/stream` → live logs  
    - `POST /ucode/run` → trigger execution
- [ ] **Frontend**  
  - Build SPA inside `uCORE/launcher/universal/ucode-ui/`.  
  - Core features: log pane, prompt bar, file picker, “copy as Markdown”.
- [ ] **Launch Flow**  
  - Extend CLI (`udos ucode`) to:  
    1. Start backend  
    2. Print access URL  
    3. Auto-open in browser (`open`, `xdg-open`, `start` depending on OS).  
- [ ] Optional: wrap same SPA in Tauri/Electron/Tauri-lite shell for kiosk/native deployments.

---

## 3. Terminal Compatibility (Mac Focus)
- [ ] Force UTF-8 locale via `ensure_utf8.sh`.  
- [ ] Document recommended fonts (JetBrains Mono Nerd Font, Menlo, SF Mono).  
- [ ] Replace hard-coded ANSI escapes with `tput` (terminfo safe).  
- [ ] Add `UDOS_GLYPHS` auto-detect (unicode vs ascii).  
- [ ] Centralise ASCII/Unicode renderers under `uCORE/code/compat/` and `uSCRIPT/library/ucode/`.  

---

## 4. Tauri Full-Screen & Display Sizing
- [ ] Add `src-tauri/src/monitors.rs` command:
  ```rust
  #[tauri::command]
  fn list_monitors(window: tauri::Window) -> tauri::Result<Vec<serde_json::Value>> { ... }
  ```
  Returns monitor name, size, workArea, scale factor.
- [ ] Expose to JS via `invoke('list_monitors')`.
- [ ] In UI bootstrap, call:
  ```ts
  import { getCurrentWindow } from '@tauri-apps/api/window';
  await getCurrentWindow().setFullscreen(true);
  ```
  - macOS: use `setSimpleFullscreen(true)` for single-Space behaviour.
- [ ] Store display info in `sandbox/tasks/active/` for debugging/logging.
- [ ] Add a React hook (`useMonitors()`) that hydrates layout dimensions.

---

## 5. Repository Integration
- **Frontend/Browser UI** → `uCORE/launcher/universal/ucode-ui/`  
- **Backend Endpoints** → `uSERVER/endpoints/ucode/`  
- **Scripts & UTF-8 Helpers** → `uSCRIPT/library/shell/`  
- **Render Fallbacks** → `uCORE/code/compat/`  
- **Tauri Native Layer** → `uCORE/launcher/platform/{macos,windows,linux}/`

---

## 6. Documentation & Roll-Out
- [ ] Create `docs/development/ucode-window.md` describing:  
  - Browser + Tauri workflows  
  - Mac Terminal setup guide  
  - Multi-monitor scaling notes  
- [ ] Update main `README.md` with new “Omni-Device uCODE Window” feature.  
- [ ] Add usage examples into `wizard/notes/`.

---

✅ **Outcome**:  
A portable “uCODE window” running identically on macOS, Windows, Linux (and optionally mobile browsers), with native full-screen/kiosk option via Tauri, and terminal output that looks correct everywhere.
