# Mission: {{mission_name}}

**Template Version:** v2.1.0  
**Generated:** {{instance_time}}  
**Instance:** {{instance_location}}  
**Session:** {{instance_session}}  
**Document ID:** {{document_id}}  
**Priority:** {{input:priority|enum:low,medium,high,critical}}  
**Status:** {{input:status|enum:planning,active,on-hold,completed,cancelled|default:planning}}

> **Mission Type:** {{input:mission_type|enum:development,research,deployment,maintenance,enhancement}}  
> **Complexity:** {{input:complexity|enum:low,medium,high,enterprise}}  
> **Estimated Duration:** {{input:estimated_duration}}  
> **Start Date:** {{input:start_date|date}}  
> {{#if input:end_date}}**Target Completion:** {{input:end_date|date}}{{/if}}

## 📊 Metadata Block

**Template System:** v2.1.0  
**Dataset Version:** {{dataset_version}}  
**Cross-References:** {{cross_references_count}}  
**Generated With:** [template:generate mission --name={{mission_name}}]

### 🔗 Cross-References
- **[project:current]({{ref:project.current.path}})** - {{ref:project.current.name}}
- **[dashboard:metrics]({{ref:dashboard.metrics.path}})** - Real-time progress tracking
- **[team:members]({{ref:team.members.path}})** - Team assignment details

### 📊 Related Datasets
- **Geographic Data** - [dataset:cities.{{input:primary_location}}] - Mission location data
- **Team Resources** - [dataset:team_resources] - Available team members
- **Project Templates** - [dataset:project_templates] - Related project types

---

## 📋 Mission Overview

### 🎯 Primary Objective
{{input:objective|required|min:10}}

### 🔍 Mission Context
{{input:context|"Context will be added as mission develops"}}

### � Location & Timezone
- **Primary Location:** {{dataset:cities.{{input:primary_location}}.name}}
- **Timezone:** {{dataset:timezones.{{input:timezone}}.name}} ({{dataset:timezones.{{input:timezone}}.offset}})
- **Local Time:** {{calc:current_time_in_timezone}}

## 💼 Resource Allocation

### 👥 Team Composition
{{#if input:team_members}}
{{#each input:team_members}}
- **{{this.name}}** ({{this.role}}) - {{this.allocation}}% allocation
  - Skills: {{dataset:team_skills.{{this.id}}.primary_skills}}
  - Availability: {{dataset:team_availability.{{this.id}}.current_status}}
{{/each}}
{{else}}
*Team assignment pending*
{{/if}}

### 💰 Budget Overview
{{#if input:budget}}
- **Total Budget:** ${{input:budget|number}}
- **Monthly Burn Rate:** ${{calc:budget / duration_months}}
- **Current Spend:** ${{calc:current_spend}}
- **Remaining:** ${{calc:budget - current_spend}}
{{/if}}

## 🎯 Success Criteria & KPIs

### ✅ Success Criteria
{{#each input:success_criteria}}
- [ ] {{this}}
{{/each}}

### 📊 Key Performance Indicators
{{#if input:kpis}}
{{#each input:kpis}}
- **{{this.metric}}**: Target {{this.target}} | Current: {{this.current}} | Progress: {{calc:this.current / this.target * 100}}%
{{/each}}
{{/if}}
{{else}}
*KPIs to be defined based on mission objectives*
{{/if}}

{{#if resources}}
## 🛠️ Resources Required

{{#each resources}}
- {{this}}
{{/each}}
{{/if}}

{{#if technologies}}
## 💻 Technologies & Tools

{{#each technologies}}
- **{{this.name}}**: {{this.purpose}} (Status: {{this.status}})
{{/each}}
{{/if}}

{{#if team_members}}
## 👥 Team Composition

{{#each team_members}}
- **{{this.name}}** - {{this.role}} ({{this.allocation}}% allocation)
  {{#if this.skills}}- Skills: {{this.skills}}{{/if}}
  {{#if this.contact}}- Contact: {{this.contact}}{{/if}}
{{/each}}
{{/if}}

{{#if stakeholders}}
## 🤝 Stakeholders

{{#each stakeholders}}
- **{{this.name}}** ({{this.role}}) - {{this.influence}} influence, {{this.interest}} interest
{{/each}}
{{/if}}

{{#if budget}}
## 💰 Budget & Resources

**Total Allocated:** ${{budget}}
{{#if budget_breakdown}}

### Budget Breakdown
{{#each budget_breakdown}}
- **{{this.category}}**: ${{this.amount}} ({{this.percentage}}%)
{{/each}}
{{/if}}

{{#if burn_rate}}
**Current Burn Rate:** ${{burn_rate}}/month
{{/if}}
{{/if}}

{{#if milestones}}
## 🗓️ Mission Milestones

{{#each milestones}}
### {{this.name}} - {{this.date}}
{{this.description}}

**Deliverables:**
{{#each this.deliverables}}
- [ ] {{this}}
{{/each}}

**Success Criteria:**
{{#each this.success_criteria}}
- [ ] {{this}}
{{/each}}

---
{{/each}}
{{/if}}

## 📊 Progress Tracking

### Mission Phase Status
- [ ] 🚀 Mission initiated
- [ ] 📋 Requirements gathered
- [ ] 👥 Team assembled
- [ ] 🛠️ Resources allocated
- [ ] ⚡ Execution begun
- [ ] 🎯 Milestones achieved
- [ ] 🔍 Quality assurance
- [ ] ✅ Mission completed
- [ ] 📝 Post-mission review

### Progress Metrics
{{#if progress_metrics}}
{{#each progress_metrics}}
- **{{this.metric}}**: {{this.current}}/{{this.target}} ({{this.percentage}}%)
{{/each}}
{{else}}
*Progress metrics will be updated as mission progresses*
{{/if}}

{{#if blockers}}
### 🚧 Current Blockers
{{#each blockers}}
- **{{this.title}}**: {{this.description}} (Priority: {{this.priority}})
  - *Owner*: {{this.owner}}
  - *Target Resolution*: {{this.target_date}}
{{/each}}
{{/if}}

{{#if recent_updates}}
### 📈 Recent Updates
{{#each recent_updates}}
- **{{this.date}}**: {{this.update}} ({{this.author}})
{{/each}}
{{/if}}

---

## 🔗 Mission Integration

**uDOS Context Integration:**
- **Mission ID:** {{mission_name | slugify}}
- **uCode Integration:** {{#if ucode_integration}}✅ Enabled{{else}}❌ Not configured{{/if}}
- **Dashboard Tracking:** {{#if dashboard_tracking}}✅ Active{{else}}❌ Not configured{{/if}}
- **Memory System:** {{#if memory_integration}}✅ Connected{{else}}❌ Not integrated{{/if}}

{{#if related_missions}}
### 🔄 Related Missions
{{#each related_missions}}
- [{{this.name}}]({{this.link}}) - {{this.relationship}}
{{/each}}
{{/if}}

{{#if external_references}}
### 🌐 External References
{{#each external_references}}
- [{{this.title}}]({{this.url}}) - {{this.description}}
{{/each}}
{{/if}}

---

**Generated:** {{generated_date}}  
**Template Version:** 2.0.0  
**uDOS Version:** 1.0.0  
**Last Updated:** {{last_updated}}
