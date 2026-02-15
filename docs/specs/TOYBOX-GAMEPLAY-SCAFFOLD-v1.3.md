# TOYBOX Gameplay Scaffold (v1.3)

Status: scaffold implemented on 2026-02-15.

Companion specs:
- `docs/specs/TOYBOX-CONTAINER-VARIABLE-COMPARISON-v1.3.md`

Reference templates:
- `docs/examples/gameplay-wireframe-demo-script.md` (tutorial/wireframe scaffold)
- `docs/examples/historical-earthly-adventure-script.md` (deep baseline)
- `docs/examples/historical-earthly-adventure-ancient-script.md` (ancient variant)
- `docs/examples/historical-earthly-adventure-industrial-script.md` (industrial variant)
- seeded system copy: `core/framework/seed/bank/system/gameplay-wireframe-demo-script.md`

## Scope

- Hook gameplay into per-user Core variables: `xp`, `hp`, `gold`.
- Persist progression gate state for interactive requirements.
- Scaffold TOYBOX profiles for:
  - `hethack` (dungeon lens)
  - `elite` (galaxy lens)
  - `rpgbbs` (social dungeon/BBS lens)
  - `crawler3d` (3D crawler lens)
- Keep no-fork policy: upstream runtime ownership stays external; uDOS owns adapter, gating, and UI reskin.

## Core Runtime Hooks

- Service: `core/services/gameplay_service.py`
  - Persistent file: `memory/bank/private/gameplay_state.json`
  - Stores:
    - per-user stats (`xp`, `hp`, `gold`)
    - progression gates (`dungeon_l32_amulet`)
    - TOYBOX profile registry and active profile
    - role permission scaffold for gameplay/toybox actions
- Command: `GPLAY` via `core/commands/gameplay_handler.py`
  - `GPLAY STATUS`
  - `GPLAY STATS SET|ADD <xp|hp|gold> <value>`
  - `GPLAY GATE STATUS|COMPLETE|RESET <gate_id>`
  - `GPLAY TOYBOX LIST|SET <profile>`
  - `GPLAY PROCEED|NEXT|UNLOCK`
- Command: `PLAY` via `core/commands/play_handler.py`
  - `PLAY STATUS`
  - `PLAY OPTIONS`
  - `PLAY START <option_id>`
  - `PLAY TOKENS`
  - `PLAY CLAIM`
- Command: `RULE` via `core/commands/rule_handler.py`
  - `RULE ADD <rule_id> IF <condition> THEN <actions>`
  - `RULE RUN [rule_id]`
  - `RULE TEST IF <condition>`

## Interactive Gate Requirement

`UNLOCK/PROCEED/NEXT STEP` behavior is enforced through:

- canonical gate id: `dungeon_l32_amulet`
- completion target: dungeon level 32 + Amulet of Yendor retrieval
- proceed state:
  - blocked when gate is pending
  - unlocked when gate is completed

## TOYBOX Container Scaffold

- Library containers:
  - `library/hethack/container.json`
  - `library/elite/container.json`
  - `library/rpgbbs/container.json`
  - `library/crawler3d/container.json`
- Wizard lifecycle exposure:
  - `POST /api/containers/hethack/launch`
  - `POST /api/containers/elite/launch`
  - `POST /api/containers/rpgbbs/launch`
  - `POST /api/containers/crawler3d/launch`
  - proxy routes:
    - `/ui/hethack/*`
    - `/ui/elite/*`
    - `/ui/rpgbbs/*`
    - `/ui/crawler3d/*`

Initial launch commands now point to adapter services:

- `python3 -m wizard.services.toybox.hethack_adapter`
- `python3 -m wizard.services.toybox.elite_adapter`
- `python3 -m wizard.services.toybox.rpgbbs_adapter`
- `python3 -m wizard.services.toybox.crawler3d_adapter`

Upstream runtime command resolution:

- `TOYBOX_HETHACK_CMD` overrides hethack runtime command.
- `TOYBOX_ELITE_CMD` overrides elite runtime command.
- `TOYBOX_RPGBBS_CMD` overrides rpgbbs runtime command.
- `TOYBOX_CRAWLER3D_CMD` overrides crawler3d runtime command.
- Without overrides, adapters probe common runtime binaries on `PATH`.

## Local Setup Scripts

- `library/hethack/setup.sh`
- `library/elite/setup.sh`
- `library/rpgbbs/setup.sh`
- `library/crawler3d/setup.sh`
- unified runner: `python3 wizard/tools/toybox_setup.py [all|hethack|elite|rpgbbs|crawler3d] [--activate-dotenv]`

Script behavior:

- clones/fetches upstream source into:
  - `memory/library/containers/hethack/src`
  - `memory/library/containers/elite/src`
  - `memory/library/containers/rpgbbs/src`
  - `memory/library/containers/crawler3d/src`
- builds locally when common toolchains are present (`make`/`cmake`)
- writes launcher wrappers into `memory/library/containers/<profile>/bin`
- writes activation exports into `memory/bank/private/toybox-runtime.env`

Optional release-binary fallback:

- `TOYBOX_HETHACK_BIN_URL=<github-asset-url>` to download a prebuilt hethack binary
- `TOYBOX_ELITE_BIN_URL=<github-asset-url>` to download a prebuilt elite binary
- `TOYBOX_ELITE_RELEASE_ZIP_URL=<url>` defaults to upstream `E-TNK v1.2` zip
- `TOYBOX_ELITE_WINE_TARBALL_URL=<url>` defaults to portable Wine bundle (no system install required)
- `TOYBOX_RPGBBS_BIN_URL=<github-asset-url>` to download a prebuilt rpgbbs binary
- `TOYBOX_CRAWLER3D_BIN_URL=<github-asset-url>` to download a prebuilt crawler3d binary

## Event Contract (Runtime -> Core)

- File: `memory/bank/private/gameplay_events.ndjson`
- Producer: TOYBOX adapter services.
- Consumer: `GameplayService.tick()` on Core dispatch path.
- Event row shape:
  - `ts` (ISO datetime)
- `source` (`toybox:hethack`, `toybox:elite`)
  - plus `toybox:rpgbbs`, `toybox:crawler3d`
  - `type` (event id)
  - `payload` (event details)

Current mapped event ids:

- hethack:
  - `HETHACK_LEVEL_REACHED`
  - `HETHACK_AMULET_RETRIEVED`
  - `HETHACK_DEATH`
- elite:
  - `ELITE_HYPERSPACE_JUMP`
  - `ELITE_DOCKED`
  - `ELITE_MISSION_COMPLETE`
  - `ELITE_TRADE_PROFIT`
- rpgbbs:
  - `RPGBBS_SESSION_START`
  - `RPGBBS_MESSAGE_EVENT`
  - `RPGBBS_QUEST_COMPLETE`
- crawler3d:
  - `CRAWLER3D_FLOOR_REACHED`
  - `CRAWLER3D_LOOT_FOUND`
  - `CRAWLER3D_OBJECTIVE_COMPLETE`

Gate automation rule:

- `dungeon_l32_amulet` auto-completes only when:
  - max observed hethack depth >= 32, and
  - `HETHACK_AMULET_RETRIEVED` has been observed.

PLAY token automation rule:

- Unlock tokens are granted from runtime-derived conditions (`xp`, `achievement_level`, gate completion, and container metrics), not manual completion commands.

## Next Dev Rounds

1. Replace stubs with adapter runtimes (PTY for dungeon, framebuffer/terminal hybrid for galaxy).
2. Emit canonical gameplay events (`ENTER`, `INTERACT`, `COMPLETE`) to Core tick/update paths.
3. Add parser/runtime hook so workflow progression can require gate completion before moving to next milestone.

## TUI Theme/Layer Switching Contract (Current)

TOYBOX profile switching and TUI message-layer switching are separate controls:

- Gameplay profile:
  - `GPLAY TOYBOX SET hethack|elite|rpgbbs|crawler3d`
- Message-level layer/theme hinting:
  - `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy`
  - `UDOS_TUI_MESSAGE_THEME=<theme>`

Reference operator flows:

```bash
# Dungeon runtime + dungeon messaging
GPLAY TOYBOX SET hethack
export UDOS_TUI_MAP_LEVEL=dungeon
export UDOS_TUI_MESSAGE_THEME=dungeon

# Galaxy runtime + galaxy messaging
GPLAY TOYBOX SET elite
export UDOS_TUI_MAP_LEVEL=galaxy
export UDOS_TUI_MESSAGE_THEME=pilot
```

This contract is TUI message-IO only and intentionally separate from GUI/web styling work.
