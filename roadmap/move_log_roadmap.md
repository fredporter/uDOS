# uOS Move Log Roadmap (`ucode.sh` Loop Protocol)

This document defines the logging behaviour at the beginning of each loop cycle in `ucode.sh`, the user interaction shell within uOS.

---

## 🔁 Loop Start: Move Logging

At the **start of each loop**, `ucode.sh` captures a minimal **Move Log Entry**, appending it to the current day’s **daily move log** file in the user's sandbox folder.

### 📍 File Location

```
/sandbox/daily-move-log-YYYY-MM-DD.md
```

### 🛠 What Gets Logged

Each entry includes:

- `Timestamp` – ISO format or 24h `HH:MM`
- `Location` – current uMap coordinate or context node
- `Input` – the raw user command or text input

This ensures that every user-driven action is timestamped and locationally grounded for future inspection or replay.

> Example Log Entry:

```markdown
## [09:42] @ /world/village/square
> look around
```

---

## 📦 Daily Move Log Commit

At the end of the 24h session (or on manual trigger), the current log is moved into local persistent memory:

```
/uMemory/logs/2025-06-22.md
```

This finalised `.md` file becomes read-only and serves as a durable, inspectable record of all user inputs for that day.

---

## 🧠 Purpose

- Provide **minimal but complete traceability** of session activity
- Enable future replay, summarisation, or audit of user-driven events
- Maintain a lightweight, human-readable log format consistent with Markdown-based uOS design

---

## ✅ Summary

| When       | What                                | Where                                   |
| ---------- | ----------------------------------- | --------------------------------------- |
| Loop Start | Log timestamp, location, user input | `/sandbox/daily-move-log-YYYY-MM-DD.md` |
| Day’s End  | Archive full log                    | `/uMemory/logs/YYYY-MM-DD.md`           |

---

