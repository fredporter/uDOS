# Dev Tools

Updated: 2026-03-04
Status: contributor lane summary

In v1.5, contributor tooling is organized under the `@dev` workspace.

## What `@dev` Means

- mount path: `/dev`
- tracked payload: `dev/ops/`, `dev/docs/`, and `dev/goblin/`
- local-only sprawl: `dev/files/`, `dev/relecs/`, `dev/dev-work/`, `dev/testing/`
- activation path: Wizard Dev Mode controls and `/api/dev/*`

## Canonical Contributor Docs

- [../dev/docs/README.md](../dev/docs/README.md)
- [../dev/docs/DEV-MODE-POLICY.md](../dev/docs/DEV-MODE-POLICY.md)
- [../dev/docs/specs/DEV-WORKSPACE-SPEC.md](../dev/docs/specs/DEV-WORKSPACE-SPEC.md)
- [../dev/docs/features/GITHUB-INTEGRATION.md](../dev/docs/features/GITHUB-INTEGRATION.md)
- [../dev/docs/howto/GETTING-STARTED.md](../dev/docs/howto/GETTING-STARTED.md)

## Repo Split

- Root `docs/`:
  operator/runtime docs only
- `dev/docs/`:
  contributor policy, workflow, Goblin, and GitHub lane docs
- `wiki/`:
  short orientation pages only

## Related Files

- Workspace file:
  [../dev/ops/templates/uDOS-dev.code-workspace](../dev/ops/templates/uDOS-dev.code-workspace)
- Contributing guide:
  [../CONTRIBUTING.md](../CONTRIBUTING.md)
