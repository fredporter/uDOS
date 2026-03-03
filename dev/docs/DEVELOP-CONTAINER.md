# Develop Container Content

Updated: 2026-03-04

Container work in v1.5 should follow the same contributor boundary as the rest of `@dev`.

## Boundary

- shipping container definitions belong in their runtime/product lane
- contributor-facing container guidance belongs in `dev/docs/`
- generic scaffold or test-server examples belong in `dev/goblin/`
- one-off local container experiments belong in ignored local-only `@dev` paths

## Goblin Use

Use `dev/goblin/server/` for distributable server-layer examples and config stubs tied to contributor workflows.

Do not turn Goblin into:

- a second deployment root
- a private container playground committed to git
- a replacement for product-owned container definitions

## Promotion Rule

Before promoting container-related work into tracked `@dev`, confirm it is:

- generic
- reusable
- contributor-facing
- aligned with the `@dev` workspace contract
