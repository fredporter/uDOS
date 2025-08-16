# 📊 {{title}}

**Generated:** {{generated_date}}  
**User:** {{user_name}}

---

{{#if active_missions}}
## 🎯 Active Missions

{{#each active_missions}}
### {{this.name}}
- **Priority:** {{this.priority}}
- **Progress:** {{this.progress}}%
- **Due:** {{this.due_date}}

{{/each}}
{{/if}}

{{#if recent_moves}}
## 🔄 Recent Activity

{{#each recent_moves}}
- **{{this.timestamp}}** - {{this.action}}
{{/each}}
{{/if}}

{{#if system_stats}}
## 📈 System Statistics

- **Total Missions:** {{system_stats.missions}}
- **Total Moves:** {{system_stats.moves}}
- **Total Milestones:** {{system_stats.milestones}}
- **System Health:** {{health_status}}
{{/if}}

---

**Dashboard Version:** 1.0.0  
**System:** uDOS Alpha v1.0.0
