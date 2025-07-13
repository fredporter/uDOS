# Date and Time Utilities Library

Collection of date/time functions for uScript automation and logging.

## Functions

### NOW()
Get current timestamp in ISO format.

```uScript
SET current_time = NOW()
LOG "Script executed at: " + current_time
CREATE MOVE "daily-tasks/timestamp-" + current_time
```

### TODAY()
Get today's date in YYYY-MM-DD format.

```uScript
SET today = TODAY()
SET log_file = "./uMemory/logs/log-" + today + ".md"
LOG "Creating daily log: " + log_file
```

### TOMORROW()
Get tomorrow's date for scheduling.

```uScript
SET next_review = TOMORROW()
LOG "Next review scheduled for: " + next_review
CREATE MILESTONE "project/review-" + next_review
```

### YESTERDAY()
Get yesterday's date for historical tracking.

```uScript
SET yesterday_log = "./uMemory/logs/log-" + YESTERDAY() + ".md"
IF file_exists(yesterday_log) THEN
    LOG "Previous day's log exists"
END IF
```

### date_add(date, days)
Add days to a date.

```uScript
SET deadline = date_add(TODAY(), 14)
LOG "Project deadline: " + deadline
CREATE MILESTONE "project/deadline-" + deadline
```

### date_diff(date1, date2)
Calculate difference between dates in days.

```uScript
SET mission_start = "2025-07-01"
SET days_elapsed = date_diff(TODAY(), mission_start)
LOG "Mission running for " + days_elapsed + " days"
```

### format_time(timestamp, format)
Format a timestamp with custom format.

```uScript
SET readable_time = format_time(NOW(), "YYYY-MM-DD HH:mm:ss")
LOG "Current time: " + readable_time
```

### is_weekend()
Check if today is weekend.

```uScript
IF is_weekend() THEN
    LOG "Weekend mode - no scheduled tasks"
ELSE
    RUN "./uScript/automation/daily-cleanup.md"
END IF
```

### get_week_number()
Get current week number of the year.

```uScript
SET week = get_week_number()
SET weekly_report = "./uMemory/reports/week-" + week + ".md"
LOG "Generating weekly report: " + weekly_report
```

### time_since(timestamp)
Get human-readable time elapsed since timestamp.

```uScript
SET last_backup = "2025-07-10T10:00:00Z"
SET elapsed = time_since(last_backup)
LOG "Last backup was " + elapsed + " ago"
```

---

*These utilities provide comprehensive date/time handling for mission tracking, scheduling, and automation workflows.*
