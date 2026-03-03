# Home Assistant Bridge Contract

**Status:** Active optional v1.5 bridge

---

## Goal
Expose a minimal contract so Home Assistant can discover uDOS services and interact via Wizard.

---

## Wizard Endpoint
`/api/ha/`

## Contract Files
- **Wizard API contract (this doc):** `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- **Service definition + routes:** `library/home-assistant/bridge.json`
- **uHOME runtime/install companion spec:** `docs/specs/UHOME-v1.5.md`

### Required Routes (v1.5 target)
- `GET /api/ha/status`
  - Returns bridge status and version.
- `GET /api/ha/discover`
  - Returns available uDOS entities/services.
- `POST /api/ha/command`
  - Execute safe uDOS/uHOME controller commands (restricted allowlist).

---

## Response Shape (Example)
```json
{
  "bridge": "udos-ha",
  "version": "0.1.0",
  "status": "ok",
  "entities": [
    {
      "id": "udos.render",
      "type": "service",
      "name": "Render Vault",
      "capabilities": ["render"]
    }
  ]
}
```

---

## Security
- Default: disabled unless explicitly enabled in Wizard config.
- LAN-only by default.
- Admin token required for command execution.
- Explicit allowlist for write/control actions.

---

## Container Link
- Home Assistant container exists at `library/home-assistant/`.
- `library/home-assistant/bridge.json` is the canonical service definition for the Wizard bridge.
- This document explains the uDOS side (Wizard API surface and policy).

## uHOME Controller UX Scope

The bridge is the control plane for uHOME game-controller UX surfaces:
- broadcast source/tuner discovery
- DVR rule control
- ad-processing mode control
- playback target handoff

For v1.5, the bridge is optional Wizard-owned control-plane support. It is not
required for a valid baseline `uHOME` install.
