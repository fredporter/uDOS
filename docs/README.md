# uDOS Documentation

Updated: 2026-03-04

This is the canonical front door for repository documentation.

Contributor-only Dev Mode documentation does not live here. Use `dev/docs/` for `@dev` workspace policy, Goblin, the Dev Mode contributor tool, and contributor GitHub integration.

## Start Here

- Installation: `docs/INSTALLATION.md`
- Stable launcher: `bin/ucode-tui-v1.5.command`
- Public status: `docs/STATUS.md`
- Architecture: `docs/ARCHITECTURE.md`
- Public specs catalog: `docs/specs/README.md`
- Public decisions catalog: `docs/decisions/README.md`
- Workflow quickstart: `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`
- Alpine packaging contract: `docs/specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md`
- Alpine bare-metal guide: `docs/howto/BARE-METAL-Alpine-Install.md`
- Certified demo pack: `docs/examples/ucode_v1_5_release_pack/README.md`
- Documentation map: `docs/specs/DOCUMENTATION-CANONICAL-MAP.md`

## By Need

- Architecture and boundaries:
  `docs/ARCHITECTURE.md`,
  `docs/ARCHITECTURE-INTEGRATION-REFERENCE.md`,
  `docs/decisions/README.md`
- Runtime contracts:
  `docs/specs/README.md`
- Operator how-to docs:
  `docs/howto/`
- Examples and sample packs:
  `docs/examples/`
- Privacy and public policy:
  `docs/PRIVACY.md`,
  `LICENSE`

## Recommended Paths

- New to the repo:
  `README.md`,
  `docs/ARCHITECTURE.md`,
  `docs/INSTALLATION.md`,
  `docs/specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md`
- Working on workflows:
  `docs/decisions/v1-5-workflow.md`,
  `docs/specs/WORKFLOW-SCHEDULER-v1.5.md`,
  `docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md`
- Working on offline assist:
  `docs/decisions/v1-5-offline-assist.md`,
  `docs/specs/OFFLINE-ASSIST-STANDARD-v1.5.md`,
  `docs/examples/udos_ulogic_pack/README.md`,
  `docs/examples/ucode_v1_5_release_pack/01-local-assist-and-knowledge.md`
- Working on operations:
  `docs/howto/MANAGED-WIZARD-OPERATIONS.md`,
  `docs/howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md`
- Working on Sonic or `uHOME`:
  `docs/specs/ALPINE-CORE-PLUGIN-FORMAT-v1.5.md`,
  `docs/howto/BARE-METAL-Alpine-Install.md`,
  `docs/howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md`,
  `docs/examples/ucode_v1_5_release_pack/04-self-hosted-dev-mode.md`
- Working on binders/templates:
  `docs/howto/BINDER-QUICKSTART.md`,
  `docs/examples/`

## Notes

- `docs/INDEX.md` is the quick navigation page.
- `wiki/` is the short orientation layer, not the canonical contract source.
- `dev/docs/README.md` is the contributor documentation front door.
- Planning notes, devlogs, and private milestone tracking belong in local `@dev` workspace paths, not in public `docs/`.
- `docs/STATUS.md` is the public release/status page.
- Superseded documents should move out of the active tree into `docs/.compost/`. Active docs should not keep redirect stubs unless a hard external dependency requires one.
