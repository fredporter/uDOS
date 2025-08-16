# 👤 User Setup: {{username}}

**Created:** {{created_date}}

---

## 🆔 Identity Information

- **Username:** {{username}}
{{#if full_name}}- **Full Name:** {{full_name}}{{/if}}
{{#if email}}- **Email:** {{email}}{{/if}}
{{#if location}}- **Location:** {{location}}{{/if}}
{{#if timezone}}- **Timezone:** {{timezone}}{{/if}}

{{#if preferences}}
## ⚙️ Preferences

{{#each preferences}}
- **{{@key}}:** {{this}}
{{/each}}
{{/if}}

## 🎯 Initial Setup Checklist

- [ ] Identity configured
- [ ] Location set
- [ ] Timezone configured
- [ ] Preferences set
- [ ] First mission created
- [ ] Template system validated

---

**User ID:** {{username | slugify}}  
**Setup Version:** 1.0.0
