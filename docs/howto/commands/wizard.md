# Wizard Commands

Version: Core/Wizard v1.3.16
Updated: 2026-02-15

Wizard owns provider, integration, and full-system network-aware checks.

## Wizard Lifecycle

```bash
WIZARD START
WIZARD STOP
WIZARD STATUS
WIZARD REBUILD
```

## Provider Commands

```bash
WIZARD PROV LIST
WIZARD PROV STATUS
WIZARD PROV ENABLE <provider>
WIZARD PROV DISABLE <provider>
WIZARD PROV SETUP <provider>
WIZARD PROV GENSECRET
```

## Integration Commands

```bash
WIZARD INTEG status
WIZARD INTEG github
WIZARD INTEG mistral
WIZARD INTEG ollama
```

## Full Wizard-side Checks

```bash
WIZARD CHECK
```

## Contract Notes

- Core no longer accepts top-level `INTEGRATION` or `PROVIDER` commands.
- `PROVIDOR` is not accepted.
- No shims/aliases are provided for removed core commands.
