---
title: Historical Earthly Adventure (Ancient Era)
type: story
version: "1.1.0"
description: "Ancient era variant with temple-city grids and token tracks."
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
allow_stdlib_commands: true
---

# Historical Earthly Adventure - Ancient Era

Slide 1 - Bronze Dawn

The river floods, the granaries open, and scribes tally debts on clay.
You stand between temple authority and hungry neighborhoods.

-----

Slide 2 - Era Defaults

```story
name: ancient_gameplay_state
label: Ancient era normalized state
type: object
required: true
default:
  stats:
    xp: 0
    hp: 100
    gold: 0
  progress:
    level: 1
    achievement_level: 0
    achievements: []
    location:
      grid_id: "earth:ancient:temple-city-01"
      x: 2
      y: 1
      z: 0
    metrics:
      events_processed: 0
      missions_completed: 0
      deaths: 0
      rpgbbs_quests: 0
      crawler3d_floors: 0
  unlock_tokens: []
```

-----

Slide 3 - Ancient Variables

```story
name: ancient_custom_variables
label: Ancient custom variables
type: object
required: true
default:
  city_state_reputation:
    temple: 0
    guild: 0
    militia: 0
  tribute:
    grain: 0
    silver: 0
  omens_seen: 0
  caravan_safety: 50
  narrative_flags:
    oracle_consulted: false
    tablet_deciphered: false
```

-----

Slide 4 - Choice [Yes|No|OK|Other]

Will you carry the king's tablet to the floodplain archive?

```story
name: ancient_choice_tablet
label: Carry the tablet?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

-----

Slide 5 - RULE/PLAY Track (Ancient Tokens)

```text
RULE ADD rule.ancient.temple IF xp>=60 and level>=2 THEN TOKEN token.ancient.temple_pass; PLAY dungeon
RULE ADD rule.ancient.oracle IF achievement_level>=1 THEN TOKEN token.ancient.oracle_whisper
RULE ADD rule.ancient.citadel IF gate:dungeon_l32_amulet and xp>=200 THEN TOKEN token.ancient.citadel_key; PLAY ascension
```

Ancient token goals:
- `token.ancient.temple_pass`
- `token.ancient.oracle_whisper`
- `token.ancient.citadel_key`

-----

Slide 6 - Runtime Payload Example

```yaml
stats_delta:
  xp: 30
  hp: -10
  gold: 15
progress:
  level: 2
  achievement_id: "ancient_tablet_secured"
location:
  grid_id: "earth:ancient:ziggurat-02"
  x: 7
  y: 3
  z: 1
```

-----

Slide 7 - Closing

If you choose well, your name is etched in fired clay.
If you fail, history survives without you.

