# 📊 uDOS Daily Move Log Template

**Template Version**: v2.1.0  
**Date**: {{log_date}}  
**Day**: {{day_of_week}}  
**Generated**: {{timestamp}}

---

## 📈 Daily Statistics Dashboard

```ascii
                    ╔═════════════════════════════════════════════════════════╗
                    ║               📊 DAILY ACTIVITY METRICS                ║
                    ╠═════════════════════════════════════════════════════════╣
                    ║                                                         ║
                    ║  🎯 MOVES: {{moves_count}}        📊 STATS: {{stats_count}}        ║
                    ║  ⚡ COMMANDS: {{commands_count}}     ❌ ERRORS: {{errors_count}}      ║
                    ║  📁 FILES: {{files_created}}       ⏱️  TIME: {{session_time}}   ║
                    ║                                                         ║
                    ║  ┌─ ACTIVITY PROGRESS ────────────────────────────────┐ ║
                    ║  │ {{progress_bar}}                                   │ ║
                    ║  │ {{completion_percentage}}% Complete               │ ║
                    ║  └─────────────────────────────────────────────────────┘ ║
                    ║                                                         ║
                    ╚═════════════════════════════════════════════════════════╝
```

---

## 🗂️ Move Categories

### 🎯 Mission Moves
```shortcode
{MOVE_CATEGORY}
type: mission
count: {{mission_moves}}
description: Strategic objectives and goal completion
icon: 🎯
priority: high
{/MOVE_CATEGORY}
```

### ⚡ System Moves  
```shortcode
{MOVE_CATEGORY}
type: system
count: {{system_moves}}
description: Administrative and maintenance operations
icon: ⚡
priority: medium
{/MOVE_CATEGORY}
```

### 📁 File Moves
```shortcode
{MOVE_CATEGORY}
type: file
count: {{file_moves}}
description: File creation, editing, and organization
icon: 📁
priority: low
{/MOVE_CATEGORY}
```

### 🔧 Development Moves
```shortcode
{MOVE_CATEGORY}
type: development
count: {{dev_moves}}
description: Code development and testing activities
icon: 🔧
priority: high
{/MOVE_CATEGORY}
```

---

## ⏰ Temporal Activity Timeline

```ascii
                         24-HOUR ACTIVITY TIMELINE
     
     00:00  03:00  06:00  09:00  12:00  15:00  18:00  21:00  24:00
       │      │      │      │      │      │      │      │      │
       ├──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
       │      │      │ ▓▓▓  │ ████ │ ███  │ ▓▓▓▓ │ ██   │      │
       │ ░░   │ ░    │ ██   │ ████ │ ████ │ ████ │ ███  │ ░░   │
       └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
       
       Legend: ░ Light Activity  ▓ Medium Activity  █ High Activity
```

---

## 📋 Move Log Entries

```shortcode
{MOVE_LOG_ENTRY}
timestamp: {{move_timestamp}}
move_id: {{move_id}}
command: {{command}}
type: {{move_type}}
duration: {{duration_seconds}}
success: {{success_status}}
context: {{move_context}}
tags: [{{move_tags}}]
{/MOVE_LOG_ENTRY}
```

### Recent Moves
{{#each moves}}
```shortcode
{MOVE_ENTRY}
time: {{this.timestamp}}
command: "{{this.command}}"
type: {{this.type}}
status: {{this.status}}
output_size: {{this.output_size}}
{{#if this.error}}
error: "{{this.error}}"
{{/if}}
{/MOVE_ENTRY}
```
{{/each}}

---

## 🎯 Daily Objectives & Progress

### Objectives Dataset
```shortcode
{DATASET_OBJECTIVES}
date: {{log_date}}
objectives:
  - id: obj_001
    description: "{{objective_1}}"
    priority: {{obj_1_priority}}
    status: {{obj_1_status}}
    progress: {{obj_1_progress}}%
    
  - id: obj_002
    description: "{{objective_2}}"
    priority: {{obj_2_priority}}
    status: {{obj_2_status}}
    progress: {{obj_2_progress}}%
    
  - id: obj_003
    description: "{{objective_3}}"
    priority: {{obj_3_priority}}
    status: {{obj_3_status}}
    progress: {{obj_3_progress}}%
{/DATASET_OBJECTIVES}
```

### Progress Visualization
```ascii
                           DAILY OBJECTIVES PROGRESS
    
    ┌─ Objective 1: {{objective_1_short}}
    │  Progress: [{{obj_1_bar}}] {{obj_1_progress}}%
    │  Status: {{obj_1_status}} | Priority: {{obj_1_priority}}
    │
    ├─ Objective 2: {{objective_2_short}}
    │  Progress: [{{obj_2_bar}}] {{obj_2_progress}}%
    │  Status: {{obj_2_status}} | Priority: {{obj_2_priority}}
    │
    └─ Objective 3: {{objective_3_short}}
       Progress: [{{obj_3_bar}}] {{obj_3_progress}}%
       Status: {{obj_3_status}} | Priority: {{obj_3_priority}}
```

---

## 📊 Performance Analytics

### Command Performance
```shortcode
{ANALYTICS_COMMANDS}
total_commands: {{total_commands}}
unique_commands: {{unique_commands}}
average_duration: {{avg_duration}}s
success_rate: {{success_rate}}%
most_used: "{{top_command}}"
fastest: "{{fastest_command}}"
slowest: "{{slowest_command}}"
{/ANALYTICS_COMMANDS}
```

### Error Analysis
```shortcode
{ANALYTICS_ERRORS}
total_errors: {{total_errors}}
error_rate: {{error_rate}}%
common_errors:
  - type: {{error_type_1}}
    count: {{error_count_1}}
    last_occurrence: {{error_last_1}}
    
  - type: {{error_type_2}}
    count: {{error_count_2}}
    last_occurrence: {{error_last_2}}
{/ANALYTICS_ERRORS}
```

### System Health
```ascii
                         SYSTEM HEALTH DASHBOARD
    
    ┌─────────────────────────────────────────────────────────────┐
    │  CPU Usage:     [{{cpu_bar}}] {{cpu_percent}}%           │
    │  Memory:        [{{mem_bar}}] {{mem_percent}}%           │
    │  Disk Space:    [{{disk_bar}}] {{disk_percent}}%         │
    │  Network:       [{{net_bar}}] {{network_status}}         │
    │                                                           │
    │  🔋 Battery:    {{battery_level}}%                       │
    │  🌡️  Temperature: {{cpu_temp}}°C                          │
    │  ⏱️  Uptime:     {{system_uptime}}                        │
    └─────────────────────────────────────────────────────────────┘
```

---

## 🏷️ Smart Tagging System

```shortcode
{TAG_ANALYSIS}
generated_tags:
  - productivity: {{productivity_score}}
  - complexity: {{complexity_level}}
  - focus_area: {{primary_focus}}
  - tools_used: [{{tools_list}}]
  - outcomes: [{{outcomes_list}}]
  
auto_categories:
  - development: {{dev_percentage}}%
  - administration: {{admin_percentage}}%
  - exploration: {{explore_percentage}}%
  - optimization: {{optimize_percentage}}%
{/TAG_ANALYSIS}
```

---

## 📈 Trend Analysis

### Weekly Comparison
```ascii
                         WEEKLY ACTIVITY TRENDS
    
    Day     │ Moves │ Errors │ Time   │ Productivity
    ────────┼───────┼────────┼────────┼──────────────
    Mon     │  {{mon_moves}}   │   {{mon_errors}}    │ {{mon_time}} │ {{mon_productivity}}
    Tue     │  {{tue_moves}}   │   {{tue_errors}}    │ {{tue_time}} │ {{tue_productivity}}
    Wed     │  {{wed_moves}}   │   {{wed_errors}}    │ {{wed_time}} │ {{wed_productivity}}
    Thu     │  {{thu_moves}}   │   {{thu_errors}}    │ {{thu_time}} │ {{thu_productivity}}
    Fri     │  {{fri_moves}}   │   {{fri_errors}}    │ {{fri_time}} │ {{fri_productivity}}
    Sat     │  {{sat_moves}}   │   {{sat_errors}}    │ {{sat_time}} │ {{sat_productivity}}
    Sun     │  {{sun_moves}}   │   {{sun_errors}}    │ {{sun_time}} │ {{sun_productivity}}
    ────────┼───────┼────────┼────────┼──────────────
    Average │  {{avg_moves}}   │   {{avg_errors}}    │ {{avg_time}} │ {{avg_productivity}}
```

---

## 🔮 Predictive Insights

```shortcode
{PREDICTIVE_ANALYSIS}
patterns_detected:
  - peak_activity_time: {{peak_time}}
  - preferred_commands: [{{top_commands}}]
  - productivity_pattern: {{productivity_pattern}}
  - error_trends: {{error_trend}}
  
recommendations:
  - optimization: "{{optimization_tip}}"
  - workflow: "{{workflow_tip}}"
  - learning: "{{learning_tip}}"
  
forecast:
  - tomorrow_activity: {{tomorrow_forecast}}
  - weekly_goal_likelihood: {{goal_likelihood}}%
  - suggested_focus: "{{suggested_focus}}"
{/PREDICTIVE_ANALYSIS}
```

---

## 💾 Data Export

```shortcode
{EXPORT_OPTIONS}
formats:
  - json: {{json_export_path}}
  - csv: {{csv_export_path}}
  - markdown: {{markdown_export_path}}
  - html: {{html_export_path}}
  
filters:
  - date_range: [{{start_date}}, {{end_date}}]
  - move_types: [{{filtered_types}}]
  - include_errors: {{include_errors}}
  - anonymize: {{anonymize_data}}
{/EXPORT_OPTIONS}
```

---

## 🎯 Session Summary

```ascii
                           SESSION SUMMARY
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  📅 Date: {{log_date}}                                        ║
    ║  ⏰ Duration: {{session_duration}}                            ║
    ║  🎯 Objectives Met: {{objectives_completed}}/{{total_objectives}}     ║
    ║  ⚡ Efficiency: {{efficiency_score}}%                         ║
    ║                                                               ║
    ║  🏆 Achievements:                                             ║
    ║    • {{achievement_1}}                                       ║
    ║    • {{achievement_2}}                                       ║
    ║    • {{achievement_3}}                                       ║
    ║                                                               ║
    ║  📝 Notes: {{session_notes}}                                 ║
    ╚═══════════════════════════════════════════════════════════════╝
```

---

**Template Metadata:**
- **File Format**: Enhanced Daily Log v2.1.0
- **Compliance**: uDOS Template Standard  
- **Generated**: {{generation_timestamp}}
- **Next Update**: {{next_update_time}}
- **Archive Date**: {{archive_date}}

*This enhanced daily log integrates with the uDOS ecosystem for comprehensive activity tracking and performance analysis.*
