# Missions / Jobs / Tasks schema (v0)

- Task: atomic action
- Job: scheduled runnable unit
- Mission: long-running programme (goal + jobs + constraints)

## Job frontmatter
```md
---
type: job
id: job_daily_summarise
schedule: "RRULE:FREQ=DAILY;BYHOUR=2;BYMINUTE=0;BYSECOND=0"
task_type: summarise
privacy: local_preferred
targets: ["01_KNOWLEDGE/"]
outputs: ["06_RUNS/job_daily_summarise/"]
---
```
