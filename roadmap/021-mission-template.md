# uOS Mission Template

A **Mission** in uOS defines a future or in-progress purpose. Missions remain persistent even after completion, unless elevated to **Legacy** at the end-of-life (EOL) phase of the user's installation.

---

## 📘 Template Structure (Markdown)

```markdown
# Mission: <title>

## 🧭 Mission ID
mission_<slug>_<index>

## 🏷️ Tags
#learning #self #project #system

## 🗓️ Created
2025-05-27

## 🔄 Status
in-progress | planned | paused | complete

## 🎯 Description
Brief mission purpose and philosophical context.

## 🪜 Milestones
- [ ] milestone_001: Define knowledge taxonomy
- [ ] milestone_002: Draft bank index and search
- [ ] milestone_003: Build memory binding logic


## 🧠 Related Concepts
- uCode interface blocks: `[mission:status]`
- Map Tile: `A2` (Wizard Tower — Archive Wing)

## 📜 Legacy Potential
Flag: eligible | not-eligible | predefined
```

---

## 🔄 Key Relationships

* **Mission** links to 1+ **Milestones**
* **Milestones** may be:

  * Achieved (✔)
  * Reversible (↩️)
  * Archived at EOL into **Legacy**
* **Moves** (Input/Output operations) are atomic, and may trigger milestone creation or update

---

## 🔂 Redefinitions

* **Move**: A single atomic I/O event in uOS. Like a message or script call. Stateless.
* **Milestone**: A goal-related unit of progression. Tracks meaningful progress. Reversible.
* **Mission**: A persistent objective composed of Milestones.
* **Legacy**: A sealed archive of missions + milestones defined at EOL.
