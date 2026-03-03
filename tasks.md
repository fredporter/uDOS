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

### Round 2 — Offline Logic and Knowledge Foundations

- [ ] Promote stable offline logic runtime pieces from `docs/examples/udos_ulogic_pack/` into canonical core modules
  - Status: In Progress
  - Owner: Core Team
  - Priority: High
  - Notes: First promoted slice now lives in `core/ulogic/` with deterministic contracts and parser primitives; next step is runtime handoff integration

- [ ] Standardize the smart logic input handler for offline-first intent parsing and workflow handoff
  - Status: In Progress
  - Owner: Core Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`; next step is runtime promotion and event standardization

- [ ] Define the global knowledge-bank and local user knowledge-tree contract
  - Status: In Progress
  - Owner: Core Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`; runtime paths and duplicate/edit flows still need implementation evidence

- [ ] Standardize Markdown capture/enhancement templates for user library gathering
  - Status: In Progress
  - Owner: Documentation Team
  - Priority: High
  - Notes: Template standard now lives in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`; next step is cross-component template alignment

### Round 3 — Template and Cross-Component Standardization

- [ ] Standardize cross-component runbook/template structure across core, Wizard, Sonic, `uHOME`, and offline logic packs
  - Status: In Progress
  - Owner: Architecture Team
  - Priority: High
  - Notes: Canonical target now lives in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`

- [ ] Ensure seeded global templates are open-box, browsable, duplicable, and locally editable
  - Status: Not Started
  - Owner: Documentation Team
  - Priority: Medium

### Round 4 — Wizard, Sonic, and Seeded Catalog Integration

- [x] Complete the Empire Wizard extension rebuild on shared managed route patterns
  - Status: Completed
  - Owner: Wizard Team
  - Priority: Medium
  - Notes: Dashboard, import review, document detail, grouped template inventory, connector jobs, and webhook tooling now run through the main Empire module surface instead of placeholder lanes or parallel scripts

- [ ] Complete Wizard workflow orchestration on top of the core workflow state and artifact contract
  - Status: Not Started
  - Owner: Wizard Team
  - Priority: High
  - Notes: Queue policy, execution windows, API/MCP surfaces, and `/admin` views must build on `core/workflows/`

- [ ] Standardize the workflow manager contract across core, Wizard, and offline logic surfaces
  - Status: In Progress
  - Owner: Wizard Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`; next step is runtime/control-plane alignment

- [ ] Define Sonic Device DB as a seeded global catalog with user submissions and contributor approval flow
  - Status: Not Started
  - Owner: Sonic Team
  - Priority: High
  - Notes: Keep the distributed seed read-only for users and contributor-editable only through the Dev extension lane

- [ ] Continue home-lane bridge closure within Wizard service ownership boundaries
  - Status: Not Started
  - Owner: Wizard Team
  - Priority: Medium

### Round 5 — TUI, Logic Standardization, and Release Freeze

- [ ] Complete the `ucode` TUI refactor and standardize the new element library
  - Status: Not Started
  - Owner: Runtime Team
  - Priority: High

- [ ] Integrate the smart logic input handler into the standard `ucode` shell flow
  - Status: Not Started
  - Owner: Runtime Team
  - Priority: High

- [ ] Align workflow, offline logic, and operator-facing templates to the same TUI/output structure
  - Status: Not Started
  - Owner: Runtime Team
  - Priority: High

- [ ] Close creator/gaming/home/core/dev profile install, verify, repair, and rollback evidence
  - Status: Not Started
  - Owner: Release Team
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
