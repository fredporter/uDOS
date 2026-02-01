# uDOS Containerization Strategy
**Round 2 Architecture Direction**  
**Decision Document**

---

## Executive Vision

uDOS is transitioning from a **monolithic local application** to a **containerized, plugin-based system** while maintaining offline-first capabilities.

**Key Principle:** No friction for users. Containers are an *implementation detail*, not a user concern.

---

## Current State

### Architecture
```
~/uDOS/
├── core/              ← Local TUI (offline, no deps)
├── wizard/            ← API server (online, config)
├── extensions/        ← Plugin system (bolt-ons)
├── memory/            ← Local data (user data)
├── knowledge/         ← Public KB
├── library/           ← Public utilities
└── .env               ← Single identity file
```

### Limitation
- **All code must understand ~/uDOS root**
- **Relative path discovery fails across container layers**
- **Plugin system needs container-aware setup**

---

## Round 2 Direction

### Goal
Enable three deployment models with zero code difference:

1. **Local Development** (macOS/Linux)
   - Run Core TUI from ~/uDOS/
   - Run Wizard server on port 8765
   - All paths via `$UDOS_ROOT` env var

2. **Docker/Podman** (Single container)
   - Mount ~/uDOS → /app/udos-root
   - Set UDOS_ROOT=/app/udos-root
   - All paths from env var

3. **Kubernetes** (Distributed)
   - Core → pod A (read-only code volume)
   - Wizard → pod B (read-only code volume)
   - Shared memory → persistent volume
   - Plugins → sidecar container

### Key Enabler
**$UDOS_ROOT environment variable** — Universal root path reference

---

## Three-Phase Rollout

### Phase 1: Local Bootstrap (This Week)
- Add UDOS_ROOT to .env
- Auto-detect at setup
- Export to subprocesses
- **Enables:** Local use + container testing

### Phase 2: Wizard Hardening (Next Week)
- Container-aware startup
- Plugin loading from volume
- Config sync with UDOS_ROOT
- **Enables:** Docker deployment

### Phase 3: Plugin Registry (Week 3)
- Unified plugin discovery
- Lifecycle management
- Isolated plugin venvs
- **Enables:** Bolt-on extensibility

---

## Architecture Decision: Container Layout

### Single Container (Development)
```bash
docker run -it \
  -e UDOS_ROOT=/app/udos-root \
  -v ~/uDOS:/app/udos-root:ro \
  -v ~/uDOS/memory:/app/memory:rw \
  udos-all:latest
```

### Multi-Container (Production)
```yaml
# docker-compose.yml
services:
  core-tui:
    image: udos-core:latest
    env:
      UDOS_ROOT: /app/udos-root
    volumes:
      - uDOS-code:/app/udos-root:ro
      - uDOS-memory:/app/memory:rw

  wizard-api:
    image: udos-wizard:latest
    env:
      UDOS_ROOT: /app/udos-root
    volumes:
      - uDOS-code:/app/udos-root:ro
      - uDOS-memory:/app/memory:rw
      - plugins:/app/plugins:rw

  plugins:
    image: udos-plugins:latest
    # Each plugin gets isolated venv
    volumes:
      - plugins:/app/plugins:rw
```

### Volume Strategy
- **uDOS-code** (read-only): All Python/TypeScript code
- **uDOS-memory** (read-write): Logs, user data, training
- **plugins** (read-write): Installed plugins with isolated venvs

---

## Implementation Artifacts

### Files to Create/Modify

**Phase 1 (Local Bootstrap)**
```
.env.example                    (ADD UDOS_ROOT field)
core/commands/setup_handler.py  (ADD UDOS_ROOT detection)
core/services/logging_service.py (HARDEN get_repo_root())
core/services/unified_logging.py (ADD subprocess env export)
core/tui/setup-story.md         (ADD UDOS_ROOT section)
memory/tests/test_udos_root.py  (NEW test suite)
docs/PHASE1-UDOS-ROOT-IMPLEMENTATION.md (NEW implementation guide)
docs/CONTAINERIZATION-READINESS-ASSESSMENT.md (NEW assessment)
```

**Phase 2 (Wizard Hardening)**
```
wizard/web/app.py               (VALIDATE UDOS_ROOT on startup)
wizard/routes/config_routes.py  (USE UDOS_ROOT from env)
wizard/routes/plugin_routes.py  (NEW container-aware plugin loading)
Dockerfile.core                 (NEW core container image)
Dockerfile.wizard               (NEW wizard container image)
docker-compose.yml              (NEW multi-container setup)
docs/DOCKER-SETUP.md            (NEW container user guide)
```

**Phase 3 (Plugin Registry)**
```
wizard/services/plugin_registry.py (NEW plugin manifest registry)
wizard/services/plugin_lifecycle.py (NEW plugin init/activate/shutdown)
wizard/routes/plugin_routes.py     (EXTEND with full plugin API)
docs/PLUGIN-DEVELOPMENT-GUIDE.md   (NEW plugin specification)
.gitignore                         (ADD wizard/distribution/plugins/*)
```

---

## User Impact

### Current Workflow
```bash
cd ~/uDOS
python -m core.tui              # ← Manual
SETUP                            # ← TUI command
python wizard.server.py          # ← Manual
```

### Post-Phase 1 Workflow (Local)
```bash
cd ~/uDOS
python -m core.tui              # ← Same (UDOS_ROOT auto-detected)
SETUP                            # ← Same (UDOS_ROOT saved to .env)
WIZARD start                     # ← Same (UDOS_ROOT exported)
```

### Post-Phase 3 Workflow (Container)
```bash
docker-compose up               # ← One command, two services
curl http://localhost:8765      # ← Wizard API
```

**Key:** No user code changes. Containerization is transparent.

---

## Success Criteria

### Phase 1 Success ✅
- [ ] UDOS_ROOT in .env after setup
- [ ] TUI exports UDOS_ROOT to subprocesses
- [ ] All existing tests pass (no regression)
- [ ] Test suite validates UDOS_ROOT propagation

### Phase 2 Success ✅
- [ ] Wizard Docker image builds
- [ ] Wizard container starts with UDOS_ROOT validation
- [ ] Plugin loading works from mounted volume
- [ ] Multi-container docker-compose.yml runs
- [ ] Config sync reads/writes to correct location

### Phase 3 Success ✅
- [ ] Plugin registry discovers and validates manifests
- [ ] Test plugin installs cleanly
- [ ] Plugin lifecycle (init/activate/shutdown) works
- [ ] Plugin API endpoints are accessible
- [ ] Plugin updates don't require full restart

---

## Risk Mitigation

### Risk: Existing .env files lack UDOS_ROOT
**Mitigation:** 
- Wizard startup detects missing UDOS_ROOT, prompts to run SETUP
- Docs clearly state "Run SETUP after upgrading"
- Migration script: `python -m core.commands.setup --migrate`

### Risk: Relative path fallback breaks in container
**Mitigation:**
- get_repo_root() requires UDOS_ROOT in containers
- Dockerfile sets UDOS_ROOT at build-time
- Docker healthcheck validates UDOS_ROOT on startup

### Risk: Plugin system too complex for users
**Mitigation:**
- Provide one-click plugin install: `PLUGIN install <name>`
- Pre-curate essential plugins (AI, OAuth, etc.)
- Fallback: Use Wizard config for extended settings

---

## Timeline

| Phase | Sprint | Duration | Start | End |
|-------|--------|----------|-------|-----|
| Phase 1 | Week 1 | 4 hours | Today | Friday |
| Phase 2 | Week 2 | 12 hours | Monday | Wednesday |
| Phase 3 | Week 3 | 16 hours | Thursday | Friday next |
| **Total** | **3 weeks** | **32 hours** | Today | Feb 14 |

**Target v1.1.14:** Friday, Feb 7 (with Phase 1 + Phase 2 partial)
**Target v1.2.0:** Friday, Feb 14 (all three phases)

---

## Decision Summary

### Architecture
✅ Keep flat ~/uDOS/ root structure (all 14 folders visible)
✅ Use $UDOS_ROOT env var as universal path reference
✅ Support local, Docker, and Kubernetes deployments

### Implementation
✅ Phase 1: Bootstrap UDOS_ROOT locally (4 hours)
✅ Phase 2: Harden Wizard for containers (12 hours)
✅ Phase 3: Build plugin registry system (16 hours)

### No Breaking Changes
✅ Existing code continues to work
✅ Relative path fallback remains (with warnings)
✅ Users run same commands: `SETUP`, `WIZARD start`
✅ No migration cost for current installations

---

## Next Actions

1. **Today (4 hours):** Implement Phase 1 (UDOS_ROOT bootstrap)
   - [ ] Add UDOS_ROOT detection to setup
   - [ ] Harden get_repo_root() validation
   - [ ] Export UDOS_ROOT to subprocesses
   - [ ] Run full test suite

2. **This Week:** Merge Phase 1, test locally
   - [ ] Code review
   - [ ] Local testing on macOS
   - [ ] Merge to main

3. **Next Week (12 hours):** Implement Phase 2 (Wizard container hardening)
   - [ ] Create Dockerfile for wizard
   - [ ] Test with docker-compose
   - [ ] Document container setup

4. **Week 3 (16 hours):** Implement Phase 3 (Plugin system)
   - [ ] Build plugin registry
   - [ ] Create plugin development guide
   - [ ] Release v1.2.0

---

## References

- [Containerization Readiness Assessment](CONTAINERIZATION-READINESS-ASSESSMENT.md)
- [Phase 1 Implementation Plan](PHASE1-UDOS-ROOT-IMPLEMENTATION.md)
- [AGENTS.md - System Boundaries](AGENTS.md)
- [ENV-STRUCTURE-V1.1.0.md - Data Boundaries](specs/ENV-STRUCTURE-V1.1.0.md)

---

_Strategy Document_  
_Approved for Round 2 Implementation_  
_Replaces previous relative-path-only approach_
