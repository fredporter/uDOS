_uDOS v1.6.1 format_

# uDOS Move Log Roadmap (`uCode` Loop Protocol)

This document defines the logging behaviour at the beginning of each loop cycle in `uCode`, the user interaction shell within uDOS.

---

## 🔁 Loop Start: Move Logging

At the **start of each loop**, `uCode` captures a minimal **Move Log Entry**, appending it to the current day’s **daily move log** file in the user's sandbox folder.

### 📍 File Location

```
/uMemory/logs/moves-YYYY-MM-DD.md
```

### 🛠 What Gets Logged

Each entry includes:

- `Timestamp` – full 24h `HH:MM:SS.mmm`
- `Location` – current uMap tile code (e.g. F180327)
- `Input` – user command or raw input (prefixed `🌀→`)
- `Output` – single-line feedback or result (prefixed `💬←`)

This ensures that every user-driven action is timestamped and locationally grounded for future inspection or replay.

> Example Log Entry:

```markdown
🌀→ DASH | F180327 | 14:02:55.493
💬← ✅ Dashboard displayed.
```

---

## 📦 Daily Move Log Commit

At the end of the 24h session (or on manual trigger), the current log is moved into local persistent memory:

```
/uMemory/logs/moves-YYYYMMDD.md
```

This finalised `.md` file becomes read-only and serves as a durable, inspectable record of all user inputs for that day.

---

## 🧠 Purpose

- Provide **minimal but complete traceability** of session activity
- Enable future replay, summarisation, or audit of user-driven events
- Maintain a lightweight, human-readable log format consistent with Markdown-based uDOS design

---

## ✅ Summary

| When       | What                                | Where                                   |
| ---------- | ----------------------------------- | ----------------------------------------|
| Loop Start | Log input/output with timestamp     | `/uMemory/logs/moves-YYYY-MM-DD.md`     |
| Day’s End  | Finalise log to flat history        | `/uMemory/logs/moves-YYYYMMDD.md`       |

---
