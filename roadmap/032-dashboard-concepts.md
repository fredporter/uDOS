# uOS Dashboard — Specification

## Purpose
The uOS Dashboard serves as the user's live mission control panel. It aggregates personal progress and uMemory state into a single screen view.

---

## 🧩 Core Sections

### 🧭 1. TODAY'S FOCUS
- **Active Mission**: Top-level goal or long-term user intention.
- **Active Milestone**: Sub-goal related to current Mission.
- **Suggested Next Move**: Intelligent pointer 
- **Location**: Current region within the user's Map structure.

### 📜 2. RECENT MOVES
- Chronological list of last 5 executed Moves.
- Each Move includes:
  - ✔️ Status
  - Description snippet
  - Timestamp

### 🗺️ 3. MAP PEEK
- ASCII minimap of current user region
- Shows visited areas and next directions
- Interconnected nodes (e.g. `[Creative Valley] --> [Structure Peak]`)


# uOS Dashboard

## Overview

The **Dashboard** is the single-entry summary view of the user’s current state in uOS. It is composed entirely of Markdown and ASCII, and is dynamically generated at each session entry or on request.

## Core Sections

- **Today’s Focus**:
  - Currently active Mission or Milestone.
  - Suggested next Move.
  - Location pointer.

- **Recent Moves**:
  - Last 5–10 user Moves with context snippets.
  - Linked to full Move logs.

- **Map Peek**:
  - ASCII visualization of current Region with unlocked paths.

- **Tower Snapshot**:
  - Recent updates to uKnowledge.
  - New rooms/floors added.

- **Health Check**:
  - System status: logs, syncs, encryption flags, pending exports.

## Interaction Model

- Markdown-formatted cards or boxes.
- Collapsible views based on verbosity preference.
- Hyperlinked summaries to respective .md files.
