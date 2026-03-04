# uDOS Vision

Updated: 2026-03-04
Status: short direction statement

uDOS aims to be a text-first, inspectable, privacy-respecting runtime with clear boundaries between:
- deterministic local execution
- managed networked services
- contributor-only dev surfaces

## Direction

- local-first by default
- explicit operator and contributor boundaries
- readable docs, commands, and workflow artifacts
- no hidden substitution of cloud behavior for local ownership

## v1.5 Framing

The current milestone is about runtime consolidation and structure:
- one authoritative repo root contract
- Python core + Wizard separation
- `@dev` workspace isolation for contributor flows
- cleaner docs and control-plane grouping

## Canonical Docs

- Vision and contributor direction:
  [../dev/docs/VISION.md](../dev/docs/VISION.md)
- Public status:
  [../docs/STATUS.md](../docs/STATUS.md)
- Rebaseline decision:
  [../dev/docs/decisions/v1-5-rebaseline.md](../dev/docs/decisions/v1-5-rebaseline.md)

---

_"Computing should serve humans, not surveil them."_
