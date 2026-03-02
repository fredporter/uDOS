Below is a framework + scaffolding plan for an offline logic engine that is:
	•	uCode-first
	•	Can write + execute scripts
	•	Can assist uDOS commands + loops
	•	Works with MCP + OK APIs
	•	Follows uDOS workflow patterns
	•	Integrates gameplay metrics to drive system functions (unlock/reveal/decode)
	•	Consumes and updates: project.json, agents.md, tasks.json, completed.json

I’m going to describe it as a buildable subsystem you can drop into core/ and progressively implement.

⸻

1) What this engine is

Name: uLogic (working name)

Purpose: deterministic, offline “thinking + acting” layer that turns:
	•	natural language intent
	•		•	workflow contracts (md)
	•		•	mission/project state (json)
into:
	•	validated plans
	•	executable uCode loops
	•	command dispatch
	•	artifact outputs
	•	state updates
	•	gameplay-driven gating

This is not “one giant OK model.” It’s a rule + contract engine with optional model hooks (local LLM) that are treated as advisors, not decision-makers.

⸻

2) Core concepts

A. uCode-first execution model
	•	uCode is the canonical “action language”
	•	Everything funnels into:
	•	PLAN → CHECK → ACT → VERIFY → LOG

B. Determinism
	•	Any non-deterministic step must be:
	•	optional
	•	sandboxed
	•	recorded (inputs/outputs)
	•	never allowed to silently change system state

C. State is file-backed and auditable
	•	project.json = project facts + constraints
	•	agents.md = roles + allowed actions + red-lines
	•	tasks.json = open tasks
	•	completed.json = completion evidence
	•	missions/*.md = contract-based steps

D. Gameplay lens

A “gameplay layer” provides:
	•	metrics
	•	achievements
	•	unlock conditions
	•	progression gates
	•	reveal/decode mechanics

These gates control:
	•	what commands can run
	•	what workflows can proceed
	•	what artifacts can be revealed to user

⸻

3) Folder scaffold

core/ulogic/
  README.md

  engine/
    runtime.py            # main loop + orchestrator
    parser_nl.py          # natural language → intent frames (offline)
    parser_md.py          # workflow/mission markdown parsing
    planner.py            # plan builder (deterministic)
    validator.py          # policy + schema validation
    executor.py           # ucode/script command runner
    verifier.py           # checks, tests, evidence capture
    state_store.py        # project/tasks/completed IO
    artifacts.py          # write outputs to vault/workflows

  ucode/
    dispatcher.py         # map ulogic actions -> uDOS commands
    loop.py               # repeat/until primitives
    sandbox.py            # script execution guardrails

  providers/
    ok_api.py             # OK API client interface (offline stubs)
    mcp_client.py         # MCP client wrapper + tool registry
    local_model.py        # optional local LLM interface (advisor-only)

  gameplay/
    metrics.py            # XP, streaks, skill levels, trust, entropy, etc.
    rules.py              # unlock/reveal/decode rules
    effects.py            # gated system functions
    telemetry.py          # log events (local)

  library/
    intents/              # NL intent frames + grammar patterns
    rulesets/             # policy packs
    workflows/            # MD workflow templates
    missions/             # mission templates
    skills/               # offline “skills” (deterministic transforms)
    datasets/             # local refs (glossaries, mappings)

  schemas/
    project.schema.json
    tasks.schema.json
    completed.schema.json
    mission.schema.json
    event.schema.json


⸻

4) Data contracts

project.json (minimum fields)

{
  "name": "uDOS",
  "version": "1.5.x",
  "constraints": {
    "offline_first": true,
    "allowed_shell": ["python", "bash"],
    "max_runtime_seconds": 60
  },
  "workflow_defaults": {
    "approval_required": true,
    "tier_policy": "offline_only"
  },
  "gameplay": {
    "enabled": true,
    "mode": "builder"
  }
}

tasks.json
	•	array of tasks with ids, owners, dependencies, status, pointers to artifacts

completed.json
	•	completion items with evidence links and timestamps (no “trust me bro”)

agents.md (policy surface)

Agents are not “model agents,” they’re roles with permissions:

# AGENTS

## role: Operator
- can: run ucode commands
- can: approve phases
- cannot: disable safety gates

## role: Builder
- can: write templates
- can: generate plans
- cannot: execute destructive commands

## role: Runner
- can: run sandbox scripts
- must: log outputs


⸻

5) Natural language → Intent Frames (offline)

You want an offline NL logic engine. Don’t try full NLP. Use:
	•	Pattern library (regex + keyword maps)
	•	Intent frames (typed slots)
	•	Optional local model only to suggest slot fills

Example intent frame:

{
  "intent": "workflow.run",
  "slots": {
    "workflow_id": "wf-2026-03-03-001",
    "phase": "draft",
    "mode": "paced",
    "approval": true
  },
  "confidence": 0.82,
  "source": "pattern"
}

Intent categories (starter set)
	•	project.open, project.status, project.validate
	•	workflow.new, workflow.run, workflow.pause, workflow.resume, workflow.approve
	•	task.add, task.block, task.done, task.list
	•	ucode.exec, ucode.loop, script.run
	•	mcp.call, ok.call (stub offline if no network)
	•	game.unlock, game.reveal, game.decode, game.status

⸻

6) uLogic runtime loop

The runtime always does:
	1.	Parse input (NL or md step)
	2.	Plan actions (deterministic)
	3.	Validate against:
	•	agents.md permissions
	•	project constraints
	•	gameplay gates
	4.	Execute
	5.	Verify
	6.	Persist
	7.	Emit artifacts

Pseudo-flow:

INPUT -> IntentFrame(s)
      -> Plan (ActionGraph)
      -> Validate (Policy + Gameplay)
      -> Execute (uCode + Scripts + MCP/OK stubs)
      -> Verify (checks/evidence)
      -> Update tasks.json + completed.json
      -> Write artifacts + logs


⸻

7) ActionGraph: the internal plan format

Every plan is a DAG of actions:

{
  "plan_id": "plan-001",
  "actions": [
    {
      "id": "a1",
      "type": "ucode.command",
      "cmd": "STATUS",
      "inputs": [],
      "outputs": ["artifacts/status.md"],
      "guards": ["gate:operator_approved"]
    },
    {
      "id": "a2",
      "type": "script.run",
      "lang": "python",
      "path": "scripts/check_env.py",
      "depends_on": ["a1"],
      "guards": ["gate:trust>=10"]
    }
  ]
}


⸻

8) uCode loops + command assistance

Loop primitives
	•	repeat N
	•	until condition
	•	foreach item in list
	•	while condition
	•	retry with backoff

Example uLogic loop spec (stored as md or json):

loop:
  foreach: tasks.open
  do:
    - ucode.command: "TASK inspect {{item.id}}"
    - ucode.command: "TASK propose_next {{item.id}}"
  until:
    condition: "time_budget_exceeded"

The engine expands these into ActionGraph steps and runs them with logs.

⸻

9) Script execution (offline, safe)

You want “can code and execute script” but safely.

Sandbox rules
	•	Default: no network
	•	Restrict file writes to:
	•	vault/
	•	.artifacts/
	•	memory/
	•	Restrict commands to allowlist
	•	Enforce time limit per script
	•	Capture stdout/stderr and hashes of inputs/outputs

The engine should run scripts through a wrapper:
	•	set env
	•	mount allowed paths
	•	enforce timeouts
	•	record “evidence bundle”

⸻

10) MCP and OK API integration (offline-first)

Treat MCP + OK APIs as capability providers:

Tool registry
	•	ToolRegistry holds tools with:
	•	name
	•	capability tags
	•	offline availability
	•	input schema
	•	output schema

Offline behavior

If offline:
	•	MCP calls can still hit local MCP servers
	•	OK API calls become:
	•	cached responses (if present)
	•	or “deferred actions” queued for later

Queue format:

{
  "queued_at": "...",
  "tool": "ok.assets.render",
  "payload": {...},
  "depends_on": ["a12"],
  "retry_policy": "next_window"
}

This matches your paced scheduling idea.

⸻

11) Gameplay metrics layer

Metrics model (examples)
	•	XP: progress points
	•	Trust: increases when verification passes
	•	Focus: decays with too many context switches
	•	Streak: consecutive successful phases
	•	Entropy: rises when artifacts drift from contracts

Events

Everything emits events:
	•	phase.started
	•	phase.completed
	•	validation.failed
	•	artifact.written
	•	gate.unlocked
	•	secret.revealed

Gates

A gate is a boolean condition over:
	•	metrics
	•	task state
	•	completion evidence
	•	time windows

Example gates:
	•	unlock:script_exec when trust >= 10 AND completed:setup_phase
	•	reveal:advanced_templates when xp >= 200
	•	decode:secret_hint when streak >= 3 AND entropy <= 20

Effects (system functions)

Effects are what gates enable:
	•	allow running a risky command
	•	reveal hidden workflow steps
	•	unlock advanced provider tier (when online)
	•	decode an encrypted payload (locally)

This is how “gameplay implements system functions.”

⸻

12) Offline library “skills”

These are deterministic helpers that reduce reliance on models.

Starter skills set:

Writing/structure
	•	outline normalization
	•	markdown lint + section contract check
	•	diff summarizer
	•	template expansion (variables → filled)

Planning
	•	dependency resolver (tasks graph)
	•	critical path finder
	•	risk checklist generator

Code
	•	static file scan
	•	grep-based ref updates
	•	safe refactor routines (simple transforms)
	•	test runner wrappers

Workflow ops
	•	parse workflow md → PhaseSpec
	•	compute next runnable phase
	•	update tasks/completed

Gameplay
	•	compute metrics
	•	evaluate gate expressions
	•	apply effects + audit log

⸻

13) Workflow/Mission markdown format

Make missions/workflows explicit, parseable.

Example missions/mission-example.md:

# MISSION: bootstrap-offline-engine

## Goal
Implement uLogic runtime skeleton and state store.

## Constraints
- offline_only: true
- destructive_commands: forbidden

## Steps
1. CREATE core/ulogic/engine/runtime.py
   - output: artifacts/runtime_stub.md
   - verify: unit_tests_pass

2. CREATE schemas/project.schema.json
   - verify: jsonschema_validate

## Rewards
- xp: 50
- unlock: "mission:provider_integration"

Engine parses this and runs step-by-step, with user approvals.

⸻

14) How it ties into your existing uDOS files

project.json
	•	engine reads constraints, default policies, gameplay mode

agents.md
	•	engine enforces permissions and red-lines

tasks.json
	•	engine adds “actionable tasks”
	•	links tasks to artifacts and mission steps

completed.json
	•	engine writes evidence entries:
	•	what ran
	•	what outputs were created
	•	hashes
	•	verification results

This gives you auditability and makes your workflows “real.”

⸻

15) Minimal build order

If you want this to land cleanly, build in this order:
	1.	state_store.py (read/write/validate the 4 files)
	2.	parser_md.py (parse workflow/mission MD into structs)
	3.	ActionGraph + validator.py (permissions + constraints + gates)
	4.	executor.py (ucode commands + safe scripts)
	5.	gameplay/metrics.py + rules.py (gates + effects)
	6.	MCP/OK provider stubs + deferred queue
	7.	parser_nl.py pattern-based intents (optional local model advisor later)

⸻
