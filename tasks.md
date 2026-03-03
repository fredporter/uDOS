# tasks.md — uDOS Active Tasks

Last Updated: 2026-03-03
Version: v1.5 rebaseline
Status: Active

---

## Active Tasks

### Round 1 — Spec and Command Surface Shakedown

- [ ] Build the consolidated v1.5 shakedown checklist from `docs/specs/README.md`
  - Status: In Progress
  - Owner: Architecture Team
  - Notes: Each active spec must map to an implemented surface, an explicit deferred lane, or a monitor-only decision
  - Tracking: `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md`

- [ ] Finish docs/examples drift cleanup for shipped command surfaces
  - Status: In Progress
  - Owner: Documentation Team
  - Notes: Prioritize `WORKFLOW`, `UCODE PROFILE`, `UCODE OPERATOR`, profile install/verify, and `ucode`-first runtime guidance

### Round 2 — Core Workflow and Offline Assist Hardening

- [ ] Expand `WORKFLOW` template coverage and strengthen phase/variable validation
  - Status: Not Started
  - Owner: Core Team
  - Priority: High

- [ ] Promote stable offline assist runtime pieces from `docs/examples/udos_ulogic_pack/` into canonical core modules
  - Status: Not Started
  - Owner: Core Team
  - Priority: High
  - Notes: Preserve the stdlib-only core boundary and avoid parallel command systems

### Round 3 — Wizard Orchestration Integration

- [ ] Complete Wizard workflow orchestration on top of the core workflow state and artifact contract
  - Status: Not Started
  - Owner: Wizard Team
  - Priority: High
  - Notes: Queue policy, execution windows, API/MCP surfaces, and `/admin` views must build on `core/workflows/`

- [ ] Continue home-lane bridge closure within Wizard service ownership boundaries
  - Status: Not Started
  - Owner: Wizard Team
  - Priority: Medium

### Round 4 — Profile Acceptance and Packaging Closure

- [ ] Close creator profile blockers and collect acceptance evidence
  - Status: In Progress
  - Owner: Creator Team
  - Priority: High
  - Notes: Track against `docs/decisions/v1-5-creator-blocker-matrix.md`

- [ ] Finish gaming/home/core/dev profile install, verify, repair, and rollback evidence
  - Status: Not Started
  - Owner: Release Team
  - Priority: High

### Round 5 — TUI Hardening and Release Freeze

- [ ] Harden the standard `ucode` TUI path against the v1.5 terminal contract
  - Status: Not Started
  - Owner: Runtime Team
  - Priority: High

- [ ] Produce final release readiness summary and freeze evidence
  - Status: Not Started
  - Owner: Release Team
  - Priority: High

---

## Notes

- Historical v1.4.x stabilization work is complete and should remain in `completed.json` or `docs/devlog/`.
- Active sequencing lives in `docs/roadmap.md`.

---

End of File
