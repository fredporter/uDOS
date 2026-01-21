# Control Flow Patterns in uCODE

**Category:** Programming Fundamentals
**Difficulty:** Beginner
**Time:** 15 minutes
**Tier:** Medium (60×40)

---

## Overview

Control flow determines the order in which code executes. Master these patterns to build logic into your uCODE programs.

**Progress:** ████████░░ **80% Essential**

---

## If-Else Statement

### Syntax

```
IF <condition> THEN
    <action>
ELSE
    <action>
END
```

### Flow Diagram

```
         START
           │
           ▼
    ┌──────────────┐
    │  CONDITION?  │
    └──────┬───────┘
           │
      ┌────┴────┐
      │         │
     YES       NO
      │         │
      ▼         ▼
  ┌──────┐  ┌──────┐
  │ THEN │  │ ELSE │
  │ CODE │  │ CODE │
  └───┬──┘  └───┬──┘
      │         │
      └────┬────┘
           ▼
          END
```

### Example: Temperature Check

```
# Check temperature and advise action
IF temp > 30 THEN
    [ASSISTANT|ASK*It's hot! Stay hydrated]
ELSE IF temp > 20 THEN
    [ASSISTANT|ASK*Pleasant weather]
ELSE IF temp > 10 THEN
    [ASSISTANT|ASK*Cool. Bring a jacket]
ELSE
    [ASSISTANT|ASK*It's cold! Bundle up]
END
```

### Truth Table

```
╔═══════════╦═══════╦═══════╦═══════╦═══════╗
║ Temp      ║  >30  ║ 20-30 ║ 10-20 ║  <10  ║
╠═══════════╬═══════╬═══════╬═══════╬═══════╣
║ Output    ║  Hot  ║ Pleas ║  Cool ║ Cold  ║
║ Action    ║ ████  ║ ███   ║ ██    ║ █     ║
╚═══════════╩═══════╩═══════╩═══════╩═══════╝

Action intensity: ████ Critical, ███ Moderate, ██ Minor, █ Minimal
```

---

## While Loop

### Syntax

```
WHILE <condition>
    <action>
    <update>
END
```

### Flow Diagram

```
      START
        │
        ▼
    ┌───────────┐
┌───│ CONDITION?│
│   └─────┬─────┘
│         │
│        YES
│         │
│         ▼
│    ┌─────────┐
│    │  LOOP   │
│    │  BODY   │
│    └────┬────┘
│         │
│         ▼
│    ┌─────────┐
│    │ UPDATE  │
│    └────┬────┘
│         │
└─────────┘
         │
        NO
         ▼
        END
```

### Example: Countdown Timer

```
# Countdown from 10
counter = 10

WHILE counter > 0
    [MEMORY|WRITE*countdown*Counter: {counter}]
    counter = counter - 1
END

[MEMORY|WRITE*countdown*Blast off!]
```

### Loop Iterations Visual

```
Iteration:  1    2    3    4    5    6    7    8    9   10
Counter:   10    9    8    7    6    5    4    3    2    1
Progress:  █    ██   ███  ████ █████████████████████████████

Loop continues while counter > 0
```

---

## For Loop

### Syntax

```
FOR variable FROM start TO end
    <action>
END
```

### Flow Diagram

```
         START
           │
           ▼
    ┌──────────────┐
    │ INIT COUNTER │
    │  i = start   │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
┌───│ i <= end?    │
│   └──────┬───────┘
│          │
│         YES
│          │
│          ▼
│   ┌──────────────┐
│   │  LOOP BODY   │
│   └──────┬───────┘
│          │
│          ▼
│   ┌──────────────┐
│   │  i = i + 1   │
│   └──────┬───────┘
│          │
└──────────┘
          │
         NO
          ▼
         END
```

### Example: Generate List

```
# Create numbered list of tasks
FOR i FROM 1 TO 5
    [MEMORY|WRITE*tasks*Task {i}: Complete step {i}]
END
```

### Iteration Tracker

```
╔══════╦═══════════════════════════════════╗
║  i   ║ Action                            ║
╠══════╬═══════════════════════════════════╣
║  1   ║ █ Write "Task 1"                  ║
║  2   ║ ██ Write "Task 2"                 ║
║  3   ║ ███ Write "Task 3"                ║
║  4   ║ ████ Write "Task 4"               ║
║  5   ║ █████ Write "Task 5"              ║
╚══════╩═══════════════════════════════════╝

Completion: █████ 100%
```

---

## Switch/Case Statement

### Syntax

```
SWITCH <variable>
    CASE value1:
        <action>
    CASE value2:
        <action>
    DEFAULT:
        <action>
END
```

### Flow Diagram

```
         START
           │
           ▼
    ┌──────────────┐
    │   EVALUATE   │
    │   VARIABLE   │
    └──────┬───────┘
           │
    ┌──────┴──────────────┬──────────┐
    │                     │          │
    ▼                     ▼          ▼
┌────────┐           ┌────────┐  ┌────────┐
│ CASE 1 │           │ CASE 2 │  │DEFAULT │
└───┬────┘           └───┬────┘  └───┬────┘
    │                    │           │
    └────────┬───────────┴───────────┘
             ▼
            END
```

### Example: TZONE Greeting

```
# Greet based on timezone
SWITCH tzone
    CASE "EST":
        [ASSISTANT|ASK*Good morning, East Coast!]
    CASE "PST":
        [ASSISTANT|ASK*Hello, West Coast!]
    CASE "GMT":
        [ASSISTANT|ASK*Greetings from London!]
    CASE "JST":
        [ASSISTANT|ASK*こんにちは Tokyo!]
    DEFAULT:
        [ASSISTANT|ASK*Hello, world!]
END
```

### Case Distribution

```
╔════════╦══════════════════════════════════════╗
║ TZONE  ║ Frequency ████████░░ 80%             ║
╠════════╬══════════════════════════════════════╣
║ EST    ║ ████████████████████ 40%             ║
║ PST    ║ ████████████ 24%                     ║
║ GMT    ║ ████████ 16%                         ║
║ JST    ║ ████ 8%                              ║
║ OTHER  ║ ██████ 12%                           ║
╚════════╩══════════════════════════════════════╝
```

---

## Break and Continue

### Break Statement

Exits loop immediately:

```
counter = 0
WHILE counter < 100
    counter = counter + 1
    IF counter == 10 THEN
        BREAK  # Exit at 10
    END
END
```

**Visual:**
```
Loop: 1→2→3→4→5→6→7→8→9→10 ⛔ BREAK
      █ █ █ █ █ █ █ █ █ █
                          └─ Exit here
```

### Continue Statement

Skips to next iteration:

```
FOR i FROM 1 TO 10
    IF i % 2 == 0 THEN
        CONTINUE  # Skip even numbers
    END
    [MEMORY|WRITE*odds*Number: {i}]
END
```

**Visual:**
```
Numbers: 1  2  3  4  5  6  7  8  9  10
Output:  ✓  ⊘  ✓  ⊘  ✓  ⊘  ✓  ⊘  ✓  ⊘
         │     │     │     │     │
         └─────┴─────┴─────┴─────┴─ Odd only
```

---

## Nested Loops

### Double Loop Pattern

```
FOR x FROM 1 TO 5
    FOR y FROM 1 TO 5
        [MEMORY|WRITE*grid*Cell ({x},{y})]
    END
END
```

### Grid Visualization

```
     y→  1    2    3    4    5
x ┌─────────────────────────────┐
│ │                             │
1 │  █    █    █    █    █      │
  │                             │
2 │  █    █    █    █    █      │
  │                             │
3 │  █    █    █    █    █      │
  │                             │
4 │  █    █    █    █    █      │
  │                             │
5 │  █    █    █    █    █      │
  │                             │
  └─────────────────────────────┘

Total cells: 5×5 = 25 iterations
```

---

## Guard Clauses

### Pattern

Exit early if conditions not met:

```
# Function with guards
FUNCTION process_data(data)
    IF data == NULL THEN
        RETURN "Error: No data"
    END

    IF data.length == 0 THEN
        RETURN "Error: Empty data"
    END

    IF data.length > 1000 THEN
        RETURN "Error: Too much data"
    END

    # Process data here
    RETURN "Success"
END
```

### Guard Flow

```
         START
           │
           ▼
    ┌──────────────┐
    │  data NULL?  │──YES──┐
    └──────┬───────┘       │
           │NO              │
           ▼                │
    ┌──────────────┐       │
    │  length==0?  │──YES──┤
    └──────┬───────┘       │
           │NO              │
           ▼                │
    ┌──────────────┐       │
    │  length>1000?│──YES──┤
    └──────┬───────┘       │
           │NO              │
           ▼                ▼
    ┌──────────────┐  ┌─────────┐
    │   PROCESS    │  │  ERROR  │
    │     DATA     │  │  RETURN │
    └──────┬───────┘  └────┬────┘
           │               │
           ▼               │
    ┌──────────────┐       │
    │   SUCCESS    │       │
    └──────┬───────┘       │
           │               │
           └───────┬───────┘
                   ▼
                  END
```

---

## Best Practices

### ✅ DO

```
✓ Use meaningful condition names
✓ Keep loop bodies short (< 20 lines)
✓ Avoid deep nesting (max 3 levels)
✓ Use early returns (guard clauses)
✓ Comment complex conditions
```

### ❌ DON'T

```
✗ Infinite loops without exit
✗ Modify loop counter inside loop
✗ Nest more than 3 loops deep
✗ Use GOTO (if available)
✗ Forget edge cases (0, null, empty)
```

---

## Performance Comparison

```
╔═══════════════╦════════╦═══════════╦══════════╗
║ Pattern       ║ Speed  ║ Readability║ Use Case ║
╠═══════════════╬════════╬═══════════╬══════════╣
║ IF-ELSE       ║ ██████ ║ █████████ ║ Branches ║
║ WHILE         ║ ██████ ║ ████████  ║ Unknown  ║
║ FOR           ║ ██████ ║ █████████ ║ Count    ║
║ SWITCH        ║ ██████ ║ ████████  ║ Multiple ║
║ Nested        ║ ███    ║ ████      ║ Grids    ║
╚═══════════════╩════════╩═══════════╩══════════╝

████████ = Excellent, ██████ = Good, ████ = Fair, ██ = Poor
```

---

## Common Patterns

### 1. Early Exit

```
IF error_condition THEN
    RETURN error
END
# Continue normal flow
```

### 2. Loop Until Found

```
found = FALSE
WHILE NOT found AND i < max
    IF item_matches THEN
        found = TRUE
    END
    i = i + 1
END
```

### 3. Accumulator

```
total = 0
FOR item IN list
    total = total + item.value
END
```

### 4. Filter

```
FOR item IN list
    IF item.meets_criteria THEN
        result.add(item)
    END
END
```

---

## Exercises

### Exercise 1: FizzBuzz
```
# Print numbers 1-100
# "Fizz" for multiples of 3
# "Buzz" for multiples of 5
# "FizzBuzz" for multiples of both
```

### Exercise 2: Fibonacci
```
# Generate first 10 Fibonacci numbers
# 1, 1, 2, 3, 5, 8, 13, 21, 34, 55
```

### Exercise 3: Prime Numbers
```
# Find all prime numbers up to 100
# Use nested loop with break
```

---

## Related Topics

- **Variables:** `knowledge/skills/programming/ucode-basics/variables.md`
- **Functions:** `knowledge/skills/programming/ucode-basics/functions.md`
- **Arrays:** `knowledge/skills/programming/ucode-basics/arrays.md`
- **Error Handling:** `knowledge/skills/programming/ucode-patterns/error-handling.md`

---

## Summary

**Key Takeaways:**
- IF-ELSE for decisions
- WHILE for unknown iterations
- FOR for known counts
- SWITCH for multiple cases
- Guards for early exits
- Avoid deep nesting

**Practice:** ████████░░ **80% Complete**

---

**Next:** [Functions and Procedures](../ucode-basics/functions.md)
