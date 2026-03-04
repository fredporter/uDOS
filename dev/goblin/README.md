# Goblin

Updated: 2026-03-04

`dev/goblin/` is the distributable dev scaffold and testing-server layer for v1.5.

## Purpose

Goblin carries the public contributor framework that is safe to sync:

- server config stubs
- seed fixtures
- scenario fixtures
- test-vault fixtures

It is not a replacement runtime root and it is not the place for personal scratch work.

## Layout

- `server/`: server-layer examples and config stubs
- `seed/`: seed payloads for repeatable dev scenarios
- `scenarios/`: named fixture scenarios
- `test-vault/`: tracked vault fixtures for dev/test flows
- `tests/`: tracked overlay tests that exercise Wizard-owned services from the contributor lane

## Layering Rule

Goblin layers over Wizard services for development and experimental feature work. It may provide fixtures, tests, and sample server stubs, but it must not become a second runtime owner.
