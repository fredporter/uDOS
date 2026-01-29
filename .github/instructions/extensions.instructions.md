extensions/api/
extensions/transport/
extensions/my-extension/
## Extensions Instructions

**Scope:** `extensions/**` — API + Transport extensions

## Critical Rules

1. Each extension needs `README.md` + `version.json`
2. No business logic duplication; delegate to Core
3. Transport policy: private (MeshCore, BT-Private, NFC, QR, Audio) allows data; Bluetooth Public is signal-only
4. Version via `python -m core.version bump <ext> ...` (never hardcode)

## Key Paths

- API: `extensions/api/`
- Transport: `extensions/transport/`
- Policy: `extensions/transport/policy.yaml`
- Version: `extensions/<ext>/version.json`

## Quick Commands

- Run API server: `python extensions/api/server.py`
- Tests: `pytest extensions/<ext>/tests/ -v`

## References

- [AGENTS.md](../../AGENTS.md)
- [extensions/README.md](../../extensions/README.md)
