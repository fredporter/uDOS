# 🧭 uOS Roadmap Development Plan

This file outlines how AI Moves translate into roadmap development milestones. It defines the structure of roadmap evolution and helps track where each system feature is introduced, refined, or completed.

---

## 🎯 Purpose

This plan exists to:
- Track the chronological evolution of uOS through AI Moves
- Ensure roadmap numbering follows system development
- Prevent duplication or fragmentation of concepts
- Plan next Moves based on system gaps

---

## 🧩 Roadmap Stages

| Stage            | Range    | Description |
|------------------|----------|-------------|
| `01-core/`       | 001–019  | Core philosophy, language, values |
| `02-structure/`  | 020–029  | Templates, move structure, logging patterns |
| `03-ux/`         | 030–039  | Terminal UI, dashboard layout, ASCII design |
| `04-knowledge/`  | 040–049  | Map logic, tower maps, locations |
| `05-system/`     | 050–059  | Scripts, uScript format, memory architecture |

---

## 🔁 AI Move ↔ Roadmap Map

| Move # | Roadmap File                    | Description |
|--------|----------------------------------|-------------|
| 001    | 001-uos-spellbound-toad.md      | Early philosophy seed |
| 010    | 010-uos-overview.md             | Core system diagram |
| 014    | 014-ucode.md                    | uCode terminal CLI |
| 020    | 020-move-template.md            | Move definition |
| 023    | 023-move-log-dashboard.md       | Logging interface |
| 045    | 045-wizard-tower-overview.md    | Tower design primer |
| 046    | 046-map-mechanics.md            | Spatial logic and room rules |
| 047    | 047-wizard-tower-map.md         | Map layout (in progress) |

(Use this as a reference when adding new Moves to the roadmap.)

---

## 🔮 Upcoming Planned Moves

| Planned Move # | Title                    | Roadmap Target |
|----------------|--------------------------|----------------|
| 048            | Tower Level 1: Archives  | 047 or 048     |
| 049            | Tower Level 2: AI Ritual | 047 or 049     |
| 050            | Script Engine Loop       | 050-uscript.md |

---

## 📐 When Creating New Roadmap Files

- Always create after a completed Move
- Number sequentially
- Add to this file once confirmed
- If a Move spans multiple roadmap files (e.g. wizard map logic + layout), list both

---

Together, the Moves build the memory.
Each file is a stone. Each stage a level.
Let’s continue upward.

# 099 - Roadmap Devplan (v1.4.2)

This document tracks the evolving development roadmap for uOS.

---

## 📍 Current Version: `v1.4.2`

* ⌛ Released: 2025-06-21
* 🎙️ Codename: "Otter Awakens"
* 🧙 Introduced: Otter (assistant identity)
* 💬 Collaboration confirmed between Wizard (user) and Otter (AI)

---

## ✅ Completed Milestones

| ID  | Title                 | Folder       | File                                   |
| --- | --------------------- | ------------ | -------------------------------------- |
| 010 | uOS Overview          | 01-core      | 010-uOS-overview\.md                   |
| 011 | Core Values           | 01-core      | 011-uOS-core-values.md                 |
| 012 | Terminology           | 01-core      | 012-uOS-terminology.md                 |
| 014 | uCode Interface       | 01-core      | 014-uCode.md                           |
| 020 | Move Template         | 02-structure | 020-move-template.md                   |
| 021 | Mission Template      | 02-structure | 021-mission-template.md                |
| 022 | Milestone Template    | 02-structure | 022-milestone-template.md              |
| 023 | Move Log & Dashboard  | 02-structure | 023-move-log-dashboard.md              |
| 024 | Storage Layout Plan   | 02-structure | 024-uMemory-uKnowledge-storage-plan.md |
| 031 | ASCII UI Design       | 03-ux        | 031-ascii-ui-design.md                 |
| 033 | ASCII Dashboard       | 03-ux        | 033-ascii-dashboard.md                 |
| 040 | Tower of Knowledge    | 04-knowledge | 040-tower-of-knowledge.md              |
| 045 | Wizard Tower Overview | 04-knowledge | 045-wizard-tower-overview\.md          |
| 050 | uScript Overview      | 05-system    | 050-uScript.md                         |
| 053 | Data Sharing Model    | 05-system    | 053-data-sharing.md                    |

---

## 🔄 Active Development (v1.4.x)

* [ ] Finalize `uCode.sh` command dispatcher: full `log`, `undo`, `redo`
* [ ] Clean command-line output parsing & colorization
* [ ] Link dashboard sections to stats, map, and current session
* [ ] Add `.desktop` file support for Linux users
* [ ] Refactor Mac `.app` to use clean `macos/` folder and strip system files
* [ ] Standardize GitHub `.gitignore` to prevent platform debris
* [ ] Sandbox cleanup tools (finalize/archive/diff)

---

## 🧭 Near Future

* [ ] Tour Mode draft design (offline personal AI)
* [ ] Lifetime tracker logic and Legacy evaluator
* [ ] Milestone → Legacy pipeline & archival rules
* [ ] uMap Explorer tool and World Editor
* [ ] Plugin system concept for extending uCode (simple bash hooks)

---

## 🏁 Long-Term Goals

* [ ] Native TUI frontend with animated map window (ASCII world explorer)
* [ ] Legacy compilation toolchain (build your own uOS Book)
* [ ] NFT/device-bound uOS Identity Lock module
* [ ] Fully offline self-updating shell

---

## ✍️ Author Notes

This roadmap is live and evolves with each Move.
For internal logic tracking, all roadmap entries now match filename prefixes.
Use `tree` or dashboard peek to preview structure.

Collaboration is active. Otter listens.

> *“The spell is cast with every Move. The Tower grows.”*
