# uOS Filename and File Structure Specification (v1.6)

This standard defines all filenames and folder conventions used within uOS for logs, moves, tasks, maps, and sandbox operations.

---

## 1. Filename Format

All filenames follow this strict structure:

```
<uXYZ>-<DATETIMESTAMP>-<LOCATIONSTAMP>.md
```

### Example:

```
uMLG-20250622-142310456-P10-F18-03-27.md
```

### Components:

| Part          | Format                              | Example                |
| ------------- | ----------------------------------- | ---------------------- |
| Category Code | Always starts with "u" + 2 CAPS/NUM | uML, uIO, uCF, uSP     |
| DateTimeStamp | YYYYMMDD-HHMMSSSSS-TZCODE           | 20250622-142310456-P10 |
| LocationStamp | Tile Code from uMaps                | F18:03:27              |
| Extension     | Always .md (lowercase)              | .md                    |

---

## 2. Category Codes

| Code | Type                   |
| ---- | ---------------------- |
| uML  | Move Log               |
| uIO  | Input/Output pair      |
| uMP  | Map Definition or Tile |
| uCF  | Configuration file     |
| uTA  | Task/Action            |
| uMS  | Memory/Snapshot        |
| uSL  | System Log             |
| uMR  | uMap Draft/Revision    |

Note: This is a recommended convention, but not enforced. In some cases, may be omitted from the filename altogether.

---

## 3. Folder Structure

```
/uOS/
├── sandbox/             # Temporary scratchpad files
│   ├── uIO-*.md         # Input/output sessions
│   ├── uMD-*.md         # uMap draft content
│   └── uTA-*.md         # Task/action files
│
├── uMemory/             # Long-term system memory
│   ├── logs/            # System logs
│   │   └── uSL-*.md
│   ├── errors/          # Error logs
│   │   └── uSL-*.md
│   ├── moves/           # Recorded state transitions
│   │   └── uML-*.md
│   ├── milestones/      # Achievements and goals
│   │   └── *.md
│   ├── missions/        # Larger tasks or operations
│   │   └── *.md
│   └── legacy/          # Archived or migrated records
│       └── *.md
│
├── uKnowledge/          # Reference material and specs
│   └── general/         # Freeform documentation
│       └── *.md
│
├── uMaps/               # Cartographic logic and geography
│   ├── layers/          # Layer definitions and overlays
│   └── tiles/           # Physical and logical tiles
```

---

## Location Stamp Format (uMap Tile Convention)

Tiles follow a multi-resolution grid system:

- Base tiles: `Xnn` where X is column A–Z, and nn is row 01–60
  - Example: `F18` (e.g. coastal France)
- Submaps: `F18:zz` where `zz` is sub-tile within that 120×60 block
- Deep detail: `F18:zz:xy` — sub-sub coordinate system

Each base cell (120×60) represents \~3° lat × 3° lon. Zoom layers allow increasing precision down to \~0.05°/cell or better.

---

This structure ensures consistent naming, cross-compatibility with uMap addressing, and clean archival across all uOS interfaces.

All filenames are safe for sorting, transfer, compression, and long-term storage.

End of spec.

