# Windows 10 Entertainment Stack

This folder scaffolds the Windows 10 living-room stack that is integrated with
the external `uDOS-sonic` repository.

## Goals

- Dual-mode Windows partitions (Media + Game)
- Controller-first boot/menu flow
- uDOS bootloader orchestrates mode switching + recovery
- Preferred shells: Kodi (Media) + Playnite (Games) with Steam as a sub-module

## Included

- `partition-layout.json` — canonical partition map for uDOS + Windows
- `controller-mapping.json` — Xbox controller input grammar
- `scripts/` — Media/Game image build plan + shell/launcher configuration
- `bootloader/` — GRUB config for uDOS + Media/Game mode boot
- `recovery/` — image restore + diagnostics hooks
- Sonic flash-pack template: `../uDOS-sonic/config/flash-packs/windows10-entertainment.json`
- Sonic device DB support:
  - query candidates with `GET /api/sonic/devices?windows10_boot=wtg&media_mode=htpc`
  - check DB status with `GET /api/sonic/db/status`
  - rebuild DB with `POST /api/sonic/db/rebuild`

## Next Steps

1. Run the Media/Game image builders on a Windows host and capture WIMs.
2. Attach mode switcher commands to the uDOS overlay (reboot into target mode).
3. Store produced payload checksums under the external `uDOS-sonic` payload/runtime tree and validate before flashing.
