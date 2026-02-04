# MIGRATION — Mac Tauri App (/app/) → v1.3 Control Plane

Drop this file into the repo at: `v1-3/MIGRATION.md`

This plan refactors the existing **Mac Tauri app** (`/app/`) into the v1.3 model:

- **Vault outside the repo** (Obsidian-compatible folder in `~/Documents` by default)
- **Typo** is the default Markdown editor
- **Tailwind Typography (`prose`)** is the baseline renderer
- **Tasks/workflow** = Markdown truth + SQLite index (fast queries)
- **Font Manager** = app-managed fonts + optional system install
- **Svelte UI components** are packaged as a reusable library (universal components)
- **Wizard networking** remains a separate lane (LAN/beacon), not required for single-device use

> Guiding rule: **Publishing/browsing is static-first; control-plane is app UI.**
> If there’s no sharing/networking, you should be able to use the app with **no server**.

---

## 0) Pre-flight decisions (locked for v1.3)

### Vault default location (Mac)
- Default path: `~/Documents/uDOS Vault`
- User can choose any folder via a Tauri folder picker.
- Store selection in app settings.

### Source of truth
- Content: Markdown + assets in the vault.
- State/index: SQLite stored alongside vault state, recommended:
  - `VAULT/.udos/state.db` (preferred; avoids clutter), OR
  - `VAULT/05_DATA/sqlite/udos.db` (matches the vault contract).

### App responsibilities vs Wizard
- App: personal authoring + local tasks + local exports + fonts
- Wizard: LAN/beacon sharing, permissions, contribution intake, multi-device portal

---

## 1) Step-by-step refactor plan

### Phase 1 — Introduce Vault Picker + “external vault” model
**Goal:** app opens a folder on disk as the vault (like Obsidian), not a repo-relative path.

1. Add first-run screen:
   - “Create new vault in Documents” (default)
   - “Open existing vault”
2. Persist the chosen vault path using a settings store.
3. Replace all hard-coded paths with a single `vaultPath` source.

**Deliverable:** app can load + save Markdown files in the chosen vault folder.

### Phase 2 — Promote Typo to the default editor surface
**Goal:** central editing loop feels like Obsidian + Typo, with live preview.

Layout suggestion (Obsidian-ish):
- Left: Binder/tree (vault navigation)
- Centre: Typo editor (Markdown)
- Right: Preview (Tailwind `prose` + theme selection)
- Bottom: quick actions (save/status/task capture)

**Deliverable:** open any note from binder → edit → save → preview updates.

### Phase 3 — Create `lib-ui` (Svelte universal components)
**Goal:** keep UI composable; avoid framework lock-in beyond Svelte itself.

Create:
```txt
app/src/lib-ui/
  components/
    Binder/
    Editor/
    Preview/
    Tasks/
    ThemePicker/
    FontManager/
  styles/
    obsidian-tokens.css
    prose.css
  index.ts
```

Move existing UI pieces into `lib-ui/components/*`, leaving only page-level wiring under `app/src/routes` (or your equivalent).

**Deliverable:** UI components are reusable by:
- Tauri app UI
- optional web control plane (later)
- optional Wizard portal UI (later)

### Phase 4 — Tasks/workflow: Markdown truth + SQLite index
**Goal:** Obsidian-style task UX without relying on Obsidian plugins.

#### Truth format (Markdown)
Support standard checkboxes:
- `- [ ] task`
- `- [x] done`

Optional inline metadata (v0, non-breaking):
- due date: `📅 2026-02-10`
- start date: `🛫 2026-02-07`
- priority: `⏫` / `⏬`
- tags: `#tag`

#### Indexing strategy
- Parse tasks on file save.
- Update SQLite tables for fast queries:
  - Today / Upcoming / Overdue
  - By tag / project folder
  - By status

#### Minimal SQLite schema (v0)
```sql
CREATE TABLE IF NOT EXISTS files (
  path TEXT PRIMARY KEY,
  mtime INTEGER NOT NULL,
  hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  file_path TEXT NOT NULL,
  line INTEGER NOT NULL,
  text TEXT NOT NULL,
  status TEXT NOT NULL,          -- open|done
  due TEXT,                      -- YYYY-MM-DD
  start TEXT,                    -- YYYY-MM-DD
  priority INTEGER,              -- -2..+2
  tags TEXT,                     -- JSON array string
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY(file_path) REFERENCES files(path)
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_due ON tasks(status, due);
CREATE INDEX IF NOT EXISTS idx_tasks_file ON tasks(file_path);
```

**Deliverable:** Tasks panel shows:
- Inbox (all open)
- Today
- Upcoming
- Overdue
- By tag
Clicking a task jumps to the file + line in Typo.

### Phase 5 — Theme packs + MD → HTML export (static-first)
**Goal:** compete with “Publish” without requiring a server.

Implement:
- Render current note/binder to `VAULT/_site/<theme>/...`
- Themes live in `v1-3/themes/` (contract already scaffolded)
- Baseline: Tailwind Typography `prose`
- Additional: medium / NES / Teletext / C64 wrappers as optional themes

**Deliverable:** “Export” button generates a browseable static site.

### Phase 6 — Font Manager (app-managed + optional system install)
**Goal:** ship a “great default typography stack” and allow optional installs.

Functions:
- Show recommended fonts (your curated stack)
- Download Google Fonts into:
  - `VAULT/.udos/fonts/` (portable with vault), OR
  - `~/Library/Application Support/uDOS/fonts/`
- Activate fonts in-app via CSS `@font-face`
- Optional: system install step (explicit user action + permissions)

**Deliverable:** user can switch body/heading/code fonts; export uses same fonts (embedded or referenced).

### Phase 7 — Svelte “Block UI Builder” (optional v1.3.x)
**Goal:** compose page layouts without inventing a proprietary document model.

Approach:
- Builder outputs **Markdown + frontmatter** (or JSON blocks that render to Markdown)
- Keep it “layout metadata”, not “content storage”
- Example:
  - frontmatter: `layout: article` / `layout: landing`
  - shortcodes/fenced blocks for callouts/cards

**Deliverable:** user can assemble a page layout and still end up with plain Markdown.

---

## 2) How this fits with Wizard and networking

The Mac app should support two modes:

### Personal mode (no server needed)
- Works entirely on local vault folder
- Exports static HTML bundles
- Tasks/workflow local
- Fonts local

### Node mode (Wizard lane)
- Either connect to a Wizard node (LAN/beacon), or
- “Host as node” (later): run Wizard services locally and expose portal to other devices

**Important:** Beacon sharing + permissions + contribution merging still requires a server process *somewhere* (Wizard). The app can host that later, but it shouldn’t be required for v1.3 personal mode.

---

## 3) Suggested code boundaries inside `/app/`

### `app/src/lib/` (platform services)
- vault FS access (Tauri commands)
- sqlite wrapper
- task indexer
- export pipeline
- font download/install helpers

### `app/src/lib-ui/` (universal components)
- Binder tree
- Typo editor wrapper
- Preview renderer (prose + theme shell)
- Tasks UI
- Theme picker
- Font manager UI

### `app/src/pages/` (composition only)
- app shell (left/centre/right layout)
- settings screens
- onboarding (vault picker)

---

## 4) If you want to “drop in” v1.3 assets now

- Copy `v1-3/themes/` into your repo and wire “Export” to use them.
- Add a vault picker and start treating vault as external.
- Add SQLite schema and tasks indexer.
- Promote Typo as default editor.

That’s the fastest path to a working v1.3 control plane.

---

## 5) Notes from your uploaded `/app/` zip

I didn’t rewrite your code here, but the scaffold assumes you already have components like:
- Typo editor
- font manager
- markdown renderers (including slides)

If you want, paste the `/app/` folder tree (or let me inspect more deeply) and I’ll produce a **precise file-by-file move map** (old path → new path) for the `lib-ui` extraction.

---
