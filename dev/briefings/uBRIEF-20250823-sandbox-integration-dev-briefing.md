# DEV MODE Briefing: Claude Session v2.0 - Sandbox Integration

**Date:** 2025-08-23 (Updated for Sandbox Integration)
**Environment:** VS Code / uDOS Enhanced Dev Mode with Sandbox
**System:** uDOS v2.0 with Complete Sandbox Workflow Integration

## 🎯 Major System Changes (v2.0)
- ✅ **Sandbox Development Environment**: All development now happens in `/sandbox`
- ✅ **Move→Milestone→Mission→Legacy Workflow**: Complete user journey tracking
- ✅ **Centralized Logging**: All logs moved from uMEMORY to `/sandbox/logs/`
- ✅ **Core Function Migration**: backup, logging, session management in `uCORE/core/`
- ✅ **AI Assist Mode**: Context-aware workflow guidance system

## 📁 New File Structure (Keep it Clean!)

### Primary Development Location: `/sandbox`
```bash
/sandbox/
├── dev/                    # 🛠️ Active development files, scripts being worked on
├── temp/                   # 🗑️ Temporary files (auto-cleaned every hour)
├── session/                # 📊 Session tracking and undo/redo
├── workflow/               # 🗺️ User journey management
│   ├── moves/              # Current activities (present)
│   ├── milestones/         # Achievements (progress markers)
│   ├── missions/           # Goals & objectives (future)
│   ├── legacy/             # Impact summaries (austere)
│   └── assist/             # AI assistance data
├── logs/                   # 📋 All system logs (migrated from uMEMORY)
├── experiments/            # 🔬 Experimental features and tests
├── tests/                  # 🧪 Test scripts and validation
└── scripts/                # ⚙️ User utilities and tools
```

### Core Functions Location: `uCORE/core/`
```bash
uCORE/core/
├── backup-restore.sh       # Centralized backup with encryption
├── logging.sh              # Unified logging system
├── session-manager.sh      # Session-based development
├── workflow-manager.sh     # Move→milestone→mission→legacy
├── sandbox.sh              # Unified sandbox command interface
├── backup-handler.sh       # uDATA backup command integration
└── migrate-logs-to-sandbox.sh # Log migration utility
```

### Legacy Dev Directory: `/dev` (Reference Only)
- **Purpose**: Historical reference and roadmaps
- **Status**: No longer used for active development
- **Content**: Existing briefings, roadmaps, templates for reference

## 🚀 New Development Workflow

### 1. **Starting Development Session**
```bash
# Start session (auto-initializes if needed)
sandbox SESSION START

# Check overall status
sandbox STATUS
```

### 2. **Creating Development Files** (No more scripts in random directories!)
```bash
# Create development script
sandbox DEV CREATE my-script.sh

# Create experimental feature
sandbox EXPERIMENT CREATE new-feature

# Create test script
sandbox TEST CREATE validation-tests
```

### 3. **Working with Files**
```bash
# List development files
sandbox DEV LIST

# Run development script
sandbox DEV RUN my-script.sh

# Run all tests
sandbox TEST RUN
```

### 4. **Workflow Tracking** (New!)
```bash
# Log current activity
sandbox WORKFLOW MOVE development "Building user auth system"

# Create achievement milestone
sandbox WORKFLOW MILESTONE "Auth Complete" "Successfully implemented secure login"

# Set future mission
sandbox WORKFLOW MISSION CREATE "Full App" "Build complete web application"

# Get AI assistance
sandbox WORKFLOW ASSIST ENTER development
```

### 5. **Session Management**
```bash
# Create save point
sandbox SESSION SAVE

# Undo last operation
sandbox SESSION UNDO

# End session (compiles daily summary)
sandbox SESSION END
```

## 🎯 File Organization Rules (Keep It Clean!)

### ✅ **DO** - Use Sandbox Structure
- **Development Work**: → `/sandbox/dev/`
- **Temporary Scripts**: → `/sandbox/temp/`
- **Experiments**: → `/sandbox/experiments/`
- **Tests**: → `/sandbox/tests/`
- **User Utils**: → `/sandbox/scripts/`
- **Notes & Summaries**: → `/sandbox/workflow/` (tracked as moves/milestones)

### ❌ **DON'T** - Drop Files Randomly
- ~~Scripts in current directory~~
- ~~Notes scattered in various folders~~
- ~~Utility scripts in random locations~~
- ~~Temporary files left lying around~~
- ~~Development work in production directories~~

### 🧹 **Auto-Cleanup Features**
- **Temp files**: Auto-cleaned every hour
- **Session files**: Archived after 3 days
- **Old logs**: Moved to archived/ after 7 days
- **Daily summaries**: Compiled and moved to uMEMORY/user/{role}/daily-logs/

## 🤖 AI Assist Mode Integration

### Context-Aware Assistance
```bash
# Enter assist mode with focus
sandbox WORKFLOW ASSIST ENTER productivity
sandbox WORKFLOW ASSIST ENTER learning
sandbox WORKFLOW ASSIST ENTER development

# Get status and recommendations
sandbox WORKFLOW ASSIST STATUS

# Exit assist mode
sandbox WORKFLOW ASSIST EXIT
```

### Assist Mode Features
- **Proactive Recommendations**: Based on current activity patterns
- **Goal Suggestions**: Mission and milestone recommendations
- **Learning Guidance**: Skill development tracking
- **Productivity Tips**: Workflow optimization suggestions

## 📊 Enhanced Command Interface

### Sandbox Unified Commands
```bash
# Development
sandbox DEV CREATE <file> [template]    # Create dev file (script/experiment/test)
sandbox DEV LIST                        # List development files
sandbox DEV RUN <file>                   # Run development file
sandbox DEV CLEAN                       # Clean development files

# Testing
sandbox TEST CREATE <name>               # Create test file
sandbox TEST RUN [name]                  # Run test(s) - all if no name
sandbox TEST LIST                        # List test files

# Experiments
sandbox EXPERIMENT CREATE <name>         # Create experiment
sandbox EXPERIMENT RUN <name>            # Run experiment
sandbox EXPERIMENT LIST                  # List experiments

# Session Management
sandbox SESSION START/END               # Manage sessions
sandbox SESSION SAVE/UNDO/REDO         # Session controls
sandbox SESSION HISTORY                # Session timeline

# Workflow Management (NEW!)
sandbox WORKFLOW MOVE <type> <desc>     # Log current activity
sandbox WORKFLOW MILESTONE <title> <desc> # Create milestone
sandbox WORKFLOW MISSION CREATE <title> <desc> # Create mission
sandbox WORKFLOW MISSION COMPLETE <id>  # Complete mission
sandbox WORKFLOW LEGACY                 # View achievements
sandbox WORKFLOW ASSIST ENTER [focus]   # Enter assist mode
sandbox WORKFLOW STATUS                 # Show journey progress

# Environment
sandbox STATUS                          # Complete overview
sandbox SANDBOX INIT/CLEAN/BACKUP      # Environment management
```

### Integration with uDATA Commands
- **BACKUP CREATE/LIST/RESTORE** → Enhanced backup system with encryption
- **SESSION SAVE/UNDO/REDO** → Session-based development with real-time tracking
- All commands accessible through help engine: `help BACKUP`, `help SESSION`

## 🗺️ User Journey Workflow

### **MOVES** (Present Activity - What you're doing now)
- Real-time logging of current development activities
- Context-aware intent detection (development/testing/learning/etc.)
- Session-based undo/redo capability
- Examples: "Building auth system", "Testing API endpoints", "Learning React"

### **MILESTONES** (Achievements - Progress markers)
- Recognition of significant progress points
- Automatic significance calculation (foundational/expertise/completion/innovation)
- Next milestone suggestions
- Examples: "First App Complete", "Testing Mastery", "Deployment Success"

### **MISSIONS** (Goals - Future objectives)
- Goal setting with clear objectives and timelines
- Progress tracking with percentage completion
- AI assist recommendations for completion
- Examples: "Learn Python", "Build Portfolio Site", "Master DevOps"

### **LEGACY** (Impact - Austere summaries)
- Condensed achievement summaries in austere format
- Value created documentation
- Knowledge and skills gained tracking
- Future application suggestions
- Examples: "Learned: Python. Applied OOP. Ready for web frameworks."

## 📋 Development Session Example

```bash
# 1. Start clean development session
sandbox SESSION START

# 2. Create development script (not in random directory!)
sandbox DEV CREATE user-auth.py script

# 3. Log what you're working on
sandbox WORKFLOW MOVE development "Building user authentication system with JWT"

# 4. Work on the script, test it
sandbox DEV RUN user-auth.py
sandbox TEST CREATE auth-validation

# 5. Create milestone when complete
sandbox WORKFLOW MILESTONE "Auth System Complete" "Successfully implemented secure JWT authentication"

# 6. Get AI assistance for next steps
sandbox WORKFLOW ASSIST ENTER development

# 7. End session (auto-compiles daily summary)
sandbox SESSION END
```

## ⚡ Quick Reference

### File Creation (Clean Locations!)
```bash
sandbox DEV CREATE script.sh           # → /sandbox/dev/script.sh
sandbox EXPERIMENT CREATE feature      # → /sandbox/dev/exp-feature.sh
sandbox TEST CREATE validation         # → /sandbox/dev/test-validation.sh
```

### File Organization
- **Active Work**: `/sandbox/dev/` (where you develop)
- **Experiments**: `/sandbox/experiments/` (testing new ideas)
- **Tests**: `/sandbox/tests/` (validation scripts)
- **Utilities**: `/sandbox/scripts/` (helper tools)
- **Temporary**: `/sandbox/temp/` (auto-cleaned)

### Workflow Tracking
```bash
sandbox WORKFLOW MOVE <type> <description>     # Log current activity
sandbox WORKFLOW MILESTONE <title> <desc>      # Mark achievement
sandbox WORKFLOW MISSION CREATE <title> <desc> # Set goal
sandbox WORKFLOW STATUS                         # See progress
```

### Session Management
```bash
sandbox SESSION START          # Begin development session
sandbox SESSION SAVE           # Create save point
sandbox SESSION UNDO/REDO      # Navigate changes
sandbox SESSION END            # End and summarize
```

## 🎯 Key Benefits

### **Clean Development Environment**
- No more scripts scattered in random directories
- Automatic cleanup of temporary files
- Organized structure for all development work
- Session-based development with undo/redo

### **Intelligent Workflow Tracking**
- Tracks your journey from current work to lasting impact
- AI-powered assistance and recommendations
- Progress recognition and goal setting
- Austere legacy summaries for lasting memory

### **Comprehensive Backup & Logging**
- All development work automatically backed up
- Session-based logging with real-time tracking
- Centralized log storage in sandbox
- Role-based access and encryption

### **Integration with Existing System**
- Full compatibility with uDATA commands
- Enhanced backup system with encryption
- Works with existing help engine and documentation
- Progressive enhancement of user experience

---

## 🚨 **Important Migration Notes**

1. **All development work now happens in `/sandbox`** - don't create scripts in random directories
2. **Use `sandbox` commands** for all development operations
3. **Temporary files go in `/sandbox/temp/`** - they auto-clean
4. **Track your work with workflow commands** - helps with progress and AI assistance
5. **Sessions auto-summarize** - daily logs are compiled automatically

**Keep it clean, use the sandbox, track your journey!** 🏖️

---

*Updated briefing for Claude to onboard with v2.0 Sandbox Integration - All development in /sandbox, workflow tracking, AI assist mode, and clean file organization.*
