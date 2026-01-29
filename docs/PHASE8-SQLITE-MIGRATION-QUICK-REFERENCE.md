# Phase 8: SQLite Migration - Quick Reference

**Status:** ✅ Complete (2026-01-29)  
**Scope:** Location data migration (JSON → SQLite)  
**Threshold:** 500KB or 1000 records

---

## Quick Commands

```bash
# Check migration status
MIGRATE

# Check if migration is needed
MIGRATE check

# Show detailed status
MIGRATE status

# Perform migration (with backup)
MIGRATE perform

# Show help
MIGRATE help
```

---

## How It Works

### Automatic (When Needed)
```
LocationService initialized
  → Check file size / record count
  → If > 500KB or > 1000 records
    → Create backup automatically
    → Migrate to SQLite
    → Log results
```

### Manual
```
MIGRATE perform
  → Check if migration is needed
  → Create backup (configurable)
  → Migrate all data
  → Verify integrity
  → Show results
```

---

## Files Involved

| File | Purpose |
|------|---------|
| `core/services/location_migration_service.py` | Migration logic |
| `core/location_service.py` | Auto-detection & backend selection |
| `core/commands/migrate_handler.py` | MIGRATE command |
| `memory/bank/locations/locations.json` | JSON backend |
| `memory/bank/locations/locations.db` | SQLite backend |
| `memory/bank/locations/backups/` | Backup directory |

---

## Data Safety

✅ **Automatic Backup**
- Before migration, JSON files are backed up
- Backup location: `memory/bank/locations/backups/locations_YYYYMMDD_HHMMSS.json`

✅ **Rollback**
- Delete `.db` file to revert to JSON: `rm memory/bank/locations/locations.db`
- Restart uDOS to use JSON backend again

✅ **Verification**
- All data is verified during migration
- Foreign key integrity checked
- Connection counts validated

---

## Performance

| Operation | JSON (60KB) | SQLite (500KB) |
|-----------|------------|----------------|
| Load time | <10ms | ~50ms |
| Lookup by ID | O(1) | O(log n) |
| Search by type | O(n) | O(log n) with index |
| Memory usage | 2x file | Minimal |

**Recommendation:** Migrate when JSON reaches 500KB for better performance.

---

## Troubleshooting

### "Migration not needed"
- JSON is under 500KB and < 1000 records
- This is normal, no action needed

### Migration fails
```bash
# Check logs
tail -f memory/logs/session-commands-*.log

# Verify JSON is valid
python -m json.tool memory/bank/locations/locations.json

# Check disk space
df -h
```

### Want to use SQLite before threshold
```bash
# Manually trigger migration
MIGRATE perform

# Or programmatically
from core.services.location_migration_service import LocationMigrator
migrator = LocationMigrator()
stats = migrator.perform_migration(backup=True)
print(f"Migrated: {stats['locations_migrated']} locations")
```

### Want to revert to JSON
```bash
# Delete SQLite database
rm memory/bank/locations/locations.db

# Restart uDOS (will use JSON)
```

---

## Implementation Details

### Schema (SQLite)
- **locations** — Main location data with indexes
- **timezones** — Timezone reference data
- **connections** — Location relationships
- **user_additions** — User-contributed locations
- **tiles** — Tile content for locations

### Thresholds
```python
SIZE_THRESHOLD_KB = 500    # File size
RECORD_THRESHOLD = 1000    # Record count
```

### API (Same for Both Backends)
```python
service = LocationService()

# Works with JSON or SQLite transparently
location = service.get_location("L300-BJ10")
all_locations = service.get_all_locations()
stats = service.get_statistics()  # Now includes "backend" field
```

---

## Log Examples

### Successful Migration
```
[LOCAL] Location data exceeds threshold: File size 512.3KB exceeds 500KB threshold
[LOCAL] Auto-triggering SQLite migration...
[LOCAL] Backup created: memory/bank/locations/backups/locations_20260129_143022.json
[LOCAL] SQLite schema created successfully
[LOCAL] Migrated 42 timezones to SQLite
[LOCAL] Migrated 1203 locations to SQLite
[LOCAL] Migration completed successfully: 1203 locations, 42 timezones, 3547 connections
```

### Using SQLite Backend
```
[LOCAL] LocationMigrator initialized (data_dir=memory/bank/locations)
[LOCAL] Using SQLite backend: memory/bank/locations/locations.db
[LOCAL] Connected to SQLite database: 1203 locations
```

---

## Testing

```bash
# Run migration tests
pytest core/tests/test_location_migration.py -v

# Test migration service directly
python -m core.services.location_migration_service

# Test via TUI
./start_udos.sh
> MIGRATE
> MIGRATE status
> MIGRATE perform
```

---

## Related Docs

- [PHASE8-SQLITE-MIGRATION.md](PHASE8-SQLITE-MIGRATION.md) — Full documentation
- [ADR-0004-data-layer-architecture.md](decisions/ADR-0004-data-layer-architecture.md) — Architecture decision
- [IMPLEMENTATION-COMPLETE-2026-01-29.md](IMPLEMENTATION-COMPLETE-2026-01-29.md) — Phase status

---

**Last Updated:** 2026-01-29  
**Version:** Phase 8 Complete

