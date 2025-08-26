# Template: Milestone - {{milestone_name}}

**Due Date:** {{due_date}}
{{#if start_date}}**Start Date:** {{start_date}}{{/if}}
{{#if assigned_to}}**Assigned To:** {{assigned_to}}{{/if}}
{{#if progress}}**Progress:** {{progress}}%{{/if}}
**Status:** {{status}}
**Priority:** {{priority}}
{{#if estimated_effort}}**Estimated Effort:** {{estimated_effort}}{{/if}}
**Legacy Save:** {{save_as_legacy|boolean|default:false}}

> **Milestone Type:** {{milestone_type}}
> **Complexity:** {{complexity}}
> **Parent Mission:** {{parent_mission}}

---

## 📝 Milestone Overview

### 🎯 Description
{{description}}

### 🔍 Context & Rationale
{{#if context}}
{{context}}
{{else}}
*Context will be added during milestone planning*
{{/if}}

### 📈 Business Value
{{#if business_value}}
{{business_value}}
{{else}}
*Business value assessment pending*
{{/if}}

## 📦 Deliverables & Outputs

{{#each deliverables}}
- [ ] **{{this.name}}** ({{this.type}})
  {{#if this.description}}- *Description*: {{this.description}}{{/if}}
  {{#if this.owner}}- *Owner*: {{this.owner}}{{/if}}
  {{#if this.due_date}}- *Due*: {{this.due_date}}{{/if}}
{{/each}}

{{#if acceptance_criteria}}
## ✅ Acceptance Criteria

{{#each acceptance_criteria}}
- [ ] {{this}}
{{/each}}
{{/if}}

## ✅ Success Criteria

{{#each success_criteria}}
- [ ] {{this}}
{{/each}}

{{#if quality_gates}}
## 🎯 Quality Gates

{{#each quality_gates}}
- **{{this.gate}}**: {{this.criteria}} ({{this.method}})
{{/each}}
{{/if}}

{{#if testing_strategy}}
## 🧪 Testing Strategy

{{testing_strategy}}

{{#if test_cases}}
### Test Cases
{{#each test_cases}}
- [ ] {{this.name}} - {{this.description}}
{{/each}}
{{/if}}
{{/if}}

{{#if dependencies}}
## 🔗 Dependencies & Prerequisites

{{#each dependencies}}
- **{{this.name}}** ({{this.type}})
  {{#if this.description}}- *Details*: {{this.description}}{{/if}}
  {{#if this.status}}- *Status*: {{this.status}}{{/if}}
  {{#if this.blocking}}- *Blocking*: {{this.blocking}}{{/if}}
{{/each}}
{{/if}}

{{#if risks}}
## ⚠️ Risk Assessment

{{#each risks}}
- **{{this.risk}}**: {{this.impact}} ({{this.probability}} probability)
  {{#if this.mitigation}}- *Mitigation*: {{this.mitigation}}{{/if}}
{{/each}}
{{/if}}

{{#if resources}}
## 🛠️ Resource Requirements

{{#each resources}}
- **{{this.type}}**: {{this.description}}
  {{#if this.quantity}}- *Quantity*: {{this.quantity}}{{/if}}
  {{#if this.availability}}- *Availability*: {{this.availability}}{{/if}}
{{/each}}
{{/if}}

## 📊 Progress Tracking

### Milestone Phase Status
- [ ] 📋 Planning complete
- [ ] 🚀 Work initiated
- [ ] ⚡ Development in progress
- [ ] 🔍 Testing phase
- [ ] 👥 Review phase
- [ ] ✅ Completed
- [ ] ✔️ Verified & approved

### Progress Metrics
{{#if progress_metrics}}
{{#each progress_metrics}}
- **{{this.metric}}**: {{this.current}}/{{this.target}} ({{this.percentage}}%)
{{/each}}
{{else}}
*Progress metrics will be defined during execution*
{{/if}}

{{#if blockers}}
### 🚧 Current Blockers
{{#each blockers}}
- **{{this.title}}**: {{this.description}}
  - *Impact*: {{this.impact}}
  - *Owner*: {{this.owner}}
  - *Target Resolution*: {{this.target_date}}
{{/each}}
{{/if}}

{{#if timeline}}
### 📅 Detailed Timeline
{{#each timeline}}
- **{{this.phase}}**: {{this.start_date}} - {{this.end_date}}
  {{#if this.activities}}- Activities: {{this.activities}}{{/if}}
{{/each}}
{{/if}}

---

## 🏆 Milestone Achievement & Legacy

### ✅ Achievement Status
{{#if status == "completed"}}
- **Achievement Date:** {{achievement_date}}
- **Final Outcome:** {{achievement_outcome}}
- **Impact Level:** {{impact_level}}/10
- **Key Learnings:** {{key_learnings}}

{{#if save_as_legacy}}
### 📚 Legacy Preservation
This milestone will be saved as legacy content for future reference.

- **Legacy Type:** {{legacy_type|enum:technique,process,innovation,knowledge|default:technique}}
- **Legacy Impact:** {{legacy_impact|textarea}}
- **Reusability:** {{reusability|textarea}}
- **Archive Location:** uMEMORY/legacy/milestones/{{milestone_name|slugify}}/
{{/if}}
{{/if}}

---

## 🔗 Milestone Integration

**uDOS Context:**
- **Milestone ID:** {{milestone_name | slugify}}
- **Parent Mission:** [{{parent_mission}}]({{parent_mission_link}})
- **Dashboard Tracking:** {{#if dashboard_tracking}}✅ Active{{else}}❌ Not configured{{/if}}
- **Memory Integration:** {{#if memory_integration}}✅ Connected{{else}}❌ Not integrated{{/if}}

{{#if related_milestones}}
### 🔄 Related Milestones
{{#each related_milestones}}
- [{{this.name}}]({{this.link}}) - {{this.relationship}}
{{/each}}
{{/if}}

{{#if documentation}}
### 📚 Documentation & References
{{#each documentation}}
- [{{this.title}}]({{this.url}}) - {{this.type}}
{{/each}}
{{/if}}

---

**Generated:** {{generated_date}}
**Template Version:** v1.0.4.1
**uDOS Version:** v1.0.4.1
**Last Updated:** {{last_updated}}
