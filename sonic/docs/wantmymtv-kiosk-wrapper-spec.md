# WantMyMTV – Kiosk / Full‑Screen Wrapper Spec (Windows)

Target URL: https://wantmymtv.vercel.app/player.html

---

## 1) Requirements

- Launches **full‑screen**
- Remote/controller friendly (minimum: Back/Exit)
- No address bar / tabs / Windows chrome visible (where possible)
- Clean return path to **Kodi** (or the Mode Selector)

---

## 2) Recommended approach: Microsoft Edge Kiosk / Full‑Screen

### Behaviour
- Opens directly to WantMyMTV
- Runs full‑screen
- Browser UI is hidden/minimised depending on mode
- Exiting returns user to Kodi

### Notes
- You must define an **exit mapping** (remote button → close window), e.g. Alt+F4 or a dedicated “Back” key.
- Edge is usually the most reliable for modern video playback on Windows.

---

## 3) Alternative approach: Chrome “App Mode”

### Behaviour
- Launches a borderless app‑style window for a single URL
- Can be combined with full‑screen start

### Notes
- Still requires an exit mapping (close window → back to Kodi)

---

## 4) Kodi integration (preferred UX)

### Goal
User selects a tile inside Kodi:
- “WantMyMTV” → launches kiosk browser
- Closing kiosk → returns to Kodi automatically

### Implementation concept
- Kodi menu item triggers a Windows shortcut / script that launches the kiosk command.
- Kodi stays running in the background.

---

## 5) Remote control mapping (minimum viable)

Map these actions to keyboard keys (via FLIRC or a Bluetooth remote):

- **Back / Exit** → Close browser window (e.g., Alt+F4)
- **Home** → Close browser window (or return to Kodi)
- **Play/Pause** → Spacebar (if supported by the site)
- **Volume** → System volume keys (preferred)

Principle: **remote‑only operation**; keyboard is for maintenance only.

---

## 6) Safety & resilience

- If the browser crashes, user should still be able to:
  - Return to Kodi (Kodi remains running)
  - Relaunch WantMyMTV from Kodi tile
- Avoid “multi‑tab” browsing: keep it single‑site to reduce confusion.

---

## 7) Nice‑to‑have enhancements (later)

- Auto‑dim / screen saver prevention while playing
- “Party mode” scene: launches WantMyMTV + sets volume + disables notifications
- Sonic Stick branded tile/icon inside Kodi
