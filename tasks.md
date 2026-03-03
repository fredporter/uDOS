# tasks.md — uDOS Active Tasks

Last Updated: 2026-03-04
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
  - Notes: Prioritize `WORKFLOW`, `UCODE PROFILE`, `UCODE OPERATOR`, health/housekeeping scopes, UTC/GMT runtime-time guidance including UI-only local timezone rendering plus dashboard/monitoring/settings/beacon and legacy management/export payloads, profile install/verify, and `ucode`-first runtime guidance. The active command reference and system guide now cover the v1.5 template/research/import flows, workspace transfer, and Sonic standalone release evidence; next pass should clear the remaining historical provider docs, secondary compatibility modules, and duplicated long-form specs.

- [ ] Complete the v1.5 central logging upgrade on the shared JSONL contract
  - Status: In Progress
  - Owner: Architecture Team
  - Priority: High
  - Notes: Keep one core-owned UTC-safe logging API, expose shared health/stats for Wizard/operator routes, and continue retiring ad hoc timestamp/log handling in legacy services

- [x] Standardize Python operation on one `.venv` + `uv` runtime contract
  - Status: Completed
  - Owner: Architecture Team
  - Priority: High
  - Notes: Launchers, workspace config, repair/runtime health, root pytest wrappers, and active docs now align to the canonical `UV_PROJECT_ENVIRONMENT=.venv` contract; contributor test policy remains under `/dev/`

### Round 2 — Offline Logic and Knowledge Foundations

- [ ] Promote stable offline logic runtime pieces from `docs/examples/udos_ulogic_pack/` into canonical core modules
  - Status: In Progress
  - Owner: Core Team
  - Priority: High
  - Notes: Promoted slices now include parser primitives, deliverables schema validation, the deterministic research/enrich/generate pipeline under `core/ulogic/`, direct workflow/binder ingestion, and `.compost`-aware artifact handling; next step is broader TUI/workflow-manager handoff aligned to `docs/decisions/v1-5-logic-assist-final-spec.md`

- [x] Standardize the smart logic input handler for offline-first intent parsing and workflow handoff
  - Status: Completed
  - Owner: Core Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`; `core/tui/ucode.py` now routes deterministic command, workflow, knowledge, and guidance frames through the real `UCODE`, `WORKFLOW`, `BINDER`, and operator surfaces before any Dev-only contributor fallback

- [ ] Define the global knowledge-bank and local user knowledge-tree contract
  - Status: In Progress
  - Owner: Core Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`; runtime paths, duplicate/edit flows, workflow/binder imports, `.compost` processing, and Markdown-safe housekeeping are now active, but broader seeded/global-bank evidence is still open

- [x] Standardize research, enrich, and generate flows on the vault-first Markdown pipeline
  - Status: Completed
  - Owner: Core Team
  - Priority: High
  - Notes: `core/ulogic/research_pipeline.py` is now wired through `UCODE RESEARCH|ENRICH|GENERATE`, persists canonical Markdown artifacts into the local knowledge tree, and supports `LIST`/`READ` follow-up operations from the same command surface

- [ ] Standardize Markdown capture/enhancement templates for user library gathering
  - Status: In Progress
  - Owner: Documentation Team
  - Priority: High
  - Notes: Template standard now lives in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`; use `docs/examples/udos_v1_5_deliverables/` as the shared framework for schemas, migration notes, and v1.5 deployment examples

### Round 3 — Template and Cross-Component Standardization

- [ ] Standardize cross-component runbook/template structure across core, Wizard, Sonic, `uHOME`, and offline logic packs
  - Status: In Progress
  - Owner: Architecture Team
  - Priority: High
  - Notes: Canonical target now lives in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`; research/enrich/generate artifacts must use the same Markdown-first structure

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

- [x] Complete Wizard workflow orchestration on top of the core workflow state and artifact contract
  - Status: Completed
  - Owner: Wizard Team
  - Priority: High
  - Notes: Wizard workflow create/list/detail/run/status/dashboard routes now use the core workflow scheduler/runtime summaries instead of parallel local-only workflow payloads

- [x] Standardize the workflow manager contract across core, Wizard, and offline logic surfaces
  - Status: Completed
  - Owner: Wizard Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/WORKFLOW-MANAGER-CONTRACT-v1.5.md`; Wizard manager/routes/dashboard summaries now present the same file-backed workflow contract used by `core/workflows/`

- [ ] Define Sonic Device DB as a seeded global catalog with user submissions and contributor approval flow
  - Status: In Progress
  - Owner: Sonic Team
  - Priority: High
  - Notes: Seed/user DB split, current-machine bootstrap, template refs, and open-box restore evidence are now in place; contributor approval and submission workflow still need full closure

- [ ] Continue home-lane bridge closure within Wizard service ownership boundaries
  - Status: Not Started
  - Owner: Wizard Team
  - Priority: Medium

### Round 5 — TUI, Logic Standardization, and Release Freeze

- [x] Complete the `ucode` TUI refactor and standardize the new element library
  - Status: Completed
  - Owner: Runtime Team
  - Priority: High
  - Notes: The standard shell now uses the canonical parser-to-command/workflow/knowledge handoff, the routed renderer exposes shared route/workflow/operator/knowledge panels, and the dedicated `tui/` Bubble Tea + Lip Gloss frontend now speaks the v1.5 JSONL contract through `core/tui/protocol_bridge.py`

- [x] Integrate the smart logic input handler into the standard `ucode` shell flow
  - Status: Completed
  - Owner: Runtime Team
  - Priority: High
  - Notes: `core/tui/ucode.py` now uses the promoted `core/ulogic` parser as the standard shell gate and emits deterministic handoff into command, workflow, knowledge, and guidance routes before Dev-only contributor fallback

- [x] Align workflow, offline logic, and operator-facing templates to the same TUI/output structure
  - Status: Completed
  - Owner: Runtime Team
  - Priority: High
  - Notes: Routed success output now standardizes workflow-state, operator guidance, research/template artifact, and command route presentation inside both the Python renderer and the Go frontend event model

- [ ] Close creator/gaming/home/core/dev profile install, verify, repair, and rollback evidence
  - Status: Not Started
  - Owner: Release Team
  - Priority: High

- [ ] Produce final release readiness summary and freeze evidence
  - Status: Not Started
  - Owner: Release Team
  - Priority: High
  - Notes: Must include proof that user Markdown/data libraries survive reinstall and restore cleanly under the split runtime/library model; Sonic/open-box restore evidence is now covered by focused tests and docs

---

## Notes

- Historical v1.4.x stabilization work is complete and should remain in `completed.json` or `docs/devlog/`.
- Active sequencing lives in `docs/roadmap.md`.

---

End of File
