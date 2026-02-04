# Home Assistant Bridge Contract (Stub)

**Status:** Draft stub (v1.3.2 target)

---

## Goal
Expose a minimal contract so Home Assistant can discover uDOS services and interact via Wizard.

---

## Wizard Endpoint
`/api/ha/`

## Contract Files
- **Wizard API contract (this doc):** `docs/HOME-ASSISTANT-BRIDGE.md`
- **Service definition + routes:** `library/home-assistant/bridge.json`

### Required Routes (Stub)
- `GET /api/ha/status`
  - Returns bridge status and version.
- `GET /api/ha/discover`
  - Returns available uDOS entities/services.
- `POST /api/ha/command`
  - Execute a basic uDOS command (read-only for v1.3.2).

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

---

## Container Link
- Home Assistant container exists at `library/home-assistant/`.
- `library/home-assistant/bridge.json` is the canonical service definition for the Wizard bridge.
- This document explains the uDOS side (Wizard API surface and policy).
