# Daily System Cleanup Automation

Automated maintenance script for uDOS system health and organization.

---
title: "Daily System Cleanup"
type: "automation"
schedule: "daily"
author: "uDOS System"
version: "1.0.0"
---

## 🧹 Daily Cleanup Tasks

```uScript
' Daily System Cleanup - Automated Maintenance
SET cleanup_date = TODAY()
SET log_file = "./uMemory/logs/cleanup-" + cleanup_date + ".md"

LOG_INFO "Starting daily cleanup for " + cleanup_date

' 1. Clean temporary files
LOG_INFO "Cleaning temporary files..."
SET temp_count = count_files("./uMemory/sandbox/*.tmp")
IF temp_count > 0 THEN
    RUN "find ./uMemory/sandbox -name '*.tmp' -mtime +1 -delete"
    LOG_INFO "Removed " + temp_count + " temporary files"
ELSE
    LOG_INFO "No temporary files to clean"
END IF

' 2. Archive old logs
LOG_INFO "Archiving old logs..."
SET old_logs = count_files("./uMemory/logs/*.log")
FOR EACH log_file IN get_files("./uMemory/logs/*.log")
    IF file_age(log_file) > 30 THEN
        SET archive_path = "./uMemory/logs/archive/" + cleanup_date + "/"
        create_directory(archive_path)
        move_file(log_file, archive_path)
        LOG_INFO "Archived old log: " + log_file
    END IF
NEXT log_file

' 3. Update mission status
LOG_INFO "Updating mission status..."
SET active_missions = count_files("./uMemory/missions/*.md")
LOG_INFO "Currently tracking " + active_missions + " missions"

FOR EACH mission_file IN get_files("./uMemory/missions/*.md")
    SET last_update = get_file_modified_date(mission_file)
    SET days_since_update = date_diff(TODAY(), last_update)
    
    IF days_since_update > 14 THEN
        LOG_WARN "Mission inactive for " + days_since_update + " days: " + mission_file
        ' Flag for review but don't auto-archive
        SET review_flag = "./uMemory/missions/review-needed/" + get_filename(mission_file)
        copy_file(mission_file, review_flag)
    END IF
NEXT mission_file

' 4. Generate daily statistics
LOG_INFO "Generating daily statistics..."
SET stats = {
    "date": cleanup_date,
    "missions_active": active_missions,
    "moves_today": count_files("./uMemory/moves/*" + cleanup_date + "*.md"),
    "milestones_reached": count_files("./uMemory/milestones/*" + cleanup_date + "*.md"),
    "temp_files_cleaned": temp_count,
    "system_health": system_status()
}

SET stats_file = "./uMemory/reports/daily-stats-" + cleanup_date + ".json"
write_json_file(stats_file, stats)
LOG_INFO "Daily statistics saved to " + stats_file

' 5. Backup critical data
LOG_INFO "Creating backup of critical data..."
SET backup_dir = "./uMemory/backups/" + cleanup_date
create_directory(backup_dir)

' Backup recent missions and moves
RUN "cp -r ./uMemory/missions " + backup_dir + "/missions"
RUN "cp -r ./uMemory/moves " + backup_dir + "/moves"
RUN "cp -r ./uMemory/milestones " + backup_dir + "/milestones"

LOG_INFO "Backup created: " + backup_dir

' 6. System health check
LOG_INFO "Running system health check..."
SET health_result = system_health_check()

IF health_result = "healthy" THEN
    LOG_INFO "✅ System health check passed"
    LOG_DASHBOARD "🟢 System healthy - daily cleanup completed"
ELSE
    LOG_WARN "⚠️ System health issues detected"
    LOG_DASHBOARD "🟡 System needs attention - check logs"
    RUN "./uCode/check.sh all"
END IF

' 7. Update dashboard
LOG_INFO "Updating system dashboard..."
RUN "./uCode/dash.sh"

' Final cleanup summary
SET cleanup_summary = {
    "timestamp": NOW(),
    "temp_files_removed": temp_count,
    "logs_archived": count_files("./uMemory/logs/archive/" + cleanup_date + "/*"),
    "backup_created": backup_dir,
    "system_status": health_result
}

LOG_TO_FILE log_file, "Daily cleanup completed: " + JSON.stringify(cleanup_summary)
LOG_INFO "Daily cleanup completed successfully"
LOG_DASHBOARD "🧹 Daily cleanup completed - system optimized"
```

## 🔧 Configuration

- **Schedule**: Runs daily at system startup
- **Duration**: ~2-5 minutes depending on data volume
- **Dependencies**: System utilities, file operations
- **Logging**: Detailed logs saved to `uMemory/logs/cleanup-{date}.md`

## 🎯 Benefits

- Maintains system performance
- Prevents disk space issues
- Keeps mission data organized
- Provides daily health monitoring
- Creates automatic backups

---

*This automation ensures uDOS runs efficiently with regular maintenance and health monitoring.*
