# uDOS Roadmap

**Current Version:** Core v1.0.1.0 | API v1.0.1.0 | App v1.0.2.1 | Wizard v1.0.1.0 | Transport v1.0.1.0  
**Release:** Alpha v1.0.1.0 (Stable Alpha) ✅ **RELEASED** 2026-01-10  
**Next Target:** Alpha v1.0.2.0 (Workspace Architecture + TinyCore Distribution)  
**Last Updated:** 2026-01-13

---

## 🔄 Now (This Week)

### Alpha v1.0.2.0 - Theme System Implementation

**Theme:** Build ThemeOverlay system and integrate 7 complete themes

| Task | Status | Owner | Priority |
|------|--------|-------|----------|
| Theme architecture design | ✅ Complete | Agent | **🔴 CRITICAL** |
| 7 themes configuration | ✅ Complete | Agent | **🔴 CRITICAL** |
| Implementation roadmap | ✅ Complete | Agent | **🔴 CRITICAL** |
| **Phase 1: ThemeOverlay class** | 📋 Ready | Agent | **🔴 HIGH** |
| **Phase 2: Display pipeline integration** | 📋 Planned | Agent | **🔴 HIGH** |
| **Phase 3: Theme commands & testing** | 📋 Planned | Agent | **🔴 MEDIUM** |

---

## 📅 Next (This Month)

### Alpha v1.0.2.0 - Theme System Implementation

**Theme:** Implement ThemeOverlay, integrate display pipeline, enable user theme selection

| Phase | Task | Duration | Owner | Priority |
|-------|------|----------|-------|----------|
| **1** | ThemeOverlay class (load/parse/apply) | 3-4 hrs | Agent | 🔴 HIGH |
| **2** | Display pipeline integration | 2-3 hrs | Agent | 🔴 HIGH |
| **3** | Theme commands (LIST/SET/SHOW) | 2-3 hrs | Agent | 🟡 MEDIUM |
| **4** | Testing all 7 themes | 2 hrs | Agent | 🔴 CRITICAL |
| **5** | Documentation update | 1 hr | Agent | 🟡 MEDIUM |

**Total:** ~12 hours over 1 week

**Success Metrics:**
- ✅ ThemeOverlay loads JSON configs correctly
- ✅ Variables replaced semantically
- ✅ Message templates applied properly
- ✅ Logs remain pure (debugging unchanged)
- ✅ All 7 themes render correctly
- ✅ Theme selection commands functional
- ✅ Community extension documented

---

## 🎨 Graphics Architecture (Integrated into v1.0.2.0)

**Three-Tier System:** Markdown Source → ASCII-Teletext (TUI) → SVG (App)

### Tier 1: Markdown Native (SOURCE)
- Flowchart.js syntax
- Mermaid diagrams
- Marp presentations
- Knowledge guide embeds

### Tier 2: ASCII-Teletext (FALLBACK - TUI)
- Unicode block characters
- Box drawing characters
- Color semantics (green=success, red=error, etc)
- **Must semantically align with SVG output**

### Tier 3: SVG (ESCALATION - App/Web)
- Graphics Service renderer (port 5555)
- High-fidelity styling
- Themes: technical, kinetic, classic, handwritten
- Tauri/browser rendering

**See:** [docs/specs/graphics-architecture.md](specs/graphics-architecture.md)

---

## 🗓️ Later (Q1-Q2 2026)

### v1.0.3.0 - TUI Consolidation + Graphics Integration

**Theme:** Fix hardcoding, consolidate duplicates, integrate graphics tiers

| Task | Category | Notes |
|------|----------|-------|
| Box drawing consolidation | TUI | ✅ Partial (width alignment improved, minor wrapping remains) |
| Progress bars consolidation | TUI | |
| Viewport detection utilities | TUI | |
| Column wrapping & alignment refinement | TUI | Fine-tune box element alignment for narrow viewports |
| Graphics Service integration | Graphics | |
| DIAGRAM command | Extension | |

### v1.0.4.0 - Groovebox Extension

**Theme:** Music production with MML sequencing

| Task | Category |
|------|----------|
| MML engine | Extension |
| 808 drum sounds | Extension |
| TUI pattern editor | Extension |
| PLAY/MUSIC commands | Core |

### v1.0.5.0 - Knowledge & Community

**Theme:** Extended knowledge and collaboration

| Task | Category |
|------|----------|
| Knowledge contributions | Knowledge |
| Mesh sync improvements | Transport |
| Group workflows | Core |
| Extension marketplace | Wizard |

---

## 📊 Recent Releases

### Alpha v1.0.1.0 - Stable Alpha (2026-01-10)

**Theme:** Polish, test, document, optimize

#### Release Highlights

✅ **Complete Optimization Round**
- Tauri app: Type consolidation, shared exports, component modularization
- Core: Extracted shared deduplication utilities, archived deprecated modules
- Fixed broken imports, standardized `.archive/` folder naming
- **300+ lines** of duplicate/deprecated code removed

✅ **Testing & Validation**
- 35 integration tests covering all major features
- SHAKEDOWN validation (47 tests) passing
- Handler architecture validated

✅ **Documentation Complete**
- Comprehensive optimization assessments (Tauri + Core)
- Wiki rebuild with current command reference
- Development conventions documented

#### Version Summary

| Component | Version | Changes |
|-----------|---------|---------|
| **Core** | v1.1.0.0 | File deduplication utilities, config consolidation |
| **API** | v1.1.0.0 | Modular architecture stable |
| **App** | v1.0.3.0 | Type sharing, SidebarContainer, font config, format architecture |
| **Wizard** | v1.1.0.0 | AI provider integrations stable |
| **Transport** | v1.0.1.0 | Policy enforcement validated |
| **Knowledge** | v1.0.2.0 | Tech/code categories added |

#### Alpha Workspace: uCode Format Architecture

**App v1.0.3.0** introduces frontmatter-based markdown format specifications:

| Format | Extension | Purpose | Features |
|--------|-----------|---------|----------|
| **uCode** | `-ucode.md` | Executable documents | ```upy code blocks (runtime), accesses maps/docs, extendable |
| **Story** | `-story.md` | Interactive presentations | Self-contained, ```story blocks, typeform-style Q&A, variables/objects, sandboxed |
| **Marp** | `-marp.md` | Full-viewport presentations | Marp prevention styling, slideshow mode |
| **Guide** | `-guide.md` | Knowledge bank articles | Standard knowledge format |
| **Config** | `-config.md` | System configuration | Settings, fonts, icons, custom functions |

**Format Comparison:** Story vs uCode
- **Story**: Sandboxed, distributable, single-file data collection. One .md file that collects/contains data within it and can be returned to sender with results. Typically sandboxed, can be sent with information pre-filled and/or to verify/update. Use cases: user setup variables at installation, step-by-step interactive games.
- **uCode**: Extensible runtime with full uDOS integration. Working ```upy code blocks (runtime) that can access other docs, maps, etc. More extendable than Story format.

**Common Structure** (both executable formats):
- Frontmatter at top (essential) - renders as Svelte tag-style buttons at top of Prose
- Main content with standard markdown + ```story blocks (typeform-style form fields)
- Variables, objects, datasets, functions at bottom (after `---`)

**See also:** [app/docs/](../app/docs/) for detailed format specifications

---

## 🎯 Milestones

| Version | Theme | Target | Status |
|---------|-------|--------|--------|
| v1.0.0.64 | Handler Implementation | 2026-01-07 | ✅ Complete |
| v1.0.1.0 | Stable Alpha | 2026-01-10 | ✅ Complete |
| **v1.0.2.0** | **Theme System** | **Q1 2026** | **🔄 In Progress** |
| v1.0.3.0 | TUI Consolidation | Q1 2026 | 📋 Planned |
| v1.0.4.0 | Groovebox Extension | Q1 2026 | 📋 Planned |
| v1.0.5.0 | Knowledge & Community | Q2 2026 | 📋 Planned |
| v1.1.0 | Beta Release | Q4 2026 | 📋 Future |

---

## 📋 Definition of Done (v1.0.2.0)

- [x] `AGENTS.md` created at root
- [x] `/docs/` spine structure established
- [x] `.vibe/` context files created
- [x] Scoped Copilot instructions per subsystem
- [x] Wizard Server TUI interface
- [x] Wizard Dev Mode functional
- [x] Theme architecture design complete
- [x] All 7 themes fully documented
- [ ] ThemeOverlay class implemented
- [ ] Display pipeline integration
- [ ] Theme selection commands functional

---

## 📚 Watchlist (Known Risks)

| Risk | Impact | Mitigation |
|------|--------|------------|
| TinyCore packaging complexity | HIGH | Start with simple TCZ first |
| Marp/SvelteKit integration | MEDIUM | Verify SvelteKit can wrap Marp rendered styles/content |
| gtx-form vs custom Svelte solution | MEDIUM | Evaluate library/gtx-form vs building Svelte-optimized interactive presentation mode |
| Vibe offline agent setup | MEDIUM | Follow Mistral docs closely |

---

## 🔗 References

- [Engineering Index](docs/_index.md)
- [AGENTS.md](../AGENTS.md)
- [Dev Logs](docs/devlog/)
- [Architecture Decisions](docs/decisions/)
- [Wizard Model Routing Policy](docs/decisions/wizard-model-routing-policy.md)

---

*For detailed historical roadmap, see [dev/roadmap/ROADMAP.md](../dev/roadmap/ROADMAP.md)*  
*Last Updated: 2026-01-13*
