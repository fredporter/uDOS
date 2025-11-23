# 🗺️ uDOS v1.1.x Roadmap

**Scope:** This roadmap covers **v1.1.0 and later** (security, dual-interface TUI/GUI, adventure systems, economy, and native apps).
Pre–1.1.0 work (v1.0.3–1.0.33) is considered the **foundation** and is referenced where relevant but tracked elsewhere.

---

## 🌍 Context & Status

- **Current Stable Core:** v1.0.32 – Planet System & World Maps (COMPLETE, all tests passing).
- **Immediate Pre-1.1 Work:** v1.0.33 – Community Features & Barter System (NEXT)
  - Community commands: `COMMUNITY CREATE/JOIN/SHARE`, location-aware discovery.
  - Barter commands: `OFFER / REQUEST / TRADE / REPUTATION`.
  - Location-aware and climate-aware survival knowledge, seasonal tips, and local resource identification.

> **Rule of thumb:** v1.0.x finishes **core survival, mapping, and community groundwork**.
> v1.1.x focuses on **security, dual interface, adventure/economy, and native apps**.

---

## 🛠️ v1.1.0 – Core TUI Stabilisation & Dual-Interface Foundation (Q2 2026)

***Focus: Deliver a robust, cross-compatible terminal experience, finalise AI assistant roles, and enable the Web GUI as a parallel interface.***

> **Development Workflow:** All v1.1.0+ development uses **local-first iteration** with live user testing in the TUI. Session logs capture real-world usage patterns, errors, and edge cases. Gemini API integration provides in-session debugging and intelligent error handling. Git operations managed via VSCode/Copilot for efficient version control.

### Phase 0: AI Assistant Logic & Role Security ✅ **COMPLETE (2025-11-24)**

This phase enforces the **security model around external AI access** and connects the 4-Tier Knowledge Bank to assistant behaviour.

**Status**: All features implemented and tested. 79/79 tests passing (100%).

| ID | Feature | Status | Implementation |
| :--- | :--- | :--- | :--- |
| **1.1.0.1** | **AI Access Control (Gemini API)** | ✅ COMPLETE | Role-based access implemented in `assistant_handler.py`. Wizard: unrestricted; User: restricted offline-first. `_check_api_access()` enforces permissions. |
| **1.1.0.2** | **Offline-First Query Fallback** | ✅ COMPLETE | User role searches 4-Tier Knowledge Bank first via `_search_local_knowledge()`. Gemini API only called if no local answer found. |
| **1.1.0.3** | **Wizard Dev-Mode Enablement** | ✅ COMPLETE | `OK DEV` restricted to Wizard role. Full system context injection via `_gather_dev_context()`. |
| **1.1.0.4** | **API Use Audit Logging** | ✅ COMPLETE | `core/services/api_audit.py` logs all API calls to `memory/logs/audit.log` with role, tokens, cost, duration. 13/13 tests passing. |
| **1.1.0.5** | **Live Session Debug System** | ✅ COMPLETE | `core/services/session_analytics.py` captures command traces, errors, performance metrics to `memory/sessions/auto/`. Structured JSON logs enable session replay. 14/14 tests passing. |
| **1.1.0.6** | **Interactive Error Handler** | ✅ COMPLETE | `core/services/intelligent_error_handler.py` classifies errors, provides contextual solutions, logs patterns. 7 error types with severity/fixes. 19/19 tests passing. |
| **1.1.0.7** | **User Testing Feedback Loop** | ✅ COMPLETE | `FEEDBACK` and `REPORT` commands implemented via `core/commands/user_handler.py`. Persists to `memory/logs/feedback/` with session integration. 23/23 tests passing. |

**Deliverables**:
- `core/services/session_analytics.py` - Session logging with CommandTrace, ErrorEntry, FeedbackEntry
- `core/services/api_audit.py` - API call audit with role-based tracking
- `core/services/intelligent_error_handler.py` - AI-powered error classification
- `core/commands/feedback_handler.py` - User feedback capture system
- `core/commands/user_handler.py` - FEEDBACK/REPORT command routing
- Enhanced `assistant_handler.py` - Role-based API access control
- 4 comprehensive test suites (79 tests total)

**Development Session**: Documented in `memory/sessions/dev/round_20251123_150741.md`

---

### Phase 1: TUI Reliability & Input System (Critical Fixes) 💻

> **Testing Protocol:** Each feature undergoes live user testing in the TUI with session logging enabled. VSCode/Copilot handles all git commits, branches, and PR management. Gemini API provides real-time code review and compatibility checking across terminal types.

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.0.8** | **TUI Selector Refactor (CRITICAL)** | Rebuild `OptionSelector` and `FilePicker` using **`prompt_toolkit`** (or equivalent) so arrow-key navigation, multi-select, and file preview work on **macOS Terminal, Linux terminals, and Windows Terminal/PowerShell**. This replaces the older smart input constraints defined in v1.0.29/1.0.30. Live testing on all 3 platforms required. |
| **1.1.0.9** | **Fallback I/O (Degraded Terminals)** | Implement a simple **numbered menu fallback** for all interactive prompts (`ask_choice()` and similar). Behaviour must be fully functional over minimal TTYs (no colours, no cursor movement), preserving all workflows. Test with SSH sessions, screen readers, and constrained environments. |
| **1.1.0.10** | **Retro Graphics & Compatibility (v1.0.30)** | Finalise Unicode/ANSI block character sets and colour schemes to deliver a stable retro aesthetic (C64/ZX/Apple II vibes) without breaking compatibility on constrained or remote terminals. Includes splash screen, loaders, and progress bars. Compatibility matrix testing across terminal emulators. |
| **1.1.0.11** | **Unified Commands Testing** | Fully test and finalise **DOCS**, **LEARN**, and **MEMORY** unified handlers so that zero-argument usage behaves intuitively and allows smart prompts rather than failure. Confirm compatibility with v1.0.x smart input work. Live user sessions validate UX flow. |
| **1.1.0.12** | **Session Replay & Analysis** | Implement session replay tools for developers: replay command sequences from session logs, step through user interactions, and identify pain points. Gemini API analyzes session patterns to suggest UX improvements and detect common error paths. |

---

### Phase 2: Web Extension Activation & Delegation (Smart I/O) 🌐

This phase brings the **Teletext Web GUI** up to parity with the native CLI for complex visual tasks, but keeps everything offline-first.

> **Integration Testing:** Dual-interface testing with synchronized session logs across CLI and Web GUI. Gemini API assists with cross-platform compatibility checks and automated regression testing.

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.0.9** | **Teletext Display System (GUI)** | Implement the Web GUI **Dashboard View** and enhanced command output as the **primary target for highly visual I/O** (maps, grids, inventories, dashboards). Backed by the embedded offline web server and existing `/api/command` endpoints. |
| **1.1.0.10** | **Delegate Complex Selectors to Web** | For complex or highly visual inputs (`select_map_cell()`, multi-file picker, skill trees, inventories), allow the CLI to open a Web GUI modal and wait for a result via WebSocket/REST. CLIs stay authoritative; GUI is an optional enhancement layer. |
| **1.1.0.11** | **POKE Command Stabilisation (v1.0.5/v1.0.11)** | Finalise and test `POKE LIST/STATUS/START/STOP` to reliably manage the embedded Teletext Web Server (start, stop, status check, and error handling). Confirm robustness on macOS, Linux, and Windows. |
| **1.1.0.12** | **TUI/GUI State Synchronisation** | Ensure state such as **command history, current mission/scenario, active planet/tile, memory tier, current project** is consistent between CLI and Teletext Web GUI. Includes conflict resolution rules and “last writer wins” semantics where required. |

---

### Phase 3: Core System & Documentation Readiness 🗺️

> **Development Methodology:** Local-first iterative development. All changes tested in live TUI sessions before commit. Session logs and error patterns inform documentation. VSCode/Copilot manages git workflow (branching, commits, PRs). Gemini API validates documentation accuracy and completeness.

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.0.18** | **Data Architecture Finalisation (v1.0.20b)** | Enforce strict separation between `/data/system/` (immutable reference) and `/memory/` (user-writable). All scripts, commands, and AI tooling must respect this boundary. Session logs validate boundary enforcement during live testing. |
| **1.1.0.19** | **TIZO & Map Core Integration (v1.0.20b/v1.0.33)** | Ensure all essential map commands (`MAP`, `GOTO`, `LOCATE`, `MAP VIEW`, `MAP STATUS`) use the alphanumeric TILE/TZONE system. Confirm compatibility with Planet/Workspace concepts from v1.0.32+. Live user testing confirms intuitive navigation. |
| **1.1.0.20** | **RUN Automation & Templates (v1.0.6)** | Validate and finalise the `.uscript` `RUN` command and core project templates so that changes to TUI/CLI behaviour do not break scripting. Include test coverage for adventure/story templates, research workflows, and survival scenarios. Session replay validates script reliability. |
| **1.1.0.21** | **Core Documentation Handbook (v1.0.22)** | Complete the **offline handbook** (target 1000+ pages) with ASCII/Teletext diagrams that reflect the **stabilised TUI and dual-interface architecture**, including RBAC/AI usage, map system, survival missions, and barter workflows. Documentation generated from live session examples and AI-validated for accuracy. |
| **1.1.0.22** | **Git Workflow Integration** | Standardize development workflow using VSCode/Copilot for all git operations: feature branches, commit messages, PR creation, and merge management. Session logs and error reports automatically tagged to relevant commits for traceability. |

---

## 🛡️ v1.1.1 – Security Model & Offline Knowledge (Q3 2026)

***Focus: Enforce security, establish user roles, and finalise the complete offline knowledge repository.***

> **Quality Assurance:** Security features undergo extensive penetration testing via session logging. All role transitions and permission checks logged. Gemini API assists with security audit and vulnerability analysis. VSCode/Copilot manages security-focused branches with mandatory review.

### Phase 1: Advanced Security & Roles

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.1.1** | **User Role System (RBAC)** | Define and implement **User, Power, Wizard, Root** roles. All core functionality routes through RBAC checks, including command execution, file access, and AI/web features. Roles must be inspectable and adjustable via config/commands (with proper protection). |
| **1.1.1.2** | **Command-Based Security Hardening** | Move the detailed “Command-Based Security Model” into enforced code: explicit `API/OK/ASSIST` calls for Gemini; `WEB/FETCH/CRAWL` for web access; `OFFLINE/PROMPT` for local prompt development. No implicit API/web calls. All rules are centralised in a security layer, not spread across commands. |
| **1.1.1.3** | **4-Tier Memory System Finalisation (v1.0.20)** | Fully implement **Tier 1: Private (Encrypted)** with secure key management; finalise Tiers 2–4 for shared/group/public knowledge. AI and commands must respect tier boundaries and visibility rules. |
| **1.1.1.4** | **Installation Types & Integrity** | Implement **Clone / Spawn / Hybrid** installation detection and lock-down rules. Production installs must protect `core/` and `extensions/core/` as read-only; sandboxed development installs may relax these constraints under Wizard/Root roles. |

---

### Phase 2: Knowledge Bank & AI Integration

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.1.6** | **Offline Knowledge Library (Tier 4)** | Complete the offline survival library: target **500+ survival guides** and **100+ reference diagrams**, organised under the 4-Tier Memory model. Indexing must integrate with `DOCS/LEARN/MEMORY` and the AI offline-first flow. Live user sessions validate search accuracy and relevance. |
| **1.1.1.7** | **Offline AI Prompt Development** | Implement `OFFLINE/PROMPT/TEST` and related commands to allow fully local prompt template editing, validation, and dry-run testing without external API calls. Store prompts in a structured, versioned format. Session logs capture prompt development iterations and success rates. |
| **1.1.1.8** | **SVG/Citation Pipeline Integration** | Finalise the full document processing pipeline: ingesting PDFs/Word/HTML, generating distilled markdown guides, SVG diagrams, and enforcing a **citation mandate**. All ingested or generated content must include source tags, IDs, and bibliographies, ready for offline use. Pipeline errors logged for troubleshooting. |
| **1.1.1.9** | **Knowledge Validation System** | Build validation tools to verify knowledge base integrity: broken links, missing citations, outdated content. Gemini API assists with content quality assessment and suggests improvements. Session logs track validation runs and fix applications. |

---

## 🎮 v1.1.2 – Adventure & Economy Systems (Q4 2026)

***Focus: Integrate application-level logic for survival, gameplay, barter, and community interaction, building on v1.0.33 groundwork.***

> **Gameplay Testing:** Extensive live playtesting with session replay analysis. Player behavior patterns inform game balance adjustments. Gemini API provides narrative generation and dynamic quest creation. VSCode/Copilot manages game content branches.

### Phase 1: Gamified Survival & Progression

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.2.1** | **XP & Achievement System (v1.0.18)** | Implement the Experience Point (XP) and achievement system, tracking competence through **Usage, Information, and Contribution**. Replaces ad-hoc counters; feeds into missions, skill trees, and community reputation. Session logs track XP gain patterns and achievement unlocks for balance tuning. |
| **1.1.2.2** | **Apocalypse Adventure Framework** | Finalise the `SCENARIO` command and NetHack-style map gameplay built on the existing map engine: interactive scenario playback, resource tracking/inventory, survival mode (health/hunger/stamina), environment threats, and mission outcomes. Live playtesting sessions inform difficulty curves and narrative pacing. |
| **1.1.2.3** | **Interactive Skill Trees (v1.0.21)** | Implement ASCII skill tree diagrams and progression for survival, technical, and community skills. Integrate with XP system and display both in CLI (retro graphics) and optional Teletext GUI modes. Player progression paths logged to optimize tree structure. |
| **1.1.2.4** | **Adaptive Difficulty & AI Storytelling** | Integrate Gemini API to generate dynamic missions, narrative events, and challenges based on player skill level and session history. System learns from player behavior to create personalized experiences. All generated content logged for quality review. |

---

### Phase 2: Community & Barter Systems

Building directly on the v1.0.33 work (community and barter commands).

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.2.5** | **Barter System (v1.0.33)** | Ship a fully functional **zero-currency economy** using `OFFER`, `REQUEST`, `TRADE`, and `REPUTATION`. Integrate with XP and mission systems. Must support offline matching between **What I Have** and **What I Need** across local communities. Trade patterns logged to analyze economy balance and prevent exploits. |
| **1.1.2.6** | **Community Integration (Tier 3)** | Finalise Tier 3 (Group/Community) knowledge: `COMMUNITY CREATE/JOIN/SHARE`, location-aware discovery (via `LOCATE`/TIZO), and controlled sharing of knowledge/resources. Ensure RBAC and privacy rules from v1.1.1 apply cleanly. Community interactions logged for moderation and health metrics. |
| **1.1.2.7** | **What I Have vs What I Need Engine** | Implement an analysis engine that compares user skills/resources vs mission/project needs, generating suggestions for barter partners, learning paths, or missions. Surface outputs in both CLI and Teletext Dashboard. Gemini API enhances matching intelligence and recommendation quality. |
| **1.1.2.8** | **Economy Analytics Dashboard** | Build analytics tools for tracking barter economy health: trade volume, resource scarcity, reputation distribution, and fairness metrics. Wizard role can access detailed session logs showing economic patterns and potential issues. |

---

## 🚀 v1.1.3+ – Advanced & Native Features (Future)

***Focus: Native apps, device spawning, and mesh networking once the core and security model are solid.***

> **Cross-Platform Development:** Native app development with continuous integration testing. Session logs synchronize across devices for unified debugging. Gemini API assists with platform-specific optimization and compatibility. VSCode/Copilot manages multi-platform branches and releases.

| ID | Feature | Rationale / Success Criteria |
| :--- | :--- | :--- |
| **1.1.3.1** | **Tauri Desktop App (v1.1.1)** | Ship a cross-platform desktop app (Tauri) that embeds the CLI/Teletext experience with better OS integration (launchers, notifications, file associations). Must remain offline-first and respect the security model from v1.1.1. Cross-platform testing with unified session logs across macOS, Windows, Linux. |
| **1.1.3.2** | **Device Spawning & Mesh Networking (v1.1.3)** | Implement master → child device spawning for laptops/desktops to create simplified, offline-first mobile instances. Add encrypted P2P mesh networking for sync and community features that do not rely on corporate networks. Session logs synchronize across mesh for distributed debugging. |
| **1.1.3.3** | **Mobile Apps (iOS & Android) (v1.1.6)** | Native, touch-optimised mobile applications acting as **field/companion devices**. Feature set is a curated subset of uDOS, focused on missions, maps, survival guides, barter, and messaging over mesh networks. Mobile session logs sync to desktop for unified user journey analysis. |
| **1.1.3.4** | **Continuous Integration Pipeline** | Implement automated CI/CD for all platforms: automated testing, build verification, and deployment. Session log analysis feeds into automated regression detection. Gemini API assists with test case generation and failure analysis. VSCode/Copilot manages release branches and changelogs. |

---

## ✅ Implementation Notes

### Development Workflow (v1.1.0+)

All v1.1.x development follows a **local-first, user-testing-driven methodology**:

1. **Live TUI Testing:** Every feature tested in real TUI sessions before commit. Session logs (`MEMORY/sessions/`) capture user interactions, errors, and performance metrics.

2. **Session Log Analysis:** Developers use session replay tools to identify UX friction, error patterns, and edge cases. Gemini API assists with pattern recognition and automated issue classification.

3. **Error Handling Integration:** Interactive error handler provides contextual help during development and production. All errors logged with full context (command stack, system state, recent history) for debugging.

4. **Git Workflow via VSCode/Copilot:** All version control managed through VSCode with GitHub Copilot:
   - Feature branches created per roadmap item
   - Commit messages auto-generated with context
   - Pull requests include session log summaries
   - Automated linking of commits to error reports and feedback

5. **AI-Assisted Development:** Gemini API integration for:
   - Real-time code review and suggestions
   - Intelligent error diagnosis and fixes
   - Documentation generation from session examples
   - Cross-platform compatibility checking
   - Security vulnerability scanning

6. **Feedback Loop:** Users can invoke `FEEDBACK` or `REPORT` during any session. Feedback captured with full context and prioritized via session log analysis.

---

### Numbering Convention

- **Numbering Convention:**
  - `1.1.0.x` – TUI/Web core, AI wiring, session logging, and docs.
  - `1.1.1.x` – Security, RBAC, memory tiers, and knowledge bank.
  - `1.1.2.x` – Gameplay, survival scenarios, community, and barter economy.
  - `1.1.3.x+` – Desktop apps, spawning, mesh networking, and mobile.

- **Dependency Highlights:**
  - Complete and stabilise **v1.0.33** community/barter features before 1.1.2 activation.
  - Finish **RBAC and command-based security** (1.1.1.1–1.1.1.5) before exposing advanced AI/web features in desktop/mobile apps.
  - Ensure **Teletext Web GUI** (1.1.0.13–1.1.0.17) is stable before Tauri and mobile work; it becomes the main GUI layer.
  - **Session logging system** (1.1.0.5–1.1.0.7) must be operational before major feature development begins; it underpins all testing and debugging workflows.
  - **Gemini API integration** (1.1.0.1–1.1.0.4) completed before advanced AI features in knowledge bank and gameplay systems.

- **Documentation Flow:**
  - Each phase should end with an update to the **offline handbook** and example `.uscript` workflows.
  - Security and AI features must include **clear user-facing docs** explaining limits, permissions, and privacy guarantees.
  - Documentation should include real-world examples extracted from session logs and user testing.
  - All error messages and help text AI-validated for clarity and usefulness.

- **Quality Assurance Protocol:**
  - **No feature ships without session log validation:** Every feature must have documented user testing sessions showing successful completion paths and error handling.
  - **Error patterns tracked:** Common errors and edge cases identified via session log analysis must have dedicated test coverage.
  - **Cross-platform verification:** TUI features tested on macOS Terminal, Linux terminals, and Windows Terminal/PowerShell before merge.
  - **Performance benchmarks:** Session logs used to establish performance baselines and detect regressions.

---

## 📊 Development Metrics & Tracking

**Session Log Metrics (captured per session):**
- Commands executed (frequency, duration, success/failure)
- Error occurrences (type, context, resolution path)
- User feedback and confusion points
- API calls (count, tokens, cost)
- Performance metrics (response times, resource usage)

**Git Integration Markers:**
- Each commit tagged with relevant session log IDs
- PRs include session replay summaries and user impact assessment
- Changelogs auto-generated from commit history and session patterns

**AI Usage Tracking:**
- API calls logged with purpose, role, and outcome
- Token usage monitored per feature and per user role
- Cost tracking and optimization recommendations
- Quality metrics for AI-generated content (accuracy, relevance, user acceptance)
