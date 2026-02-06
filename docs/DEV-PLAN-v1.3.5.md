# v1.3.5 Dev Plan (No Dates)

**Source of truth:** `docs/ROADMAP-TODO.md` (v1.3.5 Wireless & Packet Networks)
**Status:** ✅ Complete

## Scope
- Ship Wizard networking standard and MeshCore integration.
- Prepare foundations for delivery/transport in v1.3.6.

## Priorities (Ordered)

### P0 — Wizard Networking Standard (wizard/ + library/meshcore)
**Dependencies:** v1.3.4 Beacon Portal infrastructure
**Owner:** Wizard, MeshCore
**Status:** ✅ Complete
**Breakdown:**
- Local pairing flow (QR/NFC)
- Ed25519 peering handshake
- WireGuard tunnel automation + key rotation
- RadioLink daemon integration

### P1 — MeshCore Integration (library/meshcore)
**Dependencies:** Wizard networking standard
**Owner:** MeshCore
**Status:** ✅ Complete
**Breakdown:**
- Relay daemon + topology sync service
- Relay monitoring dashboard
- Coverage planning tooling

## Execution Notes
- Keep offline-first trust model explicit in policy docs.
- Avoid automatic peering; opt-in only.
