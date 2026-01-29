# Release Readiness Checklist

**Document:** uDOS v1.1.0 Public Stable Release  
**Date Created:** 2026-01-29  
**Target Release:** Q1 2026 (Post-Beacon-Portal integration)  
**Status:** Planning Phase

---

## Overview

This checklist defines concrete pass/fail gates for releasing uDOS to public stable (v1.1.0+). All gates must be **PASS** before release. Use the **Status** column to track real-time progress.

---

## 🎯 Core Release Gates

### A. Test Coverage & Quality (BLOCKING)

| Gate                   | Requirement                                | Current Status                      | Pass/Fail    | Target Date |
| ---------------------- | ------------------------------------------ | ----------------------------------- | ------------ | ----------- |
| **TypeScript Tests**   | Core story parser: 9/9 passing (100%)      | 8/9 passing (89%)                   | 🟡 NEEDS FIX | 2026-02-05  |
| **Jest Types**         | `@types/jest` installed and visible to IDE | Missing, causing 44 IDE errors      | 🔴 FAIL      | 2026-02-01  |
| **Unit Test Coverage** | Core: ≥80%, Wizard: ≥75%, Extensions: ≥70% | Not measured                        | ❓ TBD       | 2026-02-15  |
| **Integration Tests**  | Core+Wizard+App integration tests          | Partial (Goblin→Wizard tests exist) | 🟡 PARTIAL   | 2026-02-20  |
| **Shakedown Suite**    | 47/47 core system validation tests passing | Status unknown                      | ❓ VERIFY    | 2026-02-05  |

**Action Items:**

- [ ] Install `@types/jest` in core runtime (2 min)
- [ ] Fix multi-section story parser test (15 min)
- [ ] Measure and report coverage metrics (2 hours)
- [ ] Add missing integration test suites (4 hours)
- [ ] Run and verify Shakedown suite (1 hour)

---

### B. Documentation Completeness (BLOCKING)

| Gate                      | Requirement                                                    | Current Status                                | Pass/Fail  | Target Date |
| ------------------------- | -------------------------------------------------------------- | --------------------------------------------- | ---------- | ----------- |
| **Engineering Spine**     | AGENTS.md, README.md, development-streams.md updated           | ✅ Current as of 2026-01-28                   | 🟢 PASS    | —           |
| **Component Docs**        | Core, Wizard, App, Extensions have current docs                | ✅ All present in respective folders          | 🟢 PASS    | —           |
| **Specification Docs**    | TypeScript Runtime, Grid, File Parsing, Workflow specs present | ✅ All in /docs/specs/                        | 🟢 PASS    | —           |
| **Example Code**          | Complete example scripts, databases, grid examples             | ✅ All in /docs/examples/                     | 🟢 PASS    | —           |
| **CHANGELOG**             | Comprehensive entry for v1.1.0 release notes                   | 🔴 NOT STARTED                                | 🔴 FAIL    | 2026-02-28  |
| **API Documentation**     | All `/api/v1/*` endpoints documented with examples             | Partial (Wizard documented, Goblin has stubs) | 🟡 PARTIAL | 2026-02-20  |
| **Version Documentation** | All components at stable versions, no dev versions             | ✅ All 3-digit format (v1.0.x or v0.x.x)      | 🟢 PASS    | —           |

**Action Items:**

- [ ] Create comprehensive CHANGELOG for v1.1.0 (2 hours)
- [ ] Complete API documentation for all Wizard endpoints (3 hours)
- [ ] Review and update all component READMEs (2 hours)

---

### C. Feature Completeness (BLOCKING for "Core" designation)

| Gate               | Component  | Feature                                            | Status                 | Pass/Fail         | Blocker                |
| ------------------ | ---------- | -------------------------------------------------- | ---------------------- | ----------------- | ---------------------- |
| **Core Runtime**   | Core       | TypeScript Markdown Runtime                        | ~85%                   | 🟡 PARTIAL        | Grid viewport renderer |
| **Grid System**    | Core       | Viewport rendering + sprites                       | ~40%                   | 🔴 NOT READY      | Large feature gap      |
| **File Parsing**   | Core       | CSV/JSON/YAML/SQL parsing                          | ~30%                   | 🔴 NOT READY      | Not implemented        |
| **Binder**         | Core       | Compilation + output formats                       | ✅                     | 🟢 PASS           | —                      |
| **Wizard Server**  | Wizard     | Production service layer                           | ✅ v1.1.0              | 🟢 PASS           | —                      |
| **OAuth**          | Wizard     | OAuth provider integration                         | Planned (Phase 6A)     | 🟡 PLANNED        | Scheduled for Feb      |
| **Beacon Portal**  | Wizard     | WiFi infrastructure + device quotas                | ~95% (design complete) | 🟡 READY FOR IMPL | Integration pending    |
| **Notion Handler** | Wizard     | Notion integration stubs                           | 0% (11 TODOs)          | 🔴 NOT STARTED    | Not blocking v1.1.0    |
| **App**            | App        | Tauri+Svelte foundation                            | ✅ v1.0.6+             | 🟢 PASS           | —                      |
| **Transport**      | Extensions | Private transport layer (Mesh, BT, QR, Audio, NFC) | ✅ v1.0.1              | 🟢 PASS           | —                      |

**Critical Blockers for v1.1.0:**

- ❌ Grid viewport renderer (Can defer to v1.1.1)
- ❌ File parsing system (Can defer to v1.1.1)
- ✅ Core runtime state/set/form/nav/panel (Ready)
- ✅ Binder compilation (Ready)
- ✅ Wizard production services (Ready)
- ✅ App foundation (Ready)

**Release Decision:** v1.1.0 is viable if Grid/File parsing deferred to v1.1.1.

---

### D. Performance & Scalability (REQUIRED)

| Gate                 | Requirement                          | Current Status  | Pass/Fail | Target Date |
| -------------------- | ------------------------------------ | --------------- | --------- | ----------- |
| **Core Startup**     | TUI launches in <3 seconds on Alpine | Not benchmarked | ❓ TBD    | 2026-02-10  |
| **Wizard Server**    | Responds to 100 req/sec sustained    | Not load tested | ❓ TBD    | 2026-02-15  |
| **App Launch**       | Tauri window opens in <2 seconds     | Not benchmarked | ❓ TBD    | 2026-02-10  |
| **Database Queries** | Local SQLite queries <100ms (p95)    | Not profiled    | ❓ TBD    | 2026-02-15  |
| **Memory Usage**     | Core <50MB resident, Wizard <200MB   | Not measured    | ❓ TBD    | 2026-02-10  |

**Action Items:**

- [ ] Benchmark core TUI startup (1 hour)
- [ ] Load test Wizard Server (2 hours)
- [ ] Profile database query performance (2 hours)
- [ ] Measure memory footprint on Alpine (1 hour)
- [ ] Document findings + optimization opportunities (1 hour)

---

### E. Security & Privacy (CRITICAL)

| Gate                          | Requirement                                        | Current Status                       | Pass/Fail     | Target Date  |
| ----------------------------- | -------------------------------------------------- | ------------------------------------ | ------------- | ------------ |
| **Transport Policy Enforced** | Policy validator prevents data on Bluetooth Public | Implemented in extensions/transport/ | 🟢 PASS       | —            |
| **API Authentication**        | All `/api/v1/*` require bearer token               | Implemented in Wizard                | 🟢 PASS       | —            |
| **Secrets Management**        | No secrets hardcoded; config files gitignored      | Verified in recent audit             | 🟢 PASS       | —            |
| **HTTPS Required**            | Wizard production enforces TLS                     | Not tested (dev uses localhost)      | 🟡 NEEDS TEST | 2026-02-20   |
| **Rate Limiting**             | API rate limits enforced per device                | Implemented                          | 🟢 PASS       | —            |
| **Cost Tracking**             | Wizard tracks cloud API costs per device           | Implemented                          | 🟢 PASS       | —            |
| **Security Audit**            | Third-party security review                        | Not conducted                        | 🔴 OPTIONAL   | Post-release |

**Action Items:**

- [ ] Test HTTPS enforcement in production config (1 hour)
- [ ] Verify secrets are not in git history (1 hour)
- [ ] Conduct internal security review checklist (2 hours)
- [ ] Plan post-release external security audit (Optional)

---

### F. Platform Compatibility (REQUIRED)

| Platform         | Requirement                              | Status                      | Pass/Fail       |
| ---------------- | ---------------------------------------- | --------------------------- | --------------- |
| **Alpine Linux** | Core TUI boots and runs on Alpine 3.18+  | Not tested on actual Alpine | 🟡 NEEDS TEST   |
| **macOS**        | App runs on macOS 10.13+ (native)        | ✅ Tauri builds for macOS   | 🟢 PASS         |
| **Ubuntu/Linux** | Core runs on Ubuntu 20.04+               | Not specifically tested     | 🟡 LIKELY WORKS |
| **Windows**      | Core runs on WSL2 (Python 3.10+)         | Not tested                  | ❓ TBD          |
| **iOS/iPadOS**   | Future: App roadmap includes iOS support | Planned for v1.1.0+         | 🟡 DEFERRED     |

**Action Items:**

- [ ] Test Core on actual Alpine Linux container (2 hours)
- [ ] Test Core on Ubuntu 20.04/22.04 (1 hour)
- [ ] Verify WSL2 compatibility (1 hour)
- [ ] Document platform-specific issues and workarounds (1 hour)

---

### G. Dependency Stability (REQUIRED)

| Dependency | Component    | Version | Lock Status          | Risk   |
| ---------- | ------------ | ------- | -------------------- | ------ |
| Node.js    | Core, App    | 18.0+   | ✅ package-lock.json | 🟢 LOW |
| TypeScript | Core, App    | 5.3+    | ✅ package.json      | 🟢 LOW |
| Python     | Wizard, Core | 3.10+   | ✅ requirements.txt  | 🟢 LOW |
| FastAPI    | Wizard       | 0.104+  | ✅ pinned            | 🟢 LOW |
| Tauri      | App          | 2.x     | ✅ Cargo.lock        | 🟢 LOW |
| Svelte     | App          | 5.x     | ✅ package.json      | 🟢 LOW |

**Action Items:**

- [ ] Verify all package managers use lock files (30 min)
- [ ] Document minimum version requirements (30 min)
- [ ] Check for deprecated dependencies (1 hour)

---

## 🚦 Release Decision Framework

### Tier 1: MUST PASS (Release Blockers)

Gates that **must be PASS** before v1.1.0 can be released:

- ✅ **A1: TypeScript tests 9/9 passing** → Fix @types/jest + parser (17 min work)
- ✅ **B1: Engineering docs current** → Already PASS
- ✅ **E1: Transport policy enforced** → Already PASS
- ✅ **E2: API authentication required** → Already PASS
- ✅ **F1: Alpine Linux compatibility** → Needs 2-hour test

**Blocking Work:** ~3 hours total

---

### Tier 2: SHOULD PASS (Quality Gates)

Gates that are **highly recommended but can be deferred to v1.1.1**:

- 🟡 **A2: Test coverage ≥80%** → Measurement + optimization (~6 hours)
- 🟡 **B2: API documentation complete** → Full documentation (~3 hours)
- 🟡 **C2: Grid viewport renderer** → Large feature (~20+ hours) → **Defer to v1.1.1**
- 🟡 **C3: File parsing system** → Large feature (~15+ hours) → **Defer to v1.1.1**
- 🟡 **D: Performance benchmarks** → All profiling (~8 hours)

**Deferrable Work:** Could delay release by 2+ weeks if required.

---

### Tier 3: NICE-TO-HAVE (Polish)

Gates that can be deferred post-release:

- 🟠 **B3: CHANGELOG entry** → 2 hours (can be written after release)
- 🟠 **C4: Notion handler implementation** → Large feature (~6 hours)
- 🟠 **E3: External security audit** → Post-release
- 🟠 **Goblin→Wizard migration** → Scheduled for Phase 6

---

## 📋 Release Timeline

### Phase 1: Critical Fixes (Target: 2026-02-05)

- [ ] Install @types/jest in core
- [ ] Fix multi-section story parser test
- [ ] Test Alpine Linux compatibility
- [ ] Verify Shakedown suite (47 tests)

**Gate Status:** Target = PASS

---

### Phase 2: Quality Baseline (Target: 2026-02-20)

- [ ] Measure test coverage across components
- [ ] Complete API documentation
- [ ] Benchmark performance metrics
- [ ] Internal security review

**Gate Status:** Target = PASS or DEFER

---

### Phase 3: Final Integration (Target: 2026-02-28)

- [ ] Integration tests all passing
- [ ] Platform compatibility verified (Alpine, Ubuntu, macOS)
- [ ] CHANGELOG written
- [ ] Release notes published

**Gate Status:** Target = READY FOR RELEASE

---

### Release Decision Point: 2026-02-28

**If all Tier 1 gates are PASS:**

- ✅ Release v1.1.0 as **Public Stable**
- 📝 Publish official release notes
- 🏷️ Create git tags across all repositories

**If Tier 1 gates are not PASS:**

- 🔄 Extend timeline (push to 2026-03-15)
- 📌 Identify critical blockers
- 🔧 Focus on unblocking issues

**If Tier 2 gates are not PASS:**

- ✅ Can still release as v1.1.0
- 🎯 Document deferred work for v1.1.1
- 📅 Schedule Phase 2 work for 2-3 weeks post-release

---

## 🔄 Governance

### Weekly Review (Every Monday)

- Update status of all gates (PASS/FAIL/PARTIAL)
- Flag any blockers immediately
- Adjust timeline if needed

### Responsible Parties

- **Core Runtime:** fredporter (TypeScript, story parser)
- **Wizard Server:** fredporter (OAuth, Beacon Portal)
- **App:** fredporter (Tauri, Svelte)
- **Testing:** fredporter (test coverage, benchmarks)
- **Docs:** fredporter (CHANGELOG, API docs)

### Communication

- Update this checklist **before** each public communication
- Tag releases with git (e.g., `v1.1.0-rc1`, `v1.1.0`)
- Publish release notes to README + GitHub releases

---

## 📊 Status Dashboard

### Current State (2026-01-29)

**Tier 1 (Blockers):**

- ✅ Transport policy: PASS
- ✅ API authentication: PASS
- ✅ Engineering docs: PASS
- 🟡 TypeScript tests: 89% (1 test failing)
- 🟡 Alpine testing: NOT YET TESTED

**Status:** 3/5 PASS, 2/5 PENDING

**Estimated Release Date:** 2026-02-28 (if no major blockers)

---

## 📚 References

- [OUTSTANDING-TASKS.md](OUTSTANDING-TASKS.md) — Input for this checklist
- [development-streams.md](development-streams.md) — Feature roadmap
- [AGENTS.md](../AGENTS.md) — Release policies
- [README.md](README.md) — Update with release status

---

**Last Updated:** 2026-01-29 (Created)  
**Next Review:** 2026-02-05 (Phase 1 deadline)  
**Status:** Active Planning Document
