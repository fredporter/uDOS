# uDOS Python Environments Dev Brief

*Core stdlib-only + Wizard full venv + Dev piggybacks Wizard + Core TS runtime*

## Goal

Keep **uDOS core** maximally stable, portable, and dependency-light by using **Python stdlib only** (no venv). Put all third-party Python dependencies into a single **Wizard venv**, which ships alongside core. The optional **/dev** add-on **piggybacks the Wizard venv** (no separate dev venv by default).

Additionally, uDOS core includes a **TypeScript runtime layer** that is **light but critical**. It runs alongside core Python stdlib tools *when the capability exists* (Node runtime present or bundled). This enables modern JS/TS-driven features without contaminating core with heavy Python deps.

This creates a clean boundary:

- **Core (Python) = boring + durable (stdlib-only)**
- **Core (TS) = light + critical runtime capability**
- **Wizard (Python) = powerful + extensible (full venv)**
- **Dev = optional tooling riding Wizard**

---

## Design Principles

1. **Core Python must not require pip**

   - Core Python entrypoints run with system Python (or bundled Python later), using **stdlib only**.

2. **Core TS runtime is allowed, but must remain light**

   - Core can depend on a small, pinned Node/TS runtime capability.
   - TS is used for critical runtime features (CLI orchestration, contracts, renderers, IPC, plugin manifests), not for heavyweight app stacks.

3. **Wizard owns all third-party Python**

   - Anything needing pip packages (HTTP clients, rich UI libs, SDKs, build tools) belongs to Wizard.

4. **Dev depends on Wizard, not Core**

   - /dev is an add-on; it should never impose dependencies on core runtime.
   - Dev tooling can import from Wizard packages and reuse Wizard environment.

5. **Hard boundary enforcement**

   - Core code must never import Wizard deps.
   - Wizard may call core, but core must never depend on wizard.
   - TS core can orchestrate both, but must keep stable contracts and graceful fallbacks.

---

## Repo Layout

```
/
  /core/
    /py/                # core python scripts (stdlib only)
    /ts/                # core TypeScript runtime + libraries (light)
    /bin/               # core CLI entrypoints

  /wizard/
    /py/                # wizard python app + libs
    requirements.in     # high-level deps (optional)
    requirements.txt    # pinned (generated) OR lockfile
    .venv/              # wizard venv (local install or bundled build output)

  /dev/
    /py/                # dev scripts (lint/test/build/docs/etc)
    README.md           # states: uses /wizard/.venv
```

Notes:

- `.venv/` is **gitignored**.
- Requirements/lock files are committed.
- Core TS runtime should have a **build output** directory (e.g. `/core/ts/dist`) committed or produced by release packaging.

---

## Runtime Contracts

### Core Python Contract

Core Python scripts MUST:

- Use only stdlib imports (examples: `argparse`, `json`, `sqlite3`, `logging`, `subprocess`, `pathlib`).
- Never `pip install` anything.
- Never import from `/wizard/` modules.

Core Python scripts MAY:

- Spawn the wizard entrypoint as a subprocess if wizard features are needed.

### Core TS Runtime Contract

Core TS runtime MUST:

- Remain **light** (no large frameworks; avoid heavy transitive dependency trees).
- Provide stable CLI orchestration and **capability detection**.
- Support graceful fallback when Node isn’t available.

Core TS runtime MAY:

- Provide rendering helpers (e.g. grid renderers), schema validators, config loaders.
- Provide IPC adapters (local sockets/stdin) and plugin manifest parsing.
- Call into core Python scripts (stdlib-only) or wizard python (venv) as subprocesses.

### Wizard Python Contract

Wizard MAY:

- Use third-party Python packages installed into `/wizard/.venv`.
- Provide a stable CLI entrypoint callable from core, e.g. `udos wizard ...`
- Expose reusable libs for `/dev` scripts.

### Dev Contract

Dev scripts:

- Must run under Wizard venv by default.
- Must not introduce core runtime dependencies.
- Should fail clearly if Wizard venv isn’t available.

---

## Capability Detection

uDOS core runs in layers depending on what’s installed:

1. **Base Core**: system Python + core stdlib scripts
2. **Core+TS**: Node available (system or bundled) → TS runtime features enabled
3. **Core+Wizard**: Wizard venv installed → wizard commands/features enabled
4. **Core+Wizard+Dev**: dev add-on present → dev tooling enabled (still uses wizard venv)

Pseudo-matrix:

| Capability  | Requirement          | Enabled features                             |
| ----------- | -------------------- | -------------------------------------------- |
| Core Python | `python3`            | core CLI, filesystem, sqlite, logging        |
| Core TS     | `node` (or bundled)  | orchestrator, renderers, validators, plugins |
| Wizard      | `/wizard/.venv`      | server, integrations, richer tooling         |
| Dev         | `/dev` + wizard venv | tests, lint, build, docs                     |

---

## Entry Points

### `udos` launcher behaviour (recommended)

A single `udos` command routes execution:

- `udos core <cmd>` → runs stdlib-only core python (system python)
- `udos ts <cmd>` → runs TS runtime if Node capability exists; otherwise explains fallback
- `udos wizard <cmd>` → ensures Wizard venv exists, then runs via venv python
- `udos dev <cmd>` → runs via Wizard venv (dev piggybacks wizard)

ASCII flow:

```
udos
 ├─ core   -> /core/py/*                      (system python, stdlib only)
 ├─ ts     -> node /core/ts/dist/cli.js       (if node exists)
 ├─ wizard -> /wizard/.venv/bin/python -m ... (venv)
 └─ dev    -> /wizard/.venv/bin/python /dev/py/...
```

### Policy: TS orchestrates, but never becomes a hard requirement

- Core must still work without Node.
- TS can provide nicer UX when present (better rendering, faster routing, validation).

---

## Core TS Runtime Scaffold

### Recommended responsibilities

- Command routing and help output (reads command registry)
- Capability detection (python/node/wizard)
- Config loading and validation
- ASCII grid/table rendering helpers (align with uDOS grid standards)
- Stable “contract” schemas (JSON Schema / zod) for:
  - command manifests
  - plugin manifests
  - workspace/vault path mapping

### Suggested structure

```
/core/ts/
  package.json
  tsconfig.json
  /src/
    cli.ts
    capabilities.ts
    commands/
      index.ts
    render/
      grid.ts
      table.ts
    contracts/
      manifest.schema.json
      settings.schema.json
    utils/
      paths.ts
      exec.ts
  /dist/             # build output
```

### Versioning + pinning

- Keep dependencies minimal (prefer built-ins).
- Pin package versions.
- Prefer bundling build output in release artifacts.

---

## Wizard Venv Lifecycle

### Create / Update Wizard venv

Wizard installation is explicit:

- `udos wizard install`

  - create `/wizard/.venv`
  - install pinned deps
  - run minimal smoke test

- `udos wizard doctor`

  - validates venv, python version, required packages, permissions

### Offline-first option

Support a “wheelhouse” directory (optional) so Wizard can install without internet:

```
/wizard/wheels/
  *.whl
```

Then install with `--no-index --find-links`.

---

## Dependency Management Policy

### Wizard dependency files

- `/wizard/requirements.in` (optional, human-edited)
- `/wizard/requirements.txt` (pinned, committed)
- Or a lockfile approach (`uv`, `pip-tools`, etc). The rule is: **Wizard deps are pinned**.

### Rules

- Add third-party deps **only** to Wizard.
- Core Python remains stdlib-only.
- Core TS remains minimal and pinned.
- Dev tooling deps go into Wizard requirements (since dev piggybacks wizard).

---

## Guardrails (must-have)

### 1) Core “stdlib-only” enforcement (Python)

Add a CI check that scans `/core/py` imports and fails if any non-stdlib module is imported.

### 2) Core TS “lightweight” enforcement

Add a CI check that:

- blocks adding heavy frameworks
- flags large dependency graphs (e.g. threshold on transitive deps)

### 3) Clear failure mode

If user runs `udos wizard ...` or `udos dev ...` without Wizard venv:

- Print one friendly error:
  - “Wizard environment not installed. Run: `udos wizard install`”
- Exit non-zero.

If user runs `udos ts ...` without Node:

- Print:
  - “Node runtime not detected. Falling back to core mode.”
- Provide the equivalent core command if possible.

### 4) Avoid accidental coupling

- Core treats Wizard as an optional capability.
- Wizard exposes a stable CLI API so core never imports wizard code.

---

## Logging + Paths

- Core logs go to `~/memory/logs/` (existing uDOS convention).
- Wizard logs also go to `~/memory/logs/` but namespaced, e.g.:
  - `wizard.log`, `wizard-error.log`
- Dev logs are optional; if enabled, also go to `~/memory/logs/` with `dev-*.log`.

---

## Minimal Commands Spec

- `udos core <cmd>`
- `udos ts <cmd>`
- `udos wizard install`
- `udos wizard doctor`
- `udos wizard <cmd>`
- `udos dev <cmd>` (requires wizard venv)

---

## Definition of Done

- Core Python runs on a clean system Python with **no pip installs**.
- Core TS runtime is optional, minimal, and works when Node exists.
- Wizard installs into `/wizard/.venv` from pinned requirements.
- Dev scripts run using `/wizard/.venv` with no extra venv.
- CI blocks non-stdlib imports in `/core/py`.
- CI flags heavyweight TS deps.
- Error messages are clear when capabilities are missing.

---

## 7.4 Pytest Layout & Enforcement (Architecture Guard)

### Why this matters

A single repo-wide pytest entrypoint is good, but we must ensure tests do not accidentally blur the boundary between:

- **Core** (stdlib-only, no venv required)
- **Wizard/Dev** (requires venv)
- **TS runtime** (requires Node)

### Recommended test structure (repo-aligned)

```text
/tests/
  core/        # MUST pass with system Python only (no venv)
  wizard/      # MUST require venv
  dev/         # MUST require venv
  ts/          # runs only if Node exists
  fixtures/    # shared fixtures (vaults, sample trees, etc.)