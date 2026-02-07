# Wizard Service Split Map (v1.3.8)

Date: 2026-02-07
Owner: uDOS/Wizard
Goal: establish clear service boundaries and a migration path to `/api` + `/mcp`.

---

## Principles

- **Wizard** remains the umbrella name.
- **/api** holds canonical contracts; **/wizard** holds implementations.
- **/mcp** exposes tool surfaces that map to `/api` contracts.
- Each service should be testable in isolation and callable via HTTP and MCP.

---

## Target Service Boundaries

### 1) Wizard Core
**Responsibilities**
- Auth, rate limiting, config, logging, system info, health

**Primary code**
- `wizard/services/device_auth.py`
- `wizard/services/rate_limiter.py`
- `wizard/services/logging_manager.py`
- `wizard/services/system_info_service.py`
- `wizard/server.py`

**API contracts**
- `/api/wizard/services/health.md`
- `/api/wizard/services/config.md`

---

### 2) AI & Model Gateway
**Responsibilities**
- Provider routing, model selection, AI request orchestration

**Primary code**
- `wizard/services/ai_gateway.py`
- `wizard/services/model_router.py`
- `wizard/services/mistral_api.py`
- `wizard/services/provider_load_logger.py`

**API contracts**
- `/api/wizard/services/providers.md`

---

### 3) Workflow + Scheduler
**Responsibilities**
- Tasks, automation, reminders, workflow orchestration

**Primary code**
- `wizard/services/task_scheduler.py`
- `wizard/services/workflow_manager.py`
- `wizard/services/notification_history_service.py`
- `wizard/services/task_classifier.py`

**API contracts**
- (new) `/api/wizard/services/workflow.md`
- (new) `/api/wizard/services/tasks.md`

---

### 4) Assets + Data
**Responsibilities**
- Artifacts, datasets, binder, library, vault, file assets

**Primary code**
- `wizard/services/artifact_store.py`
- `wizard/services/dataset_service.py`
- `wizard/services/library_manager_service.py`
- `wizard/services/tree_service.py`
- `wizard/services/wiki_provisioning_service.py`

**API contracts**
- (new) `/api/wizard/services/artifacts.md`
- (new) `/api/wizard/services/datasets.md`
- (new) `/api/wizard/services/library.md`
- (new) `/api/wizard/services/wiki.md`

---

### 5) Plugins + Extensions
**Responsibilities**
- Plugin registry, validation, distribution, packing

**Primary code**
- `wizard/services/plugin_registry.py`
- `wizard/services/plugin_repository.py`
- `wizard/services/plugin_factory.py`
- `wizard/services/plugin_validation.py`
- `wizard/services/pack_manager.py`

**API contracts**
- (new) `/api/wizard/services/plugins.md`

---

### 6) Monitoring + Diagnostics
**Responsibilities**
- Health checks, diagnostics, monitoring summaries

**Primary code**
- `wizard/services/monitoring_manager.py`
- `wizard/services/health_diagnostics.py`
- `wizard/services/repair_service.py`

**API contracts**
- (new) `/api/wizard/services/diagnostics.md`

---

### 7) Companion Web UI
**Responsibilities**
- Dashboard and browser UI for Wizard

**Primary code**
- `wizard/web/`
- `wizard/dashboard/`

**API contracts**
- Consume `/api/wizard/services/*`

---

## Migration Phases

### Phase A — Contract First
- Create the missing `/api/wizard/services/*.md` entries.
- Define JSON request/response samples for each service.

### Phase B — Route Normalization
- Ensure `wizard/routes/*` align with contracts.
- Add route aliases where needed (e.g., `/api/providers` vs `/api/providers/list`).

### Phase C — MCP Surface
- Add MCP tool bindings for each service (in `/mcp/wizard/`).
- Keep tool names stable (e.g., `wizard.providers.list`).

### Phase D — UI Alignment
- Update Wizard web UI to consume contract endpoints.

---

## Immediate Next Tasks

1. Draft the missing contracts:
   - `workflow.md`, `tasks.md`, `artifacts.md`, `datasets.md`, `library.md`, `wiki.md`, `plugins.md`, `diagnostics.md`
2. Decide which two services to split first (recommended: **Plugins** + **Workflow**).
3. Add MCP tools for the chosen services.

