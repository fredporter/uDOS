---
title: Demo Story
type: story
version: "1.0.0"
description: "Simple demo story template."
submit_endpoint: "/api/setup/story/submit"
submit_requires_admin: false
---

# Demo Story

Lightweight sample story for testing the Wizard story renderer.

---

```story
name: demo_name
label: Demo name
type: text
required: true
placeholder: "Type your name"
```

```story
name: demo_choice
label: Demo option
type: select
required: true
options:
  - yes: Yes
  - no: No
```

---

✅ Demo complete.
