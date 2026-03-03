# Dev Mode Spec

Status: active contract  
Updated: 2026-03-03

## Purpose

This spec defines the v1.5 Dev Mode lane.

Dev Mode is not the standard runtime. It is a contributor-only extension surface that sits behind:

- the `dev` certified profile
- the installed `/dev/` extension scaffold
- Wizard-managed activation and lifecycle control

## Core Rule

Dev Mode must be called implicitly.

That means:

- it is not the default terminal runtime
- it is not a normal-user mode switch
- it is entered only when the `dev` profile is enabled and the Dev Mode extension is installed and activated
- standard runtime remains `ucode`

## Runtime Shape

Dev Mode is TUI-only.

Rules:

- the standard interactive runtime is the v1.5 `ucode` TUI
- `vibe` is a Dev Mode contributor TUI surface only
- browser management for Dev Mode install and activation is handled by Wizard GUI
- Wizard may install, uninstall, enable, disable, and report Dev Mode extension state
- normal runtime must not route contributor tooling unless Dev Mode is active

## Extension Gate

Dev Mode requires the `/dev/` folder to exist as the installed extension scaffold.

Required gate conditions:

- `/dev/` is present
- `/dev/extension.json` exists
- the `dev` certified profile is enabled
- the Dev Mode extension is installed and activated through Wizard-owned controls

If those conditions are not met:

- `vibe` is not part of the normal runtime path
- contributor tooling is unavailable
- `ucode` remains on the deterministic local path

## `/dev/` Ownership

The `/dev/` folder is the Dev Mode extension root.

It exists to hold:

- extension governance files
- contributor roadmaps
- contributor task tracking
- contributor templates
- distro-facing extension scaffold content

It must silo contributor planning from the root release tracker.

Required contributor tracking files belong under `/dev/`:

- `/dev/AGENTS.md`
- `/dev/DEVLOG.md`
- `/dev/project.json`
- `/dev/tasks.md`
- `/dev/completed.json`

Contributor roadmaps and contributor task management must stay in `/dev/` rather than leaking into the standard runtime planning surface.

## Local vs Remote Data Separation

The `/dev/` folder is the remote framework and distro template surface.

It is not the place for mutable contributor-local runtime state.

Rules:

- `/dev/` acts as the versioned template and governance scaffold
- contributor-local working data must stay outside the remote template truth
- local-only directories under `/dev/` may exist for sandboxed work, but they are not the canonical remote template payload
- Wizard must treat local mutable Dev Mode data separately from the versioned `/dev/` extension scaffold

Current local-only directories include:

- `/dev/files`
- `/dev/relecs`
- `/dev/dev-work`
- `/dev/testing`

These are local working areas, not the canonical distro template contract.

## `ucode` and `vibe` Integration Rule

`ucode` and `vibe` do not share equal ownership.

Ownership split:

- `ucode` remains the primary runtime entry point
- `vibe` is a Dev Mode-specific contributor shell
- any `vibe` bridge behavior must be gated by active Dev Mode state
- standard runtime fallback must never default into `vibe`

Implication:

- `ucode` may expose profile, extension, and operator controls that report Dev Mode status
- actual contributor-shell behavior belongs only to the active Dev Mode extension lane

## Wizard Ownership

Wizard owns Dev Mode lifecycle behavior.

Wizard responsibilities:

- install and uninstall the Dev Mode extension through GUI controls
- validate `/dev/` framework presence
- activate and deactivate Dev Mode
- manage contributor permissions and profile gates
- manage contributor GitHub integration and sync policy
- keep runtime enforcement out of the core deterministic lane

Core must not take over Dev Mode runtime orchestration.

## GitHub Sync Rule

Dev Mode syncs with GitHub as a contributor lane.

Rules:

- GitHub integration is Dev Mode-specific
- allowed repository, branch, token, and push policy are Wizard-managed
- contributor sync must operate on the extension/repo workflow, not on normal-user runtime assumptions
- GitHub sync is gated by Dev Mode permissions, profile state, and active extension status

## TUI Invocation Rule

Dev Mode should appear as a contributor context entered through profile and extension state, not as a second general-purpose user runtime.

Allowed model:

- install Dev Mode extension in Wizard GUI
- activate Dev Mode extension in Wizard GUI
- enter contributor TUI behavior once the extension gate is satisfied

Disallowed model:

- treating `vibe` as the default terminal for all users
- mixing normal-user `ucode` runtime and contributor-shell behavior without profile gating
- storing standard runtime roadmaps or tasks in `/dev/`

## Related Documents

- `docs/decisions/v1-5-rebaseline.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/specs/MINIMUM-SPEC-VIBE-CLI-UCODE.md`
- `docs/roadmap.md`
