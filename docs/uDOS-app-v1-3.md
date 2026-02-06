Yep — your current /app/ is already 90% pointed in the right direction: it’s a Svelte + Tailwind + Tauri shell with renderers (including Marp + TypoEditor + FontManager + UCodeRenderer) and some file/db utilities. The refactor is mostly about drawing hard boundaries and making “vault outside the repo” a first-class concept.

Below is a refactor plan that turns /app/ into a Mac Tauri control plane hosting Svelte “universal components”, while keeping everything else runnable in a browser/offline (static bundles) when a server isn’t needed.

⸻

What those references are useful for
	•	mcndt/obsidian-svelte-template: good patterns for Obsidian-flavoured UI built in Svelte (especially how to think in Obsidian-ish primitives and styling expectations), even if you’re not building an Obsidian plugin.  
	•	obsidian-sveltekit-blog: proven pattern for “Obsidian vault as content source → web output with SvelteKit”; useful for your publish lane and content pipeline ideas.  
	•	kepano/obsidian-minimal (+ docs): a goldmine for design tokens, typography sensibilities, and what Obsidian users expect from a clean writing UI; also note there’s a separate “publish” variant concept you can mimic.  

⸻

Target architecture for /app/ (Mac Tauri control plane)

The firm boundaries
	1.	Tauri App UI (Mac-only control plane)
	•	hosts Svelte components
	•	manages local filesystem permissions + “choose vault folder”
	•	manages local SQLite (tasks/workflow + indexes)
	•	font manager (install/download, activate for app + export)
	•	Typo editor as default authoring surface
	2.	Browser/offline lane (no server needed)
	•	static _site/ output (themes) opened via file:// or served by any dumb static server
	•	optional “portal” pages for browsing and read-only UX
	3.	Wizard lane (server needed)
	•	only for LAN/beacon sharing, permissions, contributions, discovery, syncing
	•	if you want beacon networks, you still need a server somewhere (node or desktop acting as node)

So yes: you can make the app UI live in Tauri, and keep publishing/browsing static “no server needed” for single-device/offline. The moment you want other devices on the network, Wizard (or an embedded server mode) is necessary.

⸻

Refactor plan (practical steps)

Phase 0 — Stabilise current /app/

Goal: make the current app runnable with a real vault path and no assumptions about being inside /udos.
	1.	Add “Vault Path” concept everywhere
	•	Default vault path for Mac: ~/Documents/uDOS Vault (create on first run)
	•	Allow picking any folder (Tauri dialog)
	•	Store the chosen path in app settings (Tauri store)
	2.	Make the vault external by design
	•	The repo is code
	•	The vault is user data
	•	Treat it like Obsidian does: folder on disk, app points to it
	3.	Define a minimal Vault Contract v1 (in the vault root)
	•	.udos/ folder for app state (optional)
	•	_site/ for HTML exports
	•	05_DATA/sqlite/udos.db (or .udos/state.db if you prefer)

Phase 1 — Turn Svelte UI into a reusable component library

Goal: “universal components” without binding yourself to SvelteKit.

Create a library folder inside /app/ first (keep it simple), then you can monorepo later:

app/src/lib-ui/
  components/
    Editor/
    Binder/
    Tasks/
    ThemePicker/
    FontManager/
  styles/
    obsidian-tokens.css
    prose.css
  index.ts

What becomes “universal”
	•	Typo editor wrapper component
	•	Markdown renderer component (prose + theme pack wrapper)
	•	Task list + filters
	•	Vault picker + tree view (binder)
	•	FontManager UI + state

Later, you can publish lib-ui as a package, but don’t block on tooling.

Phase 2 — Typo as the default editor (first-class)

You already have TypoEditor.svelte. Promote it to the centre of the app:
	•	Left: Binder/tree (vault navigation)
	•	Centre: Typo editor (md)
	•	Right: Preview (Tailwind prose renderer + theme selection)
	•	Bottom: task quick-add / status bar (you already have TypoBottomBar)

Key refactor: editor works directly on vault files, not in-memory demo content.

Scope detail: [app/docs/TYPO-INTEGRATION-SCOPE.md](app/docs/TYPO-INTEGRATION-SCOPE.md)

Phase 3 — Obsidian-style tasks/workflow (local-first)

Two-layer model (strong + simple):
	1.	Markdown truth: tasks live in notes as checkboxes + frontmatter tags
	2.	SQLite index: app maintains a task index for fast queries

Flow:
	•	On file save, parse tasks (checkbox lines) + metadata
	•	Update SQLite tables: tasks, task_locations, task_tags, task_status, task_schedule
	•	UI shows “Obsidian-ish tasks view” (Today / Upcoming / Tagged / By project)

This gives Obsidian vibes without being stuck in plugin-land.

Phase 4 — Font Manager (Mac app advantage)

Scope it as:
	•	“Recommended font packs” (your defaults)
	•	“Install from Google Fonts” (download, store in app-managed cache)
	•	“Activate for app” (use the downloaded fonts in CSS)
	•	Optional: “Install system-wide” (Mac permissions; keep it explicit)

Keep the font system aligned with your existing Tailwind Prose approach:
	•	Body font
	•	Heading font
	•	Monospace/code font
	•	Emoji font fallback

Phase 5 — Svelte UI builder (block UI builder)

Don’t build a whole Notion clone. Make a builder for page layouts that outputs Markdown + frontmatter or JSON blocks that render to Markdown.

Practical v1:
	•	A “Layout Canvas” that composes:
	•	hero, callout, cards, image, code, quote
	•	Output:
	•	Markdown with fenced blocks / shortcodes
	•	plus a layout: field in frontmatter

This lets you ship “universal components” as publishable layouts.

Phase 6 — Publishing: MD → HTML Themes

This is the “no server needed” lane:
	•	App runs an export: vault/_site/<theme>/...
	•	Can open locally in browser
	•	Can be copied to a USB stick, or served by Wizard later

This is also where the SvelteKit blog demo is conceptually useful as inspiration, but you can do it without SvelteKit if you keep it static-first.  

⸻

Where SvelteKit fits now (if at all)

SvelteKit should not be required for the Mac app UI.
Tauri already hosts Svelte in a WebView.

Use SvelteKit only when:
	•	you’re building a web app version of the control plane
	•	you want SSR/routing for public web publishing
	•	you’re doing the WordPress lane frontend

For the Mac app, keep it: Svelte (Vite) + Tauri.

⸻

Wizard server: how it plugs in without derailing the app
	•	Mac app = personal control plane + authoring + local exports
	•	Wizard node = network brain + sharing + permissions + contributions

The Mac app can optionally:
	•	“Run as a node” (embedded Wizard mode)
	•	or “Connect to a node” (pair to a beacon host)

But don’t force it in v1.3: treat networking as an “attachable lane”.

⸻

Immediate, concrete actions in your current /app/

Based on what’s already present in the folder you uploaded:
	1.	Add a Vault Picker first-run screen (store chosen path)
	2.	Replace demo renderers with real file open/save
	3.	Implement tasks_indexer:
	•	parse markdown on save → update SQLite
	4.	Make Preview always use Tailwind prose as baseline (your non-negotiable)
	5.	Add “Export Site” button:
	•	MD → HTML → theme pack wrapper → write to vault/_site/

⸻

If you want, I can also produce a migration note that maps your current components (TypoEditor, FontManager, MarpRenderer, UCodeRenderer) into the new lib-ui module layout, plus a proposed SQLite schema for tasks/workflow. (The legacy staging MIGRATION doc is archived under `docs/.archive/2026-02/root-legacy/`.)
