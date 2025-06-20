# Milestone Template – uOS

Milestones are units of meaningful progress within uOS. Each Milestone contributes to a Mission or Legacy and is composed of individual atomic Moves (input/output).

---

## 🪜 Milestone Template (Markdown)

```markdown
# Milestone: <title>

## 🪜 ID
milestone_<mission-id>_<index>

## 📅 Created
YYYY-MM-DD

## 🧠 Context
- Mission ID: mission_<slug>
- Associated Moves: move_<id>, move_<id>, ...
- Related Files: uKnowledge/..., uScript/...

## 🔄 Status
in-progress | complete | reversed | pending

## 📍 Description
Concise explanation of what this Milestone represents and its intended impact.

## 🧾 Activity Log
- [YYYY-MM-DD] Move ID: move_<id> — "User defined X"
- [YYYY-MM-DD] Move ID: move_<id> — "Script executed Y"
```

---

## 🔁 Key Features

* Milestones can be **reversed**, unlike Moves.
* Each Milestone connects upward to a Mission and downward to a list of related Moves.
* Milestone state affects Dashboard display and map logic.
