# memory/bank/spatial

Spatial config & seeds for the v1.3 grid system.

- `anchors.json`: Anchor registry (Earth, bodies, catalogues) used by the renderer and mission scheduler when seeding the spatial SQLite (`.udos/state.db` or `05_DATA/sqlite/udos.db`).
- `places.json`: Canonical place reference catalog that pairs `placeRef` strings (anchor + space + locId) with friendly labels/tags. Imported into the spatial index to seed `places` + `file_place_tags`.
- Add your own anchors here before running `node/mission-scheduler` or the renderer so the control plane can show them via `/api/renderer/spatial/anchors`.
