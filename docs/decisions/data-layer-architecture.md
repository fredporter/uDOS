# ADR-0004: Data Layer Architecture

Status: active decision  
Updated: 2026-03-03

## Purpose

This decision defines how uDOS separates:
- tracked framework data
- tracked reference content
- local runtime and user state

The goal is a readable, open-box data layout with clear boundaries between distributed assets and local state.

## Decision

uDOS uses a three-layer data model:

1. `core/framework/`
   - schemas
   - templates
   - seed data
   - tracked and distributed with the repo

2. `knowledge/`
   - static reference content
   - tracked markdown and supporting indexes
   - not a dumping ground for runtime state

3. `memory/`
   - local runtime state
   - user-customized data
   - logs, caches, local databases, and mutable project state

## Key Rules

### Framework layer

Use `core/framework/` for:
- schemas
- seed packs
- scaffold templates
- canonical starter assets

### Knowledge layer

Use `knowledge/` for:
- static reference material
- guides
- place or topic content intended to remain readable and distributable

Do not use `knowledge/` for:
- mutable runtime state
- operational logs
- per-user runtime scripts

### Local runtime layer

Use `memory/` for:
- logs
- local databases
- imported or generated runtime data
- user-local project state
- mutable bank content

## Format Strategy

- start with plain files where they are small and readable
- use JSON for portable structured datasets
- migrate to SQLite when size, record count, or query complexity makes JSON impractical

The exact threshold is implementation-specific, but the governing rule is:
- prefer simple readable formats first
- move to SQLite when operational needs clearly justify it

## v1.5 Relevance

For v1.5, this decision governs:
- data placement cleanup
- SQL/JSON/Python parity decisions
- seed and scaffold placement
- separation of tracked assets from local runtime state

## Related Documents

- `docs/roadmap.md`
- `docs/decisions/VAULT-MEMORY-CONTRACT.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/specs/RUNTIME-INTERFACE-SPEC.md`
