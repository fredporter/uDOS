# uDOS Architectural Call Graph & Consolidation Roadmap

**Status:** Phase 4 - Architecture Stabilization
**Generated:** 2026-03-01
**Scope:** Entry point analysis + duplication audit + convergence strategy

---

## Executive Summary

uDOS has **5 primary entry points** (vibe, ucode, wizard daemon, thin-gui, ACP) that currently operate with **significant duplication** in critical subsystems:

| Issue | Impact | Effort |
|-------|--------|--------|
| **3x Command Dispatch Paths** | Same command routed differently; inconsistent errors | **CRITICAL** |
| **6x Auth Token Validation** | Security contract drift; inconsistent permission checking | **CRITICAL** |
| **2x Incompatible Session Formats** | Can't resume Vibe in Wizard context; cross-tool workflows break | **HIGH** |
| **2x LLM Provider Routing** | Different tasks hit different backends inconsistently | **HIGH** |
| **4x Extension Loaders** | Can't hot-reload; version conflicts; discovery fragmented | **MEDIUM** |

**Recommendation:** Extract 5 unified service modules to be consumed by all entry points. Consolidation delivers:
- Single source of truth for command routing, auth, sessions, LLM routing
- Consistent error handling & logging across platforms
- Enable cross-tool workflows (Wizard → Vibe → Sonic chains)
- Reduce maintenance surface area by ~2000 LOC

---

## Part 1: Entry Point Overview

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER           │
├──────────────────────────────────────────────────┤
│  vibe (Mistral  │ ucode (TUI)  │ Wizard Server   │
│   AgentLoop)    │  Terminal    │  + Dashboard +  │
│                 │              │   Thin-GUI      │
└────────┬────────┴──────┬───────┴────────┬────────┘
         │               │               │
         ▼               ▼               ▼
┌──────────────────────────────────────────────────┐
│              COMMAND/REQUEST DISPATCH LAYER       │
├──────────────────────────────────────────────────┤
│  AgentLoop      CommandDispatcher   HTTP Routes  │
│  (vibe)         (core/tui)          (wizard)     │
│  - Tool calls   - ucode handler     - /api/* +   │
│                 - 50+ cmd handlers  - /health    │
└────────┬────────┴──────┬───────┴────────┬────────┘
         │               │               │
         ▼               ▼               ▼
┌──────────────────────────────────────────────────┐
│              UNIFIED SERVICE LAYER (NEEDED!)      │
├──────────────────────────────────────────────────┤
│ Dispatch Registry    │ Admin Token Manager       │
│ Session Manager      │ LLM Gateway               │
│ Extension Registry   │                           │
│                      │ (Currently fragmented)    │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│              CORE INFRASTRUCTURE                  │
├──────────────────────────────────────────────────┤
│  Config Management   │ Secret Store             │
│  File I/O            │ .env Parser              │
│  Logging             │ Error Tracking           │
└──────────────────────────────────────────────────┘
```

### The Five Entry Points

#### **1. Vibe CLI** → AgentLoop Agentic Model
```
bin/vibe
  └─ vibe/cli/entrypoint.py::main()
     └─ vibe/cli/cli.py::run_cli()
        └─ vibe.core.agents.AgentLoop (1000+ LOC conversation loop)
           ├─ LLM provider selection (agent_loop.py:238-244)
           ├─ Tool execution (tools/*.py executors)
           └─ Session save/resume (~/.vibe/sessions/)
```

**Responsibility:** Multi-turn conversation with LLM-powered tool integration
**State Managed:** Session ID, messages, tool use history, tokens
**Entry File:** [vibe/cli/entrypoint.py](vibe/cli/entrypoint.py#L140)

---

#### **2. uCode CLI** → TUI with Command Dispatcher
```
bin/ucode
  └─ core/tui/ucode_entry.py::main()
     └─ core/tui/ucode.py::UCODE.run() (4000+ LOC TUI class)
        └─ core/tui/dispatcher.py::CommandDispatcher.dispatch()
           ├─ 50+ command handlers (map/, find/, help/, etc.)
           ├─ Game state sync
           └─ Component routing (wizard, sonic, empire, etc.)
```

**Responsibility:** Interactive terminal UI with command routing
**State Managed:** Current route, game state, command history
**Entry File:** [core/tui/dispatcher.py](core/tui/dispatcher.py#L71)

---

#### **3. Wizard Server** → HTTP API + Dashboard
```
bin/wizardd start
  └─ core/services/wizard_daemon_cli.py::main()
     └─ wizard/server.py::WizardServer.run()
        ├─ FastAPI app (HTTP routes)
        │  ├─ /api/ucode/dispatch → re-dispatches to CommandDispatcher
        │  ├─ /api/ok/stream → LLM streaming
        │  ├─ /api/platform/launch → LaunchSessionService
        │  └─ /health, /api/*/etc.
        ├─ WebSocket handler (/ws)
        └─ Dashboard static files (wizard/dashboard/dist/)
```

**Responsibility:** HTTP server exposing all ucode/vibe functionality via REST + WS
**State Managed:** Authenticated sessions, launch sessions, cost tracking
**Entry File:** [wizard/server.py](wizard/server.py#L94)

---

#### **4. CommandDispatcher** → Unified Routing (Used By #2 & #3)
```
CommandDispatcher::dispatch(command, args)
  ├─ Handler lookup in {map, find, catalog, wizard, sonic, ...}
  ├─ Auth check (if required)
  ├─ Execution with context
  └─ State sync
```

**Responsibility:** Route string commands to handler modules
**State Managed:** Handler registry
**Entry File:** [core/tui/dispatcher.py](core/tui/dispatcher.py#L205)

**Used By:** core/tui (directly), wizard/routes/ucode_dispatch_routes.py (HTTP wrapper)

---

#### **5. Thin-GUI** → TypeScript Client Library
```
extensions/thin-gui/src/index.ts
  ├─ emitLaunchIntent(fetcher, launchPath, intent)
  │  └─ POST /api/platform/launch
  │     └─ LaunchSessionService
  │        └─ May spawn vibe/ucode/wizard elsewhere
  └─ consumeLaunchSession(fetcher, sessionId, onEvent)
     └─ Stream from /api/platform/launch/{sessionId}/stream
```

**Responsibility:** TypeScript client for launcher UX
**State Managed:** Launch intent contracts, session stream events
**Entry File:** [extensions/thin-gui/src/index.ts](extensions/thin-gui/src/index.ts)

---

## Part 2: Critical Overlaps & Duplication

### ISSUE #1: Three-Layer Command Dispatch (CRITICAL ⚠️)

**Problem:** A single user command can take three incompatible paths:

```
User Input: "map"
    │
    ├─ TUI Path (local execution)
    │  LocalInput → CommandDispatcher.dispatch("map") → MapHandler
    │
    ├─ HTTP Path (wrapped dispatch)
    │  POST /api/ucode/dispatch {command: "map"}
    │    → wizard/routes/ucode_dispatch_routes.py::dispatch_command()
    │    → calls CommandDispatcher.dispatch() again (line 53)
    │
    └─ OK Path (LLM-routed)
       POST /api/ok/stream {prompt: "show map"}
         → wizard/routes/ucode_ok_routes.py::stream_ok_command()
         → wizard/services/ok_gateway.py::complete_stream()
         → (maybe calls dispatcher, maybe calls LLM directly)
```

**Consequences:**
- **Error handling inconsistent**: MapHandler error logged in dispatcher context vs. HTTP context vs. OK routing context
- **Ghost mode enforced in one place**: [core/tui/dispatcher.py:219-225](core/tui/dispatcher.py#L219-L225) but not at HTTP layer
- **State sync fragmented**: Game state synced after local dispatch [dispatcher.py:264-292](core/tui/dispatcher.py#L264-L292) but HTTP layers may not sync
- **Same handler called twice**: If HTTP path calls dispatcher, then wizard routes also check auth

**Files Involved:**
| File | Lines | Role |
|------|-------|------|
| [core/tui/dispatcher.py](core/tui/dispatcher.py#L71) | 71-300 | Primary dispatcher (dispatch logic + handlers) |
| [wizard/routes/ucode_dispatch_routes.py](wizard/routes/ucode_dispatch_routes.py#L44) | 44-70 | HTTP wrapper that re-dispatches |
| [wizard/routes/ucode_ok_routes.py](wizard/routes/ucode_ok_routes.py) | 1-100+ | OK gateway that may or may not use dispatcher |
| [core/tui/ucode.py](core/tui/ucode.py#L525) | 525-530 | Entry point for TUI dispatch |

**Recommendation: Extract `core/services/unified_dispatch_registry.py`**
```python
class DispatchRegistry:
    """Single source of truth for command routing."""

    def register_handler(self, command: str, handler: Callable) -> None:
        """All entry points register handlers here."""

    def dispatch(self,
                 command: str,
                 args: dict,
                 context: DispatchContext) -> AsyncGenerator[Event, None]:
        """
        Unified dispatch with:
        - Auth checks (via context)
        - Logging correlation (transaction ID)
        - State sync guarantee
        - Error context preservation
        """

# Replace all three paths:
CommandDispatcher inherits from DispatchRegistry
HTTP routes call registry.dispatch()
OK routes call registry.dispatch() with ok_context
```

---

### ISSUE #2: Six Auth Token Validation Paths (CRITICAL ⚠️)

**Problem:** Admin token is validated in 6+ incompatible ways:

| # | Location | Implementation | Issue |
|---|----------|---|---|
| 1 | [wizard/services/wizard_auth.py:68-95](wizard/services/wizard_auth.py#L68-L95) | Checks `WIZARD_ADMIN_TOKEN` env vs. request Bearer header | Slow: scans .env every request |
| 2 | [wizard/routes/config_admin_routes.py:123-152](wizard/routes/config_admin_routes.py#L123-L152) | Reads `.env` directly with different parsing | Duplicates parser logic |
| 3 | [wizard/services/admin_secret_contract.py:103-180](wizard/services/admin_secret_contract.py#L103-L180) | Separate drift detection (token ≠ secret store) | Disconnected from validation |
| 4 | [core/tui/ucode.py:2720-2760](core/tui/ucode.py#L2720-L2760) | Calls wizard HTTP endpoint OR generates locally | Inconsistent with server auth |
| 5 | [wizard/dashboard/src/routes/Config.svelte:990-1010](wizard/dashboard/src/routes/Config.svelte#L990-L1010) | Frontend form that sends token to server | No client-side validation |
| 6 | [wizard/dashboard/src/lib/services/auth.ts:56](wizard/dashboard/src/lib/services/auth.ts#L56) | JS stub `validateAdminToken()` | Incomplete (doesn't actually validate) |

**Consequences:**
- **Multiple `.env` readers**: Code duplication + inconsistent parsing (some handle comments, some don't)
- **No contract enforcement**: Token can validate but still be "drifted" per [admin_secret_contract.py:115](wizard/services/admin_secret_contract.py#L115)
- **Repair logic disconnected**: Dashboard shows drift, but TUI validation doesn't trigger repair
- **Token format unclear**: Some code checks HMAC [wizard_auth.py:82](wizard/services/wizard_auth.py#L82), others compare strings
- **TUI can't validate**: [core/tui/ucode.py](core/tui/ucode.py#L2720) calls HTTP endpoint or generates, but doesn't check if token is valid

**Token Flow (Current):**
```
User sets token in Config dashboard
  → POST /api/admin-token/set
  → wizard/routes/config_admin_routes.py stores to .env

User runs ucode command that needs token
  → core/tui/dispatcher checks context.admin_token (from where?)
  → If missing, calls /api/admin-token/generate

User accesses protected Wizard API
  → POST request with Authorization: Bearer token
  → wizard_auth.py reads .env WIZARD_ADMIN_TOKEN
  → Compares with header
  → Returns 403 if mismatch

Contract audit runs
  → admin_secret_contract.py checks if token in .env == secret store
  → Marks drift if mismatch
  → DOESN'T call validation logic

Dashboard shows "Token status: DRIFTED"
```

**Recommendation: Extract `core/services/admin_token_manager.py`**
```python
class AdminTokenManager:
    """Unified admin token validation & contract management."""

    def validate(self, token: str) -> ValidationResult:
        """
        Check if token is valid.
        Integrates contract checking.
        Returns: {valid: bool, drift: dict, repair_needed: bool}
        """

    def get_current_token(self) -> str | None:
        """Fetch active token from canonical source."""

    def set_token(self, token: str, source='user') -> bool:
        """Store token, update .env + secret store, verify no drift."""

    def check_contract(self) -> ContractStatus:
        """Detect drift between .env, secret store, and dashboard state."""

    def repair_contract(self) -> RepairResult:
        """Auto-fix drift: regenerate if needed, update all sources."""

# All 6 locations call this:
wizard_auth.py                    → manager.validate()
config_admin_routes.py            → manager.set_token() + manager.check_contract()
admin_secret_contract.py          → manager.check_contract() + manager.repair_contract()
core/tui/ucode.py                 → manager.validate() if token present
wizard/dashboard/src/lib/auth.ts  → fetch /api/admin-token/validate
                                     (which calls manager.validate())
```

---

### ISSUE #3: Incompatible Session Formats (HIGH ⚠️)

**Problem:** Vibe and Wizard use two incompatible session models:

| Aspect | Vibe | Wizard |
|--------|------|--------|
| **Session ID Format** | UUID (e.g., `a1b2c3d4-e5f6...`) | target-timestamp-hex (e.g., `vibe-20260301120000-abc123`) |
| **Storage Location** | `~/.vibe/sessions/{session_id}/` | `memory/wizard/launch/{session_id}.json` |
| **State Tracking** | Conversation messages + usage stats | Platform lifecycle (planned → starting → ready → stopping) |
| **Resume Capability** | `vibe --resume {session_id}` | LaunchSessionService.get_session() |
| **Cross-Tool Resume** | Not possible | Creating Vibe via Wizard launch creates separate Vibe session |

**Example Scenario (Broken Workflow):**
```
1. User opens Wizard dashboard, clicks "Launch Vibe"
   → Wizard creates LaunchSession (id=vibe-20260301-xyz, state=planned)
   → Calls /api/platform/launch with vibe target

2. LaunchSessionService spawns vibe subprocess
   → Vibe creates AgentLoop with its own session_id (UUID)
   → Vibe session NOT linked to Wizard LaunchSession

3. User closes Wizard dashboard
   → LaunchSession marked stopped
   → Vibe session still exists in ~/.vibe/sessions/

4. User opens Wizard dashboard again, tries to resume
   → Wizard finds LaunchSession (stopped)
   → User tries "resume" — fails
   → User manually runs `vibe --resume UUID` in terminal
   → Vibe resumes its own session (disconnected from Wizard)

Result: Two incompatible session formats; can't manage Vibe from Wizard dashboard
```

**Files Involved:**
| File | Role |
|------|------|
| [wizard/services/launch_session_service.py:77-90](wizard/services/launch_session_service.py#L77-L90) | Wizard session creation |
| [vibe/core/agent_loop.py:176-185](vibe/core/agent_loop.py#L176-L185) | Vibe session save |
| [vibe/acp/acp_agent_loop.py:248-270](vibe/acp/acp_agent_loop.py#L248-L270) | Vibe session ID generation |
| [wizard/routes/platform_routes.py:246-280](wizard/routes/platform_routes.py#L246-L280) | Session streaming |

**Recommendation: Extract `core/services/unified_session_manager.py`**
```python
@dataclass
class UnifiedSession:
    """Canonical session format for all entry points."""
    session_id: str                    # UUID
    platform_session_id: str | None    # Wizard LaunchSession ID (if launched via platform)
    agent_type: str                    # 'vibe' | 'ucode' | 'acp'
    state: SessionState               # planned | running | paused | ended | error
    created_at: datetime
    started_at: datetime | None
    ended_at: datetime | None

    metadata: dict                    # {target, mode, workspace, ...}
    messages: list[Message]           # Conversation history
    artifacts: dict                   # Saved files, outputs, etc.

class UnifiedSessionManager:
    """Unified session lifecycle across all entry points."""

    def create_session(self, agent_type: str, metadata: dict) -> UnifiedSession:
        """Create new session in canonical format."""

    def get_session(self, session_id: str) -> UnifiedSession | None:
        """Retrieve session."""

    def update_state(self, session_id: str, new_state: SessionState) -> bool:
        """Update session state (planning → running → paused → ended)."""

    def link_platform_session(self, session_id: str, platform_session_id: str) -> bool:
        """Link vibe session to Wizard launch session."""

    def list_sessions(self, agent_type: str | None = None) -> list[UnifiedSession]:
        """List all sessions, optionally filtered by agent type."""

# Usage:
# Vibe: manager.create_session('vibe', {}) → UnifiedSession
# Wizard: manager.create_session('vibe', {target: 'vibe'}) → UnifiedSession
# Both use same format; Wizard can manage Vibe sessions
```

---

### ISSUE #4: Two LLM Provider Routing Paths (HIGH ⚠️)

**Problem:** Different paths hit different backends:

| Path | Selection Logic | Can Lead To |
|------|---|---|
| **Vibe AgentLoop** | [agent_loop.py:238-244](vibe/core/agent_loop.py#L238-L244) `config.get_provider_for_model(model_name)` | Hardcoded provider per model in config |
| **Wizard OK Gateway** | [ok_gateway.py:849-920](wizard/services/ok_gateway.py#L849-L920) Classify request → Apply policy → Select provider | Policy enforcement (cost limits, rate limits, etc.) |

**Example Conflict:**
```
Config has: model "gpt-4" → provider "openai"

Vibe CLI:
  vibe "Write code"
    → AgentLoop sees "gpt-4"
    → Looks up config.get_provider_for_model("gpt-4")
    → Uses OpenAI backend

Wizard API:
  POST /api/ok/stream {model: "gpt-4", task: "code-gen"}
    → OK Gateway classifies task as "code-gen"
    → Checks policy: cost_limit=500, code-gen quota=10
    → Selects provider based on quota + cost, may pick "claude" instead
    → User gets different backend than Vibe CLI for same model!
```

**Files Involved:**
| File | Lines | Role |
|------|-------|------|
| [vibe/core/agent_loop.py](vibe/core/agent_loop.py#L238) | 238-244 | Config-driven selection |
| [vibe/core/llm/backend/factory.py](vibe/core/llm/backend/factory.py) | (full file) | Backend instantiation |
| [wizard/services/ok_gateway.py](wizard/services/ok_gateway.py#L719-920) | 719-920 | Policy-driven selection |
| [wizard/services/cost_policy.py](wizard/services/cost_policy.py) | (full file ?) | Cost enforcement |

**Recommendation: Extract `core/services/unified_llm_gateway.py`**
```python
class LLMGateway:
    """Unified LLM provider selection & routing."""

    def select_provider(self,
                        model: str,
                        task_classification: TaskType | None = None,
                        context: RequestContext | None = None
    ) -> ProviderConfig:
        """
        Select provider considering:
        1. Model → provider mapping (config)
        2. Policy enforcement (cost, quota, priority)
        3. Request context (user, task, etc.)

        Returns same provider for same inputs from all callers.
        """

    async def complete(self,
                      prompt: str,
                      model: str,
                      **kwargs) -> str | AsyncGenerator[str]:
        """
        Route request to selected provider backend.
        Both Vibe + Wizard use this.
        """

# Usage:
gateway = LLMGateway(config, policy_manager)
provider = gateway.select_provider("gpt-4", TaskType.CODE_GEN)
# Both Vibe + Wizard get same provider for same task
```

---

### ISSUE #5: Four Extension Loaders (MEDIUM ⚠️)

**Problem:** Extensions loaded via 4+ incompatible systems:

| System | Location | Loading Method | Issues |
|--------|----------|---|---|
| **Wizard Extension Routes** | [wizard/routes/extension_routes.py:14-30](wizard/routes/extension_routes.py#L14-L30) | Checks path existence for `extensions/{name}/` | Can't detect unavailable extensions |
| **Empire Handler** | [core/commands/empire_handler.py:71-78](core/commands/empire_handler.py#L71-L78) | Try/except import empire | Soft-fail silently |
| **Wizard Empire Loader** | [wizard/services/empire_loader.py:15-32](wizard/services/empire_loader.py#L15-L32) | Duplicates core loader logic | Duplication |
| **Sonic Loader** | [extensions/sonic_loader.py:22-50](extensions/sonic_loader.py#L22-L50) | Custom sys.path manipulation | Can't hot-reload |

**Consequences:**
- **Inconsistent availability**: Sonic available in shell but not reported via Wizard API
- **No hot-reload**: Adding extensions requires server restart
- **Version conflicts**: No version pinning; can load incompatible versions
- **Can't depend on extensions**: Core code can't assume extension is available

**Recommendation: Extract `core/services/extension_registry.py`**
```python
class ExtensionRegistry:
    """Unified extension discovery, loading, and lifecycle management."""

    def discover(self) -> dict[str, ExtensionMetadata]:
        """Find all available extensions (installed + discoverable)."""

    def load(self, extension_id: str) -> Extension | None:
        """Load extension; return None if unavailable."""

    def reload(self, extension_id: str) -> bool:
        """Hot-reload extension (for development)."""

    def list_loaded(self) -> dict[str, Extension]:
        """List currently loaded extensions."""

# Replace all 4 loaders with calls to this registry
```

---

## Part 3: Consolidation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Objective:** Extract unified services; wire into existing entry points without changing behavior.

#### 1.1 Extract `core/services/unified_dispatch_registry.py`
```python
# New file: core/services/unified_dispatch_registry.py
class CommandRegistry:
    def register_handler(self, cmd: str, handler: Callable): ...
    def dispatch(self, cmd: str, args: dict, context: DispatchContext): ...

# Modify: core/tui/dispatcher.py
class CommandDispatcher(CommandRegistry):  # Inherit
    def __init__(self):
        super().__init__()
        self.register_handler("map", MapHandler self.map_command)
        # ...

# Modify: wizard/routes/ucode_dispatch_routes.py
from core.services.unified_dispatch_registry import CommandRegistry
dispatcher = CommandRegistry()  # Use unified
```

**Impact:**
- CommandDispatcher behavior unchanged
- HTTP routes now call same dispatcher
- No logic duplication

---

#### 1.2 Extract `core/services/admin_token_manager.py`
```python
# New file: core/services/admin_token_manager.py
class AdminTokenManager:
    def validate(self, token: str) -> ValidationResult: ...
    def get_current_token(self) -> str | None: ...

# Modify: wizard/services/wizard_auth.py
from core.services.admin_token_manager import AdminTokenManager
auth_manager = AdminTokenManager(config)

def authenticate_admin(self, request):
    token = request.headers.get("Authorization", "").split()[-1]
    result = auth_manager.validate(token)
    if not result.valid:
        raise HTTPException(403)
```

---

#### 1.3 Extract `core/services/unified_session_manager.py`
```python
# New file: core/services/unified_session_manager.py
class UnifiedSessionManager:
    def create_session(self, agent_type: str, metadata: dict): ...
    def get_session(self, session_id: str): ...

# Modify: vibe/core/agent_loop.py
from core.services.unified_session_manager import UnifiedSessionManager
manager = UnifiedSessionManager()
session = manager.create_session('vibe', {})  # Create in unified format

# Modify: wizard/services/launch_session_service.py
session = manager.create_session('vibe', {target: 'vibe'})
manager.link_platform_session(session.id, platform_session.id)
```

---

### Phase 2: Migration (Weeks 3-4)

**Objective:** Migrate all consumers to use extracted services.

- Vibe AgentLoop → UnifiedSessionManager
- Wizard LaunchSessionService → UnifiedSessionManager + unified dispatch
- TUI ucode → unified dispatch registry
- All 6 auth paths → admin token manager

---

### Phase 3: Cleanup (Week 5)

**Objective:** Remove duplicate implementations; consolidate to single source.

- Delete wizard/services/empire_loader.py (use ExtensionRegistry)
- Delete admin_secret_contract.py logic from 4 other locations
- Delete duplicate `.env` readers

---

## Part 4: Updated Architecture (Post-Consolidation)

```
┌────────────────────────────────────────────────────────┐
│                  USER INTERFACES                       │
├────────────────────────────────────────────────────────┤
│  vibe CLI      │  ucode (TUI)  │  Wizard Server/UI    │
└────────┬───────┴──────┬───────┴─────────┬─────────────┘
         │              │                 │
         ▼              ▼                 ▼
┌────────────────────────────────────────────────────────┐
│             UNIFIED SERVICE LAYER                      │
├────────────────────────────────────────────────────────┤
│  DispatchRegistry    │  AdminTokenManager               │
│  UnifiedSessionMgr   │  UnifiedLLMGateway              │
│  ExtensionRegistry   │  (All source of truth)          │
└────────────────┬─────────────────────────────┬─────────┘
                 │                             │
                 ▼                             ▼
┌────────────────────────────────────────────────────────┐
│         DATA & CONFIG LAYER                          │
├────────────────────────────────────────────────────────┤
│  File I/O  │  Config Parser  │  Secret Store  │ Logging │
└────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Single command dispatcher (not 3)
- ✅ Unified auth validation (not 6)
- ✅ Compatible session format (Wizard ↔ Vibe)
- ✅ Consistent LLM routing
- ✅ Unified extension loading
- ✅ Cross-tool workflows enabled
- ✅ ~2000 LOC reduction in duplication

---

## Summary: Files to Extract

| Module | Purpose | Consolidates | Effort |
|--------|---------|---|---|
| `core/services/unified_dispatch_registry.py` | Command routing | dispatcher + ucode_dispatch_routes + ucode_ok_routes | **High Impact** |
| `core/services/admin_token_manager.py` | Auth validation | 6 auth paths | **Critical** |
| `core/services/unified_session_manager.py` | Session lifecycle | launch_session_service + agent_loop | **High Impact** |
| `core/services/unified_llm_gateway.py` | Provider selection | agent_loop + ok_gateway | **Medium Impact** |
| `core/services/extension_registry.py` | Extension loading | 4 loaders | **Medium Impact** |

---

**Next Steps:**
1. ✅ Document entry points (DONE)
2. ✅ Identify overlaps (DONE)
3. ⏭️ **Create Phase 1 PRs to extract unified services**
4. ⏭️ Migrate consumers to use extracted services
5. ⏭️ Remove duplicate implementations
6. ⏭️ Enable cross-tool workflows (e.g., "Wizard → Vibe → Sonic" chains)
