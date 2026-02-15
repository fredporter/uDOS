---
title: Gameplay Wireframe Demo Template
type: story
version: "1.0.0"
description: "Tutorial/demo framework template for TOYBOX gameplay, RULE automations, and PLAY unlock flow."
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
allow_stdlib_commands: true
---

# Gameplay Wireframe Demo

Slide 1 - Purpose

This template is a wireframe-style tutorial:
- Demonstrates normalized gameplay variables
- Demonstrates interactive prompts
- Demonstrates RULE (if/then) paired with PLAY
- Demonstrates token unlock flow

-----

Slide 2 - Core State Scaffold

```story
name: wireframe_state
label: Wireframe gameplay state
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
      grid_id: "earth:wireframe:hub-01"
      x: 0
      y: 0
      z: 0
    metrics:
      events_processed: 0
      missions_completed: 0
      deaths: 0
      elite_jumps: 0
      elite_docks: 0
      rpgbbs_sessions: 0
      rpgbbs_messages: 0
      rpgbbs_quests: 0
      crawler3d_floors: 0
      crawler3d_objectives: 0
  unlock_tokens: []
  gates:
    dungeon_l32_amulet:
      completed: false
```

-----

Slide 3 - Custom Variable Scaffold

```story
name: wireframe_custom
label: Framework custom variables
type: object
required: true
default:
  stamina: 100
  morale: 50
  reputation:
    city: 0
    guild: 0
  discoveries:
    artifacts_found: 0
    regions_mapped: 0
  narrative_flags:
    tutorial_started: true
    tutorial_completed: false
```

-----

Slide 4 - Interactive Branch [Yes|No|OK|Other]

```story
name: tutorial_choice_start
label: Begin the guided mission?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

```story
name: tutorial_choice_start_other
label: If Other, enter custom action
type: text
required: false
placeholder: "Describe custom start action"
```

-----

Slide 5 - Runtime Payload Demo

Use this standardized payload shape from adapters:

```yaml
stats_delta:
  xp: 20
  hp: -5
  gold: 10
progress:
  level: 2
  achievement_id: "wireframe_first_step"
location:
  grid_id: "earth:wireframe:sector-02"
  x: 4
  y: 2
  z: 1
```

-----

Slide 6 - RULE + PLAY Wiring (Demo)

```text
RULE ADD rule.demo.start IF xp>=50 and level>=2 THEN TOKEN token.demo.start; PLAY dungeon
RULE ADD rule.demo.advance IF achievement_level>=1 and gold>=25 THEN TOKEN token.demo.advance; PLAY galaxy
RULE ADD rule.demo.ascension IF gate:dungeon_l32_amulet and achievement_level>=1 THEN TOKEN token.demo.ascension; PLAY ascension
```

-----

Slide 7 - Rule Test Prompt [Yes|No|OK|Other]

```story
name: tutorial_rule_test
label: Run rule test sequence now?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

-----

Slide 8 - Operator Checklist

Recommended operator flow:
1. `GPLAY STATUS`
2. `PLAY OPTIONS`
3. `RULE LIST`
4. `RULE TEST IF xp>=50 and level>=2`
5. `RULE RUN`
6. `PLAY CLAIM`

-----

Slide 9 - Template Extension Notes

To build production story variants from this template:
- Replace `grid_id` prefixes per era/profile
- Add era-specific tokens
- Add narrative-specific RULE conditions
- Keep normalized fields unchanged for adapter compatibility

