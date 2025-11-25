# Configuration Sync Issues - v1.5.3 Resolution Plan

**Version:** 1.0.0
**Created:** 2025-11-25
**Status:** 🔴 **CRITICAL** - Blocks Gemini integration
**Target Fix:** v1.5.3 (Week 9-10)

---

## 🐛 Problem Summary

User profile information (username, API keys) and Gemini API configuration are not properly synchronized across multiple configuration sources, causing authentication failures and user experience issues.

### Observed Symptoms

1. **Dashboard shows wrong username**: `testuser` instead of `Fred`
2. **Gemini API fails**: `.env file not found at /Users/fredbook/Code/uDOS/core/.env`
3. **Configuration inconsistency**: CONFIG command updates don't persist across sessions
4. **User profile mismatch**: Different usernames in different parts of the system

---

## 📋 Configuration Sources Inventory

### 1. `.env` File (MISSING - CRITICAL)
**Expected Location:** `/Users/fredbook/Code/uDOS/.env`
**Actual Location:** Not found (service looks in `core/.env`)
**Purpose:** API keys, installation settings, system configuration
**Contents:**
```env
GEMINI_API_KEY=your_key_here
UDOS_USERNAME=Fred
UDOS_INSTALL_PATH=/Users/fredbook/Code/uDOS
UDOS_VERSION=1.0.31
```

**Issues:**
- ❌ File doesn't exist at expected location
- ❌ `gemini_service.py` looks in wrong path (`core/.env` instead of root `.env`)
- ❌ No fallback mechanism if `.env` is missing
- ❌ No automatic `.env` creation on first run

### 2. `user.json` (Primary Profile)
**Location:** `/Users/fredbook/Code/uDOS/memory/sandbox/user.json`
**Purpose:** User profile, preferences, session state
**Contents:**
```json
{
  "username": "testuser",
  "password": null,
  "location": "Unknown",
  "timezone": "UTC",
  "theme": "default",
  "grid_size": [22, 15]
}
```

**Issues:**
- ⚠️ Shows `testuser` instead of `Fred` (CONFIG command didn't update it)
- ⚠️ Location shows "Unknown" despite interactive update
- ⚠️ Changes made via CONFIG command don't persist
- ⚠️ No locking mechanism (concurrent writes can corrupt)

### 3. Runtime State (In-Memory)
**Location:** `core/uDOS_main.py`, `core/config.py`
**Purpose:** Current session state, active user profile
**Storage:** Python dictionaries, global variables

**Issues:**
- ⚠️ CONFIG command updates runtime state but not file
- ⚠️ Restart loses all changes
- ⚠️ No sync manager between runtime ↔ files
- ⚠️ Multiple sources of truth (can diverge)

### 4. `USER.UDO` (Legacy Config)
**Location:** `/Users/fredbook/Code/uDOS/data/USER.UDO`
**Purpose:** Legacy user profile format
**Status:** Deprecated (replaced by user.json)

**Issues:**
- ⚠️ Still referenced in some code paths
- ⚠️ May conflict with user.json
- ⚠️ Should be migrated or removed

---

## 🔍 Code Analysis - Data Flow

### Startup Sequence
```
1. start_udos.sh → Python check → Virtual env activation
2. uDOS.py → core/uDOS_main.py
3. uDOS_startup.py → System checks
4. Load configuration:
   - core/config.py → Read user.json
   - core/services/gemini_service.py → Read .env (FAILS - file not found)
5. Initialize TUI → Display dashboard (shows stale data)
```

### Configuration Update Flow (BROKEN)
```
User types: CONFIG → User Profile → Username
↓
configuration_handler.py updates runtime state
↓
❌ MISSING: Write to user.json
❌ MISSING: Write to .env (if UDOS_USERNAME changed)
↓
Restart uDOS → Old username reappears
```

### Gemini API Authentication Flow (BROKEN)
```
User types: OK ASK "question"
↓
assistant_handler.py → gemini_service.py
↓
gemini_service.py looks for .env at: core/.env
↓
❌ File not found (should be /Users/fredbook/Code/uDOS/.env)
↓
Error: ".env file not found at /Users/fredbook/Code/uDOS/core/.env"
```

---

## 🗺️ File Locations Map

```
uDOS/
├── .env                            ← MISSING (should be here)
├── core/
│   ├── .env                        ← WRONG (service looks here)
│   ├── config.py                   ← Loads user.json
│   ├── services/
│   │   └── gemini_service.py       ← Loads .env (wrong path)
│   └── commands/
│       └── configuration_handler.py ← Updates runtime only
├── data/
│   └── USER.UDO                    ← Legacy (deprecated)
└── memory/
    └── sandbox/
        └── user.json               ← Primary profile (stale data)
```

---

## 🔧 Root Causes

### 1. **No Unified Configuration Manager**
- Multiple files read independently
- No central authority for configuration
- No synchronization between sources
- Changes in one place don't propagate

### 2. **Incorrect .env Path**
```python
# core/services/gemini_service.py (LINE 19)
self.env_path = env_path or Path(__file__).parent.parent / '.env'
# Resolves to: /Users/fredbook/Code/uDOS/core/.env ❌
# Should be:    /Users/fredbook/Code/uDOS/.env ✅
```

### 3. **Missing Persistence Layer**
```python
# core/commands/configuration_handler.py (CONFIG command)
# Updates runtime state:
state['user']['username'] = new_username
# ❌ MISSING: Write to user.json
# ❌ MISSING: Write to .env if needed
```

### 4. **No Configuration Validation**
- No checks for required fields (GEMINI_API_KEY)
- No type validation (username must be string)
- No format validation (.env syntax, JSON schema)
- No corruption detection

---

## ✅ Resolution Plan (v1.5.3)

### Phase 1: Fix .env Path (Week 9 - Day 1)

**1.1 Correct gemini_service.py Path**
```python
# BEFORE (core/services/gemini_service.py:19)
self.env_path = env_path or Path(__file__).parent.parent / '.env'

# AFTER
self.env_path = env_path or Path(__file__).parent.parent.parent / '.env'
# Resolves to: /Users/fredbook/Code/uDOS/.env ✅
```

**1.2 Create .env Template**
```python
# core/uDOS_startup.py - Add to system checks
def check_env_file():
    env_path = Path('/Users/fredbook/Code/uDOS/.env')
    if not env_path.exists():
        create_default_env(env_path)

def create_default_env(path):
    content = """# uDOS Configuration
GEMINI_API_KEY=your_key_here
UDOS_USERNAME=user
UDOS_INSTALL_PATH={install_path}
UDOS_VERSION={version}
""".format(
        install_path=os.getcwd(),
        version=get_version()
    )
    path.write_text(content)
    print(f"✅ Created .env template at {path}")
    print("   Please edit with your GEMINI_API_KEY")
```

**1.3 Add .env to .gitignore**
```gitignore
# Environment variables (contains secrets)
.env
core/.env
*.env.local
```

### Phase 2: Unified Configuration Manager (Week 9 - Day 2-3)

**2.1 Create ConfigManager Class**
```python
# core/config/config_manager.py (NEW FILE)
from pathlib import Path
import json
from typing import Any, Dict

class ConfigManager:
    """Unified configuration manager - single source of truth"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.env_path = base_path / '.env'
        self.user_json_path = base_path / 'memory' / 'sandbox' / 'user.json'

        # In-memory cache (loaded once, synced on changes)
        self._config = {}
        self.load_all()

    def load_all(self):
        """Load configuration from all sources with priority"""
        # 1. Load defaults
        self._config = self.get_defaults()

        # 2. Load .env (system settings)
        self.load_env()

        # 3. Load user.json (user profile)
        self.load_user_json()

    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any, persist=True):
        """Set configuration value and optionally persist"""
        self._config[key] = value

        if persist:
            self.save()

    def save(self):
        """Save configuration to appropriate files"""
        # Save .env changes
        self.save_env()

        # Save user.json changes
        self.save_user_json()

    def load_env(self):
        """Load .env file"""
        if not self.env_path.exists():
            return

        with open(self.env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    self._config[key] = value

    def save_env(self):
        """Save .env file"""
        lines = []
        lines.append("# uDOS Configuration")
        lines.append(f"GEMINI_API_KEY={self._config.get('GEMINI_API_KEY', '')}")
        lines.append(f"UDOS_USERNAME={self._config.get('username', 'user')}")
        lines.append(f"UDOS_INSTALL_PATH={self.base_path}")

        self.env_path.write_text('\n'.join(lines))

    def load_user_json(self):
        """Load user.json file"""
        if not self.user_json_path.exists():
            return

        with open(self.user_json_path) as f:
            user_data = json.load(f)
            self._config.update(user_data)

    def save_user_json(self):
        """Save user.json file"""
        user_data = {
            'username': self._config.get('username', 'user'),
            'password': self._config.get('password'),
            'location': self._config.get('location', 'Unknown'),
            'timezone': self._config.get('timezone', 'UTC'),
            'theme': self._config.get('theme', 'default'),
            'grid_size': self._config.get('grid_size', [22, 15])
        }

        with open(self.user_json_path, 'w') as f:
            json.dump(user_data, f, indent=2)
```

**2.2 Integrate ConfigManager**
```python
# core/uDOS_main.py
from core.config.config_manager import ConfigManager

# Global config manager
config_manager = ConfigManager(Path(__file__).parent.parent)

def get_username():
    return config_manager.get('username', 'user')

def set_username(username: str):
    config_manager.set('username', username, persist=True)
```

**2.3 Update All Config Access**
```python
# Replace all direct config access:
# BEFORE
user_json = json.load(open('memory/sandbox/user.json'))
username = user_json['username']

# AFTER
from core.uDOS_main import config_manager
username = config_manager.get('username')
```

### Phase 3: Fix Configuration Commands (Week 9 - Day 4)

**3.1 Update configuration_handler.py**
```python
# core/commands/configuration_handler.py
from core.uDOS_main import config_manager

def handle_config_username(new_username: str):
    # Update in-memory AND persist to files
    config_manager.set('username', new_username, persist=True)

    # Also update .env if UDOS_USERNAME is used
    config_manager.set('UDOS_USERNAME', new_username, persist=True)

    print(f"✅ Username updated to: {new_username}")
    print(f"   Saved to: user.json + .env")
```

**3.2 Add Config Sync Validator**
```python
# core/commands/configuration_handler.py
def validate_config_sync():
    """Check if all config sources are in sync"""
    issues = []

    # Check .env vs user.json username
    env_user = config_manager.get('UDOS_USERNAME')
    json_user = config_manager.get('username')

    if env_user != json_user:
        issues.append(f".env username ({env_user}) != user.json ({json_user})")

    # Check for missing required fields
    if not config_manager.get('GEMINI_API_KEY'):
        issues.append("GEMINI_API_KEY not set in .env")

    return issues

def repair_config_sync():
    """Auto-repair configuration sync issues"""
    issues = validate_config_sync()

    if not issues:
        print("✅ Configuration is in sync")
        return

    print("⚠️  Configuration sync issues detected:")
    for issue in issues:
        print(f"   - {issue}")

    # Auto-repair
    config_manager.save()  # Force write all files
    print("✅ Configuration repaired")
```

### Phase 4: Testing & Validation (Week 10)

**4.1 Create Test Suite**
```python
# core/tests/test_config_sync.py
import pytest
from core.config.config_manager import ConfigManager

def test_env_path_correct():
    """Test .env is at root, not in core/"""
    cm = ConfigManager(Path('/Users/fredbook/Code/uDOS'))
    assert cm.env_path == Path('/Users/fredbook/Code/uDOS/.env')

def test_username_sync():
    """Test username sync across .env and user.json"""
    cm = ConfigManager(Path('/Users/fredbook/Code/uDOS'))

    # Set username
    cm.set('username', 'TestUser', persist=True)

    # Reload from files
    cm.load_all()

    # Check both sources match
    assert cm.get('username') == 'TestUser'
    assert cm.get('UDOS_USERNAME') == 'TestUser'

def test_gemini_api_key():
    """Test Gemini API key is accessible"""
    cm = ConfigManager(Path('/Users/fredbook/Code/uDOS'))

    # Should exist (even if placeholder)
    api_key = cm.get('GEMINI_API_KEY')
    assert api_key is not None
    assert len(api_key) > 0
```

**4.2 Manual Testing Checklist**
- [ ] Start fresh uDOS → .env created automatically
- [ ] CONFIG → Update username → Restart → Username persists
- [ ] CONFIG → Update location → Restart → Location persists
- [ ] DASH → All user info matches CONFIG
- [ ] OK ASK → Gemini API connects (with valid key)
- [ ] REPAIR → Config sync validation runs
- [ ] Multiple CONFIG changes → All persist correctly

---

## 📊 Success Metrics

### Before (v1.4.0)
- ❌ .env file missing
- ❌ CONFIG changes don't persist
- ❌ Dashboard shows wrong user info
- ❌ Gemini API fails to connect
- ❌ 4 different config sources (inconsistent)

### After (v1.5.3)
- ✅ .env created automatically on first run
- ✅ All CONFIG changes persist across restarts
- ✅ Dashboard shows correct user info
- ✅ Gemini API connects successfully
- ✅ Single source of truth (ConfigManager)
- ✅ 30+ tests validating sync integrity

---

## 🚀 Migration Guide (v1.4.0 → v1.5.3)

### For Users

**1. Backup Existing Config**
```bash
# Backup old user.json
cp memory/sandbox/user.json memory/sandbox/user.json.backup
```

**2. Run uDOS v1.5.3**
```bash
./start_udos.sh
# .env will be created automatically
# user.json will be validated and repaired
```

**3. Configure Gemini API**
```bash
# Edit .env file
nano .env

# Add your API key:
GEMINI_API_KEY=your_actual_key_here
```

**4. Verify Configuration**
```
uDOS> CONFIG
# Check all settings are correct

uDOS> DASH
# Verify user info matches

uDOS> OK ASK "test"
# Should connect to Gemini
```

### For Developers

**1. Update Code to Use ConfigManager**
```python
# OLD
user_json = json.load(open('memory/sandbox/user.json'))
username = user_json['username']

# NEW
from core.uDOS_main import config_manager
username = config_manager.get('username')
```

**2. Run Migration Script**
```bash
python core/scripts/migrate_config_v1_5_3.py
# Converts old config format to new unified system
```

**3. Run Test Suite**
```bash
pytest core/tests/test_config_sync.py -v
# Verify all config sync tests pass
```

---

## 📚 Related Documentation

- `wiki/Configuration.md` - User configuration guide
- `dev/planning/ROADMAP.MD` - v1.5.3 timeline
- `QUICK-START.md` - First-run configuration
- `.env.example` - Template for environment variables

---

**Status:** 📋 Documented, ready for implementation in v1.5.3
**Priority:** 🔴 CRITICAL (blocks Gemini integration)
**Est. Time:** 3-4 days (Week 9)
**Tests Required:** 30+ config sync tests
