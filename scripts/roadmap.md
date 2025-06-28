# 📜 uCode Command Specification & Roadmap  
**System:** uDOS Shell (`uCode.sh`)  
**Version:** Beta v1.6.1  
**Maintainer:** Otter 🦦 + Master  
**Updated:** 2025-06-28  

---

## ✅ Core Commands Overview

| Command        | Aliases       | Category     | Status       | Description |
|----------------|---------------|--------------|--------------|-------------|
| `LOG`          | `SAVE`        | Logging      | ✅ Functional | Log a new `mission`, `milestone`, or `legacy` entry |
| `UNDO`         | —             | Workflow     | 🚧 Placeholder | Stub only, no real logic implemented |
| `REDO`         | —             | Workflow     | 🚧 Placeholder | Stub only, no real logic implemented |
| `RUN`          | `GO`, `START` | Execution    | ✅ Functional | Runs a user command using `command.sh` |
| `RECENT`       | `HISTORY`     | History      | ✅ Functional | Show last 10 moves for current date |
| `DESTROY`      | —             | System       | ✅ Expanded | 5-mode DESTROY logic (identity, memory, legacy) |
| `MISSION`      | —             | State        | ✅ Functional | Displays current mission (if set) |
| `MAP`          | —             | State        | ✅ Functional | Displays current map/region info |
| `TREE`         | —             | Utility      | ✅ Functional | Generates file tree display |
| `STATS`        | —             | Dashboard    | ✅ Functional | Builds dashboard stats via `make-stats.sh` |
| `DASH`         | —             | Dashboard    | ✅ Functional | Shows full system dashboard with header/footer |
| `SYNC`         | —             | Dashboard    | ✅ Functional | Triggers dashboard sync routine |
| `LIST`         | —             | Utility      | ✅ Functional | Lists current working directory contents |
| `RESTART`      | —             | System       | ✅ Functional | Soft reload of uCode shell only |
| `REBOOT`       | —             | System       | ✅ Functional | Full rebuild and relaunch of uDOS shell |
| `BYE`          | `EXIT`, `QUIT`| System       | ✅ Enhanced | Pause system; choose action (RESTART/REBOOT/DESTROY) |
| `HELP`         | —             | Info         | ✅ Functional | Lists all commands and purpose |

---

## ⚠️ Roadmap: Planned Enhancements

### 1. 🧱 Logging & Journal Expansion

- `LOG move`: log quick inline move statements  
- Template-based logging (e.g. `/uTemplate/logs/milestone.md`)  
- `LOG` auto-summarizes `RUN` or `UNDO` calls  
- Add optional tags or labels to logs (type, urgency, owner)

---

### 2. 🔁 Workflow Commands (`UNDO` / `REDO`)

- ⏮ `UNDO`: Restore from latest move (e.g. reversed command or file snapshot)  
- 🔁 `REDO`: Reapply move state (if undone)
- Possibly integrate with session checkpointing or Git hooks

---

### 3. 📂 Dashboard Enhancements

- `SYNC`: Write JSON stats from `make-stats.sh` into dashboard.json  
- `DASH`: Add optional flags (`--full`, `--summary`, `--moves`)  
- Visual scorecards (usage, logs, goals)

---

### 4. 🌍 Map & Region

- `MAP`: Switch or load region files (`uKnowledge/map/<region>.md`)  
- Allow `MAP SET region-X` and state persistence  
- Auto update mission/map pairings

---

### 5. 🧠 Memory & History

- `RECENT 50`: Show last 50 entries  
- `HISTORY mission`: filter recent entries by type  
- Timeline log visualization or memory graphing

---

### 6. 🛠 Utility & Support

- `LIST`: add `LIST -a` or sort options  
- `HELP <CMD>`: Extended help for individual commands  
- Add error replay, logging tail or interactive error viewer

---

### 7. 🔐 Advanced Commands (future)

- `LOCK`: Mark items read-only or archive state  
- `LEGACY`: View legacy/memory timeline  
- `PULSE`: Analyze recent usage, trends, and user stats

---

## 📁 Proposed File Locations

| File                          | Purpose |
|-------------------------------|---------|
| `scripts/make-stats.sh`       | Generate usage and item stats |
| `scripts/make-log.sh`         | Unified log handler |
| `scripts/command.sh`          | Natural language to execution |
| `uMemory/logs/moves/`         | Per-day move logs |
| `uMemory/state/dashboard.json`| Live dashboard data |
| `uMemory/state/current_mission.md` | Current mission |
| `uMemory/state/identity.md`   | System identity |
| `uTemplate/logs/`             | Logging templates |
| `uTemplate/docs/`             | Specs, maps, region files |

---

## 🦦 Otter Notes

- All commands will respect `uDOS` single-process design
- Logging, error handling, dashboard sync, and state inspection must be self-contained
- Reboot and DESTROY should always route through `uCode`

---