# uDOS Backup System Configuration v1.4.0
# Centralized backup settings for enhanced root backup system

# ═══════════════════════════════════════════════════════════════════════
# BACKUP LOCATIONS
# ═══════════════════════════════════════════════════════════════════════

# Primary backup location (root backup folder)
BACKUP_ROOT_DIR="$UDOS_ROOT/backup"

# Legacy backup locations (deprecated - will be migrated)
BACKUP_LEGACY_DIRS=(
    "wizard/backup"
    "sorcerer/backup"
    "imp/backup"
    "ghost/backup"
    "drone/backup"
    "tomb/backup"
    "uMEMORY/backups"
)

# ═══════════════════════════════════════════════════════════════════════
# BACKUP RETENTION POLICY
# ═══════════════════════════════════════════════════════════════════════

# Keep counts by backup type
BACKUP_RETENTION_MANUAL=3
BACKUP_RETENTION_DAILY=2
BACKUP_RETENTION_SESSION=1
BACKUP_RETENTION_STARTUP=1
BACKUP_RETENTION_EXIT=1
BACKUP_RETENTION_EMERGENCY=5

# Maximum total backups before forced cleanup
BACKUP_MAX_TOTAL=20

# Maximum backup age in days before auto-cleanup
BACKUP_MAX_AGE_DAYS=30

# ═══════════════════════════════════════════════════════════════════════
# BACKUP INCLUSION/EXCLUSION
# ═══════════════════════════════════════════════════════════════════════

# Default paths to include in backups
BACKUP_INCLUDE_PATHS=(
    "uMEMORY"
    "sandbox"
    "permissions"
    "uSCRIPT/user"
    "extensions"
)

# Paths to exclude from backups
BACKUP_EXCLUDE_PATTERNS=(
    "backup/*"
    "*.log"
    ".DS_Store"
    "cache/*"
    "tmp/*"
    "uMEMORY/backups"
    "uMEMORY/viewports"
    ".git"
    "node_modules"
    "__pycache__"
    "*.pyc"
    ".pytest_cache"
    "dist/*"
    "build/*"
)

# ═══════════════════════════════════════════════════════════════════════
# ENCRYPTION SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# Encryption method
BACKUP_ENCRYPTION_METHOD="aes-256-cbc"
BACKUP_ENCRYPTION_ITER="100000"

# Password source
BACKUP_PASSWORD_FILE="$UDOS_ROOT/sandbox/user.md"

# ═══════════════════════════════════════════════════════════════════════
# AUTOMATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# Auto-backup triggers
BACKUP_AUTO_ON_STARTUP=true
BACKUP_AUTO_ON_EXIT=true
BACKUP_AUTO_ON_SESSION_START=true

# Daily backup time (24h format)
BACKUP_DAILY_TIME="02:00"

# Emergency backup conditions
BACKUP_EMERGENCY_ON_ERROR=true
BACKUP_EMERGENCY_ON_CRASH=true

# ═══════════════════════════════════════════════════════════════════════
# NOTIFICATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# Backup completion notifications
BACKUP_NOTIFY_SUCCESS=true
BACKUP_NOTIFY_ERROR=true
BACKUP_NOTIFY_CLEANUP=false

# Notification methods
BACKUP_NOTIFY_CONSOLE=true
BACKUP_NOTIFY_LOG=true

# ═══════════════════════════════════════════════════════════════════════
# INTEGRATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# Integration with existing uDOS components
BACKUP_INTEGRATE_UMEMORY=true
BACKUP_INTEGRATE_TRASH=true
BACKUP_INTEGRATE_LOGGING=true

# Backup hooks for other scripts
BACKUP_HOOK_PRE_BACKUP=""
BACKUP_HOOK_POST_BACKUP=""
BACKUP_HOOK_PRE_RESTORE=""
BACKUP_HOOK_POST_RESTORE=""

# ═══════════════════════════════════════════════════════════════════════
# MIGRATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# Auto-migrate legacy backups to root folder
BACKUP_MIGRATE_LEGACY=true

# Preserve legacy backup metadata during migration
BACKUP_PRESERVE_LEGACY_META=true

# Remove legacy backup directories after migration
BACKUP_CLEANUP_LEGACY_DIRS=false

# ═══════════════════════════════════════════════════════════════════════
# PERFORMANCE SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# Compression level (1-9, higher = better compression but slower)
BACKUP_COMPRESSION_LEVEL=6

# Parallel processing for large backups
BACKUP_PARALLEL_JOBS=2

# Maximum backup size before warning (in bytes)
BACKUP_MAX_SIZE_WARN=$((500 * 1024 * 1024))  # 500MB

# ═══════════════════════════════════════════════════════════════════════
# EXPORT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

# Export all settings for use by backup scripts
export BACKUP_ROOT_DIR BACKUP_RETENTION_MANUAL BACKUP_RETENTION_DAILY
export BACKUP_RETENTION_SESSION BACKUP_RETENTION_STARTUP BACKUP_RETENTION_EXIT
export BACKUP_MAX_TOTAL BACKUP_MAX_AGE_DAYS BACKUP_ENCRYPTION_METHOD
export BACKUP_PASSWORD_FILE BACKUP_AUTO_ON_STARTUP BACKUP_AUTO_ON_EXIT
export BACKUP_MIGRATE_LEGACY BACKUP_COMPRESSION_LEVEL
