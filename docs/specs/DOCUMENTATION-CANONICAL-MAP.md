# Documentation Canonical Map

Status: Active  
Updated: 2026-03-03

## Purpose

This document records the current documentation assessment for:
- `docs/decisions`
- `docs/specs`
- `docs/howto`
- `docs/examples`

It exists to reduce duplication and to clarify which document type should hold which kind of information.

## Canonical Rules

### Decisions

`docs/decisions/` should contain:
- architectural choices
- boundary ownership
- chosen operating models
- scope split decisions

It should not be the long-term home for:
- detailed interfaces
- step-by-step usage
- broad tutorial material

### Specs

`docs/specs/` should contain:
- contracts
- schemas
- runtime interfaces
- state models
- canonical file layouts
- command behavior rules

### How-to

`docs/howto/` should contain:
- operational usage
- setup steps
- command walkthroughs
- recovery and maintenance procedures

### Examples

`docs/examples/` should contain:
- sample inputs
- sample outputs
- example scripts/templates
- reference packs such as `udos_creative_pack`

## Current Canonical Workflow Docs

### Decision

- `docs/decisions/v1-5-workflow.md`

### Spec

- `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`

### How-to

- `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`

### Roadmap / progress

- `docs/roadmap.md`

### Archive redirect

- `docs/v1-4-workflow-PLAN.md`

## Current Assessment

### Accurate and relevant

These doc groups remain broadly useful and should stay active:
- command reference and ucode operator docs
- MCP activation/integration material
- binder and workspace guides
- many platform/runtime specs
- the creative pack example set

### Current duplication patterns

The main duplication patterns are:
- decisions that also behave like specs
- plans/briefs that still read like active canonical docs
- repeated workflow scope spread across roadmap, decisions, and older plan files
- verbose historical execution notes mixed with current operating guidance

### Current verbose/problematic areas

The most likely cleanup targets are:
- older brief-style decision docs
- large execution-plan docs living under `docs/decisions/`
- overlapping workflow/project-management concept docs
- older spec files whose titles or body read more like planning notes than stable contracts

## Second-Pass Audit (2026-03-03)

This second pass focused on:
- duplicate workflow planning material
- oversized active docs that may be too verbose for day-to-day use
- dead or superseded pages that should become redirect notes or future `.compost` candidates

### Completed in this pass

- `docs/decisions/v1-5-wizard-PLAN.md`
  - converted to archive redirect
- `docs/specs/workflow-management.md`
  - converted to archive redirect
- workflow architecture moved into explicit decision/spec/howto/roadmap documents
- active workflow docs were cross-linked from docs indexes
- focused terminology cleanup applied to the active workflow/runtime docs touched during this cleanup
- `docs/specs/typescript-markdown-runtime.md`
  - split into a short active contract plus archived detailed brief
- `docs/specs/PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md`
  - split into a short active packaging contract plus archived milestone brief
- `docs/MANAGED-OPERATIONS.md`
  - merged into `docs/howto/MANAGED-WIZARD-OPERATIONS.md` and reduced to redirect stub
- `docs/decisions/OK-update-v1-4-6.md`
  - split into a short active governance decision and redirect stub
- `docs/specs/Spatial-Grid-COMPLETE.md`
  - split into a short active spatial contract and redirect stub

### High-confidence redirect/archive candidates already handled

- old workflow plans
- duplicate workflow-management concept docs

### High-confidence next compost candidates

These look oversized, historical, or structurally mixed enough that they likely belong in `.compost` after a reference check:

1. `docs/decisions/formatting-spec-v1-4.md`
   - now converted into a redirect stub
   - active rules live in `docs/specs/FORMATTING-SPEC-v1.4.md`
2. `docs/howto/TOOLS-REFERENCE.md`
   - split into a short tools index plus focused category reference pages

### Verbose but still probably active

These likely need trimming or splitting rather than immediate archive:

1. `docs/howto/TOOLS-REFERENCE.md`
   - now shortened; keep category pages aligned with command surface changes
2. `docs/howto/WIZARD-PLUGIN-SYSTEM.md`
   - now reduced to a front-door guide with quickstart/reference companions
3. `docs/howto/OFFLINE-ASSITANT-SETUP.md`
   - now reduced to a short front-door guide with quickstart and reference companions
4. `docs/howto/SVG-GRAPHICS-GENERATION.md`
   - now reduced to a short front-door guide with quickstart and reference companions

### Low-risk cleanup opportunities

These are good candidates for the next minor pass:

- fix legacy filenames that still contain prohibited terminology
- trim examples or repeated narrative sections from large how-to docs
- move historical execution sections out of active specs into `.compost`
- shorten docs whose title already includes a versioned milestone and are no longer current release truth

## Recommended Cleanup Direction

### Keep as decisions

These should remain decision-oriented:
- `v1-5-workflow.md`
- `v1-5-rebaseline.md`
- `WIZARD-SERVICE-SPLIT-MAP.md`
- `VAULT-MEMORY-CONTRACT.md`

### Promote or mirror into specs/how-to

These need spec/how-to companions when they are active implementation surfaces:
- workflow scheduler
- wizard control plane and managed operations
- MCP activation and operator usage
- workflow/task/project runtime surfaces

### Archive or redirect

These should become redirect/archive notes when superseded:
- old workflow plans
- brief-only implementation plans that no longer represent the active source of truth

## Next Cleanup Candidates

Recommended next review targets:

1. `docs/specs/TASK-JSON-FORMAT-OK-MODEL-INGESTION.md`
   - legacy filename removed
   - keep body terminology aligned with OK Model and import mapping language
2. older brief-style specs and decision files with implementation-plan tone instead of stable contract tone

### March 3, 2026 consolidation completed

- `docs/decisions/v1-5-wizard-PLAN.md` converted to archive redirect
- `docs/specs/workflow-management.md` converted to archive redirect
- Wizard plan milestones merged into `docs/roadmap.md`
- root and top-level docs relics moved into dated `.compost` folders
- stale devlog rollups, completion summaries, and the stale v1.5 GA completion note moved into `docs/.compost/historic/2026-03-03-devlog-rollups-and-relics/`
- interim devlog milestone plans, progress logs, and narrow completion notes moved into `docs/.compost/historic/2026-03-03-devlog-interim-plans-and-progress/`
- unreferenced active devlogs were bulk-moved into `docs/.compost/historic/2026-03-03-devlog-unreferenced-bulk/`
- oversized TypeScript runtime and packaging briefs were split into shorter active specs with archived detailed copies
- managed operations guidance was merged into the canonical how-to set
- the oversized OK governance brief and spatial-grid brief were reduced to redirect stubs with new active canonical docs
- `docs/howto/TOOLS-REFERENCE.md` was split into a short overview plus focused category reference pages
- `docs/howto/OFFLINE-ASSITANT-SETUP.md` was reduced into a front-door page plus quickstart/reference companions
- `docs/howto/SVG-GRAPHICS-GENERATION.md` was reduced into a front-door page plus quickstart/reference companions
- `docs/howto/WIZARD-PLUGIN-SYSTEM.md` was reduced into a front-door page plus quickstart/reference companions
- `docs/ARCHITECTURE.md` was reduced into an overview plus detailed integration reference
- `docs/howto/BINDER-USAGE-GUIDE.md` was reduced into a front-door page plus binder quickstart
- `docs/decisions/formatting-spec-v1-4.md` was corrected into a true redirect stub
- `docs/README.md` and `docs/INDEX.md` were reduced to a front door plus short navigation index
- root `README.md` had duplicated documentation/install narrative trimmed back to canonical entrypoints
- `docs/examples/example-sqlite.db.md` was reduced into a front-door example plus focused companion examples
- `docs/specs/UCODE-COMMAND-DISPATCH-v1.4.4.md` was reduced to a redirect stub with a shorter active dispatch contract
- `docs/decisions/uDOS-v1-3.md` was reduced to a short historical architecture snapshot
- `docs/specs/03-contributions-contract.md` was normalized into a short historical contribution contract
- `docs/decisions/uHOME-spec.md` was reduced to a short active home-profile decision
- `docs/decisions/UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md` was reduced to a short topology decision
- `docs/decisions/data-layer-architecture.md` was reduced to a short active data-layer decision
- `docs/decisions/UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md` was reduced to a short active environment decision
- `docs/specs/OK-MODES-v1.3.md` had completion-endpoint terminology normalized
- `docs/specs/ERROR-HANDLING-v1.4.4.md` had provider terminology normalized
- `docs/specs/INTEGRATION-READINESS.md` was reduced to a short active readiness summary
- `docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md` was rewritten around the `ucode`-first runtime path
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md` was reduced to a short Sonic launch-profile decision
- `docs/decisions/UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md` was reduced to a short Alpine thin-GUI runtime decision
- `docs/decisions/v1-5-ucode-tui-spec.md` was rewritten as the active v1.5 `ucode` TUI source of truth
- `docs/decisions/udos-protocol-v1.md`, `docs/decisions/udos-reference-implementation.md`, and `docs/decisions/udos-teletext-theme.md` were normalized as supporting TUI artifacts
- `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md` was rewritten to align selectors with the v1.5 `ucode` TUI
- `docs/decisions/MCP-API.md` was rewritten around Wizard MCP ownership and Dev Mode bridge behavior
- the active-tree runtime/operator docs cleanup pass is complete; the remaining active-tree work is limited to low-priority historical terminology cleanup, release-evidence updates, and keeping new docs aligned to the `ucode`-first runtime rule

### Recommended next actions

1. Continue terminology cleanup in older but still indexed docs.
2. Rename any remaining legacy filenames that still include prohibited terminology.
3. Review long active decision/spec pages that still read like milestone briefs rather than stable contracts.
4. Prefer redirect stubs in active locations once a document has been moved to `.compost`.

## Working Rule

Before adding a new doc:
- put architecture choices in `docs/decisions/`
- put stable contracts in `docs/specs/`
- put operational usage in `docs/howto/`
- put sample material in `docs/examples/`

If a document mixes all four, split it.
