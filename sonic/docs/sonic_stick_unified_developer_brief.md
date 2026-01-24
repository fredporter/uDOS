# Sonic Stick – Unified Developer Brief
**Project:** uDOS Beta Dev  
**Codename:** Sonic Stick  
**Document Type:** Single-file system design brief  
**OS Targets:** Alpine (uDOS Core), Ubuntu (Wizard Server), Windows 10 (Gaming Layer)  
**Language:** Australian English  

---

## 1. Purpose

The **Sonic Stick** is a **128 GB bootable USB system** used to provision, repair, and manage a multi-OS machine where:

- **uDOS (Alpine Linux)** is the primary, always-on operating system  
- **Ubuntu** runs a local *Wizard Server* used during provisioning and advanced configuration  
- **Windows 10** exists as a **sealed gaming console OS** (Fortnite-compatible)  

The Sonic Stick functions as both:
- A **bootable control plane**  
- A **portable installer and recovery environment**  

It assumes **no trust in the local machine state** until provisioning is complete.

---

## 2. High-Level Architecture

```
[Sonic Stick USB]
 ├─ Bootloader (UEFI)
 ├─ uDOS Core (Alpine Linux, TUI)
 ├─ Thin GUI Layer (Tauri – fullscreen, single-process)
 ├─ Ubuntu Wizard Server (optional runtime)
 ├─ Installers & Images
 └─ Provisioning Toolchain

[Local Machine Storage]
 ├─ EFI System Partition
 ├─ uDOS (Alpine)
 ├─ Ubuntu Wizard (optional, service-only)
 └─ Windows 10 Gaming (sealed)
```

---

## 3. Sonic Stick – USB Setup (128 GB)

### 3.1 USB Partition Layout (Recommended)

```
USB DEVICE (128 GB)

[ ESP ]            512 MB   FAT32    (UEFI boot)
[ CORE_RO ]        8  GB    squashfs (read-only uDOS core)
[ CORE_RW ]        8  GB    ext4     (overlay / state)
[ WIZARD_IMG ]     20 GB    ext4     (Ubuntu image / rootfs)
[ INSTALLERS ]     60 GB    exFAT    (Windows, drivers, tools)
[ CACHE ]          ~30 GB   ext4     (downloads, logs)
```

### 3.2 Boot Behaviour

- USB boots via **UEFI only**  
- Secure Boot: **off (v0)**  
- USB always boots into **uDOS Core (Alpine)**  

No automatic boot into local OS unless explicitly selected.

---

## 4. uDOS Core (Primary Runtime on USB)

### 4.1 Base OS

- **Alpine Linux**
- musl libc
- BusyBox core
- init: `openrc`

Chosen for:
- Small footprint
- Fast boot
- Deterministic behaviour
- Excellent containerisation

---

### 4.2 Interface Model

#### Core Interface
- **TUI-first**
- ncurses-based menus
- Keyboard-only operation

#### Thin GUI Layer
- **Tauri**
- Single fullscreen window
- One process
- No desktop environment
- WebView renders local UI only

```
TTY → uDOS TUI
       ↳ Launch Tauri UI (optional)
          ↳ Fullscreen wizard / dashboard
```

No window manager. No multitasking UI.

---

### 4.3 Responsibilities

uDOS Core handles:

- Hardware discovery
- Disk enumeration
- Partitioning & formatting
- OS installation orchestration
- Bootloader setup
- Firmware handoff
- Reboot routing (uDOS ↔ Windows ↔ Wizard)

It never depends on:
- Network
- Local OS state
- Installed software on disk

---

## 5. Ubuntu Wizard Server (Secondary OS / Service Layer)

### 5.1 Purpose

Ubuntu is **not** a daily OS.

It exists solely to:
- Run a **local Wizard Server**
- Provide a richer userspace for:
  - Complex install flows
  - Long-running tasks
  - Optional web-based UI

---

### 5.2 Deployment Modes

**Mode A – USB-Hosted**
- Ubuntu rootfs runs from USB
- Mounted only when needed
- No persistence on local disk

**Mode B – Local Disk (Optional)**
- Minimal Ubuntu installed to local disk
- No GUI
- Boots only when explicitly selected
- Runs Wizard Server on localhost

---

### 5.3 Wizard Server Responsibilities

- Drive layout planning
- Validation checks
- OS install coordination
- Progress reporting
- Recovery workflows
- API consumed by Tauri UI

Ubuntu remains invisible unless explicitly invoked.

---

## 6. Local Machine – Ideal Drive Setup

### 6.1 Single-Disk Layout

```
LOCAL DISK

[ EFI ]            512 MB   FAT32
[ uDOS Alpine ]     20 GB   ext4 / btrfs
[ Ubuntu Wizard ]   20 GB   ext4 (optional)
[ Shared Data ]     X  GB   exFAT / NTFS (optional)
[ Windows Gaming ]  80–120 GB NTFS
```

---

### 6.2 Dual-Disk Layout (Preferred)

```
DISK 1 (Primary)
- EFI
- uDOS Alpine
- Ubuntu Wizard (optional)

DISK 2 (Secondary)
- Windows 10 Gaming (sealed)
```

This provides:
- Physical isolation
- Cleaner boot semantics
- Easier recovery

---

## 7. Windows 10 Gaming Layer

### 7.1 Target Characteristics

- **Windows 10 (unactivated)**
- Local account only
- No Microsoft login
- No personalisation required

This configuration is legal, free, and Fortnite-safe.

---

### 7.2 Installation Source

Installed **from Sonic Stick** using:
- Official Microsoft ISO
- Scripted installer (`wimlib`-based)
- Deterministic partition targeting

---

### 7.3 “Console Mode” Hardening

Applied automatically post-install:

**Disabled / Removed**
- Cortana
- OneDrive
- Telemetry services (best effort)
- Background apps
- Search indexing
- Update auto-reboots
- Consumer features

**Installed**
- GPU drivers (vendor-detected)
- DirectX runtimes
- VC++ redistributables
- Epic Games Launcher
- Fortnite (optional staged download)

Windows is treated as **immutable** after setup.

---

## 8. Boot & Reboot Model

### 8.1 Boot Priority

1. uDOS Alpine (default)
2. Windows Gaming
3. Ubuntu Wizard (hidden / advanced)

---

### 8.2 Reboot Control

From uDOS:

```bash
reboot-to-windows
reboot-to-udos
reboot-to-wizard
```

Implemented via:
- GRUB environment flags
- EFI boot order manipulation

The user never needs to interact with raw firmware menus.

---

## 9. Run-From-USB Capability

The Sonic Stick supports:

- Running installers directly from USB
- Disk and filesystem utilities
- Firmware flashing (explicit consent required)
- Offline driver injection
- Recovery boot even on broken systems

Local disks are always treated as **targets**, never dependencies.

---

## 10. Explicit Non-Goals

The Sonic Stick does **not** attempt to:

- Run Fortnite on Linux
- Use Wine, Proton, or emulation
- Bypass anti-cheat systems
- Provide a daily Windows environment
- Ship a traditional desktop UI

---

## 11. Success Criteria

- Full machine provisioning achievable in a single USB-booted session
- uDOS remains the default daily OS
- Windows boots cleanly and runs Fortnite with no EAC errors
- Windows is perceived as a **gaming console**, not a general-purpose OS
- System is fully recoverable after disk failure or corruption

---

## 12. Summary

The **Sonic Stick** is a **portable control plane** for a role-separated, multi-OS system:

- Alpine Linux for speed, control, and determinism
- Ubuntu for orchestration when complexity demands it
- Windows only where anti-cheat forces it

This is not traditional dual-boot.

This is **operating system role separation by design**.

---