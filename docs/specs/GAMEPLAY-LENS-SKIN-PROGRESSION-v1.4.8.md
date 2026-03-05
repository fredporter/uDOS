# Gameplay LENS + SKIN Progression Contract (v1.4.8)

Superseded for command/runtime authority by:
- `docs/specs/GAMEPLAY-COMMAND-CONTRACT-v1.5.md`

## Purpose

Define and lock the shared progression contract consumed by `PLAY LENS`, `SKIN`, and `MODE`, so all three surfaces use the same readiness and advisory model.

## Current Implementation Summary

- Shared contract service: `core/services/progression_contract_service.py`.
- Progression state source: `core/services/gameplay_service.py`.
- `PLAY LENS STATUS` now emits readiness + recommendation lines from the shared contract.
- `SKIN` policy context now emits non-blocking progression drift hints (`policy_flag`) from the shared contract.
- `MODE STATUS` fit context consumes the same skin/lens policy logic.

## Canonical Progression Variables

Single source of truth (per user):

- `xp`
- `hp`
- `gold`
- `level`
- `achievement_level`
- `achievements[]`
- `metrics.*` (lens/runtime-derived counters)
- `unlock_tokens[]`

Storage:

- `memory/bank/private/gameplay_state.json`

## Command Alignment Targets

### PLAY LENS (primary gameplay surface)

- Must always report:
  - active lens
  - progression readiness summary
  - blocked requirements (if any)
  - relevant variable snapshot (`xp`, `gold`, `achievement_level`)
- Must support progression-aware recommendations:
  - example: “need +40 XP to unlock galaxy route”
- Compact operator form supported for quick inspection:
  - `PLAY LENS STATUS --compact`

### SKIN (presentation surface)

- Remains user-selectable and non-blocking during development.
- Adds progression-awareness as **flags**, not hard gates:
  - when skin/lens pairing is low-fit, return `policy_flag` + guidance.
- Never mutates progression state directly.
- Advisory command supported:
  - `SKIN CHECK`

### MODE (cross-surface inspection)

- Compact HUD status now includes mode + policy + progression-fit context:
  - `MODE STATUS --compact`
- Output includes mode, theme, lens, skin, fit state, and key progression counters.

## Canonical Mapping Model

### 1) Progression variables -> unlock token rules

Token requirements are sourced from `PLAY_UNLOCK_RULES` and normalized as requirement labels:

| Token | Requirement labels |
|---|---|
| `token.toybox.xp_100` | `xp>=100` |
| `token.toybox.achievement_l1` | `achievement_level>=1` |
| `token.toybox.navigator_l1` | `elite_jumps>=5` |
| `token.toybox.social_l1` | `rpgbbs_quests>=1` |
| `token.toybox.crawler_l1` | `crawler3d_floors>=10` |
| `token.toybox.ascension` | `gate:dungeon_l32_amulet`, `achievement_level>=1` |

### 2) Unlock/requirements -> lens readiness

Lens readiness is resolved through mapped `PLAY_OPTIONS`:

| Lens | Option ID | Typical blocked requirements |
|---|---|---|
| `hethack` | `dungeon` | none (baseline) |
| `elite` | `galaxy` | `xp>=100` |
| `rpgbbs` | `social` | `achievement_level>=1` |
| `crawler3d` | `ascension` | `gate:dungeon_l32_amulet`, `achievement_level>=1` |

### 3) Active lens -> recommended skins

Skin recommendations are advisory-only in current development rounds:

| Lens | Recommended skins |
|---|---|
| `hethack` | `dungeon`, `fantasy`, `hacker`, `default` |
| `elite` | `galaxy`, `pilot`, `bridge`, `default` |
| `rpgbbs` | `roleplay`, `fantastic`, `default` |
| `crawler3d` | `foundation`, `survival`, `adventure`, `default` |

## Mode/Policy Behavior

- Current development phase: flag-only behavior.
- No enforced blocking for SKIN/LENS mismatch until pre-launch boundary enforcement switch.

## Validation

Covered by:

- `core/tests/progression_contract_service_test.py`
- `core/tests/skin_progression_policy_test.py`
- `core/tests/gameplay_service_test.py`

## Acceptance Criteria

- `PLAY LENS`, `SKIN`, and `MODE` consume one shared progression contract.
- Lens availability/blocked state is inspectable with concrete requirement labels.
- SKIN guidance is visible and informative without restricting choice in dev rounds.
- Mapping contract is documented and test-covered.
