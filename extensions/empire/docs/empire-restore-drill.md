# Empire Restore Drill (Phase 4)

Purpose
- Validate that a backup DB can be restored and remains query-safe before alpha/live data rollout.

Prerequisites
- Source DB exists at `data/empire.db`.
- Python3 and sqlite3 available.

Procedure
1. Run backup/restore sanity script:
   `cd /Users/fredbook/Code/uDOS/extensions/empire && PYTHONPATH=/Users/fredbook/Code/uDOS python3 scripts/smoke/db_backup_restore_sanity.py --db data/empire.db`
2. Confirm output contains:
   - `PASS backup=...`
   - `PASS restore=...`
   - `PASS counts=...`
   - `PASS integrity_check=ok`
3. Optional manual verify:
   `sqlite3 <restore-db-path> "PRAGMA integrity_check; SELECT count(*) FROM records;"`
4. Record the restored DB path and timestamp in release notes.

Rollback usage
- If source DB is damaged, stop API process and replace with latest validated backup:
  - copy `data/backups/<latest>.db` to `data/empire.db`
  - restart API and run `scripts/smoke/api_smoke.py`

Latest drill
- 2026-02-15: PASS using `data/backups/empire-20260215T023711Z.db` -> `data/restore-check/restore-20260215T023711Z.db`.
