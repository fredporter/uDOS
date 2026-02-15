# TOYBOX Gameplay Scaffold (v1.3)

Status: scaffold implemented on 2026-02-15.

## Scope

- Hook gameplay into per-user Core variables: `xp`, `hp`, `gold`.
- Persist progression gate state for interactive requirements.
- Scaffold TOYBOX profiles for:
  - `hethack` (dungeon lens)
  - `elite` (galaxy lens)
- Keep no-fork policy: upstream runtime ownership stays external; uDOS owns adapter, gating, and UI reskin.

## Core Runtime Hooks

- Service: `core/services/gameplay_service.py`
  - Persistent file: `memory/bank/private/gameplay_state.json`
  - Stores:
    - per-user stats (`xp`, `hp`, `gold`)
    - progression gates (`dungeon_l32_amulet`)
    - TOYBOX profile registry and active profile
    - role permission scaffold for gameplay/toybox actions
- Command: `GAMEPLAY` via `core/commands/gameplay_handler.py`
  - `GAMEPLAY STATUS`
  - `GAMEPLAY STATS SET|ADD <xp|hp|gold> <value>`
  - `GAMEPLAY GATE STATUS|COMPLETE|RESET <gate_id>`
  - `GAMEPLAY TOYBOX LIST|SET <profile>`
  - `GAMEPLAY PROCEED|NEXT|UNLOCK`

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
- Wizard lifecycle exposure:
  - `POST /api/containers/hethack/launch`
  - `POST /api/containers/elite/launch`
  - proxy routes:
    - `/ui/hethack/*`
    - `/ui/elite/*`

Initial launch commands now point to adapter services:

- `python3 -m wizard.services.toybox.hethack_adapter`
- `python3 -m wizard.services.toybox.elite_adapter`

Upstream runtime command resolution:

- `TOYBOX_HETHACK_CMD` overrides hethack runtime command.
- `TOYBOX_ELITE_CMD` overrides elite runtime command.
- Without overrides, adapters probe common runtime binaries on `PATH`.

## Event Contract (Runtime -> Core)

- File: `memory/bank/private/gameplay_events.ndjson`
- Producer: TOYBOX adapter services.
- Consumer: `GameplayService.tick()` on Core dispatch path.
- Event row shape:
  - `ts` (ISO datetime)
  - `source` (`toybox:hethack`, `toybox:elite`)
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

Gate automation rule:

- `dungeon_l32_amulet` auto-completes only when:
  - max observed hethack depth >= 32, and
  - `HETHACK_AMULET_RETRIEVED` has been observed.

## Next Dev Rounds

1. Replace stubs with adapter runtimes (PTY for dungeon, framebuffer/terminal hybrid for galaxy).
2. Emit canonical gameplay events (`ENTER`, `INTERACT`, `COMPLETE`) to Core tick/update paths.
3. Add parser/runtime hook so workflow progression can require gate completion before moving to next milestone.
