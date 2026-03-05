# Minimum Spec for ucode and Dev Mode Runtime Pathways

Status: active contract
Updated: 2026-03-05

## Purpose

This document defines the minimum supported baseline for the `ucode` runtime surface across:

- online-capable operation
- offline-first operation
- local documentation and helper fallback
- optional Dev Mode contributor-tool activation

The standard runtime is `ucode`. The external Dev Mode contributor tool is optional and must remain extension-gated.

## Minimum Requirements

| Component | Requirement |
|---|---|
| OS | Linux/macOS/Windows 10+ (x86/ARM) |
| CPU | 2 cores |
| RAM | 4 GB |
| Storage | 5 GB free |
| Network | Optional |
| Dependencies | Python 3.12+, uDOS runtime, optional Wizard layer, optional Dev Mode extension lane |

## Runtime Pathways

### Standard runtime

- primary path: `ucode`
- optional online lane: Wizard-managed provider access where policy allows it
- features may include:
  - full command surface
  - managed provider access
  - system introspection
  - local plus network-aware documentation paths

### Offline runtime

- primary path: `ucode` commands only
- fallback path: local helper behavior and local documentation
- features must include:
  - offline docs
  - system capability reporting
  - local demos or helper scripts where provided

### Dev Mode contributor lane

- optional path: external contributor tool only when the `dev` profile is enabled
- requires the `@dev` workspace scaffold at `/dev`
- must not replace the default `ucode` runtime pathway

## Offline Fallback Requirements

Offline-capable installs should provide:

- local docs for key commands and workflows
- local capability reporting
- offline-friendly demos or helper flows for common tasks
- local metrics and bundle/signing state where those features are enabled

## Validation Contract

Minimum-spec validation must report:

- target requirements
- pass/fail summary
- per-resource checks for CPU, RAM, and storage

Structured output should expose a stable machine-readable minimum-spec section for operator and tooling use.

## Working Rule

Keep this spec focused on runtime baseline and pathway guarantees.
Detailed install procedures belong in `docs/INSTALLATION.md` and operator runbooks.
