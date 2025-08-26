# uDASH ASCII Dashboard Template

**Template Type:** Dashboard Component
**Format:** uDOS v1.3.3
**Purpose:** Generate comprehensive ASCII-based system dashboards with real-time metrics and visual indicators

## Template Configuration

[get:title]
Main dashboard title (e.g., "uDOS Control Center")

[get:subtitle]
Secondary title or tagline for the dashboard

[get:user_name]
Current user name for personalization

[get:location]
User's current location or base

[get:timezone]
User's timezone setting

[get:current_time]
Current timestamp for display

[get:uptime]
System uptime in days

[get:health_status]
Overall system health indicator (💚 Healthy, 🟡 Warning, 🔴 Critical)

## System Metrics Configuration

[get:missions_count]
Total number of active missions

[get:moves_today]
Number of operations performed today

[get:templates_count]
Available template count

[get:errors_today]
Error count for current day

[get:datasets_count]
Total dataset count

[get:dataset_records]
Total records across all datasets

## Mission Tracking

[get:current_mission]
Currently active mission description

[get:recent_move_1]
Most recent system activity

[get:recent_move_2]
Second most recent activity

[get:recent_move_3]
Third most recent activity

## Performance Metrics

[get:daily_progress]
Daily progress percentage (0-100)

[get:daily_progress_bar]
ASCII progress bar representation

[get:mission_completion]
Mission completion percentage

[get:mission_progress_bar]
Mission progress bar visualization

[get:error_rate]
System error rate percentage

[get:error_rate_bar]
Error rate progress bar

[get:system_efficiency]
Overall system efficiency percentage

[get:efficiency_bar]
Efficiency progress bar

## Resource Usage

[get:storage_used]
Used storage in GB

[get:storage_total]
Total available storage in GB

[get:storage_percent]
Storage usage percentage

[get:memory_used]
Used memory in MB

[get:memory_total]
Total available memory in MB

[get:memory_percent]
Memory usage percentage

[get:cpu_usage]
Average CPU usage percentage

[get:total_files]
Total file count

[get:total_directories]
Total directory count

## Mission Details

[get:mission_1_name]
First mission name

[get:m1_priority]
Mission 1 priority level

[get:m1_progress]
Mission 1 completion percentage

[get:m1_status]
Mission 1 current status

[get:m1_due]
Mission 1 due date

[get:m1_days]
Days remaining for mission 1

[get:mission_2_name]
Second mission name

[get:m2_priority]
Mission 2 priority level

[get:m2_progress]
Mission 2 completion percentage

[get:m2_status]
Mission 2 current status

[get:m2_due]
Mission 2 due date

[get:m2_days]
Days remaining for mission 2

[get:mission_3_name]
Third mission name

[get:m3_priority]
Mission 3 priority level

[get:m3_progress]
Mission 3 completion percentage

[get:m3_status]
Mission 3 current status

[get:m3_due]
Mission 3 due date

[get:m3_days]
Days remaining for mission 3

## Template Statistics

[get:mission_templates_today]
Mission templates generated today

[get:total_mission_templates]
Total mission templates generated

[get:mission_success]
Mission template success rate percentage

[get:mission_time]
Average mission template generation time

[get:milestone_templates_today]
Milestone templates generated today

[get:total_milestone_templates]
Total milestone templates generated

[get:milestone_success]
Milestone template success rate percentage

[get:milestone_time]
Average milestone template generation time

[get:report_templates_today]
Report templates generated today

[get:total_report_templates]
Total report templates generated

[get:report_success]
Report template success rate percentage

[get:report_time]
Average report template generation time

[get:dashboard_templates_today]
Dashboard templates generated today

[get:total_dashboard_templates]
Total dashboard templates generated

[get:dashboard_success]
Dashboard template success rate percentage

[get:dashboard_time]
Average dashboard template generation time

## Dataset Information

[get:dataset_1_name]
First dataset name

[get:ds1_records]
Dataset 1 record count

[get:ds1_size]
Dataset 1 file size

[get:ds1_updated]
Dataset 1 last update timestamp

[get:ds1_valid]
Dataset 1 validation status

[get:ds1_export]
Dataset 1 export readiness

[get:dataset_2_name]
Second dataset name

[get:ds2_records]
Dataset 2 record count

[get:ds2_size]
Dataset 2 file size

[get:ds2_updated]
Dataset 2 last update timestamp

[get:ds2_valid]
Dataset 2 validation status

[get:ds2_export]
Dataset 2 export readiness

[get:dataset_3_name]
Third dataset name

[get:ds3_records]
Dataset 3 record count

[get:ds3_size]
Dataset 3 file size

[get:ds3_updated]
Dataset 3 last update timestamp

[get:ds3_valid]
Dataset 3 validation status

[get:ds3_export]
Dataset 3 export readiness

[get:dataset_4_name]
Fourth dataset name

[get:ds4_records]
Dataset 4 record count

[get:ds4_size]
Dataset 4 file size

[get:ds4_updated]
Dataset 4 last update timestamp

[get:ds4_valid]
Dataset 4 validation status

[get:ds4_export]
Dataset 4 export readiness

## System Component Status

[get:shell_status]
uCode Shell status indicator

[get:shell_version]
uCode Shell version number

[get:shell_check]
Shell last check timestamp

[get:shell_time]
Shell response time in milliseconds

[get:shell_notes]
Shell status notes

[get:error_status]
Error Handler status indicator

[get:error_version]
Error Handler version number

[get:error_check]
Error Handler last check timestamp

[get:error_time]
Error Handler response time

[get:error_notes]
Error Handler status notes

[get:json_status]
JSON Processor status indicator

[get:json_version]
JSON Processor version number

[get:json_check]
JSON Processor last check timestamp

[get:json_time]
JSON Processor response time

[get:json_notes]
JSON Processor status notes

[get:template_status]
Template Generator status indicator

[get:template_version]
Template Generator version number

[get:template_check]
Template Generator last check timestamp

[get:template_time]
Template Generator response time

[get:template_notes]
Template Generator status notes

[get:shortcode_status]
Shortcode System status indicator

[get:shortcode_version]
Shortcode System version number

[get:shortcode_check]
Shortcode System last check timestamp

[get:shortcode_time]
Shortcode System response time

[get:shortcode_notes]
Shortcode System status notes

[get:container_status]
Container System status indicator

[get:container_version]
Container System version number

[get:container_check]
Container System last check timestamp

[get:container_time]
Container System response time

[get:container_notes]
Container System status notes

## Template Metadata

[get:generation_timestamp]
Dashboard generation timestamp

[get:full_timestamp]
Complete timestamp with timezone

[get:template_version]
Template version number

[get:total_stats_collected]
Total number of metrics collected

[get:refresh_interval]
Dashboard refresh interval in seconds

[get:export_formats]
Available export format options

[process:dashboard_variables]
- Validate all numeric values are within expected ranges
- Format timestamps consistently across all displays
- Generate progress bars using ASCII characters: █▉▊▋▌▍▎▏
- Apply color coding logic: 💚 (good), 🟡 (warning), 🔴 (critical)
- Calculate derived metrics like efficiency and completion rates
- Ensure all status indicators are properly formatted
- Generate appropriate ASCII box drawing characters for layout

[process:formatting_rules]
- Use double-line box characters (╔═╗) for main headers
- Use single-line box characters (┌─┐) for sub-sections
- Maintain consistent column widths across all tables
- Apply right-alignment for numeric values
- Use emoji indicators for visual enhancement
- Preserve spacing for ASCII art alignment
- Generate responsive layouts based on terminal width

[output:dashboard.txt]
Complete ASCII dashboard with all metrics populated and formatted

[output:dashboard-compact.txt]
Condensed version of dashboard for smaller terminals

[output:dashboard-metrics.json]
JSON export of all dashboard metrics for API consumption

## ASCII Dashboard Template

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    🌀 {{title}} 🌀                                           ║
║                                   {{subtitle}}                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ 👤 USER: {{user_name}}           │ 📍 LOCATION: {{location}}         │ ⏰ TIME: {{current_time}}     ║
║ 🏠 BASE: {{timezone}}            │ ⏳ UPTIME: {{uptime}} days       │ 💚 HEALTH: {{health_status}}  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                        📊 SYSTEM METRICS                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🎯 MISSIONS: {{missions_count}}     │ 🔄 TODAY'S MOVES: {{moves_today}}   │ 📋 TEMPLATES: {{templates_count}}    ║
║ ❌ ERRORS: {{errors_today}}       │ 📊 DATASETS: {{datasets_count}}    │ 📦 RECORDS: {{dataset_records}}     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                      🎯 ACTIVE MISSION                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ {{current_mission}}                                                                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                      📝 RECENT ACTIVITY                                       ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ {{recent_move_1}}                                                                             ║
║ {{recent_move_2}}                                                                             ║
║ {{recent_move_3}}                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                                       🔧 QUICK ACTIONS                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ [check:health]  │ [json:stats]    │ [error:stats]   │ [mission:list]  │ [template:list]    ║
║ [run:backup]    │ [dash:refresh]  │ [log:today]     │ [tree:generate] │ [help]             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║                               📅 Generated: {{generation_timestamp}}                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════════════════════

                                    🌟 PERFORMANCE DASHBOARD 🌟

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    📈 ANALYTICS OVERVIEW                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Daily Progress:     [{{daily_progress_bar}}] {{daily_progress}}%                             │
│ Mission Completion: [{{mission_progress_bar}}] {{mission_completion}}%                      │
│ Error Rate:         [{{error_rate_bar}}] {{error_rate}}%                                     │
│ System Efficiency:  [{{efficiency_bar}}] {{system_efficiency}}%                             │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                    📊 RESOURCE USAGE                                         │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 💾 Storage:         {{storage_used}}GB / {{storage_total}}GB ({{storage_percent}}%)         │
│ 🧠 Memory:          {{memory_used}}MB / {{memory_total}}MB ({{memory_percent}}%)            │
│ ⚡ CPU:             {{cpu_usage}}% average                                                    │
│ 📁 Files:           {{total_files}} files in {{total_directories}} directories              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

                                      🎯 MISSION TRACKER

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Mission Name                   │ Priority │ Progress │ Status     │ Due Date    │ Days Left │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ {{mission_1_name}}             │ {{m1_priority}} │ {{m1_progress}}% │ {{m1_status}} │ {{m1_due}} │ {{m1_days}} │
│ {{mission_2_name}}             │ {{m2_priority}} │ {{m2_progress}}% │ {{m2_status}} │ {{m2_due}} │ {{m2_days}} │
│ {{mission_3_name}}             │ {{m3_priority}} │ {{m3_progress}}% │ {{m3_status}} │ {{m3_due}} │ {{m3_days}} │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

                                    📋 TEMPLATE GENERATOR STATS

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Template Type      │ Available │ Generated Today │ Total Generated │ Success Rate │ Avg Time │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Mission            │ ✅        │ {{mission_templates_today}}        │ {{total_mission_templates}}          │ {{mission_success}}%   │ {{mission_time}}s  │
│ Milestone          │ ✅        │ {{milestone_templates_today}}      │ {{total_milestone_templates}}        │ {{milestone_success}}% │ {{milestone_time}}s│
│ Report             │ ✅        │ {{report_templates_today}}         │ {{total_report_templates}}           │ {{report_success}}%    │ {{report_time}}s   │
│ Dashboard          │ ✅        │ {{dashboard_templates_today}}      │ {{total_dashboard_templates}}        │ {{dashboard_success}}% │ {{dashboard_time}}s│
└─────────────────────────────────────────────────────────────────────────────────────────────┘

                                      🗂️ DATA MANAGEMENT

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Dataset Name       │ Records │ Size    │ Last Updated        │ Validation │ Export Ready │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ {{dataset_1_name}} │ {{ds1_records}}    │ {{ds1_size}}   │ {{ds1_updated}}         │ {{ds1_valid}}     │ {{ds1_export}}      │
│ {{dataset_2_name}} │ {{ds2_records}}    │ {{ds2_size}}   │ {{ds2_updated}}         │ {{ds2_valid}}     │ {{ds2_export}}      │
│ {{dataset_3_name}} │ {{ds3_records}}    │ {{ds3_size}}   │ {{ds3_updated}}         │ {{ds3_valid}}     │ {{ds3_export}}      │
│ {{dataset_4_name}} │ {{ds4_records}}    │ {{ds4_size}}   │ {{ds4_updated}}         │ {{ds4_valid}}     │ {{ds4_export}}      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

                                       ⚡ SYSTEM STATUS

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Component                │ Status │ Version │ Last Check          │ Response Time │ Notes   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ uCode Shell              │ {{shell_status}}  │ {{shell_version}}  │ {{shell_check}}         │ {{shell_time}}ms     │ {{shell_notes}} │
│ Error Handler            │ {{error_status}}  │ {{error_version}}  │ {{error_check}}         │ {{error_time}}ms     │ {{error_notes}} │
│ JSON Processor           │ {{json_status}}   │ {{json_version}}   │ {{json_check}}          │ {{json_time}}ms      │ {{json_notes}}  │
│ Template Generator       │ {{template_status}} │ {{template_version}} │ {{template_check}}      │ {{template_time}}ms  │ {{template_notes}} │
│ Shortcode System         │ {{shortcode_status}} │ {{shortcode_version}} │ {{shortcode_check}}     │ {{shortcode_time}}ms │ {{shortcode_notes}} │
│ Container System         │ {{container_status}} │ {{container_version}} │ {{container_check}}     │ {{container_time}}ms │ {{container_notes}} │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════════

🌀 uDOS ASCII Dashboard Template v{{template_version}} | Generated: {{full_timestamp}}
📊 Stats: {{total_stats_collected}} metrics | 🔄 Refresh: {{refresh_interval}}s | 💾 Export: {{export_formats}}

═══════════════════════════════════════════════════════════════════════════════════════════════
```

## Usage Instructions

1. **Initialize Dashboard**: Use the GET fields to collect system metrics and user preferences
2. **Process Variables**: Apply formatting rules and calculate derived metrics
3. **Generate Output**: Create ASCII dashboard with populated values
4. **Export Options**: Generate multiple formats for different use cases

## Template Integration

This dashboard template integrates with:
- **uGET Forms**: For user configuration and preferences
- **System Metrics**: Real-time data collection
- **Mission Tracking**: Active project monitoring
- **Resource Management**: System health monitoring
- **Export System**: Multiple output format generation

---

**Template Version:** v1.3.3
**Last Updated:** August 23, 2025
**Compatibility:** uDOS Core System v1.3.3+
