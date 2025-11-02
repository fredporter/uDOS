# Dev Rounds Workflow

Complete workflow for uDOS development rounds with operator checkpoints and wiki updates.

---

## Overview

The uDOS development follows a structured **dev rounds approach** where each version (v1.0.1 through v1.0.5+) focuses on specific feature sets. Each round includes automated testing, operator review checkpoints, and mandatory wiki updates.

---

## 🔄 Standard Dev Round Process

### 1. Round Preparation
```bash
# Open workspace
code uDOS.code-workspace

# Check virtual environment
# Task: "Check Virtual Environment"

# Run shakedown tests
# Task: "Shakedown Terminal Core"
```

### 2. Development Phase
- Implement features for current round
- Use `core/dev_logger.py` for structured logging
- Run tests frequently: `pytest -q memory/tests`
- Generate dev summaries: `python -m core.copilot_summary "feature implemented"`

### 3. Round Completion Checklist
Each round has specific VS Code tasks for validation:

#### v1.0.1 System Commands
```bash
# Task: "Dev Round: v1.0.1 System Check"
```
- ✅ HELP command implemented
- ✅ STATUS --live working
- ✅ REPAIR auto functional
- ✅ DASHBOARD CLI operational
- ⚠️ **Operator**: Review and adjust as needed

#### v1.0.2 File Operations
```bash
# Task: "Dev Round: v1.0.2 File Ops Check"
```
- ✅ NEW file creation
- ✅ EDIT file modification
- ✅ COPY file operations
- ✅ MOVE file operations
- ✅ SEARCH functionality
- ✅ BATCH operations
- ⚠️ **Operator**: Review and adjust as needed

#### v1.0.3 Mapping System
```bash
# Task: "Dev Round: v1.0.3 Mapping Check"
```
- ✅ APAC-centred grid implemented
- ✅ TIZO location system
- ✅ Zoom functionality
- ✅ MAP VIEW working
- ⚠️ **Operator**: Review and adjust as needed

#### v1.0.4 Teletext Integration
```bash
# Task: "Dev Round: v1.0.4 Teletext Check"
```
- ✅ TELETEXT output rendering
- ✅ MAP WEB integration
- ✅ Output formatting
- ⚠️ **Operator**: Review and adjust as needed

#### v1.0.5 Web Infrastructure
```bash
# Task: "Dev Round: v1.0.5 Web Infra Check"
```
- ✅ OUTPUT START command
- ✅ OUTPUT STOP command
- ✅ OUTPUT STATUS command
- ✅ Web server functionality
- ⚠️ **Operator**: Review and adjust as needed

### 4. Wiki Update (Mandatory)
```bash
# Task: "Update Wiki: Current Dev Round"
```

**Required wiki updates after each round:**
1. Update `wiki/Development-History.md` with:
   - Features implemented in this round
   - Technical achievements
   - Any architectural changes
   - Lessons learned

2. Update `wiki/Command-Reference.md` if new commands added

3. Update `wiki/Quick-Start.md` if user experience changed

---

## 🧪 Testing Integration

### Fast Shakedowns
```bash
# Core functionality
# Task: "Shakedown Terminal Core"

# APAC mapping
# Task: "Map APAC Center Sanity"

# Full pytest suite
# Task: "Run Pytest"
```

### Manual Testing
After automated tests, perform manual verification:
1. Launch uDOS interactive: `./start_udos.sh`
2. Test new features manually
3. Verify error handling
4. Check output formatting

---

## 📝 Logging & Documentation

### Dev Logger Usage
```python
from core.dev_logger import quick_dev_log

# Log development progress
quick_dev_log("AUS-BNE", 3, "FEATURE implement", 0, 150, "added MAP CELL command", with_user_ctx=True)
```

### Copilot Summaries
```bash
# Generate summary for current work
python -m core.copilot_summary "core/commands/map_handler.py: add CELL lookup functionality" 150 0 AUS-BNE 3
```

### Log Format
```
2025-11-02T13:47:19Z | AUS-BNE | Z3 | FEATURE implement | 0 | 150 | added MAP CELL command | ctx: workspace=default theme=FOUNDATION
```

---

## 👨‍💻 Operator Responsibilities

### During Development
- Monitor dev logs: `tail -f memory/logs/dev-*.log`
- Review automated test results
- Validate feature completeness against round goals

### At Round Completion
1. **Run all round checklist tasks**
2. **Manual feature verification**
3. **Wiki documentation update**
4. **Final quality review**
5. **Sign off on round completion**

### Quality Checkpoints
- Are all planned features implemented?
- Do automated tests pass?
- Is documentation updated?
- Are any edge cases uncovered?
- Does the user experience feel polished?

---

## 🔗 VS Code Task Reference

| Task Name | Purpose | When to Use |
|-----------|---------|-------------|
| Check Virtual Environment | Verify venv active | Before any Python commands |
| Shakedown Terminal Core | Test core commands | After major changes |
| Map APAC Center Sanity | Test mapping system | After map-related changes |
| Run Pytest | Full test suite | Before round completion |
| Dev Round: v1.0.x Check | Round completion checklist | At end of each round |
| Update Wiki: Current Dev Round | Documentation reminder | After round completion |
| Copilot: Stamp Summary Line | Generate dev summary | After significant work |

---

## 🎯 Success Criteria

A dev round is considered **complete** when:
- ✅ All planned features implemented
- ✅ Automated tests pass
- ✅ Manual testing validates functionality
- ✅ Operator checklist completed
- ✅ Wiki documentation updated
- ✅ Dev logs show clean feature implementation
- ✅ No blocking bugs identified

---

## 🔗 Related Documentation

- [Development History](Development-History) - Complete version history
- [Command Reference](Command-Reference) - All available commands
- [Architecture](Architecture) - Technical system design
- [Quick Start](Quick-Start) - Getting started guide

---

*This workflow ensures consistent quality and documentation across all uDOS development rounds, with operator oversight and automated validation at each stage.*
