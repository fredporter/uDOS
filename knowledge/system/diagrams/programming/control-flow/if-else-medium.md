┌─────────────────────────────────────────────────────────────────────────────┐
│                         uCODE IF/ELSE Control Flow                          │
└─────────────────────────────────────────────────────────────────────────────┘

Simple IF Statement
═══════════════════

                     START
                       │
                       ▼
              ┌────────────────┐
              │  Condition?    │
              └────────┬───────┘
                       │
           ┌───────────┴───────────┐
           │                       │
         TRUE                    FALSE
           │                       │
           ▼                       ▼
    ┌──────────────┐        (Skip to END)
    │  Execute     │              │
    │  IF block    │              │
    └──────┬───────┘              │
           │                      │
           └──────────┬───────────┘
                      ▼
                     END


IF/ELSE Statement
═════════════════

                     START
                       │
                       ▼
              ┌────────────────┐
              │  Condition?    │
              └────────┬───────┘
                       │
           ┌───────────┴───────────┐
           │                       │
         TRUE                    FALSE
           │                       │
           ▼                       ▼
    ┌──────────────┐        ┌──────────────┐
    │  Execute     │        │  Execute     │
    │  IF block    │        │  ELSE block  │
    └──────┬───────┘        └──────┬───────┘
           │                       │
           └──────────┬────────────┘
                      ▼
                     END


IF/ELSE IF/ELSE Chain
═════════════════════

                     START
                       │
                       ▼
              ┌────────────────┐
              │  Condition 1?  │
              └────────┬───────┘
                       │
           ┌───────────┴───────────┐
         TRUE                    FALSE
           │                       │
           ▼                       ▼
    ┌──────────────┐        ┌────────────────┐
    │  Execute     │        │  Condition 2?  │
    │  IF block    │        └────────┬───────┘
    └──────┬───────┘                 │
           │             ┌───────────┴───────────┐
           │           TRUE                    FALSE
           │             │                       │
           │             ▼                       ▼
           │      ┌──────────────┐        ┌──────────────┐
           │      │  Execute     │        │  Execute     │
           │      │  ELSE IF     │        │  ELSE block  │
           │      └──────┬───────┘        └──────┬───────┘
           │             │                       │
           └─────────────┴───────────┬───────────┘
                                     ▼
                                    END


Nested IF Statements
════════════════════

                     START
                       │
                       ▼
              ┌────────────────┐
              │  Outer Cond?   │
              └────────┬───────┘
                       │
           ┌───────────┴───────────┐
         TRUE                    FALSE
           │                       │
           ▼                       ▼
    ┌────────────────┐        (Skip to END)
    │  Inner Cond?   │              │
    └────────┬───────┘              │
             │                      │
    ┌────────┴────────┐             │
  TRUE              FALSE            │
    │                 │              │
    ▼                 ▼              │
┌────────┐      ┌────────┐          │
│ Both   │      │ Outer  │          │
│ True   │      │ Only   │          │
└───┬────┘      └───┬────┘          │
    │               │               │
    └───────┬───────┘               │
            │                       │
            └───────────┬───────────┘
                        ▼
                       END


uCODE Examples
══════════════

Simple IF:
┌────────────────────────────────────────┐
│ SET age = 25                           │
│ IF $age >= 18                          │
│   PRINT "Adult"                        │
│ END                                    │
└────────────────────────────────────────┘

IF/ELSE:
┌────────────────────────────────────────┐
│ SET score = 85                         │
│ IF $score >= 60                        │
│   PRINT "Pass"                         │
│ ELSE                                   │
│   PRINT "Fail"                         │
│ END                                    │
└────────────────────────────────────────┘

IF/ELSE IF/ELSE:
┌────────────────────────────────────────┐
│ SET grade = 85                         │
│ IF $grade >= 90                        │
│   PRINT "A"                            │
│ ELSE IF $grade >= 80                   │
│   PRINT "B"                            │
│ ELSE IF $grade >= 70                   │
│   PRINT "C"                            │
│ ELSE                                   │
│   PRINT "F"                            │
│ END                                    │
└────────────────────────────────────────┘

Nested IF:
┌────────────────────────────────────────┐
│ SET age = 25                           │
│ SET hasLicense = true                  │
│                                        │
│ IF $age >= 18                          │
│   IF $hasLicense                       │
│     PRINT "Can drive"                  │
│   ELSE                                 │
│     PRINT "Need license"               │
│   END                                  │
│ ELSE                                   │
│   PRINT "Too young"                    │
│ END                                    │
└────────────────────────────────────────┘


Common Patterns
═══════════════

Range Check:
  IF $value >= min AND $value <= max
    # Value in range
  END

Multiple Conditions (OR):
  IF $option == "A" OR $option == "B"
    # Either A or B
  END

Multiple Conditions (AND):
  IF $age >= 18 AND $hasPermission
    # Both conditions true
  END

Not Equal:
  IF $status != "completed"
    # Status is not completed
  END


Truth Table
═══════════

AND Operator:
┌───────┬───────┬─────────┐
│   A   │   B   │ A AND B │
├───────┼───────┼─────────┤
│ TRUE  │ TRUE  │  TRUE   │
│ TRUE  │ FALSE │  FALSE  │
│ FALSE │ TRUE  │  FALSE  │
│ FALSE │ FALSE │  FALSE  │
└───────┴───────┴─────────┘

OR Operator:
┌───────┬───────┬────────┐
│   A   │   B   │ A OR B │
├───────┼───────┼────────┤
│ TRUE  │ TRUE  │  TRUE  │
│ TRUE  │ FALSE │  TRUE  │
│ FALSE │ TRUE  │  TRUE  │
│ FALSE │ FALSE │ FALSE  │
└───────┴───────┴────────┘

NOT Operator:
┌───────┬────────┐
│   A   │ NOT A  │
├───────┼────────┤
│ TRUE  │ FALSE  │
│ FALSE │ TRUE   │
└───────┴────────┘


Legend
══════

Symbol Key:
  │ ─ └ ┘ ┐ ┌ ├ ┤  : Flow lines
  ▼ ▲ ► ◄             : Direction arrows
  ┌─────┐             : Process box
  │     │
  └─────┘

Terms:
  Condition : Boolean expression (TRUE/FALSE)
  Block     : Code between IF and END
  Nested    : IF statement inside another IF


Related Diagrams
════════════════

  • WHILE loop flow      : programming/control-flow/while-loop.txt
  • FOR loop flow         : programming/control-flow/for-loop.txt
  • Function calls        : programming/syntax-trees/function-call.txt
  • Variable scope        : programming/syntax-trees/variable-scope.txt


Guide References
════════════════

  • Control Flow Guide    : knowledge/skills/programming/ucode-basics/control-flow.md
  • Conditionals Practice : knowledge/skills/programming/ucode-basics/conditionals.md
  • Boolean Logic        : knowledge/skills/programming/ucode-basics/boolean-logic.md


Version: 1.0.21
Created: 2025-11-16
Screen Tier: Medium (40×60)
Format: ASCII Box Drawing
