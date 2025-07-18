# Template: Mission - {{mission_name}}

**Created:** {{start_date}}  
**Priority:** {{priority}}  
{{#if end_date}}**Target Completion:** {{end_date}}{{/if}}  
**Status:** {{status}}  
**Location:** {{location}}  
**Timezone:** {{timezone}}

> **Mission Type:** {{mission_type}}  
> **Complexity:** {{complexity}}  
> **Estimated Duration:** {{estimated_duration}}

---

## 📋 Mission Overview

### 🎯 Primary Objective
{{objective}}

### 🔍 Mission Context
{{#if context}}
{{context}}
{{else}}
*Context will be added as mission develops*
{{/if}}

## 🎯 Success Criteria

{{#each success_criteria}}
- [ ] {{this}}
{{/each}}

## 🎲 Risk Assessment

{{#if risks}}
### ⚠️ Identified Risks
{{#each risks}}
- **{{this.type}}**: {{this.description}} (Impact: {{this.impact}}, Probability: {{this.probability}})
{{/each}}
{{else}}
*Risk assessment to be completed during mission planning*
{{/if}}

## 📊 Key Performance Indicators (KPIs)

{{#if kpis}}
{{#each kpis}}
- **{{this.metric}}**: {{this.target}} (Current: {{this.current}})
{{/each}}
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
