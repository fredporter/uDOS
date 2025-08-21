# uDEV-eaeae41f-Dev-Mode-Framework
**Created:** 2025-08-21 15:21  
**Type:** Development Framework  
**Status:** Active Development Session  
**Location:** wizard/notes/

---

## 🎯 DEV MODE FRAMEWORK SPECIFICATION

### Core Principle: VS Code/Claude/Agent Sessions = Dev Mode
When working in VS Code with Claude/AI assistance, we are inherently in **development mode** and should:
- Operate from `wizard/` root folder as primary workspace
- Use proper uHEX filename protocols for all development artifacts
- Maintain development notes, roadmaps, and workflows in `wizard/notes/`
- Track all architectural decisions and implementation progress

---

## 📁 DEV MODE DIRECTORY STRUCTURE

### Wizard Root Organization
```
wizard/
├── notes/                       # Development session logs (uHEX naming)
│   ├── uDEV-XXXXXXXX-*.md      # Development session notes
│   ├── uLOG-XXXXXXXX-*.md      # Implementation logs
│   ├── uDOC-XXXXXXXX-*.md      # Architecture documentation
│   └── uTASK-XXXXXXXX-*.md     # Task tracking and planning
├── workflows/                   # Development workflows
│   ├── dev-mode-detection.sh   # Auto-detect VS Code/AI sessions
│   ├── uhex-generator.sh       # uHEX filename generation
│   └── session-logger.sh       # Development session tracking
├── tools/                       # Development utilities
│   ├── file-organizer.sh       # Auto-organize dev files
│   ├── roadmap-manager.sh      # Roadmap tracking
│   └── implementation-tracker.sh # Progress tracking
└── templates/                   # Development templates
    ├── dev-session.md          # Development session template
    ├── architecture-proposal.md # Architecture proposal template
    └── implementation-log.md   # Implementation log template
```

---

## 🔧 FILENAME PROTOCOLS

### Dev Mode Naming Convention (Date-Based)
All development artifacts use YYYYMMDD date format instead of uHEX:

#### Development Session Files
- `uDEV-YYYYMMDD-SessionName.md` - Development session notes
- `uLOG-YYYYMMDD-ImplementationName.md` - Implementation logs
- `uDOC-YYYYMMDD-DocumentName.md` - Architecture/design documents
- `uTASK-YYYYMMDD-TaskName.md` - Task planning and tracking
- `uROAD-YYYYMMDD-RoadmapName.md` - Roadmap and milestone tracking

#### Examples
- `uDEV-20250821-v1.3.1-Architecture-Implementation.md`
- `uLOG-20250821-Virtual-Environment-Setup.md`
- `uDOC-20250821-Command-Interface-Design.md`
- `uTASK-20250821-Script-Consolidation.md`
- `uROAD-20250821-Q4-2025-Development-Plan.md`

### Production Mode vs Dev Mode
- **Production Mode:** `PREFIX-UHEX-YYYYMMDD-Description.md` (8-char hex + date)
- **Dev Mode:** `PREFIX-YYYYMMDD-Description.md` (date only, simpler)
- **Error Fallback:** Always defaults to YYYYMMDD format when uHEX generation fails

---

## 🤖 DEV MODE DETECTION

### Automatic Detection Criteria
Development mode is active when:
1. **VS Code Environment:** Working in VS Code editor
2. **AI Assistance:** Claude/GitHub Copilot active
3. **Repository Context:** Working in uDOS repository
4. **File Editing:** Making changes to core system files
5. **Architecture Work:** Implementing new features or refactoring

### Environment Variables
```bash
export UDOS_DEV_MODE="true"
export UDOS_DEV_SESSION="eaeae41f"
export UDOS_DEV_ROOT="/Users/agentdigital/uDOS/wizard"
export UDOS_DEV_NOTES="$UDOS_DEV_ROOT/notes"
export UDOS_DEV_AI_ASSISTANT="claude"
```

---

## 📝 DEVELOPMENT WORKFLOW

### 1. Session Initialization
```bash
# Auto-generate session ID and setup
cd /Users/agentdigital/uDOS/wizard
SESSION_ID="$(date +"%Y%m%d%H%M%S" | md5sum | cut -c1-8)"
SESSION_FILE="notes/uDEV-${SESSION_ID}-$(date +%Y%m%d)-Development-Session.md"

# Create session file from template
cp templates/dev-session.md "$SESSION_FILE"
echo "Development session started: $SESSION_FILE"
```

### 2. Development Notes Management
- **Real-time Documentation:** Update notes as development progresses
- **Decision Tracking:** Record architectural decisions and rationale
- **Progress Logging:** Track implementation milestones
- **Issue Documentation:** Record problems and solutions

### 3. File Organization
- **Immediate Filing:** New development files go to `wizard/notes/` with uHEX naming
- **Auto-categorization:** Scripts to automatically categorize and organize files
- **Cross-referencing:** Link related development artifacts

---

## 🎯 INTEGRATION WITH uDOS ARCHITECTURE

### Dev Mode Commands
Extend uCORE command interface with dev mode support:

```bash
# Development commands (when in dev mode)
ucode dev init [session-name]        # Initialize development session
ucode dev log [message]              # Add to development log
ucode dev task [create|complete]     # Task management
ucode dev roadmap [view|update]      # Roadmap management
ucode dev notes [search|organize]    # Notes management
ucode dev session [status|close]     # Session management
```

### Context Awareness
- **Auto-detect:** VS Code environment and AI assistance
- **Smart Routing:** Development commands route to wizard workflows
- **Session Tracking:** Maintain development session state
- **Artifact Linking:** Connect development files to implementation

---

## 🔄 WORKFLOW AUTOMATION

### Automatic File Management
```bash
# Auto-organize development files
find wizard/ -name "*.md" -not -path "*/notes/*" | while read file; do
    if [[ ! "$file" =~ uDEV-|uLOG-|uDOC-|uTASK-|uROAD- ]]; then
        # Generate uHEX and move to proper location
        uhex="$(generate_uhex)"
        filename="$(basename "$file" .md)"
        mv "$file" "wizard/notes/uDEV-${uhex}-${filename}.md"
    fi
done
```

### Session State Management
```bash
# Track active development sessions
echo "$SESSION_ID:$(date):VS Code/Claude:Active" >> wizard/.dev-sessions.log

# Auto-close sessions on inactivity
cleanup_inactive_sessions() {
    # Implementation for session cleanup
}
```

---

## 📊 DEVELOPMENT METRICS

### Progress Tracking
- **Session Duration:** Track development session length
- **Files Modified:** Count of files changed per session
- **Commands Executed:** Development command usage
- **AI Interactions:** Claude/Copilot usage patterns
- **Implementation Progress:** Feature completion tracking

### Reporting
- **Daily Summaries:** Auto-generate development progress reports
- **Weekly Roadmaps:** Update roadmap progress
- **Architecture Evolution:** Track architectural changes over time

---

## 🔗 INTEGRATION POINTS

### VS Code Integration
- **Workspace Settings:** Configure VS Code for uDOS development
- **Task Definitions:** VS Code tasks for common development workflows
- **Extension Recommendations:** Suggested extensions for uDOS development

### AI Assistant Integration
- **Context Sharing:** Provide AI with development context
- **Session Continuity:** Maintain context across development sessions
- **Automated Documentation:** AI-assisted documentation generation

### Git Integration
- **Development Branches:** Separate branches for development work
- **Commit Messages:** Standard format for development commits
- **Tag Management:** Version tagging for development milestones

---

## 🎯 IMMEDIATE IMPLEMENTATION

### Phase 1: Core Framework (Today)
1. ✅ Create dev mode framework specification
2. 🔄 Implement automatic session detection
3. 🔄 Setup uHEX filename generation
4. 🔄 Create development workflow scripts

### Phase 2: Automation (Next Session)
1. Automatic file organization
2. Session state management
3. Progress tracking implementation
4. VS Code integration

### Phase 3: Advanced Features (Future)
1. AI context sharing
2. Automated documentation
3. Advanced metrics and reporting
4. Cross-session continuity

---

This framework ensures that all development work in VS Code/Claude sessions is properly organized, documented, and tracked according to uDOS standards while maintaining the flexibility needed for active development.
