# Copilot Instructions — uDOS

**Style:** Short, direct. Lean responses. No long docs.

**Boundaries:**
- **Core** (core/): offline TUI, no cloud/GUI
- **Wizard** (wizard/): services + cloud only
- **App** (app/): UI only, no logic
- **Extensions**: API + transport

**Logger:** `from core.services.logging_manager import get_logger`

**Versions:** `python -m core.version` (never hardcode)

**Unsure?** Check AGENTS.md or docs/README.md

**KEY:** Keep moving. No long docs. No deep recursion.

**Dev (VS Code):**
- Prefer Tasks: Wizard server auto-port, uDOS interactive, uCODE dispatch, Shell command.
- Dashboard should be opened via http://localhost:<port> (see .wizard-port) or rebuilt with relative base.
