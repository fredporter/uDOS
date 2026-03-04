# Wizard

Updated: 2026-03-04
Status: v1.5 short overview

Wizard is the networked and web-facing service layer for uDOS.

## Wizard Owns

- provider integrations
- API routes and dashboard UI
- GitHub integration and release-profile-aware automation
- managed operations, monitoring, and admin control plane
- Dev Mode controls for the `@dev` workspace

## Wizard Does Not Own

- deterministic local command logic
- direct replacement of `ucode`
- unrestricted contributor access outside the `@dev` gates

## Common Surfaces

```bash
WIZARD STATUS
WIZARD CHECK
WIZARD PROV STATUS
WIZARD START
```

API grouping in v1.5 is increasingly organized under dedicated surfaces such as:
- `/api/ops/*`
- `/api/ucode/*`
- `/api/dev/*`

## Canonical Docs

- Wizard architecture:
  [../wizard/ARCHITECTURE.md](../wizard/ARCHITECTURE.md)
- Managed operations:
  [../docs/howto/MANAGED-WIZARD-OPERATIONS.md](../docs/howto/MANAGED-WIZARD-OPERATIONS.md)
- Wizard plugin system:
  [../docs/howto/WIZARD-PLUGIN-SYSTEM.md](../docs/howto/WIZARD-PLUGIN-SYSTEM.md)
- `@dev` workspace policy:
  [../dev/docs/DEV-MODE-POLICY.md](../dev/docs/DEV-MODE-POLICY.md)
