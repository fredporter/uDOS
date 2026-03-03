# Dev Mode Policy

## Scope
Dev mode is gated by the installed `/dev/` extension framework, the `dev` certified profile, and admin role permissions.
Related: logging policy and diagnostics scaffolding lives in [docs/LOGGING-API-v1.3.md](docs/LOGGING-API-v1.3.md).

## Rules
- `/dev/` is the versioned Dev Mode extension scaffold and distro template root.
- Dev mode is only available when `/dev/` exists and contains the Dev extension framework.
- Dev mode is restricted to users with both `admin` and `dev_mode` permissions.
- Dev mode is entered implicitly through the active Dev extension lane and related contributor tooling.
- Wizard GUI owns install, uninstall, activation, deactivation, and status.
- The live runtime remains TUI/Dev tooling based for v1.5; `/dev` does not host a separate server.
- If `/dev/` is missing or the user is not `admin`, dev mode must be unavailable and return a friendly soft-failure reason.
- Local mutable working data must stay separate from the versioned `/dev/` template truth.

## Policy Contract (Gate)
Dev mode is gated in both Wizard APIs and uCODE clients.

- **Admin-only**: all `/api/dev/*` calls require a valid `X-Admin-Token` and an admin user role.
- **/dev required**: `/api/dev/status`, `/api/dev/health`, `/api/dev/activate`, `/api/dev/restart`, `/api/dev/clear`, `/api/dev/logs` require `/dev` + the Dev extension framework files to exist.
- **Deactivate exception**: `/api/dev/deactivate` is allowed even if `/dev` is missing so a stale activated state can be cleared safely.

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
## Local-Only Working Areas

The following working directories are local-only and not part of the canonical template contract:

- `/dev/files`
- `/dev/relecs`
- `/dev/dev-work`
- `/dev/testing`

## Rationale
The `/dev/` scaffold provides the framework, templates, governance, and contributor task surfaces for Dev Mode across core, Wizard, extensions, and plugins. It is the explicit gate for permissioned contributor capabilities and keeps local working data separate from the versioned distro template.
