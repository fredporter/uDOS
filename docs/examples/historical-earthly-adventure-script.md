---
title: Historical Earthly Adventure Template
type: story
version: "1.1.0"
description: "Deep immersive choose-your-own-adventure template for historical earthly roleplay with normalized TOYBOX variables and RULE/PLAY automation hooks."
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
allow_stdlib_commands: true
---

# Historical Earthly Adventure

Slide 1 - Oath At The Crossroads

Your boots sink into rain-dark soil as bells ring from the old city walls.
In the year `$world_year`, history is unstable, and your choices now shape what survives.
You are not a tourist. You are a witness, courier, and keeper of fragments.

-----

Slide 2 - Canonical Gameplay State (Normalized)

```story
name: gameplay_state
label: Normalized gameplay state scaffold
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
      grid_id: "earth:history:district-01"
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

Slide 3 - Deep Immersion Variables (Custom + Future)

```story
name: future_variables
label: Deeper gameplay variables (custom)
type: object
required: true
default:
  reputation:
    local_citizens: 0
    guilds: 0
    crown: 0
  stamina: 100
  knowledge:
    history: 0
    language: 0
    engineering: 0
  inventory_weight: 0
  weather_state: "clear"
  time:
    era: "medieval"
    day_phase: "dawn"
  diplomacy:
    treaties_signed: 0
  discoveries:
    artifacts_found: 0
    regions_mapped: 0
  morale: 75
  renown: 0
  fatigue: 10
  stress: 5
  faction_alignment:
    scholars: 0
    merchants: 0
    rebels: 0
  survival:
    food_days: 3
    water_days: 3
    shelter_quality: 1
  narrative_flags:
    vow_to_city: false
    oath_broken: false
    artifact_touched: false
```

-----

Slide 4 - Character Seed

```story
name: explorer_name
label: Explorer name
type: text
required: true
placeholder: "Enter your name"
```

```story
name: origin_city
label: Origin city
type: text
required: true
placeholder: "e.g. Alexandria"
```

```story
name: starting_class
label: Starting class
type: select
required: true
options:
  - scholar: Scholar
  - cartographer: Cartographer
  - envoy: Envoy
  - artisan: Artisan
```

-----

Slide 5 - First Turning [Yes|No|OK|Other]

A tired archivist offers you a sealed ledger and says, "If this burns, the city forgets itself."
Do you accept custody of the ledger?

```story
name: choice_archive_contract
label: Choose your path
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

```story
name: choice_archive_contract_other
label: If Other, specify your action
type: text
required: false
placeholder: "Describe your custom action"
```

-----

Slide 6 - Travel Choice [Yes|No|OK|Other]

At dawn, two roads open:
- Fortress route: dangerous, but rich in relic clues.
- Market route: safer, with political intelligence.

```story
name: choice_fortress_route
label: Proceed to fortress route?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

-----

Slide 7 - Encounter Choice [Yes|No|OK|Other]

A cloaked messenger offers a shortcut through a closed district.
Will you follow the messenger?

```story
name: choice_messenger_shortcut
label: Follow the messenger?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

```story
name: messenger_other_action
label: If Other, what do you do instead?
type: text
required: false
placeholder: "Describe your strategy"
```

-----

Slide 8 - Runtime Event Normalization Payload (Template)

Use this payload shape when adapters emit runtime events:

```yaml
stats_delta:
  xp: 25
  hp: -5
  gold: 40
progress:
  level: 2
  achievement_id: "earth_archive_discovered"
location:
  grid_id: "earth:history:fortress-02"
  x: 14
  y: 6
  z: 1
```

-----

Slide 9 - RULE/PLAY Condition Contract

Use RULE as gameplay automation paired with PLAY.

Example rule definitions:

```text
RULE ADD rule.history.route_fortress IF xp>=80 and level>=2 THEN TOKEN token.history.fortress_access; PLAY dungeon
RULE ADD rule.history.city_trust IF achievement_level>=1 and gold>=50 THEN TOKEN token.history.city_trust
RULE ADD rule.history.ascension IF gate:dungeon_l32_amulet and achievement_level>=1 THEN TOKEN token.history.ascension; PLAY ascension
```

Supported IF condition patterns:
- `xp>=N`
- `hp>=N`
- `gold>=N`
- `level>=N`
- `achievement_level>=N`
- `metric.<name>>=N`
- `gate:<gate_id>`
- `token:<token_id>`
- `toybox=<profile>`

Supported THEN actions:
- `TOKEN <token_id>`
- `PLAY <option>`
- `GATE COMPLETE <gate_id>`
- `STAT ADD <xp|hp|gold> <delta>`
- `ACHIEVE <achievement_id>`

-----

Slide 10 - Unlock Decision [Yes|No|OK|Other]

```story
name: unlock_ready_check
label: Should this chapter unlock the next stage now?
type: select
required: true
options:
  - yes: Yes
  - no: No
  - ok: OK
  - other: Other
```

-----

Slide 11 - Storytelling Verbage Hooks

Use these narrative tone snippets in your adapters/prompts:
- "You feel the century shift beneath your feet."
- "Every map line you draw becomes law for those who come after."
- "The city remembers favors longer than victories."
- "A quiet act here can thunder through generations."

-----

Slide 12 - Ending

Template complete.

Suggested runtime commands after adapting this file:
- `GPLAY STATUS`
- `PLAY OPTIONS`
- `PLAY START dungeon`
- `PLAY CLAIM`
- `RULE LIST`
- `RULE RUN`
