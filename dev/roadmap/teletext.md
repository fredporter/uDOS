📺 MULTI-COLOUR ANSI / TELETEXT ART STYLE GUIDE

A production brief for creating consistent, modern teletext-inspired visual content

⸻

1.0 — Overview & Intent

This style guide defines the visual language, technical constraints, and production workflow for creating multi-colour ANSI / teletext-mode artwork, including:
	•	static illustrations
	•	diagrams and UI art
	•	title cards and page layouts
	•	teletext-style “screens”
	•	photo-to-ANSI conversions
	•	video-to-teletext motion sequences

The intent is to create a cohesive, retro-digital visual identity echoing 1980s/1990s Teletext, Ceefax, and ANSI BBS art, while maintaining:
	•	readability
	•	colour consistency
	•	grid integrity
	•	stylistic cohesion across all deliverables

⸻

2.0 — Teletext / ANSI Technical Constraints

2.1 Grid & Layout
	•	Fixed-width grid (monospace only)
	•	Standard working grids:
	•	40 × 24 (classic Teletext MODE 7)
	•	80 × 25 (ANSI terminal resolution)
	•	100 × 30 (extended modern canvas; optional)
	•	All artwork must align cleanly to a character cell grid.
	•	No anti-aliasing — all pixels are characters.

2.2 Character Options

Allowed character categories:
	•	Block elements: █ ▓ ▒ ░
	•	Box drawing: │ ─ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
	•	Teletext mosaic blocks: ▟ ▙ ▛ ▜ ▐ ▌ ▖ ▗ ▘ ▙ (as available)
	•	ASCII symbols: # * + = @ . :
	•	Text characters for titles and overlays

Prohibited:
	•	Diagonal strokes made by / or \ unless deliberately stylistic
	•	Unicode characters not supported by standard ANSI or mode 7 sets

2.3 Colour Palette (Core)

Use the canonical 8-colour Teletext palette, plus bright variants where allowed:

Standard colours:
	•	Black
	•	Red
	•	Green
	•	Yellow
	•	Blue
	•	Magenta
	•	Cyan
	•	White

Brights:
	•	Bright Red, Bright Green, Bright Yellow, etc. (ANSI-supported)

2.4 Colour Use Rules
	•	Maximum 3–5 colours per frame/page for legibility
	•	High-contrast backgrounds only:
	•	Bright text on dark background
	•	Dark text on bright background
	•	No gradients (unless simulated with block characters)
	•	No semi-transparency

⸻

3.0 — Core Aesthetic Principles

3.1 Bold, Blocky Geometry
	•	Shapes are built using block elements (█ ▓ ▒ ░)
	•	Aim for chunky silhouettes, clean edges
	•	“Pixel-perfect” by character cell

3.2 Modular Panels & Layouts
	•	Teletext style uses boxed panels with strong borders
	•	Titles inside brackets [ LIKE THIS ]
	•	Clear sectioning via horizontal bars, e.g.:

───────────────────────────────────



3.3 Typography
	•	Use ALL CAPS for page titles
	•	Use bracketed headers: [ TITLE ]
	•	No proportional spacing or mixed fonts
	•	Keep text density low (Teletext readability constraint)

3.4 Motion (for video teletext output)
	•	Frame rate: 6–12 FPS
	•	No smooth interpolation — pixel-step movement only
	•	Stick to “block wipe”, “scroll”, or “flash” transitions

⸻

4.0 — Layout Templates

4.1 Title Card Template

────────────────────────────────────────
[ TITLE GOES HERE ]
────────────────────────────────────────
█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█
█▒ MAIN IMAGE AREA (BLOCK MOSAIC) ▒█
█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█
────────────────────────────────────────
Page 1/1 • Service Name • © 2025

4.2 Infographic Box

┌────────────────────────┐
│ [ KEY INFO ]           │
│                        │
│ ████  DATA POINT 1     │
│ ██    DATA POINT 2     │
│ ███████████████████    │
└────────────────────────┘

4.3 Multi-panel Teletext Screen

┌──────────────┬───────────────┐
│ [ NEWS ]     │ [ WEATHER ]    │
│ Text block    │ Graphic block  │
│ …             │ …              │
├──────────────┼───────────────┤
│ [ SPORTS ]   │ [ WHAT’S ON ]  │
│ …             │ …              │
└──────────────┴───────────────┘


⸻

5.0 — Converting Photos to Teletext Art

Workflow summary

Step 1 — Source Selection
	•	Choose well-lit, high-contrast images
	•	Subjects must be bold and recognisable at low resolution
	•	Avoid cluttered backgrounds

Step 2 — Downscaling
	•	Reduce to Teletext or ANSI grid:
	•	Teletext: 40×24 or 40×40
	•	ANSI: 80×25 or 100×40
	•	Hard downscale (nearest neighbour) — no smoothing

Step 3 — Posterisation
	•	Reduce to 6–8 colours maximum
	•	Snap colours to Teletext palette
	•	Increase local contrast manually if needed

Step 4 — Character Mapping
Choose shading characters based on intensity:

Brightness	Char
90–100%	█
70–90%	▓
40–70%	▒
10–40%	░
0–10%

	•	For outlines, optionally use box-drawing or ASCII chars.

Step 5 — Manual Cleanup
	•	Fix face outlines
	•	Adjust eye placement
	•	Fix shading blotches
	•	Remove noise

Step 6 — Colour Encoding
	•	Apply ANSI escape sequences:
\x1b[31m etc.
	•	Or Teletext colour codes:
default: double-height allowed only in some systems

Step 7 — Output
	•	.ans file (ANSI)
	•	.txt (Teletext style without control codes)
	•	or rendered frames for animation

⸻

6.0 — Converting Video Into Teletext Motion

Workflow summary

1. Frame extraction
	•	Extract at 6–12 FPS (never full-speed)
	•	Maintain consistent aspect ratio

2. Resize & posterise each frame
	•	Same rules as photos
	•	Keep colours consistent across all frames

3. Characterise each frame
	•	Map shading characters (█ ▓ ▒ ░)
	•	Reduce detail to emphasise silhouette
	•	Use block transitions instead of pixel fades

4. Encode as sequence
Options:
	•	Animated .ans sequence (cursor-control timing)
	•	Teletext-style updating frames
	•	Export as actual video (MP4) but keep text grid intact
	•	Ideal size: 1080p with sharp nearest-neighbour scaling
	•	Never anti-alias

5. Motion Constraints
	•	Only “teletext-style” effects allowed:
	•	slide-in
	•	wipe
	•	flicker
	•	jump-cut
	•	scroll
	•	No smooth tweening or easing

⸻

7.0 — House Style Summary

Do:
	•	Use bold block shapes
	•	Use high contrast
	•	Centre titles inside [ ]
	•	Use limited colours
	•	Maintain grid discipline
	•	Keep everything monospaced
	•	Embrace chunky graphics

Don’t:
	•	Use gradients or photo-realism
	•	Use diagonal ASCII unless essential
	•	Use too many colours
	•	Deform the character grid
	•	Blend characters (no half pixels)

⸻

8.0 — Optional Enhancements
	•	Glow frames using bright ANSI
	•	Double-height Teletext headers
	•	Border “banners” for section separators
	•	Pattern backgrounds (░░░░ or ▒▒▒▒ regions)
