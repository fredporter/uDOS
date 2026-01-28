# Self-Healing System Quick Reference

**Version:** v1.0.0  
**Last Updated:** 2026-01-26

---

## Overview

The uDOS self-healing system automatically detects and repairs common issues:

- Missing Python dependencies
- Port conflicts
- Deprecated code patterns
- File permissions
- Configuration errors

---

## CLI Usage

### Check All Components

```bash
./bin/udos-self-heal.sh
```

### Check Specific Component

```bash
./bin/udos-self-heal.sh wizard
./bin/udos-self-heal.sh goblin
./bin/udos-self-heal.sh core
```

### Check Without Auto-Repair

```bash
./bin/udos-self-heal.sh wizard --no-repair
```

---

## Python API

### Basic Usage

```python
from core.services.self_healer import SelfHealer

healer = SelfHealer(component="wizard", auto_repair=True)
result = healer.diagnose_and_repair()

if result.success:
    print("✅ System healthy!")
else:
    print("⚠️ Issues found:")
    for issue in result.issues_remaining:
        print(f"  - {issue.description}")
```

### Convenience Function

```python
from core.services.self_healer import run_self_heal

result = run_self_heal("wizard", auto_repair=True)
for msg in result.messages:
    print(msg)
```

---

## Issue Types

| Type                 | Description                  | Auto-Repairable |
| -------------------- | ---------------------------- | --------------- |
| `MISSING_DEPENDENCY` | Python package not installed | ✅ Yes          |
| `VERSION_MISMATCH`   | Wrong version installed      | ✅ Yes          |
| `PORT_CONFLICT`      | Port already in use          | ✅ Yes          |
| `FILE_PERMISSION`    | Script not executable        | ✅ Yes          |
| `DEPRECATED_CODE`    | Old API usage detected       | ⚠️ Manual       |
| `CONFIG_ERROR`       | Invalid configuration        | ⚠️ Manual       |

---

## Integration with Launchers

All launchers now include self-healing checks:

### Wizard Server

```bash
./bin/Launch-Wizard-Server.command
# → Runs self-heal check before starting
```

### Goblin Dev Server

```bash
./dev/bin/Launch-Goblin-Dev.command
# → Runs self-heal check before starting
```

### uDOS TUI

```bash
./bin/Launch-uDOS-TUI.command
# → Runs self-heal check before starting
```

---

## What Gets Fixed Automatically

### Missing Dependencies

**Detected:**

```
❌ Missing required dependency: fastapi
```

**Repaired:**

```bash
pip install fastapi
```

### Port Conflicts

**Detected:**

```
❌ Port 8767 is already in use
```

**Repaired:**

```bash
python -m wizard.cli_port_manager kill :8767
```

### File Permissions

**Detected:**

```
⚠️ Script not executable: launch-goblin-server.sh
```

**Repaired:**

```bash
chmod +x dev/goblin/bin/launch-goblin-server.sh
```

### Deprecated Code (Manual)

**Detected:**

```
⚠️ FastAPI on_event is deprecated, use lifespan instead
```

**Action Required:**

```
Code changes require manual review
See: https://fastapi.tiangolo.com/advanced/events/
```

---

## Exit Codes

| Code | Meaning                                  |
| ---- | ---------------------------------------- |
| `0`  | All checks passed or all issues repaired |
| `1`  | Critical issues remain unresolved        |

---

## Logging

Self-healing logs to:

- `memory/logs/session-commands-YYYY-MM-DD.log`
- Console output during launcher execution

Look for `[HEAL]` tags in logs.

---

## Examples

### Check Before Deployment

```bash
# Dry-run (no repairs)
./bin/udos-self-heal.sh all --no-repair

# If OK, proceed with repairs
./bin/udos-self-heal.sh all
```

### Fix Port Conflicts

```bash
# Let self-healer fix it
./bin/udos-self-heal.sh wizard

# Or manually
python -m wizard.cli_port_manager kill wizard
```

### Install Missing Deps

```bash
# Auto-install via self-healer
./bin/udos-self-heal.sh goblin

# Or manually
pip install -r requirements.txt
```

---

## Troubleshooting

### Self-healer Not Found

```bash
# Ensure you're in repo root and venv is activated
cd /path/to/uDOS
source .venv/bin/activate
python -m core.services.self_healer wizard
```

### Port Manager Fails

```bash
# Try direct kill
lsof -ti:8767 | xargs kill -9
```

### Permission Denied

```bash
# Fix script permissions manually
find bin/ dev/bin/ -name "*.sh" -exec chmod +x {} \;
```

---

## Extending

### Add Custom Checks

Edit `/core/services/self_healer.py`:

```python
def _check_custom(self):
    """Add your custom check."""
    if some_condition:
        self.issues.append(Issue(
            type=IssueType.CONFIG_ERROR,
            severity=IssueSeverity.WARNING,
            description="Custom issue detected",
            component=self.component,
            repairable=False
        ))
```

### Add Custom Repairs

```python
def _repair_custom(self, issue: Issue) -> bool:
    """Add your custom repair."""
    try:
        # Repair logic here
        return True
    except Exception:
        return False
```

---

## See Also

- [AGENTS.md](../AGENTS.md) - Project architecture
- [Port Manager Quick Reference](extensions/docs/PORT-REGISTRY.md)
- [Launcher Guide](../LAUNCHER-GUIDE.md)

---

**Status:** Production Ready  
**Last Updated:** 2026-01-26
