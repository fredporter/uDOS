# Dev Mode Policy

## Scope
Dev mode is gated by the public developer submodule and admin role permissions.
Related: logging policy and diagnostics scaffolding lives in [docs/LOGGING-API-v1.3.md](docs/LOGGING-API-v1.3.md).

## Rules
- `/dev/` is a public submodule repo (github.com/fredporter/uDOS-dev).
- Dev mode is only available when `/dev/` exists and contains the developer template.
- Dev mode is restricted to `admin` role users only.
- Dev mode enables the `DEV ON` / `DEV OFF` controls and related developer tooling.
- If `/dev/` is missing or the user is not `admin`, dev mode must be unavailable and return a friendly soft-failure reason.

## Policy Contract (Gate)
Dev mode is gated in both Wizard APIs and uCODE clients.

- **Admin-only**: all `/api/dev/*` calls require a valid `X-Admin-Token` and an admin user role.
- **/dev required**: `/api/dev/status`, `/api/dev/health`, `/api/dev/activate`, `/api/dev/restart`, `/api/dev/clear`, `/api/dev/logs` require `/dev` + templates to exist.
- **Deactivate exception**: `/api/dev/deactivate` is allowed even if `/dev` is missing (to shut down a stale Goblin process).

### Expected Failure Modes
- `403` — not admin / missing admin token → return a friendly “admin required” message.
- `412` — `/dev` missing or templates absent → return a friendly “dev submodule missing” message.

## System Boundaries (Context)
- `core` (uCODE runtime) is the base runtime.
- `wizard` is the brand for connected services (networking, GUI, etc.).
- Both are public OSS and included in github.com/fredporter/uDOS.
- Core can run without Wizard (limited). Wizard cannot run without Core.
- Most extensions/addons require both Core + Wizard.

## Empire & Plugins (Context)
- Empire should soft-fail when missing or unsupported and remain isolated from personal/user features.
- External services/addons should be cloned (not forked/modified), credited, and updated via pulls.
- uDOS should containerize and overlay UI without modifying upstream repos.

## Rationale
The `/dev/` submodule provides the templates and structure for vibe-cli coding across core, wizard, extensions, and plugins. It is a public, open-source extension for contributors, and serves as the explicit gate for developer capabilities.
