🎯 Dev Brief: Markdown-Based Diagram & Graphic Formats Support

1. Objectives & Purpose
	•	Support embedded diagrams directly in Markdown via text-based diagram syntaxes — avoiding the need for external image files.
	•	Enable a variety of diagram types (flowcharts, sequence diagrams, class/state diagrams, charts, etc.) to be created, edited, and rendered inline in Markdown documents.
	•	Maintain portability: diagrams should render correctly in supported editors, and degrade gracefully (or fallback) if the environment doesn’t support rendering.
	•	Facilitate version control, diffing, and collaboration — because diagrams remain textual definitions rather than binary assets.
	•	Provide configuration/flexibility: allow themes, styling options, export handling (HTML, PDF, etc.), and customization for consistent project-wide styling.

⸻

2. Supported Diagram/Graphic Formats (per Typora + expansions)

According to Typora’s documentation, the following diagram types / syntaxes should be supported.  ￼

Format / Syntax / “Dialect”	Use-case / Typical Diagrams
sequence (js-sequence)	Sequence diagrams / message flows  ￼
flow (flowchart.js syntax)	Flowcharts, branching logic, process flows  ￼
mermaid (Mermaid.js)	Broad — flowcharts, sequence diagrams, Gantt charts, class diagrams, state diagrams, pie charts, requirement diagrams, git graphs, C4 diagrams, mindmaps, timelines, Sankey diagrams, XY / quadrant charts, etc.  ￼
“Inline diagram config / options” – theming, styling, curve settings, padding, alignment	Allow customizing how diagrams render (themes, flowchart curves, layout adjustments)  ￼

Note / Caveats:
	•	Diagram support is not part of standard Markdown, CommonMark, or GFM. It relies on extended Markdown-syntax + the rendering engine’s support.  ￼
	•	When exporting to certain formats (e.g. via Markdown → other format converters), diagram rendering may be lost or fail — fallback to images may be needed.  ￼

⸻

3. Requirements & Design Constraints

3.1 Core Requirements
	•	Enable authors to embed diagrams using fenced code blocks with correct language tag (e.g. mermaid, flow, ```sequence, etc.).
	•	Render those code blocks into visual diagrams in the editor preview (and on export to HTML, PDF, etc.).
	•	Support a broad set of diagram types: flowcharts, sequence, class/state, charts, timelines, mindmaps, etc.
	•	Allow configuration of global and per-document styling (themes, flowcurve style, padding, numbering, alignment) via CSS or config metadata.  ￼
	•	Fallback / degrade gracefully: if rendering is not supported (or disabled), keep the source code block intact or optionally embed a PNG/SVG fallback.

3.2 UX / Usability Constraints
	•	Diagram syntax should be as close to plain-text as possible — easy to write by hand, easy to diff in version control.
	•	For collaborative editing: diagrams as text avoids binary diffs, encourages review, simpler merges.
	•	Performance: rendering should be reasonably fast even for complex diagrams.
	•	Accessibility: diagrams should degrade gracefully for screen-readers or plain-text exports (alternatives or alt-text).

3.3 Export / Cross-Format Constraints
	•	On export to HTML, PDF, ePub, etc., diagrams should render and embed correctly. Typora supports this for its own diagrams.  ￼
	•	If the target format does not support embedded diagram rendering, provide fallback: e.g. export as image and embed, or insert warning.
	•	Respect configuration/themes — e.g. when changing the document theme, apply relevant diagram theme (colors, fonts, layout).  ￼

⸻

4. Development / Implementation Plan

4.1 Feature Toggles / Settings
	•	In preferences or config, enable/disable “Diagram Rendering”.
	•	Allow user/global config for diagram styling: theme (light/dark), flowchart curve style, numbering on sequence diagrams, padding/margins, alignment (left/center), font settings.  ￼

4.2 Parsing & Rendering Pipeline
	•	Detect fenced code blocks with recognized diagram languages (mermaid, flow, sequence, etc.).
	•	Intercept and parse the block; hand off the source to the appropriate renderer (Mermaid.js, flowchart.js, js-sequence, etc.).
	•	Embed the rendered diagram in the preview / export output — using SVG / Canvas / appropriate markup based on environment.
	•	On export: ensure that rendered diagrams are embedded (not just raw code), when output format supports it (HTML, PDF, ePub).  ￼

4.3 Fallback & Compatibility Strategies
	•	If rendering not supported (user disabled, exporting to bare Markdown, or plain-text), leave the code block as-is so content remains readable/editable.
	•	Optionally allow: “export diagrams as images” — when target format doesn’t support inline rendering, convert to PNG/SVG and embed.

4.4 Versioning & Collaboration Best Practices
	•	Because diagrams are textual definitions, they integrate cleanly with version control (diffs, merges, audits).
	•	Encourage minimal, clean syntax usage: avoid inline HTML, avoid embedding base64 images when not necessary.
	•	Document style guidelines (naming, size constraints, color themes) to ensure consistency across team docs.

⸻

5. Documentation & Style Guidelines for Users / Writers

Provide a style guide for authors using diagrams — to maintain consistency across documents:
	•	Naming conventions for diagrams (IDs, captions).
	•	Standard color/theme usage (e.g. primary colors, highlight colors).
	•	Standard sizes / max widths (especially for exported PDF or slides).
	•	Accessibility notes (e.g. alt text, textual description for complex diagrams).
	•	When to choose diagram vs. plain text vs. embedded image fallback.
	•	Version control best practices for diagrams.

Include examples, templates, and skeletons (e.g. pre-defined code block stubs).

⸻

6. Proposed Deliverables & Timeline (for a Project / Team)

Deliverable	Description
Diagram-Support Module	Implementation (parsing + rendering + export) for diagrams in Markdown workflow
Config / Settings UI	Preferences for toggling diagrams, choosing theme, export behaviours
Style Guide Document	Guidelines for authors on how to write diagrams, when to use which format, standard templates
Template Library	A small set of ready-to-use diagram templates (flowchart, class diagram, gantt, state, etc.) to boot-start writing
Export Compatibility Suite	Tests / workflows for exporting docs with diagrams to HTML, PDF, ePub; fallback handling when needed
Version Control / Collaboration Guidelines	Recommendations for using diagrams in team / repo contexts, including branching, review, diffs

Rough Timeline:
	•	Week 1: Specification + config UI drafting
	•	Week 2: Parsing / rendering integration + basic diagram support
	•	Week 3: Export + fallback handling + template library
	•	Week 4: Style guide + documentation + training for authors

⸻

7. Risks & Limitations
	•	Because diagrams rely on external JS libraries (Mermaid, flowchart.js, etc.), updates to those libraries may break layouts — need maintenance.
	•	Not all export targets may support embedding diagrams — fallback to images may bloat output and break layout.
	•	Performance issues with very large or complex diagrams (especially on export).
	•	Non-standard Markdown: may not be compatible with other Markdown tools/renderers — portability depends on tool support.

⸻

