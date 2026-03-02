# uDOS Python Environment Decision

Status: active implementation constraint  
Updated: 2026-03-03

## Purpose

This decision defines the runtime boundary between:
- core Python
- Wizard Python
- optional development tooling
- the lightweight TypeScript runtime lane

## Decision

uDOS uses this environment model:

- `core` Python stays stdlib-only and dependency-light
- `wizard` owns third-party Python dependencies and full virtual-environment behavior
- `dev` tooling rides on the Wizard environment by default
- the TypeScript runtime remains a lightweight companion capability, not a replacement for core Python

## Boundary Rules

### Core Python

Core Python must:
- remain stdlib-only
- avoid Wizard dependency imports
- keep deterministic local behavior available without a virtual environment

### Wizard Python

Wizard may:
- use third-party Python packages
- own network-aware behavior
- expose managed services and reusable libraries for higher-level tooling

### Dev tooling

Dev tooling should:
- use the Wizard environment by default
- avoid imposing runtime dependencies on core
- fail clearly when its required environment is not available

### TypeScript runtime

The TypeScript runtime may provide:
- orchestration helpers
- validators
- renderers
- manifest and contract utilities

It must remain optional for baseline core operation.

## Capability Model

uDOS operates in progressively richer layers:
- core-only
- core plus TypeScript runtime
- core plus Wizard
- core plus Wizard plus dev tooling

This keeps base operation durable while allowing richer managed surfaces where installed.

## v1.5 Relevance

For v1.5, this decision governs:
- Wizard venv ownership
- Dev Mode environment expectations
- core vs Wizard import boundaries
- TypeScript runtime role clarity

## Related Documents

- `docs/roadmap.md`
- `docs/decisions/UDOS-PYTHON-CORE-STDLIB-PROFILE.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md`
