# Mission Automation Template

Template for creating automated mission management workflows in uScript.

---
title: "{{mission_name}} Automation"
type: "mission_automation"
author: "{{author_name}}"
version: "1.0.0"
mission_id: "{{mission_id}}"
---

## 🎯 Mission: {{mission_name}}

```uScript
' {{mission_name}} - Automated Workflow
' Generated from uScript mission template

SET mission_name = "{{mission_name}}"
SET mission_id = "{{mission_id}}"
SET author = "{{author_name}}"
SET start_date = TODAY()

LOG_INFO "Starting automated mission: " + mission_name
LOG_MISSION mission_id, "Mission automation script initiated by " + author

' 1. Initialize Mission Structure
LOG_INFO "Initializing mission structure..."
CREATE MISSION mission_name

' Create initial milestone
CREATE MILESTONE mission_id + "/mission-started"
LOG_MILESTONE mission_id, "mission-started"

' 2. Setup Mission Configuration
SET mission_config = {
    "name": mission_name,
    "id": mission_id,
    "author": author,
    "start_date": start_date,
    "auto_tracking": true,
    "auto_milestones": {{auto_milestones}},
    "notification_level": "{{notification_level}}",
    "estimated_duration": "{{estimated_duration}}",
    "target_moves": {{target_moves}},
    "category": "{{mission_category}}"
}

SET config_file = "./uMemory/missions/" + mission_id + "-config.json"
write_json_file(config_file, mission_config)
LOG_INFO "Mission configuration saved: " + config_file

' 3. Create Initial Moves
LOG_INFO "Creating initial mission moves..."

{{#each initial_moves}}
CREATE MOVE mission_id + "/{{this.id}}" {
    "description": "{{this.description}}",
    "status": "{{this.status}}",
    "priority": "{{this.priority}}",
    "estimated_effort": "{{this.effort}}",
    "created": NOW(),
    "created_by": author
}
LOG_MOVE mission_id, "{{this.id}}", "Move created: {{this.description}}"
{{/each}}

' 4. Setup Automation Rules
LOG_INFO "Configuring automation rules..."

{{#if enable_daily_check}}
' Daily progress check
SET daily_check_rule = {
    "type": "daily_check",
    "enabled": true,
    "time": "{{daily_check_time}}",
    "actions": ["progress_report", "stall_detection", "milestone_check"]
}
write_json_file("./uMemory/automation/" + mission_id + "-daily.json", daily_check_rule)
{{/if}}

{{#if enable_milestone_automation}}
' Automatic milestone creation
SET milestone_rule = {
    "type": "auto_milestone",
    "enabled": true,
    "trigger": "move_count",
    "interval": {{milestone_interval}},
    "template": mission_id + "/progress-milestone-{count}"
}
write_json_file("./uMemory/automation/" + mission_id + "-milestones.json", milestone_rule)
{{/if}}

' 5. Setup Notifications
{{#if enable_notifications}}
LOG_INFO "Setting up notification preferences..."
SET notification_config = {
    "enabled": true,
    "level": "{{notification_level}}",
    "channels": [{{#each notification_channels}}"{{this}}"{{#unless @last}}, {{/unless}}{{/each}}],
    "daily_summary": {{daily_summary}},
    "milestone_alerts": {{milestone_alerts}},
    "stall_warnings": {{stall_warnings}}
}
write_json_file("./uMemory/notifications/" + mission_id + ".json", notification_config)
{{/if}}

' 6. Create Mission Dashboard Entry
LOG_INFO "Adding mission to dashboard..."
SET dashboard_entry = {
    "mission_id": mission_id,
    "name": mission_name,
    "status": "active",
    "progress": 0,
    "moves_count": {{initial_moves.length}},
    "milestones_count": 1,
    "last_activity": NOW(),
    "category": "{{mission_category}}",
    "priority": "{{mission_priority}}",
    "automation_enabled": true
}

SET dashboard_file = "./uMemory/dashboard/missions/" + mission_id + ".json"
write_json_file(dashboard_file, dashboard_entry)

' 7. Run Initial Checks
LOG_INFO "Running initial system checks..."
IF system_status() = "healthy" THEN
    LOG_INFO "✅ System ready for mission execution"
    
    {{#if run_initial_setup}}
    ' Execute initial setup tasks
    {{#each setup_commands}}
    RUN "{{this}}"
    LOG_MOVE mission_id, "setup", "Executed: {{this}}"
    {{/each}}
    {{/if}}
    
    CREATE MILESTONE mission_id + "/setup-complete"
    LOG_MILESTONE mission_id, "setup-complete"
ELSE
    LOG_ERROR "❌ System not ready - mission setup incomplete"
    CREATE MOVE mission_id + "/system-check-failed" {
        "description": "System health check failed during setup",
        "status": "blocked",
        "priority": "high",
        "created": NOW()
    }
END IF

' 8. Final Summary
LOG_INFO "Mission automation setup completed"
LOG_MISSION mission_id, "Automation configured - mission ready for execution"

SET setup_summary = {
    "mission_name": mission_name,
    "mission_id": mission_id,
    "setup_date": start_date,
    "initial_moves": {{initial_moves.length}},
    "automation_enabled": true,
    "estimated_completion": date_add(start_date, {{estimated_duration_days}}),
    "next_review": date_add(start_date, 7)
}

LOG_DASHBOARD "🚀 New mission launched: " + mission_name
LOG_TO_FILE "./uMemory/logs/mission-setup-" + start_date + ".log", 
             "Mission created: " + JSON.stringify(setup_summary)

' Schedule first progress review
CREATE MOVE mission_id + "/first-review" {
    "description": "First progress review and planning session",
    "status": "scheduled",
    "priority": "medium", 
    "scheduled_date": date_add(start_date, 7),
    "created": NOW()
}

LOG_INFO "🎯 Mission '" + mission_name + "' is ready for action!"
```

## 📋 Template Variables

Replace these placeholders when using this template:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{mission_name}}` | Human-readable mission name | "Learn Data Science" |
| `{{mission_id}}` | Unique mission identifier | "learn-data-science" |
| `{{author_name}}` | Mission creator | "Developer" |
| `{{auto_milestones}}` | Enable automatic milestones | true/false |
| `{{notification_level}}` | Notification verbosity | "info", "warn", "error" |
| `{{estimated_duration}}` | Expected duration | "2 weeks", "1 month" |
| `{{target_moves}}` | Target number of moves | 50 |
| `{{mission_category}}` | Mission category | "learning", "project", "personal" |

## 🔧 Customization Options

### Initial Moves
```json
{
  "initial_moves": [
    {
      "id": "research-phase",
      "description": "Research and planning",
      "status": "pending",
      "priority": "high",
      "effort": "2 hours"
    }
  ]
}
```

### Automation Settings
- Daily progress checks
- Automatic milestone creation
- Stall detection and alerts
- Performance tracking
- Dashboard integration

## 🎯 Usage

1. Copy this template to a new file
2. Replace all `{{variables}}` with actual values
3. Customize initial moves and automation rules
4. Run the script to create your automated mission

---

*This template creates a fully automated mission with intelligent tracking, progress monitoring, and milestone management.*
