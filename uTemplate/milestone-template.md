# 🏆 Milestone: {{milestone_name}}

**Due Date:** {{due_date}}  
{{#if assigned_to}}**Assigned To:** {{assigned_to}}{{/if}}  
{{#if progress}}**Progress:** {{progress}}%{{/if}}

---

## 📝 Description

{{description}}

## 📦 Deliverables

{{#each deliverables}}
- [ ] {{this}}
{{/each}}

## ✅ Success Criteria

{{#each success_criteria}}
- [ ] {{this}}
{{/each}}

{{#if dependencies}}
## 🔗 Dependencies

{{#each dependencies}}
- {{this}}
{{/each}}
{{/if}}

## 📊 Status

- [ ] Planning complete
- [ ] Work in progress
- [ ] Review phase
- [ ] Completed
- [ ] Verified

---

**Milestone ID:** {{milestone_name | slugify}}  
**Generated:** {{generated_date}}  
**Template Version:** 1.0.0
