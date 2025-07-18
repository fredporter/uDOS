# uScript - Visual BASIC-style Programming Language

**uScript** is the native scripting language and execution engine for uDOS, featuring Visual BASIC-style syntax in markdown-native format with full GitHub Copilot integration.

## 🧭 Overview

uScript provides programmable automation for uDOS with:
- **Visual BASIC Syntax**: Familiar `SET`, `IF`, `FOR`, `DO` constructs
- **Markdown-Native**: Scripts stored as `.md` files with code blocks
- **AI-Assisted**: GitHub Copilot provides intelligent code completion
- **VS Code Integration**: Full syntax highlighting and debugging support
- **Memory Tracking**: All executions logged to `uMemory/moves/`

## 📁 Directory Structure

- `/automation/` — Scheduled tasks and workflow automation
- `/examples/` — Learning examples and demonstrations
- `/libraries/` — Reusable function libraries and utilities
- `/system/` — Core runtime components and interpreters
- `/templates/` — Pre-built script templates and patterns
- `/tests/` — Language feature and integration tests

## 🚀 Quick Start

### Running a uScript
```bash
# Via VS Code Task
Cmd+Shift+P → "Tasks: Run Task" → "🌀 Start uDOS"

# Direct execution
./uCode/ucode.sh run uScript/examples/hello-world.md
```

### Basic uScript Syntax
```uScript
' This is a comment in uScript
SET mission_name = "Learn uScript Programming"
LOG "Starting mission: " + mission_name

CREATE MISSION mission_name
IF system_status() = "healthy" THEN
    LOG "System is ready!"
    CREATE MILESTONE mission_name + "/setup-complete"
END IF
```

## 🔧 Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `SET` | Variable assignment | `SET name = "value"` |
| `LOG` | Output logging | `LOG "Message: " + variable` |
| `CREATE MISSION` | Initialize new mission | `CREATE MISSION "project-name"` |
| `CREATE MOVE` | Add progress step | `CREATE MOVE mission + "/step-1"` |
| `RUN` | Execute shell command | `RUN "./uCode/check.sh"` |
| `IF/THEN/ELSE` | Conditional logic | `IF condition THEN ... END IF` |

## 🤖 AI Integration

GitHub Copilot provides intelligent assistance:
- **Script Generation**: AI helps write automation workflows
- **Pattern Recognition**: Learns from uScript library patterns
- **Error Resolution**: Intelligent debugging and fixes
- **Template Creation**: AI-generated script templates
- **Optimization**: Performance improvement suggestions

## 📚 Learning Path

1. **Start Here**: `examples/hello-world.md`
2. **Basic Automation**: `examples/mission-demo.md`
3. **Advanced Features**: `examples/advanced-features.md`
4. **System Integration**: `automation/daily-cleanup.md`
5. **Template Creation**: `templates/mission-template.md`

---

*uScript transforms Visual BASIC simplicity into markdown-native automation with AI assistance and native VS Code performance.*

