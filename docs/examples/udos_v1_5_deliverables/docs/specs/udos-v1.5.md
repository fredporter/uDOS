# uDOS v1.5 Specification (Official Standard)

## Status
uDOS v1.5 is the new official standard.
It replaces Ollama with GPT4All as the local offline assist layer.
Wizard Network is the sole online routing and budget management layer.

## Architecture Overview
- Offline-first deterministic core (uLogic engine)
- GPT4All local assist (advisor only)
- Wizard Network escalation (free/paid/premium tiers)

## Core Principles
1. Deterministic execution authority
2. Offline-first cognition
3. Controlled online escalation
4. File-backed, auditable state

## Runtime Loop
1. Parse
2. Plan (ActionGraph)
3. Validate
4. Execute
5. Verify
6. Persist
7. Emit events

## Budget Management
Wizard Network enforces:
- Tier 0: Free models
- Tier 1: Economy paid models
- Tier 2: Premium models
- Deferred queue when limits exceeded

## Knowledge Libraries
- Local instruction pack (ucode, sonic db, docs)
- Global curated library
- User vault (Obsidian-linked, udos-frontmatter)

## Compliance Criteria
- GPT4All is sole local model
- Ollama deprecated
- Wizard Network exclusive API route
- Non-breaking input handler
- Workflow templates operational
