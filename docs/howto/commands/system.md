# System Commands

Version: Core v1.3.16
Updated: 2026-02-15

Core system commands are offline/local first.

## HEALTH

Offline stdlib shakedown for core readiness.

```bash
HEALTH
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
```

## REBOOT

Restart/reload local runtime flows.

```bash
REBOOT
```

## DEV

Development mode controls.

```bash
DEV MODE
DEV MODE ON
DEV MODE OFF
```

## Runtime path updates in v1.3.16

Pattern and dataset top-level commands moved:

- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`

Examples:

```bash
DRAW PAT LIST
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
