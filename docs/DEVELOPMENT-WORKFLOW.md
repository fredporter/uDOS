# Development Workflow - Clean & Ready

**Date:** 2026-01-18  
**Repository:** uDOS  
**Branch:** main  
**Status:** ✅ Ready to resume development

---

## Repository Structure (Cleaned)

```
uDOS/
├── 📄 AGENTS.md                  ← Development rules + boundaries
├── 📄 CODE_OF_CONDUCT.md         ← Community standards
├── 📄 CONTRIBUTORS.md, CREDITS.md, DISCLAIMER.md, PRIVACY.md
│
├── 📁 /app                       ← Tauri desktop GUI (v1.0.3)
├── 📁 /bin                       ← Launch scripts
├── 📁 /core                      ← TypeScript runtime (v1.1.0)
├── 📁 /dev                       ← Development tools
│   └── /goblin                   ← Dev server (v0.2.0)
│
├── 📁 /docs                      ← CANONICAL DOCUMENTATION
│   ├── roadmap.md               ← Current development priorities (MAIN)
│   ├── decisions/               ← Architecture decisions
│   ├── devlog/                  ← Development logs (YYYY-MM.md)
│   ├── howto/                   ← Repeatable procedures
│   ├── specs/                   ← Technical specifications
│   ├── integration/             ← Phase docs & config frameworks
│   └── archive/                 ← Historical docs & test suites
│
├── 📁 /empire                    ← CRM extension (v1.0.0.1)
├── 📁 /groovebox                 ← Music production
├── 📁 /library                   ← Private extensions
├── 📁 /memory                    ← Session data + logs
│
├── 📁 /public                    ← DISTRIBUTION (CLEAN)
│   ├── distribution/            ← Release packages
│   ├── extensions/              ← Public APIs (API, transport, vscode)
│   ├── knowledge/               ← Knowledge base
│   ├── library/                 ← Shared UI components
│   ├── packages/                ← Plugin packages
│   ├── wiki/                    ← Public wiki
│   └── wizard/                  ← Production server (v1.0.0.1)
│       ├── services/            ← OAuth, HubSpot, Notion, iCloud (Phase 6)
│       ├── routes/              ← API endpoints
│       ├── dashboard/           ← Web dashboard (Svelte)
│       ├── config/              ← Configuration
│       └── server.py            ← Main FastAPI app
│
└── 📁 .github                    ← CI/CD + instructions
```

---

## Key Statistics

| Area | Count | Status |
|------|-------|--------|
| **Root .md files** | 6 | ✅ Clean (essential only) |
| **/public test files** | 0 | ✅ Moved to /docs |
| **/public dev docs** | 0 | ✅ Moved to /docs |
| **Component versions** | 8 | ✅ Independent versioning |
| **/docs sections** | 7 | ✅ Well-organized |
| **API endpoints** | 19+ | ✅ Documented |
| **Services** | 40+ | ✅ Modular, separated |

---

## Development Workflow

### Starting a Development Session

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Check Wizard Server (recommended)
python public/wizard/server.py                # Interactive console + server
# or in another terminal
python public/wizard/server.py --no-interactive

# 3. Check component versions
python -m core.version check

# 4. Run tests as needed
pytest memory/tests/ -v                       # Core tests
pytest public/wizard/services/ -v             # Wizard service tests
```

### Development Priorities (From Roadmap)

**Phase 6A (Next - 2 weeks):** OAuth2 Foundation
- Set up OAuth provider credentials
- Implement authorization code flow
- Add token refresh management
- Wire into Wizard server

**Phase 6B-6D (Queued):** Service Integrations
- HubSpot CRM sync (2 weeks)
- Notion bidirectional sync (2 weeks)
- iCloud backup relay (2 weeks)

### Documentation Workflow

**Before coding:**
- Read [AGENTS.md](AGENTS.md) — Development rules
- Check [docs/roadmap.md](docs/roadmap.md) — Current priorities
- Review [docs/decisions/](docs/decisions/) — Architecture context

**During development:**
- Update [docs/devlog/YYYY-MM.md](docs/devlog/) — Keep log updated
- Create/update specs in [docs/specs/](docs/specs/)

**After completing features:**
- Move implementation docs to [docs/integration/](docs/integration/)
- Archive old docs to [docs/archive/](docs/archive/)

### Key Files to Know

| File | Purpose |
|------|---------|
| [AGENTS.md](AGENTS.md) | Development rules, workspace boundaries, policies |
| [docs/roadmap.md](docs/roadmap.md) | Current version, phases, progress |
| [public/wizard/README.md](public/wizard/README.md) | Wizard Server overview |
| [docs/WIZARD-SERVER-PROGRESS-REVIEW.md](docs/WIZARD-SERVER-PROGRESS-REVIEW.md) | Detailed status + Phase 6 plan |
| [docs/decisions/wizard-model-routing-policy.md](docs/decisions/wizard-model-routing-policy.md) | AI routing + cost tracking |
| [core/version.py](core/version.py) | Version management |

---

## CI/CD & Testing

```bash
# Check all versions
python -m core.version check

# Run shakedown (system validation)
source .venv/bin/activate
./start_udos.sh
# Then type: SHAKEDOWN

# Run pytest
pytest memory/tests/ -v
pytest core/tests/ -v
pytest public/extensions/api/tests/ -v
```

---

## Transport Policy (Non-Negotiable)

✅ **Private Transports (Commands + Data):**
- MeshCore (primary P2P)
- Bluetooth Private (paired devices)
- NFC (physical contact)
- QR Relay (visual transfer)
- Audio Relay (acoustic packets)

❌ **Public Channels (No Data):**
- Bluetooth Public (beacons only, never carry uDOS data)

[Full policy](docs/decisions/wizard-model-routing-policy.md)

---

## Version Management

```bash
# Check versions
python -m core.version check

# Bump a component
python -m core.version bump core build       # Increment build
python -m core.version bump wizard patch     # Increment patch
python -m core.version bump api minor       # Increment minor

# NEVER hardcode version strings
```

**Current Versions:**
- Core: v1.1.0.0
- API: v1.1.0.0
- Wizard: v1.0.0.1
- App: v1.0.3.0
- Goblin: v0.2.0.0

---

## Git Workflow

```bash
# Standard commit (features)
git add <files>
git commit -m "feat: description"

# Documentation
git commit -m "docs: description"

# Bug fixes
git commit -m "fix: description"

# Refactoring
git commit -m "refactor: description"
```

**Important:** Always reference:
- Specific files/line numbers
- Phase/version number
- Related issues/decisions

---

## Next Steps

1. ✅ **Cleanup Complete** — Root and /public folders cleaned
2. ✅ **Documentation Organized** — All docs in /docs/, archive ready
3. ✅ **Wizard Review Done** — Progress assessed, Phase 6 ready
4. 📋 **Phase 6A Ready** — OAuth foundation implementation
   - Obtain OAuth provider credentials
   - Set up test applications
   - Implement OAuthHandler methods
   - Wire into server.py
   - Create test suite

---

## Useful Commands

```bash
# View recent commits
git log --oneline -10

# Check git status
git status

# View changes
git diff

# Stash work
git stash

# Create feature branch (if using branches)
git checkout -b phase-6a-oauth
```

---

## Support Resources

- **Development Rules:** [AGENTS.md](AGENTS.md)
- **Architecture Guide:** [docs/decisions/](docs/decisions/)
- **How-To Guides:** [docs/howto/](docs/howto/)
- **Technical Specs:** [docs/specs/](docs/specs/)
- **Roadmap:** [docs/roadmap.md](docs/roadmap.md)
- **Wizard Details:** [docs/WIZARD-SERVER-PROGRESS-REVIEW.md](docs/WIZARD-SERVER-PROGRESS-REVIEW.md)

---

**✅ Repository is clean, organized, and ready for Phase 6A implementation.**

_Last Updated: 2026-01-18_  
_Status: READY FOR DEVELOPMENT_
