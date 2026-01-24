# Sonic Stick – Media & Streaming HTPC Add‑On Brief

**Add‑on module for the Windows Game Server (“Sonic Stick”)**

---

## 1) Objective

Extend the **Windows Game Server (Sonic Stick)** into a **hybrid Smart TV + Media Centre + Streaming Hub** while keeping the game‑server role intact.

Outcomes:
- **Remote‑first** living‑room UX (10‑foot interface)
- Strong **commercial streaming compatibility** (DRM‑safe via browser)
- Rich **local library** experience (NAS/USB/local)
- Optional **whole‑home streaming** via Plex
- Distinctive “ambient channel” mode via **WantMyMTV**

---

## 2) Included Feature Link

**WantMyMTV player:** https://wantmymtv.vercel.app/player.html

Use case: one‑click “music TV / ambient channel” playback from the couch.

---

## 3) System Overview

```
[ TV / Projector ]
      ↑ HDMI
[ Sonic Stick (Windows) ]
      │
      ├─ Kodi (primary 10‑foot UI)
      ├─ Plex (library sync + remote streaming)
      ├─ Browser apps (Netflix, YouTube, Disney+, Prime, etc.)
      └─ WantMyMTV (full‑screen web player)

(Game server services continue running in the background.)
```

Kodi provides the “Smart TV shell”; Plex and the browser cover modern streaming.

---

## 4) Core Components

### 4.1 Kodi (Primary TV Shell)
**Role:** Living‑room launcher and media centre
- Auto‑starts full‑screen on boot
- Handles local libraries (movies, TV, music)
- Optional: IPTV/PVR support

**Why:** Best‑in‑class 10‑foot UX and remote/controller support.

---

### 4.2 Plex (Library + Whole‑Home Streaming)
**Role:** Unified library management and streaming to other devices
- Plex Server can run on Sonic Stick (optional)
- Plex Client can be launched from Kodi (or used directly)

**Integration choices:**
- “Plex inside Kodi” (PlexKodiConnect / Plex add‑on)
- “Two apps” (Kodi for local, Plex for remote)

---

### 4.3 Browser Streaming (DRM‑Safe)
**Role:** Reliable playback for commercial platforms
- Use Edge/Chrome for best DRM support
- Launch as pinned shortcuts from Kodi or a custom launcher menu

---

### 4.4 WantMyMTV (Custom Web Player Mode)
**Role:** Instant ambient music‑channel experience
- Launch via a dedicated Kodi menu item or Windows launcher tile
- Runs in full‑screen/kiosk for remote‑only control

---

## 5) Couch UX (What the user experiences)

1. Power on TV
2. Sonic Stick boots Windows
3. Auto‑login (optional)
4. Landing screen appears (Kodi or Mode Selector)
5. User chooses:
   - Local Library (Kodi)
   - Plex (client or Kodi integration)
   - Streaming Apps (browser shortcuts)
   - WantMyMTV (one‑click full‑screen)

---

## 6) Input & Control

Supported control methods:
- IR remote (recommended: FLIRC)
- Bluetooth remote
- Xbox controller
- Mini keyboard (maintenance only)

Design principle: **everything essential is remote‑friendly**.

---

## 7) AV Capability Notes

- 4K/HDR (hardware dependent)
- Multi‑channel audio passthrough (AVR/soundbar dependent)
- Refresh‑rate switching where supported

---

## 8) Benefits & Positioning

- Turns Sonic Stick into an **everyday lounge‑room device**
- Increases household “stickiness” beyond gaming
- Avoids Smart TV ads + OEM lock‑in
- Delivers a “single box” story: **games + media + streaming**

**Positioning line:**
> The Sonic Stick Media Add‑On converts a Windows game server into a Smart TV replacement — combining streaming compatibility, local library mastery, and a one‑click music‑TV mode.

---

## 9) Optional Enhancements (Later)

- Sonic Stick branded Kodi skin (minimal)
- Profiles (Kids / Adult / Guest)
- Scheduled “Ambient Channel” start times
- Home automation hooks (wake TV + switch input + launch mode)
