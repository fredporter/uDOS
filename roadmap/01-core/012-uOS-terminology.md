# uOS Terminology and Naming Conventions

This document outlines the key terminology in uOS and the evolution of naming conventions throughout its design and development.

---

## Terminology Evolution and Rationale

### Step → Move

- Original term: **Step**
- New term: **Move**
- Reason: "Move" better reflects the gameplay-like, atomic nature of the input/output operation. It emphasizes the system as an interactive process involving discrete moves, akin to playing a game or engaging in a conversation.

### Milestone

- Defined as a meaningful progress marker.
- Composed of multiple Moves.
- Tracks advancement toward Missions and Legacy.
- Can be reversed or edited to reflect changes in user goals or context.

### uMemory → uKnowledge

- The central common memory bank was initially called "uMemory."
- Renamed to **uKnowledge** to better represent its function as a knowledge repository rather than simple memory.
- Holds all user data structures like Milestones, Missions, and Legacy entries.

### uBASIC → uCode

- The user interface front-end layer was named "uBASIC."
- Renamed to **uCode** to better describe its function as the Markdown-driven interactive UI layer.
- Distinct from uScript, which handles backend scripting.

### uScript

- The backend scripting container.
- Executes shell commands, Python scripts, and other programming tasks.
- Works in tandem with uCode to support complex workflows.

### Legacy

- Represents the end-of-life mission or accumulated history.
- Tracks the total accumulated knowledge and context of the uOS installation.
- Legacy entries can be viewed as the "final story" or "history book" of the system.

---

## Summary Table

| Concept          | Original Name | Current Name | Description                                   |
|------------------|---------------|--------------|-----------------------------------------------|
| Atomic I/O unit  | Step          | Move         | Single input/output operation.                 |
| Progress marker  | Step          | Milestone    | Aggregation of Moves marking progress.        |
| Memory Bank      | uMemory       | uKnowledge   | Central knowledge repository.                   |
| Front-end UI     | uBASIC        | uCode        | Markdown-driven interactive UI layer.          |
| Backend Scripts  | n/a           | uScript      | Script container for shell and Python.         |
| End-of-life data | n/a           | Legacy       | Final history and mission at EOL.               |

---

## Notes

- The renaming reflects the maturation of the uOS design and clarifies the system’s modular structure.
- The terminology supports a consistent conceptual model emphasizing interaction, progress, and knowledge preservation.
