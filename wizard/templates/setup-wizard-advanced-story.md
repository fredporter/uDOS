---
title: Wizard Advanced Setup Story
type: story
version: "1.0.0"
description: "Advanced Wizard setup details (user profile extensions)."
submit_endpoint: "/api/v1/setup/story/submit"
submit_requires_admin: true
---

# User Profile (Advanced)

These fields extend the base setup story with optional details. Where possible, existing
values should be kept or refined.

```story
name: user_permissions
label: User permissions (optional)
type: textarea
required: false
placeholder: "Describe any custom permissions or notes"
```

---
