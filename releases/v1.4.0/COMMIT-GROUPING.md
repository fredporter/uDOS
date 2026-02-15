# v1.4.0 Commit Grouping Plan

## Branch
- Recommended: `codex/v1-4-0-kickoff-containerization`

## Commit 1: TOYBOX Lifespan Migration
Message:
- `feat(v1.4.0): migrate TOYBOX adapter lifecycle to FastAPI lifespan`

Files:
- `wizard/services/toybox/base_adapter.py`
- `tools/ci/check_v1_4_0_toybox_lifespan_readiness.py`
- `core/tests/v1_4_0_toybox_lifespan_readiness_test.py`

## Commit 2: Docker and Compose Matrix Gates
Message:
- `feat(v1.4.0): add sonic/groovebox docker smoke and compose profile matrix gates`

Files:
- `sonic/Dockerfile` (in `sonic` submodule)
- `library/songscribe/Dockerfile`
- `tools/ci/check_v1_4_0_sonic_docker_smoke.py`
- `tools/ci/check_v1_4_0_groovebox_docker_smoke.py`
- `tools/ci/check_v1_4_0_compose_profile_matrix.py`
- `core/tests/v1_4_0_container_kickoff_gates_test.py`

## Commit 3: Capability Matrix and Release Preflight Automation
Message:
- `feat(v1.4.0): add container capability matrix contract and release preflight gate`

Files:
- `core/config/v1_4_0_container_capability_matrix.json`
- `tools/ci/check_v1_4_0_container_capability_matrix.py`
- `tools/ci/check_v1_4_0_release_preflight.py`
- `core/tests/v1_4_0_container_capability_matrix_test.py`
- `core/tests/v1_4_0_release_preflight_test.py`

## Commit 4: Specs and Release Docs
Message:
- `docs(v1.4.0): finalize docker automation capability spec and release drafts`

Files:
- `docs/roadmap.md`
- `docs/specs/v1.4.0-KICKOFF-CHECKLIST.md`
- `docs/specs/v1.4.0-EXECUTION-ORDER.md`
- `docs/specs/v1.4.0-DOCKER-AUTOMATION-CAPABILITY-SPEC.md`
- `docs/specs/v1.4.0-READINESS-MEMO.md`
- `releases/v1.4.0.yml`
- `releases/v1.4.0/PD-v1.4.0-kickoff-round.md`
- `releases/v1.4.0/PR-v1.4.0-kickoff-round.md`
- `releases/v1.4.0/GITHUB-RELEASE-BODY.md`

## Submodule Note
- Parent repo shows `m sonic` because `sonic` is a git submodule.
- Commit and push `sonic/Dockerfile` inside submodule first, then commit updated submodule pointer in parent repo.
