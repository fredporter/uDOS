# Vibe Playbook (uDOS)

This is a quick guide to exploring uCODE commands through Vibe + MCP.

## Prereqs

- Wizard server running on `http://localhost:8765`
- `WIZARD_ADMIN_TOKEN` set in your shell
- Vibe config at `/.vibe/config.toml`

## Suggested First Commands

- `wizard.health`
- `wizard.providers.list`
- `wizard.config.get`
- `ucode.dispatch("HELP")`
- `ucode.dispatch("MAP")`
- `ucode.dispatch("PANEL")`
- `ucode.dispatch("GOTO L300-BJ10")`
- `ucode.dispatch("TELL location")`
- `ucode.dispatch("FIND tokyo")`
- `ucode.dispatch("BAG")`

## Notes

- Only allowlisted commands are permitted.
- Update allowlist with `UCODE_API_ALLOWLIST="HELP,MAP,PANEL,GOTO,FIND,TELL,BAG,GRAB,SPAWN,STORY,RUN,BINDER,DATASET,USER,UID,WIZARD,CONFIG,SAVE,LOAD,FILE,NEW,EDIT,NPC,TALK,REPLY,LOGS"`.
