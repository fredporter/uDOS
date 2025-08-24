# 👤 User Setup: [TERM] {USERNAME}

**Created:** [TERM] {CREATED-DATE | <FORMAT-TIMESTAMP>}

---

## 🆔 Identity Information

- **Username:** [TERM] {USERNAME}
[IF] {FULL-NAME}
- **Full Name:** [TERM] {FULL-NAME}
[/IF]
[IF] {EMAIL}
- **Email:** [TERM] {EMAIL}
[/IF]
[IF] {LOCATION}
- **Location:** [TERM] {LOCATION | <RESOLVE-LOCATION>}
[/IF]
[IF] {TIMEZONE}
- **Timezone:** [TERM] {TIMEZONE | <FORMAT-TIMEZONE-FULL>}
[/IF]

[IF] {PREFERENCES}
## ⚙️ Preferences

[EACH] {PREFERENCES}
- **[TERM] {@KEY | <HUMANIZE-KEY>}:** [TERM] {THIS | <FORMAT-PREFERENCE>}
[/EACH]
[/IF]

## 🎯 Initial Setup Checklist

[WITH] [GET-RETRIEVE] {SETUP-STATUS | USERNAME}
- [[IF] {IDENTITY-CONFIGURED}x[ELSE] [/IF]] Identity configured
- [[IF] {LOCATION-SET}x[ELSE] [/IF]] Location set
- [[IF] {TIMEZONE-CONFIGURED}x[ELSE] [/IF]] Timezone configured
- [[IF] {PREFERENCES-SET}x[ELSE] [/IF]] Preferences set
- [[IF] {FIRST-MISSION-CREATED}x[ELSE] [/IF]] First mission created
- [[IF] {TEMPLATE-SYSTEM-VALIDATED}x[ELSE] [/IF]] Template system validated
[/WITH]

---

**User ID:** [TERM] {USERNAME | <SLUGIFY>}
**Setup Version:** [GET-RETRIEVE] {SYSTEM-VERSION}
**Template Version:** v1.3.3
