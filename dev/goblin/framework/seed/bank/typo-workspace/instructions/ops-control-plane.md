# Ops Control Plane Permission Grid

| capability | label | guest | operator | admin | section |
| --- | --- | --- | --- | --- | --- |
| view_planning | Planning visibility | deny | allow | allow | planning |
| view_automation | Automation visibility | deny | allow | allow | automation |
| retry_queue | Retry deferred queue work | deny | allow | allow | planning |
| manage_alerts | Acknowledge and resolve alerts | deny | allow | allow | automation |
| manage_workflows | Approve and escalate workflows | deny | allow | allow | planning |
| create_jobs | Create and import jobs | deny | allow | allow | planning |
| manage_settings | Change scheduler and control settings | deny | deny | allow | control |
| view_system | See system mode | deny | deny | allow | system |
| view_logs | Browse logs | deny | deny | allow | system |
| view_config | Inspect managed config status | deny | deny | allow | system |
| view_releases | Inspect release surface | deny | deny | allow | system |
