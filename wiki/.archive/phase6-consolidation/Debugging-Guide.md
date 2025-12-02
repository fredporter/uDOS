# Debugging Guide

Complete guide to debugging uCODE scripts in uDOS

> **💡 New in v1.0.17**: Full interactive debugger with breakpoints, stepping, variable inspection, profiling, and more!

---

## 🎯 Quick Start

### Basic Debugging Workflow

1. **Start debugging a script**
   ```
   🔮 > DEBUG "my_script.uscript"
   ```

2. **Set breakpoints**
   ```
   🔮 > BREAK 10
   🔮 > BREAK 25 IF count > 100
   ```

3. **Run the script**
   ```
   🔮 > CONTINUE
   ```

4. **Inspect variables when paused**
   ```
   🔮 > INSPECT count
   🔮 > WATCH x
   ```

5. **Step through code**
   ```
   🔮 > STEP
   🔮 > STEP INTO
   🔮 > STEP OUT
   ```

6. **Continue or stop**
   ```
   🔮 > CONTINUE
   🔮 > DEBUG STOP
   ```

---

## 🐛 Debugger Features

### Breakpoints

**Set breakpoints** at specific line numbers:
```
🔮 > BREAK 15
✅ Breakpoint set at line 15
```

**Conditional breakpoints** pause only when condition is true:
```
🔮 > BREAK 25 IF count > 100
✅ Conditional breakpoint set at line 25: count > 100
```

**List all breakpoints**:
```
🔮 > BREAK LIST
🐛 Active Breakpoints:
   Line 15 (enabled)
   Line 25 (enabled, condition: count > 100)
   Line 42 (disabled)
```

**Disable/enable breakpoints** (keep them but don't trigger):
```
🔮 > BREAK DISABLE 15
✅ Breakpoint at line 15 disabled

🔮 > BREAK ENABLE 15
✅ Breakpoint at line 15 enabled
```

**Clear breakpoints**:
```
🔮 > BREAK CLEAR 15        # Clear specific
🔮 > BREAK CLEAR ALL       # Clear all
```

---

### Stepping

**STEP** - Execute next line (step over):
```
🔮 > STEP
🐛 Stepped to line 16
   x = 42
```

**STEP INTO** - Step into function calls:
```
🔮 > STEP INTO
🐛 Stepped into function 'calculate' at line 8
   params: [5, 10]
```

**STEP OUT** - Step out of current function:
```
🔮 > STEP OUT
🐛 Stepped out to line 17
   result = 50
```

**CONTINUE** - Run until next breakpoint:
```
🔮 > CONTINUE
🐛 Execution paused at breakpoint (line 25)
   count = 150
```

---

### Variable Inspection

**Inspect specific variable**:
```
🔮 > INSPECT count
🐛 Variable: count
   Type: int
   Value: 150
   Last changed: line 23
```

**Inspect all variables**:
```
🔮 > INSPECT ALL
🐛 Current Variables:
   count = 150 (int)
   name = "test" (str)
   items = [1, 2, 3] (list)
   active = true (bool)
```

**Watch variables** (track across execution):
```
🔮 > WATCH count
✅ Watching variable: count

🔮 > WATCH LIST
🐛 Watched Variables:
   count = 150
   x = 42
```

**View change history**:
```
🔮 > HISTORY count
🐛 Change History: count
   Line 5: undefined → 0
   Line 12: 0 → 50
   Line 23: 50 → 150
   Line 35: 150 → 200
```

---

### Runtime Modification

**Modify variables during debugging**:
```
🔮 > MODIFY count = 200
✅ Variable 'count' modified: 150 → 200

🔮 > MODIFY name = "debug"
✅ Variable 'name' modified: "test" → "debug"
```

**Use cases**:
- Test edge cases without editing script
- Skip problematic sections
- Verify fix hypotheses
- Experiment with different values

---

### Call Stack

**View call stack**:
```
🔮 > STACK
🐛 Call Stack:
   #0 calculate() at line 15
   #1 process_data() at line 28
   #2 main() at line 42
   #3 <script> at line 1
```

**Stack shows**:
- Current execution position
- Function call chain
- Line numbers for each frame
- Nesting depth

---

### Performance Profiling

**View full profile**:
```
🔮 > PROFILE
🐛 Performance Profile:
   Line 15: 0.0023s (150 executions)
   Line 28: 0.0156s (1 execution)
   Line 42: 0.0001s (300 executions)
   Total: 0.0180s
```

**Show top slowest lines**:
```
🔮 > PROFILE TOP 3
🐛 Top 3 Slowest Lines:
   1. Line 28: 0.0156s
   2. Line 15: 0.0023s
   3. Line 42: 0.0001s
```

**Auto-profiling** (background profiling):
```
🔮 > PROFILE AUTO ON
✅ Auto-profiling enabled
```

**Clear profiling data**:
```
🔮 > PROFILE CLEAR
✅ Profiling data cleared
```

---

## 📖 Common Workflows

### Debug a Script from Start

```bash
# 1. Start debugger
🔮 > DEBUG "my_script.uscript"

# 2. Set breakpoint at interesting line
🔮 > BREAK 25

# 3. Run script
🔮 > CONTINUE

# 4. When paused, inspect state
🔮 > INSPECT ALL
🔮 > STACK

# 5. Step through problem area
🔮 > STEP
🔮 > STEP
🔮 > INSPECT x

# 6. Continue or stop
🔮 > CONTINUE
🔮 > DEBUG STOP
```

---

### Find Performance Bottlenecks

```bash
# 1. Enable auto-profiling
🔮 > PROFILE AUTO ON

# 2. Run script
🔮 > DEBUG "slow_script.uscript"
🔮 > CONTINUE

# 3. Check profile
🔮 > PROFILE TOP 10

# 4. Set breakpoint at slow line
🔮 > BREAK 28

# 5. Investigate
🔮 > CONTINUE
🔮 > INSPECT ALL
🔮 > STACK
```

---

### Debug Conditional Logic

```bash
# 1. Set conditional breakpoint
🔮 > DEBUG "logic_test.uscript"
🔮 > BREAK 15 IF count > 100

# 2. Run until condition met
🔮 > CONTINUE

# 3. Inspect state
🔮 > INSPECT count
🔮 > INSPECT ALL

# 4. Modify and test fix
🔮 > MODIFY count = 95
🔮 > CONTINUE
```

---

### Track Variable Changes

```bash
# 1. Watch important variables
🔮 > DEBUG "state_test.uscript"
🔮 > WATCH count
🔮 > WATCH status
🔮 > WATCH active

# 2. Run and observe
🔮 > CONTINUE

# 3. Check history
🔮 > HISTORY count
🔮 > HISTORY ALL
```

---

## 🎓 Best Practices

### Breakpoint Strategy

✅ **DO**:
- Set breakpoints before loops
- Use conditional breakpoints for edge cases
- Set breakpoints at function entry/exit
- Disable instead of clearing (easier to re-enable)

❌ **DON'T**:
- Set too many breakpoints (slows execution)
- Forget to clear when done
- Use breakpoints for simple debugging (use INSPECT)

---

### Variable Inspection

✅ **DO**:
- Use WATCH for tracking state across execution
- Use INSPECT for point-in-time checks
- Check HISTORY for unexpected changes
- Inspect ALL when context is unclear

❌ **DON'T**:
- Watch too many variables (clutters output)
- Forget to clear watches when done
- Modify variables without understanding impact

---

### Stepping Strategy

✅ **DO**:
- Use STEP for sequential debugging
- Use STEP INTO for function investigation
- Use STEP OUT when deep in call stack
- Use CONTINUE to skip known-good sections

❌ **DON'T**:
- Step through entire script (use breakpoints)
- Step into system functions (not visible)
- Forget current position (check STACK)

---

### Performance Profiling

✅ **DO**:
- Enable AUTO profiling for background tracking
- Use PROFILE TOP to identify bottlenecks
- Clear profile between test runs
- Focus on lines with high execution counts

❌ **DON'T**:
- Profile trivial scripts (overhead)
- Forget profiling is cumulative (clear it)
- Optimize without profiling first

---

## 🔍 Debugger States

The debugger has 5 states:

| State | Description | Available Commands |
|:------|:------------|:-------------------|
| **NOT_STARTED** | No debugging session | DEBUG (to start) |
| **RUNNING** | Script executing | DEBUG STOP |
| **PAUSED** | At breakpoint | STEP, CONTINUE, INSPECT, MODIFY, STACK |
| **STEPPING** | Single-step mode | STEP, STEP INTO, STEP OUT, INSPECT |
| **STOPPED** | Session ended | DEBUG (to start new) |

---

## 📝 Example Session

Complete debugging session showing all features:

```bash
# Start debugging
🔮 > DEBUG "memory/tests/debug_test.uscript"
🐛 Debugger started for: debug_test.uscript
💡 Use BREAK <line> to set breakpoints, CONTINUE to run

# Set breakpoints
🔮 > BREAK 10
✅ Breakpoint set at line 10

🔮 > BREAK 25 IF count > 50
✅ Conditional breakpoint set at line 25: count > 50

# Watch variables
🔮 > WATCH count
✅ Watching variable: count

🔮 > WATCH status
✅ Watching variable: status

# Start execution
🔮 > CONTINUE
🐛 Execution paused at breakpoint (line 10)

# Inspect state
🔮 > INSPECT ALL
🐛 Current Variables:
   count = 0 (int)
   status = "initializing" (str)

🔮 > STACK
🐛 Call Stack:
   #0 main() at line 10
   #1 <script> at line 1

# Step through
🔮 > STEP
🐛 Stepped to line 11
   count = 1

🔮 > STEP
🐛 Stepped to line 12
   count = 2

# Continue to next breakpoint
🔮 > CONTINUE
🐛 Execution paused at breakpoint (line 25)
   Condition met: count > 50

# Check state
🔮 > INSPECT count
🐛 Variable: count
   Type: int
   Value: 75
   Last changed: line 23

# View history
🔮 > HISTORY count
🐛 Change History: count
   Line 10: undefined → 0
   Line 11: 0 → 1
   Line 12: 1 → 2
   ...
   Line 23: 50 → 75

# Modify and test
🔮 > MODIFY count = 100
✅ Variable 'count' modified: 75 → 100

# Check performance
🔮 > PROFILE TOP 5
🐛 Top 5 Slowest Lines:
   1. Line 15: 0.0045s (75 executions)
   2. Line 18: 0.0023s (75 executions)
   3. Line 23: 0.0012s (1 execution)
   4. Line 10: 0.0001s (1 execution)
   5. Line 25: 0.0001s (1 execution)

# Continue to end
🔮 > CONTINUE
✅ Script execution completed

# Check final status
🔮 > DEBUG STATUS
🐛 Debugger Status:
   State: STOPPED
   Script: debug_test.uscript
   Total lines executed: 42
   Total execution time: 0.0082s

# Stop debugger
🔮 > DEBUG STOP
✅ Debugging session stopped
```

---

## 🚨 Troubleshooting

### Breakpoint Not Hit

**Problem**: Breakpoint set but never triggered

**Solutions**:
1. Check line number (use LIST to verify)
2. Verify script actually reaches that line
3. Check if breakpoint is enabled (BREAK LIST)
4. For conditional: verify condition syntax

---

### Variable Not Found

**Problem**: INSPECT shows "Variable not found"

**Solutions**:
1. Check variable name spelling
2. Verify variable is in current scope
3. Check if variable has been initialized yet
4. Use INSPECT ALL to see available variables

---

### Performance Overhead

**Problem**: Debugger slows script execution

**Solutions**:
1. Clear unnecessary breakpoints
2. Disable auto-profiling if not needed
3. Clear watch list (WATCH CLEAR ALL)
4. Use CONTINUE instead of stepping

---

### Stack Overflow

**Problem**: Call stack too deep

**Solutions**:
1. Check for infinite recursion
2. Use STACK to identify loop
3. Set conditional breakpoint to catch cycle
4. Use MODIFY to break loop

---

## 📚 Related Documentation

- [Command Reference](Command-Reference) - Full command syntax
- [uCODE Language](uCODE-Language) - Script language guide
- [Script Automation](Script-Automation) - Writing scripts
- [Quick Start](Quick-Start) - Getting started with uDOS

---

## 💡 Tips & Tricks

### Debugging Loops

```bash
# Set conditional breakpoint for loop iterations
BREAK 15 IF i == 10       # Pause at 10th iteration
BREAK 15 IF i % 100 == 0  # Pause every 100 iterations
```

### Debugging Functions

```bash
# Set breakpoint at function entry
BREAK 8                   # First line of function

# Step into to debug function
STEP INTO

# Or step out to skip function
STEP OUT
```

### Debugging State Changes

```bash
# Watch all state variables
WATCH status
WATCH phase
WATCH error_count

# Run and check history
CONTINUE
HISTORY status
```

### Finding Memory Issues

```bash
# Watch object sizes
WATCH items.length
WATCH cache_size

# Profile memory-heavy operations
PROFILE AUTO ON
CONTINUE
PROFILE TOP 10
```

---

*Master these debugging techniques to build robust uCODE scripts!* 🐛🔍
