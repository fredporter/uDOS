# uDOS Xbox-Style Entertainment System  
## Platform Spec — Windows 10 (Media Mode) + Game Partition (Game Mode)

---

## 1. Target Hardware Profile (Xbox One–Class Reference)

**Xbox One is the UX reference, not necessarily the literal hardware.**

### Reference Assumptions
- Controller standard: Xbox One controller (XInput)
- CPU class: x86_64 (low-power desktop / mini-PC equivalent)
- GPU class: Integrated or low-profile discrete GPU
- Form factor: Living-room friendly (mini-PC, NUC, ITX, console-style case)

### Minimum Practical Hardware
| Component | Spec |
|--------|-----|
| CPU | Intel i5 6th gen+ / AMD Ryzen 3+ |
| RAM | 8 GB (16 GB recommended) |
| Storage | 256 GB SSD minimum |
| GPU | Integrated OK, DX11+ |
| Input | Xbox One controller (USB or Bluetooth) |
| Output | HDMI (1080p minimum) |

---

## 2. Storage & Partition Layout

```
Physical Disk (SSD)
│
├─ uDOS_BOOT          (512 MB – 1 GB)
│   └─ GRUB + recovery
│
├─ uDOS_CORE          (8–16 GB)
│   └─ uDOS Linux (TUI + thin GUI)
│
├─ WINDOWS_MEDIA      (40–80 GB)
│   └─ Windows 10 (Media Mode)
│
├─ WINDOWS_GAMES      (Remainder)
│   └─ Game installs + launchers
│
└─ SHARED_DATA        (Optional)
    └─ ROMs, media, saves
```

---

## 3. Boot & Mode Selection Flow

### Cold Boot Experience (Controller-First)

```
Power On
   ↓
uDOS Bootloader
   ↓
Controller Detected?
   ↓
uDOS Mode Selector
   ├─ Media Mode
   └─ Game Mode
```

- No keyboard required
- Xbox controller navigates everything
- Keyboard/mouse optional

---

## 4. Media Mode (Windows 10 — Locked Down)

### Purpose
- Streaming
- Local media
- Retro gaming
- Casual PC games
- Couch-first UX

### OS
- Windows 10 LTSC preferred
- Telemetry disabled
- Updates frozen or manual
- Desktop hidden by default

### Shell Replacement

```
Windows Boot
   ↓
Auto-login
   ↓
Media Shell (Fullscreen)
```

Shell options:
- Kodi
- Playnite (Fullscreen)
- Steam Big Picture
- Custom uDOS Media Launcher

### Allowed
- Streaming apps
- RetroArch
- Emulator frontends
- Casual Steam titles

### Hidden
- Explorer
- Taskbar
- System notifications
- Background apps

---

## 5. Game Mode (Windows 10 — Performance Partition)

### Purpose
- Full PC gaming
- AAA titles
- Mods
- Controller + KB/M

### Behaviour
- Boots to Steam / Playnite / uDOS Game Launcher
- Desktop optional
- Performance-first tuning

| Media Mode | Game Mode |
|---------|----------|
| Locked down | Open |
| Controller-only | Controller + KB/M |
| Low background load | Full performance |

---

## 6. Controller Input Grammar (Xbox One)

### Global Controls
| Button | Action |
|------|------|
| Xbox | uDOS System Menu |
| A | Confirm |
| B | Back |
| X | Context |
| Y | Search / Info |
| Menu | Options |
| View | Overlay / Mode |
| LB / RB | Tab |
| LT / RT | Fast scroll |
| D-Pad | Navigation |
| Left Stick | Primary |
| Right Stick | Secondary |

### Long Press
- Xbox: Mode switcher
- View: uDOS overlay
- Menu: Power / sleep

---

## 7. Mode Switching

```
Xbox Button (Hold)
   ↓
uDOS System Overlay
   ├─ Switch to Media Mode
   ├─ Switch to Game Mode
   ├─ Sleep
   └─ Power Off
```

Triggers clean shutdown and reboot into target mode.

---

## 8. uDOS Core Responsibilities

uDOS Linux (hidden layer):
- Bootloader ownership
- Mode switching
- Controller detection
- Power states
- Recovery

Provides:
- Input abstraction
- System policy
- Safe fallback

---

## 9. Recovery & Maintenance

- Boot into uDOS Core (TUI)
- Restore Media Mode image
- Rebuild partitions
- Diagnostics
- Controller remapping

Update strategy:
- uDOS: controlled
- Media Mode: frozen snapshot
- Game Mode: user-managed

---

## 10. Design Philosophy

- Xbox One defines modern controller UX
- Windows ensures compatibility
- uDOS enforces structure and safety
- Dual-mode avoids compromise

**A console without permission.**

---

## 11. Future Extensions

- Offline-first mode
- LAN co-op uDOS nodes
- Achievements
- Controller scripting
- Guest / kids modes
