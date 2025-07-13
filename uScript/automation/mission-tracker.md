# Mission Progress Tracker Automation

Automated monitoring and reporting for mission progress and milestone achievement.

---
title: "Mission Progress Tracker"
type: "automation"
schedule: "hourly"
author: "uDOS System"
version: "1.0.0"
---

## 📊 Mission Tracking Automation

```uScript
' Mission Progress Tracker - Automated Monitoring
SET tracker_timestamp = NOW()
SET tracker_date = TODAY()

LOG_INFO "Starting mission progress tracking at " + tracker_timestamp

' 1. Scan all active missions
LOG_INFO "Scanning active missions..."
SET mission_count = 0
SET stalled_missions = 0
SET active_missions = 0

FOR EACH mission_file IN get_files("./uMemory/missions/*.md")
    SET mission_count = mission_count + 1
    SET mission_name = get_mission_name(mission_file)
    SET mission_id = get_mission_id(mission_file)
    
    ' Analyze mission activity
    SET last_move = get_latest_move(mission_id)
    SET moves_today = count_files("./uMemory/moves/" + mission_id + "*" + tracker_date + "*.md")
    SET total_moves = count_files("./uMemory/moves/" + mission_id + "*.md")
    SET milestones = count_files("./uMemory/milestones/" + mission_id + "*.md")
    
    ' Calculate mission health
    SET days_since_activity = 0
    IF last_move != "" THEN
        SET days_since_activity = date_diff(tracker_date, get_file_date(last_move))
    END IF
    
    ' Mission status classification
    IF days_since_activity = 0 THEN
        SET mission_status = "active"
        SET active_missions = active_missions + 1
        LOG_INFO "✅ " + mission_name + " - Active (moves today: " + moves_today + ")"
    ELSIF days_since_activity <= 3 THEN
        SET mission_status = "recent"
        LOG_INFO "📅 " + mission_name + " - Recent activity (" + days_since_activity + " days ago)"
    ELSIF days_since_activity <= 7 THEN
        SET mission_status = "idle"
        LOG_WARN "😴 " + mission_name + " - Idle (" + days_since_activity + " days ago)"
    ELSE
        SET mission_status = "stalled"
        SET stalled_missions = stalled_missions + 1
        LOG_WARN "⚠️ " + mission_name + " - Stalled (" + days_since_activity + " days ago)"
    END IF
    
    ' Log mission progress
    LOG_MISSION mission_id, "Progress check: " + total_moves + " moves, " + milestones + " milestones"
    
    ' Calculate progress percentage
    SET estimated_completion = get_mission_target_moves(mission_file)
    SET progress_percent = 0
    IF estimated_completion > 0 THEN
        SET progress_percent = (total_moves / estimated_completion) * 100
        IF progress_percent > 100 THEN
            SET progress_percent = 100
        END IF
    END IF
    
    ' Update mission progress data
    SET progress_data = {
        "mission_id": mission_id,
        "mission_name": mission_name,
        "status": mission_status,
        "total_moves": total_moves,
        "moves_today": moves_today,
        "milestones": milestones,
        "progress_percent": progress_percent,
        "days_since_activity": days_since_activity,
        "last_updated": tracker_timestamp
    }
    
    SET progress_file = "./uMemory/progress/" + mission_id + "-progress.json"
    write_json_file(progress_file, progress_data)
    
NEXT mission_file

' 2. Generate overall progress summary
LOG_INFO "Generating progress summary..."
SET overall_summary = {
    "timestamp": tracker_timestamp,
    "total_missions": mission_count,
    "active_missions": active_missions,
    "stalled_missions": stalled_missions,
    "completion_rate": (active_missions / mission_count) * 100,
    "system_health": "good"
}

IF stalled_missions > (mission_count / 2) THEN
    SET overall_summary.system_health = "attention_needed"
    LOG_WARN "High number of stalled missions detected"
END IF

' 3. Check for milestone opportunities
LOG_INFO "Checking for milestone opportunities..."
FOR EACH mission_file IN get_files("./uMemory/missions/*.md")
    SET mission_id = get_mission_id(mission_file)
    SET moves_count = count_files("./uMemory/moves/" + mission_id + "*.md")
    
    ' Suggest milestones based on move count
    IF moves_count MOD 10 = 0 AND moves_count > 0 THEN
        SET milestone_suggestion = mission_id + "/progress-milestone-" + moves_count
        LOG_INFO "💡 Milestone suggestion for " + mission_id + ": " + milestone_suggestion
        
        ' Auto-create progress milestone if configured
        IF get_mission_setting(mission_file, "auto_milestones") = "true" THEN
            CREATE MILESTONE milestone_suggestion
            LOG_MILESTONE mission_id, "progress-milestone-" + moves_count
        END IF
    END IF
NEXT mission_file

' 4. Update dashboard with progress
LOG_INFO "Updating progress dashboard..."
SET dashboard_update = {
    "section": "mission_progress",
    "data": overall_summary,
    "updated": tracker_timestamp
}

write_json_file("./uMemory/dashboard/mission-progress.json", dashboard_update)

' 5. Generate alerts for attention-needed missions
IF stalled_missions > 0 THEN
    LOG_DASHBOARD "⚠️ " + stalled_missions + " missions need attention"
    
    ' Create review reminder
    SET review_file = "./uMemory/reviews/mission-review-" + tracker_date + ".md"
    SET review_content = "# Mission Review Required\n\n"
    SET review_content = review_content + "Generated: " + tracker_timestamp + "\n\n"
    SET review_content = review_content + "## Stalled Missions (" + stalled_missions + ")\n\n"
    
    FOR EACH mission_file IN get_files("./uMemory/missions/*.md")
        SET mission_id = get_mission_id(mission_file)
        SET last_move = get_latest_move(mission_id)
        SET days_since = date_diff(tracker_date, get_file_date(last_move))
        
        IF days_since > 7 THEN
            SET review_content = review_content + "- **" + get_mission_name(mission_file) + "** ("
            SET review_content = review_content + days_since + " days inactive)\n"
        END IF
    NEXT mission_file
    
    write_file(review_file, review_content)
    LOG_INFO "Review file created: " + review_file
ELSE
    LOG_DASHBOARD "✅ All missions active or recently updated"
END IF

' 6. Performance tracking
SET tracking_duration = time_diff(NOW(), tracker_timestamp)
LOG_PERFORMANCE "mission_tracking", tracking_duration

LOG_INFO "Mission progress tracking completed in " + tracking_duration + "ms"
LOG_DASHBOARD "📊 Progress tracking updated - " + active_missions + "/" + mission_count + " missions active"
```

## 🔧 Configuration

- **Schedule**: Runs hourly during active hours
- **Duration**: ~30-60 seconds depending on mission count
- **Dependencies**: Mission files, move tracking
- **Outputs**: Progress JSON files, dashboard updates, review files

## 📈 Metrics Tracked

- Mission activity status
- Move count and frequency
- Milestone achievement
- Progress percentage
- Stall detection
- Completion estimates

## 🎯 Benefits

- Proactive mission management
- Early stall detection
- Automated progress reporting
- Milestone opportunity identification
- Dashboard integration

---

*This automation ensures missions stay on track with proactive monitoring and intelligent alerts.*
