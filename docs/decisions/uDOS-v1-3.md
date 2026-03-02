# uDOS v1.3 Architecture Snapshot

Status: historical snapshot  
Updated: 2026-03-03

This document is retained for architecture context only. It is not current release truth for v1.5.

## What Persisted From v1.3

- Vault-first, open-box content storage
- Offline-first operation with policy-gated provider usage
- Core for deterministic local transforms
- Wizard for networking, scheduling, and governance
- Contribution bundles instead of direct curated-note mutation
- Static publishing for reading surfaces and richer app UI only where needed

## Snapshot Summary

The v1.3 architecture established uDOS as:
- a markdown-first runtime beside an Obsidian-compatible vault
- a split system with deterministic local behavior in `core`
- a managed, networked control layer in `wizard`
- a contribution-based editing model where OK Assistants and OK Agents propose changes rather than silently mutating curated content

It also established the early direction for:
- scheduled missions and reporting
- provider routing policy
- theme-based publishing
- local portal and public publishing as separate concerns

## What Changed After v1.3

Later releases refined or replaced parts of this snapshot:
- workflow orchestration now lives under the v1.5 workflow decision and scheduler spec
- governance and terminology now live under the OK governance policy
- newer core vs Wizard boundary rules are defined by current architecture and service-split docs

Use these instead:
- `docs/decisions/v1-5-workflow.md`
- `docs/decisions/OK-GOVERNANCE-POLICY.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`

## Working Rule

Keep this file as a short historical reference only.
Do not implement new work from this snapshot without first reconciling it against the active v1.5 roadmap and current decision set.
