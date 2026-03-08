# Windows10 Entertainment Scripts (Placeholders)

These scripts are scaffolds for future Media/Game mode image builders.
They intentionally do not perform any destructive operations yet.

- `build-media-mode.ps1` — build Windows Media Mode image
- `build-game-mode.ps1` — build Windows Game Mode image

Integration notes:
- Flash-pack metadata is defined in `../uDOS-sonic/config/flash-packs/windows10-entertainment.json`.
- Device capability selection can be pre-filtered with:
  - `GET /api/sonic/devices?windows10_boot=wtg&media_mode=htpc`
  - `GET /api/sonic/db/status`
