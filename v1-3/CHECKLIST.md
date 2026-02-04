# v1.3.0 Development Checklist

**Current Focus:** Vault-first architecture + Tauri app foundation

---

## Phase 1: Vault + Editor Foundation ✅ SETUP COMPLETE

- [x] Remove Copilot model overrides (ChatGPT compatibility)
- [x] Update workspace extensions
- [x] Document v1.3 architecture
- [ ] Verify v1-3/ folder structure complete
- [ ] Create vault contract schema
- [ ] Design SQLite state schema

## Phase 2: Tauri App — Vault Picker

- [ ] First-run screen
  - [ ] "Create new vault in Documents"
  - [ ] "Open existing vault" (folder picker)
- [ ] Settings store for vault path
- [ ] Replace hardcoded paths with `vaultPath`
- [ ] File system watcher for vault changes

## Phase 3: Typo Editor Integration

- [ ] Layout: Binder (left) | Editor (center) | Preview (right)
- [ ] Typo component wrapper
- [ ] Live preview with Tailwind `prose`
- [ ] Save → update preview flow
- [ ] Bottom panel: quick actions (save/status/task capture)

## Phase 4: Task System (Markdown + SQLite)

### Parser
- [ ] Detect standard checkboxes (`- [ ]`, `- [x]`)
- [ ] Extract inline metadata (dates, priority, tags)
- [ ] Parse on file save

### SQLite Schema
- [ ] `files` table (path, mtime, hash)
- [ ] `tasks` table (id, file, line, text, status, due, start, priority, tags)
- [ ] Indexes for fast queries

### UI
- [ ] Tasks panel: Inbox / Today / Upcoming / Overdue
- [ ] Filter by tag/folder
- [ ] Click → jump to file + line in Typo

## Phase 5: Theme Engine + Export

- [ ] Baseline: Tailwind Typography `prose`
- [ ] Theme loader from `v1-3/themes/`
- [ ] Export: Markdown → HTML static site
- [ ] Theme picker UI
- [ ] Output to `VAULT/_site/<theme>/`

## Phase 6: Font Manager

- [ ] Font library UI (recommended stack)
- [ ] Download Google Fonts → `VAULT/.udos/fonts/`
- [ ] In-app activation via CSS `@font-face`
- [ ] Optional: system install (user permission)
- [ ] Export embeds/references fonts

## Phase 7: Svelte Block UI Builder (Optional)

- [ ] Layout builder → Markdown + frontmatter
- [ ] Shortcodes/fenced blocks (callouts, cards)
- [ ] Keep output as plain Markdown

---

## Testing Milestones

1. **Vault + Editor:** Open vault → edit note → save → preview
2. **Tasks:** Create tasks → view in Today panel → jump to file
3. **Export:** Generate static site → browse locally
4. **Fonts:** Download font → apply in app → see in export
5. **Wizard (later):** Host node → share vault via LAN beacon

---

## Blocked / Needs Clarification

- None currently

---

**Last Updated:** 2026-02-03
