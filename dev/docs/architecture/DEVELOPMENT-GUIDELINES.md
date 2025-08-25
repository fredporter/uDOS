# uDOS v1.4 Development Guidelines & System Organization

## 🎯 Core Principles

### Data Separation Strategy
- **uCORE/**: System code and components (no user data)
- **uMEMORY/**: User data, session data, logs, memory archives
- **sandbox/**: User workspace for experiments and temporary work
- **dev/**: Development framework and tools (core development only)

### Logging Philosophy
```
🚫 OLD: Logs scattered across uCORE, wizard, various directories
✅ NEW: All logs consolidated in uMEMORY/system/logs/
```

**Rationale**: Logs contain user data, session data, and error information that belongs with user memory, not system code.

## 📁 Directory Organization

### uCORE/ (System Code Only)
```
uCORE/
├── system/           # System components & utilities
│   ├── server/       # Server infrastructure
│   ├── error-handler.sh
│   ├── process-manager.sh
│   └── [system files]
├── core/            # Core engine components
├── geo/             # Geographic system
├── launcher/        # System launchers
└── [other system directories]
```

**Rules**:
- ✅ System code, engines, launchers, utilities
- 🚫 NO user data, logs, session data, personal files

### uMEMORY/ (User & Session Data)
```
uMEMORY/
├── system/
│   ├── logs/        # ← ALL system logs here
│   │   ├── errors/
│   │   ├── debug/
│   │   ├── crashes/
│   │   └── network/
│   └── geo/         # Geographic data
├── user/            # User-specific data
├── role/            # Role-specific data
└── logs -> system/logs
```

**Rules**:
- ✅ User data, session data, logs, memory archives
- ✅ Anything that contains personal/session information
- 🚫 NO system code or executables

### sandbox/ (User Workspace)
```
sandbox/
├── experiments/     # User experiments
├── scripts/         # User scripts
├── sessions/        # Session data
├── dev/            # User development work
├── dev-logs/       # Development logs
└── [user workspace]
```

**Rules**:
- ✅ User experiments, temporary work, testing
- ✅ Flushable content (can be cleared between sessions)
- 🚫 NO permanent system components

### dev/ (Development Framework)
```
dev/
├── scripts/         # Core development scripts
├── templates/       # Development templates
├── tools/          # Development tools
├── active/         # Active development work
└── [dev framework]
```

**Rules**:
- ✅ Core development framework and tools
- ✅ Scripts for system development and maintenance
- 🚫 NO user sandbox work (use sandbox/ instead)
- 🚫 NO duplicate sandboxes

## 🚀 Development Workflow

### For Core System Development
```bash
# Work in dev/ for system development
cd dev/active/
./develop-system-feature.sh

# Use dev/scripts/ for development tools
./dev/scripts/cleanup-system-v14.sh
```

### For User Experiments & Testing
```bash
# Work in sandbox/ for experiments
cd sandbox/experiments/
# Create, test, experiment freely

# Logs automatically go to uMEMORY/system/logs/
# Session data stays in sandbox/sessions/
```

### For Memory & Data Management
```bash
# All user/session data in uMEMORY/
cd uMEMORY/
# Check logs: uMEMORY/logs/ (symlink to system/logs/)
# User data: uMEMORY/user/
# Role data: uMEMORY/role/
```

## 🧹 Git Repository Health

### Always Excluded from Git
```gitignore
# Development environments
**/venv/
**/node_modules/
**/__pycache__/
**/cache/

# User data (stays local)
uMEMORY/user/
uMEMORY/role/
sandbox/sessions/
sandbox/experiments/

# Logs and temporary files
**/*.log
**/*.tmp
**/*.cache
```

### Included in Git
```
✅ uCORE/ (system code)
✅ dev/ (development framework)
✅ docs/ (documentation)
✅ extensions/ (core extensions)
✅ README.md, LICENSE, etc.
```

### Regular Cleanup
```bash
# Run system cleanup regularly
./dev/scripts/cleanup-system-v14.sh

# Check git status
git status --porcelain | wc -l  # Should be low

# Check repository size
du -sh .git/  # Should be reasonable
```

## 🔧 Development Best Practices

### Logging Guidelines
```bash
# ✅ Good: All logs go to uMEMORY
echo "Error occurred" >> "$UDOS_ROOT/uMEMORY/system/logs/errors/$(date).log"

# 🚫 Bad: Logs in system directories
echo "Error occurred" >> "$UDOS_ROOT/uCORE/system/some.log"
```

### Data Placement
```bash
# ✅ User data belongs in uMEMORY
user_config="$UDOS_ROOT/uMEMORY/user/config.json"

# ✅ System code belongs in uCORE
system_tool="$UDOS_ROOT/uCORE/core/tools/processor.sh"

# ✅ User experiments belong in sandbox
experiment="$UDOS_ROOT/sandbox/experiments/test-feature/"

# ✅ Development tools belong in dev
dev_script="$UDOS_ROOT/dev/scripts/build-system.sh"
```

### Sandbox Usage
```bash
# ✅ Use sandbox for temporary work
cd sandbox/experiments/
mkdir my-test-feature/
# Work freely, content is flushable

# ✅ Use sandbox for user scripts
cp my-script.sh sandbox/scripts/
chmod +x sandbox/scripts/my-script.sh

# 🚫 Don't put permanent system components in sandbox
```

## 📋 Quick Checks

### Verify Proper Organization
```bash
# Check log location (should be in uMEMORY)
ls -la uMEMORY/system/logs/

# Check no logs in uCORE (should be empty)
find uCORE/ -name "*.log" -o -name "logs" -type d

# Check sandbox structure
ls -la sandbox/

# Check development framework
ls -la dev/
```

### Verify Git Cleanliness
```bash
# Check for large files
find . -size +1M -not -path "./.git/*" | head -10

# Check for development bloat
find . -name "venv" -o -name "__pycache__" -o -name "node_modules"

# Check git status
git status --porcelain | wc -l
```

## 🚨 Common Issues & Fixes

### Issue: Logs in Wrong Location
```bash
# Problem: Logs found in uCORE/
find uCORE/ -name "*.log"

# Fix: Move to proper location
mv uCORE/system/logs/* uMEMORY/system/logs/
```

### Issue: Duplicate Sandboxes
```bash
# Problem: Multiple sandbox directories
ls -la dev/sandbox sandbox/

# Fix: Consolidate to main sandbox
mv dev/sandbox/* sandbox/
rmdir dev/sandbox
```

### Issue: Git Repository Bloat
```bash
# Problem: Large repository size
du -sh .git/

# Fix: Check .gitignore and clean
./dev/scripts/cleanup-system-v14.sh
git status --porcelain
```

## 🎯 Summary

**DO**:
- ✅ Keep system code in uCORE/
- ✅ Keep user/session data in uMEMORY/
- ✅ Use sandbox/ for user experiments
- ✅ Use dev/ for development framework
- ✅ Run cleanup scripts regularly
- ✅ Verify git repository health

**DON'T**:
- 🚫 Put user data in uCORE/
- 🚫 Put system code in uMEMORY/
- 🚫 Create duplicate sandboxes
- 🚫 Let development files bloat git
- 🚫 Scatter logs across multiple directories

This organization ensures clean separation of concerns, proper data management, and a healthy git repository for uDOS v1.4 development.
