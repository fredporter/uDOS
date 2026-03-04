# Copilot Instructions

Use the v1.5 contributor workflow:

- Read root `AGENTS.md` for architecture boundaries.
- Read `dev/AGENTS.md` for `@dev` workspace rules.
- Read `dev/ops/AGENTS.md` for contributor operations rules.
- Keep contributor planning and mission state in `dev/ops/`.
- Keep contributor docs in `dev/docs/`.
- Keep distributable experimental fixtures and overlay tests in `dev/goblin/`.
- Keep runtime logic in `core/` or `wizard/`, not in `dev/`.

Preferred workflow:

1. Check the active contributor mission in `dev/ops/tasks.json` and `dev/ops/tasks.md`.
2. Update `dev/ops/DEVLOG.md` when contributor work changes materially.
3. Put reusable workspace/editor templates in `dev/ops/templates/`.
4. Use `ucode` for standard runtime work and `vibe` only inside the active Dev Mode lane.
