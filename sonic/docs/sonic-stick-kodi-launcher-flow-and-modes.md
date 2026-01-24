# Sonic Stick – Kodi Launcher Flow (ASCII) + Mode Boot Experience

---

## A) Kodi launcher flow diagrams (ASCII)

### Option A: “Kodi is the shell” (most appliance‑like)
```
[Power On]
   |
   v
[Windows Boot]
   |
   v
[Auto‑Login]
   |
   v
[Start Kodi Fullscreen]
   |
   +--> Movies / TV / Music (Local Library)
   |
   +--> Plex (Launch Plex app OR Plex‑in‑Kodi)
   |
   +--> Streaming Apps (Launch Edge/Chrome shortcuts)
   |
   +--> WantMyMTV (Launch kiosk browser)
   |
   v
[Sleep / Hibernate]
```

### Option B: “Mode Selector first” (clear separation)
```
[Power On]
   |
   v
[Windows Boot + Auto‑Login]
   |
   v
[Sonic Stick Mode Selector]
   |
   +--> (A) MEDIA MODE  ---------> [Launch Kodi Fullscreen]
   |                                 |
   |                                 +--> Plex / Streaming / WantMyMTV
   |
   +--> (B) GAME SERVER MODE -----> [Minimal UI / Dashboard]
                                     |
                                     +--> Server status / start/stop services
                                     +--> Optional: Launch Steam Big Picture
```

---

## B) “Media Mode” vs “Game Server Mode” boot experience

### Media Mode (default for living room)
**Goal:** feel like a Smart TV, not a PC.

**Boot behaviour**
- Windows auto‑login
- Immediately launches **Kodi** in full‑screen
- Background services continue as normal (game servers, Plex server if enabled)

**Exit / power behaviour**
- “Power” on remote = Kodi exit → triggers **Sleep/Hibernate**
- Hidden “Admin” entrypoint for maintenance (keyboard combo or menu item)

**Success metric**
- A non‑technical person can use it with a remote in under 10 seconds.

---

### Game Server Mode (headless‑first / maintenance‑first)
**Goal:** minimise distractions; keep the box stable.

**Boot behaviour**
- Windows auto‑login
- Launch a **Sonic Stick Dashboard** (simple UI)
- Starts/monitors server services (and can optionally start Plex server)

**Dashboard contents (minimal)**
- Status lights: CPU/RAM/Disk/Network
- Game server status: Running/Stopped + key ports
- Buttons: Start/Stop/Restart services
- Button: “Switch to Media Mode” (launch Kodi)

**Success metric**
- You can check health from the couch without touching the desktop.

---

## C) Mode selection strategies (pick one)

1. **Timed selector** at boot (e.g., 10 seconds; defaults to Media Mode)  
2. **Last‑used mode** persists across reboots  
3. **Remote override** rule (e.g., hold “Home” on boot → Media Mode)
