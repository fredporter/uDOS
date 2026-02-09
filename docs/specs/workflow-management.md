uDOS Projects

Workflow management + call-rotation + organic automation (concept)

Projects (aka Missions) layer that turns “do this thing” into a living work plan that runs steadily over time, rotates provider calls, respects daily quotas, and builds durable “binders” of linked knowledge — while staying compatible with:
	•	uDOS Core (TUI only)
	•	Wizard Server (always-on jobs, web hooks, packaging, routing)
	•	Dev operations via VS Code + Vib CLI
	•	Local runtimes (Ollama/LocalAI) for privacy/offline and “house models”

Below is a conceptual design.

⸻

1) Core idea

A Project is a container for:
	1.	Goal + constraints (what “done” means, budget, time horizon, privacy level)
	2.	Prompt library (reusable patterns and house style)
	3.	Task graph (decomposed steps + dependencies)
	4.	Runs (scheduled executions over time)
	5.	Binders (compiled evidence + citations + summaries + exports)
	6.	Policies (provider rotation rules, quotas, retry logic, trust levels)

The magic is the Scheduler: a “not-a-race” cron that spreads work out, prioritises learning loops, and upgrades quality via staged passes.

⸻

2) Mental model: “Organic Cron”

Instead of “run everything at 2am”, uDOS runs a gardening loop:
	•	Plant (expand project into tasks)
	•	Sprout (quick web scan / cheap calls / broad collection)
	•	Prune (dedupe, classify, remove noise)
	•	Trellis (deep dives only where needed)
	•	Harvest (compile binder chapters, generate outputs)
	•	Compost (store learnings into prompt library + house rules)

This keeps work steady, paced, and quota-aware, improving output quality over multiple cycles.

⸻

3) System components

3.1 uDOS Core (TUI)
	•	Shows project status, next scheduled tasks, quotas, and binder progress
	•	Provides commands to create/modify missions and run manual steps
	•	Stores lightweight metadata locally (with encrypted secrets references)

3.2 Wizard Server (control plane)
	•	Runs scheduler + worker queue
	•	Handles job orchestration, web proxy access, extraction, packaging
	•	Hosts routing policy for provider rotation
	•	Maintains project storage (binders, indexes, logs, artefacts)

3.3 Providers / Runtimes (execution plane)
	•	OpenRouter (breadth + routing to hosted models)
	•	LocalAI (self-hosted OpenAI-compatible platform)
	•	Ollama (local/offline runtime on model nodes)
	•	Gemini API (creative tasks)
	•	Vib CLI (dev/coding tasks)

Internally, treat these as Agents with capabilities and costs.

⸻

4) Data model (practical)

4.1 Project (Mission)
	•	id, name, goal, definition_of_done
	•	constraints: budget, max daily calls, privacy, deadlines
	•	policy: routing rules, escalation thresholds
	•	promptsets: references to prompt templates
	•	binders: binder configuration + chapter outline
	•	task_graph: tasks + dependencies

4.2 Task
	•	type: research | capture | summarise | compare | code | write | verify | export
	•	inputs: URLs, queries, prior notes, files, schemas
	•	outputs: binder updates, docs, code patches, datasets
	•	quality_target: draft | standard | publish-ready
	•	schedule: cadence + windows + backoff
	•	agent_profile: preferred agents + fallback list
	•	cost_limits: max tokens, max calls, time caps
	•	trust: requires citations? requires cross-check?

4.3 Run (execution record)
	•	timestamps, chosen agent, parameters
	•	logs, artifacts
	•	outcome: success | partial | failed | deferred
	•	learned signals: sources quality, cost efficiency, prompt effectiveness

4.4 Binder

A binder is the “compiled knowledge product”:
	•	chapters
	•	source_index (URLs, dates, snapshots, hashes)
	•	evidence_notes
	•	summaries at multiple levels (bullet → section → executive)
	•	exports: Markdown / PDF / JSON / “dev brief”

⸻

5) Provider rotation + quota management

5.1 Agent registry (capability-based)

Each Agent has:
	•	capabilities: creative, reasoning, extraction, coding, summarisation
	•	cost_model: per token/call, or “free” local compute
	•	rate_limits: daily caps, per-minute caps
	•	quality_score (learned over time per task type)
	•	reliability_score (timeouts/errors)

5.2 Rotation strategy (simple + effective)

For each task, Wizard chooses an Agent using:
	1.	Policy constraints (privacy/offline requirement)
	2.	Budget & quota (daily remaining)
	3.	Capability match (task type → best-fit agents)
	4.	Exploration (occasionally try an alternative agent to learn)
	5.	Escalation (upgrade only if draft quality is insufficient)

Example escalation ladder (per task)

Local (Ollama/LocalAI) draft
  -> Hosted cheap pass (OpenRouter budget model) refine
    -> Premium pass (hosted stronger model) only if needed

5.3 Daily quota pacing (“organic”)
	•	Divide daily budget into time slices (morning/afternoon/evening)
	•	Maintain a reserve (eg. 20%) for interactive user requests
	•	Use cooldowns to prevent hammering any single provider
	•	Automatically defer “nice to have” tasks when quotas are tight

⸻

6) Prompt library: reusable, evolving, project-aware

6.1 Prompt primitives

Store as versioned assets:
	•	system_style (tone, formatting rules, citations policy)
	•	task_templates (capture, summarise, compare, code review, etc.)
	•	project_overlays (domain-specific terminology and goals)
	•	checklists (quality gates)

6.2 Prompt learning loop

After each run:
	•	Record what worked (sources, structure, constraints)
	•	Save a “delta note” into:
	•	project prompt overlay (project-specific)
	•	core distributed rules (house style / shared conventions)

This creates the two-layer knowledge model you described:

a) Knowledge/core distributed rules (global)
b) User-developed project overlays (local to mission)

⸻

7) Research + scavenging + binder compilation pipeline

7.1 Pipeline stages (repeatable)
	1.	Scout: broad query set, collect candidate sources
	2.	Capture: snapshot URLs, store metadata, extract key sections
	3.	Sift: dedupe, classify, rank by credibility/recency
	4.	Synthesize: build chapter notes with citations
	5.	Verify: cross-check top claims (2+ sources)
	6.	Publish: compile binder outputs (Markdown-first)

7.2 Binder chapter automation

Chapters are updated incrementally:
	•	“Sources added today”
	•	“Key findings updated”
	•	“Open questions”
	•	“Next tasks scheduled”

⸻

8) Dev operations integration (VS Code + Vib CLI + Dev TUI)

8.1 VS Code workflow

Each Project can generate a “dev bundle”:
	•	PROJECT.md (goal, status, roadmap)
	•	TASKS.md (task graph, next actions)
	•	BINDER/ (chapter notes, citations index)
	•	PROMPTS/ (prompt templates + overlays)
	•	RUNS/ (logs, artifacts, diffs)
	•	optional .code-workspace or config hints

8.2 Vib CLI lane (coding tasks)

Coding tasks are explicit types:
	•	“Create module”
	•	“Refactor function”
	•	“Write tests”
	•	“Generate docs”
	•	“Audit dependencies”

Outputs:
	•	patch files / diffs
	•	test reports
	•	changelog entries

8.3 Dev TUI mode

A focused interface for:
	•	queue view (what’s running next)
	•	logs + artefacts
	•	quick rerun with adjusted constraints
	•	approval gates for sensitive steps (eg. publishing, emailing)

⸻

9) TUI command design (uDOS-friendly)

Example command set (conceptual):

PROJECT NEW "Market Research: Event Promoter Tools"
PROJECT SET goal "Compile a binder of tools, pricing, and integrations"
PROJECT POLICY SET privacy local-first
PROJECT POLICY SET rotate on
PROJECT POLICY SET daily_budget_calls 200

TASK ADD research.scout --query "Audience engagement platforms 2026" --cadence daily
TASK ADD capture.collect --sources from:research.scout --cadence daily
TASK ADD synth.chapter --chapter "Competitive Landscape" --cadence weekly
TASK ADD verify.claims --cadence weekly

BINDER OUTLINE ADD "Executive Summary"
BINDER OUTLINE ADD "Competitive Landscape"
BINDER OUTLINE ADD "Pricing & Plans"
BINDER OUTLINE ADD "Integration Notes"
BINDER OUTLINE ADD "Source Index"

RUN NOW --task research.scout
STATUS --project
QUEUE


⸻

10) Scheduling logic (what makes it “organic”)

10.1 Task scoring (priority)

Each task gets a dynamic score:
	•	urgency (deadline proximity)
	•	value (moves binder forward)
	•	freshness need (news-like topics)
	•	dependency readiness
	•	cost (tokens/time)
	•	quota impact
	•	user attention (prefer tasks that unblock user decisions)

10.2 Cadence patterns

Support:
	•	fixed cadence (daily/weekly)
	•	windowed cadence (“only evenings”)
	•	adaptive cadence (“more often if sources are changing fast”)
	•	backoff on repeated failures
	•	“slow burn” research mode (eg. 2–5 tasks/day)

⸻

11) Output philosophy: Markdown-first, export-ready

Default artefacts:
	•	BINDER.md (main compiled output)
	•	SOURCES.md (linked index + snapshot dates)
	•	OPEN_QUESTIONS.md
	•	NEXT_ACTIONS.md
	•	CHANGELOG.md (what changed since last cycle)

Optional:
	•	PDF export
	•	JSON knowledge pack for core indexes
	•	“dev brief” export for Vib CLI sessions

⸻

12) One ASCII diagram tying it together

[ uDOS Core (TUI) ]
        |
        |  project/task commands + status
        v
[ Wizard Server: Control Plane ]
  - Scheduler (organic cron)
  - Policy (rotation + quotas)
  - Workers (capture/synth/verify)
  - Storage (binders, runs, prompts)
        |
        +------------------------------+
        |                              |
        v                              v
[ LocalAI / Ollama ]              [ OpenRouter ]
(local/private/offline)           (hosted breadth)
        |
        v
[ Binders + Prompt Library + Artefacts ]
        |
        +--> VS Code workspace bundle
        +--> Vib CLI jobs (code patches/tests)
        +--> uDOS Core summaries (TUI)


⸻
