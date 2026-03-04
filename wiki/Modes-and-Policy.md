# Modes and Policy

Updated: 2026-03-04
Status: short policy map

uDOS keeps mode boundaries explicit so gameplay, operator work, and contributor work do not blur together.

## Main Modes

- Ghost Mode:
  safe first-run and read-mostly mode
- User Mode:
  standard daily runtime lane
- Wizard/Admin lane:
  managed operations and service control
- Dev Mode:
  permissioned contributor access to the `@dev` workspace

## v1.5 Boundary Rule

Dev Mode is not just “editing while in Wizard”.
It is the explicit contributor lane gated by:
- admin and Dev Mode permissions
- active `@dev` workspace framework payload
- Wizard-managed activation

## Canonical Policies

- Ghost policy:
  [../docs/specs/GHOST-MODE-POLICY.md](../docs/specs/GHOST-MODE-POLICY.md)
- Runtime rebaseline:
  [../dev/docs/decisions/v1-5-rebaseline.md](../dev/docs/decisions/v1-5-rebaseline.md)
- `@dev` workspace policy:
  [../dev/docs/DEV-MODE-POLICY.md](../dev/docs/DEV-MODE-POLICY.md)
- `@dev` workspace spec:
  [../dev/docs/specs/DEV-WORKSPACE-SPEC.md](../dev/docs/specs/DEV-WORKSPACE-SPEC.md)
