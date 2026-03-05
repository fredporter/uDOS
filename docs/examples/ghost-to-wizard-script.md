---
script: ghost-to-wizard
version: "1.5"
engine: ucode
mode: onboarding-mission
lens: progression
save_file: ~/.udos/player.json
estimated_duration_minutes: 45
---

# Ghost to Wizard

A playable onboarding mission where each action configures real uDOS runtime state.

## Mission Contract

- Every objective maps to a real command and setup outcome.
- Mission progress is persisted and resumable.
- Unlocks are additive and role-gated.
- Event output uses TUI block events (`narration`, `objective`, `challenge`, `reward`, `unlock`, `progress`).

## Initial State

```json
{
  "player": {
    "role": "ghost",
    "xp": 0,
    "inventory": [],
    "abilities": ["look", "help"],
    "achievements": [],
    "levels_cleared": [],
    "missions": {
      "primary": null,
      "current": null
    }
  },
  "runtime": {
    "doctor_checked": false,
    "core_installed": false,
    "workspace_initialized": false,
    "workflow_run": false,
    "extension_installed": false,
    "research_completed": false,
    "publish_completed": false
  }
}
```

## Dungeon Map

```
Surface - Wizard
L6 Research Tower
L5 Extension Forge
L4 Workflow Engine
L3 TUI Hall
L2 Command Vault
L1 Awakening Chamber
Dungeon Depth - Ghost
```

## Level 1: Awakening Chamber

```mission
level: awakening_chamber
rank: ghost

narration:
  You awaken as a Ghost in the uDOS dungeon. The terminal is silent until you act.

objective:
  run "help"

challenge:
  read scroll "ucode_intro"

setup:
  run "udos doctor"

unlock:
  - command.look
  - command.help
  - command.inventory

reward:
  - scroll.ucode_intro
  - xp +40

checks:
  - doctor.python == true
  - doctor.git == true
  - doctor.network in ["ok", "degraded"]
  - doctor.shell_compatible == true
```

## Level 2: Command Vault

```mission
level: command_vault
rank: ghost

narration:
  Stone doors answer only to true commands.

objective:
  run "udos status"

challenge:
  retrieve artifacts ["run", "install", "status"]

setup:
  run "udos install core"

unlock:
  - command.run
  - command.install
  - command.status

reward:
  - artifact.run
  - artifact.install
  - artifact.status
  - xp +60

promotion:
  from: ghost
  to: apprentice

checks:
  - runtime.core_installed == true
  - file.exists("~/.udos")
  - file.exists("project.json")
  - file.exists("agents.md")
  - file.exists("tasks.json")
```

## Level 3: TUI Hall

```mission
level: tui_hall
rank: apprentice

narration:
  The hall reveals panels, grids, and controls used across all missions.

objective:
  open control palette

challenge:
  perform key sequence ["Ctrl+Space", "Tab", "Enter"]

setup:
  run "udos init my-first-binder"

unlock:
  - tui.palette
  - tui.panel_switch
  - tui.command_execute

reward:
  - artifact.tui_console
  - xp +80

checks:
  - runtime.workspace_initialized == true
  - dir.exists("binder")
  - dir.exists("workspace")
  - dir.exists("dev")
  - dir.exists("extensions")
```

## Level 4: Workflow Engine

```mission
level: workflow_engine
rank: apprentice

narration:
  The machine room turns plans into running missions.

objective:
  execute mission "hello_world"

challenge:
  review task output blocks and mark first task complete

setup:
  run "run mission hello_world"

unlock:
  - command.build
  - command.execute
  - command.workflow

reward:
  - artifact.workflow_core
  - xp +120

promotion:
  from: apprentice
  to: operator

checks:
  - runtime.workflow_run == true
  - tasks.completed >= 1
```

## Level 5: Extension Forge

```mission
level: extension_forge
rank: operator

narration:
  Tools are forged here. Extensions expand what your runtime can do.

objective:
  install first extension and run it

challenge:
  run command "generate image"

setup:
  - run "udos install extension.image"
  - run "generate image"

unlock:
  - extension.image
  - extension.write
  - extension.scrape

reward:
  - artifact.extension_forge
  - xp +140

promotion:
  from: operator
  to: alchemist

checks:
  - runtime.extension_installed == true
  - file.exists("output/image.png")
```

## Level 6: Research Tower

```mission
level: research_tower
rank: alchemist

narration:
  The tower converts live sources into structured knowledge.

objective:
  research topic "terminal interfaces"

challenge:
  verify tagged markdown output exists in binder

setup:
  run "research topic terminal interfaces"

unlock:
  - command.research
  - command.scrape
  - command.summarise
  - command.publish

reward:
  - artifact.research_core
  - xp +180

checks:
  - runtime.research_completed == true
  - file.exists("research/terminal-interfaces.md")
```

## Final Trial: Surface

```mission
level: surface
rank: alchemist

narration:
  The dungeon gate opens. Complete one full project cycle.

objective:
  create and publish project "guidebook"

setup:
  - run "create project guidebook"
  - run "publish"

reward:
  - achievement.wizard
  - xp +220

promotion:
  from: alchemist
  to: wizard

checks:
  - runtime.publish_completed == true
  - file.exists("output/guidebook.md")
  - file.exists("site/index.html")
```

## Optional Hidden Rooms

```mission
rooms:
  - id: container_runtime_lab
    unlock: "complete level workflow_engine"
    reward: "achievement.explorer"
  - id: offline_mode_vault
    unlock: "complete level command_vault"
    reward: "artifact.offline_core"
  - id: prompt_pack_archive
    unlock: "complete level extension_forge"
    reward: "artifact.prompt_pack"
```

## Achievement Table

- `achievement.explorer`: discovered one hidden room
- `achievement.builder`: completed first workflow mission
- `achievement.scholar`: completed first research mission
- `achievement.alchemist`: installed first extension
- `achievement.wizard`: completed onboarding and reached surface

## Streaming Event Example

```text
[NARRATION]
The chamber trembles.

[OBJECTIVE]
Run: udos doctor

[PROGRESS]
Checking environment...
OK python
OK git
OK shell

[REWARD]
scroll.ucode_intro acquired
```
