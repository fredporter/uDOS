# tasks.md — uDOS Active Tasks

Last Updated: 2026-03-04
Version: v1.5 rebaseline
Status: Active

---

## Active Tasks

### Round 1 — Spec and Command Surface Shakedown

- [x] Build the consolidated v1.5 shakedown checklist from `docs/specs/README.md`
  - Status: Completed
  - Owner: Architecture Team
  - Notes: Closed with `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md` as the canonical spec-to-surface audit, linked directly from `docs/specs/README.md` and used as the release-facing shakedown source
  - Tracking: `docs/specs/V1-5-SHAKEDOWN-CHECKLIST.md`

- [x] Finish docs/examples drift cleanup for shipped command surfaces
  - Status: Completed
  - Owner: Documentation Team
  - Notes: Closed with the shipped command/example docs aligned to the certified v1.5 surfaces: `UCODE PROFILE` install/enable/disable/verify, `UCODE REPAIR STATUS`, the certified release demo pack, the canonical `uv` + `/.venv` runtime, and the Sonic submission/review flow across the main command reference, command overview, examples, and public docs index.

- [x] Complete the v1.5 central logging upgrade on the shared JSONL contract
  - Status: Completed
  - Owner: Architecture Team
  - Priority: High
  - Notes: Closed with the shared `udos-log-v1.5` JSONL contract in `core/services/logging_api.py`, Wizard wrapper parity, `/api/logs/status` health/stats output, and focused coverage in `core/tests/logging_v15_status_test.py`

- [x] Standardize Python operation on one `.venv` + `uv` runtime contract
  - Status: Completed
  - Owner: Architecture Team
  - Priority: High
  - Notes: Launchers, workspace config, repair/runtime health, root pytest wrappers, and active docs now align to the canonical `UV_PROJECT_ENVIRONMENT=.venv` contract; contributor test policy remains under `/dev/`

- [x] Complete the v1.5 `@dev` provisioning round on canonical `dev/ops`, `dev/docs`, and `dev/goblin` roots
  - Status: Completed
  - Owner: Architecture Team
  - Priority: High
  - Notes: Compatibility tracker files are removed, Dev Mode exposes tracked browser/read contracts in the GUI, Codex/Copilot/VS Code templates align to one contributor workspace, and Goblin now owns the contributor overlay tests already drained from `wizard/tests`

### Round 2 — Offline Logic and Knowledge Foundations

- [x] Promote stable offline logic runtime pieces from `docs/examples/udos_ulogic_pack/` into canonical core modules
  - Status: Completed
  - Owner: Core Team
  - Priority: High
  - Notes: Closed with promoted deterministic action-graph, runtime, state-store, artifact-store, and bounded script-sandbox primitives under `core/ulogic/`, alongside the already-shipped parser, deliverable validation, and research/enrich/generate pipeline. The example pack now remains the supplemental reference surface for optional gameplay/provider scaffolds rather than the only execution model.

- [x] Standardize the smart logic input handler for offline-first intent parsing and workflow handoff
  - Status: Completed
  - Owner: Core Team
  - Priority: High
  - Notes: Canonical spec now lives in `docs/specs/LOGIC-INPUT-HANDLER-v1.5.md`; `core/tui/ucode.py` now routes deterministic command, workflow, knowledge, and guidance frames through the real `UCODE`, `WORKFLOW`, `BINDER`, and operator surfaces before any Dev-only contributor fallback

- [x] Define the global knowledge-bank and local user knowledge-tree contract
  - Status: Completed
  - Owner: Core Team
  - Priority: High
  - Notes: Closed with `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`, canonical user storage under `memory/bank/knowledge/user/`, seed/default/user template layers in `core/services/seed_template_service.py`, and file-backed import/archive handling in `core/services/knowledge_artifact_service.py`

- [x] Standardize research, enrich, and generate flows on the vault-first Markdown pipeline
  - Status: Completed
  - Owner: Core Team
  - Priority: High
  - Notes: `core/ulogic/research_pipeline.py` is now wired through `UCODE RESEARCH|ENRICH|GENERATE`, persists canonical Markdown artifacts into the local knowledge tree, and supports `LIST`/`READ` follow-up operations from the same command surface

- [x] Standardize Markdown capture/enhancement templates for user library gathering
  - Status: Completed
  - Owner: Documentation Team
  - Priority: High
  - Notes: Closed with the shared Markdown family in `core/framework/seed/bank/templates/`, mirrored example packs, and operator-facing `UCODE TEMPLATE` browse/read/duplicate flows backed by tests

### Round 3 — Template and Cross-Component Standardization

- [x] Standardize cross-component runbook/template structure across core, Wizard, Sonic, `uHOME`, and offline logic packs
  - Status: Completed
  - Owner: Architecture Team
  - Priority: High
  - Notes: Closed with the canonical structure in `docs/specs/KNOWLEDGE-BANK-RUNBOOK-STANDARD-v1.5.md`, seed templates under `core/framework/seed/bank/templates/`, Sonic submission template refs, and shared workflow/runbook examples across the v1.5 packs

- [x] Ensure seeded global templates are open-box, browsable, duplicable, and locally editable
  - Status: Completed
  - Owner: Documentation Team
  - Priority: Medium
  - Notes: Closed with seeded/default/user template workspace layers, `UCODE TEMPLATE LIST|READ|DUPLICATE`, and focused coverage in `core/tests/seed_template_service_test.py` and `core/tests/ucode_min_spec_command_test.py`

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

- [x] Define Sonic Device DB as a seeded global catalog with user submissions and contributor approval flow
  - Status: Completed
  - Owner: Sonic Team
  - Priority: High
  - Notes: Closed with the local submission queue under `memory/sonic/submissions/`, core `SONIC SUBMISSION` command support, Wizard review routes under `/api/sonic/submissions`, approval/reject handling, merged-catalog visibility after approval, and focused service/command/route coverage.

- [x] Continue home-lane bridge closure within Wizard service ownership boundaries
  - Status: Completed
  - Owner: Wizard Team
  - Priority: Medium
  - Notes: Closed with Wizard-owned `uHOME` presentation/service boundaries under `wizard/services/uhome_presentation_service.py`, `wizard/services/uhome_command_handlers.py`, `wizard/routes/home_assistant_routes.py`, and `wizard/routes/platform_routes.py`, plus focused route/service tests covering template-workspace defaults and Home Assistant bridge behavior.

- [x] Continue draining contributor-overlay coverage from `wizard/tests` into Goblin
  - Status: Completed
  - Owner: Wizard Team
  - Priority: Medium
  - Notes: Dev scaffold status, Dev browser/read contracts, extension hot-reload contributor coverage, launcher workspace-selection coverage, and certified-profile Dev extension gate coverage now live in `dev/goblin/tests/`; scaffold status now reads from the canonical `DevExtensionService` contract, and the remaining Dev-mode branches in `wizard/tests` are explicitly runtime-owned

- [x] Complete the v1.5 `@dev` tracked editor round
  - Status: Completed
  - Owner: Wizard Team
  - Priority: Medium
  - Notes: The Dev Mode GUI now supports nested tracked navigation, preview, safe text editing, structured validation for JSON, TOML, YAML, Python, shell, and Markdown fence integrity, plus helper-aware backend-owned format/normalize/cleanup actions whose labels match the actual file-type behavior across `dev/ops`, `dev/docs`, and `dev/goblin`

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

- [x] Close the v1.5 self-hosted `@dev` contributor loop
  - Status: Completed
  - Owner: Runtime Team
  - Priority: High
  - Notes: From the `@dev` workspace in Dev Mode, contributors can now plan, schedule, review, and execute uDOS work through canonical runtime surfaces instead of ad hoc repo-local loops; the closure slice adds runtime planning handoff, workflow-plan sync, scheduler-template registration, workflow run/start control, and runtime task-status updates through both Dev Mode and `DEV PLAN` / `DEV SYNC` / `DEV SCHEDULE` / `DEV RUN` / `DEV TASK`

- [x] Harden the local conversation engine and uDOS knowledge bundle for reliable offline assist
  - Status: Completed
  - Owner: Wizard Team
  - Priority: High
  - Notes: GPT4All remains the designated local assist layer and Wizard remains the only network escalation lane; this release lane now has workspace-aware context bundles, conversation carry-over, offline-required enforcement, explicit local-to-network fallback behavior, operator-visible context/conversation/cache readiness, shared bootstrap/install-state evidence across setup/provider-health/self-heal, and focused proof that the local prompt contract includes active uDOS governance plus `ucode`/`@dev` standards under both `core` and `@dev`

- [x] Certify provider rotation, budget policy, and task-scheduler handoff as one managed contract
  - Status: Completed
  - Owner: Wizard Team
  - Priority: High
  - Notes: Closed with quota-aware cloud execution planning, scheduler budget gating, provider-preserving queue execution, operator-visible managed-operations payloads in Ops runtime/config status, prompt-driven `logic/status` parity, and one mounted-route runtime proof showing `/api/ucode/logic/status`, `/api/ops/planning/jobs`, and `/api/ops/config/status` report the same quota-blocked provider contract

- [x] Build the v1.5 demo `ucode` release pack
  - Status: Completed
  - Owner: Release Team
  - Priority: High
  - Notes: Closed with a certified five-demo pack under `docs/examples/ucode_v1_5_release_pack/`, checked-in certification docs/JSON, CLI execution coverage for the runnable scripts, and runtime-generated reports under `.artifacts/release-demos/` executed on the canonical `uv` + `/.venv` contract

- [x] Close creator/gaming/home/core/dev profile install, verify, repair, and rollback evidence
  - Status: Completed
  - Owner: Release Team
  - Priority: High
  - Notes: Closed with persisted install-state for all five certified profiles, checked-in stable-signoff docs/JSON, shared repair evidence through `UCODE REPAIR STATUS`, optional-profile recovery coverage through `UCODE PROFILE DISABLE|ENABLE`, and home rollback-token evidence through the existing `uHOME` installer contract

- [x] Produce final release readiness summary and freeze evidence
  - Status: Completed
  - Owner: Release Team
  - Priority: High
  - Notes: Closed with `docs/specs/V1-5-FREEZE-SUMMARY.md` and `docs/specs/V1-5-FREEZE-SUMMARY.json`, naming the exact demo pack, certified profiles, local assist baseline, managed-operations proof, offline-runtime promotion, Sonic review flow, home-lane bridge evidence, and the remaining metadata-cut decision boundary.

---

## Notes

- Historical v1.4.x stabilization work is complete and should remain in `completed.json` or `dev/docs/devlog/`.
- Active sequencing lives in `dev/docs/roadmap/ROADMAP.md`.

---

End of File
