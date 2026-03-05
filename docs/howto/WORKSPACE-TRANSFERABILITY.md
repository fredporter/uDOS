# Workspace Transferability

Updated: 2026-03-04
Status: active how-to

## Canonical Rule

uDOS v1.5 is open-box:
- the repo is replaceable
- user Markdown/data libraries are not
- recovery history lives in `/.compost/`

## What Travels With Git

- source code
- docs and seed templates
- `pyproject.toml`
- `uv.lock`
- launcher scripts and tests

## What Stays Local

| Item | Role |
|------|------|
| `/.venv/` | local Python runtime |
| `.env` | local identity and machine settings |
| `wizard/secrets.tomb` | local encrypted secrets |
| `memory/` | user libraries, workflow artifacts, Sonic overlay data |
| `/.compost/` | backup, trash, and version retention |
| `@dev` local tool state | contributor-only workspace state |

## Reinstall Proof Model

The standard v1.5 expectation is:

```text
destroy or replace repo
-> keep memory/.env/secrets/.compost
-> reinstall runtime
-> restore or reuse local data
-> continue operating
```

That is why `DESTROY` and `RESTORE` are part of the normal runtime contract.

## Move To A New Machine

```bash
git clone <repo-url> uDOS
cd uDOS
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev
./bin/udos
```

To preserve an existing local workspace, transfer:
- `memory/`
- `.env`
- `wizard/secrets.tomb` only if the matching `WIZARD_KEY` is also preserved
- `/.compost/` if you want restore history and older file versions

## Restore Order

1. Clone the repo.
2. Sync `/.venv`.
3. Run `SETUP`.
4. Restore `memory/`.
5. Restore `.env`.
6. Restore `wizard/secrets.tomb` only when the matching `WIZARD_KEY` is present.
7. Use `RESTORE` or inspect `/.compost/` if specific runtime state needs to be recovered.

## Open-Box Notes

- `DESTROY` can clean runtime state without treating Markdown libraries as disposable.
- `RESTORE` and `UNDO` read from `/.compost/<date>/backups/<scope>/`.
- Sonic seeded data stays distributable, while local Sonic user data lives under `memory/sonic/`.
- UTC timestamps remain canonical in stored state; local timezone conversion happens at render time.

## Troubleshooting

- missing Python deps: `UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev`
- missing `.env`: rerun `SETUP`
- locked secrets: restore the correct `WIZARD_KEY` or recreate secrets
- missing generated files: inspect `/.compost/` before assuming data loss

## Canonical Paths

- [INSTALLATION.md](../INSTALLATION.md)
- [COMPOST-POLICY.md](../COMPOST-POLICY.md)
- [UCODE Command Reference](UCODE-COMMAND-REFERENCE.md)
