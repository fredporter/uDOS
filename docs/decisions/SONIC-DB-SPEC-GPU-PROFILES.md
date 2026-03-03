# Sonic DB GPU and Launch Profile Decision

Status: active Sonic contract  
Updated: 2026-03-03

## Purpose

This decision defines the Sonic DB role in hardware-aware launch planning for:
- machine capability records
- GPU profiles
- UI bundle references
- resolved launch profiles

## Decision

Sonic DB is the source of truth for hardware-aware launch behavior.
Launchers must materialize their runtime plan from Sonic DB records rather than inventing ad hoc flags or package choices.

## Required Record Families

Sonic DB must provide deterministic records for:
- `machines`
- `gpu_profiles`
- `ui_bundles`
- `ui_launch_profiles`

## Working Rules

### Machine records

Machine records define:
- stable identity
- platform role
- operating-system family and architecture
- relevant hardware capability facts

### GPU profiles

GPU profiles define:
- rendering mode
- driver and package expectations
- browser or runtime flags
- vendor-specific notes where required

### UI bundles

UI bundles define:
- the UI release identity
- build target
- compatibility expectations across supported shells

### Launch profiles

Launch profiles bind together:
- machine
- UI bundle
- GPU profile
- resolved packages
- final launch command plan

## v1.5 Relevance

For v1.5, this decision governs:
- Sonic DB schema consistency
- launch-profile determinism
- thin-UI launch planning
- hardware-profile parity across supported Sonic lanes

## Related Documents

- `docs/roadmap.md`
- `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md`
- `docs/decisions/uHOME-spec.md`
- `docs/specs/UHOME-v1.5.md`
