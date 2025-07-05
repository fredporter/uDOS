---
title: "uDOS Roadmap Index"
version: "Beta v1.6.1"
id: "roadmap-index"
tags: ["roadmap", "index", "navigation", "docs"]
created: 2025-07-05
updated: 2025-07-05
---

# 🧭 uDOS Roadmap Index

This document provides a top-level overview of the core roadmap files in the uDOS system. Each roadmap defines a foundational area of the OS architecture, runtime logic, or user experience.

---

## 📘 Roadmap Files

### 001. [uDOS Foundation](001-uDOS-foundation.md)
Core principles, terminology, mission/move structure, and NetHack integration strategy that shape the uDOS environment.

### 002. [uDOS Template & Format Guide](002-uDOS-format.md)
Markdown-based standards for:
- Move, Mission, Milestone templates
- Logging architecture
- Filename and datetime formats
- Dashboard rendering spec

### 003. [uDOS Execution Model](003-uDOS-execution.md)
Describes the single-process runtime system:
- `uCode` — the shell and loop interface
- `uScript` — task engine, syntax, and logic examples

### 004. [uDOS Interface Philosophy](004-uDOS-interface.md)
Human-centered ASCII UX philosophy:
- Dashboard components
- Display modes
- Layout ethos and mockups

### 005. [uDOS Location & Map Logic](005-uDOS-location.md)
Spatial and cartographic model:
- Tile mechanics
- Base maps and uMap integration
- Data sharing across regions

### 006. [uDOS Future Concepts](006-uDOS-future.md)
Speculative and upcoming features, tools, and interface enhancements under consideration for future development.

---

## 🌀 Usage

These roadmap files are intended to remain versioned, minimal, and readable by both developers and AI agents.  
Each one may link out to supporting documents inside:
- `/uTemplate/` for reusable content structures
- `/scripts/` for executable logic
- `/uMemory/` for live state examples

Use `README.md` at root level for install/runtime.  
Use this `ROADMAP_INDEX.md` to navigate uDOS architecture and evolution.

---

