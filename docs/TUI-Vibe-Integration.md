# TUI Setup Story ↔ Vibe CLI Integration

> **See also:** [specs/UCODE-PROMPT-SPEC.md](specs/UCODE-PROMPT-SPEC.md) for the uCODE prompt contract (OK/: commands, slash routing, dynamic autocomplete).

This note ensures the new v1.3 architecture keeps the existing `.env` + Wizard keystore boundary alive while letting the Core TUI setup story speak the same IO language as the Vibe CLI (the interactive agent console referenced in `docs/uDOS-v1-3.md`).

## 1. Preserve the `.env` + Wizard keystore boundary

- `.env` stays the single device-local identity store (`USER_NAME`, `USER_DOB`, `USER_LOCATION`, `WIZARD_KEY`) as described in `.env.example`. Even though new directories (`core/`, `wizard/`, `themes/`, `web-admin/`) now define separate lanes, they all read the same root `.env` for identity and environment hints.
- Anything beyond base identity (API keys, OAuth tokens, integration secrets) remains in the Wizard keystore (`wizard/keystore/` or the Vault secrets service) and is only synchronized when the Wizard server is present. The TUI setup story writes its sensitive outputs (passphrases, OAuth tokens) to the keystore while leaving `.env` intact.
- When the TUI story emits `WIZARD_KEY`, the Vibe CLI (and every lane: Core, Wizard, renderer, CLI) can resolve it via the shared `wizard-key-store` interface so the new architecture still boots with the same identity handshake.

## 2. Refactor the TUI setup story for Vibe CLI IOs

- The existing story (`memory/bank/system/tui-setup-story.md` and `core/framework/seed/bank/system/tui-setup-story.md`) already collects identity/location/timezone data. Extend each step to emit both:
  1. A deterministic `.env` fragment (set `USER_NAME`, `USER_DOB`, `USER_LOCATION`, `USER_TIMEZONE`, `OS_TYPE`).
  2. A keystore bundle (Wizard secrets) that holds non-shared metadata like `USER_PASSWORD` or `OAuth` tokens.
- The new `Vibe CLI` agent console is also a runner (see `docs/uDOS-v1-3.md:175-194` and `docs/AI-Policy-Contract.md`), so the setup story should expose its prompts via the shared `Vibe CLI IO` channel:
  - Wrap each question in the story with `vibe_input`/`vibe_output` envelopes so the CLI can replay them when operating headlessly or when the mission scheduler (Vibe) re-runs the onboarding content.
  - Provide `story.get_prompt()`/`story.submit_response()` hooks in `core/tui/story_form_handler.py` so both the traditional TUI and Vibe CLI (via the `wizard/extensions/assistant/vibe_cli_service.py`) can drive the same conversation.
- When the story finishes, it should write a manifest (e.g., `memory/logs/setup-story.json`) that lists:
  - `.env` updates applied
  - Keystore entries recorded
  - `Vibe CLI` prompt IDs (so the agent can resume or replay the story)
- This manifest lets the Vibe CLI replicate the TUI experience even outside a terminal, and it keeps the `.env`/Wizard keystore boundary explicit in the new architecture (per `docs/Vault-Contract.md` and `docs/Contributions-Contract.md`).

## 3. Operational checklist for the new arcitecture

1. On first boot, run the TUI setup story (`python -m core.tui` or `./bin/Launch-uDOS-TUI.command`). It dumps identity into `.env` and the keystore, then signals the same `WIZARD_KEY` to the Vibe CLI.
2. `Vibe CLI` (local lane) validates that the `.env` values exist and that the keystore contains any referenced secrets before allowing missions or contributions to run.
3. Any lane (Core, Wizard, renderer, web-admin) that needs to rehydrate identity can simply load `.env` + the keystore bundle that the story generated, so the new folders still share the same root secrets without duplicating them.
4. If the TUI story is ever replayed (e.g., `SETUP` command), the manifest provides a deterministic diff so Vibe CLI can offer an automated “re-run story?” path while the `.env` changes remain mininal and auditable.

## 4. uCODE Vibe Commands (v1.3)

uCODE exposes Vibe CLI integration directly:

```
VIBE CHAT <prompt> [--no-context] [--model <name>]
VIBE CONTEXT [--files a,b,c] [--notes "..."]
VIBE HISTORY [--limit N]
VIBE CONFIG
```

Routing:
- **Goblin dev**: `/api/dev/vibe/*` (preferred for local workflows)
- **Wizard**: `/api/ai/*` (requires `WIZARD_ADMIN_TOKEN`)

By keeping the `.env`/Wizard keystore boundary and the Vibe CLI IO hooks explicit in the story, the v1.3 scaffolding can evolve without breaking the identity or onboarding experience.
