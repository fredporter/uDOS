# v1.5 Decision Implementation Audit

Updated: 2026-03-05
Status: Release-ready with documented deferred lanes

## Purpose

This audit maps the active decision set to implementation and test evidence for
the v1.5 release cut.

## Decision Coverage Matrix

| Decision doc | Gate class | Status | Evidence |
| --- | --- | --- | --- |
| `docs/decisions/udos-protocol-v1.md` | supporting protocol | implemented in current runtime | `core/tui/protocol_bridge.py`, `core/tests/tui_protocol_bridge_test.py` |
| `docs/decisions/udos-reference-implementation.md` | supporting reference | aligned with current runtime | `core/tui/protocol_bridge.py`, `core/tui/vibe_dispatch_adapter.py` |
| `docs/decisions/udos-teletext-theme.md` | supporting theme reference | implemented for TUI lane | `core/tui/ui_elements.py`, `core/tui/renderer.py`, `core/tests/tui_protocol_bridge_test.py` |
| `docs/decisions/uDOS-v1-3.md` | historical snapshot | no v1.5 implementation gate | historical by decision status |
| `docs/decisions/UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md` | active non-blocking platform reference | non-blocking and aligned | `wizard/routes/home_assistant_routes.py`, `wizard/tests/home_assistant_routes_test.py`, `wizard/tests/uhome_platform_presentation_test.py` |
| `docs/decisions/uHOME-spec.md` | active home profile lane | implemented for v1.5 release lane | `docs/specs/UHOME-v1.5.md`, `core/tests/sonic_uhome_bundle_test.py`, `wizard/tests/home_assistant_routes_test.py`, `wizard/tests/uhome_presentation_service_test.py` |
| `docs/decisions/v1-5-logic-assist-final-spec.md` | supporting narrative | partially promoted; non-gating remainder | promoted runtime surfaces: `core/ulogic/`, `core/tests/ulogic_runtime_test.py`, `wizard/services/logic_assist_service.py`, `wizard/tests/logic_assist_service_test.py` |
| `docs/decisions/v1-5-logic-input-handler.md` | active v1.5 runtime contract | implemented | `core/tui/ucode.py` routing contract, `core/tests/ucode_tui_v15_routing_test.py`, `core/tests/test_input_router.py` |
| `docs/decisions/v1-5-offline-assist.md` | supporting scaffold | implemented where promoted into canonical runtime | `core/ulogic/parser.py`, `core/ulogic/runtime.py`, `core/ulogic/script_sandbox.py`, `core/tests/ulogic_parser_test.py`, `core/tests/ulogic_runtime_test.py` |
| `docs/decisions/v1-5-python-runtime-contract.md` | active v1.5 runtime contract | implemented | `core/services/python_runtime_contract.py`, `scripts/run_pytest.sh`, `scripts/run_pytest_core_stdlib.sh`, `core/tests/python_runtime_contract_test.py` |
| `docs/decisions/v1-5-ucode-tui-spec.md` | active source of truth | implemented | `core/tui/ucode.py`, `core/tui/protocol_bridge.py`, `core/tests/ucode_tui_v15_routing_test.py`, `core/tests/tui_protocol_bridge_test.py` |
| `docs/decisions/v1-5-workflow-manager.md` | active v1.5 runtime contract | implemented | `core/workflows/`, `core/commands/workflow_handler.py`, `wizard/routes/workflow_routes.py`, `core/tests/workflow_scheduler_test.py`, `wizard/tests/workflow_routes_test.py` |
| `docs/decisions/v1-5-workflow.md` | active scheduler decision | implemented with explicit deferred lanes preserved | implemented core lane: `core/workflows/`, `core/tests/workflow_scheduler_test.py`; implemented Wizard orchestration surfaces: `wizard/routes/workflow_routes.py`; deferred lanes remain as stated in the decision doc |

## Release Blockers Found During Audit

- fixed: `core/tests/v1_5_stable_signoff_test.py` expected `release_channel == "beta"` while canonical signoff json is `stable`.
- action: updated assertion to `stable`.

## Validation Runs (2026-03-05)

Command group 1:

```bash
./scripts/run_pytest.sh -q \
  core/tests/python_runtime_contract_test.py \
  core/tests/ucode_tui_v15_routing_test.py \
  core/tests/tui_protocol_bridge_test.py \
  core/tests/ulogic_parser_test.py \
  core/tests/ulogic_runtime_test.py \
  core/tests/ulogic_deliverables_test.py \
  core/tests/workflow_scheduler_test.py \
  core/tests/workflow_handler_test.py \
  core/tests/v1_5_stable_signoff_test.py \
  core/tests/sonic_uhome_bundle_test.py \
  wizard/tests/workflow_routes_test.py \
  wizard/tests/platform_launch_session_routes_test.py \
  wizard/tests/renderer_routes_test.py \
  wizard/tests/publish_routes_test.py \
  wizard/tests/publish_service_test.py \
  wizard/tests/graphics_service_test.py \
  wizard/tests/managed_operations_runtime_contract_test.py
```

Result: 78 passed.

Command group 2:

```bash
./scripts/run_pytest.sh -q \
  wizard/tests/home_assistant_routes_test.py \
  wizard/tests/uhome_presentation_service_test.py \
  wizard/tests/uhome_platform_presentation_test.py \
  wizard/tests/test_beacon_portal.py
```

Result: 61 passed.

## Release Decision

v1.5 is ready for release against this decision set.

No blocking contract gaps were found in the audited lanes.
Deferred lanes remain deferred by explicit decision design and are not release blockers.
