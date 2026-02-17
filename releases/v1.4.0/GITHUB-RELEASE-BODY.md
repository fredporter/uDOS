## uDOS v1.4.0 — Containerization, Library Management, and Modularization

This release completes the v1.4.0 milestone: Core containerization readiness, the LIBRARY command surface, and the modularization cleanup pass.

---

### Highlights

**Container Readiness**
- Migrated TOYBOX adapter lifecycle to FastAPI lifespan handlers (replaces deprecated `on_event` hooks).
- Sonic Screwdriver Dockerfile — entrypoint corrected, CI smoke gate added.
- Songscribe/Groovebox Dockerfile — build definition and CI smoke gate added.
- Compose profile matrix validator verifies all required `docker compose --profile` combinations.
- Container capability matrix contract validates lane definitions, artifacts, and smoke gates.

**LIBRARY Command**
- New `LIBRARY` TUI command with `STATUS`, `SYNC`, `INFO`, `LIST`, and `HELP` subcommands.
- Backed by `LibraryManagerService` — discovers all integrations from `/library`.
- Wired into dispatcher, help, ghost mode guard, and autocomplete.
- Ghost-mode safe: read-only subcommands pass through without block.

**Modularization and CI**
- `library-command` lane added to capability matrix with `skip_compose` flag for non-docker lanes.
- Unified release preflight (`check_v1_4_0_release_preflight.py`) aggregates all 8 gates.
- v1.3.25 contract freeze baseline rebased after GPLAY→PLAY rename and deprecated_aliases cleanup.

---

### CI Gates (all green)

| Gate | Status |
|---|---|
| `check_v1_3_25_contract_freeze.py` | ✅ PASS |
| `check_v1_3_26_final_stabilization.py` | ✅ PASS |
| `check_v1_4_0_toybox_lifespan_readiness.py` | ✅ PASS |
| `check_v1_4_0_sonic_docker_smoke.py` | ✅ PASS |
| `check_v1_4_0_groovebox_docker_smoke.py` | ✅ PASS |
| `check_v1_4_0_compose_profile_matrix.py` | ✅ PASS |
| `check_v1_4_0_container_capability_matrix.py` | ✅ PASS |
| `check_v1_4_0_library_command_smoke.py` | ✅ PASS |

---

### Report Artifacts
- `memory/reports/v1_4_0_release_preflight.json`
- `memory/reports/v1_4_0_container_capability_matrix.json`
- `memory/reports/v1_4_0_compose_profile_matrix.json`

---

### Deferred to v1.4+
- Groovebox Songscribe parser pipeline (tokenizer, AST, audio synthesis, MIDI/WAV export, transport layer). The Groovebox Dockerfile and smoke gate are included in this release; the full pipeline moves to the next active development round.

---

### Notes
- Compose profile validation runs in parser mode when Docker Compose is unavailable in the CI runner.
- `sonic/` is a git submodule — ensure the submodule pointer is updated in the parent repo release.
- v1.3.x contract surfaces remain frozen; no frozen artifacts were modified in this release.
