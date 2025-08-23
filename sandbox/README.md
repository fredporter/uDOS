# uDOS Sandbox Environment - Clean Development Workspace

This is your **primary development workspace** for uDOS. **All development, testing, and experimentation should happen here** - keep the main directories clean!

## 🎯 **Keep It Clean Rule**
**NO MORE scattered scripts, notes, or utilities in random directories!**
Everything has a proper place in the sandbox structure.

## 📁 Structure

- **`dev/`** - Development files, scripts being worked on
- **`temp/`** - Temporary files (auto-cleaned every hour)
- **`session/`** - Session management and logging
- **`workflow/`** - User journey management (moves→milestones→missions→legacy)
- **`logs/`** - All system logs (migrated from uMEMORY)
- **`experiments/`** - Experimental features and tests
- **`tests/`** - Test scripts and validation
- **`scripts/`** - User scripts and utilities

## 🚀 **Quick Start**

### Start Development Session
```bash
sandbox SESSION START
```

### Create Files (Clean Locations!)
```bash
sandbox DEV CREATE my-script.sh           # → /sandbox/dev/my-script.sh
sandbox EXPERIMENT CREATE new-feature     # → /sandbox/dev/exp-new-feature.sh
sandbox TEST CREATE validation            # → /sandbox/dev/test-validation.sh
```

### Track Your Work
```bash
sandbox WORKFLOW MOVE development "Building authentication system"
sandbox WORKFLOW MILESTONE "Auth Complete" "Successfully implemented secure login"
```

## 🗺️ **Workflow Management**

The sandbox uses **move→milestone→mission→legacy** workflow:
- **MOVES**: Current activities (what you're doing now)
- **MILESTONES**: Achievements (progress markers)
- **MISSIONS**: Goals & objectives (future plans)
- **LEGACY**: Impact summaries (austere lasting value)

## 🤖 **AI Assist Mode**

Get context-aware guidance:
```bash
sandbox WORKFLOW ASSIST ENTER development  # For coding guidance
sandbox WORKFLOW ASSIST ENTER learning     # For skill development
sandbox WORKFLOW ASSIST ENTER productivity # For workflow optimization
```

## 📊 **Session Management**

- **Session data tracked in real-time** for undo/redo
- **Daily summaries compiled at session end**
- **Final summaries archived to uMEMORY**
- **Automatic cleanup** of temp files and old logs

## ⚡ **Commands**

Use the **`sandbox`** command for all operations:

### Development
- `sandbox DEV CREATE <file>` - Create development file
- `sandbox DEV RUN <file>` - Run development file
- `sandbox DEV LIST` - List development files

### Testing
- `sandbox TEST CREATE <name>` - Create test
- `sandbox TEST RUN [name]` - Run test(s)
- `sandbox TEST LIST` - List tests

### Experiments
- `sandbox EXPERIMENT CREATE <name>` - Create experiment
- `sandbox EXPERIMENT RUN <name>` - Run experiment
- `sandbox EXPERIMENT LIST` - List experiments

### Session Management
- `sandbox SESSION START/END` - Manage sessions
- `sandbox SESSION SAVE/UNDO/REDO` - Session controls
- `sandbox SESSION HISTORY` - Session timeline

### Workflow Tracking
- `sandbox WORKFLOW MOVE <type> <desc>` - Log current activity
- `sandbox WORKFLOW MILESTONE <title> <desc>` - Create milestone
- `sandbox WORKFLOW MISSION CREATE <title> <desc>` - Create mission
- `sandbox WORKFLOW STATUS` - Show progress

### Environment
- `sandbox STATUS` - Show complete overview
- `sandbox SANDBOX CLEAN` - Clean environment
- `sandbox SANDBOX BACKUP` - Create backup

## 🧹 **Clean Development Habits**

### ✅ **DO**
- Create all development files with `sandbox DEV CREATE`
- Put temporary work in `/sandbox/temp/` (auto-cleans)
- Track significant work with workflow commands
- Use experiments for testing new ideas
- Start/end sessions to track progress

### ❌ **DON'T**
- Create scripts in random directories
- Leave temporary files scattered around
- Work without session management
- Skip workflow tracking for significant work

## 🎯 **Benefits**

- **Organized Development**: No more scattered files
- **Session Tracking**: Full undo/redo with history
- **Progress Monitoring**: Track journey from moves to legacy
- **AI Assistance**: Context-aware guidance
- **Automatic Cleanup**: Temp files and logs auto-managed
- **Backup Integration**: All work automatically backed up

---

**All work is logged and can be undone/redone within the current session.**

**Keep it clean - use the sandbox structure!** 🏖️
