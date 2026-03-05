# uDOS Architecture

Updated: 2026-03-03
Status: active overview

## Purpose

This page is the short architecture overview for the repository.

## Core Model

uDOS is organized around clear boundary ownership:
- `core` for deterministic local behavior
- `wizard` for networked and web-facing behavior
- lightweight partner runtimes where explicitly allowed

## Integration Direction

The repo follows a non-fork integration model:
- keep local addon behavior in uDOS-owned surfaces
- avoid patching upstream runtime internals as the default strategy
- use explicit configuration and command boundaries for integration

## Key Boundaries

- command surfaces remain explicit
- Wizard owns provider, API, and managed orchestration work
- core remains deterministic and offline-capable
- docs, commands, and workflows should stay human-readable where possible

## Start Here

- [Architecture Integration Reference](ARCHITECTURE-INTEGRATION-REFERENCE.md)
- [Workflow Decision](decisions/v1-5-workflow.md)
- [Workflow Scheduler Spec](specs/WORKFLOW-SCHEDULER-v1.5.md)
- [OK Governance Policy](decisions/OK-GOVERNANCE-POLICY.md)
