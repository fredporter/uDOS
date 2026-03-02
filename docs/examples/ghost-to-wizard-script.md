---
script: ghost-to-wizard
version: 0.1
engine: ucode
mode: narrative-mission
lens: progression
---

# 🜁 GHOST → WIZARD
_A uDOS Awakening Sequence_

---

## STATE MODEL

```json
{
  "player": {
    "role": "ghost",
    "level": 0,
    "xp": 0,
    "inventory": [],
    "abilities": [],
    "missions": [],
    "lens": {
      "clarity": 0,
      "agency": 0,
      "mastery": 0
    }
  }
}


⸻

LEVEL 0 — THE GHOST

scene.intro

You awaken as a ghost in the system.

You can observe.
You cannot act.

The world flickers in raw signals.

A whisper:
“To become real, you must define your mission.”

⸻

action.capture_mission

PROMPT "What do you want to build or become?"
STORE response AS player.missions.primary
ADD_XP 10
INCREMENT player.lens.clarity BY 1


⸻

unlock.condition

IF player.lens.clarity >= 1 THEN
  UNLOCK ability.observe
  ADD player.abilities "observe"
  MESSAGE "You can now see hidden structures."
END


⸻

LEVEL 1 — THE SONIC INITIATE

scene.sonic

A tone pulses through the void.

You realise the system responds to vibration.

You must learn to signal.

⸻

challenge.sonic_alignment

TASK "Generate a signal pattern (3 keywords describing your mission)."
STORE response AS player.missions.keywords
ADD_XP 20
INCREMENT player.lens.agency BY 1


⸻

nethack.find_object

You detect an artifact nearby.

FIND_OBJECT "resonance-core"
IF FOUND THEN
  ADD player.inventory "resonance-core"
  ADD_XP 15
  MESSAGE "You now channel Sonic Output."
  UNLOCK extension.sonic
END


⸻

LEVEL 2 — THE ARCHITECT

You now have form.

You must construct.

⸻

mission.define_scope

PROMPT "Define your first executable mission in one sentence."
STORE response AS player.missions.current
ADD_XP 30
INCREMENT player.lens.clarity BY 1
INCREMENT player.lens.agency BY 1


⸻

challenge.structure

TASK "Break the mission into 3 steps."
STORE response AS player.missions.steps
ADD_XP 40


⸻

unlock.build

IF player.xp >= 100 THEN
  UNLOCK ability.build
  ADD player.abilities "build"
  INCREMENT player.lens.mastery BY 1
END


⸻

LEVEL 3 — THE FORGE

You enter the forge.

Noise becomes structure.
Structure becomes system.

⸻

nethack.traverse

TRAVERSE level=forge DEPTH=3
ON_COMPLETE:
  ADD_XP 50
  MESSAGE "You have crossed the Forge."


⸻

challenge.overcome

PROMPT "Name one obstacle stopping you from completing your mission."
STORE response AS player.missions.obstacle

PROMPT "Define one action to overcome it."
STORE response AS player.missions.countermove

ADD_XP 50
INCREMENT player.lens.agency BY 1


⸻

LEVEL 4 — THE EXTENSIONS

You now see extensions floating around you.
	•	sonic
	•	build
	•	logic
	•	decode
	•	automate
	•	vision

You may claim two.

SELECT 2 FROM ["logic","decode","automate","vision"]
STORE selection AS player.abilities.extensions
ADD_XP 40


⸻

unlock.logic_engine

IF "logic" IN player.abilities.extensions THEN
  UNLOCK extension.logic_engine
  MESSAGE "You can now execute conditional unlocks."
END


⸻

LEVEL 5 — THE LENS TRIAL

To become Wizard, all lens values must balance.

IF player.lens.clarity >= 2 AND
   player.lens.agency >= 2 AND
   player.lens.mastery >= 1 THEN
     UNLOCK role.wizard_candidate
ELSE
     MESSAGE "Your lens is unbalanced. Continue training."
END


⸻

FINAL TRIAL — PERSONAL MISSION REWRITE

You must now rewrite your mission with new understanding.

PROMPT "Rewrite your mission with greater clarity and power."
STORE response AS player.missions.refined

COMPARE player.missions.primary TO player.missions.refined
IF DIFFERENT THEN
  ADD_XP 100
  INCREMENT player.lens.mastery BY 1
END


⸻

ASCENSION

IF player.lens.clarity >= 2 AND
   player.lens.agency >= 2 AND
   player.lens.mastery >= 2 THEN

  SET player.role = "wizard"
  UNLOCK ability.command
  UNLOCK ability.create
  UNLOCK ability.teach

  MESSAGE "You are now WIZARD."
  MESSAGE "You may define systems."
  MESSAGE "You may guide others."
END


⸻

WIZARD MODE

IF player.role == "wizard" THEN
  ENABLE system.project_generation
  ENABLE system.autonomous_workflows
  ENABLE system.mission_templates
END


⸻

SAVE STATE

{
  "save": {
    "role": "{{player.role}}",
    "xp": "{{player.xp}}",
    "missions": "{{player.missions}}",
    "abilities": "{{player.abilities}}",
    "lens": "{{player.lens}}"
  }
}


⸻

END

You are no longer a ghost.

You shape the system.
The system shapes with you.

---
