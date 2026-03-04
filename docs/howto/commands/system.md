# System Commands

Version: Core v1.5
Updated: 2026-03-04

Core system commands are offline/local first.

## HEALTH

Offline stdlib shakedown for core readiness.

```bash
HEALTH
HEALTH CHECK storage
HEALTH CHECK housekeeping --scope vault
HEALTH CHECK housekeeping --scope knowledge
HEALTH CHECK housekeeping --scope dev --apply
HEALTH CHECK release-gates
```

## VERIFY

TypeScript/runtime shakedown for Node + TS execution path.

```bash
VERIFY
```

## REPAIR

Local repair and maintenance tasks.

```bash
REPAIR
REPAIR --check
REPAIR --install
REPAIR --pull
REPAIR --upgrade
UCODE REPAIR STATUS
```

## REBOOT

Restart/reload local runtime flows.

```bash
REBOOT
```

## DEV

Development mode controls.

```bash
DEV ACTIVATE
DEV DEACTIVATE
```

## Research And Workflow Hand-Off

The standard `ucode` shell now routes deterministic research and runbook intent
through the same core command surfaces instead of ad hoc helper flows.

```bash
UCODE TEMPLATE LIST
UCODE TEMPLATE READ missions MISSION-template
UCODE RESEARCH prompt shell://input local librarian design
UCODE ENRICH prompt shell://input workflow queue summary
UCODE GENERATE prompt shell://input release note draft
WORKFLOW IMPORT RESEARCH <workflow_id> <note_id> research
BINDER IMPORT-RESEARCH <binder_id> <note_id> research
```

Operator guidance remains the standard path for ambiguous natural-language
requests. Dev-only contributor fallback belongs to the `@dev` workspace lane rooted at `/dev`.

## Open-Box Runtime Notes

- `TIDY vault|knowledge|dev` and `CLEAN vault|knowledge|dev` use scoped Markdown/data cleanup rules and move removed files into `/.compost/`
- `DESTROY` and `RESTORE` matter in v1.5 because runtime code is separable from persisted user libraries and local data
- `/.compost` is managed elastically: old entries and overflow file versions are pruned as needed
- persisted timestamps stay in UTC/GMT; local timezone conversion happens at UI and command-render time only

## Runtime path updates in v1.3.16

Pattern and dataset top-level commands moved:

- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`

Examples:

```bash
DRAW PAT LIST
DRAW --py PAT CYCLE
DRAW --md MAP
DRAW --md --save diagrams/map-demo.md DEMO
RUN DATA LIST
RUN DATA VALIDATE locations
```

## Removed from Core (hard fail)

- `SHAKEDOWN`
- `INTEGRATION`
- `PROVIDER`
- `PATTERN`
- `DATASET`

Use Wizard surfaces for provider/integration/full-system checks.
