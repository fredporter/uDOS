## 🏗️ System Overview

This section provides an overview of the core directories and ecosystem structure of uDOS.

### Core Directories Explained

- **uCORE/** → Core system & utilities (shell, datasets, templates, installers)
- **uSCRIPT/** → Script management system (multi-language engines, libraries, registry)
- **uMEMORY/** → User memory & workspace (missions, notes, personal archive)
- **uKNOWLEDGE/** → Shared knowledge base and references
- **wizard/** → Development environment (tools, notes, VS Code integration)
- **docs/** → Documentation system (guides, standards, technical references)
- **extensions/** → Extension framework (Gemini, reasoning, profiles)
- **sandbox/** → User's active workspace (tasks, experiments, daily activity)
- **uSERVER/** → Server endpoints, middleware, and configs
- **shared/** → Shared configs, permissions, and common resources
- **drone/** → Automation & task scheduling
- **ghost/** → Demo interface & public documentation
- **imp/** → Script editor & project management
- **sorcerer/** → Advanced tools & user administration
- **tomb/** → Archive browser & backup manager

### Ecosystem Map (ASCII)

### How They Work Together

```
User (sandbox/)
      |
      v
+-----------+      +-----------+
|   uCORE   | ---> | uSCRIPT   |
+-----------+      +-----------+
      |                  |
      v                  v
  +--------+        +-----------+
  | uMEMORY|        |uKNOWLEDGE |
  +--------+        +-----------+
      |
      v
+-------------------------+
| Extensions & Role-Modules|
| (drone, ghost, imp, etc.)|
+-------------------------+
      |
      v
   Output → User
```

### Step-by-Step Flow

1. User begins in `sandbox/`, where they input commands or tasks.
2. Commands are routed to `uCORE/`, which acts as the core system and utility handler.
3. `uCORE/` invokes scripts and logic managed within `uSCRIPT/`.
4. Data is read from or written to `uMEMORY/`, the user's personal workspace and archive.
5. Relevant knowledge and references are pulled from `uKNOWLEDGE/` to enrich processing.
6. Extensions and role-modules (such as `drone`, `ghost`, `imp`) add additional logic, automation, or user interface enhancements.
7. The final output is formatted and returned back to the user in the `sandbox/` workspace.
