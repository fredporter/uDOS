Local-first Markdown workstation with three “superpowers” layered on top of a Typo-style editor

    1.	Parsing/transforms (image→text, image→ASCII/teletext/SVG, text→table.md)
    2.	Presentation + form modes (Marp + “Typeform-style” paginated forms)
    3.	Light programmable Markdown (ucode / uPY subset) that can render safely

Here’s the cleanest way to structure this so it’s shippable, App-Store-safe-ish, and doesn’t blow up your repo or runtime complexity.

⸻

1. Product architecture for the Mac app

A. Typo Editor remains the “Shell”
• Homepage = Typo editor/reader + file browser (iCloud + local)
• Everything else is a mode invoked from:
• context menu (right click)
• command palette
• “Convert…” toolbar

Key rule: editor stays fast and predictable. Transforms run as separate tasks with clear output files.

⸻

B. File access + iCloud (no internal memory filesystem)

You’re right: for the commercial app, treat files as real files:
• Use macOS file open/save panels everywhere
• Store app state only as:
• recent files
• user preferences
• cached thumbnails/previews

For iCloud:
• Use a dedicated app container folder (Documents)
• Allow user-chosen iCloud folders via bookmark-scoped access (if you’re sandboxed)

⸻

2. Parsing/transforms: design it as a “Converter Pipeline”

Don’t bake these into editor code. Make a converter framework:

Converter types you listed
• image → text
• image → ASCII / teletext
• image → SVG
• text → table.md

Recommended UX pattern
• User selects input (image / text / selection / pasted content)
• Picks target converter
• A side panel shows:
• settings
• preview (optional)
• output location (same folder by default)
• Output becomes a file next to the source:
• photo.md
• photo.teletext.txt
• photo.svg
• notes.table.md

This keeps it “file-native” and works beautifully with iCloud syncing.

⸻

3. Emoji rules (Noto + GitHub :emoji:)

Goals
• Use Noto Emoji for consistent rendering (and pixel editor previews)
• Display “app emojis” rather than system variation
• Use GitHub :emoji: tokens in source

Practical approach
• Internally, store Markdown as:
• :smile: form (GitHub style)
• Rendering pipeline: 1. parse Markdown 2. replace :emoji: tokens with emoji glyph OR custom image sprites (your call) 3. render with Noto Emoji available

If you want pixel editor integration:
Prefer mapping :emoji: → a standard emoji codepoint first, then render to pixels using Noto Emoji. It gives predictable output and avoids managing a massive sprite sheet library.

⸻

4. Fonts: Heading vs body separation + macOS system fonts

You want:
• Tailwind/Typo “core 3 fonts” remain
• Plus system font selection
• Plus separate font choice for headings vs body

Implement it as document-level style settings
• Default styles stored as:
• App preference (global)
• Optional per-document frontmatter override

Example frontmatter:

---

font:
body: "SF Pro Text"
heading: "SF Pro Display"
mono: "SF Mono"
emoji: github

---

Rendering then becomes deterministic across machines.

⸻

5. ucode / uPY inside Markdown safely

You’re on the right track: keep it inside fenced code blocks, but treat it as templating, not “run arbitrary code”.

Recommendation: two execution tiers 1. Safe templating (default ON)
• Variables
• if/then
• simple functions (date, format, choose)
• no filesystem, no network, no shell 2. Privileged local execution (default OFF, explicit user enable)
• allowed for power users
• clearly labelled
• still sandboxed with permission prompts

Markdown convention

Use fenced blocks like:

```ucode
set title = "Event Brief"
if user.plan == "paid" then set cta = "Buy now"
```

Output model:
• ucode does not mutate files silently
• It renders a view (presentation/form) or emits a derived output file

⸻

6. Marp slides + “Typeform-style” forms

Treat these as renderers that consume:
• Markdown
• frontmatter config
• optional ucode variables

A. Marp mode
• You can support standard Marp frontmatter and themes
• Add your own theme layer (“gtx-form styled”)

B. Form mode

I’d define a spec like:
• Each “page” is a section separated by --- or # Question
• Fields defined with a small syntax (or frontmatter blocks)
• ucode can decide conditional visibility of pages/questions

Example pattern:

---

mode: form
theme: gtx-form

---

# Your name

[input name="full_name" required]

# Do you need catering?

[radio name="catering" options="yes,no"]

```ucode
if catering == "yes" then show "Catering details"

Output:
- saved JSON response bundle next to the `.md`
- optionally export a PDF

---

## 7) The “uCode Reader” distribution question

You asked: if `.md` contains `ucode`, do we need to distribute a reader? Or render on a webpage?

Here are the clean options, in order of least headache:

### Option A (best): **Pre-render on export**
- When sharing, user exports:
  - “Rendered Markdown” (plain `.md` without `ucode`)
  - “Static HTML” (fully rendered)
  - “PDF” (slides/forms)

This avoids requiring anyone else to run anything.

### Option B: **Lightweight open-source renderer**
- Ship a tiny `ucode-render` CLI (from `ucode-core` public repo)
- Anyone can render:
  - `.md + ucode → html/pdf`
- Great for devs and collaborators

### Option C: **Hosted web renderer (later)**
- You can offer a “Render to share link” feature
- But that breaks your “no API reliance” and raises privacy expectations

Given your offline-first goal: **Option A + Option B** is the best pairing.

---

## 8) Ollama role in the Mac app (local-only)

You want Ollama to:
- parse HTML → clean Markdown
- parse pasted text/raw docs → structured Markdown
- help with formatting + conversion prompts
- assist transforms (image→SVG/ASCII/etc.) where appropriate

### Recommended boundaries
- Use Ollama for:
  - cleanup
  - restructuring
  - summarising
  - consistent Markdown formatting
- Don’t rely on Ollama for:
  - deterministic transforms where you want reproducibility (tables, strict syntax)

So:
- `text → table.md` should be mostly deterministic (parser-based), *with optional* “improve formatting” via Ollama.

---

## 9) What I’d lock for v1 (so you can ship)

If the goal is a logical commercial launch, the v1 scope should be:

**Core**
- Typo editor + iCloud + file dialogs
- Heading/body font separation + system fonts
- GitHub `:emoji:` rendering + Noto Emoji + pixel preview

**Modes**
- Slides (Marp) with a couple themes
- Tables `.md` support (import/export)
- Converters:
  - image→text
  - text→table.md
  - (pick ONE of image→ASCII/teletext/SVG for v1, not all three)

**Programmable Markdown**
- `ucode` safe templating only (variables + if/then)
- Export to static HTML/PDF (pre-render)

Everything else can become:
- v1.1 / v1.2
- or Wizard-server territory

---

If you want, next I can turn this into two concrete artefacts (Markdown format, ready to drop into your repos):
1) **Mac App v1 Spec** (features, UX flows, file formats, export rules)
2) **`ucode` in Markdown mini-spec** (grammar, safety model, rendering rules, export behaviour)

Got it — that “format / CLEAN” feature is a huge value add, and you can ship it without turning the app into a weird internal database, as long as you treat it as a file-native batch operation with a very explicit preview + output plan.

Here’s a clean way to design it.

⸻

CLEAN feature: Folder smart scan + dedupe + combine

What the user wants (in plain terms)

Given a folder (a “binder”) full of Markdown (and maybe related files), the app can:
	•	detect duplicates / near-duplicates
	•	prefer the most recent / most complete versions
	•	merge related material into a single clean Markdown file
	•	keep the originals intact (or optionally archive them)

Output is one file: e.g. Binder CLEAN.md

⸻

1) Modes and safety rules

Two operations (keep them separate)
	1.	SCAN (read-only)
	•	Finds duplicates, conflicts, clusters, candidates for merge
	•	Builds an index and a proposed plan
	•	Does not change files
	2.	CLEAN (write)
	•	Produces a new file (and optional “archive” folder)
	•	Never overwrites original files by default

This makes it App Store / customer safe and avoids “where did my work go?” panic.

⸻

2) What “duplicates” means (use layered detection)

You’ll get the best results by combining 4 signals:

A. Exact duplicates
	•	Same file hash (byte-for-byte)
	•	Easiest and most reliable

B. Structural duplicates (Markdown-aware)
	•	Ignore whitespace
	•	Normalise line endings
	•	Strip frontmatter (optional)
	•	Compare normalised content hash

C. Near duplicates (fuzzy)
	•	Similarity score based on:
	•	headings overlap
	•	paragraph similarity
	•	common keyphrases
	•	Use thresholds, eg:
	•	95%+ = “likely duplicate”
	•	80–95% = “revision / related”

D. Semantic relatedness (topic clustering)
	•	Cluster files into groups like:
	•	“Product”
	•	“Wizard”
	•	“Launch plan”
	•	This enables combining related notes into structured sections

Because your app already has local Ollama for formatting/parsing, you can optionally use it for clustering + section naming, but keep dedupe logic deterministic.

⸻

3) What “combine useful and updated information” means

Think of it as a merge strategy with user-configurable rules.

Default merge rules (sensible)
	•	Prefer newer files when two blocks conflict
	•	Keep both when conflicts are meaningful
	•	Combine additions chronologically unless the user chooses “topic mode”
	•	Preserve original timestamps and source filenames as references

Output structure (suggested)

---
cleaned_from: "Binder Name"
created: 2026-01-14
mode: "topic"  # or "chronological"
sources: 42
duplicates_removed: 7
---

# Binder CLEAN

## Summary
- Key outcomes…
- Open questions…

## Topics
### Topic: X
- Merged notes…

### Topic: Y
- Merged notes…

## Source index
- 2026-01-10 — file-a.md
- 2026-01-11 — file-b.md

This is human-readable, audit-friendly, and doesn’t require an internal database.

⸻

4) UX flow that won’t frustrate people

Step 1: Select binder folder
	•	Options:
	•	include subfolders ✅
	•	include file types: .md, .txt, .html, .json (optional)

Step 2: Scan results screen (preview)

Show:
	•	Duplicates (exact)
	•	Likely revisions (near dup clusters)
	•	Related clusters (topic groups)
	•	Orphans (not related to anything)

Each cluster has a dropdown:
	•	keep latest only
	•	keep all (append)
	•	merge (smart)
	•	ignore

Step 3: Choose output
	•	“Create Binder CLEAN.md in this folder”
	•	Optional: “Archive originals to /Binder Archive YYYY-MM-DD/”
	•	Optional: “Create Binder CLEAN.assets/ for copied images”

Step 4: Run + produce outputs
	•	A single output .md
	•	Optional archive folder
	•	Optional report file:
	•	Binder CLEAN.report.md

⸻

5) Handling non-Markdown files and attachments

Common binder reality: images, PDFs, random snippets.

Rules
	•	If an .md references images:
	•	keep links intact
	•	optionally copy used assets into CLEAN.assets/
	•	If OCR/image→text is enabled:
	•	treat extracted text as a source block with metadata, eg:

> Source: scan-01.png (OCR)
> Confidence: 0.83


	•	For HTML:
	•	convert to Markdown first (your existing feature)
	•	then include in merge

⸻

6) Where local Ollama helps (without making it flaky)

Use Ollama for:
	•	topic clustering labels (“Marketing Plan”, “Research”, “Decisions”)
	•	summarising the combined binder into a “Summary” section
	•	cleaning formatting and consistent heading hierarchy

Don’t use Ollama for:
	•	deciding which version is the “truth” when two files conflict
	•	file identity / dedupe (use hashes + deterministic similarity)

This keeps CLEAN reliable and repeatable.

⸻

7) The feature name and mental model

In the UI, call it:
	•	CLEAN Binder
	•	Subtitle: “Scan, dedupe, merge, and export one tidy Markdown file”

In menus:
	•	File → CLEAN Folder…
	•	Right-click folder → CLEAN Binder
	•	Command Palette → CLEAN: Scan Binder, CLEAN: Create Output

⸻

8) Recommended v1 scope (so it ships)

Ship v1 CLEAN with:
	•	exact duplicates
	•	normalised duplicates
	•	near-duplicate clustering
	•	merge into one file (chronological mode)
	•	optional archive + report

Then v1.1:
	•	topic clustering + summaries
	•	attachment consolidation
	•	“decision extraction” (pull lines under ## Decisions)

⸻

CLEAN Binder Specification

Purpose

CLEAN Binder is a file-native batch operation in the uMarkdown App that scans a folder (binder) and optionally its subfolders to detect duplicates, cluster related content, and produce a single clean Markdown output file. The operation is safe by default (read-only scan first) and never overwrites originals unless explicitly requested.

⸻

Design Principles
	•	File-native: Operates on real files and folders (local or iCloud). No internal memory filesystem.
	•	Safe-by-default: Scan/preview first, explicit write step second.
	•	Deterministic core: Hashing and structural similarity for dedupe; optional AI only for clustering/summaries.
	•	Auditability: Output includes provenance, timestamps, and a source index.
	•	Offline-first: Works without network or external APIs.

⸻

Supported Inputs
	•	Markdown: .md
	•	Text: .txt
	•	HTML: .html (converted to Markdown before processing)
	•	Optional (if enabled): images for OCR (.png, .jpg, .jpeg, .webp)

Excluded by default:
	•	Binary formats (PDF, DOCX) unless converted first

⸻

Operations

1) SCAN (Read-only)

Produces a preview of findings without modifying files.

Outputs (preview UI):
	•	Exact duplicates
	•	Structural duplicates (normalised Markdown)
	•	Near-duplicate clusters
	•	Related topic clusters
	•	Orphans (unrelated or low-similarity files)

2) CLEAN (Write)

Creates new output files only.

Outputs:
	•	Binder CLEAN.md (primary output)
	•	Optional: Binder CLEAN.report.md
	•	Optional: Binder Archive YYYY-MM-DD/ (originals copied, never deleted)
	•	Optional: Binder CLEAN.assets/ (copied images/assets)

⸻

Duplicate Detection Layers

A. Exact Duplicates
	•	Byte-for-byte hash match (SHA-256)
	•	Resolution: keep one (latest mtime by default)

B. Structural Duplicates (Markdown-aware)
	•	Normalisation steps:
	•	Trim whitespace
	•	Normalise line endings
	•	Optional: remove frontmatter
	•	Compare normalised hash

C. Near Duplicates (Fuzzy)
	•	Signals:
	•	Heading overlap
	•	Paragraph similarity
	•	Keyphrase overlap
	•	Thresholds:
	•	≥95%: Likely duplicate
	•	80–94%: Revision/related

D. Topic Relatedness (Optional AI)
	•	Clusters files by topic for merge structuring
	•	AI used only for labels and ordering, not truth resolution

⸻

Merge Strategies

(Default selectable per cluster)
	•	Keep latest only (by modified time)
	•	Keep all (append)
	•	Smart merge (combine sections, prefer newer conflicts)
	•	Ignore (exclude from output)

Conflict handling:
	•	Prefer newer blocks when conflicts detected
	•	Preserve both when conflict is ambiguous
	•	Annotate merged blocks with source metadata

⸻

Output Structure (Default)

---
cleaned_from: "<Binder Name>"
created: <ISO-8601>
mode: chronological | topic
sources: <count>
duplicates_removed: <count>
---

# <Binder Name> CLEAN

## Summary
<Optional generated summary>

## Content
<Chronological or topic-organised merged content>

## Source Index
- 2026-01-10 — notes-a.md
- 2026-01-11 — notes-b.md


⸻

Assets & Attachments
	•	Preserve original relative links when possible
	•	Optional asset consolidation to CLEAN.assets/
	•	OCR-derived text annotated with confidence and source

Example:

> Source: scan-01.png (OCR)
> Confidence: 0.83


⸻

UI Flow
	1.	Select Binder
	•	Options: include subfolders, file types
	2.	Scan Preview
	•	Lists duplicates, clusters, orphans
	•	Per-cluster merge strategy selector
	3.	Output Options
	•	Output filename/location
	•	Archive originals (on/off)
	•	Create report (on/off)
	4.	Run CLEAN
	•	Progress indicator
	•	Open output on completion

⸻

Settings & Defaults
	•	Include subfolders: ON
	•	Output mode: Chronological
	•	Archive originals: OFF
	•	AI clustering/summaries: OFF

⸻

Error Handling
	•	Read errors logged to report
	•	Files that fail parsing are skipped and listed
	•	CLEAN aborts safely on write permission errors

⸻

Versioning
	•	Spec version: 1.0
	•	Compatible with uMarkdown App v1.x



Recommended division of labour

CLI (ucode-core) owns the mechanics
Responsibilities
	•	Scan folder/subfolders
	•	Detect exact + structural duplicates
	•	Create archives (Binder Archive YYYY-MM-DD/)
	•	Copy/normalise assets (CLEAN.assets/ if you want)
	•	Produce a machine-readable report (.json) + a human report (.md)
	•	Optionally emit a stitched draft that is purely deterministic (chronological concatenation + provenance)

Why
It’s repeatable, scriptable, safe, and works on Alpine / terminal everywhere.

Mac app (uMarkdown) owns the editorial “compilation”
Responsibilities
	•	Take the CLI report + the source files (or the stitched draft)
	•	Build a Draft and optionally a Final combined document
	•	Use local Ollama only for:
	•	topic clustering (optional)
	•	section headings
	•	formatting cleanup
	•	summary + table-of-contents
	•	Provide a review UI (“accept / reject merges”, reorder sections, resolve conflicts)
	•	Export outputs:
	•	Binder CLEAN.draft.md
	•	Binder CLEAN.final.md (after user review)

Why
This is where judgement and presentation matter, and the user needs a human-friendly workflow.

⸻

A really practical workflow

Step 1: CLI runs a “binder scan”

User triggers from app, but the app is just a wrapper.

Outputs:
	•	binder.scan.json (clusters, duplicates, file metadata)
	•	binder.report.md (human readable)
	•	Optional: binder.stitched.md (deterministic chronological draft)

Step 2: App opens a “Compilation workspace”
	•	Left: clusters / duplicates / conflicts (from JSON)
	•	Middle: preview of stitched draft
	•	Right: “Final document outline” the user can rearrange

Step 3: App generates draft/final
	•	Draft = deterministic + light formatting
	•	Final = (optional) topic structure + summaries + polished headings

Important: originals never change unless the user explicitly archives/moves them.

⸻

Key design decision: “Draft” vs “Final”

To avoid trust issues, make it explicit:
	•	Draft: “Everything, organised, nothing lost”
	•	Final: “Best version, deduped, summarised, tidy”

Users love this because Draft is safety, Final is usefulness.

⸻

What the CLI command could look like (conceptually)
	•	ucode clean scan <folder> --subfolders --out <folder>
	•	ucode clean archive <folder> --plan binder.scan.json
	•	ucode clean stitch <folder> --plan binder.scan.json --mode chrono

Then the app does:
	•	Compile Draft (from stitched or from sources via plan)
	•	Compile Final (optionally with local model assist)
```
