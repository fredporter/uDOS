# 🗺️ uDOS Development Roadmap

**Current Version:** v1.2.9 ✅ **COMPLETE** (Gmail Cloud Sync)
**Previous Versions:** v1.2.9 ✅ v1.2.8 ✅ v1.2.7 ✅ v1.2.6 ✅ v1.2.5 ✅ v1.2.11 ✅ v1.2.10 ✅ v1.2.4 ✅ v1.2.3 ✅ uPY v2.0.2 ✅
**Next Version:** v1.3.0 📋 **PLANNED** (Community Features & Sharing)
**Last Updated:** December 5, 2025
**Roadmap Size:** 2,100+ lines (comprehensive planning document with all future work)

**Recent Updates (Dec 5, 2025):**
- ✅ v1.2.9 - COMPLETE! (Gmail Cloud Sync, all 4 parts done, 4,429 lines delivered)
- ✅ Part 4: Commands & Integration - QUOTA, CONFIG, DOWNLOAD, TASKS commands (555 lines)
- ✅ Part 3: Email to Markdown conversion with auto-detection (1,123 lines)
- ✅ Part 2: Google Drive sync engine with conflict resolution (1,314 lines)
- ✅ Part 1: Gmail OAuth2 authentication with encrypted tokens (1,437 lines)
- ✅ Complete integration tests and wiki documentation (1,170 lines)
- ✅ uPY v2.0.2 - COMPLETE! (All 6 parts done, 4,945 lines delivered)
- ✅ Part 6: Documentation complete - Runtime architecture, language reference, migration guide (1,282 lines)
- ✅ Integration tests: 4 categories combining math, lists, and file I/O (all passing)
- ✅ FILE commands: READ, WRITE, EXISTS, DELETE, SIZE, LIST
- ✅ JSON commands: PARSE, STRINGIFY, READ, WRITE
- ✅ File I/O integration with lists and variables
- ✅ List literals: [item1, item2, item3] with parsing and variable support
- ✅ LIST commands: CREATE, APPEND, REMOVE, INSERT, GET, SET, SIZE, SLICE, CONTAINS, INDEX, CLEAR, JOIN, SPLIT
- ✅ Enhanced FOREACH with practical list iteration
- ✅ Comprehensive test suites (21 test categories, all passing)
- ✅ Math operations with PEMDAS (+, -, *, /, %, **, parentheses)
- ✅ Function definitions and calls (@function(args), FUNCTION/END FUNCTION)
- ✅ RETURN statements with early exit support
- ✅ v1.2.8 released - Incremental Updates & Connection Health (2,300+ lines delivered)
- ✅ v1.2.7 released - Chart.js & WebSocket Real-Time (1,800+ lines delivered)
- ✅ v1.2.6 released - Webhook Analytics & Event History (2,595 lines delivered)

> **Philosophy:** Development measured in STEPS and MOVES, not time. Work proceeds through organic pacing and cron patterns. Priorities shift based on immediate needs and strategic value.

---

## 📍 Latest Releases

### v1.2.9 (December 5, 2025) ✅ **COMPLETE**

**Gmail Cloud Sync** - Secure Gmail authentication, email import, and Google Drive synchronization for memory/shared content.

**Delivered:**
- **Part 1: OAuth2 Authentication (1,437 lines)**
  - gmail_auth.py (432 lines) - OAuth2 flow, token encryption with Fernet
  - gmail_service.py (460 lines) - Gmail API operations, email listing/sending
  - gmail_handler.py (545 lines) - LOGIN/LOGOUT/STATUS commands
  - test_gmail_auth.py (182 lines) - Authentication test suite

- **Part 2: Google Drive Sync Engine (1,314 lines)**
  - sync_engine.py (542 lines) - Bidirectional sync, MD5 checksums, change detection
  - sync_manager.py (307 lines) - Background threading, sync history (50 entries)
  - SYNC commands: NOW, STATUS, ENABLE, DISABLE, CHANGES, HISTORY
  - 4 conflict strategies: newest-wins (default), local-wins, cloud-wins, manual
  - test_sync_engine.py (182 lines) - Sync validation tests

- **Part 3: Email to Markdown Conversion (1,123 lines)**
  - email_parser.py (380 lines) - HTML/plain text parsing, task extraction
  - email_converter.py (408 lines) - Convert to notes/checklists/missions
  - IMPORT GMAIL command with --preview, --type, --limit options
  - Auto-detection: 3+ tasks=mission, 1-2 tasks=checklist, 0 tasks=note
  - test_email_conversion.py (335 lines) - Conversion test suite

- **Part 4: Commands & Integration (555 lines)**
  - QUOTA command (50 lines) - Drive quota monitoring with 15 MB limit
  - CONFIG command (118 lines) - Sync configuration management
  - EMAIL DOWNLOAD (56 lines) - Individual email conversion
  - EMAIL TASKS (73 lines) - Task extraction from emails
  - test_gmail_integration.py (348 lines) - Complete integration tests
  - Gmail-Cloud-Sync.md (822 lines) - Comprehensive wiki documentation

**Total: 4,429 lines delivered (3,607 code + 822 docs)**

**Commits:** `9c617494` (Part 1), `bca87fa8` (Part 2), `c0edf7cb` (Part 3), `0e889ee3` (Part 4)

**Key Features:**
- ✅ Gmail OAuth2 authentication with encrypted token storage
- ✅ Email import with auto-conversion to notes/checklists/missions
- ✅ Smart task extraction from email content (regex patterns)
- ✅ Google Drive bidirectional sync with conflict resolution
- ✅ 10 commands: LOGIN, LOGOUT, STATUS, EMAIL (4 subcommands), IMPORT, SYNC (6 subcommands), QUOTA, CONFIG
- ✅ Syncable directories: memory/missions, workflows, checklists, system/user, docs, drafts
- ✅ Gmail query syntax support (is:unread, from:, subject:, etc.)
- ✅ 15 MB recommended sync limit with quota monitoring
- ✅ Background sync with configurable interval (60-3600s)
- ✅ Complete test suites and comprehensive documentation

**Security:**
- OAuth2 (no password storage)
- Fernet encrypted tokens in .env
- App-data-only Drive access
- User controls all sync settings

**Wiki:** `wiki/Gmail-Cloud-Sync.md`

### uPY v2.0.2 (December 6, 2025) ✅ **COMPLETE**

**Custom Runtime Implementation** - Complete interpreter for v2.0.2 syntax with arithmetic, functions, lists, file I/O, and comprehensive documentation.

**Delivered:**
- New runtime engine (843 lines) - Custom interpreter with function support
- Math parser (343 lines) - Recursive descent, PEMDAS, variable support
- Function system (+265 lines) - Define, call, return, parameter binding
- List operations (+325 lines) - Literals, LIST commands, FOREACH integration
- File I/O module (+344 lines) - FileIO class with read/write/JSON operations
- Command parser improvements (+338 lines) - FILE/JSON commands, nested parentheses
- Test suites (1,411 lines) - Math (75), functions (150), lists (296), file I/O (380), integration (272), validation (238)
- Integration with uDOS_main.py (+20 lines) - CommandHandler, Grid, Parser integration
- **Documentation (1,282 lines):**
  - Runtime Architecture (450 lines) - Technical implementation guide
  - Language Reference (632 lines) - Complete syntax reference with examples
  - Migration Guide (200 lines) - v1.x to v2.0.2 conversion guide
- **Total: 4,945 lines delivered (100% complete)**

**Commits:** `c3c0b80d`, `d97444b5`, `e5d8e87d`, `90cf4ef7`, `9eeba72e`, `3b40569c`, `[documentation commits]`

**Key Features:**
- ✅ Variables: `{$var}` substitution, system vars (MISSION, WORKFLOW, SPRITE)
- ✅ Commands: `(COMMAND|params)` syntax with full CommandHandler integration
- ✅ Math: `+`, `-`, `*`, `/`, `%`, `**` (power), parentheses, PEMDAS
- ✅ Functions: `@function(args)`, `FUNCTION/END FUNCTION`, RETURN statements
- ✅ Lists: `[item1, item2]` literals, 13 LIST commands
- ✅ File I/O: FILE READ/WRITE/EXISTS/DELETE/SIZE/LIST
- ✅ JSON: PARSE/STRINGIFY/READ/WRITE
- ✅ Conditionals: Short `[IF]`, medium `[IF THEN ELSE]`, long `IF/ELSE IF/ELSE/END IF`
- ✅ Loops: WHILE/FOREACH with proper END markers
- ✅ Smart action splitting (nested parentheses support)
- ✅ 21 test categories ALL PASSING (math, functions, lists, file I/O, integration)
- ✅ 4 integration tests validating feature combinations
- ✅ Complete documentation: Architecture (450 lines), language reference (632 lines), migration guide (200 lines)

**Performance:**
- Direct interpretation (no transpilation overhead)
- <1ms per command execution
- Math parsing with recursive descent (fast!)
- Function calls with minimal overhead
- Zero Python syntax errors
- 100% v2.0.2 compatibility

**Remaining Work:**
- ✅ Part 1: Math Operations (COMPLETE - 393 lines)
- ✅ Part 2: Function Execution (COMPLETE - 265 lines)
- ✅ Part 3: Advanced List Operations (COMPLETE - 621 lines)
- ✅ Part 4: File I/O (COMPLETE - 724 lines)
- ✅ Part 5: Integration Testing (COMPLETE - 272 lines)
- ✅ Part 6: Complete Documentation (COMPLETE - 1,282 lines)

**All parts complete! uPY v2.0.2 ready for production.**

### v1.2.8 (December 5, 2025) ✅ **COMPLETE**

**Incremental Chart Updates & Connection Health** - Performance optimization with incremental data updates and real-time health monitoring.

**Delivered:**
- Chart data manager (373 lines) - Centralized dataset management
- Incremental update logic (+338 lines) - 10-90x performance improvement
- Event buffering system (320 lines) - Zero data loss during disconnection
- Reconnection replay (+188 lines) - Smart deduplication, visual feedback
- Latency measurement (+135 lines) - Ping/pong with rolling average
- Connection health dashboard (617 lines) - Uptime, rate, quality metrics
- Testing suite (628 lines) - Performance validation, load tests
- Complete documentation (734 lines) - Architecture, benchmarks, guides
- **Total: 2,333 lines delivered**

**Tags:** Tasks 1-9 complete
**Commits:** `a55bdbaa`, `a5892aab`, `1790aaaf`, `aa3dd4cb`

**Key Features:**
- ✅ Incremental chart updates (no full refresh)
- ✅ Event buffering during disconnection (max 100 events)
- ✅ Connection latency monitoring (ping/pong)
- ✅ Health dashboard (uptime, rate, quality)
- ✅ Toast notifications for buffer replay
- ✅ 90% reduction in API calls
- ✅ 70% reduction in DOM updates
- ✅ <1ms per event update vs ~80-280ms full refresh

### v1.2.7 (December 5, 2025) ✅ **COMPLETE**

**Chart.js Visualizations & WebSocket Real-Time Updates** - Professional interactive charts and instant event notifications via WebSocket broadcasting.

**Delivered (Phase 1 - Chart.js Integration):**
- Chart utilities library (450 lines) - Timeline, platform, gauge, histogram charts
- Analytics widget enhancements (+173 lines) - Chart.js rendering with interactive features
- Demo page (220 lines) - Complete interactive demonstration
- **Phase 1 Total: 600+ lines**

**Delivered (Phase 2 - WebSocket Real-Time):**
- Server-side broadcasting (60 lines) - Socket.IO event emission on webhook processing
- Client-side WebSocket integration (200 lines) - Real-time updates, connection management
- Connection status UI (55 lines) - Visual indicators with pulse/blink animations
- Testing infrastructure (440 lines) - WebSocket test scripts and validation
- Complete documentation (500 lines) - Architecture, usage, troubleshooting
- **Phase 2 Total: 1,200+ lines**

**Combined Total: ~1,800 lines delivered**

**Tags:** Phase 1: `6bb94690`, Phase 2: `cf4e085c`

**Key Features:**
- ✅ Chart.js 4.4.0 integration with professional visualizations
- ✅ Interactive charts: timeline, platform distribution, success gauge, response histogram
- ✅ WebSocket real-time broadcasting (<100ms latency)
- ✅ Connection status indicator (Live/Connecting/Offline)
- ✅ Auto-reconnect with exponential backoff
- ✅ Multi-client synchronization
- ✅ Flash animation feedback
- ✅ Fallback to polling for older browsers
- ✅ Complete testing and documentation

### v1.2.6 (December 5, 2025) ✅ **COMPLETE**

**Webhook Event History & Analytics** - Comprehensive event tracking, performance analytics, and replay system for webhook debugging.

**Delivered:**
- Event storage system (445 lines) - SQLite database with indexes for fast queries
- Event logging integration (+190 lines server.py) - Automatic tracking with execution timing
- Analytics API endpoints (5 routes) - List events, get details, replay, analytics, delete
- Analytics dashboard widget (1,034 lines) - Real-time metrics, charts, event visualization
- Event replay system - Re-execute webhooks for debugging and testing
- Test suite (399 lines) - Automated testing for all analytics features
- Complete documentation (567 lines) - API reference, setup, troubleshooting
- **Total: 2,595 lines delivered (2,028 code + 567 docs)**

**Tag:** `v1.2.6`
**Commit:** `2e8ce1c2`

**Key Features:**
- ✅ SQLite event storage with 4 indexes for performance
- ✅ Automatic event logging with execution timing (<1ms overhead)
- ✅ Analytics metrics: success rate, response time, platform distribution
- ✅ Event replay for debugging failed webhooks
- ✅ 90-day automatic retention with cleanup
- ✅ Thread-safe operations for concurrent access
- ✅ Dashboard widget with real-time updates

### v1.2.5 (December 3, 2025) ✅ **COMPLETE**

**Integration & Automation (Webhook Server)** - Event-driven knowledge automation with GitHub, Slack, Notion, and ClickUp integration.

**Delivered:**
- Webhook manager service (312 lines) - Registration, validation, event routing
- GitHub webhook handler (356 lines) - Push/PR/release events, auto-workflows
- Platform handlers (455 lines) - Slack slash commands, Notion sync, ClickUp tasks
- API endpoints (5 routes, +280 lines) - Register, list, delete, receive, test
- Dashboard widget (363 lines) - Visual webhook management, live stats
- Testing suite (363 lines) - 8 automated tests, signature validation
- Complete documentation (480 lines) - Setup, security, troubleshooting
- **Total: 2,246 lines delivered (1,766 code + 480 docs)**

**Tag:** `v1.2.5`
**Commits:** [pending]

**Key Features:**
- ✅ GitHub webhooks: Push → knowledge scan, PR → gap analysis, Release → changelog
- ✅ Slack slash commands: `/udos`, `/knowledge`, `/map`
- ✅ Notion page sync, ClickUp task tracking
- ✅ HMAC-SHA256 signature validation (all platforms)
- ✅ Dashboard widget with live stats and testing

### v1.2.11 (December 3, 2025) ✅ **COMPLETE**

**VS Code Extension & Developer Tools** - Complete .uPY language support, script execution, sandbox testing, knowledge quality checking, and image format validation.

**Delivered:**
- VS Code extension foundation (1,783 lines) - Syntax highlighting, IntelliSense, hover docs, snippets
- Script executor & debugger (500 lines) - API integration, debug panels, execution tracking
- Sandbox testing environment (integrated) - Isolated instances, auto-cleanup
- Knowledge quality checker (450 lines) - 6 validation types, REGEN flagging, HTML reports
- Image format validators (400 lines) - SVG inspector, ASCII tester, teletext validator
- **Total: 3,133 lines delivered (87% of 3,600 target)**

**Tag:** `v1.2.10`
**Commits:** 8da33e6c, 9107fee1

### v1.2.4 (December 4, 2025) ✅ **COMPLETE**

**Developer Experience & Hot Reload** - Fast iteration cycle with extension hot reload, GitHub-centric feedback, and enhanced documentation.

**Delivered:**
- Extension hot reload system (621 lines) - <1s reload vs 3-10s restart
- GitHub browser integration (499 lines) - Privacy-first feedback workflow
- Command prompt mode indicators (270 lines) - Visual DEV/ASSIST/regular modes
- Developer documentation (1,015 lines) - Complete guides for hot reload + GitHub feedback
- SHAKEDOWN tests (24 tests, 100% passing)
- **Total: 3,588 lines delivered**

**Tag:** `v1.2.4`
**Commits:** fcb85650, 9460052d, b84c19c1, 289ffe6c, 3929894c, d93ce95e

### v1.2.3 (December 4, 2025) ✅ **COMPLETE**

**Knowledge & Map Layer Expansion** - Multi-layer mapping system with spatial data structures.

**Delivered:**
- 4 map layers (surface, cloud, satellite, underground) - 500 lines
- Spatial data (Earth, planets, galaxies) - 720 lines
- GeoJSON visualization - 130 lines
- Integration tests - 300 lines
- **Total: 1,650 lines delivered**

**Tag:** `v1.2.3`

### v1.2.2 (December 2025) ✅ **COMPLETE**

**DEV MODE Debugging System** (archived to `dev/roadmap/.archive/v1.2.2-complete.md`)

### v1.1.4 (November 2025) ✅ **COMPLETE**

**Graphics System & Visual Output** - Complete graphics system with 4 output formats and AI-assisted diagram generation.

**Delivered:**
- DRAW command handler (526 lines) - AI-assisted diagrams with 4 types (FLOW, TREE, GRID, HIERARCHY)
- Graphics library (450 lines) - Box-drawing characters, templates, color support
- Diagram compositor (350 lines) - Canvas rendering, node/connection model
- Diagram generator (400 lines) - Auto type detection, text parsing, AI integration
- SPRITE command handler (526 lines) - Character/entity management with JSON schema
- PANEL library (902 lines) - 50+ ASCII panel examples (solid, shaded, progress bars)
- Teletext extension (active) - BBC-style rendering, 8-color palette, grid layouts
- SVG extension (active) - Vector diagram generation
- Graphics documentation (597 lines) - Complete wiki guide
- **Total: 3,751 lines delivered**

**Test Coverage:** 120 tests (100% passing)

**Commands:**
- `DRAW [TYPE] <description>` - Generate diagrams (FLOW/TREE/GRID/HIERARCHY)
- `SPRITE [CREATE|LOAD|SAVE|SET|GET] <args>` - Manage sprite entities
- `MAKE SVG <description>` - Generate vector diagrams (formerly GENERATE)
- `MAKE ASCII <description>` - Generate ASCII art
- `MAKE TELETEXT <description>` - Generate teletext graphics

**Graphic Formats:**
1. **ASCII Diagrams** - Box-drawing, FLOW/TREE/GRID/HIERARCHY types
2. **Teletext** - BBC MODE 7 style, 40×24 / 80×25 / 100×30 grids
3. **SVG** - Vector graphics via Gemini AI (Nano Banana pipeline)
4. **SPRITE** - JSON-based character entities with $SPRITE variables

**Tag:** `v1.1.4`
**Wiki:** `wiki/Graphics-System.md`

---

## 📍 Completed Releases Archive

**See:** `dev/roadmap/.archive/completed-releases-v1.2.7.md`

**Summary:**
- v1.2.7 - Chart.js & WebSocket (1,800 lines)
- v1.2.6 - Webhook Analytics (2,595 lines)
- v1.2.5 - Webhook Integration (2,246 lines)
- v1.2.11 - VS Code Extension (3,133 lines)
- v1.2.4 - Hot Reload & Dev Tools (3,588 lines)
- v1.2.3 - Map Layers (1,650 lines)
- v1.1.4 - Graphics System (3,751 lines)

**Summary:**
- v1.2.9 - Gmail Cloud Sync (4,429 lines)
- v1.2.8 - Incremental Updates (2,333 lines)
- v1.2.7 - Chart.js & WebSocket (1,800 lines)
- v1.2.6 - Webhook Analytics (2,595 lines)
- v1.2.5 - Webhook Integration (2,246 lines)
- v1.2.11 - VS Code Extension (3,133 lines)
- v1.2.4 - Hot Reload & Dev Tools (3,588 lines)
- v1.2.3 - Map Layers (1,650 lines)
- v1.1.4 - Graphics System (3,751 lines)

**Total:** ~24,500+ lines delivered across 9 major releases

---

## 📍 Next Priority: v1.3.0

**Status:** 📋 **PLANNED** - Community Features & Content Sharing
**Complexity:** Medium (Building on Gmail Cloud Sync foundation)
**Effort:** ~30-40 MOVES (Part 1: 10-12, Part 2: 8-10, Part 3: 8-10, Part 4: 4-8)
**Dependencies:** v1.2.9 complete (Gmail Cloud Sync provides infrastructure)
**Target:** ~1,500-2,000 lines

### Mission: Community-Driven Knowledge & Content Ecosystem

**Strategic Rationale:**
With Gmail Cloud Sync (v1.2.9) providing secure cloud infrastructure, we can now build community features:
- Users can share missions, workflows, and knowledge
- Community-curated content discovery
- Collaborative knowledge building
- Reputation and contribution tracking

**Strategic Focus:**
- **Content Sharing** - Publish missions/workflows to community
- **Discovery System** - Browse, search, rate community content
- **Collaboration** - Fork, improve, contribute back
- **Reputation** - Track contributions, build community trust

---

## 📍 Archived: v1.2.9 Planning (NOW COMPLETE ✅)

**Status:** ✅ **COMPLETE** - All 4 parts delivered (4,429 lines)
**Delivered:** December 5, 2025
**Commits:** 9c617494, bca87fa8, c0edf7cb, 0e889ee3

### Summary of Completed Work

**Part 1: Gmail Authentication** ✅ COMPLETE (1,437 lines)
- OAuth2 Flow Implementation ✅
  - gmail_auth.py (432 lines) - OAuth2 flow, token encryption
  - Browser-based consent screen
  - Encrypted token storage in .env
  - Token expiry handling and auto-refresh

- Gmail API Integration ✅
  - gmail_service.py (460 lines) - Email listing, sending
  - Gmail query syntax support
  - Message retrieval and metadata parsing

**Part 2: Google Drive Sync Engine** ✅ COMPLETE (1,314 lines)
- Drive API Integration ✅
  - sync_engine.py (542 lines) - Bidirectional sync
  - MD5 checksums for change detection
  - 15 MB storage quota management
  - Incremental sync (only changed files)

- Selective Sync Configuration ✅
  - sync_manager.py (307 lines) - Background threading
  - User-defined sync rules
  - Tier-based filtering
  - Sync history tracking (50 entries)

- Conflict Resolution ✅
  - 4 strategies: newest-wins, local-wins, cloud-wins, manual
  - Local commit history (last 5 versions)
  - Conflict notification in STATUS

**Part 3: Email to uDOS Conversion** ✅ COMPLETE (1,123 lines)
- Email to Markdown Converter ✅
  - email_parser.py (380 lines) - HTML/plain text parsing
  - email_converter.py (408 lines) - Auto-conversion
  - Task extraction with regex patterns
  - Priority detection (urgent, important, low)

- IMPORT GMAIL Command ✅
  - Auto-detection: 3+ tasks=mission, 1-2=checklist, 0=note
  - --preview, --type, --limit options
  - Gmail query syntax support
  - Batch processing

**Part 4: Commands & Integration** ✅ COMPLETE (555 lines)
- Additional Commands ✅
  - QUOTA (50 lines) - Drive quota monitoring
  - CONFIG (118 lines) - Sync configuration
  - EMAIL DOWNLOAD (56 lines) - Individual email conversion
  - EMAIL TASKS (73 lines) - Task extraction

- Testing & Documentation ✅
  - test_gmail_integration.py (348 lines) - Integration tests
  - Gmail-Cloud-Sync.md (822 lines) - Complete wiki guide

**All 10 commands delivered:**
LOGIN, LOGOUT, STATUS, EMAIL LIST/SEND/DOWNLOAD/TASKS, IMPORT, SYNC (6 subcommands), QUOTA, CONFIG

---

## 📍 Future Release: v1.2.10 (Renamed from previous v1.2.9)

**Status:** 📋 **PLANNED** - Cloud POKE Extension Publishing & HTTPS Hosting
**Complexity:** Medium-High (OAuth2 + Google Drive API + sync engine)
**Effort:** ~35-45 MOVES (Part 1: 12-15, Part 2: 10-12, Part 3: 8-10, Part 4: 5-8)
**Dependencies:** v1.2.8 complete (Incremental updates provide sync foundation)
**Target:** ~1,200-1,500 lines

### Mission: Secure Cloud Synchronization with Personal Gmail

**Strategic Rationale:**
Users need to sync essential uDOS content across devices while maintaining offline-first principles. Gmail OAuth provides:
- Zero onboarding friction (most users already have Gmail)
- Secure Google authentication (no password handling)
- 15 MB personal Google Drive storage for text-based sync
- Privacy-first architecture (user controls what syncs)

**Strategic Focus:**
- **Gmail OAuth Integration** - Login with personal Gmail account
- **Google Drive Sync** - 15 MB allocation for memory/shared content
- **Email Integration** - Convert .eml to uDOS-flavored .md, tasks.json
- **Selective Sync** - User controls which tiers sync (Tier 1 always offline-only)
- **Conflict Resolution** - Last-write-wins with local commit history

---

### Part 1: Gmail Authentication (Tasks 1-2)

**Objective:** Implement Gmail OAuth login and token management

**Task 1: OAuth2 Flow Implementation** 📋 PLANNED
- **File:** `core/services/gmail_auth.py` (~350 lines)
- **Features:**
  - Google OAuth2 authentication flow
  - Browser-based consent screen
  - Access token and refresh token management
  - Secure token storage in .env (encrypted)
  - Token expiry handling and auto-refresh
  - User profile retrieval (email, name, ID)

**Commands:**
```python
LOGIN GMAIL              # Start OAuth flow
LOGOUT GMAIL             # Revoke tokens
STATUS GMAIL             # Show connection status
```

**OAuth Scopes:**
- `https://www.googleapis.com/auth/drive.appdata` - App folder access only
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.send` - Send emails
- `https://www.googleapis.com/auth/userinfo.email` - User profile

**Task 2: Gmail API Integration** 📋 PLANNED
- **File:** `core/services/gmail_service.py` (~300 lines)
- **Features:**
  - List emails with filters
  - Download .eml files
  - Convert .eml to uDOS .md format
  - Parse email metadata (from, to, subject, date)
  - Extract tasks from email content
  - Delete emails from server (download & delete workflow)
  - Send emails from uDOS

**Estimated:** ~650 lines

---

### Part 2: Google Drive Sync Engine (Tasks 3-5)

**Objective:** Sync memory/shared content to Google Drive (15 MB limit)

**Task 3: Drive API Integration** 📋 PLANNED
- **File:** `core/services/drive_sync.py` (~400 lines)
- **Features:**
  - Create `/uDOS-sync/` folder in user's Drive
  - Upload/download files
  - 15 MB storage quota management
  - File versioning and conflict detection
  - Incremental sync (only changed files)
  - Bandwidth optimization (compress text files)

**Drive Folder Structure:**
```
/uDOS-sync/
├── memory/
│   ├── docs/              # User documentation
│   ├── shared/            # Community/public content
│   │   ├── groups/
│   │   ├── public/
│   │   └── metadata/
│   └── ucode/             # .uPY scripts
├── config/
│   ├── sync-manifest.json # What's synced, when, checksums
│   └── user-settings.json # Sync preferences
└── metadata/
    └── sync-history.jsonl # Sync log
```

**Task 4: Selective Sync Configuration** 📋 PLANNED
- **File:** `core/services/sync_config.py` (~200 lines)
- **Features:**
  - User-defined sync rules
  - Tier-based filtering (Tier 1 always excluded)
  - File type filters (include .md, .upy, .json; exclude binaries)
  - Size limits per file type
  - Sync schedule (manual, on-exit, periodic)

**Sync Rules Example:**
```json
{
  "enabled": true,
  "tiers": {
    "tier1": false,          // Never sync (offline-only)
    "tier2": true,           // Sync shared content
    "tier3": true            // Sync public content
  },
  "paths": {
    "memory/docs": true,
    "memory/shared": true,
    "memory/ucode": true,
    "memory/missions": false, // Keep local
    "memory/workflows": false // Keep local
  },
  "file_types": [".md", ".upy", ".json", ".txt"],
  "max_file_size_mb": 1,
  "total_quota_mb": 15,
  "schedule": "manual"        // manual | on-exit | hourly
}
```

**Task 5: Conflict Resolution** 📋 PLANNED
- **File:** `core/services/sync_resolver.py` (~250 lines)
- **Features:**
  - Detect conflicts (modified on multiple devices)
  - Last-write-wins strategy (configurable)
  - Local commit history (keep last 5 versions)
  - Conflict notification in STATUS
  - Manual merge tool for critical files

**Estimated:** ~850 lines

---

### Part 3: Email to uDOS Conversion (Tasks 6-7)

**Objective:** Convert emails to uDOS-flavored markdown and tasks

**Task 6: Email to Markdown Converter** 📋 PLANNED
- **File:** `core/services/email_converter.py` (~300 lines)
- **Features:**
  - Parse .eml format
  - Extract headers (From, To, Subject, Date, CC, BCC)
  - Convert HTML body to markdown
  - Preserve attachments metadata
  - Generate uDOS frontmatter
  - Store in `memory/docs/email/`

**Output Format:**
```markdown
---
type: email
from: sender@example.com
to: user@gmail.com
subject: Project Update
date: 2025-12-05T10:30:00Z
gmail_message_id: 18c5f2a1b3d4e5f6
attachments:
  - diagram.svg (stored separately)
tags: [work, project-alpha]
---

# Project Update

Email body converted to markdown...

- **Action Items:**
  - [ ] Review diagram
  - [ ] Schedule meeting
```

**Task 7: Tasks Extraction** 📋 PLANNED
- **File:** `core/services/email_tasks.py` (~200 lines)
- **Features:**
  - Detect task patterns in email body
  - Parse markdown checkboxes `- [ ]`
  - Identify action items (words: "TODO", "Action:", "Next steps")
  - Generate tasks.json entries
  - Link tasks to source email

**Tasks JSON Output:**
```json
{
  "tasks": [
    {
      "id": "task_001",
      "title": "Review diagram",
      "source": "email",
      "email_id": "18c5f2a1b3d4e5f6",
      "created": "2025-12-05T10:30:00Z",
      "status": "todo",
      "priority": "medium"
    }
  ]
}
```

**Estimated:** ~500 lines

---

### Part 4: Commands & Integration (Tasks 8-9)

**Objective:** User-facing commands for sync and email management

**Task 8: Sync Commands** 📋 PLANNED
- **File:** `core/commands/sync_handler.py` (~250 lines)
- **Commands:**
  ```
  SYNC NOW                    # Start manual sync
  SYNC STATUS                 # Show sync state, last sync time
  SYNC CONFIG                 # Show/edit sync configuration
  SYNC CONFLICTS              # List and resolve conflicts
  SYNC HISTORY                # Show sync log
  SYNC QUOTA                  # Show Drive usage (X/15 MB)
  ```

**Task 9: Email Commands** 📋 PLANNED
- **File:** `core/commands/email_handler.py` (~200 lines)
- **Commands:**
  ```
  EMAIL LIST                  # List recent emails
  EMAIL DOWNLOAD <id>         # Download and convert specific email
  EMAIL SYNC                  # Download all unread, convert, delete from Gmail
  EMAIL SEND <to> <subject>   # Send email from uDOS
  EMAIL TASKS                 # Show tasks extracted from emails
  ```

**Estimated:** ~450 lines

---

### Testing & Documentation

**Task 10: Testing Suite** 📋 PLANNED
- **File:** `dev/scripts/test_gmail_sync.py` (~200 lines)
- Test OAuth flow
- Validate Drive sync (upload/download/conflict)
- Email conversion accuracy
- Task extraction
- Quota enforcement

**Task 11: Documentation** 📋 PLANNED
- **File:** `wiki/Gmail-Cloud-Sync.md` (~400 lines)
- Setup guide (OAuth consent screen)
- Security and privacy
- Sync configuration
- Email workflow
- Troubleshooting

**Estimated:** ~600 lines

---

### Summary

**Total Estimated Effort:** ~3,050 lines (code + tests + docs)

**Deliverables:**
- ✅ Gmail OAuth authentication (~650 lines)
- ✅ Google Drive sync engine (~850 lines)
- ✅ Email to markdown converter (~500 lines)
- ✅ Sync & email commands (~450 lines)
- ✅ Testing suite (~200 lines)
- ✅ Complete documentation (~400 lines)

**Key Features:**
- Secure Gmail login (no password handling)
- 15 MB Google Drive storage for text-based sync
- Email to .md conversion (download & delete)
- Task extraction from emails
- Selective sync (user controls what syncs)
- Tier 1 always offline-only
- Conflict resolution with local history
- Bandwidth optimized (compress, incremental)

**Privacy & Security:**
- OAuth scopes limited to app folder only
- Tokens encrypted in .env
- User controls all sync settings
- Email deleted from Gmail after download
- No access to user's personal Drive files
- Tier 1 never syncs (survival knowledge stays offline)

**Dependencies:**
- v1.2.8 incremental updates (sync state management)
- Google OAuth2 client library
- Google Drive API v3
- Email parsing libraries (email, html2text)

**NOTE:** All v1.2.9 tasks above were completed December 5, 2025. See "Latest Releases" section for full delivery details.

---

## 📍 Future Release: v1.2.10 (Previously v1.2.9)

**Status:** 📋 **PLANNED** - Cloud POKE Extension Publishing & HTTPS Hosting
**Complexity:** High (HTTPS server + security + access control + cloud integration)
**Effort:** ~40-55 MOVES (Part 1: 12-15, Part 2: 15-20, Part 3: 10-15, Part 4: 3-5)
**Dependencies:** v1.2.6 complete (Groovebox Extension)

### Mission: Secure Local Extension Publishing with Public HTTPS Access

**Strategic Focus:**
- **HTTPS Extension Hosting** - Publish extensions via secure local HTTPS server
- **Access Control** - User authentication, permissions, sharing controls
- **Cloud Gateway** - Optional bridge to public internet (separated from MeshCore)
- **Security Isolation** - Cloud/web functions completely separate from private mesh network
- **Extension Marketplace** - Discover, share, and install community extensions

**Architectural Decisions:**
1. ✅ **Network Separation:** Cloud POKE uses internet/HTTPS, MeshCore uses private LoRa mesh
2. ✅ **Security First:** TLS/SSL certificates, authentication, rate limiting, input validation
3. ✅ **Optional Service:** Users opt-in to publishing (default: local-only)
4. ✅ **Privacy Controls:** Granular sharing permissions (public, authenticated, private)
5. ✅ **Zero Trust:** All external requests treated as untrusted

**Rationale:**
- Extensions/POKE servers currently local-only (no external access)
- Users want to share extensions, dashboards, teletext pages publicly
- Need secure way to expose select content without compromising system
- Cloud ≠ MeshCore (different networks, different threat models, different use cases)
- Public internet sharing vs. private mesh communication are separate concerns

---

### Part 1: HTTPS Server Infrastructure (Tasks 1-3)

**Task 1: Secure HTTPS Server** 📋 PLANNED
- Create `extensions/cloud/services/https_server.py` (~500 lines)
- **Features:**
  - Built on Python's `aiohttp` or `hypercorn` (async HTTPS server)
  - TLS/SSL certificate management (Let's Encrypt integration + self-signed fallback)
  - Reverse proxy support (nginx/Caddy integration)
  - Automatic certificate renewal
  - HTTP → HTTPS redirect
  - CORS configuration
  - Request logging and metrics
- **Certificate Handling:**
  - Let's Encrypt ACME protocol (certbot integration)
  - Self-signed certificates for testing/local networks
  - Certificate storage in `memory/system/cloud/certs/` (gitignored)
  - Expiry monitoring and auto-renewal alerts
- **Server Configuration:**
  ```json
  {
    "enabled": false,
    "hostname": "localhost",
    "port": 8443,
    "tls_cert": "memory/system/cloud/certs/cert.pem",
    "tls_key": "memory/system/cloud/certs/key.pem",
    "allow_self_signed": true,
    "auto_renew": true,
    "rate_limit": {
      "requests_per_minute": 60,
      "burst": 10
    },
    "cors": {
      "enabled": true,
      "origins": ["*"],
      "methods": ["GET", "POST"]
    }
  }
  ```

**Task 2: Authentication & Access Control** 📋 PLANNED
- Create `extensions/cloud/services/auth_manager.py` (~400 lines)
- **Authentication Methods:**
  - API key tokens (long-lived, revocable)
  - JWT tokens (short-lived, stateless)
  - Basic Auth (username/password, optional)
  - Public (no auth, read-only)
- **Permission Levels:**
  - `PUBLIC` - Anyone can access (read-only)
  - `AUTHENTICATED` - Valid token required
  - `OWNER` - Only extension owner
  - `PRIVATE` - Not externally accessible
- **User Management:**
  ```python
  # User database: memory/system/cloud/users.json (gitignored)
  {
    "users": [
      {
        "id": "user_abc123",
        "username": "explorer",
        "api_keys": [
          {
            "key": "sk_live_xyz789",
            "name": "Dashboard Access",
            "permissions": ["read:extensions", "read:dashboard"],
            "created": "2026-04-01T12:00:00Z",
            "expires": null
          }
        ],
        "created": "2026-04-01T12:00:00Z",
        "last_login": "2026-04-15T09:30:00Z"
      }
    ]
  }
  ```
- **Access Control Lists (ACL):**
  - Per-extension permissions
  - IP allowlist/blocklist
  - Rate limiting per user/IP
  - Audit logging of access attempts

**Task 3: Extension Registry & Discovery** 📋 PLANNED
- Create `extensions/cloud/services/registry.py` (~350 lines)
- **Extension Manifest Enhancement:**
  ```json
  {
    "id": "my-dashboard",
    "name": "My Dashboard",
    "version": "1.0.0",
    "type": "web",
    "cloud": {
      "enabled": true,
      "access_level": "AUTHENTICATED",
      "endpoints": [
        {
          "path": "/dashboard",
          "methods": ["GET"],
          "rate_limit": 30
        },
        {
          "path": "/api/data",
          "methods": ["GET", "POST"],
          "auth_required": true
        }
      ],
      "public_metadata": {
        "description": "Real-time uDOS status dashboard",
        "author": "explorer",
        "tags": ["dashboard", "monitoring"],
        "preview_url": "/dashboard/preview.png"
      }
    }
  }
  ```
- **Discovery API:**
  - `GET /api/extensions` - List public extensions
  - `GET /api/extensions/{id}` - Extension details
  - `GET /api/extensions/{id}/install` - Installation manifest
- **Features:**
  - Search and filter extensions
  - Star/favorite system
  - Download counts and usage stats
  - Version compatibility checking
  - Security scanning (basic validation)

**Estimated:** ~1,250 lines (500 server + 400 auth + 350 registry)

---

### Part 2: Cloud POKE Commands (Tasks 4-6)

**Task 4: CLOUD Command Handler** 📋 PLANNED
- Create `extensions/cloud/commands/cloud_handler.py` (~600 lines)
- **Commands:**
  - `CLOUD ENABLE` - Start HTTPS server (with warnings)
  - `CLOUD DISABLE` - Stop HTTPS server
  - `CLOUD STATUS` - Show server status, URLs, active connections
  - `CLOUD PUBLISH <extension>` - Make extension publicly accessible
  - `CLOUD UNPUBLISH <extension>` - Remove public access
  - `CLOUD CERT` - Certificate management (generate, renew, info)
  - `CLOUD USERS` - User management (add, remove, list)
  - `CLOUD KEYS` - API key management (create, revoke, list)
  - `CLOUD FIREWALL` - IP allowlist/blocklist management
  - `CLOUD LOGS` - Access logs and security events
- **Safety Features:**
  - Interactive confirmation for ENABLE (warns about security)
  - Automatic firewall rules suggestion
  - Security checklist before first publish
  - Rate limit warnings
  - Certificate expiry alerts

**Task 5: Extension Publishing Workflow** 📋 PLANNED
- Create `extensions/cloud/services/publisher.py` (~300 lines)
- **Publishing Steps:**
  1. **Validation** - Check extension manifest, security scan
  2. **Preparation** - Generate public metadata, preview images
  3. **Route Registration** - Add HTTPS endpoints
  4. **DNS/Proxy Setup** - Optional dynamic DNS, reverse proxy config
  5. **Testing** - Automated accessibility checks
  6. **Announcement** - Generate shareable URLs
- **Output:**
  ```
  ✅ Extension published successfully!

  📡 PUBLIC URLS:
     https://udos.local:8443/ext/my-dashboard
     https://12.34.56.78:8443/ext/my-dashboard

  🔗 SHARE LINK:
     https://udos.extensions/my-dashboard (via dynamic DNS)

  🔐 ACCESS CONTROL:
     Level: AUTHENTICATED
     API Key: sk_live_xyz789

  📊 ANALYTICS:
     https://udos.local:8443/ext/my-dashboard/stats

  ⚙️  MANAGE:
     CLOUD UNPUBLISH my-dashboard
     CLOUD LOGS my-dashboard
  ```

**Task 6: Dynamic DNS Integration** 📋 PLANNED
- Create `extensions/cloud/services/ddns_client.py` (~200 lines)
- **Optional Service** for public URLs without static IP
- **Supported Providers:**
  - DuckDNS (free, no registration)
  - No-IP (free tier available)
  - Custom DDNS (user-provided endpoint)
- **Features:**
  - Auto-update IP address on change
  - Subdomain management (udos.duckdns.org)
  - Health monitoring (ping to verify accessibility)
  - Fallback to IP address if DDNS fails
- **Configuration:**
  ```json
  {
    "provider": "duckdns",
    "domain": "my-udos",
    "token": "xyz789-abc123",
    "update_interval": 300,
    "enabled": true
  }
  ```

**Estimated:** ~1,100 lines (600 commands + 300 publisher + 200 DDNS)

---

### Part 3: Security & Isolation (Tasks 7-8)

**Task 7: Network Separation Architecture** 📋 PLANNED
- Create `wiki/Cloud-vs-MeshCore.md` (~400 lines)
- **Clear Distinction:**
  ```
  ┌─────────────────────────────────────────────────────────────┐
  │                      uDOS NETWORKING                         │
  ├─────────────────────────────────────────────────────────────┤
  │                                                               │
  │  CLOUD POKE (Public Internet)        MeshCore (Private Mesh)│
  │  ─────────────────────────           ────────────────────────│
  │  • HTTPS (port 8443)                 • LoRa radio            │
  │  • TLS/SSL encrypted                 • AES-256 encrypted     │
  │  • Authentication required           • Private keys only     │
  │  • Rate limited                      • No internet access    │
  │  • Optional service (opt-in)         • Always offline        │
  │  • Shares extensions/dashboards      • Shares messages/data  │
  │  • Threat: Internet attacks          • Threat: Radio intercept│
  │  • Use: Collaboration, sharing       • Use: Off-grid comms   │
  │                                                               │
  │  ⚠️  NEVER BRIDGE THESE NETWORKS ⚠️                          │
  │  Cloud ≠ Mesh | Public ≠ Private | Optional ≠ Required      │
  └─────────────────────────────────────────────────────────────┘
  ```
- **Documentation:**
  - When to use Cloud POKE vs MeshCore
  - Security considerations for each
  - Privacy implications
  - Threat models
  - Best practices
- **Code Isolation:**
  - Cloud code in `extensions/cloud/`
  - MeshCore code in `extensions/cloned/meshcore/`
  - No shared network stack
  - Separate configuration files
  - Different command namespaces (`CLOUD` vs `MESH`)

**Task 8: Security Hardening** 📋 PLANNED
- Create `extensions/cloud/security/hardening.py` (~300 lines)
- **Security Features:**
  - Input validation (all external requests sanitized)
  - SQL injection prevention (parameterized queries)
  - XSS prevention (output escaping)
  - CSRF tokens for state-changing operations
  - Rate limiting (per IP, per user, per endpoint)
  - Request size limits (prevent DoS)
  - Path traversal prevention
  - Allowlist-based routing (explicit endpoint registration)
- **Security Checklist:**
  ```python
  CLOUD_SECURITY_CHECKLIST = [
      "✓ TLS/SSL certificate configured",
      "✓ Strong passwords/API keys only",
      "✓ Firewall rules reviewed",
      "✓ Rate limiting enabled",
      "✓ Access logs enabled",
      "✓ Regular certificate renewal",
      "✓ No sensitive data in public endpoints",
      "✓ Extension code reviewed for vulnerabilities",
      "✓ CORS properly configured",
      "✓ Input validation on all endpoints"
  ]
  ```
- **Automated Scanning:**
  - Detect common vulnerabilities in extension code
  - Check for exposed secrets/keys
  - Validate HTTPS configuration
  - Test authentication bypass attempts
  - Monitor for suspicious activity
- **Incident Response:**
  - Automatic IP blocking on attack detection
  - Alert notifications (STATUS dashboard)
  - Audit log of security events
  - Revoke compromised API keys

**Estimated:** ~700 lines (400 docs + 300 hardening)

---

### Part 4: Extension Marketplace (Tasks 9-10)

**Task 9: Extension Browser Interface** 📋 PLANNED
- Create `extensions/cloud/web/marketplace.html` + backend (~500 lines)
- **Web UI for discovering extensions:**
  - Browse public extensions by category
  - Search and filter
  - Preview screenshots/demos
  - Read reviews and ratings
  - One-click install (generates `EXTENSION INSTALL` command)
- **API Backend:**
  - `GET /marketplace/extensions` - List all public extensions
  - `GET /marketplace/extensions/{id}` - Extension details
  - `GET /marketplace/categories` - Category list
  - `POST /marketplace/extensions/{id}/star` - Favorite extension
  - `GET /marketplace/search?q=dashboard` - Search
- **Extension Metadata:**
  ```json
  {
    "id": "teletext-news",
    "name": "Teletext News Reader",
    "author": "community",
    "version": "2.1.0",
    "downloads": 142,
    "stars": 23,
    "category": "web",
    "tags": ["teletext", "news", "retro"],
    "description": "BBC-style teletext news pages",
    "preview_url": "/marketplace/extensions/teletext-news/preview.png",
    "install_url": "/marketplace/extensions/teletext-news/install",
    "public_endpoint": "https://udos.local:8443/ext/teletext-news"
  }
  ```

**Task 10: Community Sharing Features** 📋 PLANNED
- Create `extensions/cloud/services/sharing.py` (~250 lines)
- **Sharing Capabilities:**
  - Generate shareable links with expiry
  - Temporary access tokens (24 hours, revocable)
  - QR codes for mobile access
  - Embed codes for external sites
  - Usage analytics (views, installs)
- **Commands:**
  - `CLOUD SHARE <extension>` - Generate shareable link
  - `CLOUD SHARE <extension> --expires 24h` - Time-limited link
  - `CLOUD SHARE <extension> --qr` - Display QR code in terminal
  - `CLOUD SHARE <extension> --revoke` - Disable link
- **Output:**
  ```
  📤 SHAREABLE LINK GENERATED

  🔗 URL: https://udos.extensions/share/abc123xyz

  📱 QR Code:
     ████ ▄▄▄▄▄ █▀█  ████
     █  █ █   █ █▀▀▄█  █
     █▄▄█ █▄▄▄█ █ ▀ █▄▄█

  ⏱️  Expires: 2026-04-16 12:00 UTC

  🔐 Access: Public (no auth required)

  📊 Track: CLOUD LOGS share/abc123xyz
  ```

**Estimated:** ~750 lines (500 marketplace + 250 sharing)

---

### Part 5: Documentation & Testing (Tasks 11-12)

**Task 11: Cloud POKE Documentation** 📋 PLANNED
- Create `wiki/Cloud-POKE-Guide.md` (~800 lines)
- **Sections:**
  1. **Introduction** - What is Cloud POKE, when to use it
  2. **Quick Start** - Enable server, publish first extension
  3. **HTTPS Setup** - Certificate management, Let's Encrypt
  4. **Access Control** - Users, API keys, permissions
  5. **Publishing Extensions** - Workflow, validation, testing
  6. **Security Best Practices** - Hardening, monitoring, incident response
  7. **Dynamic DNS** - Setup providers, auto-updates
  8. **Marketplace** - Browsing, installing, sharing
  9. **API Reference** - All endpoints, parameters, examples
  10. **Troubleshooting** - Common issues, firewall, certificates
- **Security Warnings:**
  - Prominently warn about exposing system to internet
  - Recommend starting with authenticated-only access
  - Explain threat model differences (Cloud vs MeshCore)
  - Best practices for API key rotation
  - How to monitor for suspicious activity

**Task 12: Integration Testing** 📋 PLANNED
- Add Cloud POKE tests to `core/commands/shakedown_handler.py` (+150 lines)
- **Test Scenarios:**
  1. **HTTPS Server** - Start/stop, certificate loading, TLS handshake
  2. **Authentication** - API key validation, JWT tokens, unauthorized access blocked
  3. **Publishing** - Extension validation, route registration, accessibility
  4. **Access Control** - Permission levels enforced, rate limiting works
  5. **Security** - Input validation, XSS prevention, path traversal blocked
  6. **DDNS** - IP update, subdomain resolution
  7. **Marketplace** - Extension listing, search, install
  8. **Network Separation** - Cloud and MeshCore remain isolated
- **Security Testing:**
  - Penetration testing basics (OWASP top 10)
  - Rate limit enforcement
  - Certificate expiry handling
  - API key revocation
  - Firewall rule validation
- **Integration:**
  - Test with real Let's Encrypt certificates (staging environment)
  - Validate reverse proxy compatibility (nginx, Caddy)
  - Test from external network (accessibility checks)
  - Verify mobile QR code access

**Estimated:** ~950 lines (800 docs + 150 tests)

---

## Success Metrics

**HTTPS Server:**
- ✅ Secure TLS/SSL with Let's Encrypt or self-signed certificates
- ✅ Auto-renewal and expiry monitoring
- ✅ Reverse proxy support (nginx/Caddy)
- ✅ Rate limiting and CORS configured
- ✅ Performance: 100+ concurrent connections

**Security & Access Control:**
- ✅ API key and JWT authentication working
- ✅ Permission levels enforced (public, authenticated, private)
- ✅ Rate limiting prevents abuse
- ✅ Input validation on all endpoints
- ✅ Audit logging and security monitoring
- ✅ No vulnerabilities in automated scans

**Publishing & Sharing:**
- ✅ Extensions publish in <30 seconds
- ✅ Shareable links with QR codes
- ✅ Dynamic DNS integration working
- ✅ Marketplace lists public extensions
- ✅ One-click install from marketplace

**Network Separation:**
- ✅ Cloud POKE and MeshCore completely isolated
- ✅ Different codebases, configs, commands
- ✅ Clear documentation on when to use each
- ✅ No accidental bridging of networks

**Documentation & Testing:**
- ✅ Complete Cloud POKE guide (800 lines)
- ✅ Security best practices documented
- ✅ 8/8 SHAKEDOWN tests passing
- ✅ Security scanning passes (no critical vulnerabilities)

---

## Deliverables Summary

**Code:**
- HTTPS server & TLS management (500 lines)
- Authentication & access control (400 lines)
- Extension registry (350 lines)
- CLOUD command handler (600 lines)
- Publishing workflow (300 lines)
- DDNS client (200 lines)
- Security hardening (300 lines)
- Marketplace interface (500 lines)
- Sharing features (250 lines)
- Integration tests (150 lines)
- **Total: ~3,550 lines code**

**Documentation:**
- Cloud vs MeshCore architecture (400 lines)
- Cloud POKE guide (800 lines)
- Security best practices (included)
- API reference (included)
- CHANGELOG entry (100 lines)
- **Total: ~1,300 lines docs**

**Infrastructure:**
- TLS certificate automation
- HTTPS server configuration
- Firewall rules
- Dynamic DNS setup
- Reverse proxy configs

**Grand Total: ~4,850 lines delivered**

---

## Strategic Value

- 🌐 **Public Sharing:** Users can share extensions, dashboards, content globally
- 🔒 **Security First:** TLS, authentication, rate limiting, input validation
- 🚧 **Network Isolation:** Cloud POKE ≠ MeshCore (different networks, different purposes)
- 🎯 **Optional Service:** Users opt-in, default remains local-only (offline-first)
- 🛒 **Marketplace:** Discover and install community extensions
- 📱 **Mobile Friendly:** QR codes, responsive web interfaces
- 🔐 **Access Control:** Granular permissions (public, authenticated, private)
- 🚀 **Extension Ecosystem:** Enables community sharing and collaboration

---

## Security Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    uDOS CLOUD POKE STACK                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🌍 Internet (Untrusted)                                       │
│       ↓                                                         │
│  🔥 Firewall (IP filtering, rate limits)                       │
│       ↓                                                         │
│  🔒 HTTPS Server (TLS/SSL, port 8443)                          │
│       ↓                                                         │
│  🛡️  Authentication Layer (API keys, JWT)                      │
│       ↓                                                         │
│  📋 Access Control (Permissions, ACLs)                         │
│       ↓                                                         │
│  🎯 Extension Router (Validated endpoints only)                │
│       ↓                                                         │
│  📦 Extension Code (Sandboxed execution)                       │
│       ↓                                                         │
│  🗄️  uDOS Core (Read-only access to public data)              │
│                                                                 │
│  ⚠️  NO ACCESS TO:                                             │
│     • User credentials (memory/system/.env)                    │
│     • Private keys (memory/system/cloud/certs/*.key)           │
│     • MeshCore network (separate stack)                        │
│     • System commands (REBOOT, DEV MODE, etc.)                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

**Week 1: HTTPS Infrastructure**
1. HTTPS server with TLS support
2. Certificate management (Let's Encrypt + self-signed)
3. Basic authentication (API keys)
4. CLOUD ENABLE/DISABLE commands

**Week 2: Publishing & Security**
1. Extension publishing workflow
2. Access control and permissions
3. Security hardening (input validation, rate limiting)
4. Firewall integration

**Week 3: Marketplace & Sharing**
1. Extension registry and discovery API
2. Marketplace web interface
3. Sharing features (links, QR codes)
4. Dynamic DNS integration

**Week 4: Documentation & Testing**
1. Complete documentation
2. Security testing and validation
3. Integration tests
4. Real-world testing (external access)

**Total Estimated Time:** 4 weeks

---

## Threat Model & Mitigations

| Threat | Mitigation |
|--------|-----------|
| **DDoS attacks** | Rate limiting, IP blocking, Cloudflare/proxy |
| **Brute force auth** | Rate limiting on login, API key complexity requirements |
| **SQL injection** | Parameterized queries, input validation |
| **XSS attacks** | Output escaping, Content Security Policy |
| **Path traversal** | Allowlist-based routing, path validation |
| **Man-in-the-middle** | TLS/SSL enforced, HSTS headers |
| **API key theft** | Short-lived tokens, key rotation, revocation |
| **Extension vulnerabilities** | Code scanning, sandboxed execution |
| **Certificate expiry** | Auto-renewal, expiry monitoring, alerts |
| **Network bridging** | Architectural separation (Cloud ≠ MeshCore) |

---

## Next Steps (Post v1.2.7)

Cloud POKE enables uDOS to become a platform for sharing creativity while maintaining strict separation from private mesh networks and preserving offline-first principles.

---

## 📍 Future Releases

### Overview of Planned Work

The following sections detail all planned releases and future enhancements for uDOS. Work is organized by priority and dependencies, with estimated complexity and effort for each major release.

**Priority Levels:**
- 🔥 **HIGH** - Critical path, immediate priority
- 🎯 **MEDIUM** - Important, scheduled for near-term
- 💡 **LOW** - Future enhancements, long-term planning

**Status Legend:**
- 📋 **PLANNED** - Design complete, ready for implementation
- 🔄 **IN PROGRESS** - Active development
- ✅ **COMPLETE** - Delivered and tested

---

## 📍 v1.2.10 - Enhanced Webhook Integration & API Server

**Status:** 📋 **PLANNED** (Previously part of v1.2.5, expanded scope)
**Priority:** 🎯 **MEDIUM**
**Complexity:** Medium-High (Event processing + API layer + security)
**Effort:** ~30-40 MOVES
**Dependencies:** v1.2.6 complete (Webhook Analytics provides foundation)
**Target:** ~1,800-2,200 lines

### Mission: Advanced Event-Driven Automation & External API Access

**Strategic Rationale:**
v1.2.5 established basic webhook reception. v1.2.10 expands this with:
- Enhanced event processing and normalization
- Outbound API capabilities (not just inbound webhooks)
- Webhook simulation and testing tools
- Integration with VS Code extension for development

**Strategic Focus:**
- **Event Processing Pipeline** - Normalize, validate, route webhook events
- **API Server Layer** - Expose controlled REST endpoints for automation
- **Webhook Simulation** - Test webhook integrations without real services
- **VS Code Integration** - Developer tools for webhook/API testing

---

### Part 1: Enhanced Event Processing (Tasks 1-2)

**Task 1: Event Normalization Engine** 📋 PLANNED
- **File:** `extensions/core/webhook/services/event_processor.py` (~350 lines)
- **Features:**
  - Normalize payloads from different platforms (Slack, Notion, ClickUp, GitHub)
  - Unified event schema for internal processing
  - Hash/ID mapping for duplicate detection
  - Event validation against schemas
  - Auto-conversion to `.md` and store in appropriate memory tier
- **Event Schema:**
  ```json
  {
    "event_id": "evt_abc123",
    "platform": "github",
    "type": "push",
    "timestamp": "2025-12-05T14:30:00Z",
    "source": {
      "repo": "fredporter/uDOS",
      "branch": "main",
      "user": "fredporter"
    },
    "payload": { /* normalized data */ },
    "actions": ["trigger_script", "update_dashboard", "log_event"]
  }
  ```

**Task 2: Event Routing & Triggers** 📋 PLANNED
- **File:** `extensions/core/webhook/services/event_router.py` (~300 lines)
- **Features:**
  - Route events to appropriate handlers
  - Trigger `.uPY` scripts based on event type
  - Start missions automatically
  - Update dashboards in real-time
  - Send notifications
  - Rate limiting per platform/event type
- **Routing Rules:**
  ```json
  {
    "routes": [
      {
        "platform": "github",
        "event_type": "push",
        "actions": [
          {"type": "script", "path": "memory/workflows/github_push.upy"},
          {"type": "dashboard", "update": "dev-activity"},
          {"type": "log", "tier": "tier3"}
        ]
      }
    ]
  }
  ```

**Estimated:** ~650 lines

---

### Part 2: API Server Layer (Tasks 3-5)

**Task 3: REST API Endpoints** 📋 PLANNED
- **File:** `extensions/core/api/api_server.py` (~500 lines)
- **Core Endpoints:**
  - `POST /api/run` - Execute `.uPY` script
  - `POST /api/memory/add` - Add document to memory
  - `GET /api/memory/search` - Search memory tiers
  - `GET /api/map/status` - Map and location info
  - `GET /api/mission/{id}` - Mission details
  - `POST /api/ask` - AI assistant query (RBAC-enforced)
- **Security:**
  - API key authentication
  - Rate limiting (per key, per endpoint)
  - Input validation
  - RBAC enforcement (role-based access)
  - Audit logging

**Task 4: API Client Library** 📋 PLANNED
- **File:** `extensions/core/api/client.py` (~250 lines)
- **Features:**
  - Python client for uDOS API
  - Authentication handling
  - Retry logic with exponential backoff
  - Response parsing
  - Error handling
- **Usage Example:**
  ```python
  from udos.api import UDOSClient

  client = UDOSClient(api_key="sk_xxx")
  result = client.run_script("memory/workflows/task.upy")
  docs = client.search_memory("water purification")
  ```

**Task 5: Integration Use Cases** 📋 PLANNED
- **Files:** `extensions/core/api/integrations/` (~400 lines)
- **Slack Bot:** Respond to slash commands via API
- **Notion Automation:** Sync pages to uDOS memory
- **ClickUp Workflows:** Create tasks from uDOS missions
- **GitHub Actions:** Trigger uDOS scripts from CI/CD
- **Custom Integrations:** Template for user-created integrations

**Estimated:** ~1,150 lines

---

### Part 3: Webhook Simulation & Testing (Tasks 6-7)

**Task 6: Webhook Simulator** 📋 PLANNED
- **File:** `extensions/core/webhook/simulator.py` (~350 lines)
- **Features:**
  - Send mock webhook events (Slack, Notion, ClickUp, GitHub)
  - Pre-built event templates
  - Custom payload builder
  - Signature generation (HMAC)
  - Response validation
- **Commands:**
  ```
  WEBHOOK SIM SLACK --message "Test message"
  WEBHOOK SIM GITHUB --event push --repo uDOS
  WEBHOOK SIM NOTION --page created
  WEBHOOK SIM CLICKUP --task updated
  ```

**Task 7: API Testing Panel** 📋 PLANNED
- **File:** `extensions/core/api/test_panel.py` (~250 lines)
- **Features:**
  - Interactive API endpoint tester
  - Save/load request templates
  - Response inspection
  - Performance metrics
  - Export to curl/Postman

**Estimated:** ~600 lines

---

### Part 4: Documentation & Testing

**Task 8: Documentation** 📋 PLANNED
- **File:** `wiki/Webhook-API-Integration.md` (~500 lines)
- **Sections:**
  - Event processing pipeline
  - API endpoints reference
  - Authentication and security
  - Integration examples (Slack, Notion, ClickUp, GitHub)
  - Webhook simulation guide
  - Troubleshooting

**Task 9: Integration Tests** 📋 PLANNED
- **File:** `memory/tests/test_webhook_api.py` (~200 lines)
- Test event normalization
- Validate API endpoints
- Security testing (auth, rate limiting)
- Integration scenarios

**Estimated:** ~700 lines

---

### Summary

**Total Estimated:** ~3,100 lines

**Deliverables:**
- Event processing and normalization (~650 lines)
- API server with REST endpoints (~1,150 lines)
- Webhook simulation tools (~600 lines)
- Documentation and tests (~700 lines)

**Key Features:**
- Unified event processing from multiple platforms
- Controlled API access for external automation
- Webhook simulation for testing
- Integration templates for common use cases
- RBAC enforcement for security
- Rate limiting and audit logging

---

## 📍 v1.2.11 - VS Code Extension Enhancement

**Status:** 📋 **PLANNED** (Expansion of existing extension)
**Priority:** 🎯 **MEDIUM**
**Complexity:** Medium (Extension features + testing tools)
**Effort:** ~25-35 MOVES
**Dependencies:** v1.2.10 complete (API/webhook foundation)
**Target:** ~1,500-1,800 lines

### Mission: Complete Developer Environment for uDOS

**Note:** Basic VS Code extension already exists (v1.2.11 delivered syntax highlighting, IntelliSense, script execution). This phase adds advanced features.

**Strategic Focus:**
- **Sandbox Environment** - Isolated uDOS instances for testing
- **Webhook/API Simulation** - Test integrations from VS Code
- **Scenario Testing** - Multi-instance mesh simulation
- **Debug Tools** - Enhanced debugging for `.uPY` scripts

---

### Part 1: Sandbox Environment (Tasks 1-2)

**Task 1: Isolated Instance Manager** 📋 PLANNED
- **File:** `extensions/vscode/src/sandbox/instance_manager.ts` (~400 lines)
- **Features:**
  - Create isolated uDOS instances
  - Clean workspace (no user data)
  - Dev mode enabled by default
  - Auto-cleanup on exit
  - Instance status monitoring
- **Commands:**
  - `uDOS: Launch Sandbox` - Start isolated instance
  - `uDOS: Stop Sandbox` - Clean shutdown
  - `uDOS: Reset Sandbox` - Clear and restart

**Task 2: Replayable Test Runner** 📋 PLANNED
- **File:** `extensions/vscode/src/sandbox/test_runner.ts` (~300 lines)
- **Features:**
  - Run `.uPY` scripts in sandbox
  - Capture output and state
  - Save test scenarios
  - Replay tests automatically
  - Compare results (regression testing)

**Estimated:** ~700 lines

---

### Part 2: Integration Testing Tools (Tasks 3-4)

**Task 3: Webhook Simulator Panel** 📋 PLANNED
- **File:** `extensions/vscode/src/panels/webhook_sim.ts` (~350 lines)
- **Features:**
  - Visual webhook event builder
  - Platform templates (Slack, Notion, ClickUp, GitHub)
  - Send to local or sandbox instance
  - Response viewer
  - Event history

**Task 4: API Route Tester** 📋 PLANNED
- **File:** `extensions/vscode/src/panels/api_tester.ts` (~300 lines)
- **Features:**
  - REST client interface
  - Endpoint explorer (list all API routes)
  - Request builder (headers, body, auth)
  - Response inspector
  - Save request collections

**Estimated:** ~650 lines

---

### Part 3: Scenario Simulation (Tasks 5-6)

**Task 5: Multi-Instance Orchestrator** 📋 PLANNED (Future)
- **File:** `extensions/vscode/src/simulation/orchestrator.ts` (~400 lines)
- **Features:**
  - Spawn multiple uDOS instances
  - Simulate mesh network communication
  - Test distributed scenarios
  - Visualize message flow
  - Performance monitoring

**Task 6: Scenario Test Library** 📋 PLANNED (Future)
- **File:** `extensions/vscode/src/simulation/scenarios/` (~300 lines)
- **Pre-built Scenarios:**
  - 3-node mesh network
  - Leader election simulation
  - Message propagation testing
  - Conflict resolution scenarios
  - Off-grid knowledge sync

**Estimated:** ~700 lines (Future)

---

### Part 4: Documentation & Polish

**Task 7: VS Code Extension Guide** 📋 PLANNED
- **File:** `extensions/vscode/README.md` (update, +300 lines)
- **Sections:**
  - Sandbox environment guide
  - Webhook/API testing
  - Scenario simulation
  - Debugging tips
  - Extension configuration

**Task 8: Extension Polish** 📋 PLANNED
- **Files:** Various (+150 lines)
- **Improvements:**
  - Better error messages
  - Progress indicators
  - Status bar integration
  - Command palette organization
  - Keyboard shortcuts

**Estimated:** ~450 lines

---

### Summary

**Deliverables:**
- Sandbox environment (~700 lines)
- Webhook/API testing tools (~650 lines)
- Multi-instance simulation (~700 lines, future)
- Documentation and polish (~450 lines)

**Key Features:**
- Isolated sandbox instances for safe testing
- Visual webhook/API testing from VS Code
- Replayable test scenarios
- Multi-instance mesh simulation (future)
- Enhanced debugging capabilities

---

## 📍 Future Major Features (Unscheduled)

The following features are planned but not yet assigned to specific releases. They represent long-term strategic initiatives for uDOS.

---

### Native Applications & Device Spawning

**Priority:** 💡 **LOW** (Future strategic initiative)
**Complexity:** Very High (Native development + mesh networking)
**Dependencies:** RBAC complete, security hardening, stable core

#### Tauri Desktop App

**Mission:** Cross-platform native desktop application

**Features:**
- Embedded CLI + Teletext dashboard
- Native menus, notifications, file integration
- Sandbox instances for development
- Offline-first architecture
- System tray integration
- Auto-updates

**Benefits:**
- No terminal required (user-friendly)
- Better performance (native vs web)
- OS integration (file associations, notifications)
- Easier distribution (app stores)

**Estimated:** ~2,500 lines

---

#### Mobile Apps (iOS / Android)

**Mission:** Lightweight field edition of uDOS

**Features:**
- Missions, Maps, Knowledge Library, Tasks, Barter
- Touch-optimized Teletext UI
- Optional sync via Gmail Drive engine
- Offline-first (works without internet)
- Camera integration (document scanning to .md)
- Voice commands (optional)

**Use Cases:**
- Field documentation (survival scenarios)
- Mobile task management
- Quick knowledge lookup
- Bartering on-the-go
- Off-grid mapping

**Estimated:** ~3,000 lines (iOS) + ~3,000 lines (Android)

---

#### Device Spawning + Mesh Networking

**Mission:** Spawn lightweight child nodes for off-grid mesh communication

**Features:**
- Spawn mini uDOS devices (Raspberry Pi, ESP32)
- LoRa-based mesh networking
- Knowledge sync between devices
- Strict Cloud vs Mesh isolation (different networks)
- Auto-discovery of nearby nodes
- Message relay and routing

**Architecture:**
```
Parent Node (Full uDOS)
  ├── Child Node 1 (Mesh device)
  ├── Child Node 2 (Mesh device)
  └── Child Node 3 (Mesh device)
       └── LoRa Mesh Network (offline)

Separate from:
  Cloud POKE (Internet/HTTPS)
```

**Security:**
- AES-256 encryption for mesh messages
- Private key authentication
- No internet access from mesh nodes
- Read-only knowledge sync

**Estimated:** ~4,000 lines

---

### Graphics System Expansion

**Priority:** 💡 **LOW** (Future enhancements)
**Complexity:** Medium (Creative tools + rendering)

#### Teletext / ANSI Renderer Enhancements

**Features:**
- Multi-panel screen generator
- Auto-layout teletext templates
- Dynamic panel builder (titles, sections, grids)
- Block-character shading engine (█ ▓ ▒ ░)
- Colour discipline enforcement (max 5 colors)
- Animation support (6-12 FPS teletext)

**Commands:**
```
MAKE TELETEXT LAYOUT --panels 3 --grid 40x24
MAKE TELETEXT TITLE "News Page"
MAKE TELETEXT ANIMATE sprite_walk.txt --fps 8
```

**Estimated:** ~800 lines

---

#### Photo & Video Teletext Conversion

**Features:**
- Downscale & posterize pipeline (image → teletext)
- Teletext palette mapping (8 colors + brights)
- Character-based shading
- 6–12 FPS teletext animation export
- Batch processing for video frames

**Use Cases:**
- Convert photos to teletext art
- Create retro-style animations
- Generate diagrams from screenshots
- Art projects and aesthetics

**Commands:**
```
CONVERT PHOTO mountain.jpg --teletext --palette bbc --size 80x25
CONVERT VIDEO walk.mp4 --teletext --fps 8 --output walk_teletext/
```

**Estimated:** ~600 lines

---

#### Graphics Template Library Integration

**Features:**
- Merge panel libraries from graphics1.md / graphics2.md
- System diagrams, flows, timelines, theatre layouts
- Export via MAKE ASCII / MAKE TELETEXT / MAKE SVG
- Template browser and selector
- Custom template creation

**Templates:**
- Title pages
- Infographic tiles
- Multi-panel layouts
- System diagrams
- Flowcharts
- Timelines

**Estimated:** ~400 lines

---

### Audio & Groovebox System

**Priority:** 💡 **LOW** (Future creative tools)
**Complexity:** Medium-High (Audio synthesis + music theory)

#### MML Pattern Generator

**Features:**
- Generate MML (Music Macro Language) loops
- 808 drum patterns, 303 basslines, 80s leads
- Pattern chaining + variation support
- Export to MML files for retro systems
- Integration with LMMS/DAWs via MIDI

**Use Cases:**
- Generate retro game music
- Create chiptune loops
- Prototype musical ideas quickly
- Nostalgic sound design

**Commands:**
```
MML DRUM 808 --pattern basic --tempo 120
MML BASS 303 --key Cm --pattern acid
MML LEAD 80s --key Dm --arpeggio up
MML EXPORT track.mml
```

**Estimated:** ~700 lines

---

#### LilyPond Score Rendering

**Features:**
- Multi-stave score builder
- MIDI export for LMMS/DAWs
- Section markers & arrangement tools
- PDF score generation
- MusicXML export

**Use Cases:**
- Generate sheet music from MML
- Compose music in text format
- Export for notation software
- Print-ready scores

**Commands:**
```
LILY SCORE new_song --staves 4
LILY ADD MELODY melody.mml --stave 1
LILY EXPORT song.pdf
LILY EXPORT song.mid
```

**Estimated:** ~500 lines

---

#### Retro & Nostalgic SFX Layer

**Features:**
- CC0 retro SFX library integration
- Funny/nostalgic SFX (bleeps, bloops, 8-bit)
- Routing into `.uPY` scenarios and missions
- Trigger sounds on events
- Sound effect browser

**Use Cases:**
- Add audio feedback to missions
- Retro game aesthetics
- Fun notifications
- Accessibility (audio cues)

**Commands:**
```
SFX PLAY blip
SFX TRIGGER mission_complete --sound fanfare
SFX BROWSE --category retro
```

**Estimated:** ~300 lines

---

### Core System Enhancements (Ongoing)

**Priority:** 🎯 **MEDIUM** (Security and reliability)
**Complexity:** Varies

#### RBAC (Role-Based Access Control)

**Features:**
- Enforce role limits (User/Power/Wizard/Root)
- Apply to AI access, API, sync, and webhooks
- Per-command permissions
- Role inheritance
- Audit logging of privileged actions

**Roles:**
- **User:** Basic commands, offline knowledge, local operations
- **Power:** Web access, AI assistant (rate-limited), cloud sync
- **Wizard:** Extension installation, API access, advanced tools
- **Root:** System configuration, dev mode, unrestricted access

**Estimated:** ~600 lines

---

#### Security Hardening

**Features:**
- CSRF protection for web interfaces
- Input validation (all user inputs)
- JSON schema validation
- Abuse throttling (rate limiting)
- MeshCore separation guarantee (network isolation)
- Dependency vulnerability scanning
- Code signing for extensions

**Ongoing Tasks:**
- Regular security audits
- Penetration testing
- OWASP top 10 compliance
- Security documentation

**Estimated:** ~500 lines (initial) + ongoing maintenance

---

#### Knowledge Bank Upgrades

**Features:**
- PDF → MD → SVG conversion pipelines
- Citation mandates (source tracking)
- Indexing rules for search optimization
- Public Tier 4 enhancements
- Multi-language support
- Version control for guides

**Commands:**
```
KNOWLEDGE IMPORT guide.pdf --category water
KNOWLEDGE INDEX --rebuild
KNOWLEDGE CITE --show-sources
```

**Estimated:** ~800 lines

---

#### Offline AI Prompt Tools

**Features:**
- Prompt testing (quality metrics)
- Prompt versioning (A/B testing)
- Scoring & quality metrics (response evaluation)
- Prompt library (reusable templates)
- Offline prompt optimization (no API calls for testing)

**Use Cases:**
- Optimize AI assistant prompts
- Test prompt effectiveness
- Version control for prompts
- Share prompt templates

**Commands:**
```
PROMPT TEST water_query --iterations 10
PROMPT SCORE --evaluate quality
PROMPT VERSION --compare v1 v2
PROMPT LIBRARY --show templates
```

**Estimated:** ~400 lines

---

### Teletext/ANSI Art House Style Guide

**Priority:** 💡 **LOW** (Content creation support)
**Complexity:** Low (Documentation and templates)

#### Templates & Constraints

**Deliverables:**
- Title page templates
- Infographic tile templates
- Multi-panel layout templates
- Style guide documentation

**Constraints:**
- 40×24 / 80×25 / 100×30 grids
- Max 5 colours (BBC palette)
- No gradients or diagonals
- Block geometry only (█ ▓ ▒ ░ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼)

**Use in:**
- MAKE TELETEXT command
- Dashboard widgets
- Status displays
- Content generation

**Estimated:** ~200 lines (templates + docs)

---

## 📊 Roadmap Summary

### Immediate Priorities (Next 3-6 months)

1. **v1.2.9** - Gmail Cloud Sync (~3,050 lines)
   - OAuth authentication
   - Google Drive sync engine
   - Email to markdown conversion
   - Selective sync with conflict resolution

2. **v1.2.10** - Enhanced Webhooks & API (~3,100 lines)
   - Event processing pipeline
   - REST API server
   - Webhook simulation
   - Integration templates

3. **v1.2.11** - VS Code Extension Enhancement (~1,800 lines)
   - Sandbox environment
   - Webhook/API testing tools
   - Debug improvements

**Total Immediate Work:** ~7,950 lines

---

### Medium-Term (6-12 months)

4. **Cloud POKE** - HTTPS Extension Publishing (~4,850 lines)
   - Secure HTTPS server
   - Extension marketplace
   - Access control & authentication
   - Dynamic DNS integration

5. **RBAC & Security** - Access Control (~1,600 lines)
   - Role-based permissions
   - Security hardening
   - Audit logging

**Total Medium-Term:** ~6,450 lines

---

### Long-Term (12+ months)

6. **Native Apps** - Desktop & Mobile (~8,500 lines)
   - Tauri desktop app
   - iOS/Android apps
   - Device spawning & mesh networking

7. **Creative Tools** - Graphics & Audio (~3,300 lines)
   - Teletext/photo conversion
   - MML/LilyPond music tools
   - SFX integration

8. **Knowledge Expansion** - Content & Tools (~1,400 lines)
   - Knowledge bank upgrades
   - Offline AI tools
   - Multi-language support

**Total Long-Term:** ~13,200 lines

---

### Grand Total Planned Work

**All Future Features:** ~27,600 lines (code + tests + docs)

**By Category:**
- Cloud & Sync: ~7,900 lines (Gmail, Cloud POKE)
- Integration & API: ~4,900 lines (Webhooks, API, VS Code)
- Security & Core: ~2,600 lines (RBAC, hardening, knowledge)
- Native Apps: ~8,500 lines (Desktop, mobile, mesh)
- Creative Tools: ~3,700 lines (Graphics, audio, teletext)

---

## 🗓️ Development Pacing

**Philosophy:** Development measured in STEPS and MOVES, not time.

**Work Proceeds Through:**
- Organic pacing (when inspiration and energy align)
- Cron patterns (scheduled bursts of focused work)
- Priority shifts (immediate needs take precedence)
- Strategic value (high-impact features first)

**Realistic Timeline:**
- v1.2.9 (Gmail Sync): ~35-45 MOVES (~3-5 weeks focused work)
- v1.2.10 (Webhooks/API): ~30-40 MOVES (~3-4 weeks)
- v1.2.11 (VS Code): ~25-35 MOVES (~2-3 weeks)
- Cloud POKE: ~40-55 MOVES (~4-6 weeks)
- Native Apps: ~80-100 MOVES (~8-12 weeks)

**Note:** MOVES are not days. Work proceeds organically based on:
- Available time and energy
- Complexity and focus required
- Testing and validation needs
- Documentation thoroughness

---

## 🎯 Strategic Themes

### 1. Offline-First, Always

Every feature maintains uDOS's core principle:
- Full functionality without internet
- Cloud features are optional enhancements
- Local data remains primary source of truth
- Graceful degradation when services unavailable

### 2. Privacy & Security

User control and data protection:
- Explicit opt-in for cloud features
- Encryption for sensitive data
- RBAC enforcement
- Audit logging
- Network separation (Cloud ≠ Mesh)

### 3. Developer Experience

Tools and workflows for building:
- VS Code extension for development
- Webhook/API simulation
- Sandbox testing environments
- Clear documentation
- Example templates

### 4. Creative Expression

Enable artistic and musical creation:
- Teletext/ASCII art tools
- Music generation (MML/LilyPond)
- Graphics templates
- Retro aesthetics

### 5. Community & Sharing

Optional collaboration features:
- Cloud POKE for extension sharing
- Marketplace for discovery
- Gmail sync for cross-device work
- Webhook integrations for automation

---

## 🤝 Contributing

**Development Process:**
1. Work in `/dev/` for tracked development files
2. Test in `/memory/` (user workspace) for experiments
3. Update wiki for documentation
4. Run full test suite before commit
5. Follow coding standards (see `.github/copilot-instructions.md`)

**Current Priorities:**
1. v1.2.8 implementation (Incremental Updates & Event Buffering)
2. v1.2.9 implementation (Gmail Cloud Sync)
3. v1.2.10 implementation (Cloud POKE Extension)
4. Knowledge & map layer expansion

**How to Help:**
- Report bugs via GitHub Issues
- Suggest features in Discussions
- Contribute knowledge guides to knowledge bank
- Test new features in beta
- Improve documentation

---

## 📝 Roadmap Maintenance

**This Document:**
- **Purpose:** Comprehensive planning document for all uDOS development
- **Scope:** Completed releases + all planned future work
- **Size:** 2,100+ lines (expanded from 1,260 lines)
- **Updated:** December 5, 2025

**Sections:**
1. **Latest Releases** - Recently completed work (v1.2.8, uPY v2.0.2)
2. **Completed Releases** - Archive reference (v1.1.4 through v1.2.7)
3. **Next Priority** - v1.2.9 Gmail Cloud Sync (detailed planning)
4. **Future Releases** - v1.2.10 (Webhooks/API), v1.2.11 (VS Code), Cloud POKE
5. **Future Major Features** - Native apps, graphics, audio, core enhancements
6. **Strategic Summary** - Roadmap overview, themes, development pacing

**Updates:**
- Completed work moves from "Next Priority" → "Latest Releases" → "Completed Archive"
- New features added to "Future Releases" or "Future Major Features"
- Effort estimates refined based on actual delivery
- Dependencies updated as prerequisites complete

**Related Documents:**
- `ROADMAP-incomplete.md` - Source for future planning (consolidated into this file)
- `dev/sessions/` - Development session logs and notes
- `wiki/` - User-facing documentation for completed features
- `CHANGELOG.md` - Release notes and version history

---

**Last Updated:** December 5, 2025
**Roadmap Version:** 2.0 (Comprehensive)
**Next Priority:** v1.2.9 - Gmail Cloud Sync
**Maintainer:** @fredporter
**License:** MIT

---

**Total Planned Future Work:** ~27,600 lines across all releases
**Current Delivered:** ~18,750 lines (v1.1.4 through v1.2.8 + uPY v2.0.2)
**Grand Total Vision:** ~46,000+ lines for complete uDOS ecosystem
