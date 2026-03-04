# Self-Healing

Updated: 2026-03-04
Status: short maintenance map

Self-healing and repair flows are maintenance surfaces, not a separate product lane.

## Use Cases

- runtime drift
- missing local dependencies
- config and setup recovery
- Wizard readiness and repair checks

## Canonical Docs

- Managed operations:
  [../docs/howto/MANAGED-WIZARD-OPERATIONS.md](../docs/howto/MANAGED-WIZARD-OPERATIONS.md)
- Admin secret recovery:
  [../docs/howto/WIZARD-ADMIN-SECRET-CONTRACT-RECOVERY.md](../docs/howto/WIZARD-ADMIN-SECRET-CONTRACT-RECOVERY.md)
- Compost and cleanup behavior:
  [../docs/COMPOST-POLICY.md](../docs/COMPOST-POLICY.md)

## Rule

Self-healing should stay safe by default, auditable, and explicit about any mutation it performs.
