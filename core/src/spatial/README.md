# core/src/spatial

v1.3 Spatial core contracts.

Files:
- `schema.sql` — SQLite tables for anchors/locids/places and file tagging.
- `types.ts` — TypeScript interfaces.
- `parse.ts` — Canonical parsers + frontmatter normalisation.
- `anchors.default.json` — Launch-ready anchor registry (minimal, expandable).
- `places.default.json` — Tracked default place catalog with optional seed-depth metadata.

Recommended string format for frontmatter + APIs:

`<ANCHOR_ID>:<SPACE>:<LOCID>[:D<depth>][:I<instance>]`

Examples:
- `EARTH:SUR:L305-DA11`
- `EARTH:UDN:L305-DA11`
- `EARTH:SUB:L305-DA11:D7`
- `BODY:MARS:SUR:L610-AB22`
- `GAME:skyrim:SUB:L402-CC18:Iwinterhold`
