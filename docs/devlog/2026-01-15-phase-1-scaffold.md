# Development Log - 2026-01-15

## Phase 1: Architecture Split + App Scaffold (Week 1-2)

### Completed Today

#### 1. AGENTS.md Updated

- Added Dev Server section (3.3.2)
- Clarified Wizard Server as production-only (3.3.1)
- Noted service split: Wizard stays frozen at v1.1.0.0, Dev experimental at v0.x
- Documented port assignments: 8765 (Wizard), 8766 (Dev)

#### 2. Roadmap Updated (docs/roadmap.md)

- Updated v1.0.2.0 focus from "Theme System" → "Architecture Split + App Scaffold"
- Added extended roadmap with 4 phases over 8 weeks
- Success criteria include both servers operational + TS runtime basic blocks

#### 3. uMarkdown App Scaffold (`/app`)

**Dependencies:**

- Added Svelte 4.2.0 + Tailwind CSS 3.4.1
- Added svelte-vite-plugin + autoprefixer
- Updated package.json scripts for Tauri dev

**Frontend Stack:**

- `tailwind.config.js` — Theme, colors, typography
- `postcss.config.js` — PostCSS + autoprefixer
- `vite.config.ts` — Svelte plugin integration
- `src/App.svelte` — Root component (header, sidebar, editor/preview split)
- `src/main.ts` — Entry point (Svelte initialization)

**Components:**

- `BinderNav.svelte` — Tree navigation (folders, files, tasks)
- `MarkdownEditor.svelte` — Editor with toolbar (B, I, code, links)
- `Preview.svelte` — Live markdown rendering

**Updated:**

- `index.html` → Clean Svelte entry point (removed old Tauri template)
- `app/README.md` → Complete feature + development guide

#### 4. Wizard Server Split

**Shared Services:**

- Created `/wizard/services/shared/` — Reusable utilities (paths, configs)

**Dev Server Implementation:**

- `wizard/dev_server.py` — Complete FastAPI implementation (port 8766)
  - Health check
  - Notion webhooks + sync status
  - TS runtime parse/execute/state endpoints
  - Task scheduling API
  - Binder compilation API

**Dev Server Service Stubs:**

- `wizard/services/dev/notion_sync_service.py` — Webhook handler, publish mode
- `wizard/services/dev/runtime_executor.py` — Parse AST, execute blocks, state mgmt
- `wizard/services/dev/task_scheduler.py` — Organic cron scheduling
- `wizard/services/dev/binder_compiler.py` — Chapter compilation, exports

**Configuration:**

- Created `wizard/config/init_dev_config.py` — Helper to initialize dev.json (local-only)

---

## Status Summary

| Component      | Version  | Status       | Notes                                             |
| -------------- | -------- | ------------ | ------------------------------------------------- |
| **AGENTS.md**  | v1       | ✅ Complete  | Dev Server boundaries defined                     |
| **Roadmap**    | v1.0.2.0 | ✅ Complete  | 8-week phase breakdown                            |
| **App**        | v1.0.0.0 | ✅ Scaffold  | Svelte + Tailwind ready, binder UI sketched       |
| **Dev Server** | v0.1.0   | ✅ Skeleton  | Endpoints defined, stubs ready for implementation |
| **Wizard**     | v1.1.0.0 | ✅ Unchanged | Production-only, no changes                       |

---

## Next Steps (Week 2-3)

### Priority Order

1. **App File System Integration** (4 hrs)

   - Implement HostFS (file open/save dialogs)
   - SQLite schema initialization
   - Initial binder tree population

2. **Dev Server Notion Stub** (3 hrs)

   - Implement `NotionSyncService.handle_webhook()`
   - Setup notion_sync_queue table
   - Test webhook validation

3. **TS Runtime Phase 0** (5 hrs)

   - Implement markdown parser (extract runtime blocks)
   - Simple state block execution
   - Form validation + submission

4. **App Integration** (2 hrs)
   - Connect editor to Dev Server `/api/v0/runtime/parse`
   - Display parsed blocks in preview
   - Test variable interpolation

---

## Technical Decisions

### Why Split Wizard into Two Servers?

1. **Stability**: Wizard (v1.1) locked, Production-safe
2. **Experimentation**: Dev (v0.x) unstable, free to iterate
3. **Separation of Concerns**: Clear boundaries between production + experimental
4. **Deployment Flexibility**: Deploy Wizard to prod, keep Dev local

### Why Svelte for App?

- Lightweight, reactive, low-boilerplate
- Tailwind integration seamless
- Easy component composition
- Mobile-ready (future iOS/iPad)

### Why Binder Tree First?

- Core to uMarkdown UX
- Enables local organization without Notion
- Foundation for tasks + databases later

---

## Known Risks / Blockers

| Risk                    | Mitigation                                             | Timeline |
| ----------------------- | ------------------------------------------------------ | -------- |
| Notion API complexity   | Phase 1 = publish-only (read remote, write local only) | Week 3-4 |
| TS runtime robustness   | Start with forms only, no loops/functions              | Week 5-6 |
| SQLite schema evolution | Version migrations, test with seed data                | Week 2   |
| App ↔ Backend sync      | Use HTTP client library (e.g., fetch) for API calls    | Week 2-3 |

---

## Files Created/Modified

### Created

- `/app/tailwind.config.js`
- `/app/postcss.config.js`
- `/app/src/App.svelte`
- `/app/src/components/BinderNav.svelte`
- `/app/src/components/MarkdownEditor.svelte`
- `/app/src/components/Preview.svelte`
- `/wizard/services/shared/__init__.py`
- `/wizard/services/dev/notion_sync_service.py`
- `/wizard/services/dev/runtime_executor.py`
- `/wizard/services/dev/task_scheduler.py`
- `/wizard/services/dev/binder_compiler.py`
- `/wizard/services/dev/__init__.py`
- `/wizard/config/init_dev_config.py`

### Modified

- `/AGENTS.md` — Added Dev Server section (3.3.2)
- `/docs/roadmap.md` — Updated v1.0.2.0 focus + 8-week phases
- `/app/package.json` — Added Svelte + Tailwind deps
- `/app/vite.config.ts` — Added Svelte plugin
- `/app/src/main.ts` — Converted to Svelte entry point
- `/app/index.html` — Cleaned for Svelte
- `/app/README.md` — Complete feature guide
- `/wizard/dev_server.py` — Complete rewrite (FastAPI impl)

---

## Deployment Notes

### Local Development

```bash
# Terminal 1: Core TUI
source .venv/bin/activate
./bin/start_udos.sh

# Terminal 2: Wizard Server (production)
python -m wizard.server --port 8765

# Terminal 3: Dev Server (experimental)
python -m wizard.dev_server --port 8766 --debug

# Terminal 4: App
cd app && npm run tauri:dev
```

### Git Workflow

```bash
# Create feature branches for each phase
git checkout -b phase-2-notion-integration
git checkout -b phase-3-ts-runtime
git checkout -b phase-4-task-scheduler

# Commit strategy: One commit per phase completion
git commit -m "v1.0.2.0 Phase 2: Notion sync + webhook handling"
```

---

**Status:** Phase 1 Complete ✅  
**Next Phase Starts:** Week 2-3  
**Estimated Timeline:** 8 weeks to full v1.0.2.0 (Notion + TS Runtime + Tasks)
