# uDOS v1.3 Architecture Guide

---
**Foreword**

This Architecture Guide explains how uDOS v1.3 is organised. Written in the style of early home computer manuals, it avoids jargon and gives you a clear picture of how the system fits together.

---

## System Overview

uDOS v1.3 uses a modular design. The clean core shell handles only essential tasks.  
Complex features live in *uCode scripts*. Extensions and role-based modules expand the system.  

```
User Input
    |
    v
+----------+     +-----------+
|  uCORE   | --> |  uSCRIPT  |
+----------+     +-----------+
    |
    v
+--------------------+
| Extensions / Roles |
| drone, ghost, etc. |
+--------------------+
    |
    v
 Output to User
```

---

## Core Components

- **uCORE/** → The clean system shell, only 247 lines. Handles routing and setup.  
- **uSCRIPT/** → Script library (Visual Basic-style `.ucode` files).  
- **uMEMORY/** → Workspace for missions, notes, personal files.  
- **uKNOWLEDGE/** → Shared documentation and references.  
- **wizard/** → Development environment and tools.  

---

## Modules and Scripts

Each uCode module provides a set of commands:

- **MEMORY.ucode** → File management, search, statistics.  
- **MISSION.ucode** → Create and track tasks.  
- **PACKAGE.ucode** → Install, remove, search, update packages.  
- **LOG.ucode** → Logging and reports.  
- **DEV.ucode** → Development, testing, profiling.  
- **RENDER.ucode** → (Art) ASCII graphics, charts, simple UIs.  
- **DASH.ucode** → System dashboard.  
- **PANEL.ucode** → Control panels.  
- **TREE.ucode** → Repository visualisation.  

---

## Extensions

Extensions add new capabilities:

- **Gemini** → Context, reasoning, profiles.  
- **Role Modules**:  
  - *drone/* → automation and scheduling  
  - *ghost/* → demos and public docs  
  - *imp/* → project editing and scripts  
  - *sorcerer/* → advanced tools, admin  
  - *tomb/* → backup and archives  

---

## Command Flow

1. User enters a command in the shell.  
2. uCORE parses input and decides if it is a core or script command.  
3. uSCRIPT executes the requested `.ucode` file.  
4. If needed, Extensions or role-modules are called.  
5. Results are shown in clear Markdown output.  

---

**Notes**

This guide is presented in a clear and practical style, inspired by the Acorn 1981 User Manual. It is meant to be studied alongside the User Guide, giving you both a quick start and a deeper understanding of the system’s design.
