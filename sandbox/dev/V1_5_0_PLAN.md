# v1.5.0 Development Plan - DEV MODE & Gemini TUI Integration

**Version:** 1.0.0
**Created:** 2025-11-25
**Timeline:** 12 weeks (Q2 2026)
**Status:** 📋 Planned

---

## 📋 Executive Summary

v1.5.0 marks a critical evolution in uDOS development methodology. This release transitions from external AI-assisted development to **integrated AI coding directly within the TUI**, establishes a secure **DEV MODE framework for master users**, and resolves critical **configuration synchronization issues** that block Gemini API integration.

### Core Objectives

1. **DEV MODE Framework** (v1.5.0 Core)
   - Master user authentication and permissions
   - Dangerous operation safeguards
   - Activity logging and audit trails
   - Development tool integration

2. **uCODE Language Refinement** (v1.5.1)
   - Consolidate shortcode syntax: `[COMMAND|option|$variable]`
   - Minimal one-line complex commands
   - Unify CLI and .uscript scripting
   - Human-readable markdown-compatible format

3. **Content Generation & Design** (v1.5.2)
   - Image generation with Gemini Imagen
   - General knowledge article generation
   - Enhanced prompt refinement system
   - REFRESH/REDO for design standard updates
   - TUI testing and validation

4. **Configuration Sync & Polish** (v1.5.3)
   - Fix .env/user.json synchronization
   - Unified configuration manager
   - Resolve username/API key mismatches
   - Shared assets expansion
   - Final testing and documentation

---

## 🗓️ Timeline Overview

| Phase | Duration | Milestone | Deliverables |
|-------|----------|-----------|--------------|
| **v1.5.1** | Weeks 1-4 | uCODE Language Refinement | Shortcode system, minimal commands, .uscript v2.0, example scripts |
| **v1.5.2** | Weeks 5-8 | Content Generation & Design | Image/article generation, prompt refinement, REFRESH/REDO, TUI testing |
| **v1.5.3** | Weeks 9-12 | Config Sync & Finalization | .env fix, ConfigManager, DEV MODE polish, shared assets, docs |

---

## 📊 Detailed Phase Breakdown

### v1.5.1 - uCODE Language Refinement (Weeks 1-4)

**Week 1-2: Syntax Standardization**
- [ ] Finalize `[COMMAND|option|$variable]` shortcode syntax
- [ ] Create shortcode parser with validation
- [ ] Define one-line command structure
- [ ] Establish option priority system
- [ ] Build command validator

**Week 2-3: Command Set Consolidation**
- [ ] Audit CLI vs .uscript command disparities
- [ ] Create unified command registry (50+ commands)
- [ ] Map complex commands to single-line equivalents
- [ ] Build command compatibility layer (CLI ↔ uCODE)
- [ ] Extend command schemas with full parameter specs

**Week 4: Example Scripts & Testing**
- [ ] Extend startup_options.uscript with DEV MODE detection
- [ ] Add image/article generation to content_generation.uscript
- [ ] Create configuration sync repair scripts
- [ ] Build semantic analysis validator
- [ ] Create REPL for interactive uCODE testing

**Deliverables:**
- ✅ uCODE v2.0 specification (syntax, commands, examples)
- ✅ Shortcode parser and validator
- ✅ 3 production .uscript examples
- ✅ 50+ unified command tests

---

### v1.5.2 - Content Generation & Design (Weeks 5-8)

**Week 5-6: Gemini Content Generation**
- [ ] Integrate Gemini Imagen API for diagram generation
- [ ] Build `GENERATE IMAGE` command with quality validation
- [ ] Create article generation system (tutorial, reference, how-to)
- [ ] Implement multi-section article assembly
- [ ] Expand enhanced prompts (50+ reusable templates)

**Week 6-7: Design System Evolution**
- [ ] Expand color palettes (C64, ZX Spectrum, Apple II)
- [ ] Create style mixing system (combine retro aesthetics)
- [ ] Implement Teletext Level 2.5/3.5 features
- [ ] Add lighting/texture/composition controls
- [ ] Build interactive preview system

**Week 7-8: REFRESH/REDO & TUI Testing**
- [ ] Extend REFRESH to REDO command (regenerate with new standards)
- [ ] Build diff system (old vs new content side-by-side)
- [ ] Create approval workflow (review before applying)
- [ ] Build batch REFRESH for entire categories
- [ ] Test all .uscript commands in TUI
- [ ] Implement live Gemini integration (OK ASK, OK GENERATE, OK DEBUG)

**Deliverables:**
- ✅ Image generation system (Gemini Imagen)
- ✅ Article generation framework
- ✅ 50+ enhanced prompt templates
- ✅ REFRESH/REDO v2.0 with diff system
- ✅ 40+ content generation tests

---

### v1.5.3 - Configuration Sync & Finalization (Weeks 9-12)

**Week 9-10: Configuration Sync Resolution** ⭐ **CRITICAL**
- [ ] Fix .env path detection (core/.env → root/.env)
- [ ] Create unified ConfigManager class
- [ ] Implement configuration priority system (runtime > user.json > .env > defaults)
- [ ] Build configuration sync manager (bidirectional updates)
- [ ] Fix username/API key synchronization
- [ ] Create configuration migration scripts

**Week 10-11: DEV MODE Finalization**
- [ ] Implement master user detection (environment + password)
- [ ] Create DEV MODE toggle (ON/OFF with confirmation)
- [ ] Build master user command restrictions (whitelist dangerous operations)
- [ ] Add live code reloading (watch files, auto-restart)
- [ ] Implement interactive debugger (breakpoints, step-through)
- [ ] Create performance profiler (timing, memory usage)

**Week 11-12: Shared Assets & Final Testing**
- [ ] Expand font collection (C64, Atari, Apple II bitmap fonts)
- [ ] Build icon library (100+ survival/UI icons)
- [ ] Create pattern library (50+ Teletext/ASCII patterns)
- [ ] Build asset loader with dependency system
- [ ] Run full integration testing (1,733+ tests + 267 new)
- [ ] Update wiki with v1.5.x features
- [ ] Create release notes and upgrade guide

**Deliverables:**
- ✅ ConfigManager with unified sync
- ✅ .env/user.json synchronization fixed
- ✅ DEV MODE with master user permissions
- ✅ Expanded shared assets (fonts, icons, patterns)
- ✅ 30+ config sync tests, 25+ DEV MODE tests
- ✅ Complete v1.5.0 documentation

---

## 🎯 Success Metrics

### Test Coverage
- **Target:** 2,000+ tests (267+ new for v1.5.x)
- **Current:** 1,733 tests (v1.4.0)
- **New Categories:**
  - uCODE Tests: 50
  - Gemini Integration: 40
  - Configuration Sync: 30
  - DEV MODE: 25
  - Content Generation: 40
  - TUI Integration: 50
  - Shared Assets: 32

### Quality Gates
- ✅ 100% pass rate (no failing tests)
- ✅ 85%+ code coverage (up from 80%)
- ✅ Zero critical/high security vulnerabilities
- ✅ <1s average command response time
- ✅ Backward compatibility with v1.4.0
- ✅ All configuration sync issues resolved
- ✅ Gemini API integration fully functional

### User Experience
- ✅ DEV MODE secure and stable
- ✅ All .uscript commands work in TUI
- ✅ CONFIG changes persist across restarts
- ✅ DASH shows correct user information
- ✅ OK commands connect to Gemini successfully
- ✅ Live AI coding assistance operational

---

## 🔧 Critical Issues Resolved

### 1. Configuration Sync (v1.5.3) 🔴 **CRITICAL**

**Problem:**
- .env file not found (wrong path: `core/.env` instead of root `.env`)
- Username doesn't persist (CONFIG updates runtime only, not files)
- Dashboard shows stale user info (`testuser` vs `Fred`)
- Gemini API fails (can't find .env)

**Solution:**
- Fix .env path in `gemini_service.py`
- Create ConfigManager for unified configuration
- Implement bidirectional sync (runtime ↔ files)
- Auto-create .env on first run
- Validate configuration integrity

**Impact:** Unblocks Gemini API integration, fixes user experience issues

### 2. uCODE Language Fragmentation (v1.5.1)

**Problem:**
- CLI commands ≠ .uscript commands (inconsistent syntax)
- Complex operations require multiple commands
- No human-readable scripting format
- Hard to chain commands or build workflows

**Solution:**
- Unified command registry (single source of truth)
- Shortcode system for parameters
- One-line complex commands
- Markdown-compatible .uscript format
- Command compatibility layer

**Impact:** Makes scripting easier, improves developer experience

### 3. No Development Environment (v1.5.0)

**Problem:**
- No integrated AI coding assistance
- Dangerous operations available to all users
- No debugging tools in TUI
- Code changes require full restart

**Solution:**
- DEV MODE with master user restrictions
- Gemini TUI integration (OK ASK, OK GENERATE, OK DEBUG)
- Interactive debugger and profiler
- Hot reload system (watch files, auto-reload)
- Activity logging and audit trails

**Impact:** Enables AI-assisted development, improves security, faster iteration

---

## 🚀 Key Features

### DEV MODE (Master User Only)

**Authentication:**
```
uDOS> DEV MODE ON
🔐 Master User Authentication Required
Enter master password: ********
✅ DEV MODE ACTIVATED
📋 [MAIN] 🔧 DEV>
```

**Capabilities:**
- 🤖 Live Gemini coding assistance (OK ASK, OK GENERATE, OK DEBUG, OK EXPLAIN)
- 🛠️ Development tools (debugger, profiler, test runner)
- ⚠️ Dangerous operations (DELETE without confirmation, DESTROY, direct DB access)
- 🔄 Hot reload (watch files, auto-restart modules)
- 📊 Activity logging (complete audit trail)

**Safety:**
- Master password required
- All actions logged to `memory/logs/dev_mode.log`
- Disabled by default
- Only available to configured master user

### uCODE v2.0 Syntax

**Shortcodes:**
```
[GENERATE|category=water|style=technical|diagrams=3]
[REFRESH|category=fire|quality-min=0.8|update-diagrams]
[MISSION|action=create|template=quest|difficulty=hard|reward=500xp]
```

**One-Line Complex Commands:**
```
GENERATE GUIDE water/filtration --style=technical --diagrams=3 --output=knowledge/water/
CONVERT PDF manual.pdf --extract-diagrams --format=markdown --category=medical
REFRESH CATEGORY fire --quality-min=0.8 --update-diagrams --backup
```

**Markdown-Compatible Scripts:**
```markdown
---
name: Batch Water Guide Generation
version: 1.0.0
author: Fred
---

# Water Guide Generation Workflow

## Step 1: Prepare Environment
[CONFIG|check|requirements]
[WORKSPACE|switch|sandbox]

## Step 2: Generate Guides
[GENERATE|category=water|count=10|style=technical]
[VALIDATE|category=water|quality-min=0.8]

## Step 3: Review and Publish
[GUIDE|review|category=water]
[PUBLISH|category=water|tier=public]
```

### Gemini Content Generation

**Image Generation:**
```
uDOS> GENERATE IMAGE water filtration diagram --style=technical --format=svg
🤖 Generating image with Gemini Imagen...
✅ Created: knowledge/water/diagrams/filtration-technical.svg (12.3 KB)
📊 Quality score: 0.92
```

**Article Generation:**
```
uDOS> GENERATE ARTICLE "introduction to wilderness navigation" --template=tutorial
🤖 Generating article with Gemini...
✅ Created: knowledge/navigation/wilderness-intro.md (3,456 words)
📊 Sections: 7 | Examples: 5 | Citations: 12
```

**Prompt Refinement:**
```
uDOS> OK REFINE improve GENERATE GUIDE prompt for accuracy
🤖 Analyzing current prompt...
✅ Suggested improvements:
   - Add "cite sources" instruction
   - Specify "step-by-step format"
   - Include "safety warnings"
   - Add "metric + imperial units"
📋 Updated: core/knowledge/prompts/generate_guide_v2.txt
```

---

## 📚 Documentation Deliverables

### New Documentation (v1.5.0)
- [x] `dev/planning/DEV_MODE_GUIDE.md` - Master user setup, usage, restrictions
- [x] `dev/planning/CONFIG_SYNC_ISSUES.md` - Problem analysis and resolution
- [ ] `dev/docs/UCODE_V2_REFERENCE.md` - Complete syntax guide
- [ ] `wiki/Gemini-Integration.md` - AI features, prompts, examples
- [ ] `wiki/DEV-MODE.md` - User-facing DEV MODE guide
- [ ] `dev/planning/V1_5_0_MIGRATION.md` - Upgrade guide

### Updated Documentation
- [ ] `ROADMAP.MD` - v1.5.0-1.5.3 phases
- [ ] `README.MD` - v1.5.0 features
- [ ] `CHANGELOG.MD` - Detailed changes
- [ ] `wiki/Configuration.md` - ConfigManager usage
- [ ] `wiki/Command-Reference.md` - uCODE v2.0 commands

---

## 🔄 Migration Path (v1.4.0 → v1.5.0)

### For Users

**1. Backup Configuration**
```bash
cp memory/sandbox/user.json memory/sandbox/user.json.backup
```

**2. Update to v1.5.0**
```bash
git pull origin main
./start_udos.sh
```

**3. Configure .env (Auto-Created)**
```bash
# Edit .env file
nano .env

# Add Gemini API key:
GEMINI_API_KEY=your_actual_key_here
UDOS_USERNAME=YourName
```

**4. Setup Master User (Optional)**
```bash
./start_udos.sh --setup-master
# Enter secure password
```

**5. Verify Installation**
```
uDOS> CONFIG
# Check settings are correct

uDOS> DASH
# Verify user info matches

uDOS> OK ASK "test"
# Should connect to Gemini
```

### For Developers

**1. Update Code to ConfigManager**
```python
# OLD
user_json = json.load(open('memory/sandbox/user.json'))
username = user_json['username']

# NEW
from core.uDOS_main import config_manager
username = config_manager.get('username')
```

**2. Migrate to uCODE v2.0**
```python
# OLD .uscript syntax
GENERATE water/filtration technical 3

# NEW .uscript syntax
[GENERATE|category=water/filtration|style=technical|diagrams=3]
# OR
GENERATE GUIDE water/filtration --style=technical --diagrams=3
```

**3. Run Migration Script**
```bash
python core/scripts/migrate_v1_5_0.py
```

**4. Run Test Suite**
```bash
pytest -v
# 2,000+ tests should pass
```

---

## 🎯 Next Steps After v1.5.0

### v1.6.0 - Content Population & Community (Q3-Q4 2026)

**Mass Content Generation:**
- Generate 1,000+ survival guides with refined v1.5.2 tools
- Convert 100+ external resources
- Create 500+ diagrams (ASCII, Teletext, SVG)

**Community Features:**
- Real-time collaborative editing
- Group missions with live coordination
- Community knowledge voting/curation
- Peer-to-peer guide sharing

**Plugin Ecosystem:**
- Extension API for third-party developers
- Plugin marketplace with ratings/reviews
- Sandboxed plugin execution
- Hot-reload plugin system

---

## 📊 Resource Requirements

### Development Time
- **Total:** 12 weeks (3 months)
- **v1.5.1:** 4 weeks (uCODE refinement)
- **v1.5.2:** 4 weeks (content generation)
- **v1.5.3:** 4 weeks (config sync + polish)

### Team Size
- **Core Developer:** 1 (full-time)
- **Beta Testers:** 10-20 (community)
- **Documentation:** 1 (part-time)

### Infrastructure
- **Gemini API:** Production access (paid tier)
- **CI/CD:** GitHub Actions (existing)
- **Testing:** Local + cloud runners

---

## 🚨 Risks & Mitigation

### Risk 1: Gemini API Rate Limits
**Impact:** High | **Probability:** Medium
**Mitigation:**
- Implement request caching
- Add rate limit handling (retry with backoff)
- Provide local LLM fallback (Llama, Mistral)

### Risk 2: Configuration Migration Issues
**Impact:** High | **Probability:** Low
**Mitigation:**
- Comprehensive migration script with rollback
- Backup configuration before migration
- Extensive testing on multiple setups

### Risk 3: DEV MODE Security Vulnerabilities
**Impact:** Critical | **Probability:** Low
**Mitigation:**
- Security audit of DEV MODE code
- Strict password requirements
- Activity logging and monitoring
- Disable by default

### Risk 4: Breaking Changes in uCODE v2.0
**Impact:** Medium | **Probability:** Low
**Mitigation:**
- Maintain backward compatibility with v1.0
- Provide migration guide for scripts
- Auto-convert old syntax to new

---

## ✅ Definition of Done

### v1.5.1 Complete When:
- ✅ Shortcode parser validates 100% of test cases
- ✅ All 50+ commands in unified registry
- ✅ 3 production .uscript examples working
- ✅ Command compatibility layer passes all tests
- ✅ REPL operational for interactive testing

### v1.5.2 Complete When:
- ✅ Image generation produces valid SVG/PNG/ASCII diagrams
- ✅ Article generation creates properly formatted markdown
- ✅ 50+ enhanced prompts documented
- ✅ REFRESH/REDO updates content without breaking
- ✅ All OK commands work in TUI with Gemini

### v1.5.3 Complete When:
- ✅ .env file auto-created on first run
- ✅ CONFIG changes persist across restarts
- ✅ DASH shows correct user information
- ✅ Gemini API connects successfully
- ✅ DEV MODE secure and fully functional
- ✅ 2,000+ tests passing (100% pass rate)
- ✅ All documentation updated

---

**Status:** 📋 Planned | Ready for v1.4.0 completion
**Next Milestone:** v1.4.0 beta launch (before starting v1.5.0)
**Target Start:** After v1.4.0 beta feedback cycle (Q2 2026)
