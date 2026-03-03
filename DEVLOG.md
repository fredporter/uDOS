# DEVLOG.md — uDOS Development Log

Last Updated: 2026-03-03
Version: v1.5 rebaseline
Status: Active

---

## Purpose

This log tracks root-level milestone changes and release-tracking updates for the active repository state.

---

## Entries

### 2026-03-03: Empire Wizard Refactor Closure

**Status:** Completed

**Changes:**
- completed the active Empire Wizard extension surface with route-backed document review, import job detail, grouped template inventory, connector review, and webhook tooling
- removed the remaining placeholder import/template language from the Empire dashboard and aligned it to the real managed route flow
- expanded Empire template discovery to include mappings, workflows, and general template files under one extension inventory
- closed the current release-tracking gap by updating the roadmap and task tracker to treat Empire as a completed active lane rather than a partial placeholder

**Implementation truth captured:**
- Empire dashboard imports now review real documents and import jobs through `/api/empire`
- Empire templates now expose mapping and workflow inventory from the official extension tree
- Wizard route tests cover template kinds and document detail access in addition to the existing import, sync, and webhook surfaces
- Empire follow-on work now belongs under broader Wizard/workflow release closure instead of module-specific refactor cleanup

**Next steps:**
1. keep Empire aligned with the shared workflow/template standards as Round 4 and Round 5 continue
2. close the remaining Wizard-wide orchestration and release evidence work outside the Empire module itself

### 2026-03-03: Python Runtime Contract Consolidation

**Status:** In Progress

**Changes:**
- standardized the active Python runtime direction on `uv` plus `/.venv`
- aligned launcher scripts and workspace settings away from legacy `venv/` references
- added a canonical Python runtime decision/spec pair and a root stdlib smoke lane
- kept pytest execution centralized in root `scripts/` while reinforcing `/dev/` as contributor governance only

**Implementation truth captured:**
- `UCODE REPAIR STATUS` now reports Python runtime contract health
- `bin/ucode` no longer auto-installs Wizard extras on normal runtime launch
- root tooling now treats `/.venv` as the canonical local Python environment path
- active docs are being rewritten to one `uv`/`/.venv` operating model

**Next steps:**
1. finish the remaining active-doc cleanup for stale `venv/` references
2. tighten the stdlib boundary audit allowlist as legacy core exceptions are retired

### 2026-03-03: v1.5 Roadmap Rebaseline Consolidation

**Status:** Completed

**Changes:**
- rewrote the canonical roadmap around active v1.5 implementation rounds
- converted decision coverage into round-based release sequencing
- updated root tracking files from the stale v1.4.6 stabilization snapshot to the current v1.5 rebaseline
- aligned high-traffic command/example docs with the shipped `WORKFLOW` and `UCODE` command surfaces
- kept historical milestone detail out of the active roadmap and root task tracker

**Implementation truth captured:**
- core `WORKFLOW` runtime is live and tested
- `UCODE PROFILE`, `UCODE OPERATOR`, `UCODE EXTENSION`, `UCODE PACKAGE`, and `UCODE REPAIR STATUS` are live surfaces
- Wizard follow-on work is now tracked as an integration round rather than as speculative pre-implementation planning
- offline assist remains an active v1.5 lane, with the example scaffold treated as the current promotion source rather than as completed core runtime

**Next steps:**
1. complete the Round 1 shakedown checklist across the active specs catalog
2. harden core workflow and offline assist implementation slices
3. continue Wizard orchestration only on top of the canonical core workflow contract

### 2026-02-24: AGENTS.md Governance Standardisation (v1.4.6)

**Status:** Completed

**Changes:**
- implemented the OK Agent governance policy
- created root AGENTS governance and subsystem-scoped AGENTS files
- scaffolded governance templates in `/dev`
- updated binder seed templates with AGENTS, DEVLOG, and task tracking files
- created the initial root governance tracker set

### 2026-02-23: Testing Phase Verification

**Status:** Completed

**Changes:**
- verified the core and Wizard test baselines for the then-active stabilization milestone
- recorded milestone readiness in the historical devlog stream

---

End of Log
