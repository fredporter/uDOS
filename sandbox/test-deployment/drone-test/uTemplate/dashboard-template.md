# 🌀 uDOS v1.0 Enhanced Dashboard

**Generated**: {{instance_time}}  
**Instance**: {{instance_location}}  
**Session**: {{instance_session}}  
**Timezone**: {{dataset:timezones.{{instance_timezone}}.name}}  
**System Health**: {{health_status}}  
**Version**: {{udos_version}}  
**Document ID**: {{document_id}}

## 📊 Metadata Block

**Template System:** v2.1.0  
**Dataset Version:** {{dataset_version}}  
**Cross-References:** {{cross_references_count}}  
**Generated With:** [template:generate dashboard]

### 🔗 Cross-References
- **[mission:current]({{ref:mission.current.path}})** - {{ref:mission.current.name}}
- **[packages:registry]({{ref:packages.registry.path}})** - Package installation status
- **[system:health]({{ref:system.health.path}})** - System health metrics

### 📊 Related Datasets
- **System Metrics** - [dataset:system_metrics] - Real-time system data
- **Package Registry** - [dataset:packages] - Installation database
- **Geographic Data** - [dataset:cities] - Location information

---

## 📊 Executive Summary

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                  🌀 uDOS v1.0 COMMAND CENTER 🌀                              ║
║                                Instance: {{instance_location}} | {{instance_time}}              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🎯 PROJECTS: {{projects_count}}      │ 🚀 MISSIONS: {{missions_count}}     │ ⭐ MILESTONES: {{milestones_count}}║
║ ✅ COMPLETED: {{completed_count}}    │ 🔄 IN PROGRESS: {{in_progress}}     │ ⏳ PENDING: {{pending_count}}     ║
║ 📊 DATASETS: {{dataset:datasets.count}} │ 🎨 TEMPLATES: {{template:templates.count}} │ 📊 RECORDS: {{total_records}}     ║
║ ⚠️ ISSUES: {{issues_count}}         │ 🎯 SUCCESS RATE: {{calc:success_rate}}%  │ 🕐 UPDATED: {{instance_time}}       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Project Portfolio Status

{{#if active_projects}}
{{#each active_projects}}
### 🏗️ {{this.name}} ({{this.status}})
**Manager**: {{this.manager}} | **Priority**: {{this.priority}} | **Health**: {{this.health}}

```
Progress: [{{this.progress_bar}}] {{this.progress}}%
Budget:   [{{this.budget_bar}}] ${{this.spent}}/${{this.budget}}
Timeline: {{this.start_date}} → {{this.end_date}} ({{this.days_remaining}} days left)
```

**Current Phase**: {{this.current_phase}}  
**Next Milestone**: {{this.next_milestone}} ({{this.milestone_date}})  
**Team Size**: {{this.team_size}} members  

{{#if this.blockers}}
⚠️ **Blockers**: {{this.blockers}}
{{/if}}

{{#if this.recent_achievements}}
✅ **Recent Wins**: {{this.recent_achievements}}
{{/if}}

---
{{/each}}
{{else}}
### 🌟 Ready to Start Your First Project?

**Quick Actions:**
- 🚀 Create Project: `./uCode/structure.sh project "My Project"`
- 📋 New Mission: `./uCode/structure.sh mission "My Mission"`
- 🎯 Add Milestone: `./uCode/structure.sh milestone "My Goal"`

**Templates Available:**
- `project-template.md` - Comprehensive project planning
- `mission-template.md` - Mission-focused execution
- `milestone-template.md` - Goal tracking
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
