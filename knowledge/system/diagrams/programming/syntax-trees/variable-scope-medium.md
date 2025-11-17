┌─────────────────────────────────────────────────────────┐
│             uCODE Variable Scope Visualization          │
└─────────────────────────────────────────────────────────┘

Scope Hierarchy
═══════════════

    GLOBAL SCOPE
    ════════════════════════════════════════════════
    │                                              │
    │  SET globalVar = "Available everywhere"     │
    │                                              │
    │  FUNCTION outerFunction                     │
    │  ┌──────────────────────────────────────┐   │
    │  │  FUNCTION SCOPE (OUTER)              │   │
    │  │  ────────────────────────────────────│   │
    │  │  SET outerVar = "Outer only"         │   │
    │  │                                      │   │
    │  │  Can access:                         │   │
    │  │    ✓ globalVar                       │   │
    │  │    ✓ outerVar                        │   │
    │  │                                      │   │
    │  │  FUNCTION innerFunction              │   │
    │  │  ┌────────────────────────────────┐  │   │
    │  │  │ FUNCTION SCOPE (INNER)         │  │   │
    │  │  │ ───────────────────────────────│  │   │
    │  │  │ SET innerVar = "Inner only"    │  │   │
    │  │  │                                │  │   │
    │  │  │ Can access:                    │  │   │
    │  │  │   ✓ globalVar                  │  │   │
    │  │  │   ✓ outerVar                   │  │   │
    │  │  │   ✓ innerVar                   │  │   │
    │  │  └────────────────────────────────┘  │   │
    │  │                                      │   │
    │  │  Can still access:                   │   │
    │  │    ✓ globalVar                       │   │
    │  │    ✓ outerVar                        │   │
    │  │    ✗ innerVar (out of scope)         │   │
    │  └──────────────────────────────────────┘   │
    │                                              │
    │  Can access:                                 │
    │    ✓ globalVar                               │
    │    ✗ outerVar (out of scope)                 │
    │    ✗ innerVar (out of scope)                 │
    ════════════════════════════════════════════════


Variable Lifetime
═════════════════

Time →
────────────────────────────────────────────────────────

Script Start
│
├─ GLOBAL created ────────────────────────────────────►
│  │
│  ├─ Function called
│  │  │
│  │  ├─ LOCAL created ──────────────────┐
│  │  │  │                                │
│  │  │  ├─ Nested function called        │
│  │  │  │  │                             │
│  │  │  │  ├─ NESTED created ──────┐     │
│  │  │  │  │  Work...              │     │
│  │  │  │  └─ NESTED destroyed ────┘     │
│  │  │  │                                │
│  │  │  │  Work...                       │
│  │  └─ LOCAL destroyed ─────────────────┘
│  │
│  │  Global still exists...
│  │
└─ Script End
   │
   └─ GLOBAL destroyed


Memory Layout
═════════════

┌───────────────────────────────────────────────────────┐
│                    STACK (Active)                     │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ innerFunction() Frame               [CURRENT]  │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ innerVar = "Hello"                              │ │
│  │ tempResult = 42                                 │ │
│  └─────────────────────────────────────────────────┘ │
│                         ↑                             │
│  ┌─────────────────────────────────────────────────┐ │
│  │ outerFunction() Frame                           │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ outerVar = "World"                              │ │
│  │ count = 5                                       │ │
│  └─────────────────────────────────────────────────┘ │
│                         ↑                             │
│  ┌─────────────────────────────────────────────────┐ │
│  │ GLOBAL Frame                                    │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ globalVar = "uDOS"                              │ │
│  │ version = "1.0.21"                              │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
└───────────────────────────────────────────────────────┘


Variable Shadowing
══════════════════

┌──────────────────────────────────────────┐
│ SET name = "Global"                      │
│                                          │
│ FUNCTION showName                        │
│   SET name = "Local"  ← Shadows global   │
│   PRINT $name         → "Local"          │
│ END                                      │
│                                          │
│ PRINT $name           → "Global"         │
│ CALL showName                            │
│ PRINT $name           → "Global"         │
└──────────────────────────────────────────┘

Visual:
              ┌──────────┐
              │  Global  │
              │  name    │
              │ "Global" │
              └────┬─────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
    │  Function Called            │
    │  ┌──────────┐               │
    │  │  Local   │ ← Hides       │
    │  │  name    │   global      │
    │  │ "Local"  │               │
    │  └──────────┘               │
    │                             │
    └─────────────────────────────┘

    After function ends,
    local disappears,
    global visible again.


Scope Resolution
════════════════

Variable Lookup Order:
  1. Local scope (current function)
  2. Enclosing scope (parent function)
  3. Global scope
  4. ERROR: Undefined variable

Example:
┌──────────────────────────────────────────┐
│ SET x = "global"                         │
│                                          │
│ FUNCTION outer                           │
│   SET x = "outer"                        │
│                                          │
│   FUNCTION inner                         │
│     SET x = "inner"                      │
│     PRINT $x  → "inner"  (1. Local)      │
│   END                                    │
│                                          │
│   CALL inner                             │
│   PRINT $x  → "outer"  (2. Enclosing)    │
│ END                                      │
│                                          │
│ CALL outer                               │
│ PRINT $x  → "global"  (3. Global)        │
└──────────────────────────────────────────┘


Block Scope
═══════════

IF/WHILE blocks create scope:

┌──────────────────────────────────────────┐
│ SET count = 0                            │
│                                          │
│ IF $count == 0                           │
│   SET message = "Zero"  ← Block scope    │
│   PRINT $message        → Works          │
│ END                                      │
│                                          │
│ PRINT $message  → ERROR (out of scope)   │
└──────────────────────────────────────────┘

Scope Boundaries:
┌────────────────────────────────┐
│ GLOBAL SCOPE                   │
│ ┌────────────────────────────┐ │
│ │ IF BLOCK SCOPE             │ │
│ │   Variables here die       │ │
│ │   when block ends          │ │
│ └────────────────────────────┘ │
│ Variables here survive         │
└────────────────────────────────┘


Common Scope Issues
═══════════════════

Issue 1: Accessing out-of-scope variable
┌──────────────────────────────────────────┐
│ FUNCTION test                            │
│   SET localVar = "Hello"                 │
│ END                                      │
│                                          │
│ PRINT $localVar  ✗ ERROR: Undefined      │
└──────────────────────────────────────────┘

Fix: Return value or use global
┌──────────────────────────────────────────┐
│ FUNCTION test                            │
│   SET localVar = "Hello"                 │
│   RETURN $localVar                       │
│ END                                      │
│                                          │
│ SET result = [CALL test]                 │
│ PRINT $result  ✓ Works                   │
└──────────────────────────────────────────┘

Issue 2: Accidental shadowing
┌──────────────────────────────────────────┐
│ SET count = 10                           │
│                                          │
│ FUNCTION process                         │
│   SET count = 0  ← New variable!         │
│   # Meant to modify global...           │
│   SET count = $count + 1                 │
│ END                                      │
│                                          │
│ CALL process                             │
│ PRINT $count  → Still 10 (not 11)        │
└──────────────────────────────────────────┘

Fix: Use GLOBAL keyword
┌──────────────────────────────────────────┐
│ SET count = 10                           │
│                                          │
│ FUNCTION process                         │
│   GLOBAL count  ← Reference global       │
│   SET count = $count + 1                 │
│ END                                      │
│                                          │
│ CALL process                             │
│ PRINT $count  → 11 ✓                     │
└──────────────────────────────────────────┘


Best Practices
══════════════

✓ DO:
  • Use smallest scope possible
  • Avoid globals when possible
  • Return values from functions
  • Use descriptive names
  • Document scope intentions

✗ DON'T:
  • Shadow variables accidentally
  • Rely on global state
  • Create variables in loops
  • Use same names at different levels


Scope Keywords
══════════════

GLOBAL - Access global variable
┌──────────────────────────────────────────┐
│ SET total = 0                            │
│                                          │
│ FUNCTION addToTotal value                │
│   GLOBAL total                           │
│   SET total = $total + $value            │
│ END                                      │
└──────────────────────────────────────────┘

LOCAL - Explicitly local (default)
┌──────────────────────────────────────────┐
│ FUNCTION calculate                       │
│   LOCAL result  ← Optional, default      │
│   SET result = 42                        │
│   RETURN $result                         │
│ END                                      │
└──────────────────────────────────────────┘


Related Diagrams
════════════════

• Function calls    : syntax-trees/function-call.txt
• Variable memory   : data-structures/memory-layout.txt
• Stack frames      : systems/stack-execution.txt


Guide References
════════════════

• Variables Guide   : ../../../knowledge/skills/
                      programming/ucode-basics/
                      variables.md
• Functions Guide   : functions.md
• Scope Best Practices : best-practices/scope.md


Version: 1.0.21
Created: 2025-11-16
Screen Tier: Medium (40×60)
Format: ASCII Box Drawing
