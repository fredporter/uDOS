# Knowledge Bank and Runbook Standard v1.5

Status: Active
Last updated: 2026-03-03

## Purpose

This spec defines the librarian-facing content model for uDOS v1.5.

It standardizes:
- the global knowledge-bank
- the user knowledge-tree
- the Sonic Device DB seeded catalog rule
- the shared Markdown template and runbook structure used across uDOS

The goal is one open-box Markdown-first operating model that users can browse,
duplicate, and edit locally without mutating distributed source material.

## Product Rule

uDOS v1.5 is an offline-first logic-assisted knowledge gatherer and local
librarian.

That means:
- shipped global reference content is seed data
- users can read and duplicate seed content
- users edit local copies and user-owned knowledge trees
- only contributors in the Dev extension lane edit distributable seed sources

## Content Layers

### 1. Global knowledge-bank

The global knowledge-bank is:
- distributed with uDOS
- read-only for normal users
- Markdown-first and browsable
- intended as seed/reference material
- contributor-editable only through the Dev extension lane

Typical content types:
- how-to references
- workflow templates
- mission templates
- capture forms
- rulesets
- catalog records

### 2. User knowledge-tree

The user knowledge-tree is:
- local
- writable
- user-owned
- used for topic gathering, enrichment, classification, and runbook execution

Typical content types:
- duplicated seed templates
- user notes and summaries
- local research topics
- user-specific procedures
- enriched copies of reference material

### 3. Sonic Device DB seeded catalog

The Sonic Device DB follows the same seed/local rule:
- the distributed catalog is read-only for normal users
- user submissions are stored locally first
- contributor review and approval controls what becomes part of the distributed seed
- only contributors in the Dev extension lane may edit approved source catalog records

## Open-Box Rule

All shipped seed content must be open-box:
- visible on disk
- Markdown or plain data where practical
- browsable from the TUI and file system
- duplicable into local writable trees
- reusable as templates for normal user operations

The release must not depend on hidden packaged-only templates for standard
operations.

## Canonical Markdown Template Shape

v1.5 standardizes one recognizable Markdown structure for operational content.

Supported document families include:
- runbooks
- workflows
- missions
- capture templates
- knowledge topic templates
- device submission templates

The common shape is:

```markdown
# <TYPE>: <id>

## Purpose
<text>

## Inputs
- Key: Value

## Steps
1. <step>

## Outputs
- <artifact or destination>

## Evidence
- <what proves completion>

## Notes
- <operator-visible guidance>
```

The exact section set may expand by content family, but all active components
must stay visibly compatible with this structure.

## Cross-Component Compatibility Rule

Core, Wizard, Sonic, `uHOME`, and offline logic packs must use one compatible
template/runbook shape for active v1.5 work.

Compatibility means:
- recognizable headings
- consistent metadata expectations
- consistent evidence sections
- consistent operator-readable outcomes
- no component-specific hidden template dialects for normal operations

## Capture and Enhancement Process

The standard user-facing capture flow is:

```text
browse seed content
-> duplicate template into local knowledge-tree
-> gather or enrich Markdown content
-> run workflow/runbook where needed
-> record evidence and local outcomes
```

This process must work for:
- personal topic gathering
- local library enhancement
- device submission preparation
- repeatable operational runbooks

## Integration Anchors

Current repository anchors for this spec:
- `core/services/seed_template_service.py`
- `docs/examples/udos_ulogic_pack/core/ulogic/library/workflows/WORKFLOW-template.md`
- `docs/examples/udos_ulogic_pack/core/ulogic/library/missions/MISSION-template.md`
- `docs/examples/udos_ulogic_pack/core/ulogic/library/captures/CAPTURE-template.md`
- `docs/examples/udos_ulogic_pack/core/ulogic/library/submissions/DEVICE-SUBMISSION-template.md`
- `docs/examples/udos_ulogic_pack/core/ulogic/library/intents/patterns.md`
- `docs/examples/udos_creative_pack/templates/`
- `core/workflows/`
- `docs/decisions/v1-5-offline-assist.md`

## Required v1.5 Standardization Steps

Before freeze, v1.5 must:
- identify the shipped global knowledge-bank seed paths
- identify the writable user knowledge-tree paths
- provide browse and duplicate flows for seed templates
- standardize capture/enhancement templates for user topics
- standardize Sonic submission and contributor approval templates
- align workflow/runbook Markdown structure across active components

## Related Documents

- `docs/decisions/v1-5-offline-assist.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`
- `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`
- `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`
