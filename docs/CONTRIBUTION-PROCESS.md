# Contribution Process (Containers + Extensions)

**Goal:** Safe, repeatable onboarding for community containers.

---

## 1) Fork + Local Test
- Fork repo and create container definition under `library/<name>/`.
- Test container locally via Goblin dev routes.

## 2) Submit PR
- Include `container.json` + README + any Dockerfile/scripts.
- Provide permissions required by the container.

## 3) Security Review
- Permissions + network scope reviewed.
- Signature policy applied (v1.3.2+).

## 4) Merge + Publish
- Wizard plugin registry updated.
- Container appears in `/api/plugin/list`.

---

## Required Files
- `library/<name>/container.json`
- `library/<name>/README.md`

