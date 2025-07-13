---
title: "Hello World uScript Example"
version: "Beta v1.7.0"
language: "uScript"
tags: ["example", "tutorial", "basic"]
created: 2025-07-13
---

# 👋 Hello World uScript

This is a simple uScript example demonstrating basic Visual BASIC-style syntax in uDOS.

## 🚀 Basic Commands

```uScript
' This is a comment in uScript
SET user_name = "Developer"
SET mission_title = "Learn uScript Programming"

LOG "Hello, " + user_name + "!"
LOG "Starting mission: " + mission_title

' Create a new mission
CREATE MISSION mission_title

' Add some moves to track progress
CREATE MOVE mission_title + "/step-1" {
    "description": "Set up development environment",
    "status": "completed",
    "timestamp": NOW()
}

CREATE MOVE mission_title + "/step-2" {
    "description": "Write first uScript program", 
    "status": "in-progress",
    "timestamp": NOW()
}

' Check system status
IF system_status() = "healthy" THEN
    LOG "System is running well!"
    CREATE MILESTONE mission_title + "/environment-ready"
ELSE
    LOG "System needs attention - run health check"
    RUN "./uCode/check.sh all"
END IF

LOG "uScript example completed successfully!"
```

## 🎯 Key Features Demonstrated

1. **Variables**: `SET user_name = "Developer"`
2. **String Concatenation**: `"Hello, " + user_name + "!"`
3. **Comments**: `' This is a comment`
4. **Conditional Logic**: `IF/THEN/ELSE` blocks
5. **Function Calls**: `system_status()`, `NOW()`
6. **uDOS Integration**: `CREATE MISSION`, `CREATE MOVE`, `LOG`

## 🔧 Running This Script

### Via VS Code Task
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"
3. Select "🌀 Start uDOS"
4. Run: `run uScript/examples/hello-world.md`

### Direct Execution
```bash
cd /Users/agentdigital/uDOS
./uCode/ucode.sh run uScript/examples/hello-world.md
```

## 🧠 GitHub Copilot Tips

When editing uScript files in VS Code:
- Type `' TODO:` and let Copilot suggest the next steps
- Start with `SET` and Copilot will suggest variable assignments
- Type `CREATE MISSION` and get intelligent mission naming suggestions
- Use `LOG` statements for debugging and progress tracking

## 📚 Next Steps

- Explore more examples in `uScript/examples/`
- Read the full uScript specification in `roadmap/007-uDOS-uScript.md`
- Try creating your own mission automation scripts
- Use GitHub Copilot to assist with complex workflows

---

*This example demonstrates the power of Visual BASIC-style syntax combined with uDOS memory management and AI assistance.*
