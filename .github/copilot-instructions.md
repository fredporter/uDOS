# GitHub Copilot Instructions for uDOS

Keep responses short and impersonal. Follow repository boundaries:

- Core (core/**): offline TUI only, no cloud or GUI.
- Wizard (wizard/**): server + cloud integrations only.
- App (app/**): UI only, no business logic.
- Extensions (extensions/**): API + transport only.

Use the canonical logger in Core:
from core.services.logging_manager import get_logger

Never hardcode versions; use: python -m core.version

When unsure, check:
- AGENTS.md
- docs/README.md
