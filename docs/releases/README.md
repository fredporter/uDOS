# uDOS Release Notes Archive

**Current Stable Release:** [v1.4.7](v1.4.7-release-notes.md) (2026-06-30)

---

## Quick Links

### Current Release
- **[v1.4.7 Stable Release Notes](v1.4.7-release-notes.md)** — Consolidated stable release (RECOMMENDED for all installations)

### Roadmap
- **[Canonical Roadmap](../roadmap.md)** — Single source of truth for all development planning

### Legacy Archives
- **[v1.4.3 Release Notes](v1.4.3-release-notes.md)** — Previous stable (2026-02-17, LEGACY)
- **[v1.3.x Release Notes](LEGACY-v1.3.x-release-notes.md)** — Pre-v1.4 archives (2024-2025, END OF LIFE)

---

## Version Overview

### v1.4.7 — Stable Release (Current, RECOMMENDED)
**Release Date:** 2026-06-30
**Status:** Stable, Production-Ready
**Scope:** Consolidation of v1.4.4-6 work, command audit, version unification
**Key Features:** Complete command set (40+), gameplay lenses, GitHub Pages publishing, local libraries, Docker hardening

**See:** [v1.4.7 Release Notes](v1.4.7-release-notes.md)

### v1.4.3 — Previous Stable (Legacy)
**Release Date:** 2026-02-17
**Status:** Legacy (support ends 2026-12-31)
**Scope:** Container readiness, LIBRARY command, modularization
**Migration:** Upgrade to v1.4.7 via `REPAIR --full`

**See:** [v1.4.3 Release Notes](v1.4.3-release-notes.md)

### v1.3.x Series — End of Life
**Versions:** v1.3.0 to v1.3.26
**Status:** UNSUPPORTED (support ended 2026-06-30)
**Archive:** [Legacy v1.3.x Notes](LEGACY-v1.3.x-release-notes.md)
**Migration:** Mandatory upgrade to v1.4.7

---

## Release Timeline

```
v1.3.0 ──────────────────────── v1.3.26  v1.4.0 ──── v1.4.3  v1.4.7 ────→
2024-2025          EOL: 2026-06-30    |      LEGACY: 2026-12-31    CURRENT
(5 years)                              |                            (2 years+)
                                  v1.4.4-6 dev
                                2026-03 to 2026-05
                                (integrated into v1.4.7)
```

---

## Migration Paths

### From v1.3.x → v1.4.7
```bash
# Export old setup
./uDOS.py setup --export > v1.3-config.json

# Install v1.4.7 fresh (download from GitHub)
./uDOS.py setup --import v1.3-config.json

# Validate migration
./uDOS.py repair --full
./uDOS.py verify
```

### From v1.4.0-6 → v1.4.7
```bash
# Simple upgrade (same binary)
./uDOS.py --version          # Check current
./uDOS.py repair --pull      # Pull v1.4.7, reinstall deps
./uDOS.py verify             # Validate
```

---

## Support Policy

| Version | Release | EOL | Status | Support |
|---------|---------|-----|--------|---------|
| **v1.4.7** | 2026-06-30 | 2027-06-30 | **CURRENT** | ✅ Active |
| v1.4.3 | 2026-02-17 | 2026-12-31 | Legacy | ⚠️ Ends 2026-12-31 |
| v1.3.x | 2024-2025 | 2026-06-30 | EOL | ❌ Unsupported |

---

## Channel Guides

### For Users
- Start here: [v1.4.7 Release Notes](v1.4.7-release-notes.md)
- Installation: See "Installation & Upgrade" section in release notes
- Troubleshooting: See "Known Issues" section in release notes

### For Developers
- Roadmap planning: [docs/roadmap.md](../roadmap.md)
- Architecture specs: [docs/specs/](../specs/)
- Contributing: See [CONTRIBUTORS.md](../../CONTRIBUTORS.md)

### For Operations
- Upgrade guide: [v1.4.7 Release Notes → Upgrade Guide](v1.4.7-release-notes.md#upgrading-from-v13x-or-v140-6)
- Deployment: `brew install udos-wizard-full` or Docker images
- Monitoring: `./uDOS.py repair --health-only`

---

## Consolidated Development Work

### v1.4.4-6 Development Cycle (2026-03-01 to 2026-05-31)
**Integration Point:** All work consolidated into v1.4.7 Stable Release

**Key Deliverables:**
- **v1.4.4:** Core hardening, gameplay lenses, TUI genres, command dispatch (2026-03-01 to 2026-03-31)
- **v1.4.5:** Wizard stabilization, GitHub Pages publishing, GUI refinement (2026-04-01 to 2026-04-30)
- **v1.4.6:** Distribution packaging, local libraries, Docker hardening, Sonic standalone (2026-05-01 to 2026-05-31)

**Specifications:**
- [CORE-MODULARIZATION-AUDIT-v1.4.4.md](../specs/CORE-MODULARIZATION-AUDIT-v1.4.4.md)
- [ERROR-HANDLING-v1.4.4.md](../specs/ERROR-HANDLING-v1.4.4.md)
- [GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md](../specs/GAMEPLAY-LENS-ARCHITECTURE-v1.4.4.md)
- [TUI-GENRE-ARCHITECTURE-v1.4.4.md](../specs/TUI-GENRE-ARCHITECTURE-v1.4.4.md)
- [uCLI-COMMAND-DISPATCH-v1.4.4.md](../specs/uCLI-COMMAND-DISPATCH-v1.4.4.md)
- [WIZARD-GITHUB-PAGES-PUBLISH-ARCHITECTURE-v1.4.5.md](../specs/WIZARD-GITHUB-PAGES-PUBLISH-ARCHITECTURE-v1.4.5.md)
- [PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md](../specs/PACKAGING-DISTRIBUTION-ARCHITECTURE-v1.4.6.md)

---

## Archived Development Summaries

**Note:** Legacy development summaries (v1.4.4 prep, branch stabilization plans, etc.) have been consolidated into the canonical [roadmap](../roadmap.md) and [v1.4.7 release notes](v1.4.7-release-notes.md). Historical references maintained in [devlog/ROADMAP-LEGACY.md](../devlog/ROADMAP-LEGACY.md).

---

## References

- **Canonical Roadmap:** [docs/roadmap.md](../roadmap.md)
- **Architecture Decisions:** [docs/decisions/](../decisions/)
- **Specification Index:** [docs/specs/README.md](../specs/README.md) (if available)
- **Contributing Guide:** [CONTRIBUTORS.md](../../CONTRIBUTORS.md)
- **License:** [LICENSE.txt](../../LICENSE.txt)

---

**Last Updated:** 2026-02-20
**Status:** Current and Stable
