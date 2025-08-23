# 🏖️ Sandbox Development Migration Guide

**Quick Guide for Transitioning to Sandbox-Based Development**

## 🎯 **Before vs After**

### ❌ **OLD Way (Don't do this anymore!)**
```bash
# Scattered files everywhere
./some-script.sh                    # Random directory
./temp-test.py                      # Current directory
./utils/helper.sh                   # Random utils folder
./notes.md                          # Floating notes
./experiment.js                     # Loose experiments
```

### ✅ **NEW Way (Clean sandbox structure)**
```bash
# Everything organized in sandbox
sandbox DEV CREATE some-script.sh           # → /sandbox/dev/some-script.sh
sandbox DEV CREATE temp-test.py             # → /sandbox/dev/temp-test.py
sandbox DEV CREATE helper.sh script         # → /sandbox/dev/helper.sh
sandbox WORKFLOW MOVE development "notes"   # → Tracked in workflow
sandbox EXPERIMENT CREATE experiment        # → /sandbox/dev/exp-experiment.js
```

## 🚀 **Quick Start Commands**

### 1. **Initialize Sandbox** (One-time setup)
```bash
./uCORE/core/sandbox.sh SANDBOX INIT
```

### 2. **Start Development Session**
```bash
sandbox SESSION START
```

### 3. **Create Development Files** (Instead of random scripts)
```bash
# Replace: touch my-script.sh
sandbox DEV CREATE my-script.sh

# Replace: nano temp-test.py
sandbox DEV CREATE temp-test.py

# Replace: creating files in current directory
sandbox EXPERIMENT CREATE new-feature
```

### 4. **Track Your Work** (New workflow feature)
```bash
# Log what you're doing
sandbox WORKFLOW MOVE development "Building user authentication"

# Mark achievements
sandbox WORKFLOW MILESTONE "First API" "Successfully created REST API"
```

## 📁 **File Migration Examples**

### Scripts & Utilities
```bash
# OLD: ./scripts/backup.sh
# NEW: Move to sandbox and track
mv ./scripts/backup.sh /sandbox/scripts/
sandbox WORKFLOW MOVE utility "Moved backup script to sandbox"
```

### Development Work
```bash
# OLD: Working in random directories
# NEW: Use sandbox dev space
sandbox DEV CREATE my-project.py
sandbox DEV RUN my-project.py
```

### Temporary Files
```bash
# OLD: temp files everywhere
# NEW: Use temp directory (auto-cleaned)
sandbox DEV CREATE temp-analysis.sh
# File goes to /sandbox/temp/ and auto-cleans
```

### Experiments
```bash
# OLD: experiment-*.sh files scattered
# NEW: Organized experiments
sandbox EXPERIMENT CREATE api-test
sandbox EXPERIMENT CREATE performance-check
sandbox EXPERIMENT LIST  # See all experiments
```

## 🎯 **Workflow Integration Examples**

### Example 1: Building a Feature
```bash
# Start session
sandbox SESSION START

# Log current work
sandbox WORKFLOW MOVE development "Building user login system"

# Create development files
sandbox DEV CREATE login.py
sandbox TEST CREATE login-tests

# Work on files
sandbox DEV RUN login.py
sandbox TEST RUN login-tests

# Mark milestone when complete
sandbox WORKFLOW MILESTONE "Login Complete" "User authentication working"

# End session
sandbox SESSION END
```

### Example 2: Learning New Technology
```bash
# Start session
sandbox SESSION START

# Set learning mission
sandbox WORKFLOW MISSION CREATE "Learn React" "Master React fundamentals and build sample app"

# Log learning activities
sandbox WORKFLOW MOVE learning "Studying React components"

# Create experimental files
sandbox EXPERIMENT CREATE react-component
sandbox EXPERIMENT CREATE react-hooks

# Enter assist mode for learning guidance
sandbox WORKFLOW ASSIST ENTER learning

# Mark progress
sandbox WORKFLOW MILESTONE "React Basics" "Understand components, props, and state"
```

## 🧹 **Clean Development Habits**

### ✅ **DO**
- Use `sandbox DEV CREATE` for all development files
- Put temporary work in `/sandbox/temp/` (auto-cleans)
- Track significant work with `sandbox WORKFLOW MOVE`
- Create milestones for achievements
- Use experiments for testing new ideas
- Start/end sessions to track progress

### ❌ **DON'T**
- Create scripts in random directories
- Leave temporary files scattered around
- Work without tracking in workflow system
- Skip session management
- Put utilities in random folders

## 🤖 **AI Assist Integration**

### Get Smart Recommendations
```bash
# Enter assist mode for your focus area
sandbox WORKFLOW ASSIST ENTER productivity    # For workflow optimization
sandbox WORKFLOW ASSIST ENTER learning       # For skill development
sandbox WORKFLOW ASSIST ENTER development    # For coding guidance

# Check assist status
sandbox WORKFLOW ASSIST STATUS

# Exit when done
sandbox WORKFLOW ASSIST EXIT
```

### Assist Mode Benefits
- **Context-aware suggestions** based on your activity
- **Goal recommendations** for missions and milestones
- **Learning guidance** for skill development
- **Productivity tips** for workflow optimization

## 📊 **Status Monitoring**

### Check Overall Status
```bash
sandbox STATUS                    # Complete overview
sandbox WORKFLOW STATUS          # Journey progress
sandbox SESSION STATUS           # Current session info
```

### View Progress
```bash
sandbox WORKFLOW LEGACY          # See achievements
sandbox DEV LIST                 # Development files
sandbox TEST LIST                # Test files
sandbox EXPERIMENT LIST          # Experiments
```

## ⚡ **Quick Reference Card**

```bash
# SESSION MANAGEMENT
sandbox SESSION START/END        # Manage sessions
sandbox SESSION SAVE/UNDO/REDO  # Session controls

# FILE CREATION (Clean locations!)
sandbox DEV CREATE <file>        # Development file
sandbox EXPERIMENT CREATE <name> # Experiment
sandbox TEST CREATE <name>       # Test file

# WORKFLOW TRACKING
sandbox WORKFLOW MOVE <type> <desc>     # Log activity
sandbox WORKFLOW MILESTONE <title>      # Mark achievement
sandbox WORKFLOW MISSION CREATE <title> # Set goal
sandbox WORKFLOW ASSIST ENTER <focus>   # Get AI help

# STATUS & MONITORING
sandbox STATUS                   # Everything
sandbox WORKFLOW STATUS          # Journey progress
sandbox DEV LIST                 # Development files
```

## 🎉 **Benefits of New System**

1. **Organized Development**: No more scattered files
2. **Session Tracking**: Undo/redo with full history
3. **Progress Monitoring**: Track your journey from moves to legacy
4. **AI Assistance**: Context-aware guidance and recommendations
5. **Automatic Cleanup**: Temp files and old logs auto-managed
6. **Backup Integration**: All work automatically backed up
7. **Clean Environment**: Structured workspace for productivity

---

**Remember: Keep it clean, use the sandbox, track your journey!** 🏖️

*Start every development session with `sandbox SESSION START` and create all files with `sandbox DEV CREATE` - your future self will thank you!*
