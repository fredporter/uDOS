# uDOS Command Reference

Version: v1.5 rebaseline
Updated: 2026-03-04

uDOS command ownership is split between deterministic core runtime surfaces and Wizard-managed integration surfaces.

## Standard Runtime

The standard user path is `ucode` first.

Primary surfaces:

- `UCODE PROFILE <LIST|SHOW|INSTALL|ENABLE|DISABLE|VERIFY>`
- `UCODE OPERATOR <STATUS|PLAN <prompt>|QUEUE>`
- `UCODE EXTENSION <LIST|VERIFY>`
- `UCODE PACKAGE <LIST|VERIFY>`
- `UCODE REPAIR STATUS`
- `WORKFLOW <LIST|NEW|RUN|STATUS|APPROVE|ESCALATE>`
- `SONIC <STATUS|SYNC|BOOTSTRAP|SUBMISSION|VERIFY|PLAN|RUN>`

See:

- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`
- `docs/examples/COMMAND-WORKFLOWS.md`
- `docs/examples/ucode_v1_5_release_pack/README.md`

## Core Ownership

Core owns deterministic local command surfaces, including:

- command/runtime validation and repair
- local workflow execution and vault artifacts
- local offline logic state/artifact/sandbox runtime primitives
- file-backed state and offline-first operator flows
- text-graphics, spatial, and local content tooling
- local Sonic seeded-catalog bootstrap and submission review state

## Wizard Ownership

Wizard owns:

- managed operations and `/admin`
- API and MCP integration surfaces
- network-aware provider and service integrations
- home, publishing, managed scheduling, and Sonic submission review APIs

See:

- `docs/howto/commands/wizard.md`
- `docs/howto/MANAGED-WIZARD-OPERATIONS.md`
- `docs/howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md`

## Dev Mode Boundary

`vibe` remains available for Dev Mode contributor workflows only. It is not the standard runtime path for v1.5 normal-user operation.

## Historical Command Notes

Older top-level command pages and migration stubs may still exist for reference, but active release guidance should follow the `ucode`-first runtime rule and the current `WORKFLOW` surface.

The certified v1.5 demo pack runs on the canonical shared runtime:

`UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python ...`
