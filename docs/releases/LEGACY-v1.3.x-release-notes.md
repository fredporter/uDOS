# uDOS v1.3.x Release Archives (End of Life)

**Status:** UNSUPPORTED — Support ended 2026-06-30
**Migration Required:** Upgrade to [v1.4.7](v1.4.7-release-notes.md)
**Contact:** See [CONTRIBUTORS.md](../../CONTRIBUTORS.md) for historical context

---

## Version Archive

This document consolidates release materials from the v1.3.x development cycle (2024-2025). These versions are no longer supported and all installations should upgrade to v1.4.7.

### Available Releases

| Version | Release | Scope | File |
|---------|---------|-------|------|
| v1.3.26 | 2025-12 | Final v1.3 iteration | v1.3.26-final.json |
| v1.3.25 | 2025-11 | Seed depth refinement | v1.3.25-seed-depth.json |
| v1.3.24 | 2025-10 | Zone migration | — |
| ... | ... | ... | — |
| v1.3.16 | 2025-02 | Release checklist | v1.3.16-release-checklist.md* |
| v1.3.17 | 2025-03 | Sonic auth rate limit | v1.3.17-sonic-auth-rate-limit-review.md* |
| v1.3.18 | 2025-04 | Spatial loc-id migration | v1.3.18-spatial-locid-z-migration-notes.md* |
| v1.3.19 | 2025-05 | Seed depth foundation | v1.3.19-seed-depth-foundation.md* |

*Archived files available in [docs/devlog/archive/](../devlog/archive/) for historical reference

---

## Consolidated Release Notes

### v1.3.19 — Seed Depth Foundation (2025-05)
**Key Feature:** Local seeding depth system for immersive exploration
**See:** [v1.3.19-seed-depth-foundation.md](../devlog/archive/v1.3.19-seed-depth-foundation.md)

### v1.3.18 — Spatial Loc-ID Z Migration (2025-04)
**Key Change:** 3D spatial coordinate migration (x,y,z loc-IDs)
**See:** [v1.3.18-spatial-locid-z-migration-notes.md](../devlog/archive/v1.3.18-spatial-locid-z-migration-notes.md)

### v1.3.17 — Sonic Auth & Rate Limiting (2025-03)
**Focus Areas:**
- Authentication hardening for Sonic subsystem
- Rate limiting policies and enforcement
**See:**
- [Sonic Auth Review](../devlog/archive/v1.3.17-sonic-auth-rate-limit-review.md)
- [Sonic Release Checklist](../devlog/archive/v1.3.17-sonic-release-checklist.md)

### v1.3.16 — Modularization Checkpoint (2025-02)
**Key Milestone:** First major modularization phase
**See:** [v1.3.16-release-checklist.md](../devlog/archive/v1.3.16-release-checklist.md)

---

## Migration from v1.3.x → v1.4.7

### 1. Pre-Migration Checklist
```bash
# Capture your current configuration
./uDOS.py setup --export v1.3-config.json
./uDOS.py backup --full v1.3-backup.tar.gz

# Validate existing state
./uDOS.py repair --diagnose
./uDOS.py verify
```

### 2. Install v1.4.7
```bash
# Download and install v1.4.7
# See https://github.com/yourusername/uDOS/releases/tag/v1.4.7

# Or via package manager:
brew install udos-wizard-full@1.4.7
# or
pip install udos[wizard]==1.4.7
```

### 3. Migrate Configuration
```bash
# Restore v1.3 settings (auto-converted to v1.4.7)
./uDOS.py setup --import v1.3-config.json

# Run full repair to apply version-specific updates
./uDOS.py repair --full

# Validate migration
./uDOS.py verify
./uDOS.py repair --health-only
```

### 4. Validation & Testing
```bash
# Check version
./uDOS.py --version  # Should show v1.4.7

# Run system tests
./uDOS.py test --all

# Verify known good commands
./uDOS.py help  # Should show v1.4.7 command set
./uDOS.py resource list gold  # Quick command test
```

### 5. Backup & Archive
```bash
# Keep v1.3 exports for reference (not needed operationally)
mv v1.3-config.json archive/v1.3-config-final.json
mv v1.3-backup.tar.gz archive/v1.3-full-backup.tar.gz
```

---

## Breaking Changes v1.3.x → v1.4.7

### Removed Commands (Hard Fail, No Fallback)
- `SERF` (superseded by `RESOURCE`)
- `PLOT` (merged into `MARKET`)
- `SIGNAL` (integrated into `COMM`)

### Deprecated Commands (Shim with Warning)
- `BANK:QUERY` → `WALLET:QUERY` (automatic redirect)
- `SHOP:BROWSE` → `MARKET:BROWSE` (automatic redirect)

### Configuration Changes
- `config/tui.json` renamed to `config/genres/default.json`
- `colors/` legacy folder structure → `themes/genre-{name}/colors/`
- Environment variable `UDOS_MONOREPO` removed (no impact; always offline)

### Breaking API Changes
- Command return codes standardized to 3-digit format: `{category}{severity}{code}`
- Old format `XYZABC` → New format `123` or `456`
- See [Error Handling Spec](../specs/ERROR-HANDLING-v1.4.4.md) for full mapping

---

## Historical Decisions & Context

For understanding the evolution of uDOS design:
- **Why modularization?** See [devlog/ROADMAP-LEGACY.md](../devlog/ROADMAP-LEGACY.md)
- **v1.3 design rationale?** Consult CONTRIBUTORS.md or contact original authors

---

## Support & Questions

**v1.3.x is End of Life** — No further updates or bug fixes planned.

For issues:
1. **First:** Upgrade to v1.4.7 (will solve most issues)
2. **If still problem:** File issue at https://github.com/yourusername/uDOS/issues (specify v1.4.7)
3. **Legacy question?** Check [CONTRIBUTORS.md](../../CONTRIBUTORS.md) or [devlog/ROADMAP-LEGACY.md](../devlog/ROADMAP-LEGACY.md)

---

**Last Updated:** 2026-02-20
**Archive Status:** Closed (v1.3.x EOL)
**See Also:** [v1.4.7 Release Notes](v1.4.7-release-notes.md) | [Roadmap](../roadmap.md)
