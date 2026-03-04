uDOS v1.5 Standard

Offline-First Architecture with GPT4All Local Assist + Wizard Network API Budget Control

⸻

Status

uDOS v1.5 is the new official standard.
It replaces prior local model integrations and formalizes:
	•	✅ GPT4All as the sole local offline assist model layer
	•	✅ Wizard Network as the only online routing + budget control layer
	•	✅ Deterministic uLogic engine as execution authority
	•	✅ Advanced project/mission workflow templates and utilities as core runtime features

Legacy local runtime integrations are no longer required or supported in the default stack.

⸻

1. Architectural Doctrine

uDOS v1.5 is built on three foundational principles:
	1.	Offline-first cognition
	2.	Deterministic execution authority
	3.	Controlled, policy-driven online escalation

The AI model never owns execution.
The uLogic engine owns execution.

⸻

2. System Overview

2.1 Core Runtime Layers

Layer A — Deterministic Core (Authority Layer)
	•	uLogic Engine (planner → validator → executor → verifier → logger)
	•	Logic Input Handler (non-breaking)
	•	File-backed state (project/tasks/completed/workflows)
	•	Script sandbox

This layer always works offline.

⸻

Layer B — Local Assist (Default Cognitive Layer)

Engine: GPT4All (optimized local model)
Role: Advisory only
Network required: No (after model download)

Responsibilities:
	•	Intent suggestion
	•	Plan drafting
	•	Summarization
	•	Context compression
	•	Operator guidance
	•	Draft writing

Prohibited:
	•	Direct state mutation
	•	Silent execution
	•	Bypassing validation
	•	Network calls

⸻

Layer C — Wizard Network (Online Escalation Layer)

Wizard Network is the only allowed outbound API path.

Responsibilities:
	•	Model routing (free/cheap/premium tiers)
	•	Budget management
	•	Daily allowance tracking
	•	Usage logging + cost accounting
	•	Deferred execution queue
	•	Response caching
	•	Escalation policy enforcement

⸻

3. Removal of legacy local runtime integrations

uDOS v1.5 officially removes the previous local runtime integrations.

Reasons:
	•	GPT4All provides optimized desktop runtime
	•	Better curated model packaging
	•	Easier onboarding
	•	Smaller dependency surface
	•	Unified local model management

Any references to prior local runtime integrations in earlier versions are considered legacy.

⸻

4. GPT4All Local Assist Specification

4.1 Model Profile

The selected local model must be:
	•	≤ 8B parameter class (quantized)
	•	Optimized for:
	•	reasoning-lite
	•	summarization
	•	structured drafting
	•	Fast on CPU (GPU optional)

4.2 Prompt Contract

Local prompts must include:
	•	explicit role framing
	•	structured output expectations
	•	no authority language
	•	deterministic fallback handling

All local outputs are:
	•	parsed
	•	validated
	•	logged

⸻

5. Advanced API Budget Management (Wizard Network)

Wizard Network introduces tiered routing:

5.1 Model Tiers

Tier 0 — Free Models
	•	Community / free quotas
	•	Used for:
	•	low-risk summarization
	•	secondary reasoning checks
	•	bulk classification

Tier 1 — Paid Economy Models
	•	Low-cost per-token
	•	Used for:
	•	structured code generation
	•	long summaries
	•	mid-level reasoning

Tier 2 — Premium Models
	•	High reasoning capability
	•	Used only when:
	•	complexity threshold exceeded
	•	policy requires
	•	user explicitly requests

⸻

5.2 Escalation Rules

Escalation occurs only if:
	•	local confidence < threshold
	•	context window exceeded
	•	plan complexity > N nodes
	•	mission template requires external validation

Otherwise, remain offline.

⸻

5.3 Budget Controls

Wizard Network maintains:

{
  "daily_limit": 10.00,
  "tier0_quota": "unlimited",
  "tier1_budget": 5.00,
  "tier2_budget": 5.00,
  "cooldown_windows": true,
  "auto_defer_when_exceeded": true
}

When exceeded:
	•	create deferred queue entry
	•	notify user
	•	continue offline

⸻

6. Knowledge Architecture

6.1 Local Instruction Pack (Curated)

Includes:
	•	ucode commands reference
	•	ucode scripting guide
	•	sonic device database
	•	uDOS documentation
	•	how-to guides
	•	runbooks

All stored in markdown with:

---
udos_id:
type:
tags:
links:
offline_ok: true
---


⸻

6.2 Global Knowledge Library

Curated canonical references.
Versioned.
Indexed.

⸻

6.3 User Knowledge Vault

Linked via:
	•	user-tree structure
	•	Obsidian tags
	•	udos-frontmatter metadata

Supports:
	•	backreferences
	•	tag clustering
	•	working set extraction

⸻

7. Logic Input Handler (v1.5 Standard)

The input handler is mandatory and non-breaking.

All input resolves into:
	1.	Command
	2.	Workflow
	3.	Library
	4.	Operator Guidance

If ambiguous:
	•	suggest options
	•	preserve raw input
	•	never fail silently

If execution fails:
	•	log evidence
	•	propose next action
	•	remain interactive

⸻

8. Advanced Project & Mission Workflow System

uDOS v1.5 formalizes structured workflow templates.

8.1 Template Types
	•	project templates
	•	mission templates
	•	agent definitions
	•	task pipelines
	•	escalation workflows
	•	offline-only workflows
	•	hybrid workflows

⸻

8.2 Template Files

/library/workflows/
/library/missions/
/schemas/

Includes:
	•	workflow.json
	•	mission.md
	•	tasks.json
	•	agents.md
	•	completed.json

⸻

8.3 Mission Engine Features
	•	conditional unlock
	•	dependency graph execution
	•	validation gates
	•	evidence capture
	•	artifact generation
	•	deferred online stages

Supports gameplay-style progression logic if enabled.

⸻

9. Execution Model (Deterministic Core)

The runtime loop:
	1.	Parse
	2.	Plan (ActionGraph)
	3.	Validate
	4.	Execute
	5.	Verify
	6.	Persist
	7.	Emit events

Models may assist planning.
They never execute.

⸻

10. Utilities & Tooling (v1.5 Expanded)

Includes:
	•	working-set summarizer
	•	knowledge index builder
	•	tag cluster generator
	•	workflow scaffolder
	•	mission compiler
	•	escalation analyzer
	•	budget monitor
	•	prompt cache
	•	deferred queue manager
	•	sandbox script runner

All tools operate file-backed and auditable.

⸻

11. Flow-State UI Requirements

The UI must:
	•	never stall
	•	stream output blocks
	•	show routing decisions
	•	show model tier used
	•	show budget impact
	•	offer safe next steps

Preferred pattern:

Select → Input → Run → Stream → Next

⸻

12. Security and Determinism

Default:
	•	no network in sandbox
	•	allowlisted commands only
	•	strict file write boundaries
	•	model outputs validated before execution

Any nondeterministic behavior must be:
	•	optional
	•	logged
	•	reversible

⸻

13. Directory Scaffold (v1.5)

/core/ulogic/
/providers/local_model_gpt4all.py
/providers/wizard_network.py
/library/intents/
/library/workflows/
/library/missions/
/library/sonic/
/schemas/
/vault/
/memory/
/artifacts/
/logs/
/deferred_queue/


⸻

14. Acceptance Criteria

uDOS v1.5 is compliant if:
	•	GPT4All is the sole local model
	•	legacy local runtime removed
	•	Wizard Network is the only API route
	•	Offline logic fully functional
	•	Budget tiers enforced
	•	Non-breaking input handler implemented
	•	Workflow templates operational
	•	All state file-backed

⸻

15. Strategic Outcome

uDOS v1.5 delivers:
	•	Unlimited offline AI logic
	•	Intelligent premium usage without waste
	•	Deterministic execution control
	•	Auditable system state
	•	Advanced workflow templating
	•	Hybrid cognition with strict governance
