# Distribution Guide (v1.3)

**Purpose:** Define what ships together and how to deploy each component.

---

## Core
- **npm**: `@udos/core`
- **tarball**: `core-v1.3.0.tar.gz`

## Wizard
- **PyPI**: `udos-wizard`
- **Docker**: `fredporter/udos-wizard`

## Sonic
- **GitHub Releases**: USB builder + ISO artifacts.

## App
- **macOS DMG** (alpha).

## Extensions
- Distributed via Wizard plugin API from `library/` definitions.

---

## Release Manifest
See `v1.3.0-release-manifest.yml` for version locks.

---

## Offline-First Policy
- Core must work without Wizard.
- Wizard should prefer local Ollama models.
- Cloud is optional + explicit.

