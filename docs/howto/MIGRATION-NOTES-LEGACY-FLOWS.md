# Migration Notes: Legacy Flows to v1.4.4+

Date: 2026-02-22  
Status: Active

This note is for operators migrating from legacy pre-v1.5 command habits into the current v1.5 `ucode`-first runtime model.

## Execution Model Changes

- Standard interactive runtime is now `ucode` first.
- Dev Mode contributor tooling is a contributor surface only.
- Command dispatch order is fixed:
  1. ucode command match
  2. shell passthrough (safety gated)
  3. OK fallback or Wizard-backed handling where enabled
- Wizard MCP is the canonical tool gateway.

## Legacy Command Compatibility

The following legacy entries are still accepted and mapped:

- `RESTART` -> `REBOOT`
- `SCHEDULE` -> `SCHEDULER`
- `TALK` -> `SEND`
- `UCLI` -> `UCODE`
- `NEW` -> `FILE NEW ...`
- `EDIT` -> `FILE EDIT ...`

## Operator Checklist

1. Use `MODE STATUS` to confirm runtime mode and policy flags.
2. Use `HELP` and `HELP <COMMAND>` to inspect canonical command names.
3. Replace scripts/docs that still emit legacy tokens with canonical names.
4. Keep legacy aliases only as compatibility bridges during migration windows.

## Related References

- `docs/specs/COMMAND-DISPATCH-RC-SCOPE.md`
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
