## uDOS v1.4.0 (Kickoff Containerization Readiness)

This release advances Docker spec, automation, and capability gating before full v1.4.0 finalization.

### Highlights
- Migrated TOYBOX adapter lifecycle from deprecated FastAPI `on_event` hooks to lifespan handlers.
- Corrected Sonic container entrypoint and added CI smoke validation.
- Added Songscribe/Groovebox Dockerfile and CI smoke validation.
- Added compose profile matrix validator for required profiles.
- Added container capability matrix contract and validation gate.
- Added unified release preflight automation to aggregate all required gates.

### Included Gates
- `tools/ci/check_v1_4_0_toybox_lifespan_readiness.py`
- `tools/ci/check_v1_4_0_sonic_docker_smoke.py`
- `tools/ci/check_v1_4_0_groovebox_docker_smoke.py`
- `tools/ci/check_v1_4_0_compose_profile_matrix.py`
- `tools/ci/check_v1_4_0_container_capability_matrix.py`
- `tools/ci/check_v1_4_0_release_preflight.py`

### Validation Status
- All above gates passed.
- Preflight report: `memory/reports/v1_4_0_release_preflight.json`
- Capability report: `memory/reports/v1_4_0_container_capability_matrix.json`
- Compose profile report: `memory/reports/v1_4_0_compose_profile_matrix.json`

### Notes
- Compose profile config validation runs in parser mode when Docker Compose is unavailable in runner environment.
- `sonic/` is a submodule; ensure submodule commit and pointer update are included in release PR.

### Remaining v1.4.0 Work
- Library manager command completion: `LIBRARY sync` and `LIBRARY status`.
