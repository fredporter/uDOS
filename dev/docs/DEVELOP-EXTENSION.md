# Develop Extension Content

Updated: 2026-03-04

For v1.5, `/dev` is not a freeform extension nursery. It is the tracked contributor framework.

## Where Extension Work Belongs

- product/runtime code belongs in `core/`, `wizard/`, or the relevant extension tree
- contributor docs about extension workflows belong in `dev/docs/`
- distributable extension fixtures or examples may live in `dev/goblin/`
- personal experiments stay in ignored local-only `@dev` paths until promoted

## Use `@dev` For

- extension governance guidance
- contributor templates
- review checklists
- generic example manifests or fixtures

## Do Not Use `@dev` For

- shipping runtime logic
- private extension repos
- local scratch projects intended to stay private
- alternate runtime roots

If you need a new tracked extension-facing guide, place it in `dev/docs/howto/`, `dev/docs/specs/`, or `dev/docs/features/` and tie it back to the `@dev` workspace contract.
