# TOYBOX Container Variable Comparison (v1.3)

Status: drafted on 2026-02-15 against current scaffold code.

## Purpose

Define a cross-container variable model so TOYBOX runtimes can feed a shared uDOS gameplay layer without forking upstream game code.

Containers covered:

- `hethack` (NetHack-class dungeon runtime)
- `elite` (galaxy runtime)
- `rpgbbs` (social dungeon/BBS runtime)
- `crawler3d` (3D crawler runtime)

## Canonical Core Variables

| Canonical variable | Type | Current state | Source of truth |
| --- | --- | --- | --- |
| `xp` | integer | Implemented | `core/services/gameplay_service.py` user stats |
| `hp` | integer | Implemented | `core/services/gameplay_service.py` user stats |
| `gold` | integer | Implemented | `core/services/gameplay_service.py` user stats |
| `level` | integer | Derived by events, not persisted as top-level stat | Adapter event payload (`depth`, mission progression cues) |
| `achievement` | string/list | Not yet first-class; represented via gate completion + notes | Gameplay gates + event notes |
| `location.grid` | object/string | Not yet first-class | Future normalized adapter payload |
| `location.z` | integer | Partially derived (`depth`) | Adapter event payload depth |

## Current Event-to-Stat Deltas (Implemented)

These deltas are live in `GameplayService._apply_event`.

| Event type | XP delta | HP delta | Gold delta | Notes |
| --- | --- | --- | --- | --- |
| `HETHACK_LEVEL_REACHED` | `+10` | `0` | `0` | Also updates max depth tracker |
| `HETHACK_AMULET_RETRIEVED` | `+500` | `0` | `+1000` | Participates in gate unlock |
| `HETHACK_DEATH` | `0` | `-25` (clamped at 0) | `0` | Death penalty |
| `ELITE_HYPERSPACE_JUMP` | `+15` | `0` | `0` | Travel progression |
| `ELITE_DOCKED` | `+20` | `0` | `0` | Docking progression |
| `ELITE_MISSION_COMPLETE` | `+100` | `0` | `+250` | Mission reward |
| `ELITE_TRADE_PROFIT` | `+max(1, profit//50)` | `0` | `+profit` | Profit is payload-driven |
| `RPGBBS_SESSION_START` | `+5` | `0` | `0` | Session engagement |
| `RPGBBS_MESSAGE_EVENT` | `+3` | `0` | `0` | Social interaction |
| `RPGBBS_QUEST_COMPLETE` | `+40` | `0` | `+25` | Quest completion |
| `CRAWLER3D_FLOOR_REACHED` | `+max(5, floor*2)` | `0` | `0` | Depth progression |
| `CRAWLER3D_LOOT_FOUND` | `+5` | `0` | `+15` | Loot pickup |
| `CRAWLER3D_OBJECTIVE_COMPLETE` | `+50` | `0` | `+75` | Milestone reward |

## Container Comparison

| Container | Native progression concept | Native resource concept | Location model | Current adapter events | Current canonical mapping |
| --- | --- | --- | --- | --- | --- |
| `hethack` | Dungeon depth + artifact retrieval | Gold/items from run | Tile/grid dungeon with depth | `HETHACK_LEVEL_REACHED`, `HETHACK_AMULET_RETRIEVED`, `HETHACK_DEATH` | Strongest fit for `level`, `location.z`, gate progression |
| `elite` | Flight, jumps, missions | Credits/profit | Star systems + stations | `ELITE_HYPERSPACE_JUMP`, `ELITE_DOCKED`, `ELITE_MISSION_COMPLETE`, `ELITE_TRADE_PROFIT` | Strongest fit for economy (`gold`) and mission XP |
| `rpgbbs` | Session + quest + social board progress | Optional economy per door game | Text rooms/boards/channels | `RPGBBS_SESSION_START`, `RPGBBS_MESSAGE_EVENT`, `RPGBBS_QUEST_COMPLETE` | Best fit for low-intensity XP and social achievements |
| `crawler3d` | Floor/depth and objective clears | Loot/treasure | 3D dungeon coordinates + floor | `CRAWLER3D_FLOOR_REACHED`, `CRAWLER3D_LOOT_FOUND`, `CRAWLER3D_OBJECTIVE_COMPLETE` | Mirrors dungeon profile for depth/gold/xp |

## Proposed Normalized Variable Contract

Adapters should emit payload fields that can be consumed uniformly:

| Field | Description | Example |
| --- | --- | --- |
| `progress.level` | Session progression number in container terms | `32` |
| `progress.achievement_id` | Canonical achievement key | `amulet_of_yendor` |
| `stats_delta.xp` | XP change | `+40` |
| `stats_delta.hp` | HP change | `-10` |
| `stats_delta.gold` | Gold/credits change normalized to `gold` | `+250` |
| `location.grid_id` | Logical map namespace | `dungeon:main` / `galaxy:chart1` |
| `location.x` | Horizontal coordinate (if known) | `14` |
| `location.y` | Vertical coordinate (if known) | `7` |
| `location.z` | Depth/altitude tier | `32` or `0` |

## Location Grid/Z Mapping Guidance

| Container | `location.grid_id` guideline | `location.z` guideline |
| --- | --- | --- |
| `hethack` | `dungeon:<branch-or-main>` | Dungeon depth (positive downward) |
| `crawler3d` | `crawler3d:<zone>` | Floor/depth level |
| `elite` | `galaxy:<chart-or-sector>` | Usually `0`; use signed value only if vertical sectoring exists |
| `rpgbbs` | `bbs:<board-or-room>` | Default `0` unless game door exposes depth/floor |

## Achievement Normalization

Current scaffold uses gate completion as the achievement mechanism.

| Canonical achievement | Trigger container/event | Current status |
| --- | --- | --- |
| `dungeon_l32_amulet` | `hethack` with depth `>=32` and `HETHACK_AMULET_RETRIEVED` | Implemented and auto-completed by runtime events |
| `elite_first_mission` | `ELITE_MISSION_COMPLETE` | Proposed |
| `rpgbbs_first_quest` | `RPGBBS_QUEST_COMPLETE` | Proposed |
| `crawler3d_floor_10` | `CRAWLER3D_FLOOR_REACHED` where floor `>=10` | Proposed |

## Installer and Runtime Variable Matrix

| Container | Setup script | Runtime command env | Install source strategy |
| --- | --- | --- | --- |
| `hethack` | `library/hethack/setup.sh` | `TOYBOX_HETHACK_CMD` | git clone/build, optional binary URL |
| `elite` | `library/elite/setup.sh` | `TOYBOX_ELITE_CMD` | git clone/build, optional upstream zip + portable wine |
| `rpgbbs` | `library/rpgbbs/setup.sh` | `TOYBOX_RPGBBS_CMD` | git clone/build, optional binary URL |
| `crawler3d` | `library/crawler3d/setup.sh` | `TOYBOX_CRAWLER3D_CMD` | git clone/build, optional binary URL |

Unified bootstrap:

`python3 wizard/tools/toybox_setup.py [all|hethack|elite|rpgbbs|crawler3d] [--activate-dotenv]`

## Practical Notes

- `xp`, `hp`, and `gold` are already runtime-driven from adapter events.
- `level`, `achievement`, and `location-grid/z` are partially implemented and should be finalized via a canonical payload schema.
- `PLAY` command aligns these standardized fields to conditional options and unlock-token progression (`PLAY OPTIONS`, `PLAY START`, `PLAY CLAIM`).
- Keep no-fork policy: normalization belongs in adapters and Core mapping, not in upstream game code changes.
