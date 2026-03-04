# Documentation Archive

Updated: 2026-03-04
Context: superseded root docs, retired milestone notes, and historic architecture material

## Archive Structure

### `/historic/` - Completed Phase/Milestone Docs
Historic phase-based planning docs, consolidation summaries, and superseded architecture decisions.

**Files**:
- `PHASE-A-QUICKREF.md`, `PHASE-A-READY.md`, `PHASE-C-IMPLEMENTATION.md` - Phase-based planning (superseded)
- `AUDIT-RESOLUTION.md` - Point-in-time audit (2026-02 complete)
- `CONSOLIDATION-SUMMARY.md` - Historic consolidation notes
- `UPSTREAM-MERGE.md` - Merge notes (complete)
- `DOCS-SPINE-v1.3.md` - Duplicate (kept in root)
- `HYBRID-ARCHITECTURE.md` - Superseded by main ARCHITECTURE.md
- `SUBMODULE-STRATEGY.md` - Strategy finalized
- `DEV-Mode-Spec.md` - Superseded by `dev/docs/DEV-MODE-POLICY.md`
- `OK-ROUTE-PROTOTYPE-PLAN.md`, `PROMPT-WORKFLOW.md` - Prototypes complete

### `/tui-legacy-2026-02/` - Standalone TUI Documentation
Documentation for the standalone ucli/ucode interactive TUI, archived due to migration to Vibe-only architecture.

**Files**:
- `TUI-SMART-FIELDS-GUIDE.md` - Form field system for standalone ucli TUI
- `VIBE-UCLI-INTEGRATION-GUIDE.md` - Phase 1-2 integration guide (obsolete with Vibe-only)

**Note**: Command infrastructure preserved; only interactive UI layer removed. See `/docs/decisions/TUI-MIGRATION-PLAN.md` for details.

### `/releases/v1.3.x/` - v1.3.x Release Milestones
Version-specific specs, checklists, and release notes for v1.3.17 through v1.3.26.

**Files** (15 total):
- `v1.3.17-SONIC-SCREWDRIVER-AND-STICK-PLAN.md`
- `v1.3.17-SONIC-WIZARD-GUI-ENTRYPOINTS.md`
- `v1.3.20-CHUNKING-CONTRACT.md`
- `v1.3.21-ADAPTER-READINESS-CHECKLIST.md`
- `v1.3.21-CAPABILITY-BENCHMARK-MISSIONS.md`
- `v1.3.21-DUAL-LENS-COMPAT-MATRIX.md`
- `v1.3.21-WORLD-ADAPTER-CONTRACT.md`
- `v1.3.23-ADAPTER-LIFECYCLE-AND-REPLAY-CONTRACT.md`
- `v1.3.23-CONTRACT-DRIFT-CI-GUARDRAILS.md`
- `v1.3.23-MISSION-OBJECTIVE-REGISTRY-CONTRACT.md`
- `v1.3.23-STABILIZATION-ROUND-A-CHECKLIST.md`
- `v1.3.24-ROUND-B-PARITY-AND-MIGRATION-CHECKLIST.md`
- `v1.3.25-CONTRACT-FREEZE-AND-RELEASE-CHECKLIST.md`
- `v1.3.26-CORE-STABILIZATION-RELEASE-NOTES.md`
- `v1.3.26-FINAL-GATE-READINESS-CHECKLIST.md`
- `P0-PHASE1-DISCOVERY-SUMMARY.md`

**Status**: Milestones complete, contracts remain valid but version-frozen.

### `/releases/v1.4.0/` - v1.4.0 Milestone
v1.4.0 kickoff and execution docs (milestone complete).

**Files**:
- `v1.4.0-DOCKER-AUTOMATION-CAPABILITY-SPEC.md`
- `v1.4.0-EXECUTION-ORDER.md`
- `v1.4.0-KICKOFF-CHECKLIST.md`
- `v1.4.0-READINESS-MEMO.md`

**Status**: v1.4.0 complete, now at v1.4.4+

---

## v1.5 Rule

- `docs/` contains active runtime/operator documentation.
- `dev/docs/` contains active contributor-facing `@dev` documentation.
- `wiki/` contains short orientation pages only.
- Superseded but still useful history belongs here in `docs/.compost/`.

## How to Access

Archived docs remain git-tracked and accessible:
```bash
ls docs/.compost/
git log -- docs/.compost/
```

## When to Archive

Documents move to archive when:
1. **Obsolete**: Feature/approach no longer used (e.g., standalone TUI)
2. **Superseded**: Newer version exists (e.g., v1.3.x → v1.4.x)
3. **Complete**: One-time task/milestone finished (e.g., phase completion)
4. **Duplicate**: Content consolidated elsewhere

## Active Documentation

Current docs remain in:
- `/docs/` - active operator/runtime guides and contracts
- `/dev/docs/` - active contributor `@dev` docs
- `/wiki/` - short repo orientation pages

See `/docs/README.md` for the active docs index.
