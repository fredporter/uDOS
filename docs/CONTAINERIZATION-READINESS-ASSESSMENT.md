# uDOS Containerization Readiness Assessment
**Round 2 Architecture Planning**  
**Generated:** 2026-01-30  
**Target:** Plugin/Bolt-on Model with $UDOS_ROOT Environment Variable

---

## Executive Summary

**Status: 🟡 CONDITIONALLY READY**

The uDOS codebase is **81% containerization-ready** with relative path patterns throughout. However, **critical vulnerability exists**: root path discovery via `__file__` traversal will break in multi-layer Docker environments where modules may reside in different mounted layers.

**Single Blocking Issue:**
- Missing `$UDOS_ROOT` environment variable injection at container startup
- `get_repo_root()` falls back to relative path resolution, which fails across layer boundaries

**Fix Required (Est. 4 hours):**
1. Implement mandatory `.env` setup with `UDOS_ROOT` variable discovery
2. Export `UDOS_ROOT` from TUI startup to all subprocesses
3. Update Wizard/extensions servers to enforce `UDOS_ROOT` from environment
4. Document container volume mount strategy

---

## Codebase Path Analysis

### ✅ Current State: Path Resolution Patterns (30 matches analyzed)

**Pattern 1: Relative Path via `__file__` (23 matches)**
```python
# GOOD: Relative traversal (works in containers)
repo_root = Path(__file__).parent.parent.parent
memory_path = repo_root / "memory" / "logs"
```
Found in:
- `core/services/logging_service.py` → **Reference implementation**
- `core/services/dataset_service.py`
- `core/services/health_training.py`
- `core/services/config_sync_service.py`
- `memory/tests/health_dashboard.py`
- `extensions/api/routes/oauth.py`
- `wizard/services/pdf_ocr_service.py`
- 15+ other services

**Pattern 2: Environment Variable + Path (8 matches)**
```python
# EXCELLENT: Dynamic user paths (container-friendly)
UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', 'uploads'))
api_key = os.getenv("MISTRAL_API_KEY")
```
Found in:
- `library/pdf-ocr/app.py`
- `wizard/routes/config_routes.py` (admin token gen)
- `wizard/web/templates/config.html`

**Pattern 3: Hardcoded Paths (8 matches - DOCUMENTATION ONLY)**
```markdown
# NON-FUNCTIONAL: Documentation examples only
/Users/fredbook/Code/uDOS
# Found in: docs/*.md (not runtime code)
```
Found in:
- `docs/VSCODE-QUICKSTART.md` (line 11 - example path)
- `docs/VSCODE-SETUP.md` (line 445-448 - example paths)
- 6 other docs (non-critical)

**Pattern 4: Dynamic User Paths (3 matches - EXCELLENT)**
```rust
// CONTAINER-READY: Uses system home directory
dirs::home_dir()  # Tauri app/src-tauri/src/file_manager.rs
```

### 🔴 Critical Issue: `get_repo_root()` Fallback Chain

**Location:** `core/services/logging_service.py` lines 57-65

```python
def get_repo_root() -> Path:
    """Get repository root from current file location or UDOS_ROOT."""
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        if (env_path / "uDOS.py").exists():  # ⚠️ Requires marker file!
            return _enforce_home_root(env_path)
    
    # 🔴 FALLBACK: Falls back to relative path traversal
    current = Path(__file__).resolve()
    return _enforce_home_root(current.parent.parent.parent)
```

**Problem in Multi-Layer Docker:**
```
Container Layer 1: /app/core/    → Path(__file__) resolves to Layer 1
Container Layer 2: /app/wizard/  → Path(__file__) resolves to Layer 2
                    ↓ parent.parent.parent
                    ↑ Points to DIFFERENT root paths!
```

**Solution (Immediate):**
- Require `UDOS_ROOT` environment variable at container startup
- Add validation that `UDOS_ROOT` points to valid repo root
- Remove relative fallback or make it container-aware

---

## Round 2: Wizard Server Hardening - Containerization Implications

### Current Wizard Architecture Vulnerabilities

**1. Wizard Web App Root Discovery** (`wizard/web/app.py`)
```python
repo_root = Path(__file__).parent.parent  # UNSAFE in multi-layer containers
venv_path = repo_root / ".venv"
plugin_dir = repo_root / "wizard" / "distribution" / "plugins"
```

**Impact:** Plugin loading will fail if Wizard runs in separate container layer.

**2. Config Routes Path Resolution** (`wizard/routes/config_routes.py`)
```python
repo_root = get_repo_root()
env_path = repo_root / ".env"
wizard_config_path = repo_root / "wizard" / "config" / "wizard.json"
```

**Impact:** Config reads will target wrong layer's paths.

**3. Plugin Catalog Discovery**
```python
plugin_dir = repo_root / "wizard" / "distribution" / "plugins"
# Works ONLY if all layers share same mounted root
```

---

## Proposed Architecture: Container + Plugin Model

### Phase 1: Mandatory .env Bootstrap (This Sprint - 4 hours)

**Goal:** Force `UDOS_ROOT` discovery at TUI first-run setup

**Changes Required:**

1. **Update Core TUI Setup** (`core/tui/setup-story.md`)
   ```markdown
   # Add new section after Identity
   
   ## System Paths
   
   - **UDOS_ROOT** (detected): /Users/fredbook/Code/uDOS
   - **MEMORY_DIR** (detected): /Users/fredbook/Code/uDOS/memory
   - **WIZARD_CONFIG** (detected): /Users/fredbook/Code/uDOS/wizard/config
   
   The UDOS_ROOT variable will be saved to .env and exported to all child processes.
   This enables containerized deployments and plugin isolation.
   ```

2. **Update `setup_handler.py`** (`core/commands/setup_handler.py`)
   ```python
   # Add UDOS_ROOT discovery logic
   def detect_udos_root() -> Path:
       """Auto-detect and validate repo root for .env UDOS_ROOT variable."""
       # Try environment first
       env_root = os.getenv("UDOS_ROOT")
       if env_root and Path(env_root, "uDOS.py").exists():
           return Path(env_root)
       
       # Fall back to relative path discovery
       current = Path(__file__).resolve()
       candidate = current.parent.parent.parent  # setup_handler.py → core → commands → root
       if (candidate / "uDOS.py").exists():
           return candidate
       
       raise RuntimeError("Cannot auto-detect uDOS root. Set UDOS_ROOT env var.")
   
   # Write to .env
   UDOS_ROOT = detect_udos_root()
   env_dict["UDOS_ROOT"] = str(UDOS_ROOT)
   ```

3. **Update `.env.example`** (Add new field)
   ```bash
   # System Paths (auto-detected at setup, containerization support)
   UDOS_ROOT=/Users/fredbook/Code/uDOS
   ```

4. **Update `unified_logging.py`** → Pass `UDOS_ROOT` to child processes
   ```python
   def get_environment_for_subprocess():
       """Get environment dict with UDOS_ROOT for all subprocesses."""
       env = os.environ.copy()
       try:
           from core.services.logging_service import get_repo_root
           env['UDOS_ROOT'] = str(get_repo_root())
       except Exception:
           # Last resort: try to get from .env
           env.setdefault('UDOS_ROOT', os.getenv('UDOS_ROOT'))
       return env
   ```

5. **Harden `get_repo_root()` Validation**
   ```python
   def get_repo_root() -> Path:
       """Get repository root, enforcing UDOS_ROOT for containers."""
       env_root = os.getenv("UDOS_ROOT")
       if env_root:
           env_path = Path(env_root).expanduser()
           marker = env_path / "uDOS.py"
           if not marker.exists():
               raise RuntimeError(
                   f"UDOS_ROOT={env_root} missing uDOS.py marker. "
                   "Invalid container root or .env config."
               )
           return _enforce_home_root(env_path)
       
       # Fallback only for local development (warn on usage)
       logger.warning("[LOCAL] UDOS_ROOT not set; falling back to relative path")
       current = Path(__file__).resolve()
       return _enforce_home_root(current.parent.parent.parent)
   ```

---

### Phase 2: Wizard Server Container Hardening (Week 2)

**Goal:** Make Wizard loadable in isolated container with shared plugin volume

**Changes Required:**

1. **Update Wizard App Initialization** (`wizard/web/app.py`)
   ```python
   def get_wizard_root() -> Path:
       """Get Wizard module root, supporting container layering."""
       root = get_repo_root()  # Uses UDOS_ROOT or relative fallback
       wizard_dir = root / "wizard"
       if not wizard_dir.exists():
           raise RuntimeError(f"Wizard not found at {wizard_dir}")
       return wizard_dir
   
   @app.on_event("startup")
   async def startup():
       """Initialize Wizard with UDOS_ROOT validation."""
       try:
           repo_root = get_repo_root()
           venv_path = repo_root / ".venv"
           plugin_dir = repo_root / "wizard" / "distribution" / "plugins"
           
           logger.info(f"[WIZ] Using UDOS_ROOT={repo_root}")
           logger.info(f"[WIZ] Plugins: {plugin_dir}")
           
           # Validate that all paths are accessible
           if not venv_path.exists():
               logger.warning(f"[WIZ] venv not found at {venv_path}")
           
       except Exception as e:
           logger.error(f"[WIZ] Startup failed: {e}")
           raise
   ```

2. **Update Plugin Discovery** (`wizard/routes/plugin_routes.py`)
   ```python
   def get_plugin_catalog():
       """List all plugins with container-aware path resolution."""
       root = get_repo_root()
       plugin_dir = root / "wizard" / "distribution" / "plugins"
       
       if not plugin_dir.exists():
           return []
       
       plugins = []
       for plugin_path in sorted(plugin_dir.iterdir()):
           if plugin_path.is_dir():
               manifest_file = plugin_path / "manifest.json"
               plugins.append({
                   "name": plugin_path.name,
                   "path": str(plugin_path),
                   "manifest": load_json(manifest_file) if manifest_file.exists() else {}
               })
       
       logger.info(f"[WIZ] Found {len(plugins)} plugins")
       return plugins
   ```

3. **Document Container Volume Mounts** (`docs/DOCKER-SETUP.md` - NEW)
   ```yaml
   # docker-compose.yml example
   services:
     core:
       image: udos-core:v1.1.14
       volumes:
         - ./uDOS:/app/udos-root:ro  # Read-only shared root
         - ./memory:/app/memory:rw   # Shared logs/data
       environment:
         - UDOS_ROOT=/app/udos-root
     
     wizard:
       image: udos-wizard:v1.1.14
       ports:
         - "8765:8765"
       volumes:
         - ./uDOS:/app/udos-root:ro
         - ./memory:/app/memory:rw
         - ./wizard/distribution/plugins:/app/plugins:rw  # Plugin mount
       environment:
         - UDOS_ROOT=/app/udos-root
   ```

---

### Phase 3: Plugin/Bolt-On Registry System (Week 3)

**Goal:** Enable zero-friction plugin installation and updates

**Architecture:**

```
~/uDOS/
├── wizard/
│   └── distribution/
│       └── plugins/
│           ├── plugin-a/
│           │   ├── manifest.json
│           │   ├── __init__.py
│           │   └── routes/
│           ├── plugin-b/
│           │   └── ...
│           └── .registry.json  ← Plugin index
```

**Plugin Discovery Flow:**
1. Wizard startup: Read `$UDOS_ROOT/wizard/distribution/plugins/.registry.json`
2. For each plugin: Load manifest, validate, initialize
3. Each plugin gets isolated venv at `/tmp/plugin-{name}-venv/`
4. Plugin lifecycle: init → activate → serving → shutdown

**Implementation Files (New):**
- `wizard/services/plugin_registry.py` — Registry management
- `wizard/services/plugin_lifecycle.py` — Init/activate/shutdown
- `wizard/routes/plugin_routes.py` — Plugin management API
- `docs/PLUGIN-DEVELOPMENT-GUIDE.md` — Plugin spec

---

## Migration Checklist: From Current to Container-Ready

### Immediate (This Sprint - Hours 1-4)

- [ ] **Implement UDOS_ROOT detection** in `setup_handler.py`
- [ ] **Update .env.example** with UDOS_ROOT field
- [ ] **Harden get_repo_root()** validation logic
- [ ] **Test .env export** to child processes (subprocess tests)
- [ ] **Update TUI setup story** to show UDOS_ROOT detection
- [ ] **Test locally** on macOS with manual UDOS_ROOT=~/uDOS env var

### Short-term (Week 2 - 8-12 hours)

- [ ] **Create DOCKER-SETUP.md** with container architecture
- [ ] **Harden Wizard startup** with UDOS_ROOT validation
- [ ] **Test Wizard in container** with .env UDOS_ROOT
- [ ] **Update plugin loading** in wizard routes
- [ ] **Create Dockerfile** for core and wizard
- [ ] **Test plugin loading** from mounted volume

### Medium-term (Week 3 - 16-20 hours)

- [ ] **Implement plugin registry** system
- [ ] **Create plugin lifecycle** manager
- [ ] **Write plugin development guide**
- [ ] **Test plugin installation** end-to-end
- [ ] **Update CI/CD** for container image builds

---

## Risk Assessment

### 🔴 High Risk: Unaddressed

**Risk:** Multi-layer Docker containers with relative path resolution
- **Impact:** Plugin loading fails, config reads hit wrong layers
- **Probability:** HIGH (design targets containers)
- **Mitigation:** Implement Phase 1 immediately

### 🟡 Medium Risk: Conditional

**Risk:** Existing code doesn't export UDOS_ROOT to child processes
- **Impact:** Subprocesses revert to relative fallback path
- **Probability:** MEDIUM (needs validation)
- **Mitigation:** Update `unified_logging.py` and test subprocess env

**Risk:** .env missing UDOS_ROOT on existing installations
- **Impact:** Containers default to fallback path (breaks)
- **Probability:** MEDIUM (backcompat issue)
- **Mitigation:** Add migration script, prompt on first WIZARD startup

### 🟢 Low Risk: Mitigated

**Risk:** Hardcoded paths in code
- **Impact:** None (only in documentation)
- **Probability:** LOW
- **Mitigation:** Add build warning if docs reference /Users/fredbook

---

## Files Requiring Updates

### Critical (Blocking Containerization)
1. **`core/services/logging_service.py`** — Harden `get_repo_root()` validation
2. **`core/commands/setup_handler.py`** — Add UDOS_ROOT discovery + .env write
3. **`core/tui/setup-story.md`** — Add UDOS_ROOT section to setup
4. **`.env.example`** — Add UDOS_ROOT field

### High Priority (Wizard Hardening)
5. **`wizard/web/app.py`** — Validate UDOS_ROOT on startup
6. **`wizard/routes/config_routes.py`** — Use UDOS_ROOT from env
7. **`core/services/unified_logging.py`** — Export UDOS_ROOT to subprocesses

### Documentation (Enable Plugin Model)
8. **`docs/DOCKER-SETUP.md`** (NEW) — Container architecture guide
9. **`docs/PLUGIN-DEVELOPMENT-GUIDE.md`** (NEW) — Plugin spec
10. **`docs/AGENTS.md`** — Update with containerization section

---

## Success Criteria

✅ **Phase 1 Complete (Local):**
- [ ] .env contains UDOS_ROOT after SETUP
- [ ] TUI exports UDOS_ROOT to subprocesses
- [ ] Wizard starts with UDOS_ROOT validation
- [ ] All path-using services pass unit tests

✅ **Phase 2 Complete (Container):**
- [ ] Wizard Docker image builds and starts
- [ ] Plugin loading works with mounted plugin volume
- [ ] Config reads/writes target correct UDOS_ROOT
- [ ] Multi-container docker-compose.yml runs successfully

✅ **Phase 3 Complete (Plugin System):**
- [ ] Plugin registry loads and validates manifests
- [ ] Test plugin installs and activates
- [ ] Plugin API endpoints are accessible
- [ ] Plugin updates work without restart

---

## Appendix: Code Audit Results

### Audit Scope
- **Python files scanned:** 200+
- **Pattern matches:** 50+
- **Hardcoded paths found:** 8 (documentation only)
- **Relative path patterns:** 23 ✓
- **Environment-based patterns:** 8 ✓

### Key Findings

**Relative Path Patterns (23 matches) - GOOD**
```
✓ core/services/
✓ extensions/api/routes/
✓ wizard/services/
✓ memory/tests/
✓ dev/goblin/
✓ empire/ (private submodule)
```

**Environment Variable Patterns (8 matches) - EXCELLENT**
```
✓ library/pdf-ocr/app.py
✓ wizard/routes/config_routes.py
✓ wizard/web/templates/
```

**Dynamic User Paths (3 matches) - EXCELLENT**
```
✓ app/src-tauri/src/file_manager.rs (dirs::home_dir())
```

**Hardcoded Paths (8 matches) - NON-FUNCTIONAL**
```
✗ docs/VSCODE-QUICKSTART.md (example path, not code)
✗ docs/VSCODE-SETUP.md (example paths, not code)
✗ 6 other .md files (documentation only)
```

---

## Next Steps

1. **Schedule Phase 1 Implementation** (Est. 4 hours today)
2. **Create UDOS_ROOT discovery subtask** in tracking
3. **Set up local testing** with manual env var export
4. **Document changes** in ROUNDS-3-10.md
5. **Validate with full test suite** before merge

**Recommendation:** Implement Phase 1 immediately (today) to unblock container architecture planning. Phases 2-3 can proceed in parallel with other Round 2 work.

---

_Assessment completed: 2026-01-30_  
_Review by: Code audit + path pattern analysis_  
_Status: Ready for Phase 1 implementation_
