# uCODE Command Reference

Version: Core v1.3.16
Updated: 2026-02-15

This reference documents the active core command surface after the v1.3.16 core/wizard split.

## Core Commands (v1.3.16)

### Navigation

- `MAP`
- `PANEL`
- `FIND`
- `TELL`
- `GOTO`

### State and Runtime

- `BAG`
- `GRAB`
- `SPAWN`
- `SAVE`
- `LOAD`
- `STORY`
- `RUN`
- `DRAW`

### System

- `HEALTH` (offline stdlib shakedown)
- `VERIFY` (TS runtime shakedown)
- `REPAIR`
- `REBOOT`
- `DEV`
- `UID`
- `CONFIG`
- `WIZARD`
- `LOGS`
- `SETUP`

### Workspace and Files

- `FILE`
- `NEW`
- `EDIT`
- `BINDER`
- `USER`
- `NPC`
- `TALK`
- `REPLY`
- `SONIC`
- `TAG`

## Core Health Commands

### `HEALTH`

Runs offline/local checks only.

```bash
HEALTH
```

Checks include local config, parser/dispatcher readiness, local paths, and offline policy signals.

### `VERIFY`

Runs TypeScript/runtime checks.

```bash
VERIFY
```

Checks include Node availability, TS runtime artifacts, and script parse/execute smoke tests.

## TS-backed command paths

### Pattern flow

Top-level `PATTERN` is removed. Use `DRAW PAT ...`.

```bash
DRAW PAT LIST
DRAW PAT CYCLE
DRAW PAT TEXT "hello"
DRAW PAT <pattern-name>
```

### Dataset flow

Top-level `DATASET` is removed. Use `RUN DATA ...`.

```bash
RUN DATA LIST
RUN DATA VALIDATE <id>
RUN DATA BUILD <id> [output_id]
RUN DATA REGEN <id> [output_id]
```

## Wizard-owned flows

Provider/integration/full-system checks are Wizard-owned.

Use:

```bash
WIZARD PROV LIST
WIZARD PROV STATUS
WIZARD INTEG status
WIZARD CHECK
```

## Removed Core Commands (No Shims)

The following top-level commands are removed from core and hard-fail in v1.3.16:

- `SHAKEDOWN`
- `PATTERN`
- `DATASET`
- `INTEGRATION`
- `PROVIDER`
- `PROVIDOR` (typo; not accepted)

## Migration Table

- `SHAKEDOWN` -> `HEALTH` or `VERIFY` (core), `WIZARD CHECK` (full Wizard-side checks)
- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`
- `INTEGRATION ...` -> `WIZARD INTEG ...`
- `PROVIDER ...` -> `WIZARD PROV ...`

## Examples

```bash
# Core checks
HEALTH
VERIFY

# Pattern and dataset flows
DRAW PAT LIST
RUN DATA LIST
RUN DATA VALIDATE locations

# Wizard-owned checks
WIZARD START
WIZARD CHECK
WIZARD INTEG status
WIZARD PROV STATUS
```

## Notes

- Command names are canonical uppercase in docs.
- Removed commands are not aliased or remapped.
- Use `HELP` in TUI for live command help.
