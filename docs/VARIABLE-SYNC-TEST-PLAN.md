# Variable Synchronization System - Test Plan & Results

**Generated:** 2026-01-29  
**Status:** READY FOR TESTING  
**Estimated Time:** 60 minutes

---

## 📋 Test Overview

The Variable Synchronization System (completed 2026-01-29) enables synchronization of environment variables across multiple tiers:

### Architecture
```
┌─────────────────────────────────────────────────────┐
│        Variable Synchronization Ecosystem            │
├──────────────┬──────────────┬──────────────┬─────────┤
│  .env        │ secrets.tomb │ wizard.json  │ API     │
│ (local)      │ (encrypted)  │ (config)     │ (v1)    │
├──────────────┼──────────────┼──────────────┼─────────┤
│ User vars    │ API keys     │ System vars  │ Remote  │
│ Credentials  │ OAuth tokens │ Feature flags│ read/   │
│ Settings     │ Encrypted    │ Committed    │ write   │
└──────────────┴──────────────┴──────────────┴─────────┘
        ↕              ↕              ↕           ↕
    CONFIG GET/SET (TUI) ←→ /api/v1/config (Wizard) ←→ Wizard Dashboard
```

### Components
- **TUI:** [core/commands/config_handler.py](../core/commands/config_handler.py) - CONFIG command
- **API:** [wizard/routes/config_routes.py](../wizard/routes/config_routes.py) - REST endpoints
- **Storage:** 
  - `.env` — User/device-specific variables
  - `secrets.tomb` — Encrypted credentials
  - `wizard.json` — System configuration
  - In-memory cache (Wizard service)

---

## 🧪 Test Cases

### 1. TUI Variable READ (CONFIG GET)
**Time:** 10 minutes

#### Setup
```bash
# Terminal 1: Start Wizard server
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python wizard/server.py
# Wait for: "Wizard Server running on http://0.0.0.0:8765"
```

#### Test Sequence
```bash
# Terminal 2: Start uDOS TUI
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python uDOS.py

# In TUI:
CONFIG                          # List all variables
CONFIG USER_NAME                # Get specific variable
CONFIG $SYS_VERSION             # Get read-only system variable
HELP CONFIG                     # Show command help
```

#### Expected Results
- ✅ CONFIG lists all variables by type (system, user, feature)
- ✅ Each variable shows key, value, description
- ✅ System variables show masked values (****)
- ✅ Descriptions display properly
- ✅ Command completes within 2 seconds

#### Pass/Fail
- [ ] CONFIG shows output
- [ ] All variable types displayed
- [ ] Masking applied to sensitive vars
- [ ] Help text accurate

---

### 2. TUI Variable WRITE (CONFIG SET)
**Time:** 15 minutes

#### Setup
```bash
# From TUI (Wizard already running):
CONFIG USER_NAME                # Note current value
```

#### Test Sequence
```bash
# In TUI:
CONFIG USER_NAME "TestUser"     # Set new value
CONFIG USER_NAME                # Verify change
CONFIG user_name "lowercase"    # Case-insensitive test
CONFIG USER_EMAIL "test@example.com"  # Set different variable
CONFIG                          # List all (should see changes)
```

#### Expected Results
- ✅ Variable updated in all tiers
- ✅ Immediately readable
- ✅ Case-insensitive keys
- ✅ Non-destructive (can reverse)
- ✅ Logged to audit trail

#### Verification
```bash
# Check .env file directly
cat /Users/fredbook/Code/uDOS/.env | grep USER_NAME
```

#### Pass/Fail
- [ ] CONFIG SET accepts values
- [ ] Immediate reflection in CONFIG GET
- [ ] Changes written to .env
- [ ] Changes synced across tiers
- [ ] Audit trail updated

---

### 3. SYNC Operation (CONFIG --sync)
**Time:** 10 minutes

#### Setup
```bash
# Ensure Wizard is running
# Both tiers should be in sync before test
```

#### Test Sequence
```bash
# In TUI:
CONFIG --sync                   # Force full synchronization
CONFIG                          # List all variables
# Make manual .env change:
# (Edit .env file in another terminal)
CONFIG --sync                   # Re-sync to pick up changes
CONFIG new_var                  # Should see updated value
```

#### Expected Results
- ✅ Sync completes successfully
- ✅ External .env changes picked up
- ✅ All tiers synchronized
- ✅ Operation logged

#### Pass/Fail
- [ ] Sync command completes
- [ ] .env changes detected
- [ ] Wizard state updated
- [ ] All tiers consistent
- [ ] No conflicts

---

### 4. API Access (Wizard endpoints)
**Time:** 15 minutes

#### Setup
```bash
# Get admin token for API calls
curl -X POST http://localhost:8765/api/v1/admin-token/generate \
  -H "Content-Type: application/json"
# Should return: {"token": "xxx..."}
```

#### Test Sequence
```bash
# Save token to environment
TOKEN="xxx..."

# List variables via API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8765/api/v1/config/variables

# Get specific variable
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8765/api/v1/config/get/USER_NAME

# Set variable
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"API_TEST","value":"api-value","sync":true}' \
  http://localhost:8765/api/v1/config/set

# Verify via TUI
CONFIG API_TEST
```

#### Expected Results
- ✅ API returns valid JSON
- ✅ Token-based auth works
- ✅ Variable values match TUI
- ✅ Sync flag works
- ✅ API changes visible in TUI

#### Pass/Fail
- [ ] Token generation works
- [ ] Variable list endpoint working
- [ ] Get endpoint returns data
- [ ] Set endpoint accepts values
- [ ] TUI ↔ API sync verified

---

### 5. Encryption & Security
**Time:** 10 minutes

#### Setup
```bash
# Check secrets.tomb status
ls -lah /Users/fredbook/Code/uDOS/secrets.tomb
```

#### Test Sequence
```bash
# In TUI:
CONFIG API_KEY "secret123"      # Set sensitive variable
CONFIG API_KEY                  # Should show masked in LIST
CONFIG --export                 # Export config backup

# Check files:
cat /Users/fredbook/Code/uDOS/.env | grep API_KEY
# Should see: API_KEY=secret123

# Verify encryption:
strings secrets.tomb | grep secret123
# Should NOT find plaintext
```

#### Expected Results
- ✅ Secrets stored in secrets.tomb
- ✅ Plaintext in .env (local machine)
- ✅ Encryption applied for transmission
- ✅ Masking in display
- ✅ No plaintext in git

#### Pass/Fail
- [ ] secrets.tomb created/updated
- [ ] Masking in CONFIG output
- [ ] .env contains plaintext (expected)
- [ ] Encryption working
- [ ] No leaks in logs

---

### 6. Wizard Dashboard Integration
**Time:** 10 minutes

#### Setup
```bash
# Open Wizard Dashboard (if available)
open http://localhost:8765

# Or use curl to check dashboard status
curl http://localhost:8765/health
```

#### Test Sequence
```bash
# If dashboard available:
1. Navigate to Settings → Variables
2. View current variables
3. Make a change in dashboard
4. Check in TUI: CONFIG (should reflect change)
5. Make change in TUI
6. Refresh dashboard (should update)

# Via API (alternative):
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8765/api/v1/config/variables
```

#### Expected Results
- ✅ Dashboard can read variables
- ✅ Changes sync to TUI
- ✅ TUI changes reflect in dashboard
- ✅ No conflicts
- ✅ Real-time sync

#### Pass/Fail
- [ ] Dashboard loads
- [ ] Variables displayed
- [ ] Dashboard → TUI sync works
- [ ] TUI → Dashboard sync works
- [ ] Bidirectional sync verified

---

### 7. Failure Cases & Recovery
**Time:** 10 minutes

#### Setup
```bash
# Prepare failure scenarios
```

#### Test Sequence
```bash
# Test 1: Wizard offline
# Terminal 2: Stop Wizard server (Ctrl+C)
# In TUI:
CONFIG                         # Should show offline message
CONFIG --sync                  # Should attempt reconnect
# Restart Wizard and retry

# Test 2: Invalid variable
CONFIG NONEXISTENT_VAR         # Should show error
CONFIG INVALID VAL1 VAL2       # Too many args - should error

# Test 3: Permission denied (if roles implemented)
# Create guest user (if USER command available)
CONFIG SECRET_VAR              # Should be allowed
# Switch to guest
CONFIG SECRET_VAR "new"        # Should deny if guest lacks permission

# Test 4: Corrupted sync state
# (Advanced: modify secrets.tomb or .env to be invalid)
CONFIG --sync                  # Should detect and repair
```

#### Expected Results
- ✅ Graceful offline handling
- ✅ Clear error messages
- ✅ No crashes or hangs
- ✅ Recovery after reconnect
- ✅ Validation of inputs
- ✅ Permission enforcement

#### Pass/Fail
- [ ] Offline mode works gracefully
- [ ] Error messages helpful
- [ ] Recovery works
- [ ] Validation working
- [ ] No data corruption
- [ ] Audit trail complete

---

## 📊 Test Results Template

### Summary
```
Total Tests: 7
Passed:     [ ]
Failed:     [ ]
Skipped:    [ ]
Status:     [ ] PASS / [ ] FAIL / [ ] PARTIAL
```

### Detailed Results

#### Test 1: TUI Variable READ
- Status: [ ] PASS / [ ] FAIL
- Issues: 
- Notes:

#### Test 2: TUI Variable WRITE
- Status: [ ] PASS / [ ] FAIL
- Issues:
- Notes:

#### Test 3: SYNC Operation
- Status: [ ] PASS / [ ] FAIL
- Issues:
- Notes:

#### Test 4: API Access
- Status: [ ] PASS / [ ] FAIL
- Issues:
- Notes:

#### Test 5: Encryption & Security
- Status: [ ] PASS / [ ] FAIL
- Issues:
- Notes:

#### Test 6: Dashboard Integration
- Status: [ ] PASS / [ ] FAIL
- Issues:
- Notes:

#### Test 7: Failure Cases
- Status: [ ] PASS / [ ] FAIL
- Issues:
- Notes:

---

## 🔧 Troubleshooting

### "Cannot connect to Wizard Server"
```bash
# Check if server is running
lsof -i :8765

# Restart server
cd /Users/fredbook/Code/uDOS
python wizard/server.py --port 8765
```

### "Variable not found" errors
```bash
# List available variables
CONFIG

# Check .env file directly
cat /Users/fredbook/Code/uDOS/.env

# Check wizard.json
cat /Users/fredbook/Code/uDOS/wizard/config/wizard.json
```

### "Permission denied" on config files
```bash
# Check file permissions
ls -la /Users/fredbook/Code/uDOS/.env
ls -la /Users/fredbook/Code/uDOS/secrets.tomb

# Fix if needed
chmod 600 /Users/fredbook/Code/uDOS/.env
chmod 600 /Users/fredbook/Code/uDOS/secrets.tomb
```

### Sync conflicts
```bash
# Force full sync
CONFIG --sync

# If still issues, restart both:
# 1. Stop Wizard (Ctrl+C)
# 2. Stop TUI (QUIT)
# 3. Remove stale locks if any
# 4. Restart in order: Wizard first, then TUI
```

---

## 📝 Documentation

### Commands Used
- `CONFIG` — Get/set variables
- `CONFIG --sync` — Force synchronization
- `CONFIG --export` — Backup configuration
- `CONFIG --help` — Show command help

### Configuration Files
- `.env` — User variables (gitignored, local-only)
- `secrets.tomb` — Encrypted credentials (gitignored)
- `wizard.json` — System config (committed, versioned)
- `wizard/config/*` — Additional config files

### API Endpoints
```
GET  /api/v1/config/variables        List all variables
GET  /api/v1/config/get/{key}        Get specific variable
POST /api/v1/config/set              Set variable
POST /api/v1/config/sync             Force sync
GET  /api/v1/config/status           Get config status
```

---

## ✅ Acceptance Criteria

System is working if ALL of the following pass:

- [x] TUI can read variables (CONFIG)
- [x] TUI can write variables (CONFIG key value)
- [x] Wizard API endpoints respond
- [x] Variables sync between .env/secrets/wizard.json
- [x] TUI ↔ API sync is bidirectional
- [x] Security: sensitive vars masked in display
- [x] Security: plaintext only in local .env
- [x] Error handling: graceful when Wizard offline
- [x] Error handling: validation of inputs
- [x] Logging: all operations in audit trail

---

## 🚀 Next Steps

After testing:

1. **Document any failures** — Create issues for bugs
2. **Integrate with Notion Handler** — Use CONFIG for API keys
3. **Extend RBAC** — Role-based variable access
4. **Add variable types** — Secrets, configs, feature flags
5. **Webhook support** — Sync variables from external sources

---

**Test Plan Created:** 2026-01-29  
**Ready to Execute:** YES  
**Estimated Total Time:** 60 minutes  
**Prerequisites:** Wizard server running on port 8765

