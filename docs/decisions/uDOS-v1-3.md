uDOS v1.3.x Dev Brief

Open-box, local-first knowledge runtime with optional public publishing lane

⸻

1. Purpose

uDOS is an execution + scheduling + publishing layer that sits beside an Obsidian-compatible Markdown vault (files on disk). It powers:
	•	Local/private sharing over Wizard-hosted LAN / beacon networks (offline-first)
	•	Background “missions” (scheduled research, summarise, dedupe, indexing, reporting)
	•	Themeable rendering (MD → HTML) using a universal Theme Pack system
	•	Optional public/web lane (headless WordPress) for user logins, web publishing, and wiki-style updates over the Internet

This brief locks the architecture into two distinct lanes so we don’t accidentally build an Obsidian clone or a monolithic CMS.

⸻

2. Non-negotiables
	•	Vault is truth: content lives as .md + assets + optional .db on disk.
	•	Open-box: users can read everything without uDOS installed.
	•	Deterministic core: parsing/rendering/diffs/sync are reproducible and testable.
	•	AI behaves like a contributor: proposes edits via patches + run reports.
	•	Offline-first: local models preferred; online models used by policy.
	•	No Obsidian plugin dependency for core functionality.

⸻

3. System lanes

Lane A — uDOS Local Portal (Wizard-hosted)

Goal: host, share, and publish vault content across private/local networks (LAN / beacon), with permissions and contributions.

Key capabilities
	•	Host a Portal (web UI) on the local node
	•	Serve rendered HTML from MD (static-first)
	•	Device discovery / pairing (beacon/proximity)
	•	Permission model (Viewer / Contributor / Editor / Maintainer)
	•	Contribution intake (patch bundles), review/merge, snapshots
	•	Scheduler + AI router + logging + audit
	•	Optional “public beacon” mode (still node-controlled)

Storage
	•	Markdown + assets in vault
	•	SQLite for state: jobs, runs, provenance, permissions, contribution queue

⸻

Lane B — Headless WordPress Public/Web

Goal: provide a web publishing and user-login surface (internet-facing), with wiki-like updates and public identity features.

Key capabilities
	•	User accounts, roles, moderation
	•	Public publishing, commenting, editorial workflows (if needed)
	•	External/public wiki contributions with authentication
	•	Themeable web presentation

Critical constraint
	•	WordPress is never the source of truth.
It receives published snapshots from the vault, and contributions flow back as patch bundles.

Why this is a separate lane
	•	Keeps uDOS local/offline-first vision pure
	•	Avoids “WordPress gravity” becoming your core data model
	•	Allows you to ship the local portal fast while WP lane evolves independently

⸻

4. Rendering + Themes: “Universal Theme Pack” contract

Core idea

uDOS provides a single renderer pipeline:

Markdown → HTML → Theme Shell → Output Bundle

This supports your theme ecosystem:
	•	Tailwind Typography (baseline prose)
	•	medium.css
	•	NES.css
	•	TELETEXT
	•	c64css3
	•	Marp (slides lane)
	•	gtx-form (forms lane)

Theme Pack structure (v0)

themes/
  prose/
    shell.html
    theme.css
    assets/
    theme.json
  nes/
  teletext/
  c64/
  medium/

shell.html defines slots:
	•	{{content}} (rendered MD HTML)
	•	{{title}}, {{nav}}, {{meta}}, {{footer}}

theme.json declares:
	•	name, version, mode (article|retro|slides|forms)
	•	required assets
	•	optional JS
	•	default typography and container classes

Output target

Rendered sites land in the vault:
	•	memory/vault/_site/<theme>/<path>/index.html
	•	(or a parallel publish/ folder if preferred)

Wizard serves the static output directly.

⸻

5. Firm line: SvelteKit vs Flat HTML

The decision boundary (rule set)

Use Flat HTML (static-first) when:
	•	Content is mostly read-only browsing
	•	You need maximum offline reliability
	•	You want minimal moving parts + instant load
	•	The UI is “document + navigation + search” (basic)
	•	You’re publishing snapshots (LAN/beacon)

Use SvelteKit when:
	•	You need an application experience:
	•	authenticated dashboards
	•	contribution review UI
	•	permission management
	•	mission control (queues, approvals, history)
	•	interactive search facets, filters, graph, etc.
	•	You need client-side components, state, routing, or realtime updates

Default posture
	•	Publishing = static HTML
	•	Control plane (admin) = SvelteKit

This keeps the “universal components” goal achievable without forcing SvelteKit everywhere.

⸻

6. Containerisation policy (including SvelteKit)

Local Node (Wizard-hosted) containers

Containerise services, not content.

Recommended container set:
	•	wizard-core (API gateway + auth + permissions + scheduler)
	•	renderer (md→html + theme pack build)
	•	ollama (local model runtime)
	•	ai-router (policy engine)
	•	vault-service (sync, contributions, snapshots)
	•	portal-static (static file server for _site)
	•	optional: sveltekit-admin (control plane UI)

SvelteKit container

Yes, containerise SvelteKit as a service:
	•	build once, run anywhere
	•	keep it optional and replaceable
	•	SvelteKit becomes the admin/control UI, not a requirement for reading content

Static publishing remains independent of SvelteKit.

⸻

7. Runtime split: TS Core, Vibe CLI, Wizard Server

TS Core (deterministic engine)

Owns:
	•	Markdown parsing → AST → transforms
	•	JSON/YAML/CSV parsing + schema validation
	•	SQLite handling (migrations, queries, indices)
	•	Diff/patch generation (contributions)
	•	Rendering pipeline (MD→HTML, theme shell)
	•	Export packaging (site bundles, LAN snapshots)

Produces:
	•	output HTML
	•	run reports
	•	contribution bundles

Vibe CLI (interactive agent console)

Owns:
	•	interactive “do the thing” dev/operator workflows
	•	tool calling and command execution
	•	calling TS core tools as “actions”
	•	optional ACP mode for service integration

Vibe does not own the deterministic transforms.

Wizard Server (node brain)

Owns:
	•	Portal hosting (LAN/beacon)
	•	permissions + pairing + sharing scopes
	•	contribution intake/review/merge
	•	scheduler and off-peak execution
	•	AI router policy + quotas
	•	audit logs, run history, snapshots

Wizard is required for networking + portal + governance.

⸻

8. AI model strategy (local-first with policy)

Local lanes (Ollama pool)
	•	Dev lane: devstral-small-2, codellama, llama2
	•	Knowledge lane: mistral, neural-chat, openchat, zephyr, orca-mini

Online lanes (policy-triggered)
	•	OpenRouter
	•	OpenAI
	•	Gemini

Selection triggers

Online is allowed when:
	•	quality threshold is “publish-grade”
	•	context window exceeds local
	•	capability needed (vision/long-context/tooling)
	•	time constraints / compute constraints
	•	mission policy explicitly allows it

Every AI call logs:
	•	model + provider
	•	input hashes (not raw secrets)
	•	outputs + file paths
	•	estimated cost (online)
	•	timestamps + mission/job IDs

⸻

9. Missions and tasks (ongoing programmes)

Mission definition

A Mission is a long-running programme with:
	•	goal, constraints, cadence
	•	targets (folders, notes, feeds)
	•	allowed capabilities (offline-only vs online ok)
	•	outputs (reports, published pages, contribution queues)

Outputs
	•	Run reports in memory/vault/06_RUNS/...
	•	Logs in memory/vault/07_LOGS/...
	•	Proposed edits as contribution bundles

AI is treated as a Contributor, not an editor.

⸻

10. Milestones

Milestone 1 — Static publishing + theme packs (local)
	•	Implement TS Core render pipeline
	•	Theme Pack contract v0
	•	Tailwind Prose baseline + 1 retro theme (NES or Teletext)
	•	Wizard serves _site/ over LAN

Milestone 2 — Control plane (SvelteKit admin)
	•	SvelteKit “Admin” UI container
	•	Mission/job queue view
	•	Contribution review/merge UI
	•	Permissions management (local pairing)

Milestone 3 — AI routing + off-peak missions
	•	AI router policy engine
	•	Ollama pool integration
	•	online fallback support with quota rules
	•	scheduled nightly “knowledge gardening” mission

Milestone 4 — WP public lane (optional add-on)
	•	Containerised headless WP stack
	•	Publish snapshots to WP
	•	Accept web contributions → patch bundles → review/merge back to vault
	•	Public user login / moderation flow

⸻

11. Deliverables

Repo structure (target)

memory/vault/       # Obsidian truth store
themes/             # Theme packs
core/               # TS deterministic engine (render, parse, sqlite, diff)
wizard/             # node services + portal + scheduler + permissions
node/               # docker compose / deployment
web-admin/          # SvelteKit control plane (optional)
docs/               # architecture, contracts

Contract documents (must exist)
	•	Vault Contract
	•	Theme Pack Contract
	•	Contributions Contract (patch bundle format)
	•	AI Policy Contract
	•	Mission/Job Schema

⸻

12. “Universal components” without locking to one framework

Universal components = HTML contracts + data contracts, not a single UI framework.
	•	Publishing components: HTML partials + theme shells (framework-free)
	•	Control plane components: SvelteKit components (containerised)
	•	Shared definitions:
	•	JSON schemas for mission/job/prompt
	•	CSS tokens (typography scale, spacing)
	•	minimal “slot” conventions in shell.html

This gives you portability (static + SvelteKit + WP lane) with one set of rules.

⸻

13. Summary decision statements
	•	Headless WordPress is its own lane (public web + logins + wiki updates). Vault remains truth.
	•	Wizard hosts local portal publishing (LAN/beacon) via static HTML bundles.
	•	SvelteKit is used only for “app UI” (admin/control plane), not for reading/publishing content.
	•	TS core owns deterministic transforms (MD/JSON/SQLite/render/diff).
	•	Vibe is the operator console, not the transform engine.

⸻

If you want, I can also generate a matching repo folder scaffold (themes/core/web-admin layout) that drops cleanly alongside your existing wizard/, wiki/, knowledge/, and .vibe/ directories—without breaking current work.