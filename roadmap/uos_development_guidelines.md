# uOS Development Guidelines

This document provides guiding principles and best practices for developing the uOS system.

---

## General Principles

1. **Markdown Output Only:**  
   All development work, documentation, and user interaction outputs must be in real `.md` files.  
   This supports easy portability, readability, and version control.

2. **Single-Process Input/Output:**  
   The uOS architecture is a single-process system that operates like ChatGPT.  
   Each **Move** consists of exactly one user input and one system output.

3. **Stepwise Development:**  
   Build the uOS personality and system capabilities incrementally, respecting the evolving system structure and user needs.

4. **Comprehensive Logging:**  
   Every Move must be recorded sequentially in a single chronological log file for auditability and history.

5. **Structured Knowledge Storage:**  
   Milestones, Missions, Legacy, and other uKnowledge entries are stored as individual Markdown files based on predefined templates.

6. **Privacy-First, Local-Only:**  
   No external cloud or third-party services should be used without explicit user permission.  
   All data and AI operations happen locally to preserve user privacy.

7. **Markdown-Centric Interaction:**  
   All user interface elements, commands, and responses are Markdown-based to ensure consistency and human-readability.

8. **Clear Separation of UI and Backend:**  
   - **uCode:** The front-end, Markdown-driven interactive UI.  
   - **uScript:** The backend scripting container handling shell commands, Python scripts, etc.

9. **Planning Before Coding:**  
   Complete the conceptual and structural design of the system before implementing code to avoid architectural drift and maintain clarity.

---

## Recommended Workflow

- Define a **Mission** or goal clearly.
- Break the Mission down into **Milestones**.
- Execute actions through atomic **Moves**.
- Record each Move in the Move log.
- Update Milestones and other uKnowledge entries as progress occurs.
- Use uCode to interactively present information and accept commands.
- Use uScript for executing complex scripted tasks.
- Regularly review Milestones and Legacy for insights and system health.

---

## Version Control and Updates

- All Markdown files (Moves log, Milestones, Missions, Legacy, etc.) should be version controlled.
- Updates to uOS personality or core logic should be reflected as Moves or Milestones to maintain traceability.

---

## Summary

Adhering to these development guidelines ensures a structured, privacy-respecting, and user-centered evolution of the uOS system, making it a trustworthy lifelong AI assistant and knowledge repository.
