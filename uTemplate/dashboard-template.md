# 🌀 uDOS Enhanced Dashboard Template

**Generated**: {{generated_date}}  
**User**: {{user_name}}  
**Location**: {{location}}  
**System Health**: {{health_status}}

---

## 📊 System Metrics Dashboard

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    🌀 uDOS METRICS CENTER 🌀                                  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🎯 MISSIONS: {{missions_count}}     │ 🔄 MOVES TODAY: {{moves_today}}   │ 📋 TEMPLATES: {{templates_count}}    ║
║ ❌ ERRORS: {{errors_today}}       │ 📊 DATASETS: {{datasets_count}}    │ 📦 RECORDS: {{dataset_records}}     ║
║ ⏳ UPTIME: {{uptime_days}} days   │ 💚 HEALTH: {{health_status}}       │ 🕐 TIME: {{current_time}}           ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Active Missions

{{#if active_missions}}
{{#each active_missions}}
### 📋 {{this.name}}
- **Priority**: {{this.priority}}
- **Status**: {{this.status}}
- **Progress**: {{this.progress}}%
- **Created**: {{this.created_date}}

{{/each}}
{{else}}
*No active missions found*

**💡 Quick Start:**
- Use `[mission:create name=my-project]` to create a new mission
- Use `TEMPLATE generate mission project-name` for structured mission planning
{{/if}}

---

## 🔄 Recent Activity Feed

{{#if recent_moves}}
### Today's Moves ({{moves_today}} total):

{{#each recent_moves}}
- **{{this.timestamp}}** - {{this.action}}
{{/each}}

{{else}}
*No moves logged today*

**💡 Activity Tracking:**
- All commands are automatically logged as "moves"
- View full activity with `RECENT` command
- Use `LOG move "custom message"` for manual entries
{{/if}}

---

## 📈 Performance Analytics

### System Statistics:
- **Total Missions**: {{total_missions}}
- **Total Moves**: {{total_moves}}
- **Total Templates Generated**: {{total_templates}}
- **System Uptime**: {{uptime_days}} days
- **Error Rate**: {{error_rate}}%

### Data Management:
- **JSON Datasets**: {{datasets_count}} files
- **Total Records**: {{dataset_records}} entries
- **Data Validation**: {{validation_status}}
- **Export Operations**: {{export_count}} today

### Template System:
- **Available Templates**: {{available_templates}}
- **Generated Today**: {{templates_today}}
- **Success Rate**: {{template_success_rate}}%

---

## 🛠️ System Health Check

| Component | Status | Details |
|-----------|--------|---------|
| Error Handler | {{error_handler_status}} | {{error_handler_details}} |
| JSON Datasets | {{datasets_status}} | {{datasets_details}} |
| Template System | {{template_system_status}} | {{template_system_details}} |
| Shortcode System | {{shortcode_status}} | {{shortcode_details}} |
| Container System | {{container_status}} | {{container_details}} |

---

## 🚀 Quick Actions

### Command Shortcuts:
```bash
# System Management
[check:health]              # Full system health check
[error:stats]               # Error statistics and logs
[json:stats]                # Dataset statistics

# Data Operations  
[json:search "query"]       # Search across all datasets
[json:export dataset csv]   # Export data to CSV
[template:list]             # Show available templates

# Mission Management
[mission:create name=test]  # Create new mission
[mission:list]              # List active missions
[log:move "message"]        # Log activity

# Dashboard Operations
[dash:refresh]              # Refresh dashboard
[dash:ascii]                # Show ASCII dashboard
[dash:live]                 # Live updating dashboard
```

### File Operations:
- **View Dashboard**: `cat {{dashboard_file}}`
- **ASCII Dashboard**: `cat {{ascii_dashboard_file}}`
- **Stats Data**: `cat {{stats_file}}`

---

## 📊 Usage Patterns

### Most Used Commands:
{{#each top_commands}}
- **{{this.command}}**: {{this.usage_count}} times
{{/each}}

### Peak Activity Hours:
- **Morning (6-12)**: {{morning_activity}}%
- **Afternoon (12-18)**: {{afternoon_activity}}%
- **Evening (18-24)**: {{evening_activity}}%
- **Night (0-6)**: {{night_activity}}%

---

## 📋 Configuration

### Dashboard Settings:
- **Refresh Interval**: {{refresh_interval}} seconds
- **Stats Retention**: {{stats_retention}} days
- **Export Format**: {{default_export_format}}
- **ASCII Mode**: {{ascii_mode_enabled}}

### Customization:
- **Theme**: {{dashboard_theme}}
- **Timezone**: {{user_timezone}}
- **Date Format**: {{date_format}}
- **Language**: {{interface_language}}

---

## 📝 Recent System Changes

{{#if recent_changes}}
{{#each recent_changes}}
- **{{this.date}}**: {{this.description}}
{{/each}}
{{else}}
*No recent system changes*
{{/if}}

---

## 🎯 Goals & Metrics

### Daily Goals:
- **Target Moves**: {{daily_move_target}} ({{daily_progress}}% complete)
- **Mission Progress**: {{mission_progress_target}}%
- **Error Target**: < {{error_threshold}} errors

### Weekly Goals:
- **New Missions**: {{weekly_mission_target}}
- **Templates Generated**: {{weekly_template_target}}
- **Data Exports**: {{weekly_export_target}}

---

*Dashboard Template v1.7.1 Enhanced - Generated {{generation_timestamp}}*  
*System: uDOS Enhanced Architecture with ASCII Dashboard Support*
