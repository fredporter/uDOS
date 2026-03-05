# Gameplay Command Contract v1.5

Status: canonical contract  
Updated: 2026-03-05

## Purpose

Define one canonical command/runtime contract for gameplay, lens progression, and skin integration in v1.5.

This contract supersedes fragmented command guidance spread across older gameplay/lens specs.

## Ownership

Core owns canonical gameplay semantics:

- player progression state (`xp`, `hp`, `gold`, `level`, `achievement_level`, metrics)
- gate and token rules
- `PLAY` and `RULE` command semantics
- lens readiness/score/checkpoint calculations
- skin fit/advisory policy signals

Wizard/extension layers may present and orchestrate, but must not fork canonical gameplay state.

## Canonical Commands

- `PLAY STATUS`
- `PLAY STATS SET|ADD <xp|hp|gold> <value>`
- `PLAY MAP STATUS|ENTER|MOVE|INSPECT|INTERACT|COMPLETE|TICK`
- `PLAY GATE STATUS|COMPLETE|RESET <gate_id>`
- `PLAY TOYBOX LIST|SET <profile>`
- `PLAY GUI STATUS|OPEN|INTENT [profile]`
- `PLAY LENS LIST|SHOW|SET|STATUS|SCORE|CHECKPOINTS|ENABLE|DISABLE`
- `PLAY PROFILE STATUS [--group <id>] [--session <id>]`
- `PLAY PROFILE GROUP|SESSION SET|CLEAR ...`
- `PLAY OPTIONS|START <id>|TOKENS|CLAIM`
- `RULE ADD|RUN|TEST ...`
- `SKIN STATUS|CHECK|LIST|SHOW|SET|CLEAR`
- `SKIN SCAFFOLD <name>`
- `SKIN INSERT <name> CSS <css...>`
- `SKIN INSERT <name> SLOT <slot> <content...>`

## Gameplay State Model

Primary state file:

- `memory/bank/private/gameplay_state.json`

Runtime events file:

- `memory/bank/private/gameplay_events.ndjson`

Progression contract source:

- `core/services/progression_contract_service.py`
- `core/services/thin_gui_bridge_service.py`

## Lens and Skin Framework (Scaffold)

Lens/skin profile catalog:

- `core/config/lens_skin_game_catalog_v1_5.json`

Baseline game profiles:

- `hethack` / `nethack` (container: `library/hethack`)
- `elite` (container: `library/elite`)
- `crawler3d` (container: `library/crawler3d`, 3D lane)

Policy model:

- recommendations and fit checks are advisory in v1.5 unless explicit enforcement is enabled
- unavailable recommended skins must not hard-fail command execution

## Skin Content Insertion via ucode

`SKIN SCAFFOLD <name>` ensures:

- `themes/<name>/assets/ucode-overrides.css`
- `themes/<name>/assets/ucode-slots.json`
- `themes/<name>/theme.css` imports `ucode-overrides.css`

`SKIN INSERT` writes content through this scaffold:

- CSS path for GUI style overrides
- slot payload path for theme-integrated content blocks

## Compatibility Rules

- gameplay and lens command semantics remain stable across core and Wizard surfaces
- skin content insertion must stay under `themes/<name>/assets/` or theme-local CSS entrypoints
- 3D-specific rendering features must remain extension-owned (see 3DWORLD extension contract)

## Related

- `docs/specs/3DWORLD-EXTENSION-CONTRACT-v1.5.md`
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `core/commands/play_handler.py`
- `core/commands/gameplay_handler.py`
- `core/commands/skin_handler.py`
