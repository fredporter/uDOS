# uDOS Filename and File Structure Specification (Beta v1.6.1)

This standard defines all filenames and folder conventions used within uOS for logs, moves, tasks, maps, and sandbox operations.

---

## 1. Filename Format

All filenames follow this strict structure:

```
<type>-<YYYYMMDD-HHMMSSmmm>-<timezone>-<location>.md
```

### Example:

```
mission-20250623-142310361-AEST-F180327.md
```

Note: Location colons are removed for compatibility. Timezone comes before location.

### Components:

| Part          | Format                              | Example                |
| ------------- | ----------------------------------- | ---------------------- |
| Category Code | Type of file                        | mission                |
| DateTimeStamp | YYYYMMDD-HHMMSSmmm (24hr clock, milliseconds)     | 20250623-142310361     |
| Timezone      | Readable TZ (e.g. AEST, PST, UTC)        | AEST                   |
| LocationStamp | Tile Code from uMaps (no colons)         | F180327                |
| Extension     | Always .md (lowercase)              | .md                    |

Default timezone and location are derived at startup from /uMemory/state/location.txt.

---

## 2. Category Codes

| Code    | Type                |
|---------|---------------------|
| moves   | Move logs           |
| mission | Active missions     |
| legacy  | Archived records    |
| draft   | Drafted input       |
| map     | Map tile or region  |
| config  | Configuration file  |

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
