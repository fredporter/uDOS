# uCODE TUI ↔ Vibe CLI Integration (v1.3)

> **See also:** [specs/UCODE-PROMPT-SPEC.md](specs/UCODE-PROMPT-SPEC.md) for the uCODE prompt contract (OK/? commands, slash routing, auto‑route).

This doc reflects the current **uCODE‑TUI‑first** architecture. Vibe‑TUI has been deprecated and archived; all routing now lives in the uCODE TUI, with Vibe CLI invoked through uCODE’s OK gateway and Wizard services when available.

## 1. Core boundary: `.env` + Wizard keystore

- `.env` stays the device‑local identity store (`USER_NAME`, `USER_DOB`, `USER_ROLE`, `USER_TIMEZONE`, `USER_LOCATION_ID`, etc.) as described in `.env.example`.
- Non‑identity secrets (API keys, OAuth tokens, integration secrets) remain in the Wizard keystore (under `memory/bank/private/`), synchronized only when the Wizard server is present.
- uCODE TUI setup writes identity to `.env` and generates/syncs `WIZARD_ADMIN_TOKEN` for Wizard access.

## 2. uCODE‑TUI is the single entry point

**Entry points**
- `uDOS.py` → `core/tui/ucode.py`
- `./bin/Launch-uCODE.command`

**Routing**
- `OK` / `?` → AI prompt handler (local‑first; optional cloud sanity via Wizard).
- `/` → uCODE command if registry match, else shell (if enabled).
- no prefix → auto‑route **uCODE → shell → AI**.

## 3. Vibe CLI integration (current)

uCODE exposes Vibe functionality via **OK prompts** and the Wizard OK gateway. Vibe CLI is used behind the scenes when configured.

Routing:
- **Wizard**: `/api/ai/*` (requires `WIZARD_ADMIN_TOKEN`)
- **Local OK**: uses Ollama or Vibe wrapper per OK gateway policy

Vibe‑native commands are not required in uCODE; the OK gateway handles local‑first vs. cloud sanity policy.

## 4. MCP TUI replacement (Vibe-compatible)

The MCP gateway (`/mcp/wizard/`) provides a lightweight **Vibe‑style TUI wrapper** for uCODE command output.

- `ucode.dispatch` and `ucode.command` wrap results with a status line, prompt marker, and toolbar block.
- Output stays JSON-native but includes a `display` field for rendering TUI-like text.
- This replaces the deprecated Vibe‑TUI without reintroducing a separate TUI runtime.

## 5. Quick operational checklist

1. Run `SETUP` to write identity to `.env` and generate/sync `WIZARD_ADMIN_TOKEN`.
2. Use `OK` / `?` prompts for AI routing, and `/` for shell when enabled.
3. Wizard UI provides AI setup + model install status via OK setup.

## 6. Archived Vibe‑TUI materials

Vibe‑TUI has been fully archived. Historical reports now live under:
- `docs/.archive/2026-02/PHASE-1-VIBE-TUI-REPLACEMENT-REPORT.md`
