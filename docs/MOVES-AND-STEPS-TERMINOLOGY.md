# Moves & Steps Terminology Guide

**For:** uDOS Development & Documentation  
**Effective:** 2026-01-14  
**Purpose:** Standardize practical, action-oriented language across all uDOS work

---

## 🎯 Core Terminology

### Complete Hierarchy (Smallest to Largest)

```
Step → Move → Phase → Milestone → Mission/Project
```

### **Step**
A **Step** is a single, concrete action — the smallest unit of work.

- Examples:
  - "Compare files to verify duplication" = 1 Step
  - "Archive deprecated module" = 1 Step
  - "Update all imports" = 1 Step
  - "Run test suite" = 1 Step
- Steps are the actual work units that get done
- Multiple Steps combine into a Move

### **Move**
A **Move** is a major, self-contained actionable unit of work comprised of multiple Steps.

- Practical scope: Typically 2-5 Steps
- Represents a meaningful consolidation, refactor, or feature
- Example: "Graphics consolidation" = 1 Move with 4 Steps:
  - Step 1: Compare files to verify duplication
  - Step 2: Archive deprecated module
  - Step 3: Update all imports
  - Step 4: Run test suite
- Not time-based (some Moves complete faster, some slower)
- Multiple Moves combine into a Phase

### **Phase (aka "Next Step" or Task List)**
A **Phase** is a task list of related Moves that achieves progress toward a Milestone.

- Phase = Collection of Moves to be completed
- Phase 1: 2-3 Moves (Graphics + OK handler)
- Phase 2: 4-5 Moves (Error handling, theme, naming, monitoring)
- Phase 3: 8-10 Moves (Logging split, extensions)
- Completing all Moves in a Phase achieves a Milestone

### **Milestone**
A **Milestone** is a major achievement marker — a measurable outcome.

- Examples:
  - "Core consolidation complete" (after Phase 1 + Phase 2 + Phase 3)
  - "TinyCore distribution ready" (after packaging work)
  - "Alpha v1.0.2.0 released"
- Milestones mark significant progress toward Mission/Project goals
- Multiple Milestones progress a Mission forward

### **Mission / Project**
The **Mission** or **Project** is the overall goal or desired outcome.

- Examples:
  - "uDOS Alpha v1.0.2.0" (Mission)
  - "Core consolidation initiative" (Project)
  - "TinyCore Linux distribution" (Mission)
- Contains multiple Milestones
- Represents the complete objective

---

## � Workflow: How It All Connects

### Order of Activity/Achievement

```
1. Complete Steps (individual actions)
2. Complete Moves (collections of Steps)
3. Complete Phase (task list of Moves)
4. Achieve Milestone (major achievement marker)
5. Progress Mission/Project (toward outcome/goal)
```

### Example Workflow

**Mission:** uDOS Alpha v1.0.2.0 Release

**Milestone 1:** Core Consolidation Complete
- **Phase 1** (Task list: 2-3 Moves)
  - **Move 1:** Graphics Consolidation
    - Step 1: Compare files
    - Step 2: Archive duplicate
    - Step 3: Update imports
    - Step 4: Test
  - **Move 2:** OK Handler Merge
    - Step 1: Analyze structure
    - Step 2: Merge code
    - Step 3: Update router
    - Step 4: Archive old file
    - Step 5: Test
  - **Move 3:** Documentation Update
    - Step 1: Update README
    - Step 2: Update audit docs

- **Phase 2** (Task list: 4-5 Moves)
  - Move 1: Error handling unification
  - Move 2: Theme consolidation
  - Move 3: Naming standardization
  - Move 4: Monitoring consolidation

- **Phase 3** (Task list: 8-10 Moves)
  - Move 1-5: Logging system split
  - Move 6-10: Extension architecture

**→ Milestone 1 ACHIEVED** (Core 50K → 40K LOC, 20% reduction)

**Milestone 2:** TinyCore Distribution Ready
- Phase 4 (TCZ packaging)
- Phase 5 (Stack installer)
- Phase 6 (ISO builder)

**→ Mission COMPLETE** (Alpha v1.0.2.0 Released)

### Key Principle

**A Phase is a task list of Moves to be completed.**
- You execute Steps
- Steps complete Moves
- Moves complete Phases
- Phases achieve Milestones
- Milestones progress the Mission toward the goal

---

## �📝 Language Examples

### ❌ **AVOID (Time-Based Language)**

```
"This will take 2-3 hours"
"Do this next week"
"We'll spend 20+ hours on logging"
"Phase 1 is this month, Phase 2 next month"
"That's about 30 minutes of work"
"Complete in Q1 2026"
"Work on this for a week"
"It'll take 8-10 days"
"Estimate 4-6 weeks for all phases"
```

### ✅ **USE (Moves & Steps Language)**

```
"Mission: uDOS Alpha v1.0.2.0"
"Milestone 1: Core consolidation complete"
"Phase 1 is a task list of 2-3 Moves"
"Move 1: Graphics consolidation (4 Steps)"
"Step 1: Compare files to verify duplication"
"Step 2: Archive deprecated module"
"Step 3: Update all imports across codebase"
"Step 4: Run test suite and verify"
"Complete all Steps in Move 1 before starting Move 2"
"Complete all Moves in Phase 1 to achieve Milestone 1"
"Phase 2: 4-5 Moves covering error, theme, naming, monitoring"
"Phase 3: 8-10 Moves to split logging and clarify extensions"
"Phases 1-3 complete = Milestone 1 achieved"
"Milestones 1-2 complete = Mission accomplished"
```

---

## 🔄 Conversion Guide

### From Time to Moves

| Time Estimate | Moves | Why |
|---------------|-------|-----|
| 1-2 hours | 1 Move | Single consolidation task |
| 3-5 hours | 2 Moves | Two related consolidations |
| 6-10 hours | 3-5 Moves | Multiple consolidations with decisions |
| 15+ hours | 6+ Moves | Major refactoring with testing |

**Formula:** 1 Move ≈ 2-5 hours of focused work, but don't mention the hours

---

## 📊 Documentation Standards

### **In Project Planning**

Change from:
```markdown
## Q1 2026: Core Consolidation
- Week 1-2: Graphics and handlers (10 hours)
- Week 3-4: Error and theme (15 hours)
- Rest of Q1: Logging (20+ hours)
```

To:
```markdown
## Mission: Core Consolidation
Milestone 1: Architecture Clean (Phases 1-3)

Phase 1 (2-3 Moves): Graphics & OK Handler
- Move 1: Graphics consolidation
- Move 2: OK handler merge

Phase 2 (4-5 Moves): Error, Theme, Naming, Monitoring
- Move 1: Error handling unification
- Move 2: Theme consolidation
- Move 3: Naming standardization
- Move 4: Monitoring consolidation

Phase 3 (8-10 Moves): Logging & Extensions
- Move 1-5: Logging system split
- Move 6-10: Extension architecture

→ Milestone 1 ACHIEVED: Core 50K → 40K LOC
```

### **In Audit Documents**

Change from:
```markdown
## Phase 1 (THIS WEEK - 2-3 hours)
- Task 1 (20 min)
- Task 2 (30 min)
- Task 3 (60 min)
```

To:
```markdown
## Phase 1: Task List of 2-3 Moves

Move 1: Graphics Consolidation
- Step 1: Compare files
- Step 2: Archive duplicate
- Step 3: Update imports
- Step 4: Test

Move 2: OK Handler Merge
- Step 1: Analyze structure
- Step 2: Merge code
- Step 3: Update router
- Step 4: Test
```

### **In Roadmaps**

Change from:
```
Next 2 weeks: Error handling (8-10 hours)
Q1 2026: Complete all consolidation
```

To:
```
Milestone 1: Core Consolidation
- Phase 1 (2-3 Moves): Graphics & OK Handler
- Phase 2 (4-5 Moves): Error, Theme, Naming, Monitoring
- Phase 3 (8-10 Moves): Logging & Extensions

Milestone 2: TinyCore Distribution
- Phase 4 (3-4 Moves): TCZ packaging
- Phase 5 (2-3 Moves): Stack installer
```

### **In Instructions**

Change from:
```
This should take about 30 minutes. Follow these steps:
1. Do thing A (10 min)
2. Do thing B (15 min)
3. Do thing C (5 min)
```

To:
```
Move 1: Do Three Things (3 Steps)

Complete each Step in order:
- Step 1: Do thing A
- Step 2: Do thing B
- Step 3: Do thing C
```

### **In Progress Updates**

Change from:
```
Status: 50% complete (spent 5 hours, 5 more to go)
ETA: End of week
```

To:
```
Status: Phase 1 in progress
- Move 1: ✅ Complete (4/4 Steps)
- Move 2: 🔄 In Progress (2/5 Steps complete)
- Move 3: 📋 Pending

Next: Complete Move 2, then Move 3
Milestone 1 Progress: 30% (Phase 1 of 3 Phases complete)
```

---

## 🎯 Exception: Specific Instructions

**When to use time:** Only for specific, measurable instructions like recipes or timed operations.

✅ **OK to use time:**
```
Food Recipe:
- Cook rice: 18 minutes at medium heat
- Simmer sauce: 10 minutes
- Rest: 5 minutes before serving

Build Process:
- npm install: typically completes in 60-90 seconds
- Tauri build: typical 5-10 minute build time
```

❌ **NOT OK to use time:**
```
Phase 1 will take 2-3 hours
Expect this to take a week
Do this next Tuesday
Estimate: 8-10 hours total
```

---

## 🗣️ Talking About Progress

### **Instead of:**
- "We're on week 2 of Phase 1"
- "About 4 hours of work remain"
- "This will take until Friday"
- "Progress: 60% complete in time"

### **Say:**
- "We're on Move 1 of Phase 1 (2 of 3 Moves)"
- "3 Moves remain in Phase 2"
- "We're completing Step 4 of Move 2"
- "Progress: 1 Move complete, 1.5 Moves in progress, 3 Moves pending"

---

## 📋 Checklist: Applying Moves & Steps

When documenting any uDOS work:

- [ ] **No time estimates** (hours, days, weeks, months)
- [ ] **Use Steps** for individual actions
- [ ] **Use Moves** for collections of Steps
- [ ] **Use Phases** for task lists of Moves
- [ ] **Use Milestones** for achievement markers
- [ ] **Use Mission/Project** for overall goals
- [ ] **Describe sequences** (Step → Move → Phase → Milestone → Mission)
- [ ] **Track progress** by Steps/Moves completed, not calendar
- [ ] **Phase is a task list** of Moves to be completed
- [ ] **Completing Phases achieves Milestones**
- [ ] **Milestones progress the Mission**
- [ ] **Exception only** for specific timed instructions (recipes, build times)

---

## 📚 Documents Updated (2026-01-14)

The following documents have been updated to use Moves & Steps:

- ✅ CORE-AUDIT-DUPLICATES.md
- ✅ CONSOLIDATION-CHECKLIST.md
- ✅ PHASE-1-IMPLEMENTATION.md
- ✅ CORE-AUDIT-QUICKREF.md
- ✅ AUDIT-INDEX.md
- ✅ AUDIT-SUMMARY.md
- ✅ CORE-DUPLICATE-VISUAL-MAP.md

---

## 🔄 When to Update Workspace Settings

Add to VS Code settings & workspace config:

```json
{
  "comments.ignore": [
    "hours",
    "hours of work",
    "minutes",
    "time estimate",
    "this week",
    "next week",
    "days",
    "weeks",
    "months"
  ],
  "customLanguage.hints": [
    "Use 'Moves' for major work units",
    "Use 'Steps' for concrete actions",
    "Avoid time-based language in docs"
  ]
}
```

---

## 💡 Benefits of Moves & Steps Terminology

### Complete Hierarchy Benefits

| Level | Purpose | Benefit |
|-------|---------|---------|
| **Step** | Individual action | Concrete, unambiguous |
| **Move** | Collection of Steps | Meaningful unit of progress |
| **Phase** | Task list of Moves | Clear next steps |
| **Milestone** | Achievement marker | Measurable outcome |
| **Mission/Project** | Overall goal | Strategic direction |

### Why This Works

1. **Action-Oriented:** Focus on what to do (Steps), not when
2. **Hierarchical:** Clear progression from smallest to largest unit
3. **Flexible:** Complete Steps/Moves at your own pace
4. **Practical:** Task list (Phase) of concrete work (Moves/Steps)
5. **Measurable:** Track by Moves completed, not time passed
6. **Clear Progress:** "Move 2 of Phase 1 complete" vs "30% done in time"
7. **Outcome-Focused:** Phases achieve Milestones, Milestones progress Mission
8. **Offline-Friendly:** No clock dependency for offline-first system
9. **Repeatable:** Same structure works across different projects
10. **Scalable:** Works for 1-Step task or 100-Move project

### Comparison: Time-Based vs Moves & Steps

| Aspect | Time-Based | Moves & Steps |
|--------|-----------|---------------|
| **Planning** | "3 hours, 2 weeks" | "2-3 Moves in Phase 1" |
| **Flexibility** | Bound to calendar | Action-focused |
| **Progress** | "50% of time used" | "Move 1 complete, Move 2 in progress" |
| **Communication** | "Take a week" | "Phase 1 (task list of 3 Moves)" |
| **Achievement** | "Done on Friday" | "Milestone 1 achieved" |
| **Clarity** | Depends on worker | Same for everyone |
| **Offline** | Clock-dependent | Time-independent |
| **Outcome** | Time passed | Work completed |

---

## 📖 Related Documentation

- See PHASE-1-IMPLEMENTATION.md for examples of Moves & Steps in action
- See CONSOLIDATION-CHECKLIST.md for Phase structure
- See CORE-AUDIT-DUPLICATES.md for practical Moves

---

## 📌 Quick Reference Card

```
HIERARCHY (smallest → largest):
Step → Move → Phase → Milestone → Mission/Project

WORKFLOW:
1. Execute Steps (individual actions)
2. Complete Moves (collections of Steps)
3. Complete Phase (task list of Moves)
4. Achieve Milestone (major achievement)
5. Progress Mission (toward goal)

KEY PRINCIPLE:
Phase = Task list of Moves to be completed
Completing Phases achieves Milestones
Milestones progress Mission toward outcome

LANGUAGE:
✅ "Phase 1 is a task list of 2-3 Moves"
✅ "Move 1 has 4 Steps to complete"
✅ "Complete Phase 1 to achieve Milestone 1"
✅ "Milestone 1 progresses Mission toward goal"
❌ "This takes 2-3 hours"
❌ "Do this next week"
❌ "Estimate 8-10 days"

EXCEPTION:
Time OK for: recipes, build processes, timed operations only
Time NOT OK for: planning, progress, documentation, development
```

---

**Effective Date:** 2026-01-14  
**Applies To:** All uDOS documentation and development planning  
**Future Updates:** Maintain this guide as new patterns emerge

