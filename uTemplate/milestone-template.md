# 🪜 Milestone: {{title}}

> Summary: {{summary}}
> Author: {{username}}, Last Edited: {{iso8601}}

---

## Section 1: Purpose

{{description}}

---

## Section 2: Details

### 🧠 Context

* **Mission ID:** {{mission\_id}}
* **Associated Moves:**
  {{#each moves}}

  * {{this}}
    {{/each}}
* **Related Files:**
  {{#each files}}

  * {{this}}
    {{/each}}

### 🔄 Status

{{status}}

### 🧾 Activity Log

{{#each activity}}

* \[{{date}}] {{entry}}
  {{/each}}

---

## Section 3: Metadata

```yaml
id: milestone-{{slug}}
type: milestone
title: "{{title}}"
mission: {{mission_id}}
moves:
  {{#each moves}}
  - {{this}}
  {{/each}}
files:
  {{#each files}}
  - {{this}}
  {{/each}}
tags: [{{tags}}]
created: {{iso8601}}
last_edited: {{iso8601}}
user: {{username}}
status: {{status}}
version: uDOS Beta v1.6.1
```
