┌──────────────────────────────────────────┐
│      uCODE WHILE Loop Control Flow       │
└──────────────────────────────────────────┘

Basic WHILE Loop
════════════════

         START
           │
           ▼
    ┌──────────────┐
    │  Initialize  │
    │  counter     │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐◄─────┐
    │  Condition?  │      │
    └──────┬───────┘      │
           │              │
      ┌────┴────┐         │
    TRUE      FALSE       │
      │         │         │
      ▼         │         │
  ┌────────┐   │         │
  │ Loop   │   │         │
  │ Body   │   │         │
  └───┬────┘   │         │
      │        │         │
      ▼        │         │
  ┌────────┐  │         │
  │ Update │  │         │
  │ counter│  │         │
  └───┬────┘  │         │
      │       │         │
      └───────┘         │
                        ▼
                       END


WHILE with Break
════════════════

         START
           │
           ▼
    ┌──────────────┐◄─────┐
    │  Condition?  │      │
    └──────┬───────┘      │
           │              │
      ┌────┴────┐         │
    TRUE      FALSE       │
      │         │         │
      ▼         │         │
  ┌────────────┐│         │
  │  Process   ││         │
  └─────┬──────┘│         │
        │       │         │
        ▼       │         │
  ┌────────────┐│         │
  │Break cond? ││         │
  └─────┬──────┘│         │
        │       │         │
   ┌────┴────┐  │         │
 TRUE      FALSE │         │
   │         │  │         │
   │         └──┘         │
   │                      │
   └──────────────────────┤
                          ▼
                         END


WHILE with Continue
═══════════════════

         START
           │
           ▼
    ┌──────────────┐◄────────┐
    │  Condition?  │         │
    └──────┬───────┘         │
           │                 │
      ┌────┴────┐            │
    TRUE      FALSE          │
      │         │            │
      ▼         │            │
  ┌────────────┐│            │
  │  Step 1    ││            │
  └─────┬──────┘│            │
        │       │            │
        ▼       │            │
  ┌────────────┐│            │
  │Skip cond?  ││            │
  └─────┬──────┘│            │
        │       │            │
   ┌────┴────┐  │            │
 TRUE      FALSE │            │
   │         │  │            │
   │         ▼  │      ┌─────┘
   │     ┌────────┐   │
   │     │ Step 2 │   │
   │     └───┬────┘   │
   │         │        │
   │         ▼        │
   │     ┌────────┐   │
   │     │ Update │   │
   │     └───┬────┘   │
   │         │        │
   └─────────┴────────┘


Nested WHILE Loops
══════════════════

              START
                │
                ▼
         ┌──────────────┐
         │ Outer init   │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐◄────┐
         │Outer cond?   │     │
         └──────┬───────┘     │
                │             │
           ┌────┴────┐        │
         TRUE      FALSE      │
           │         │        │
           ▼         │        │
    ┌──────────────┐ │        │
    │ Inner init   │ │        │
    └──────┬───────┘ │        │
           │         │        │
           ▼         │        │
    ┌──────────────┐ │        │
    │Inner cond?   │◄┼──┐     │
    └──────┬───────┘ │  │     │
           │         │  │     │
      ┌────┴────┐    │  │     │
    TRUE      FALSE  │  │     │
      │         │    │  │     │
      ▼         │    │  │     │
  ┌────────┐   │    │  │     │
  │ Inner  │   │    │  │     │
  │ body   │   │    │  │     │
  └───┬────┘   │    │  │     │
      │        │    │  │     │
      └────────┘    │  │     │
                    │  │     │
                    ▼  │     │
             ┌──────────┐    │
             │Outer updt│    │
             └────┬─────┘    │
                  │          │
                  └──────────┘
                             ▼
                            END


uCODE Examples
══════════════

Basic WHILE:
┌──────────────────────────────────┐
│ SET count = 1                    │
│ WHILE $count <= 5                │
│   PRINT "Count: $count"          │
│   SET count = $count + 1         │
│ END                              │
│                                  │
│ Output:                          │
│   Count: 1                       │
│   Count: 2                       │
│   Count: 3                       │
│   Count: 4                       │
│   Count: 5                       │
└──────────────────────────────────┘

WHILE with BREAK:
┌──────────────────────────────────┐
│ SET count = 1                    │
│ WHILE true                       │
│   PRINT "Count: $count"          │
│   SET count = $count + 1         │
│   IF $count > 5                  │
│     BREAK                        │
│   END                            │
│ END                              │
│ PRINT "Done!"                    │
└──────────────────────────────────┘

WHILE with CONTINUE:
┌──────────────────────────────────┐
│ SET count = 0                    │
│ WHILE $count < 5                 │
│   SET count = $count + 1         │
│   IF $count == 3                 │
│     CONTINUE                     │
│   END                            │
│   PRINT "Count: $count"          │
│ END                              │
│                                  │
│ Output:                          │
│   Count: 1                       │
│   Count: 2                       │
│   Count: 4  (skips 3)            │
│   Count: 5                       │
└──────────────────────────────────┘

Nested WHILE:
┌──────────────────────────────────┐
│ SET row = 1                      │
│ WHILE $row <= 3                  │
│   SET col = 1                    │
│   WHILE $col <= 3                │
│     PRINT "$row,$col "           │
│     SET col = $col + 1           │
│   END                            │
│   PRINT "\n"                     │
│   SET row = $row + 1             │
│ END                              │
│                                  │
│ Output:                          │
│   1,1 1,2 1,3                    │
│   2,1 2,2 2,3                    │
│   3,1 3,2 3,3                    │
└──────────────────────────────────┘


Common Patterns
═══════════════

Input Validation:
┌──────────────────────────────────┐
│ SET valid = false                │
│ WHILE NOT $valid                 │
│   PROMPT "Enter age: " age       │
│   IF $age >= 0 AND $age <= 120   │
│     SET valid = true             │
│   ELSE                           │
│     PRINT "Invalid age!"         │
│   END                            │
│ END                              │
└──────────────────────────────────┘

Processing Until Done:
┌──────────────────────────────────┐
│ SET done = false                 │
│ WHILE NOT $done                  │
│   # Process items                │
│   IF [condition]                 │
│     SET done = true              │
│   END                            │
│ END                              │
└──────────────────────────────────┘

Countdown:
┌──────────────────────────────────┐
│ SET count = 10                   │
│ WHILE $count > 0                 │
│   PRINT "$count..."              │
│   SET count = $count - 1         │
│   SLEEP 1                        │
│ END                              │
│ PRINT "Blast off!"               │
└──────────────────────────────────┘


Infinite Loop Guard
═══════════════════

Without Guard (DANGER):
┌──────────────────────────────────┐
│ SET count = 1                    │
│ WHILE $count > 0                 │
│   PRINT $count                   │
│   # Forgot to update count!      │
│ END                              │
│ # Will loop forever!             │
└──────────────────────────────────┘

With Guard (SAFE):
┌──────────────────────────────────┐
│ SET count = 1                    │
│ SET maxIter = 1000               │
│ SET iter = 0                     │
│ WHILE $count > 0                 │
│   PRINT $count                   │
│   SET iter = $iter + 1           │
│   IF $iter >= $maxIter           │
│     PRINT "Safety break!"        │
│     BREAK                        │
│   END                            │
│ END                              │
└──────────────────────────────────┘


Loop Comparison
═══════════════

WHILE vs FOR:

WHILE:
  • Condition checked first
  • Manual counter management
  • More flexible control
  • Use when: Unknown iterations

FOR:
  • Fixed number of iterations
  • Automatic counter
  • Cleaner syntax
  • Use when: Known iterations

WHILE true:
  • Infinite loop
  • Must use BREAK
  • Common for menus/servers
  • Dangerous without exit


Best Practices
══════════════

✓ DO:
  • Update loop variable
  • Use meaningful names
  • Add safety guards
  • Test exit conditions

✗ DON'T:
  • Modify during iteration
  • Create infinite loops
  • Forget BREAK in WHILE true
  • Nest too deeply (max 3)


Related Diagrams
════════════════

• FOR loop flow     : control-flow/for-loop.txt
• IF/ELSE flow      : control-flow/if-else.txt
• Function calls    : syntax-trees/function-call.txt


Guide References
════════════════

• Loops Guide       : ../../../knowledge/skills/
                      programming/ucode-basics/
                      loops.md
• Control Flow      : control-flow.md


Version: 1.0.21
Created: 2025-11-16
Screen Tier: Medium (40×60)
Format: ASCII Box Drawing
