# ASCII Display Ethos in uOS

## Overview

uOS uses ASCII and plain-text graphical metaphors as a core aesthetic and functional philosophy. This design choice reinforces its goals of simplicity, portability, and longevity.

## Guiding Principles

1. **Timeless Display**:
   - ASCII-based visuals render on any device from modern terminals to retro displays.
   - Interfaces degrade gracefully.

2. **Symbolic Navigation**:
   - Symbols and layout convey structure, priority, or action.
   - Borders, arrows, and indentation substitute for color or GUI widgets.

3. **Portable Logs**:
   - Everything can be stored, reviewed, printed, and parsed as plain text.
   - Enables future-proofing and inspection with any text tool.

4. **Minimalism as UX**:
   - ASCII encourages intentionality.
   - User attention is directed to knowledge and action, not decoration.

## Visual Elements

- **Maps**: `[Area] --> [Next Area]`
- **Menus**: `* Item`, `- Option`
- **Frames**: `== HEADER ==`, `----` for dividers
- **Pointers**: `→`, `↳`, `✔️`, `✖️`

## Sample Displays

```markdown
== TOWER OF KNOWLEDGE ==
Floor: Cognitive Science
  ↳ Room: Heuristics
    ✔️ Milestone: Anchoring Bias Summary

== MAP ==
[Knowledge Hub] --> [Research Path]
                    ↳ [Neuroscience Node]

== MISSION TRACKER ==
Mission: Build uOS Docs
  - [x] Define Terminology
  - [x] Structure Moves and Milestones
  - [ ] Draft UX Philosophy
```

