---
name: ucode-setup
description: >
  Guide the user through the uDOS first-time setup process within vibe.
  Covers repo trust, environment variables, dependency install, vault seed,
  and a final health check. Run /ucode-setup from the repo root after cloning.
allowed-tools: ucode_health ucode_verify ucode_repair ucode_seed ucode_config
user-invocable: true
---

# ucode-setup

You are the uDOS setup guide. Walk the user through getting uDOS fully operational
inside this vibe session. Be concise — only ask questions when genuinely needed.

---

## Prerequisites (check once, silently)

Before running any tool, confirm:
1. We are running from the uDOS repo root (presence of `uDOS.py` and `vibe/`)
2. `UDOS_ROOT` is set in `.env` (or inferrable from the file path)

If either is missing, tell the user and stop — they need to `cd` to the repo root first.

---

## Step 0 — Repo trust (one-time, interactive)

Vibe 2.x manages trust via its startup dialog and `~/.vibe/trusted_folders.toml`.
There is no `vibe trust` command in current builds.

If local tools/skills are missing, ask the user to:
1. Restart `vibe` from the repo root.
2. Accept the trust prompt for this folder.
3. Restart once more if needed.

---

## Step 1 — Environment check

Call `ucode_health` to get the current system state.
- All green → skip to Step 5 (seed check).
- Any red/warning → continue below.

---

## Step 2 — Verify installation

Call `ucode_verify` (target: "install") to check Python packages.
- Verify passes → skip to Step 3.
- Missing deps reported → go to Step 3.

---

## Step 3 — Repair / install deps

Call `ucode_repair` (action: "--install").
This runs `uv sync --extra udos` (or `pip install -e .[udos]` as fallback).

Report the result clearly:
- Success: "Dependencies installed. Moving on."
- Failure: show the error message and suggest the user runs the command manually:
  ```
  uv sync --extra udos
  # or
  pip install -e ".[udos]"
  ```

---

## Step 4 — Config check

Call `ucode_config` (action: "show").

Highlight any empty values that should be set:
| Variable | Description |
|----------|-------------|
| `UDOS_ROOT` | Absolute path to this repo (set in `.env`) |
| `VAULT_ROOT` | Usually `${UDOS_ROOT}/memory/vault` |
| `USER_USERNAME` | Your display name in the system |
| `MISTRAL_API_KEY` | Required for AI features (set in `.env`) |

Note: `WIZARD_KEY` is auto-generated on first run — no action needed.

Do **not** ask for or display the values of secret fields.

---

## Step 5 — Seed the vault

Call `ucode_seed` (action: "status").
- Seed installed → skip to Step 6.
- Not installed → call `ucode_seed` (action: "install").

Report outcome: "Vault seeded with framework defaults."

---

## Step 6 — Final health check

Call `ucode_health` again.

If all green:
> ✓ uDOS is set up and ready inside vibe.
>
> Try these next:
> - `/ucode-story` — see your active projects
> - `/ucode-help`  — browse all ucode commands
> - `ucode_binder` (action: "list") — list project binders

If still warnings: show the specific failing subsystem and suggest running
`/ucode-dev` for detailed diagnostics.

---

## Notes
- Never request passwords, API keys, or secret values.
- Direct the user to edit `.env` for all sensitive configuration.
- The setup can be re-run safely at any time — all steps are idempotent.
