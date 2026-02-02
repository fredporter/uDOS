# uDOS Architecture Migration: Package → Hybrid Container Model

**Date:** 2026-02-01
**Status:** In Progress
**Impact:** Reduces package bloat, enables independent deployment

## The Change

We're moving away from **pure package structure** (`__init__.py` everywhere) to a **hybrid model**:
- **Core infrastructure** stays as packages (logging, config, user mgmt)
- **Self-contained modules** become containers (groovebox, empire, sonic)
- **Test structure** unifies in `memory/tests/`

## What This Means for You

### ✅ Keep Package Structure
```
core/services/          # Core infrastructure - keep __init__.py
core/commands/          # Command handlers - keep __init__.py
wizard/services/        # Wizard infrastructure - keep __init__.py
knowledge/              # Knowledge banks - keep __init__.py
```

Import directly:
```python
from core.services.logging_service import get_logger
from wizard.services.config import load_config
```

### 🔄 Migrate to Containers
```
groovebox/              # → /library/groovebox/container.json
empire/                 # → /library/empire/container.json
sonic/                  # → /library/sonic/container.json (coming)
```

**Definition tracked:** `/library/groovebox/container.json` (git)
**Clone stored:** `/library/containers/groovebox/` (gitignored)

Import via service client:
```python
# OLD (direct import)
from groovebox.engine.sequencer import Sequencer

# NEW (container-aware)
from core.services.registry import get_service
engine = get_service('groovebox')  # Type: GrooveboxEngine
sequencer = engine.sequencer
```

### 📦 Container Definition Example

```json
{
  "container": {
    "id": "groovebox",
    "name": "Groovebox - Music Engine",
    "type": "git",
    "source": "https://github.com/fredporter/uDOS",
    "entry_point": "groovebox/engine/sequencer.py"
  },
  "policy": {
    "containerized": true,
    "allow_direct_imports": false,
    "service_interface": "GrooveboxEngine"
  }
}
```

## How Tests Work

All tests in **one place:** `memory/tests/`

```bash
# Test core infrastructure
python memory/tests/test_logging.py

# Test containerized modules
python memory/tests/test_groovebox.py  # Imports via registry
python memory/tests/test_empire.py     # Imports via registry

# Shakedown (full system)
./start_udos.sh memory/tests/shakedown-script.md
```

## Why This Helps

| Problem | Before | After |
|---------|--------|-------|
| 5,744 `__init__.py` files | Everywhere | Only where needed |
| Module imports | `from x.y.z import Thing` | `get_service('x').Thing` |
| Deployment | Everything together | Containers independent |
| Testing | Multiple test dirs | Unified `memory/tests/` |
| Circular deps | Hard to debug | Clear boundaries |

## Migration Timeline

**Phase 1 (Done)** ✅
- Created container definitions for groovebox, empire
- Added ServiceRegistry pattern
- Updated .gitignore

**Phase 2 (Next)**
- Update groovebox tests to use registry
- Update empire tests to use registry
- Remove direct imports from containerized modules

**Phase 3 (Later)**
- Containerize sonic, distribution
- Create plugin/extension containers
- Deprecate legacy imports

## For Now: What You Can Do

### Don't Remove `__init__.py` Files Yet
Keep them in:
- `core/services/__init__.py` (new, documents pattern)
- `core/commands/__init__.py`
- `wizard/services/__init__.py`
- `knowledge/` subdirs

### Start Using Registry for New Code
```python
# New code
from core.services.registry import get_service
logger = get_service('logging').get_logger('my-category')

# Old code still works
from core.services.logging_service import get_logger
logger = get_logger('my-category')
```

### Document Your Container Modules
If you build something that should be containerized:
```bash
mkdir -p library/mymodule
cat > library/mymodule/container.json << 'EOF'
{
  "$schema": "../container.schema.json",
  "container": {
    "id": "mymodule",
    "name": "My Module Name",
    "type": "git",
    "source": "https://...",
    "entry_point": "mymodule/main.py"
  },
  ...
}
EOF
```

## FAQ

**Q: Do I need to change my imports now?**
A: No. Direct imports still work. Start with new code.

**Q: When can I delete `__init__.py`?**
A: Only in containerized modules (groovebox, empire). Core modules keep them.

**Q: What's `/library/containers/`?**
A: Local clones of containerized repos. Never committed. Used for testing/development.

**Q: How do I test a containerized module?**
A: In `memory/tests/test_modulename.py`, use the registry:
```python
from core.services.registry import get_service

@pytest.fixture
def engine():
    return get_service('groovebox')

def test_something(engine):
    # Test using registry-loaded module
    ...
```

---

**Next:** Check [CONTAINER-MANIFEST.md](../library/README.md) for full container spec.
