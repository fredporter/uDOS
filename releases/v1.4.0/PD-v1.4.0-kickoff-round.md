# PD: v1.4.0 Kickoff Round (Containerization Readiness)

## Context
This round transitions from v1.3 stabilization closure into the first actionable v1.4.0 containerization slice.

## Goals
- Complete kickoff checklist items for containerization readiness.
- Ensure TOYBOX lifecycle is migrated to FastAPI lifespan model.
- Ensure Sonic and Groovebox container definitions are present and smoke-checked.
- Ensure compose profile combinations are validated with a deterministic gate.

## Scope Delivered
- TOYBOX lifespan migration + readiness gate.
- Sonic Dockerfile correction + smoke gate.
- Songscribe/Groovebox Dockerfile implementation + smoke gate.
- Compose profile matrix validator + report artifact.
- Container capability matrix contract + validation gate.
- Unified release preflight automation gate.

## Non-Goals
- Full production hardening of Sonic/Groovebox container runtimes.
- Complete v1.4 library manager delivery.

## Acceptance Criteria
- All v1.4 kickoff CI gates pass.
- Kickoff checklist immediate tasks are all checked.
- Artifacts are documented for release traceability.

## Validation Commands
```bash
python3 tools/ci/check_v1_4_0_toybox_lifespan_readiness.py
python3 tools/ci/check_v1_4_0_sonic_docker_smoke.py
python3 tools/ci/check_v1_4_0_groovebox_docker_smoke.py
python3 tools/ci/check_v1_4_0_compose_profile_matrix.py
python3 tools/ci/check_v1_4_0_container_capability_matrix.py
python3 tools/ci/check_v1_4_0_release_preflight.py
```

## Risks / Follow-ups
- Compose matrix performs `docker compose config` validation only when Docker Compose is available.
- Sonic and Songscribe runtime behavior will need deeper integration tests in later v1.4 slices.
