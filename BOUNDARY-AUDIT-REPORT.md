# Core/Wizard Boundary Audit Report
Generated: 2026-02-20

## Executive Summary
Core module has **5 boundary violations** where handlers import non-stdlib or wizard-side dependencies directly.

**Policy Target:** Core is stdlib-only + core services. Wizard-specific operations should delegate via provider registry or be Wizard-only handlers.

---

## Critical Violations

### 1. ❌ MUSIC Handler - Groovebox Service Import
**File:** `core/commands/music_handler.py` (lines 25, 31)
**Type:** Wizard service dependency
**Severity:** HIGH

```python
# Lines 25-31 (violates core-only boundary)
from groovebox.wizard.services.groovebox_service import get_groovebox_service
from groovebox.wizard.services.songscribe_service import get_songscribe_service
```

**Issue:** Core handler directly imports wizard-side groovebox services. Should use provider registry pattern.

**Recommendation:**
- Lazy-load via provider registry: `core.services.provider_registry.get_service("groovebox")`
- Fallback gracefully if wizard not available

---

### 2. ❌ SONIC Handler - External Library Import
**File:** `core/commands/sonic_handler.py` (line 183)
**Type:** External stdlib boundary
**Severity:** MEDIUM

```python
# Line 183 (context)
from sonic.core.plan import write_plan
```

**Issue:** Imports from `sonic.core` which is external to core/wizard. Sonic is optional extension.

**Recommendation:**
- Wrap in try/except
- Check provider registry first
- Detect sonic/ path existence before import

---

### 3. ❌ WIZARD Handler - Non-stdlib requests Library
**File:** `core/commands/wizard_handler.py` (lines 416, 614, 740, 787)
**Type:** Non-stdlib dependency
**Severity:** CRITICAL

```python
# Lines 416, 614, 740, 787
import requests  # Non-stdlib, breaks core-only policy
```

**Issue:** Core handler uses `requests` library which violates stdlib-only constraint. Core must use only stdlib (`urllib`, `subprocess`, etc).

**Recommendation:**
- Replace with `urllib.request` (stdlib alternative)
- OR move WIZARD handler to wizard/ side entirely
- OR use subprocess to call `curl` (available on all systems)

---

### 4. ❌ DEV Mode Handler - Non-stdlib requests Library
**File:** `core/commands/dev_mode_handler.py` (line 6)
**Type:** Non-stdlib dependency
**Severity:** CRITICAL

```python
# Line 6
import requests
```

**Issue:** Same as WIZARD handler - non-stdlib violates core policy.

**Recommendation:** Replace with stdlib `urllib.request`

---

### 5. ❌ EMPIRE Handler - Non-stdlib requests Library
**File:** `core/commands/empire_handler.py` (lines 299, 324)
**Type:** Non-stdlib dependency
**Severity:** HIGH

```python
# Lines 299, 324
import requests
```

**Issue:** Non-stdlib dependency in core handler.

**Recommendation:** Replace with stdlib `urllib.request`

---

## Summary by Category

| Handler | Issue | Severity | Fix Complexity |
|---------|-------|----------|-----------------|
| MUSIC | Wizard service import | HIGH | Low - use provider registry |
| SONIC | External library import | MEDIUM | Low - wrap in try/except |
| WIZARD | requests non-stdlib | CRITICAL | Medium - use urllib or subprocess |
| DEV | requests non-stdlib | CRITICAL | Medium - use urllib or subprocess |
| EMPIRE | requests non-stdlib | HIGH | Medium - use urllib or subprocess |

---

## Requests → Urllib Migration Strategy

For WIZARD/DEV/EMPIRE handlers, replace `requests` with `urllib`:

```python
# Before:
import requests
response = requests.get(url, timeout=5)
response.json()

# After (stdlib):
import urllib.request
import json
try:
    with urllib.request.urlopen(url, timeout=5) as response:
        data = json.loads(response.read())
except urllib.error.URLError as e:
    # Handle error
```

---

## Audit Checklist

- [ ] Fix MUSIC handler groovebox imports → provider registry
- [ ] Fix SONIC handler sonic imports → wrap/detect
- [ ] Fix WIZARD handler requests → urllib
- [ ] Fix DEV handler requests → urllib
- [ ] Fix EMPIRE handler requests → urllib
- [ ] Run `python tools/ci/check_core_stdlib_boundary.py` (if core/py exists)
- [ ] Verify all handlers pass validation

---

## Next Steps

1. **Immediate (Critical):** Fix requests → urllib in WIZARD, DEV, EMPIRE
2. **High Priority:** Fix MUSIC groovebox imports via provider registry
3. **Medium Priority:** Fix SONIC external imports with try/except
4. **Validation:** Re-run boundary checker to confirm all violations resolved
