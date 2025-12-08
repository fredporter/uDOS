# OK Assistant Guide

**Version:** v1.2.21
**Last Updated:** December 8, 2025

Complete guide to using the OK Assistant - uDOS's AI-powered content generation system with context-aware assistance.

---

## 🎯 Overview

The **OK Assistant** (v1.2.21) is an integrated AI helper that provides:

✅ **Context-Aware Assistance** - Tracks workspace state, git status, and recent errors
✅ **8 Quick MAKE Commands** - Generate workflows, SVGs, docs, tests, and missions
✅ **O-Key Command Panel** - Interactive TUI for common AI tasks
✅ **Intelligent Content Generation** - Powered by Gemini AI with graceful fallback
✅ **Workspace Integration** - Understands your project structure and files

### What's New in v1.2.21

- **O-Key Panel** - Press `O` for instant access to 8 AI prompts
- **Context Manager** - Automatically tracks workspace, git, and error state
- **MAKE Commands** - 5 specialized generation commands
- **CONFIG Integration** - Dedicated [OK] tab in CONFIG panel

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [O-Key Command Panel](#o-key-command-panel)
3. [MAKE Commands](#make-commands)
4. [Context Tracking](#context-tracking)
5. [Configuration](#configuration)
6. [Workflow Integration](#workflow-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

1. **Gemini API Key** - Required for AI features
   ```bash
   # Add to .env file
   GEMINI_API_KEY=your_api_key_here
   ```

2. **Enable OK Assistant** (if disabled)
   ```
   CONFIG ok_enabled true
   ```

### First Steps

**1. Press O-Key for Quick Access**
```
Press: O
```
Shows interactive panel with 8 common prompts.

**2. Generate Your First Workflow**
```
OK MAKE WORKFLOW "backup system files"
```

**3. Check Status**
```
OK STATUS
```

---

## 🔑 O-Key Command Panel

Press **O** to open the interactive OK Assistant panel.

### Panel Features

```
╔════════════════════════════════════════════════════════════╗
║              OK ASSISTANT - Quick Actions                  ║
╠════════════════════════════════════════════════════════════╣
║  1. MAKE WORKFLOW  - Generate uPY workflow script         ║
║  2. MAKE SVG       - Generate SVG diagram                  ║
║  3. MAKE DOC       - Generate documentation                ║
║  4. MAKE TEST      - Generate unit tests                   ║
║  5. MAKE MISSION   - Generate mission script               ║
║  6. ASK            - Ask AI a question                     ║
║  7. STATUS         - Show usage statistics                 ║
║  8. CLEAR          - Clear conversation history            ║
╠════════════════════════════════════════════════════════════╣
║  Press 1-8 to select action, ESC to cancel                ║
╚════════════════════════════════════════════════════════════╝
```

### Using the Panel

1. **Press O** - Opens panel
2. **Select 1-8** - Choose action
3. **Enter details** - Prompted for specifics
4. **Review output** - AI-generated content displayed

**Example Flow:**
```
Press: O
Select: 1 (MAKE WORKFLOW)
Enter: "daily system health check"
Result: workflow script generated in memory/workflows/missions/
```

---

## 🛠️ MAKE Commands

### OK MAKE WORKFLOW

Generate uPY workflow scripts for automation.

**Syntax:**
```
OK MAKE WORKFLOW "<description>"
OK MAKE WORKFLOW "<description>" --save <filename>
```

**Examples:**
```
OK MAKE WORKFLOW "backup configuration files"
OK MAKE WORKFLOW "daily knowledge guide check" --save daily-check.upy
OK MAKE WORKFLOW "scan and repair system health"
```

**Output:**
- Saves to: `memory/workflows/missions/<auto-name>.upy`
- Includes: Frontmatter, variables, commands, error handling
- Features: Context-aware, workspace-integrated

**Use Cases:**
- System maintenance tasks
- File management workflows
- Batch operations
- Knowledge base updates

---

### OK MAKE SVG

Generate SVG diagrams with AI.

**Syntax:**
```
OK MAKE SVG "<description>"
OK MAKE SVG "<description>" --style <style>
OK MAKE SVG "<description>" --save <filename>
```

**Styles:**
- `technical-kinetic` (default) - MCM geometry, monochrome
- `hand-illustrative` - Organic, hand-drawn
- `hybrid` - Mixed technical + illustrative

**Examples:**
```
OK MAKE SVG "water filtration system"
OK MAKE SVG "fire triangle diagram" --style hand-illustrative
OK MAKE SVG "shelter construction" --save shelter.svg
```

**Output:**
- Saves to: `memory/drafts/svg/<description>.svg`
- Pipeline: AI → PNG → SVG vectorization
- Validation: Technical-Kinetic compliance checked

**Use Cases:**
- Knowledge base diagrams
- Tutorial illustrations
- System architecture diagrams
- Process flowcharts

---

### OK MAKE DOC

Generate documentation for code files.

**Syntax:**
```
OK MAKE DOC <file_path>
OK MAKE DOC <file_path> --format <md|rst|txt>
OK MAKE DOC <file_path> --save <filename>
```

**Examples:**
```
OK MAKE DOC core/commands/ok_handler.py
OK MAKE DOC extensions/assistant/ok_context_manager.py --format md
OK MAKE DOC core/services/knowledge_manager.py --save api-docs.md
```

**Output:**
- Analyzes: Functions, classes, methods, variables
- Generates: API documentation, usage examples
- Saves to: `memory/docs/<auto-name>.md`

**Features:**
- Code structure analysis
- Docstring extraction
- Usage example generation
- API reference formatting

**Use Cases:**
- API documentation
- Code explanations
- Developer onboarding
- Knowledge transfer

---

### OK MAKE TEST

Generate unit tests for code.

**Syntax:**
```
OK MAKE TEST "<test_description>"
OK MAKE TEST "<test_description>" --file <target_file>
OK MAKE TEST "<test_description>" --save <filename>
```

**Examples:**
```
OK MAKE TEST "test_load_knowledge function"
OK MAKE TEST "configuration validation" --file core/config.py
OK MAKE TEST "grid TILE code parsing" --save test_grid.py
```

**Output:**
- Saves to: `memory/ucode/tests/<auto-name>.py`
- Includes: Test cases, assertions, fixtures
- Framework: pytest compatible

**Features:**
- Context-aware test generation
- Edge case coverage
- Mock/fixture suggestions
- Assertion best practices

**Use Cases:**
- Unit test creation
- Test coverage improvement
- Regression testing
- TDD support

---

### OK MAKE MISSION

Generate mission workflow scripts.

**Syntax:**
```
OK MAKE MISSION "<mission_description>"
OK MAKE MISSION "<mission_description>" --difficulty <easy|medium|hard>
OK MAKE MISSION "<mission_description>" --save <filename>
```

**Examples:**
```
OK MAKE MISSION "establish base camp"
OK MAKE MISSION "water source identification" --difficulty easy
OK MAKE MISSION "advanced shelter construction" --difficulty hard
```

**Output:**
- Saves to: `memory/workflows/missions/<mission-name>.upy`
- Includes: Objectives, checkpoints, XP rewards, progression
- Features: Adventure-style structure, RPG elements

**Use Cases:**
- Tutorial missions
- Learning paths
- Achievement systems
- Gamified workflows

---

### OK ASK

Ask the AI assistant a question.

**Syntax:**
```
OK ASK "<question>"
```

**Examples:**
```
OK ASK "how do I optimize this workflow?"
OK ASK "what's the best way to structure mission scripts?"
OK ASK "explain the grid system"
```

**Features:**
- Context-aware responses
- Knowledge bank integration
- Code suggestions
- Best practice recommendations

**Note:** For general knowledge queries, consider using `MAKE DO` for offline-first answers.

---

### OK STATUS

Show OK Assistant usage statistics.

**Syntax:**
```
OK STATUS
```

**Output:**
```
╔════════════════════════════════════════════════════════════╗
║              OK ASSISTANT - Status Report                  ║
╠════════════════════════════════════════════════════════════╣
║  Total Requests:        47                                 ║
║  Workflows Generated:   12                                 ║
║  SVGs Generated:        8                                  ║
║  Docs Generated:        5                                  ║
║  Tests Generated:       3                                  ║
║  Missions Generated:    2                                  ║
║  Questions Asked:       17                                 ║
║                                                            ║
║  API Calls:             23                                 ║
║  Tokens Used:           45,832                             ║
║  Estimated Cost:        $0.023                             ║
║                                                            ║
║  Last Request:          2025-12-08 14:32:05                ║
║  Conversation Items:    12                                 ║
╚════════════════════════════════════════════════════════════╝
```

---

### OK CLEAR

Clear conversation history.

**Syntax:**
```
OK CLEAR
```

**Effect:**
- Clears AI conversation context
- Resets token usage tracking
- Preserves usage statistics

**Use When:**
- Starting new topic/context
- Conversation context too large
- Want fresh AI perspective

---

## 🎯 Context Tracking

The OK Assistant automatically tracks workspace context to provide intelligent assistance.

### Tracked Context

**1. Workspace State**
- Current directory
- Recent file changes
- Modified files (git status)
- Active branches

**2. Git Status**
- Staged changes
- Unstaged changes
- Untracked files
- Current branch

**3. Error Context**
- Recent error messages
- Stack traces
- Failed commands
- Problem files

**4. Session State**
- Recent commands executed
- Generated content
- User preferences
- Working files

### How Context Is Used

**Workflow Generation:**
```
OK MAKE WORKFLOW "fix recent errors"
# Uses: Recent error messages, problem files, git status
# Generates: Targeted repair workflow
```

**Documentation:**
```
OK MAKE DOC core/commands/ok_handler.py
# Uses: File structure, recent changes, related files
# Generates: Complete API documentation
```

**Test Generation:**
```
OK MAKE TEST "configuration validation"
# Uses: Related code files, existing tests, error patterns
# Generates: Comprehensive test suite
```

---

## ⚙️ Configuration

### Access CONFIG Panel

```
CONFIG
Navigate to: [OK] tab
```

### Available Settings

**ok_enabled** (boolean)
- Enable/disable OK Assistant
- Default: `true`

**ok_model** (string)
- AI model to use
- Options: `gemini-2.0-flash-exp`, `gemini-exp-1206`
- Default: `gemini-2.0-flash-exp`

**ok_max_tokens** (integer)
- Maximum response tokens
- Range: 1000-8192
- Default: 2048

**ok_temperature** (float)
- Response creativity
- Range: 0.0-2.0
- Default: 0.7

**ok_context_depth** (integer)
- Conversation history items
- Range: 5-50
- Default: 12

**ok_auto_save** (boolean)
- Auto-save generated content
- Default: `true`

**ok_default_path** (string)
- Default save location
- Default: `memory/workflows/missions/`

### Quick Configuration

```upy
# Enable OK Assistant
CONFIG ok_enabled true

# Use Pro model
CONFIG ok_model gemini-exp-1206

# Increase context
CONFIG ok_context_depth 20

# Higher creativity
CONFIG ok_temperature 1.2
```

---

## 🔄 Workflow Integration

### Use in uPY Scripts

```upy
# Generate workflow from within script
OK MAKE WORKFLOW "system health check"

# Generate documentation for files
OK MAKE DOC core/commands/workflow_handler.py

# Ask for help
OK ASK "how should I structure this mission?"
```

### Conditional Generation

```upy
# Generate only if file doesn't exist
IF NOT FILE_EXISTS("memory/workflows/missions/backup.upy") THEN
  OK MAKE WORKFLOW "backup configuration files"
END IF

# Generate based on errors
IF {$ERROR_COUNT} > 0 THEN
  OK MAKE WORKFLOW "fix recent errors"
END IF
```

### Batch Operations

```upy
# Generate multiple diagrams
{$topics} = ["water", "fire", "shelter"]

FOR {$topic} IN {$topics}
  OK MAKE SVG "{$topic} basics diagram"
  SLEEP 3
END FOR
```

---

## 💡 Best Practices

### 1. Provide Clear Descriptions

**Good:**
```
OK MAKE WORKFLOW "backup user configuration files to archive with timestamp"
```

**Poor:**
```
OK MAKE WORKFLOW "backup stuff"
```

### 2. Use Specific Context

**Good:**
```
OK MAKE DOC core/services/knowledge_manager.py
# AI sees file structure, can generate accurate docs
```

**Poor:**
```
OK ASK "document the knowledge manager"
# Less context, less specific output
```

### 3. Iterate with Context

```
# First attempt
OK MAKE WORKFLOW "system check"

# Refine (context preserved)
OK ASK "add error logging to the workflow"
OK ASK "include git status check"
```

### 4. Monitor Usage

```
# Check before expensive operations
OK STATUS

# If token usage high, clear context
OK CLEAR
```

### 5. Leverage Auto-Save

```
# Auto-save enabled by default
OK MAKE WORKFLOW "daily tasks"
# Automatically saved to memory/workflows/missions/

# Check output location
ls -l memory/workflows/missions/
```

### 6. Use Appropriate Commands

**For Code:**
- `OK MAKE DOC` - Documentation
- `OK MAKE TEST` - Tests

**For Content:**
- `OK MAKE SVG` - Diagrams
- `OK MAKE WORKFLOW` - Automation

**For Missions:**
- `OK MAKE MISSION` - Adventure scripts

---

## 🔧 Troubleshooting

### "OK Assistant not available"

**Cause:** Gemini API key not configured
**Fix:**
```bash
# Add to .env file
GEMINI_API_KEY=your_api_key_here

# Or set in environment
export GEMINI_API_KEY=your_api_key_here
```

### "OK Assistant disabled"

**Cause:** Feature disabled in config
**Fix:**
```
CONFIG ok_enabled true
```

### "Context limit exceeded"

**Cause:** Too much conversation history
**Fix:**
```
OK CLEAR
```

### "Generation failed"

**Causes:**
1. Network issues
2. API rate limits
3. Invalid request

**Fixes:**
```
# Check status
OK STATUS

# Wait and retry
SLEEP 5
OK MAKE WORKFLOW "retry task"

# Check logs
cat memory/logs/dev.log | grep OK
```

### "File already exists"

**Cause:** Auto-save trying to overwrite
**Fix:**
```
# Use --save with specific name
OK MAKE WORKFLOW "task" --save custom-name.upy

# Or delete existing file
rm memory/workflows/missions/existing-file.upy
```

---

## 📚 Additional Resources

- [Command Reference](Command-Reference.md#ok-commands) - All OK commands
- [Workflow Guide](Workflows.md) - Workflow automation
- [Graphics System](Graphics-System.md) - SVG generation
- [TUI Guide](TUI-Guide.md) - O-Key panel usage

---

## 🆘 Support

Having issues with OK Assistant?

1. **Check status:** `OK STATUS`
2. **Review logs:** `memory/logs/dev.log`
3. **Verify config:** `CONFIG` → [OK] tab
4. **Report bug:** [GitHub Issues](https://github.com/fredporter/uDOS/issues)

---

**Version:** v1.2.21
**Last Updated:** December 8, 2025
**Status:** Production Ready
