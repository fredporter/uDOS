# Migration Guide: v1.1.6

**Upgrading to**: uDOS v1.1.6 (Production Logging & Configuration)
**From**: v1.1.5 or earlier
**Date**: November 28, 2025

---

## Overview

uDOS v1.1.6 introduces major improvements to logging and configuration systems. This guide helps you migrate from earlier versions.

### Breaking Changes

❌ **Configuration**:
- `UDOS_USERNAME` removed from `.env` (use `user.json` instead)

✅ **Backward Compatible**:
- Logging API (old `Logger` class still works via `SessionLogger`)
- All commands and features
- Extension system

---

## Quick Migration

### 1. Update Version

```bash
cd /path/to/uDOS
git pull origin main
pip install -e .
```

### 2. Remove UDOS_USERNAME from .env

**Before** (`.env`):
```bash
UDOS_USERNAME='YourName'
GEMINI_API_KEY='your-key'
```

**After** (`.env`):
```bash
# Username removed - now in user.json only
GEMINI_API_KEY='your-key'
```

### 3. Ensure Username in user.json

**File**: `sandbox/user/user.json`

```json
{
  "USER_PROFILE": {
    "NAME": "YourName",
    "LOCATION": "Your City",
    "TIMEZONE": "Your/Timezone"
  }
}
```

### 4. Test Startup

```bash
python uDOS.py --version
# Should show: uDOS v1.1.6 - Production Logging & Configuration

python uDOS.py
# Should start without errors
```

---

## Detailed Changes

### Configuration System

#### Single Source of Truth

**What Changed**: Username no longer duplicated between `.env` and `user.json`

**Before (v1.1.5)**:
```python
# Username in BOTH places (duplicated)
.env:        UDOS_USERNAME='Fred'
user.json:   USER_PROFILE.NAME: "Fred"
```

**After (v1.1.6)**:
```python
# Username in ONE place only
.env:        # UDOS_USERNAME removed
user.json:   USER_PROFILE.NAME: "Fred"
```

#### Code Updates

**If you have custom extensions:**

```python
# ❌ Old way (v1.1.5)
from core.config import get_config
config = get_config()
username = config.get_env('UDOS_USERNAME')

# ✅ New way (v1.1.6)
from core.config import get_config
config = get_config()
username = config.get_user('USER_PROFILE.NAME')
# Or simpler:
username = config.username
```

---

### Logging System

#### New Architecture

**What Changed**: Flat-file logging replaces nested log structure

**Before (v1.1.5)**:
```
sandbox/logs/
└── sessions/
    └── session_42/
        ├── commands.log
        └── errors.log
```

**After (v1.1.6)**:
```
sandbox/logs/
├── session-commands-2025-11-28.log
├── errors-2025-11-28.log
└── system/
    ├── startup-2025-11-28.log
    └── config-2025-11-28.log
```

#### Code Updates

**Old Logger (still works!)**:
```python
from core.uDOS_logger import Logger

logger = Logger()
logger.log('Message')
logger.log_error('Error')
logger.close()
```

**New Logger (recommended)**:
```python
from core.services.session_logger import SessionLogger

logger = SessionLogger()
logger.log('Message')
logger.error('Error')
logger.close()
```

**New Logging Manager (for extensions)**:
```python
from core.services.logging_manager import get_logger

logger = get_logger('my-extension')
logger.info('Message')
logger.error('Error')
# No close() needed - automatic cleanup
```

---

## File-by-File Migration

### .env File

**Step 1**: Open `.env` in editor

**Step 2**: Remove `UDOS_USERNAME` line:
```bash
# ❌ Remove this line
UDOS_USERNAME='YourName'

# ✅ Keep everything else
GEMINI_API_KEY='your-key'
UDOS_INSTALLATION_ID='abc123'
THEME='foundation'
```

**Step 3**: Save and close

### user.json File

**Step 1**: Check file exists:
```bash
ls -la sandbox/user/user.json
```

**Step 2**: If missing, create it:
```bash
mkdir -p sandbox/user
cat > sandbox/user/user.json << 'EOF'
{
  "USER_PROFILE": {
    "NAME": "YourName",
    "LOCATION": "Your City, Country",
    "TIMEZONE": "Your/Timezone",
    "PASSWORD": ""
  }
}
EOF
```

**Step 3**: Verify USERNAME is set:
```python
python -c "
from core.config import get_config
config = get_config()
print(f'Username: {config.username}')
"
```

### Custom Extensions

**If your extension uses configuration:**

```python
# Before (v1.1.5)
class MyExtension:
    def __init__(self):
        config = get_config()
        self.username = config.get_env('UDOS_USERNAME')

# After (v1.1.6)
class MyExtension:
    def __init__(self):
        config = get_config()
        self.username = config.username  # Uses user.json
```

**If your extension uses logging:**

```python
# Before (v1.1.5)
from core.uDOS_logger import Logger

class MyExtension:
    def __init__(self):
        self.logger = Logger()

    def process(self):
        self.logger.log('Processing')
        self.logger.close()

# After (v1.1.6) - Option 1 (backward compatible)
from core.services.session_logger import SessionLogger

class MyExtension:
    def __init__(self):
        self.logger = SessionLogger()

    def process(self):
        self.logger.log('Processing')
        self.logger.close()

# After (v1.1.6) - Option 2 (recommended)
from core.services.logging_manager import get_logger

class MyExtension:
    def __init__(self):
        self.logger = get_logger('my-extension')

    def process(self):
        self.logger.info('Processing')
        # No close() needed
```

---

## Testing Your Migration

### 1. Version Check

```bash
python uDOS.py --version
```

**Expected output**:
```
uDOS v1.1.6 - Production Logging & Configuration
Released: November 28, 2025

Features:
  • Production logging system (flat-file)
  • Single source of truth configuration
  • SVG graphics generation
  • Modern uCODE syntax
  • 166+ survival knowledge guides
```

### 2. Configuration Check

```python
python -c "
from core.config import get_config

config = get_config()

# Should be None or empty (not in .env)
env_user = config.get_env('UDOS_USERNAME', None)
if env_user:
    print(f'❌ UDOS_USERNAME still in .env: {env_user}')
else:
    print('✅ UDOS_USERNAME removed from .env')

# Should have value (from user.json)
json_user = config.get_user('USER_PROFILE.NAME')
if json_user:
    print(f'✅ Username in user.json: {json_user}')
else:
    print('❌ Username missing from user.json')

# Property should work
username = config.username
print(f'✅ config.username works: {username}')
"
```

### 3. Logging Check

```python
python -c "
from core.services.logging_manager import LoggingManager
from core.services.session_logger import SessionLogger

# Test new logging system
lm = LoggingManager()
logger = lm.get_logger('test')
logger.info('Test message')
print('✅ LoggingManager works')

# Test backward compatibility
sl = SessionLogger()
sl.log('Test message')
sl.close()
print('✅ SessionLogger works')
"
```

### 4. Startup Test

```bash
echo "EXIT" | python uDOS.py
```

**Expected**: Clean startup, no errors

### 5. Profile Test

```bash
python uDOS.py
# At prompt:
CONFIG PROFILE
# Should show your username correctly
EXIT
```

---

## Troubleshooting

### Problem: "Username not set" or shows "user"

**Solution**: Create/update `user.json`

```bash
cat > sandbox/user/user.json << 'EOF'
{
  "USER_PROFILE": {
    "NAME": "YourActualName",
    "LOCATION": "Your City",
    "TIMEZONE": "UTC"
  }
}
EOF
```

### Problem: UDOS_USERNAME still in .env

**Solution**: Manually remove it

```bash
# Edit .env and remove the UDOS_USERNAME line
nano .env
# Or use sed:
sed -i '' '/^UDOS_USERNAME=/d' .env
```

### Problem: Logs not appearing

**Solution**: Check log directory permissions

```bash
mkdir -p sandbox/logs
chmod 755 sandbox/logs
```

### Problem: Old Logger import fails

**Solution**: Update import path

```python
# ❌ Old import
from core.uDOS_logger import Logger

# ✅ New import
from core.services.session_logger import SessionLogger
```

### Problem: Custom extension breaks

**Solution**: Update configuration access

```python
# ❌ Old
username = config.get_env('UDOS_USERNAME')

# ✅ New
username = config.username
```

---

## Rollback (If Needed)

If you encounter issues and need to rollback:

### 1. Checkout Previous Version

```bash
git checkout v1.1.5
pip install -e .
```

### 2. Restore .env

Add `UDOS_USERNAME` back if needed:
```bash
echo "UDOS_USERNAME='YourName'" >> .env
```

### 3. Test

```bash
python uDOS.py --version
```

---

## Benefits of v1.1.6

### Configuration Benefits

✅ **Single Source of Truth**
- Username in ONE place (user.json)
- No sync issues
- Clear data ownership

✅ **Cleaner .env**
- Only system configuration
- No user data mixed in
- Easier to understand

### Logging Benefits

✅ **Production Ready**
- Flat-file architecture
- Daily rotation
- No database overhead

✅ **Better Performance**
- Faster log writes
- Easier to search
- Automatic cleanup

✅ **Developer Friendly**
- Simple API
- Rich context support
- Backward compatible

---

## Getting Help

If you encounter issues during migration:

1. **Check logs**: `sandbox/logs/errors-*.log`
2. **Run diagnostics**: `python uDOS.py --check`
3. **Review docs**: `wiki/Logging-System.md`
4. **Check variables**: `core/docs/SYSTEM-VARIABLES.md`
5. **GitHub issues**: [uDOS Issues](https://github.com/fredporter/uDOS/issues)

---

## Next Steps

After successful migration:

1. ✅ Review [Logging System](Logging-System.md) documentation
2. ✅ Update custom extensions if needed
3. ✅ Clean old log files: `CLEAN` command in uDOS
4. ✅ Explore new features: `python uDOS.py --version`
5. ✅ Update your extensions to use new logging

---

## Changelog Reference

For complete list of changes, see:
- [CHANGELOG.md](../CHANGELOG.md) - Full changelog
- [README.MD](../README.MD) - v1.1.6 summary
- [SYSTEM-VARIABLES.md](../core/docs/SYSTEM-VARIABLES.md) - Variable reference

---

**Migration complete?** You're now running uDOS v1.1.6 with production-grade logging and clean configuration! 🎉

---

**Updated**: November 28, 2025
**Version**: v1.1.6
