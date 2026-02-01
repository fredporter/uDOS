# Round 2: Containerization & Plugin Architecture Initiative

**Status:** READY FOR EXECUTION  
**Timeline:** 3 weeks (Today → Feb 14)  
**Impact:** Full container + plugin support for v1.2.0  
**Current Phase:** Phase 1 Ready (4 hours, today)

---

## 📋 Executive Summary

uDOS is implementing **containerization and plugin architecture** as a core feature of Round 2, enabling:

- ✅ Local development (unchanged user experience)
- ✅ Docker/Podman single-container deployment
- ✅ Kubernetes multi-pod distributed deployment
- ✅ Plugin/bolt-on extensibility system
- ✅ Zero friction for users (transparent upgrade)

**Single Breaking Issue Identified:** Relative path discovery fails across container layers.  
**Single Solution:** $UDOS_ROOT environment variable (standard practice).

---

## 📊 Current Codebase Status

### Path Resolution Audit (50+ matches analyzed)

| Pattern | Count | Status | Files Affected |
|---------|-------|--------|-----------------|
| Relative path via `__file__` | 23 | ✅ GOOD | core/*, wizard/*, extensions/* |
| Environment variable based | 8 | ✅ EXCELLENT | pdf-ocr, config routes, templates |
| Dynamic user paths | 3 | ✅ EXCELLENT | Tauri, GUI components |
| Hardcoded paths | 8 | ⚠️ NON-FUNCTIONAL | Documentation only (.md files) |

**Verdict:** Codebase is **81% containerization-ready**. Only issue is missing env var injection point.

### Root Cause Analysis

**Current get_repo_root() in logging_service.py:**
```python
def get_repo_root() -> Path:
    env_root = os.getenv("UDOS_ROOT")  # ← Falls back if not set!
    if env_root:
        if (env_path / "uDOS.py").exists():
            return env_path
    
    # FALLBACK: Relative path (breaks in containers!)
    return current.parent.parent.parent
```

**Multi-Layer Docker Problem:**
```
Layer A (Core):        /app/core/services/logging.py → resolves to /app
Layer B (Wizard):      /app/wizard/web/app.py → resolves to /app (CORRECT)
Separate Container:    /code/wizard/web/app.py → resolves to /code (WRONG!)
```

**Solution:** Make UDOS_ROOT mandatory in containers, set at startup.

---

## 🎯 Three-Phase Rollout

### Phase 1: Local Bootstrap ✅ READY
**Timeline:** This week (4 hours, today)  
**Outcome:** $UDOS_ROOT available in all local processes  
**No Breaking Changes**

**Tasks:**
1. Add UDOS_ROOT to `.env.example`
2. Implement auto-detection in setup_handler.py
3. Harden get_repo_root() validation
4. Export UDOS_ROOT to subprocesses
5. Update TUI setup story
6. Create comprehensive test suite

**Deliverables:**
- [x] `docs/CONTAINERIZATION-READINESS-ASSESSMENT.md` — Audit results
- [x] `docs/PHASE1-UDOS-ROOT-IMPLEMENTATION.md` — Step-by-step guide
- [x] `docs/CONTAINERIZATION-STRATEGY.md` — Overall vision
- [x] `docs/decisions/ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md` — Architecture decision

**Files to Modify:**
```
.env.example
core/commands/setup_handler.py
core/services/logging_service.py
core/services/unified_logging.py
core/tui/setup-story.md
memory/tests/test_udos_root.py (NEW)
```

---

### Phase 2: Wizard Hardening 🚀 NEXT WEEK
**Timeline:** Next week (12 hours)  
**Outcome:** Wizard server works in containerized environments  
**Docker Support**

**Tasks:**
1. Update Wizard startup with UDOS_ROOT validation
2. Update config routes with UDOS_ROOT
3. Create Dockerfile for wizard
4. Create docker-compose.yml
5. Test multi-container setup
6. Document container deployment

**Deliverables:**
- [ ] `Dockerfile.core` — Core service image
- [ ] `Dockerfile.wizard` — Wizard service image
- [ ] `docker-compose.yml` — Multi-container orchestration
- [ ] `docs/DOCKER-SETUP.md` — Container user guide

**Files to Modify:**
```
wizard/web/app.py
wizard/routes/config_routes.py
wizard/routes/plugin_routes.py (NEW)
```

---

### Phase 3: Plugin Registry 🔮 WEEK 3
**Timeline:** Week 3 (16 hours)  
**Outcome:** Full plugin/bolt-on extensibility system  
**v1.2.0 Release**

**Tasks:**
1. Implement plugin registry system
2. Create plugin lifecycle manager
3. Build plugin development guide
4. Support isolated plugin venvs
5. Release v1.2.0

**Deliverables:**
- [ ] `wizard/services/plugin_registry.py` — Plugin manifest registry
- [ ] `wizard/services/plugin_lifecycle.py` — Init/activate/shutdown
- [ ] `docs/PLUGIN-DEVELOPMENT-GUIDE.md` — Plugin specification
- [ ] Example plugins (AI, OAuth, CRM)

---

## 📈 Impact on v1.1.14 vs v1.2.0

### v1.1.14 (This Week)
**Focus:** Phase 1 Local Bootstrap
- ✅ UDOS_ROOT in .env
- ✅ Auto-detection at setup
- ✅ Full test coverage
- ✅ Zero user friction
- ✅ Local development unchanged

**Version Number:** v1.1.14 (minor improvement)

### v1.2.0 (Feb 14)
**Focus:** Phases 2 + 3 Container + Plugin
- ✅ Docker Compose support
- ✅ Plugin registry system
- ✅ Plugin marketplace
- ✅ Kubernetes docs
- ✅ Full container architecture

**Version Number:** v1.2.0 (major feature release)

---

## 🔧 Architecture Changes

### Current (v1.1.13)
```
~/uDOS/
├── core/              (TUI)
├── wizard/            (API server)
├── extensions/        (Routes, services)
├── memory/            (Local data)
├── knowledge/         (Public KB)
├── library/           (Utilities)
└── .env               (Identity)

Path Resolution: Relative from __file__
Deployment: Local only
Plugins: Hardcoded routes
```

### Round 2 (v1.2.0)
```
~/uDOS/
├── core/              (TUI, container-aware)
├── wizard/            (API server, container-aware)
├── extensions/        (Plugin system, registry)
├── memory/            (Shared volume)
├── knowledge/         (Public KB)
├── library/           (Utilities)
├── wizard/distribution/plugins/  (Plugin registry)
└── .env               (Identity + UDOS_ROOT)

Path Resolution: $UDOS_ROOT env var (with fallback)
Deployment: Local, Docker, Kubernetes
Plugins: Dynamic registry + lifecycle
```

---

## 🚀 User Experience

### Local Development (v1.1.14+)
```bash
# SETUP auto-detects and saves UDOS_ROOT
$ python -m core.tui
> SETUP

✅ Your uDOS Root: /Users/fredbook/Code/uDOS
✅ UDOS_ROOT saved to .env
✅ Ready to start!

# All services inherit UDOS_ROOT
$ WIZARD start
[WIZ] Using UDOS_ROOT=/Users/fredbook/Code/uDOS
[WIZ] Plugins: /Users/fredbook/Code/uDOS/wizard/distribution/plugins
```

### Docker (v1.2.0)
```bash
# One command, full setup
$ docker-compose up

# Wizard API ready
$ curl http://localhost:8765

# Plugins available
$ curl http://localhost:8765/api/plugins
```

---

## ✅ Success Criteria

### Phase 1 (Local Bootstrap)
- [ ] UDOS_ROOT in .env after SETUP
- [ ] TUI exports UDOS_ROOT to subprocesses
- [ ] get_repo_root() validates UDOS_ROOT first
- [ ] All existing tests pass (no regression)
- [ ] test_udos_root.py passes (new tests)
- [ ] Wizard starts with UDOS_ROOT log message

### Phase 2 (Wizard Hardening)
- [ ] Wizard Docker image builds
- [ ] Wizard container starts with UDOS_ROOT validation
- [ ] Plugin loading works from mounted volume
- [ ] docker-compose.yml runs all services
- [ ] Config sync works across containers

### Phase 3 (Plugin System)
- [ ] Plugin registry discovers manifests
- [ ] Test plugin installs cleanly
- [ ] Plugin lifecycle (init/activate/shutdown) works
- [ ] Plugin API endpoints accessible
- [ ] Plugin updates don't require restart

---

## 📚 Documentation

### Created Today (Phase 1 Docs)
1. ✅ [CONTAINERIZATION-READINESS-ASSESSMENT.md](CONTAINERIZATION-READINESS-ASSESSMENT.md)
   - 50+ code pattern audit
   - Risk assessment
   - Migration checklist

2. ✅ [PHASE1-UDOS-ROOT-IMPLEMENTATION.md](PHASE1-UDOS-ROOT-IMPLEMENTATION.md)
   - Step-by-step implementation guide
   - 7 concrete tasks
   - Testing & validation checklist

3. ✅ [CONTAINERIZATION-STRATEGY.md](CONTAINERIZATION-STRATEGY.md)
   - Architecture vision
   - Three-phase rollout
   - Timeline & success criteria

4. ✅ [ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md](decisions/ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md)
   - Architecture decision record
   - Rationale & alternatives
   - Implementation plan

### To Be Created (Phase 2-3)
- [ ] `docs/DOCKER-SETUP.md` — Container user guide
- [ ] `docs/PLUGIN-DEVELOPMENT-GUIDE.md` — Plugin specification
- [ ] `docs/ENV-VARIABLES.md` — Environment variable reference

---

## 🎬 Getting Started

### Immediate Actions (Next 4 Hours)

1. **Read and Review Documentation** (30 min)
   - Read `CONTAINERIZATION-READINESS-ASSESSMENT.md` (overview)
   - Skim `PHASE1-UDOS-ROOT-IMPLEMENTATION.md` (implementation)

2. **Execute Phase 1 Implementation** (3 hours)
   - Follow `PHASE1-UDOS-ROOT-IMPLEMENTATION.md` tasks 1-7
   - Each task has clear code examples
   - Estimated 20-30 min per task

3. **Run Test Suite** (30 min)
   - Execute `memory/tests/test_udos_root.py`
   - Run full pytest: `pytest memory/ tests/`
   - Verify no regressions

4. **Validate Locally** (30 min)
   - Run SETUP interactively
   - Verify UDOS_ROOT in .env
   - Start Wizard and check logs
   - Run health check task

### If Issues Occur
- Refer to "Risk Mitigation" section in ADR-006
- Check test suite for debugging patterns
- Rollback is simple (revert .env field)

---

## 📊 Metrics & Monitoring

### Phase 1 Metrics
- Test suite pass rate (target: 100%)
- Setup execution time (target: <5 sec)
- UDOS_ROOT detection success rate (target: 100%)

### Phase 2 Metrics
- Docker build time (target: <60 sec)
- Container startup time (target: <10 sec)
- Plugin load time (target: <2 sec)

### Phase 3 Metrics
- Plugin installation success rate (target: >95%)
- Plugin isolation effectiveness
- Plugin marketplace adoption

---

## 🚨 Known Risks & Mitigations

### Risk 1: Multi-layer Container Path Confusion
**Severity:** HIGH  
**Mitigation:** Phase 1 solves with mandatory UDOS_ROOT

### Risk 2: Existing .env Missing UDOS_ROOT
**Severity:** MEDIUM  
**Mitigation:** Wizard startup detects and prompts user to SETUP

### Risk 3: Plugin System Complexity
**Severity:** MEDIUM  
**Mitigation:** Start simple (config-based), add features gradually

---

## 🤝 How to Contribute

### Phase 1 (Today)
- Code review of implementation changes
- Test on your local environment
- Report issues or edge cases

### Phase 2 (Next Week)
- Docker image optimization
- Kubernetes manifest creation
- Container performance testing

### Phase 3 (Week 3)
- Plugin development & testing
- Plugin marketplace curation
- Community feedback

---

## 📞 Questions?

Refer to:
1. **Architecture Decision:** `ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md`
2. **Implementation:** `PHASE1-UDOS-ROOT-IMPLEMENTATION.md`
3. **Audit Results:** `CONTAINERIZATION-READINESS-ASSESSMENT.md`
4. **Overall Vision:** `CONTAINERIZATION-STRATEGY.md`

---

## 📅 Timeline Summary

| Date | Phase | Target | Status |
|------|-------|--------|--------|
| Today | Phase 1 | v1.1.14 | 🟢 READY |
| Next Week | Phase 2 | v1.1.15 | 🟡 PLANNED |
| Week 3 | Phase 3 | v1.2.0 | 🟡 PLANNED |
| Feb 7 | Release | v1.1.14 | 📅 TARGET |
| Feb 14 | Release | v1.2.0 | 📅 TARGET |

---

_Round 2 Initiative: Containerization & Plugin Architecture_  
_Ready for Execution_  
_All Documentation Complete_
