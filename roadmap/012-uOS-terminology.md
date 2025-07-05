# uOS Terminology and Naming Conventions

This document outlines the key terminology in uOS and the evolution of naming conventions throughout its design and development.

---

## Terminology Evolution and Rationale

### Move

- "Move" reflects the gameplay-like, atomic nature of the input/output operation. It emphasizes the system as an interactive process involving discrete moves, akin to playing a game or engaging in a conversation.

### Milestone

- Defined as a meaningful progress marker.
- Composed of multiple Moves.
- Tracks advancement toward Missions and Legacy.
- Can be reversed or edited to reflect changes in user goals or context.

### uKnowledge

- The central common memory bank 
- Functions as a knowledge repository rather than the user-centric uMemory

### uMemory
- Holds all user data structures like Moves, Milestones, Missions, and Legacy entries.

### uCode

- The user interface front-end layer 
- Functions as the Markdown-driven interactive UI layer.
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

