# ucode Selector Integration Brief

Status: active supporting brief  
Updated: 2026-03-03

## Purpose

This brief defines how interactive selectors should behave in the v1.5 `ucode` TUI.

It supports the `ucode`-first terminal experience and should not assume that `vibe` is the standard user-facing runtime.

## Design Target

Selectors must fit the standard v1.5 `ucode` TUI direction:
- keyboard-driven
- fixed-width friendly
- scriptable when needed
- safe for standard terminal use

## Core Requirements

- compatibility across Linux, macOS, and Windows
- alignment with shared `ucode` TUI primitives
- non-interactive fallbacks for scripted usage
- predictable key handling and narrow-terminal behavior

## Selector Rules

Selectors should provide:
- single-select flows
- multi-select flows
- file or path picking where required
- explicit non-interactive flags for automation paths

They must preserve:
- `Enter` to accept
- `Esc` to cancel or back out
- search/filter where appropriate
- stable output formatting under fixed-width rendering

## Recommended Tooling

For shell-backed selector flows, prefer lightweight tools such as:
- `fzf`
- `fd`
- `gum`

For Python-backed selector flows, prefer supported lightweight options and keep dependencies explicit.

## Working Rule

Selector UX should match the v1.5 `ucode` TUI decision, not legacy `vibe`-first terminal conventions.

Related documents:
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/specs/RUNTIME-INTERFACE-SPEC.md`
- `docs/specs/UCODE-DISPATCH-CONTRACT.md`
