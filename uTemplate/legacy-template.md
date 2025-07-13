# 🧓 Legacy Entry: {{title}}

> Summary: {{summary}}
> Author: {{username}}, Last Edited: {{iso8601}}

---

## Section 1: Purpose

{{description}}

---

## Section 2: Details

### 🧠 Origin Context

* **Mission ID:** {{mission\_id}}
* **Retired Milestone(s):**
  {{#each milestones}}

  * {{this}}
    {{/each}}
* **Associated Moves:**
  {{#each moves}}

  * {{this}}
    {{/each}}

### 📜 Legacy Notes

{{notes}}

### 🏷️ Type

{{legacy\_type}}
(e.g. `system`, `user-process`, `external-doc`, etc.)

---

## Section 3: Metadata

```yaml
id: legacy-{{slug}}
type: legacy
title: "{{title}}"
mission: {{mission_id}}
milestones:
  {{#each milestones}}
  - {{this}}
  {{/each}}
moves:
  {{#each moves}}
  - {{this}}
  {{/each}}
tags: [{{tags}}]
created: {{iso8601}}
last_edited: {{iso8601}}
user: {{username}}
legacy_type: {{legacy_type}}
status: archived
version: uDOS Beta v1.7.1
```
