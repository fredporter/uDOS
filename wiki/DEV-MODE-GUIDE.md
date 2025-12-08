# DEV MODE Guide (v1.2.2)

**Interactive Debugging System for uPY Scripts**

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [Command Reference](#command-reference)
5. [Breakpoints](#breakpoints)
6. [Step Execution](#step-execution)
7. [Variable Inspection](#variable-inspection)
8. [Call Stack](#call-stack)
9. [Trace Logging](#trace-logging)
10. [Watch Variables](#watch-variables)
11. [Practical Examples](#practical-examples)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Overview

**DEV MODE** is uDOS's built-in interactive debugging system for `.upy` scripts. It provides professional-grade debugging capabilities including:

- **Breakpoints** - Pause execution at specific lines
- **Step Execution** - Execute code line-by-line
- **Variable Inspection** - Examine variable values during execution
- **Call Stack** - Track function call hierarchy
- **Trace Logging** - Detailed execution logs
- **Watch Variables** - Monitor specific variables
- **State Persistence** - Save/load debugging sessions

### When to Use DEV MODE

✅ **Use DEV MODE when:**
- Developing new uPY scripts or workflows
- Debugging complex mission logic
- Understanding variable state changes
- Tracing execution flow issues
- Testing script behavior interactively

❌ **Don't use DEV MODE for:**
- Production script execution
- Automated workflows (use logging instead)
- Performance-critical operations

---

## Getting Started

### Enable DEV MODE

```
DEV|MODE*ENABLE
```

**Output:**
```
═══════════════════════════════════════════════════
🐛 DEV MODE ENABLED
═══════════════════════════════════════════════════
Status:           ACTIVE
Breakpoints:      0
Call Stack:       Empty
Watch Variables:  0
Trace Logging:    DISABLED
═══════════════════════════════════════════════════
Use DEV|HELP for command reference
```

### Check DEV MODE Status

```
DEV|MODE*STATUS
```

**Output:**
```
═══════════════════════════════════════════════════
🐛 DEV MODE Status
═══════════════════════════════════════════════════
Status:           ACTIVE
Trace Logging:    ENABLED

Breakpoints:      3 set
  Line 15:        Enabled
  Line 23:        Enabled (condition: counter > 5)
  Line 42:        Disabled

Call Stack:       2 frames
  → test-workflow.upy:15  main()
    setup-mission.upy:8   initialize()

Watch Variables:  2
  counter:        10
  mission_status: ACTIVE
═══════════════════════════════════════════════════
```

### Disable DEV MODE

```
DEV|MODE*DISABLE
```

**Output:**
```
═══════════════════════════════════════════════════
🐛 DEV MODE DISABLED
═══════════════════════════════════════════════════
All breakpoints cleared
Debug state saved to: memory/system/debug_state.json
```

---

## Core Concepts

### Debug Engine Architecture

```
┌─────────────────────────────────────────────────┐
│              DEV MODE System                    │
├─────────────────────────────────────────────────┤
│  🎯 Breakpoint Manager                          │
│     • Set/remove/toggle breakpoints             │
│     • Conditional breakpoints                   │
│     • Hit count tracking                        │
│                                                  │
│  👣 Step Execution Engine                       │
│     • Step into (line-by-line)                  │
│     • Step over (skip function calls)           │
│     • Continue to next breakpoint               │
│                                                  │
│  🔍 Variable Inspector                          │
│     • Inspect any variable                      │
│     • Nested object access                      │
│     • Watch list management                     │
│                                                  │
│  📚 Call Stack Tracker                          │
│     • Function call hierarchy                   │
│     • Script navigation                         │
│     • Variable scope per frame                  │
│                                                  │
│  📝 Trace Logger                                │
│     • Line execution logs                       │
│     • Variable state tracking                   │
│     • Performance metrics                       │
└─────────────────────────────────────────────────┘
```

### Execution Flow

**Normal Execution:**
```
Script Start → Line 1 → Line 2 → Line 3 → ... → Script End
```

**DEV MODE Execution:**
```
Script Start → Line 1 → Line 2 → [BREAKPOINT] → PAUSE
                                                   ↓
User inspects variables, call stack, watches      ↓
                                                   ↓
User issues: STEP, CONTINUE, or INSPECT           ↓
                                                   ↓
Resume → Line 3 → Line 4 → ... → Script End
```

---

## Command Reference

### DEV|MODE*ENABLE

**Enable DEV MODE debugging system**

```
DEV|MODE*ENABLE
```

**When:**
- Before running a script you want to debug
- At the start of a debugging session

**Effect:**
- Activates breakpoint checking
- Enables step execution
- Loads previous debug state (if exists)

---

### DEV|MODE*DISABLE

**Disable DEV MODE and save state**

```
DEV|MODE*DISABLE
```

**When:**
- After debugging session complete
- Before production script execution

**Effect:**
- Clears all breakpoints
- Saves debug state to `memory/system/debug_state.json`
- Disables trace logging

---

### DEV|MODE*STATUS

**Display current DEV MODE state**

```
DEV|MODE*STATUS
```

**Shows:**
- Active/inactive status
- Breakpoints (with conditions)
- Call stack (script:line function)
- Watched variables (with current values)
- Trace logging status

**Use:**
- Check if DEV MODE is active
- See all active breakpoints
- Review watched variable values
- Inspect call stack depth

---

### DEV|BREAK*LINE [CONDITION]

**Set breakpoint at specific line**

```
DEV|BREAK*15                    # Simple breakpoint at line 15
DEV|BREAK*23*counter > 5        # Conditional breakpoint
DEV|BREAK*42                    # Another simple breakpoint
```

**Arguments:**
- `LINE` - Line number (required)
- `CONDITION` - Optional condition (e.g., `x > 10`, `status == "ACTIVE"`)

**When:**
- You want execution to pause at a specific line
- Testing conditional logic
- Investigating variable values at a point

**Output:**
```
✅ Breakpoint set at line 15
✅ Conditional breakpoint set at line 23 (counter > 5)
```

---

### DEV|BREAK*REMOVE*LINE

**Remove breakpoint from line**

```
DEV|BREAK*REMOVE*15
```

**Use:**
- Remove breakpoint no longer needed
- Clear all breakpoints: use DEV|MODE*DISABLE

---

### DEV|BREAK*TOGGLE*LINE

**Enable/disable breakpoint without removing**

```
DEV|BREAK*TOGGLE*23
```

**Use:**
- Temporarily disable a breakpoint
- Re-enable without resetting conditions

---

### DEV|STEP

**Execute next line (step into)**

```
DEV|STEP
```

**When:**
- Execution is paused at a breakpoint
- You want to execute one line and pause again

**Effect:**
- Executes current line
- Pauses at next line
- Updates call stack if entering function

**Use Case:**
```
Current Line 15: VAR-SET('counter'|10)
↓ DEV|STEP
Executed Line 15
Current Line 16: IF('$counter'|>|5)
[PAUSED]
```

---

### DEV|CONTINUE

**Resume execution until next breakpoint**

```
DEV|CONTINUE
```

**When:**
- Finished inspecting at current breakpoint
- Want to run until next breakpoint or script end

**Effect:**
- Resumes normal execution
- Stops at next breakpoint (if any)
- Completes script if no more breakpoints

---

### DEV|INSPECT*VARIABLE

**Inspect variable value**

```
DEV|INSPECT*counter                  # Simple variable
DEV|INSPECT*mission.status           # Nested object
DEV|INSPECT*config.api.endpoint      # Deep nesting
```

**When:**
- Execution is paused
- You want to see current variable values

**Output:**
```
🔍 Variable: counter
   Type:     integer
   Value:    10

🔍 Variable: mission.status
   Type:     string
   Value:    "ACTIVE"
```

**Limitations:**
- Variable must exist in current scope
- Use dot notation for nested access

---

### DEV|STACK

**Display call stack**

```
DEV|STACK
```

**Output:**
```
═══════════════════════════════════════════════════
📚 Call Stack (3 frames)
═══════════════════════════════════════════════════
Frame 0 (current):
  Script:   test-workflow.upy
  Line:     15
  Function: validate_inputs()
  Variables: 2
    - input_data: {...}
    - validation_result: true

Frame 1:
  Script:   test-workflow.upy
  Line:     42
  Function: process_mission()
  Variables: 4
    - mission_id: "WATER-PURIFY-001"
    - start_time: "2025-12-03T14:30:00Z"
    - status: "ACTIVE"
    - progress: 45

Frame 2:
  Script:   main-runner.upy
  Line:     8
  Function: main()
  Variables: 1
    - missions: [...]
═══════════════════════════════════════════════════
```

**Use:**
- Understand function call hierarchy
- See which script called current function
- Inspect variables in each stack frame

---

### DEV|TRACE*ENABLE / DISABLE

**Enable/disable trace logging**

```
DEV|TRACE*ENABLE
DEV|TRACE*DISABLE
```

**When Enabled:**
- Every line execution is logged
- Variable changes are tracked
- Performance metrics collected

**Output Location:**
- `memory/logs/dev_mode/trace-{timestamp}.log`

**Example Trace Log:**
```
2025-12-03 14:30:00 | LINE 15 | VAR-SET('counter'|10)
2025-12-03 14:30:00 | VARIABLE | counter = 10 (integer)
2025-12-03 14:30:01 | LINE 16 | IF('$counter'|>|5)
2025-12-03 14:30:01 | BRANCH  | Condition TRUE
2025-12-03 14:30:01 | LINE 17 | PANEL('SUCCESS'|'Counter is high')
2025-12-03 14:30:02 | OUTPUT  | Panel displayed
```

**⚠️ Warning:**
- Trace logging creates large log files
- Can slow down execution significantly
- Use only for detailed debugging

---

### DEV|WATCH*ADD*VARIABLE

**Add variable to watch list**

```
DEV|WATCH*ADD*counter
DEV|WATCH*ADD*mission.status
```

**Effect:**
- Variable value displayed in STATUS
- Value updated after each step
- Persisted in debug state

**Use:**
- Monitor critical variables
- Track state changes across execution

---

### DEV|WATCH*REMOVE*VARIABLE

**Remove variable from watch list**

```
DEV|WATCH*REMOVE*counter
```

---

### DEV|HELP

**Show command reference**

```
DEV|HELP
```

**Output:**
```
═══════════════════════════════════════════════════
🐛 DEV MODE Command Reference
═══════════════════════════════════════════════════

MODE:
  DEV|MODE*ENABLE       Enable DEV MODE
  DEV|MODE*DISABLE      Disable DEV MODE
  DEV|MODE*STATUS       Show current status

BREAKPOINTS:
  DEV|BREAK*LINE              Set breakpoint
  DEV|BREAK*LINE*CONDITION    Set conditional breakpoint
  DEV|BREAK*REMOVE*LINE       Remove breakpoint
  DEV|BREAK*TOGGLE*LINE       Enable/disable breakpoint

EXECUTION:
  DEV|STEP              Execute next line
  DEV|CONTINUE          Resume until next breakpoint

INSPECTION:
  DEV|INSPECT*VARIABLE  Inspect variable value
  DEV|STACK             Show call stack

TRACE:
  DEV|TRACE*ENABLE      Enable trace logging
  DEV|TRACE*DISABLE     Disable trace logging

WATCH:
  DEV|WATCH*ADD*VAR     Add variable to watch list
  DEV|WATCH*REMOVE*VAR  Remove from watch list

HELP:
  DEV|HELP              Show this reference
═══════════════════════════════════════════════════
```

---

## Breakpoints

### Simple Breakpoints

**Pause execution at a specific line:**

```
DEV|BREAK*15
```

**When script reaches line 15:**
1. Execution pauses
2. Debug prompt displayed
3. User can inspect variables, call stack
4. User issues STEP or CONTINUE

### Conditional Breakpoints

**Pause only when condition is true:**

```
DEV|BREAK*23*counter > 5
```

**Condition Syntax:**
- `variable > value` - Greater than
- `variable < value` - Less than
- `variable == value` - Equal (use single or double ==)
- `variable != value` - Not equal
- Combine with AND/OR (implementation-dependent)

**Example:**
```
DEV|BREAK*42*mission_status == "FAILED"
```
↓
Pauses at line 42 **only if** `mission_status` equals `"FAILED"`

### Managing Breakpoints

**List all breakpoints:**
```
DEV|MODE*STATUS
```

**Remove specific breakpoint:**
```
DEV|BREAK*REMOVE*15
```

**Temporarily disable (without removing):**
```
DEV|BREAK*TOGGLE*15   # Disable
DEV|BREAK*TOGGLE*15   # Re-enable
```

**Clear all breakpoints:**
```
DEV|MODE*DISABLE
```

---

## Step Execution

### Single-Step Debugging

**Execute one line at a time:**

```
# At line 15 (paused at breakpoint)
DEV|STEP

# Executes line 15
# Pauses at line 16
# Show updated variable values

DEV|STEP

# Executes line 16
# Pauses at line 17
# ...and so on
```

### Step vs Continue

| Command | Behavior | Use When |
|---------|----------|----------|
| `DEV|STEP` | Execute 1 line, pause | Detailed inspection needed |
| `DEV|CONTINUE` | Run until next breakpoint | Section looks correct |

**Example Workflow:**
```
DEV|BREAK*15              # Set breakpoint at line 15
RUN|SCRIPT*test.upy       # Run script

[Execution pauses at line 15]

DEV|INSPECT*counter       # Check counter value
counter = 0

DEV|STEP                  # Execute line 15
[Line 15 executed: VAR-SET('counter'|10)]

DEV|INSPECT*counter       # Verify update
counter = 10

DEV|CONTINUE              # Resume until next breakpoint or end
```

---

## Variable Inspection

### Basic Inspection

**Inspect simple variable:**
```
DEV|INSPECT*counter

Output:
🔍 Variable: counter
   Type:     integer
   Value:    10
```

### Nested Objects

**Inspect nested properties:**
```
DEV|INSPECT*mission.id

Output:
🔍 Variable: mission.id
   Type:     string
   Value:    "WATER-PURIFY-001"
```

**Deep nesting:**
```
DEV|INSPECT*config.api.gemini.endpoint

Output:
🔍 Variable: config.api.gemini.endpoint
   Type:     string
   Value:    "https://generativelanguage.googleapis.com/v1/models/..."
```

### Inspection During Execution

**At any breakpoint or after STEP:**

```
[Paused at line 23]

DEV|INSPECT*input_data
DEV|INSPECT*validation_result
DEV|INSPECT*error_count

# Review all values before continuing
DEV|CONTINUE
```

### Scope Rules

- Variables must exist in **current scope**
- Use `DEV|STACK` to see available variables per frame
- Cannot inspect variables from other scripts (unless in call stack)

---

## Call Stack

### Understanding the Call Stack

**What is the call stack?**

The call stack tracks function calls in hierarchical order:

```
Frame 0 (current):   validate_inputs()    ← Currently executing
Frame 1:             process_mission()    ← Called validate_inputs()
Frame 2:             main()               ← Called process_mission()
```

### Viewing the Stack

```
DEV|STACK
```

**Output:**
```
═══════════════════════════════════════════════════
📚 Call Stack (3 frames)
═══════════════════════════════════════════════════
Frame 0 (current):
  Script:   test-workflow.upy
  Line:     15
  Function: validate_inputs()
  Variables: 2
    - input_data: {...}
    - validation_result: true

Frame 1:
  Script:   test-workflow.upy
  Line:     42
  Function: process_mission()
  Variables: 4
    - mission_id: "WATER-PURIFY-001"
    - start_time: "2025-12-03T14:30:00Z"
    - status: "ACTIVE"
    - progress: 45

Frame 2:
  Script:   main-runner.upy
  Line:     8
  Function: main()
  Variables: 1
    - missions: [...]
═══════════════════════════════════════════════════
```

### Use Cases

✅ **Understanding execution flow:**
- Which function called which?
- How deep is the call stack?
- What script initiated the current function?

✅ **Debugging recursion:**
- How many times has function been called?
- Are we approaching stack overflow?

✅ **Variable scope inspection:**
- What variables exist at each level?
- Can I access parent scope variables?

---

## Trace Logging

### Enable Trace Logging

```
DEV|TRACE*ENABLE
```

**Effect:**
- Every line execution is logged
- Variable changes tracked
- Performance metrics collected
- Logs saved to `memory/logs/dev_mode/trace-{timestamp}.log`

### Example Trace Log

```log
2025-12-03 14:30:00.123 | EXEC  | test-workflow.upy:15 | VAR-SET('counter'|10)
2025-12-03 14:30:00.124 | VAR   | counter = 10 (integer)
2025-12-03 14:30:00.125 | EXEC  | test-workflow.upy:16 | IF('$counter'|>|5)
2025-12-03 14:30:00.126 | EVAL  | Condition: counter > 5 = TRUE
2025-12-03 14:30:00.127 | EXEC  | test-workflow.upy:17 | PANEL('INFO'|'Counter is high')
2025-12-03 14:30:00.130 | OUT   | Panel displayed: "Counter is high"
2025-12-03 14:30:00.131 | EXEC  | test-workflow.upy:18 | ENDIF
2025-12-03 14:30:00.132 | PERF  | Lines 15-18 executed in 9ms
```

### Log Format

```
TIMESTAMP | TYPE | LOCATION | DETAILS
```

**Types:**
- `EXEC` - Line execution
- `VAR` - Variable change
- `EVAL` - Condition evaluation
- `OUT` - Output/panel
- `PERF` - Performance metric
- `ERROR` - Execution error

### Performance Impact

⚠️ **Warning:** Trace logging significantly impacts performance:

- **Without trace:** ~1000 lines/second
- **With trace:** ~100 lines/second (10x slower)

**Use trace logging only for:**
- Detailed debugging of small scripts
- Investigating complex logic errors
- Understanding execution flow

**Don't use for:**
- Large mission workflows
- Production scripts
- Performance-critical operations

### Disable Trace Logging

```
DEV|TRACE*DISABLE
```

---

## Watch Variables

### Adding Variables to Watch List

```
DEV|WATCH*ADD*counter
DEV|WATCH*ADD*mission_status
DEV|WATCH*ADD*api_calls_remaining
```

**Effect:**
- Variables displayed in `DEV|MODE*STATUS`
- Values update after each `DEV|STEP`
- Persisted in debug state

### Viewing Watched Variables

```
DEV|MODE*STATUS
```

**Output:**
```
Watch Variables:  3
  counter:             42
  mission_status:      "ACTIVE"
  api_calls_remaining: 87
```

### Removing from Watch List

```
DEV|WATCH*REMOVE*counter
```

### Use Cases

✅ **Monitor critical state:**
- Track mission progress variables
- Watch API quota remaining
- Monitor error counters

✅ **Quick variable overview:**
- See multiple variables without repeated INSPECT
- Compare values before/after operations

---

## Practical Examples

### Example 1: Debugging a Loop

**Script: `test-loop.upy`**
```python
VAR-SET('counter'|0)
VAR-SET('sum'|0)

WHILE('$counter'|<|10)
  VAR-INCREMENT('counter')
  VAR-SET('sum'|'$(sum + counter)')
  PANEL('INFO'|'Iteration $counter: sum=$sum')
ENDWHILE

PANEL('RESULT'|'Final sum: $sum')
```

**Debug Session:**
```bash
# Enable DEV MODE
DEV|MODE*ENABLE

# Set breakpoint inside loop
DEV|BREAK*5

# Add watch variables
DEV|WATCH*ADD*counter
DEV|WATCH*ADD*sum

# Run script
RUN|SCRIPT*test-loop.upy

# [Pauses at line 5 on first iteration]

# Check current state
DEV|MODE*STATUS
# Shows: counter=1, sum=1

# Step to next iteration
DEV|CONTINUE

# [Pauses at line 5 again]

# Check state after second iteration
DEV|MODE*STATUS
# Shows: counter=2, sum=3

# Let it run to completion
DEV|BREAK*REMOVE*5
DEV|CONTINUE

# Final result: sum=55
```

---

### Example 2: Conditional Breakpoint

**Script: `check-status.upy`**
```python
VAR-SET('mission_id'|'WATER-001')
VAR-SET('status'|'ACTIVE')

FOR-EACH('check'|1..100)
  # Simulate status changes
  IF('$check'|%|10|==|0)
    VAR-SET('status'|'FAILED')
  ELSE
    VAR-SET('status'|'ACTIVE')
  ENDIF

  PANEL('INFO'|'Check $check: status=$status')
ENDFOR
```

**Debug Session:**
```bash
# Enable DEV MODE
DEV|MODE*ENABLE

# Set conditional breakpoint - pause only on FAILED status
DEV|BREAK*11*status == "FAILED"

# Run script
RUN|SCRIPT*check-status.upy

# [Script runs normally until check=10]
# [Pauses at line 11 when status becomes "FAILED"]

# Inspect variables
DEV|INSPECT*check
# check = 10

DEV|INSPECT*status
# status = "FAILED"

# Continue to next failure
DEV|CONTINUE

# [Pauses at line 11 when check=20]
# ...and so on
```

---

### Example 3: Mission Workflow Debugging

**Script: `water-purification-mission.upy`**
```python
# Phase 1: Initialize
VAR-SET('mission.id'|'WATER-PURIFY-001')
VAR-SET('mission.status'|'INIT')
PANEL('PHASE'|'Initializing mission...')

# Phase 2: Load knowledge
VAR-SET('mission.status'|'LOADING')
GENERATE-GUIDE('Water purification methods'|'water'|'knowledge/water/purification-advanced.md')

# Phase 3: Review quality
VAR-SET('mission.status'|'REVIEWING')
DOCS-REVIEW('knowledge/water/purification-advanced.md')

# Phase 4: Validate
IF('$DOCS.REVIEW.SCORE'|<|85)
  VAR-SET('mission.status'|'FAILED')
  PANEL('ERROR'|'Quality too low: $DOCS.REVIEW.SCORE')
  EXIT(1)
ENDIF

VAR-SET('mission.status'|'COMPLETED')
PANEL('SUCCESS'|'Mission complete!')
```

**Debug Session:**
```bash
# Enable DEV MODE and trace
DEV|MODE*ENABLE
DEV|TRACE*ENABLE

# Set breakpoints at phase transitions
DEV|BREAK*6      # Before GENERATE-GUIDE
DEV|BREAK*10     # Before DOCS-REVIEW
DEV|BREAK*13     # Before quality check

# Watch mission state
DEV|WATCH*ADD*mission.status
DEV|WATCH*ADD*DOCS.REVIEW.SCORE

# Run mission
RUN|SCRIPT*water-purification-mission.upy

# [Pauses at line 6]
DEV|MODE*STATUS
# mission.status = "LOADING"

DEV|CONTINUE

# [Pauses at line 10 after GENERATE-GUIDE completes]
DEV|MODE*STATUS
# mission.status = "REVIEWING"

DEV|CONTINUE

# [Pauses at line 13 after DOCS-REVIEW]
DEV|INSPECT*DOCS.REVIEW.SCORE
# DOCS.REVIEW.SCORE = 92

DEV|INSPECT*DOCS.REVIEW.ISSUES
# DOCS.REVIEW.ISSUES = []

# Continue to completion
DEV|CONTINUE

# [Mission completes successfully]

# Review trace log
DEV|TRACE*DISABLE
# Check: memory/logs/dev_mode/trace-2025-12-03-143000.log
```

---

## Best Practices

### 1. Use Strategic Breakpoints

❌ **Don't:**
```
DEV|BREAK*1
DEV|BREAK*2
DEV|BREAK*3
DEV|BREAK*4
... (every line)
```

✅ **Do:**
```
DEV|BREAK*15    # Start of critical section
DEV|BREAK*42    # Before API call
DEV|BREAK*78    # Error handling entry
```

### 2. Conditional Breakpoints for Rare Cases

✅ **Efficient debugging:**
```
# Only pause when error occurs
DEV|BREAK*50*error_count > 0

# Only pause when API quota low
DEV|BREAK*25*api_calls_remaining < 10

# Only pause on specific mission
DEV|BREAK*10*mission_id == "CRITICAL-001"
```

### 3. Watch Critical Variables

✅ **Monitor important state:**
```
DEV|WATCH*ADD*mission.status
DEV|WATCH*ADD*api.calls.remaining
DEV|WATCH*ADD*quality.score
DEV|WATCH*ADD*error.count
```

### 4. Enable Trace Logging Selectively

❌ **Don't enable for entire script:**
```
DEV|TRACE*ENABLE
RUN|SCRIPT*large-workflow.upy  # 1000+ lines
```

✅ **Enable for specific sections:**
```
DEV|BREAK*100
RUN|SCRIPT*large-workflow.upy

[Paused at line 100]
DEV|TRACE*ENABLE         # Enable trace
DEV|CONTINUE             # Run traced section
[Paused at line 150]
DEV|TRACE*DISABLE        # Disable trace
DEV|CONTINUE             # Run rest normally
```

### 5. Save Debug State Between Sessions

✅ **Preserve breakpoints:**
```
# End of debugging session
DEV|MODE*STATUS          # Review current state
DEV|MODE*DISABLE         # Saves state to memory/system/debug_state.json

# Next session
DEV|MODE*ENABLE          # Restores breakpoints, watches
```

### 6. Use Call Stack for Context

✅ **Understand execution context:**
```
[Paused at mysterious line]

DEV|STACK                # See how we got here
# Frame 0: current_function() - line 15
# Frame 1: process_data()   - line 42
# Frame 2: main()           - line 8

# Now understand: main() → process_data() → current_function()
```

### 7. Clean Up After Debugging

✅ **Before production:**
```
# Remove all debug artifacts
DEV|MODE*DISABLE                    # Clear breakpoints
DEV|TRACE*DISABLE                   # Stop trace logging

# Remove #BREAK directives from script
# (Search for: #BREAK)
```

---

## Troubleshooting

### Breakpoint Not Triggering

**Problem:** Breakpoint set but execution doesn't pause

**Checks:**
1. Is DEV MODE enabled?
   ```
   DEV|MODE*STATUS
   # Should show: Status: ACTIVE
   ```

2. Is breakpoint on an executed line?
   ```
   # Breakpoint on line inside IF that never runs
   IF('$always_false'|==|TRUE)
     VAR-SET('test'|1)   # ← Breakpoint here never triggers
   ENDIF
   ```

3. Is conditional breakpoint condition ever true?
   ```
   DEV|BREAK*15*counter > 100
   # If counter never exceeds 100, breakpoint never triggers
   ```

**Solution:**
- Verify DEV MODE active: `DEV|MODE*ENABLE`
- Set breakpoint on unconditional line
- Check condition logic: `DEV|INSPECT*variable`

---

### Variable Inspection Shows "Not Found"

**Problem:** `DEV|INSPECT*variable` returns "Variable not found"

**Causes:**
1. Variable not in current scope
2. Variable hasn't been set yet
3. Typo in variable name

**Solution:**
1. Check call stack:
   ```
   DEV|STACK
   # See available variables in current frame
   ```

2. Verify variable exists:
   ```
   DEV|MODE*STATUS
   # Watch Variables section shows defined vars
   ```

3. Check spelling:
   ```
   # Script has: mission_id
   DEV|INSPECT*mission-id   # ❌ Wrong (underscore vs dash)
   DEV|INSPECT*mission_id   # ✅ Correct
   ```

---

### Trace Log Too Large

**Problem:** Trace log file grows to gigabytes

**Cause:** Trace logging on long-running script

**Solution:**
1. Disable trace immediately:
   ```
   DEV|TRACE*DISABLE
   ```

2. Use trace selectively:
   ```
   # Only trace specific function
   DEV|BREAK*100             # Function entry
   DEV|CONTINUE
   [Paused at line 100]
   DEV|TRACE*ENABLE          # Enable
   DEV|BREAK*150             # Function exit
   DEV|CONTINUE
   [Paused at line 150]
   DEV|TRACE*DISABLE         # Disable
   ```

3. Clean up old logs:
   ```
   SHELL('rm memory/logs/dev_mode/trace-*.log')
   ```

---

### Execution Hangs After STEP

**Problem:** `DEV|STEP` command doesn't return

**Cause:** Script waiting for external input/command

**Solution:**
1. Check if script has blocking operation:
   ```
   # Script at line 42:
   SHELL('sleep 60')   # ← Blocks for 60 seconds
   ```

2. Use CONTINUE instead:
   ```
   DEV|CONTINUE   # Let blocking operation complete
   ```

3. Set breakpoint after blocking operation:
   ```
   DEV|BREAK*REMOVE*42
   DEV|BREAK*43   # After blocking operation
   DEV|CONTINUE
   ```

---

### State Not Persisting Between Sessions

**Problem:** Breakpoints lost when restarting uDOS

**Cause:** DEV MODE disabled without saving

**Solution:**
1. Always disable properly:
   ```
   DEV|MODE*DISABLE   # Saves to memory/system/debug_state.json
   ```

2. Check state file exists:
   ```
   FILE-EXISTS('memory/system/debug_state.json')
   ```

3. Manually verify state:
   ```
   FILE-READ('memory/system/debug_state.json')
   # Should contain: breakpoints, watches, trace status
   ```

---

## Advanced Topics

### #BREAK Directive in Scripts

**Embed breakpoints directly in code:**

```python
# water-test.upy
VAR-SET('counter'|0)

WHILE('$counter'|<|10)
  VAR-INCREMENT('counter')

  #BREAK   # ← Pause here every iteration

  PANEL('INFO'|'Counter: $counter')
ENDWHILE
```

**When:**
- Permanent debugging checkpoints
- Complex loop debugging
- Script development phase

**⚠️ Remember:** Remove `#BREAK` directives before production!

---

### Performance Profiling

**Use trace logs for performance analysis:**

```bash
# Enable trace
DEV|TRACE*ENABLE

# Run script
RUN|SCRIPT*slow-workflow.upy

# Disable trace
DEV|TRACE*DISABLE

# Analyze log for slow lines
SHELL('grep "PERF" memory/logs/dev_mode/trace-*.log | sort -t"|" -k5 -nr | head -20')
# Shows: 20 slowest operations
```

---

### Remote Debugging (Future)

**Planned for v1.3.0:**
- TCP socket debug protocol
- Remote breakpoint management
- IDE integration (VS Code extension)
- Multi-session debugging

---

## Summary

**DEV MODE** provides comprehensive debugging for uPY scripts with:

✅ **Breakpoints** - Simple and conditional
✅ **Step Execution** - Line-by-line control
✅ **Variable Inspection** - Deep object access
✅ **Call Stack** - Execution context
✅ **Trace Logging** - Detailed execution logs
✅ **Watch Variables** - Real-time monitoring

**Quick Start:**
```bash
DEV|MODE*ENABLE                    # Enable DEV MODE
DEV|BREAK*42                       # Set breakpoint
DEV|WATCH*ADD*mission.status       # Watch variable
RUN|SCRIPT*my-workflow.upy         # Run script
[Paused at line 42]
DEV|INSPECT*mission.status         # Check value
DEV|STEP                           # Execute next line
DEV|CONTINUE                       # Resume
DEV|MODE*DISABLE                   # Save state and exit
```

**Documentation:**
- [Command Reference](Command-Reference.md#dev-mode)
- [uPY Language Guide](uCODE-Language.md)
- [Workflow System](Getting-Started.md#workflows)

**Support:**
- GitHub Issues: [uDOS/issues](https://github.com/MatthewPDingle/uDOS/issues)
- Wiki: [uDOS Wiki](https://github.com/MatthewPDingle/uDOS/wiki)

---

**Last Updated:** 2025-12-03 (v1.2.2)
**Maintained by:** uDOS Development Team
