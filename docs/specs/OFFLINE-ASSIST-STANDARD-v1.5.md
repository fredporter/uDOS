# Offline Assist Standard v1.5

Status: Active  
Last updated: 2026-03-03

## Purpose

This spec defines the canonical v1.5 offline assist standard for uDOS.

It standardizes an offline-first assist layer that:
- is `ucode`-first
- remains deterministic by default
- can parse markdown workflow and mission contracts
- can write and execute sandboxed scripts
- can assist command loops without requiring network access
- can consume and update project state files
- can apply gameplay gates to unlock, reveal, and decode system functions

This standard is the contract layer for offline assist work. It is not a claim that the whole reference scaffold is already merged into `core/`.

## Scope

### In scope

- offline intent parsing from natural language and markdown contracts
- deterministic plan construction and validation
- `PLAN -> CHECK -> ACT -> VERIFY -> LOG` execution loops
- file-backed project state:
  - `project.json`
  - `agents.md`
  - `tasks.json`
  - `completed.json`
- sandboxed local script execution
- optional MCP and OK API adapter points with offline-safe stubs and deferred work
- gameplay-driven gating for workflow progression and artifact reveal

### Out of scope

- mandatory network access for normal operation
- hidden state mutation outside the audited file/runtime contract
- replacing core command/runtime ownership with a second command system
- Wizard web control plane behavior
- provider-led decision making that bypasses deterministic validation

## Canonical Reference Pack

The base reference scaffold for this standard lives under:

```text
docs/examples/udos_ulogic_pack/
```

The main implementation reference points are:

```text
docs/examples/udos_ulogic_pack/core/ulogic/
docs/examples/udos_ulogic_pack/examples/demo_project/
docs/examples/udos_ulogic_pack/examples/run_mission_demo.py
```

That pack is the reference for file layout, demo data, and execution shape until production code is promoted into `core/`.

## Architecture Rules

- offline assist belongs to `core/` when promoted into the runtime
- core implementations must remain stdlib-only and deterministic by default
- Wizard may integrate with the standard, but must not replace the offline contract
- if a `ucode` command exists, the assist layer should route through it instead of mutating subsystems directly
- every side effect must be auditable through logs, artifacts, or state-file updates

## Runtime Model

The offline assist runtime always follows this loop:

```text
INPUT -> IntentFrame(s)
      -> Plan
      -> Validate
      -> Execute
      -> Verify
      -> Persist
      -> Emit artifacts + logs
```

The canonical phase names are:
- `PLAN`
- `CHECK`
- `ACT`
- `VERIFY`
- `LOG`

## Canonical Layout

When implemented, the standard runtime is expected to follow this module shape:

```text
core/ulogic/
  engine/
  ucode/
  providers/
  gameplay/
  library/
  schemas/
```

The reference scaffold under `docs/examples/udos_ulogic_pack/` already mirrors this layout.

The first promoted canonical slice now lives under:

```text
core/ulogic/
```

Current promoted modules:
- `core/ulogic/contracts.py`
- `core/ulogic/parser.py`

## State Contracts

### `project.json`

Minimum required fields:
- `name`
- `version`
- `constraints`
- `workflow_defaults`
- `gameplay`

Expected contract areas:
- offline policy
- allowed shell/runtime constraints
- runtime budget/timeout rules
- workflow approval defaults
- gameplay mode

### `tasks.json`

Must hold open work items with:
- stable ids
- owners or roles
- dependencies when present
- status
- pointers to outputs or artifacts

### `completed.json`

Must hold completion evidence with:
- stable ids
- timestamps
- evidence references
- outcome/status data

### `agents.md`

Acts as the local policy surface for role permissions and red lines.

It must define:
- roles
- allowed actions
- prohibited actions
- approval or safety expectations

## Intent Frame Contract

Offline natural-language handling must compile into typed intent frames rather than freeform execution.

Minimum frame shape:

```json
{
  "intent": "workflow.run",
  "slots": {},
  "confidence": 0.0,
  "source": "pattern"
}
```

Starter intent families:
- `project.open`
- `project.status`
- `project.validate`
- `workflow.new`
- `workflow.run`
- `workflow.pause`
- `workflow.resume`
- `workflow.approve`
- `task.add`
- `task.block`
- `task.done`
- `task.list`
- `ucode.exec`
- `ucode.loop`
- `script.run`
- `mcp.call`
- `ok.call`
- `game.unlock`
- `game.reveal`
- `game.decode`
- `game.status`

## Planning Contract

Internal planning must use a structured action graph.

Each action node must be able to carry:
- an id
- an action type
- declared inputs
- declared outputs
- dependency edges
- guard conditions

The reference scaffold models this in:

```text
docs/examples/udos_ulogic_pack/core/ulogic/engine/contracts.py
```

## Execution Contract

Execution must support:
- `ucode` command dispatch
- bounded loop execution
- sandboxed script runs
- optional deferred provider/MCP work

The reference scaffold for these pieces lives in:

```text
docs/examples/udos_ulogic_pack/core/ulogic/ucode/dispatcher.py
docs/examples/udos_ulogic_pack/core/ulogic/ucode/sandbox.py
docs/examples/udos_ulogic_pack/core/ulogic/providers/
```

The promoted deterministic parser anchor now lives in:

```text
core/ulogic/parser.py
```

## Verification and Artifact Contract

Every completed action path must produce verifiable evidence.

Expected outputs include:
- artifact files
- completion entries
- local runtime logs
- state transitions in `tasks.json` and `completed.json`

The reference scaffold for persistence and artifacts lives in:

```text
docs/examples/udos_ulogic_pack/core/ulogic/engine/runtime.py
docs/examples/udos_ulogic_pack/core/ulogic/engine/validator.py
docs/examples/udos_ulogic_pack/core/ulogic/engine/artifacts.py
docs/examples/udos_ulogic_pack/core/ulogic/engine/state_store.py
```

## Gameplay Lens Contract

Gameplay is a first-class gate, not decoration.

It may control:
- unlock conditions
- reveal/decode conditions
- progression thresholds
- trust/streak/skill metrics
- whether specific actions may execute

Gameplay rules must still remain deterministic and file-backed.

Reference scaffold:

```text
docs/examples/udos_ulogic_pack/core/ulogic/gameplay/
```

## Markdown Contract

Offline assist must understand markdown as an editable contract surface.

Expected sources:
- missions
- workflows
- rulesets
- intent patterns

Reference scaffold:

```text
docs/examples/udos_ulogic_pack/core/ulogic/library/
docs/examples/udos_ulogic_pack/examples/demo_project/missions/
```

This aligns with the open-box Obsidian editing model already used elsewhere in uDOS.

## Integration Rules

- offline assist must integrate with `ucode`, not bypass it
- offline assist may expose MCP and OK API hooks, but those hooks must degrade safely when offline
- provider calls must be optional and recorded
- the standard must work without an online API requirement for core scripting, planning, or workflow definition

## Reference Demo

The baseline demo path is:

```text
docs/examples/udos_ulogic_pack/examples/run_mission_demo.py
```

The demo project state is under:

```text
docs/examples/udos_ulogic_pack/examples/demo_project/
```

This demo is the base example for:
- state-file contracts
- mission markdown parsing
- offline execution loops
- artifact writing
- completion updates

## v1.5 Release Expectations

For v1.5, this standard means:
- offline assist is a supported architecture lane
- the reference pack is canonical implementation guidance
- roadmap work should align workflow, task, gameplay, and `ucode` evolution to this contract
- production promotion into `core/` should happen by lifting the contract, not by inventing a separate runtime model
