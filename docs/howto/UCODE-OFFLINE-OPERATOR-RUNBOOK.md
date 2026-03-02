# UCODE Offline Operator Runbook

Updated: 2026-02-22

Compact runbook for operating `UCODE` when network access is unavailable or unstable.

## Scope

Use this runbook for:
- No-network sessions.
- Partial network outages where cloud/provider pathways are degraded.
- Offline fallback verification after updates or installs.

## Baseline Command Order (Offline)

Run in this order:

1. `UCODE DEMO LIST`
2. `UCODE DOCS --query <topic>`
3. `UCODE SYSTEM INFO`

This is the canonical fallback routing order.

## Fast Triage

1. Confirm local demos are present:
```bash
UCODE DEMO LIST
```

2. Confirm local docs lookup works:
```bash
UCODE DOCS --query reference
UCODE DOCS --section troubleshooting
```

3. Confirm system introspection is healthy:
```bash
UCODE SYSTEM INFO
```

4. Confirm capability surface for your profile:
```bash
UCODE CAPABILITIES --filter profile:core
UCODE CAPABILITIES --filter profile:full
UCODE CAPABILITIES --filter profile:wizard
```

## Refresh Procedure (When Network Returns)

1. Run update:
```bash
UCODE UPDATE
```

2. Verify update manifest:
```bash
cat memory/ucode/update-manifest.json
cat memory/ucode/bundles/offline-content-bundle.json
```

3. Re-run offline triage:
```bash
UCODE DEMO LIST
UCODE DOCS --query reference
UCODE SYSTEM INFO
UCODE METRICS
```

## Recovery for Missing Local Assets

If demos/docs are missing:

1. Re-run:
```bash
UCODE UPDATE
```

2. Verify local asset directories:
```bash
ls -la memory/ucode/demos
ls -la memory/ucode/docs
```

3. Validate seeded examples exist:
```bash
UCODE DEMO RUN parse_file
UCODE DOCS --query "uCode Command Reference"
```

## Operator Output Checklist

Capture these fields in incident notes:
- Timestamp (UTC).
- Network state (`offline`, `degraded`, `online`).
- Commands run.
- `UCODE UPDATE` result status.
- Manifest timestamp from `memory/ucode/update-manifest.json`.
- Bundle verification status from `memory/ucode/bundles/offline-content-bundle.json`.
- Local usage summary from `memory/ucode/metrics/usage-summary.json`.
- Any missing demo/doc artifacts after refresh.

## Storage Root

Default `UCODE` offline assets live under:
- `memory/ucode/`

If `UDOS_UCODE_ROOT` is set, the handler uses that override instead.

## Related Docs

- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md`
- `docs/troubleshooting/README.md`
