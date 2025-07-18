# Enhanced Logging Functions Library

Advanced logging utilities for uScript with structured output and categorization.

## Functions

### LOG(message)
Standard logging to console and file.

```uScript
LOG "Mission started successfully"
LOG "Processing " + file_count + " files"
```

### LOG_INFO(message)
Information-level logging with timestamp.

```uScript
LOG_INFO "System health check completed"
LOG_INFO "Found " + mission_count + " active missions"
```

### LOG_WARN(message)
Warning-level logging for potential issues.

```uScript
IF disk_space < 1000 THEN
    LOG_WARN "Low disk space: " + disk_space + "MB remaining"
END IF
```

### LOG_ERROR(message)
Error-level logging for failures.

```uScript
IF system_check() = "failed" THEN
    LOG_ERROR "System check failed - manual intervention required"
    EXIT 1
END IF
```

### LOG_DEBUG(message)
Debug-level logging for development.

```uScript
LOG_DEBUG "Variable state: mission_name=" + mission_name
LOG_DEBUG "Loop iteration: " + i + "/" + total_count
```

### LOG_MISSION(mission_id, message)
Mission-specific logging to dedicated file.

```uScript
SET mission = "data-analysis-2025"
LOG_MISSION mission, "Starting data processing phase"
LOG_MISSION mission, "Processed " + record_count + " records"
```

### LOG_MOVE(mission_id, move_id, message)
Move-specific logging for detailed tracking.

```uScript
LOG_MOVE "project-alpha", "setup-environment", "Environment configured"
LOG_MOVE "project-alpha", "setup-environment", "Dependencies installed"
```

### LOG_MILESTONE(mission_id, milestone_name)
Milestone achievement logging.

```uScript
LOG_MILESTONE "learning-uscript", "basic-syntax-mastered"
LOG_MILESTONE "automation-project", "first-script-completed"
```

### LOG_PERFORMANCE(operation, duration)
Performance tracking for optimization.

```uScript
SET start_time = NOW()
RUN "./uCode/heavy-operation.sh"
SET end_time = NOW()
LOG_PERFORMANCE "heavy-operation", time_diff(end_time, start_time)
```

### LOG_TO_FILE(filename, message)
Log to specific file.

```uScript
SET log_file = "./uMemory/logs/custom-" + TODAY() + ".log"
LOG_TO_FILE log_file, "Custom process completed successfully"
```

### LOG_STRUCTURED(level, category, data)
Structured logging with JSON-like data.

```uScript
LOG_STRUCTURED "INFO", "mission", {
    "name": mission_name,
    "status": "active",
    "progress": 75,
    "last_update": NOW()
}
```

### LOG_DASHBOARD(message)
Log messages that should appear on dashboard.

```uScript
LOG_DASHBOARD "📊 Daily report generated"
LOG_DASHBOARD "🚀 New mission launched: " + mission_name
```

## Configuration

### set_log_level(level)
Set minimum log level to display.

```uScript
set_log_level("INFO")  ' Only INFO, WARN, ERROR messages
set_log_level("DEBUG") ' All messages including DEBUG
```

### set_log_format(format)
Configure log message format.

```uScript
set_log_format("[{timestamp}] {level}: {message}")
set_log_format("{level} | {category} | {message}")
```

---

*These utilities provide comprehensive logging with automatic timestamping, categorization, and integration with uMemory storage.*
