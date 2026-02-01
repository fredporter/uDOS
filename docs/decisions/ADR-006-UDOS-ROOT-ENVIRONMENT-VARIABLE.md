# ADR-006: UDOS_ROOT Environment Variable for Containerization

**Date:** 2026-01-30  
**Status:** ACCEPTED  
**Deciders:** uDOS Engineering  
**Affected Components:** Core, Wizard, Extensions, All Services

---

## Context

### Problem Statement
The current uDOS architecture relies on relative path discovery via `Path(__file__).parent.parent.parent` patterns. This works for local development but **breaks in containerized environments** where code may be distributed across multiple layers or mounted at different paths.

**Blocking Issues:**
1. Multi-layer Docker containers (e.g., Core in `/app/core`, Wizard in `/app/wizard`) cause `__file__` to resolve to different roots
2. Plugin system requires a unified root path for shared resource access
3. No way to inject repository root at container startup without code changes
4. Subprocesses don't inherit root path context, causing fallback to relative discovery

**Example Failure:**
```python
# In wizard/web/app.py (layer A: /app/wizard)
repo_root = Path(__file__).resolve().parent.parent  # → /app
plugin_dir = repo_root / "wizard" / "distribution" / "plugins"

# In separate container task (layer B: /code/wizard)
repo_root = Path(__file__).resolve().parent.parent  # → /code (WRONG!)
plugin_dir = repo_root / "wizard" / "distribution" / "plugins"  # ✗ File not found!
```

### Scope
This decision affects:
- **Core:** Path resolution in services, logging, config
- **Wizard:** App startup, config loading, plugin discovery
- **Extensions:** Plugin routes and service paths
- **All Services:** get_repo_root(), relative path fallback patterns
- **Containers:** Docker/Kubernetes deployments
- **Future Plugins:** Plugin system requirements

### Constraints
1. **No Breaking Changes:** Existing local installations must continue working
2. **No New Dependencies:** Use only stdlib (Path, os.getenv)
3. **Transparent to Users:** No behavior change; env var is transparent
4. **Container-Ready:** Must support Docker, Podman, Kubernetes
5. **Offline-First:** Core TUI must work without UDOS_ROOT set (graceful fallback)

---

## Decision

We will implement **$UDOS_ROOT environment variable** as the primary path reference mechanism, with intelligent fallback to relative path discovery for backward compatibility.

### Implementation Strategy

**Three Phases:**

#### Phase 1: Local Bootstrap (Week 1, 4 hours)
1. Add `UDOS_ROOT` field to `.env.example`
2. Implement auto-detection in `setup_handler.py` (discovers from file system)
3. Save detected UDOS_ROOT to `.env` after setup
4. Harden `get_repo_root()` to prefer env var over relative fallback
5. Export UDOS_ROOT to all subprocesses via environment
6. Update TUI setup story to show UDOS_ROOT detection

**Outcome:** All processes have access to `$UDOS_ROOT` pointing to repository root.

#### Phase 2: Wizard Hardening (Week 2, 12 hours)
1. Add UDOS_ROOT validation to Wizard startup
2. Update plugin loading to use UDOS_ROOT
3. Update config routes to use UDOS_ROOT
4. Create Dockerfile with UDOS_ROOT mount + env var
5. Test multi-container docker-compose setup
6. Document container volume strategy

**Outcome:** Wizard server works in containerized environments with plugin support.

#### Phase 3: Plugin Registry (Week 3, 16 hours)
1. Implement plugin registry system
2. Create plugin lifecycle manager
3. Support isolated plugin venvs
4. Build plugin development guide
5. Release as v1.2.0 (full containerization support)

**Outcome:** Zero-friction plugin system with container support.

### Technical Design

**Path Resolution Chain (in priority order):**

```python
def get_repo_root() -> Path:
    """
    Resolution chain for repository root:
    1. UDOS_ROOT environment variable (containers)
    2. Relative path discovery (local development)
    3. Error (no valid root found)
    """
    # PRIORITY 1: Environment variable (containers, subprocesses)
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser().resolve()
        if (env_path / "uDOS.py").exists():
            return env_path  # ✓ Valid container root
        else:
            raise RuntimeError(f"Invalid UDOS_ROOT: {env_path}")
    
    # PRIORITY 2: Relative discovery (local dev, TUI startup)
    current_file = Path(__file__).resolve()
    candidate = current_file.parent.parent.parent
    if (candidate / "uDOS.py").exists():
        return candidate  # ✓ Valid local root
    
    # PRIORITY 3: Error
    raise RuntimeError("Cannot detect repository root")
```

### Container Deployment Pattern

**Docker Compose Example:**

```yaml
services:
  core:
    image: udos-core:v1.1.14
    environment:
      UDOS_ROOT: /app/udos-root
    volumes:
      - ./uDOS:/app/udos-root:ro

  wizard:
    image: udos-wizard:v1.1.14
    ports:
      - "8765:8765"
    environment:
      UDOS_ROOT: /app/udos-root
    volumes:
      - ./uDOS:/app/udos-root:ro
      - ./memory:/app/memory:rw

  plugins:
    image: udos-plugins:v1.1.14
    environment:
      UDOS_ROOT: /app/udos-root
    volumes:
      - ./uDOS:/app/udos-root:ro
      - ./wizard/distribution/plugins:/app/plugins:rw
```

### User Experience

**Local (No Change):**
```bash
cd ~/uDOS
python -m core.tui                  # TUI auto-detects UDOS_ROOT
SETUP                               # Saves UDOS_ROOT to .env
WIZARD start                        # Wizard inherits UDOS_ROOT
```

**Container (New, but Hidden):**
```bash
docker-compose up                   # UDOS_ROOT set at startup
curl http://localhost:8765          # Works identically
```

---

## Rationale

### Why Environment Variable?
✅ **Standard Practice:** Docker, Kubernetes, systemd all use env vars for paths  
✅ **No Code Changes:** Containers just set env var; code is unchanged  
✅ **Container-Aware:** Supports multi-layer, multi-pod deployments  
✅ **Subprocess-Safe:** Inherited automatically by child processes  
✅ **Testable:** Easy to inject UDOS_ROOT in test environments

### Why Not Just Update `__file__` Logic?
❌ Still breaks across container layers (file location doesn't change)  
❌ More complex to understand and debug  
❌ Requires reading file system during every import  

### Why Not Use Fixed Paths Like `/app/udos-root`?
❌ Inflexible (users might mount at different paths)  
❌ Not testable (hard to inject in tests)  
❌ Couples container images to specific paths  

### Why Three Phases, Not All At Once?
✅ **Risk Mitigation:** Phase 1 proves concept locally before containers  
✅ **Testing Opportunity:** Extensive testing before Phase 2 complexity  
✅ **User Feedback:** Gather feedback on .env UDOS_ROOT before containers  
✅ **Delivery Velocity:** Ship local improvements in Week 1 (v1.1.14)  

---

## Consequences

### Positive
✅ Full Docker/Kubernetes support without code changes  
✅ Plugin system can assume shared UDOS_ROOT  
✅ Subprocesses inherit correct path context  
✅ Local development unaffected (relative path fallback)  
✅ Clear, standard approach (env var patterns)  
✅ Easy to test with different root paths  

### Negative
⚠️ **Requires setup:** Users must run SETUP to save UDOS_ROOT (or set env var manually)  
⚠️ **Breaking on container:** If UDOS_ROOT is wrong, services fail clearly (not silently)  
⚠️ **Documentation burden:** Must explain UDOS_ROOT to container users  

### Mitigations
✅ Auto-detect UDOS_ROOT at setup (no manual entry needed)  
✅ Wizard detects missing UDOS_ROOT, prompts user  
✅ Comprehensive Docker setup guide (docs/DOCKER-SETUP.md)  
✅ Container healthcheck validates UDOS_ROOT on startup  

---

## Implementation Plan

### Phase 1: Local Bootstrap
**Effort:** 4 hours  
**Files Modified:** 6  
**Test Coverage:** 95%  
**Rollback Risk:** LOW (can revert .env field)

1. Add UDOS_ROOT to `.env.example`
2. Implement detection in `setup_handler.py`
3. Harden `get_repo_root()` validation
4. Export UDOS_ROOT in `unified_logging.py`
5. Update setup story in `core/tui/setup-story.md`
6. Create test suite: `memory/tests/test_udos_root.py`
7. Run full test suite (pytest)
8. Document in `PHASE1-UDOS-ROOT-IMPLEMENTATION.md`

**Acceptance Criteria:**
- ✅ .env contains UDOS_ROOT after SETUP
- ✅ get_repo_root() returns UDOS_ROOT env value if set
- ✅ Subprocesses inherit UDOS_ROOT
- ✅ All existing tests pass (no regression)
- ✅ test_udos_root.py passes (new tests)

### Phase 2: Wizard Hardening
**Effort:** 12 hours  
**Files Modified:** 5  
**Test Coverage:** 90%  
**Rollback Risk:** LOW (containerization is opt-in)

1. Update Wizard app startup with UDOS_ROOT validation
2. Update config routes with UDOS_ROOT
3. Create Dockerfile for wizard
4. Create docker-compose.yml
5. Test multi-container setup
6. Document in `docs/DOCKER-SETUP.md`

**Acceptance Criteria:**
- ✅ Wizard Docker image builds successfully
- ✅ Wizard container starts with UDOS_ROOT
- ✅ docker-compose.yml runs all services
- ✅ Plugin loading works from mounted volume

### Phase 3: Plugin Registry
**Effort:** 16 hours  
**Files Modified:** 8  
**Test Coverage:** 85%  
**Rollback Risk:** MEDIUM (plugin system is new)

1. Implement plugin registry system
2. Create plugin lifecycle manager
3. Extend plugin routes
4. Write plugin development guide
5. Release v1.2.0

---

## Alternatives Considered

### Alternative 1: Fixed Installation Path (/opt/udos)
**Rejected:** Too inflexible for development and testing.

### Alternative 2: Configuration File Instead of Env Var
**Rejected:** Less container-friendly; env vars are standard practice.

### Alternative 3: No Containerization Support (Status Quo)
**Rejected:** Round 2 goal explicitly requires container support.

### Alternative 4: Mandatory UDOS_ROOT (No Fallback)
**Rejected:** Breaking change for existing installations; Phase 1 goal is zero friction.

---

## Monitoring & Metrics

### Metrics to Track
- **Phase 1:** Test suite pass rate, setup time (target: <5 sec)
- **Phase 2:** Docker build time, container startup time, plugin load time
- **Phase 3:** Plugin installation success rate, isolation effectiveness

### Alerts
- ⚠️ get_repo_root() fallback usage (should be ~0 after setup)
- ⚠️ Invalid UDOS_ROOT errors in logs
- 🚨 Container startup failures due to missing UDOS_ROOT

---

## Future Considerations

### Beyond v1.2.0
1. **Plugin Marketplace:** Central registry of tested plugins
2. **Plugin Versioning:** Support multiple versions running simultaneously
3. **Kubernetes Manifests:** Official Helm charts for uDOS
4. **Multi-Region:** Plugin sync across distributed Wizard instances
5. **Plugin Signing:** Cryptographic verification of plugin authenticity

---

## References

- [Containerization Readiness Assessment](../CONTAINERIZATION-READINESS-ASSESSMENT.md)
- [Phase 1 Implementation Plan](../PHASE1-UDOS-ROOT-IMPLEMENTATION.md)
- [Containerization Strategy](../CONTAINERIZATION-STRATEGY.md)
- [AGENTS.md - System Boundaries](../AGENTS.md)
- [ENV-STRUCTURE-V1.1.0.md - Data Boundaries](../specs/ENV-STRUCTURE-V1.1.0.md)

---

## Approval

- **Proposed By:** Code Architecture Review
- **Reviewed By:** Engineering Team
- **Decision Date:** 2026-01-30
- **Status:** ✅ ACCEPTED
- **Implementation Start:** 2026-01-30 (Today)
- **Target Completion:** 2026-02-14

---

## Document History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-01-30 | Initial ADR - UDOS_ROOT environment variable |

---

_Architecture Decision Record_  
_uDOS Containerization Initiative_  
_Round 2 Implementation_
