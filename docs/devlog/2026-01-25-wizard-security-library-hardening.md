# 2026-01-25 — Wizard Security + Library Hardening

- Added admin auth guard for Wizard admin surfaces (port manager, logs, device list, library routes) and tightened device auth checks.
- Hardened web admin app: localhost-only by default, admin token requirement for sensitive routes, removed external QR dependency, path traversal protections for POKE + mesh sync.
- Implemented Alpine APK build flow, APKINDEX generation (optional signing), and toolchain update endpoint.
- Added library repo cloning/build/packaging APIs and CLI wrappers, plus dependency inventory and APK status checks.
- Updated Wizard dashboard Library view to expose new library/APK tooling with admin token handling.
- Wired dashboard routes to admin-token protected endpoints (Devices, Logs, Config, GitHub) and added mesh endpoints to Wizard Server.
- Added router-level auth guard for config/provider routes and removed a redundant server signature helper.
- Documented remaining dashboard placeholders (Catalog/Webhooks/POKE controls) as TODO.
- Added POKE service control endpoints and wired the POKE dashboard actions.
- Added local QR SVG rendering for device pairing and centralized admin token input in the top bar.
- Added dashboard status banner for missing admin token and included qrcode in Wizard web startup installer.
- Added Wizard repair/self-heal service (venv bootstrap, dependency installs, dashboard build, Alpine toolchain update) plus backup/restore endpoints.
- Added artifact store endpoints and dashboard UI for managing installers/downloads/upgrades/backups locally.
- Implemented Catalog and Webhooks APIs + dashboard views, plus clearer admin-token error handling for Devices/POKE.
- Migrated Font Manager, Pixel Editor, Layer Editor, and SVG Processor into Wizard dashboard with new font + layer persistence APIs.
- Removed Goblin routes for those tools and fixed Wizard startup error in webhook router setup.
- Added DEV MODE TUI commands (dev on/off/status/clear), AI context bundling for Vibe/Mistral, and basic git/workflow/log helpers in Wizard TUI.
