---
title: "Hello World uScript Example"
version: "Beta v1.7.0"
language: "uScript"
tags: ["example", "tutorial", "basic"]
created: 2025-07-13
---

# 👋 Hello World uScript

This is a simple uScript example demonstrating basic Visual BASIC-style syntax in uDOS.

# 👋 Hello World uScript

This is a comprehensive uScript example demonstrating Visual BASIC-style syntax in the uDOS environment with GitHub Copilot integration.

---
title: "Hello World uScript Example"
type: "example"
language: "uScript"
version: "1.0.0"
difficulty: "beginner"
---

## 🚀 Basic uScript Commands

```uScript
' This is a comment in uScript - Visual BASIC style syntax
' uScript brings familiar programming constructs to markdown-native automation

SET user_name = "Developer"
SET mission_title = "Learn uScript Programming" 
SET learning_goal = "Master Visual BASIC-style automation in uDOS"

LOG "Hello, " + user_name + "!"
LOG "Starting mission: " + mission_title
LOG "Goal: " + learning_goal

' Create a new mission for tracking progress
CREATE MISSION mission_title

' Add structured moves to track learning progress
CREATE MOVE mission_title + "/setup-environment" {
    "description": "Set up uScript development environment",
    "status": "completed",
    "priority": "high",
    "estimated_effort": "30 minutes",
    "timestamp": NOW(),
    "created_by": user_name
}

CREATE MOVE mission_title + "/first-script" {
    "description": "Write and execute first uScript program", 
    "status": "in-progress",
    "priority": "high",
    "estimated_effort": "1 hour",
    "timestamp": NOW(),
    "created_by": user_name
}

CREATE MOVE mission_title + "/explore-features" {
    "description": "Explore advanced uScript features and libraries",
    "status": "pending",
    "priority": "medium",
    "estimated_effort": "2 hours",
    "timestamp": NOW(),
    "created_by": user_name
}

' Conditional logic with system integration
IF system_status() = "healthy" THEN
    LOG "✅ System is running well!"
    CREATE MILESTONE mission_title + "/environment-ready"
    
    ' Demonstrate string operations and concatenation
    SET welcome_message = "Welcome to uScript - " + user_name + "!"
    SET system_info = "System Status: " + system_status()
    SET timestamp_info = "Current Time: " + NOW()
    
    LOG welcome_message
    LOG system_info
    LOG timestamp_info
    
ELSE
    LOG "⚠️ System needs attention - running health check"
    RUN "./uCode/check.sh all"
    
    CREATE MOVE mission_title + "/fix-system-issues" {
        "description": "Resolve system health issues",
        "status": "urgent",
        "priority": "critical",
        "timestamp": NOW()
    }
END IF

' Demonstrate numeric operations and loops
SET total_examples = 5
SET completed_examples = 0

FOR i = 1 TO total_examples
    SET example_name = "Example " + i
    LOG "Processing " + example_name
    SET completed_examples = completed_examples + 1
NEXT i

' Calculate progress percentage
SET progress_percent = (completed_examples / total_examples) * 100
LOG "Progress: " + completed_examples + "/" + total_examples + " (" + progress_percent + "%)"

' Create progress milestone if we've made good progress
IF progress_percent >= 80 THEN
    CREATE MILESTONE mission_title + "/examples-mastered"
    LOG "🎉 Great progress! Examples mastered."
END IF

' Demonstrate array operations
SET learning_topics = ["Variables", "Conditionals", "Loops", "Functions", "Integration"]
SET topics_completed = 0

LOG "Learning Topics:"
FOR EACH topic IN learning_topics
    LOG "- " + topic
    SET topics_completed = topics_completed + 1
NEXT topic

LOG "Total topics to cover: " + topics_completed

' File operations demonstration
SET log_file = "./uMemory/logs/hello-world-" + TODAY() + ".log"
SET log_content = "Hello World uScript executed successfully\n"
SET log_content = log_content + "User: " + user_name + "\n"
SET log_content = log_content + "Time: " + NOW() + "\n"
SET log_content = log_content + "Progress: " + progress_percent + "%\n"

write_file(log_file, log_content)
LOG "Execution log saved to: " + log_file

' Advanced features demonstration
SET performance_start = NOW()

' Simulate some processing work
FOR j = 1 TO 100
    ' Processing simulation
NEXT j

SET performance_end = NOW()
SET execution_time = time_diff(performance_end, performance_start)

LOG_PERFORMANCE "hello_world_script", execution_time
LOG "Script execution time: " + execution_time + "ms"

' Generate summary report
SET summary_data = {
    "script_name": "Hello World uScript",
    "user": user_name,
    "mission": mission_title,
    "execution_date": TODAY(),
    "execution_time": NOW(),
    "performance_ms": execution_time,
    "examples_completed": completed_examples,
    "topics_covered": topics_completed,
    "progress_percent": progress_percent,
    "system_status": system_status(),
    "log_file": log_file
}

SET summary_file = "./uMemory/reports/hello-world-summary-" + TODAY() + ".json"
write_json_file(summary_file, summary_data)

LOG "Summary report generated: " + summary_file
LOG "🎯 uScript Hello World example completed successfully!"

' Final milestone
CREATE MILESTONE mission_title + "/hello-world-complete"
LOG_MILESTONE mission_title, "hello-world-complete"

' Dashboard update
LOG_DASHBOARD "👋 Hello World uScript completed - " + user_name + " ready for advanced features"
```

## 🎯 Key Features Demonstrated

1. **Variables & Data Types**: `SET user_name = "Developer"`, numeric operations
2. **String Operations**: Concatenation, formatting, multi-line content
3. **Comments**: `' This is a Visual BASIC-style comment`
4. **Conditional Logic**: `IF/THEN/ELSE` blocks with system integration
5. **Loops**: `FOR/NEXT` and `FOR EACH` constructs
6. **Arrays**: `["Variables", "Conditionals", "Loops"]` and iteration
7. **Functions**: `system_status()`, `NOW()`, `TODAY()`, `time_diff()`
8. **uDOS Integration**: `CREATE MISSION`, `CREATE MOVE`, `CREATE MILESTONE`
9. **File Operations**: `write_file()`, `read_file()`, log management
10. **JSON Handling**: Structured data creation and file output
11. **Performance Tracking**: `LOG_PERFORMANCE()` for optimization
12. **Dashboard Integration**: `LOG_DASHBOARD()` for system updates

## 🔧 Running This Script

### Via VS Code Task
1. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Tasks: Run Task"
3. Select "🌀 Start uDOS"
4. Run: `run uScript/examples/hello-world.md`

### Direct Execution
```bash
cd /Users/agentdigital/uDOS
./uCode/ucode.sh run uScript/examples/hello-world.md
```

### Expected Output
- Mission created in `uMemory/missions/`
- Moves and milestones tracked in respective directories
- Execution log saved to `uMemory/logs/hello-world-{date}.log`
- Summary report in `uMemory/reports/hello-world-summary-{date}.json`
- Dashboard notification about completion

## 🧠 GitHub Copilot Tips

When editing uScript files in VS Code with Copilot enabled:

### Smart Code Completion
- Type `' TODO:` and let Copilot suggest the next steps
- Start with `SET` and Copilot will suggest variable assignments
- Type `CREATE MISSION` and get intelligent mission naming suggestions
- Use `LOG` statements and Copilot suggests appropriate messages

### Pattern Recognition
- Copilot learns from existing uScript patterns in your workspace
- Type `IF system_status()` and get suggested health check logic
- Start loops with `FOR` and get contextual iteration suggestions
- Begin functions with common names and get implementation hints

### AI-Assisted Development
- Use descriptive comments and Copilot generates matching code
- Type mission-related keywords for domain-specific suggestions
- Leverage Copilot for error handling and validation patterns
- Get suggestions for dashboard and logging integration

### Best Practices
- Write clear, descriptive variable names for better AI suggestions
- Use consistent naming patterns (snake_case, camelCase)
- Include comments explaining business logic for context
- Break complex operations into smaller, focused functions

## 📚 Next Steps

### Beginner Path
1. **Explore More Examples**: Check `uScript/examples/` for advanced patterns
2. **Read Language Specification**: Review `docs/development-strategy.md` and `docs/future-roadmap.md`
3. **Try Templates**: Use `uScript/templates/` for common workflows
4. **Run Tests**: Execute `uScript/tests/syntax-tests.md` to understand language features

### Intermediate Development
1. **Create Custom Automation**: Build your own mission automation scripts
2. **Explore Libraries**: Use functions from `uScript/libraries/`
3. **Integration Projects**: Connect uScript with external tools and APIs
4. **Performance Optimization**: Use performance tracking and optimization techniques

### Advanced Features
1. **Multi-Language Integration**: Combine uScript with Python, JavaScript, and Bash
2. **Scheduled Automation**: Create cron-like scheduled script execution
3. **Custom Libraries**: Build reusable function libraries for your workflows
4. **System Integration**: Deep integration with uDOS components and external systems

### Learning Resources
- **uScript Language Guide**: Complete syntax and feature documentation
- **Template Library**: Pre-built patterns for common use cases
- **Integration Examples**: Real-world automation and workflow scripts
- **GitHub Copilot Integration**: AI-assisted development techniques

---

*This example demonstrates the power of Visual BASIC-style syntax combined with uDOS memory management, file operations, performance tracking, and AI assistance for productive automation development.*
