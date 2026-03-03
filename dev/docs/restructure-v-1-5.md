This is the right moment to lock this down properly before v1.5 spreads further.

I reviewed your current tree output   and the core issue is clear:
	•	Root is polluted with operational + dev + distribution + runtime artifacts.
	•	Hardcoded paths assume repo-relative execution.
	•	Containers don’t have a single authoritative $UDOS_ROOT.
	•	Dev seed, framework seed, runtime, dist, and testing assets are intermingled.
	•	node_modules and __pycache__ are inside core.
	•	Dev docs are at root and scattered in subtrees.
	•	Extensions/plugins don’t have a clear isolation contract.

We’re going to fix this by enforcing:

🔒 One authoritative $UDOS_ROOT

🧱 Clean production root

🧪 All dev isolated in /dev

📦 Overlayable framework layers (wizard → goblin → bistro)

🧩 Plugin/extension isolation contract

🧼 Git hygiene separation between distributable and sprawl

⸻

## Implemented foundation slice (2026-03-04)

The active repo pass now has a concrete v1.5 foundation instead of only target structure:

- grouped Wizard ops surfaces now exist under:
  - `/api/ops/session`
  - `/api/ops/switchboard`
  - `/api/ops/planning/*`
  - `/api/ops/automation/*`
  - `/api/ops/alerts*`
  - `/api/ops/config/*`
  - `/api/ops/releases/*`
  - `/api/ops/logs/*`
- `/admin` now consumes those grouped surfaces directly, including role-aware switchboard data
- planning data is sourced from the full planning overview instead of the compact summary payload
- system/log/config/release visibility now has a logical API grouping for the v1.5 control plane
- Python runtime contract resolution now goes through the canonical root path service instead of direct `parents[2]` root discovery
- Wizard monitoring state now writes under the shared `memory/logs/` tree via the central path helpers

This is not the full file-tree migration yet.
It is the stabilization layer needed before larger moves into cleaner `dev/`, `containers/`, `library/`, and runtime-root boundaries.

⸻

🔥 v1.5 Repository Structure Standard

1️⃣ Hard Rule: Everything runs from $UDOS_ROOT

You define:

export UDOS_ROOT=/opt/udos

or inside container:

ENV UDOS_ROOT=/app

And nothing in the repo uses relative ../.. assumptions anymore.

All path resolution must use:

from pathlib import Path
import os

UDOS_ROOT = Path(os.environ["UDOS_ROOT"]).resolve()

Never Path(__file__).parent.parent.

⸻

🧱 Proposed Clean Root Structure

uDOS/
│
├── bin/                    # CLI entrypoints only
├── core/                   # Runtime engine (pure)
├── providers/              # GPT4All + Wizard Network adapters
├── runtime/                # Active runtime state (empty in git)
├── library/                # Built-in canonical instruction packs
├── extensions/             # Installed plugins (cloned repos)
├── containers/             # Dockerfiles, compose, runtime defs
│
├── schemas/
├── pyproject.toml
├── README.md
├── LICENSE
│
├── dev/                    # 🔥 EVERYTHING dev goes here
│   ├── docs/
│   ├── tooling/
│   ├── test/
│   ├── goblin/             # Scaffolded seed/test server
│   ├── playground/
│   └── experiments/
│
└── .gitignore


⸻

🚫 What Must Leave Root

From your current tree  , these must move:

Move to /dev/docs
	•	AGENTS.md
	•	CHANGELOG.md
	•	CONTRIBUTING.md
	•	CONTRIBUTORS.md
	•	CODE_OF_CONDUCT.md

Move to /dev/goblin
	•	framework/seed installer logic
	•	example seeds
	•	demo vault
	•	example stories
	•	gameplay wireframes

Move to /dev/tooling
	•	smoke tests
	•	patch scripts
	•	sync scripts
	•	setup-vibe scripts
	•	dev mode handlers
	•	mock assets

Move out of git entirely
	•	__pycache__
	•	node_modules
	•	build /dist artifacts
	•	compiled JS

⸻

🧪 dev/goblin = Overlay Test Framework

Goblin becomes:

dev/goblin/
├── server/
│   ├── compose.yml
│   ├── Dockerfile
│   └── config/
│
├── seed/
├── test-vault/
├── scenarios/
└── README.md

Goblin is:

a lightweight overlay framework for wizard server testing

It mounts $UDOS_ROOT and overlays seed + config.

It does NOT redefine paths.

⸻

🧩 Extension & Plugin Isolation

All cloned repos go into:

extensions/
    wizard-ai/
    sonic-driver-rpi/
    binder-sql/

Each extension must follow:

extension-root/
├── extension.json
├── library/
├── commands/
├── providers/
└── containers/ (optional)

Extensions never write into core.
They register via extension.json.

⸻

🐳 Container Structure

containers/
├── base/
│   └── Dockerfile
├── wizard/
│   └── Dockerfile
├── goblin/
│   └── Dockerfile
└── compose.yml

All containers:

ENV UDOS_ROOT=/app
WORKDIR $UDOS_ROOT

No relative filesystem assumptions allowed.

⸻

📦 Library vs Dev Separation

Production library:

/library/
    intents/
    workflows/
    missions/
    sonic/
    templates/

Dev templates and experimental packs go to:

/dev/goblin/seed/

Never mix these.

⸻

🧼 Git Hygiene Strategy

.gitignore (Clean Bistro Mode)

# runtime
/runtime/
/logs/
/artifacts/
/memory/
/deferred_queue/

# python
__pycache__/
*.pyc

# node
node_modules/
dist/

# dev sprawl
/dev/playground/
/dev/experiments/

# local config
.env
config.local.toml


⸻

🧠 Eliminate Hardcoded Locations

Replace all:

Path("core/config")

With:

CORE_DIR = UDOS_ROOT / "core"
CONFIG_DIR = CORE_DIR / "config"

Then pass these via dependency injection.

Never resolve relative to current working directory.

⸻

🧱 Dist Folder Problem

Right now core/dist is bundled compiled JS.

That should become:

/dev/build-artifacts/

And be regenerated by build process.

Production runtime should not contain node_modules or compiled TS unless it’s a built release artifact.

⸻

🪄 Overlay Model (Wizard → Goblin → Bistro)

Think in layers:

Layer 1:
uDOS core

Layer 2:
Wizard runtime

Layer 3:
Goblin test harness (dev only)

Layer 4:
Bistro production deployment

Each layer:
	•	mounts $UDOS_ROOT
	•	overrides configs only
	•	never mutates core structure

⸻

🔐 Final Structural Rules
	1.	Root contains only runtime and production code.
	2.	/dev contains all dev documentation and dev tools.
	3.	$UDOS_ROOT must be required to boot.
	4.	Containers must use $UDOS_ROOT.
	5.	Extensions are self-contained.
	6.	No dev docs at root.
	7.	No build artifacts in core.
	8.	Runtime state never committed.

⸻

🚀 Immediate Actions for You

If I were doing this next:
	1.	Create /dev folder.
	2.	Move all non-runtime docs into /dev/docs.
	3.	Move framework/seed → /dev/goblin.
	4.	Extract dist and node_modules from core.
	5.	Implement UDOS_ROOT resolver utility.
	6.	Refactor all path calls.
	7.	Lock .gitignore.
