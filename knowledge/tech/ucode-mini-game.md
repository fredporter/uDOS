---
uid: udos-guide-tech-20260130173000-UTC-L300AB22
title: uCODE Mini-Game: Guess the Number
tags: [guide, knowledge, tech]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---

# uCODE Mini-Game: Guess the Number

**Category:** uCODE Basics — Practice Project
**Difficulty:** Beginner
**Time:** 10-20 minutes

---

## Overview

Build a small guessing game to practice variables, loops, and conditionals.

---

## State Diagram (ASCII)

```
[ START ] → [ PICK SECRET ] → [ ASK GUESS ]
                     ↑            │
                     │            ▼
                 [ TOO LOW ]  [ TOO HIGH ]
                     │            │
                     └──────┬─────┘
                            ▼
                         [ CORRECT ] → [ END ]
```

---

## Game Flow (Flowchart)

```diagram flowchart
START: Initialize game
STEP: Choose secret number (1-10)
STEP: Ask player for guess
STEP: Guess matches? YES → Win message
STEP: Guess too low? → Hint: Higher
STEP: Guess too high? → Hint: Lower
STEP: Try again (loop back)
END: End game
```

---

## Example uCODE (Simple)

```ucode
SET secret = 7
SET guess = 0

WHILE $guess != $secret
    [ASSISTANT|ASK*Guess a number 1-10]
    SET guess = $last_input
    IF $guess < $secret THEN
        [ASSISTANT|ASK*Too low]
    ELSE IF $guess > $secret THEN
        [ASSISTANT|ASK*Too high]
    ELSE
        [ASSISTANT|ASK*Correct!]
    END
END
```

---

## Extensions

- Add a guess counter
- Add difficulty levels (1-10, 1-50, 1-100)
- Add limited attempts

---

**Related Guides:**
- Control Flow Patterns in uCODE
- Variables in uCODE
- Pomodoro Technique Guide
