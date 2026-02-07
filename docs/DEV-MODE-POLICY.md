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

## System Boundaries (Context)
- `core` (uCODE runtime) is the base runtime.
- `wizard` is the brand for connected services (networking, GUI, etc.).
- Both are public OSS and included in github.com/fredporter/uDOS.
- Core can run without Wizard (limited). Wizard cannot run without Core.
- Most extensions/addons require both Core + Wizard.

## Empire & Plugins (Context)
- `/empire/` is a private submodule for a paid business extension; keep it separate.
- Empire should soft-fail when missing or unsupported and remain isolated from personal/user features.
- External services/addons should be cloned (not forked/modified), credited, and updated via pulls.
- uDOS should containerize and overlay UI without modifying upstream repos.

## Rationale
The `/dev/` submodule provides the templates and structure for vibe-cli coding across core, wizard, extensions, and plugins. It is a public, open-source extension for contributors, and serves as the explicit gate for developer capabilities.
