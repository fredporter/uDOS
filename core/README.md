# core (TS deterministic engine)

This is the “compiler layer”:
- md → html (AST-based)
- json/yaml/csv parsing
- sqlite state
- diff/patch bundles
- theme wrapping

Implement as a library + CLI:
- `udos-core render <input> --theme prose`
- `udos-core diff <old> <new> --out _contributions/...`
- `udos-core sqlite migrate`

## Documentation Flow

- Repo docs index: `docs/README.md`
- Core command surface: `docs/howto/UCODE-COMMAND-REFERENCE.md`
- Core command handlers: `core/commands/`
- Core tests: `core/tests/`
