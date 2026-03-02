# OK Governance Policy

Updated: 2026-03-03
Status: active decision
Scope: branding terminology, architecture boundaries, AGENTS governance, and OK Agent behavior rules

## Decision

uDOS uses a single repo-wide OK governance policy for:
- approved terminology
- AGENTS.md authority
- core vs Wizard vs TypeScript runtime boundaries
- Vibe-CLI interaction rules
- ucode command-first behavior

This policy is active release truth for governance-facing documentation.

## Terminology Policy

uDOS does not use the prohibited legacy term in active user-facing or implementation guidance.

Approved terms:
- OK Assistant
- OK Agent
- OK Helper
- OK Model
- OK Provider
- Agent
- Helper
- Model
- Provider
- Assistant

Legacy terminology must be removed from active docs, comments, UI text, and governance files.

## AGENTS Authority

`AGENTS.md` is authoritative within its scope.

Rules:
- deeper scoped `AGENTS.md` files override higher-level ones
- `AGENTS.md` must describe current architecture only
- `AGENTS.md` must not become a roadmap, backlog, or historical journal

## Architecture Boundaries

Core:
- deterministic
- stdlib-only
- no external networking logic

Wizard:
- networked and web-capable
- owns provider, API, MCP, and external-service work

TypeScript runtime:
- lightweight execution partner
- must not duplicate core or Wizard ownership

## Interaction Model

Terminal-based interactive operator flow routes through:
- user
- Vibe-CLI
- OK Provider or OK Model
- ucode commands
- uDOS subsystems

ucode remains the command boundary for automation and operator actions.

## Agent Constraints

OK Agents working in uDOS must:
- read the nearest `AGENTS.md`
- respect boundary ownership
- prefer command surfaces over bypass behavior
- avoid generating deprecated or duplicate subsystems
- avoid reintroducing prohibited terminology

## Milestone Governance

Architecture guidance should reflect:
- tested working state
- current milestone truth
- current directory ownership

Completed milestones belong in:
- `DEVLOG.md`
- `completed.json`
- the roadmap and canonical docs set

Not in `AGENTS.md`:
- TODO items
- speculative ideas
- stale milestone notes

## Canonical Status

This file replaces the older oversized governance brief as the active decision-level policy.
