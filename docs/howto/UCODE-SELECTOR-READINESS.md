# uCODE Selector Readiness

This guide validates selector and input-method readiness for the ucode command-set.

## Standard

Canonical selector contract:

- `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md`

Execution model:

- Interactive flows through the v1.5 `ucode` TUI
- ucode commands must support non-interactive flags for automation

## Readiness Check

Run from repo root:

```bash
./dev/tooling/bin/check-ucode-selectors.sh
```

The checker validates:

- Interactive terminal detection (TTY)
- Shell selector stack: `fzf`, `fd`, `gum`, `bat`
- Python selector stack: `pick` (and optional richer prompt tooling where installed)
- Fallback policy expectations

## Required vs Optional

- Required for selector-ready status:
  - `fzf`
- Recommended:
  - `fd`
  - `gum`
  - `bat`
  - `pick`

## Input Method Contract

For each selector-enabled command:

1. Detect interactive mode (`isatty` / shell TTY).
2. If interactive and selector tooling exists, use selectors.
3. If selector tooling is unavailable, fallback to built-in menu/simple prompt.
4. Always support non-interactive flags (`--file`, `--files`, `--choice`, etc.).

## Acceptance Gate

A command-set is considered selector-ready when:

- `./dev/tooling/bin/check-ucode-selectors.sh` reports no `FAIL`
- At least one command path demonstrates:
  - file picker flow
  - menu selector flow
  - multi-select flow
  - non-interactive fallback flow

Current reference command path:

```bash
FILE SELECT --workspace @user/sandbox
FILE SELECT --files readme.md,docs/STATUS.md
```

Note:
- If Ghost Mode is active, workspace access can be restricted by role policy.
- Run `SETUP` to exit Ghost Mode before validating workspace selectors.
