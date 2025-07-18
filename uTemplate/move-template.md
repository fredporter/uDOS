# Template: Move - {{action}}

**Move ID:** {{move_id}}  
**Timestamp:** {{timestamp}}  
{{#if duration}}**Duration:** {{duration}} minutes{{/if}}

---

## 📝 Context

{{context}}

## 🎯 Expected Outcome

{{expected_outcome}}

{{#if actual_outcome}}
## ✅ Actual Outcome

{{actual_outcome}}
{{/if}}

{{#if tags}}
## 🏷️ Tags

{{#each tags}}
- {{this}}
{{/each}}
{{/if}}

---

**Generated:** {{generated_date}}  
**Template Version:** 1.0.0
