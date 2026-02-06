# Vibe Router Contract (Core Baseline)

**Status:** Draft
**Last Updated:** 2026-02-06

## Purpose
Define the baseline model routing rules used by `/core` via Vibe-CLI. Wizard may extend these rules but cannot bypass offline restrictions.

## Scope
Applies to `/core`, `/dev`, and all submodules. Wizard can add online providers but must enforce policy.

## Inputs
Required:
- `intent`: `design | chat | code`
- `mode`: `conversation | creative | code`
- `privacy`: `private | internal | public`

Optional:
- `offline_required`: boolean
- `ghost_mode`: boolean
- `task_hint`: string

## Output
The router returns:
- `provider`: `ollama | wizard`
- `model`: string
- `reason`: string
- `online_allowed`: boolean

## Baseline Routing Rules (Core)
1. If `ghost_mode` is true, force:
   - `provider=ollama`
   - `online_allowed=false`
2. If `privacy=private` or `offline_required=true`, force local only.
3. Default model mapping:
   - `intent=chat` → `mistral-small`
   - `intent=design` → `mistral-large`
   - `intent=code` → `devstral-small-2`

## Wizard Extensions
1. Wizard may map `provider=wizard` when policy allows online access.
2. Wizard must not allow online access when:
   - `privacy=private`
   - `offline_required=true`
   - `ghost_mode=true`

## Compliance
All routing decisions must be logged with:
- `intent`, `mode`, `privacy`, `provider`, `model`, and policy flags
- Estimated cost for online requests
