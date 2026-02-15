---
title: Historical Earthly Adventure (Industrial Era)
type: story
version: "1.1.0"
description: "Industrial era variant with rail-city grids and token tracks."
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
allow_stdlib_commands: true
---

# Historical Earthly Adventure - Industrial Era

Slide 1 - Smoke Horizon

Steam whistles split the morning fog as workers flood toward the ironworks.
Your choices decide whether this city mechanizes with justice or fear.

-----

Slide 2 - Era Defaults

```story
name: industrial_gameplay_state
label: Industrial era normalized state
type: object
required: true
default:
  stats:
    xp: 0
    hp: 100
    gold: 25
  progress:
    level: 1
    achievement_level: 0
    achievements: []
    location:
      grid_id: "earth:industrial:rail-district-01"
      x: 5
      y: 5
      z: 0
    metrics:
      events_processed: 0
      missions_completed: 0
      deaths: 0
      elite_jumps: 0
      elite_docks: 0
      crawler3d_objectives: 0
  unlock_tokens: []
```

-----

Slide 3 - Industrial Variables

```story
name: industrial_custom_variables
label: Industrial custom variables
type: object
required: true
default:
  labor_relations:
    worker_trust: 0
    owner_trust: 0
  machine_integrity: 100
  coal_stock: 20
  city_smog_index: 40
  patents_registered: 0
  narrative_flags:
    strike_called: false
    prototype_approved: false
```

-----

Slide 4 - Choice [Yes|No|OK|Other]

A foreman asks you to suppress tonight's worker meeting.
Do you comply?

```story
name: industrial_choice_meeting
label: Suppress worker meeting?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

-----

Slide 5 - RULE/PLAY Track (Industrial Tokens)

```text
RULE ADD rule.industrial.railpass IF xp>=80 and gold>=100 THEN TOKEN token.industrial.rail_pass; PLAY galaxy
RULE ADD rule.industrial.union IF achievement_level>=1 and metric.missions_completed>=1 THEN TOKEN token.industrial.union_charter
RULE ADD rule.industrial.engine IF level>=3 and metric.crawler3d_objectives>=1 THEN TOKEN token.industrial.engine_blueprint; PLAY social
```

Industrial token goals:
- `token.industrial.rail_pass`
- `token.industrial.union_charter`
- `token.industrial.engine_blueprint`

-----

Slide 6 - Runtime Payload Example

```yaml
stats_delta:
  xp: 45
  hp: -5
  gold: 60
progress:
  level: 3
  achievement_id: "industrial_engine_trial"
location:
  grid_id: "earth:industrial:foundry-03"
  x: 11
  y: 9
  z: 2
```

-----

Slide 7 - Closing

When gears seize, people starve.
When agreements hold, cities become futures.

