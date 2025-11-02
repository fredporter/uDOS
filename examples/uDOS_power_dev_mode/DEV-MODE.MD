# uDOS • VS Code Power Dev Mode

This pack sets up a **fast dev loop** with tight shakedowns, minimal **dev logs** (uDOS pattern), and **.md-first** docs. It keeps a flat-feel repo, clean `.py` and `.json`, and precise **Copilot dev summaries** that are already machine-friendly.

---

## Quick start
1. Open the workspace: `uDOS.code-workspace`
2. Run tasks: **venv: create** → **venv: deps**
3. Launch **Run uDOS** or run the task **run: uDOS**
4. Run **shakedown: terminal core**
5. Tail logs with **logs: tail dev**

---

## Structure (suggested)
```
.vscode/               # VS Code config (ready)
core/                  # Python modules (uDOS logic)
sandbox/tests/         # Fast shakedowns & pytest
sandbox/logs/          # session-*.log, dev-*.log
README.MD, ROADMAP.MD  # md-first docs
uDOS.code-workspace    # open-and-go workspace
```
Keep `.env` out of logs and VCS. Put durable user prefs in `sandbox/user.json` if needed.

---

## Dev rounds (1.0.x)
- **v1.0.1 System:** HELP/STATUS/REPAIR/DASHBOARD
- **v1.0.2 File Ops:** NEW/EDIT/COPY/MOVE/SEARCH/BATCH
- **v1.0.3 Mapping:** APAC-centred grid, TIZO + zoom
- **v1.0.4 Teletext:** TELETEXT output + MAP WEB
- **v1.0.5 Web Infra:** OUTPUT START/STOP/STATUS

Use VS Code tasks:
- **round: v1.0.x checklist** to skim goals
- **shakedown: terminal core** for CLI surface
- **map: APAC center sanity** for quick visuals

---

## uDOS log format (dev & session)
**File name:** `dev-YYYYMMDD-HHMMSS_TIZO_Z{n}.log`

**Line:** `ISO8601Z | TIZO | Z{zoom} | CMD | CODE | MS | MSG`

- **Timestamp (ISO8601Z)** is UTC with `Z` (e.g., `2025-11-02T03:45:11Z`)
- **TIZO** like `AUS-BNE`
- **Zoom** integer (e.g., `Z3`)
- **CODE** 0=OK; non-zero=error
- **Never log** `.env` values. Redaction is enforced in `core/dev_logger.py`
- **Allowed:** selected, non-sensitive values from `sandbox/user.json` (see below)

Example lines:
```
2025-11-02T13:47:19Z | AUS-BNE | Z3 | STATUS --live | 0 | 128 | ok: 6 checks pass
2025-11-02T13:47:22Z | AUS-BNE | Z3 | MAP VIEW 480 270 | 0 | 412 | ascii: 129k chars
2025-11-02T13:47:40Z | AUS-BNE | Z2 | OUTPUT START teletext | 1 | 987 | port 8080 busy
```

---

## Dev logger (ready)
Use `core/dev_logger.py`:
```python
from core.dev_logger import dev_log_path, dev_log

path = dev_log_path(tizo="AUS-BNE", zoom=3)
with open(path, "a", encoding="utf-8") as fp:
    dev_log(fp, "AUS-BNE", 3, "STATUS --live", 0, 128, "ok: 6 checks pass", with_user_ctx=True)
```
- **with_user_ctx=True** appends a tiny `sandbox/user.json` context (safe keys only).
- **Secrets redaction**: env-like strings and keys such as `*token`, `*secret`, `*apikey` are redacted automatically.
- **.env is never read** by the logger.

---

## Copilot dev summaries (precise, single line)
Goal: **ONE** line per dev session, **uDOS log format**, easy to grep.

- Snippet: type `udos-summary` in Copilot Chat to get the prompt.
- Command/task: `copilot: stamp summary line` runs `python -m core.copilot_summary "<summary>"`

Example (Copilot or you run):
```bash
python -m core.copilot_summary "core/maps/grid.py: add APAC-centre wrap; improve cell refs" 45 0 AUS-BNE 3
# Produces:
# 2025-11-02T03:45:11Z | AUS-BNE | Z3 | DEV SUMMARY | 0 | 45 | core/maps/grid.py: add APAC-centre wrap; improve cell refs | ctx: workspace=default theme=FOUNDATION tizo=AUS-BNE zoom=3
```
**Rules**
- Always **ISO8601Z** timestamps (automatic).
- Never include `.env` values or secrets; logger redacts aggressively.
- You **may** include non-sensitive `sandbox/user.json` keys (workspace/theme/tizo/zoom).

---

## Terminal shakedowns
Core:
```bash
printf "STATUS --live
" | python uDOS.py
printf "REPAIR auto
" | python uDOS.py
printf "TREE
" | python uDOS.py
printf "DASHBOARD CLI
" | python uDOS.py
printf "OUTPUT STATUS
" | python uDOS.py
```
Mapping + APAC:
```bash
printf "MAP STATUS
MAP VIEW 480 270
MAP CITIES
" | python uDOS.py
printf "MAP LOCATE BNE
MAP CELL H120
MAP NAVIGATE SYD TYO
" | python uDOS.py
```

---

## Tests (pytest)
- `sandbox/tests/test_session_minimal.py` validates core events appear in the last session log.
- `sandbox/tests/test_map_surface.py` smokes a small `MAP VIEW` when `uDOS.py` is present.

Run the **Pytest** launch config or:
```bash
pytest -q sandbox/tests
```

---

## Env & system vars
- Runtime vars prefixed **UDOS_** (e.g., `UDOS_TIZO`, `UDOS_ZOOM`, `UDOS_PORT_*`)
- **Time** is UTC in logs; UI can show local time (Australia/Brisbane)
- **Never** log raw env values
- Durable prefs may live in `sandbox/user.json`

That’s it—open the workspace, run the tasks, and ship rounds fast.
