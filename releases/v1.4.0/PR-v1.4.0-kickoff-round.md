# PR Draft: v1.4.0 Kickoff Round - Containerization Readiness

## Summary
Completes the v1.4.0 kickoff round by implementing lifecycle/container readiness gates and baseline container artifacts for Sonic + Groovebox lanes.

## Changes
- Migrated TOYBOX adapter app lifecycle to FastAPI lifespan handlers.
- Added CI gate: `check_v1_4_0_toybox_lifespan_readiness.py`.
- Fixed Sonic Dockerfile entrypoint to `core/sonic_cli.py` and added smoke gate.
- Added `library/songscribe/Dockerfile` and smoke gate.
- Added compose profile matrix CI validator and report generation.
- Added container capability matrix contract and validation gate.
- Added unified release preflight automation gate.
- Updated kickoff/spec docs and release docs for GitHub version release prep.

## Key Files
- `wizard/services/toybox/base_adapter.py`
- `sonic/Dockerfile`
- `library/songscribe/Dockerfile`
- `tools/ci/check_v1_4_0_toybox_lifespan_readiness.py`
- `tools/ci/check_v1_4_0_sonic_docker_smoke.py`
- `tools/ci/check_v1_4_0_groovebox_docker_smoke.py`
- `tools/ci/check_v1_4_0_compose_profile_matrix.py`
- `tools/ci/check_v1_4_0_container_capability_matrix.py`
- `tools/ci/check_v1_4_0_release_preflight.py`
- `core/config/v1_4_0_container_capability_matrix.json`
- `docs/specs/v1.4.0-DOCKER-AUTOMATION-CAPABILITY-SPEC.md`
- `docs/specs/v1.4.0-KICKOFF-CHECKLIST.md`
- `docs/specs/v1.4.0-EXECUTION-ORDER.md`
- `releases/v1.4.0/PD-v1.4.0-kickoff-round.md`

## Validation
```bash
python3 tools/ci/check_v1_4_0_toybox_lifespan_readiness.py
python3 tools/ci/check_v1_4_0_sonic_docker_smoke.py
python3 tools/ci/check_v1_4_0_groovebox_docker_smoke.py
python3 tools/ci/check_v1_4_0_compose_profile_matrix.py
python3 tools/ci/check_v1_4_0_container_capability_matrix.py
python3 tools/ci/check_v1_4_0_release_preflight.py
python3 -m pytest -q core/tests/v1_4_0_toybox_lifespan_readiness_test.py core/tests/v1_4_0_container_kickoff_gates_test.py wizard/tests/toybox_adapter_lifecycle_test.py
```

## Rollout Notes
- No contract freeze files were modified.
- Existing v1.3 stabilization gates remain enabled as v1.4 guardrails.
