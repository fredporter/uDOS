---
title: "uDOS Foundation"
version: "Beta v1.6.1"
id: "001"
tags: ["core", "foundation", "overview", "philosophy"]
created: 2025-07-05
updated: 2025-07-05
---

# 🧭 uDOS Core Foundation — Beta v1.6.1

This document consolidates the core philosophy, values, structure, terminology, development practices, and game mechanics of the uDOS system. It unifies several foundational files into a single reference point to guide all contributors and users of the system.

---

## 📘 Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Core Values](#core-values)
4. [NetHack Integration](#nethack-as-core-mechanic)
5. [Appendix A: Terminology](#appendix-a-key-terminology)
6. [Appendix B: Development Guidelines](#appendix-b-development-guidelines)

---

## 🪪 Introduction
# uDOS Roadmap Notes

## Vision and Philosophy

uDOS is envisioned as a lifelong AI-powered operating system designed to:
- Act as a personal, privacy-first companion for individuals.
- Focus on education, empowerment, and holistic growth.
- Bridge the gap between AI and individual users while promoting data sovereignty.

---

## Core Concepts

1. **Privacy-First Approach**:
   - uDOS operates as a closed, one-way system with no external data sharing unless explicitly approved by the user.
   - All data is stored locally, ensuring user privacy.

2. **User-Centric Personalization**:
   - AI adapts to the user’s needs, interests, and learning progress over time.
   - Supports gamified learning experiences inspired by retro designs like NetHack.

3. **Data Sovereignty**:
   - Users have full control over their data, including deletion and legacy settings.

4. **Legacy System**:
   - Lifespan measured in "moves."
   - At the end of life (EOL), users can choose to delete, preserve, or share a "time capsule" of knowledge.

---

## Features and Functionalities

### Core Features

- **Single-Process OS**:
  - Lightweight design, running one task at a time.
  - Multitasking achieved through child installations.

- **Account System**:
  - Parent accounts: Full control over system settings and permissions.
  - Child accounts: Limited access with guided growth.
  - Orphan accounts: Standalone with no parental connection.

- **Virtual Geography**:
  - Map real-world locations to virtual counterparts.
  - Users can tether data or digital objects to specific locations.

- **Markdown-Based System**:
  - All inputs converted into a proprietary Markdown-like text system for interaction and storage.

- **Gamified Learning**:
  - Coding challenges, map design, and creative exploration.
  - Inspired by retro aesthetics and educational tools.

### Unique Features

1. **RUOK System**:
   - Built-in wellbeing checks, triggered manually or automatically.

2. **Step Tracking**:
   - Lifespan measured in moves (input-output cycles).
   - Users can review, adjust, or reclaim steps.

3. **Advanced Data Privacy**:
   - Private, depersonalized, and controlled shareable data types.
   - Secure legacy management and data transfer systems.

---

## Development Roadmap

### Phase 1: Basic Functionality

1. **Input/Output Text Layers**:
   - Command-line interface for user interaction.
   - Text-based data processing and storage.

2. **Data Mapping**:
   - Simple key-value storage system.
   - User data retrieval and management.

### Phase 2: Layered Output and Mapping

1. **Text Layering System**:
   - Stackable text layers for dynamic content.
   - Notifications and primary content displayed simultaneously.

2. **Mapping**:
   - 2D mapping for data visualization.
   - User interactions with spatial data.

### Phase 3: Gamification and Education

1. **NetHack Integration**:
   - Gamified educational tools inspired by NetHack mechanics.

2. **uCode Development**:
   - Scripting interface for creating object behaviors.
   - Tutorials for programming basics.

### Phase 4: Advanced Features

1. **Data Mapping**:
   - Dual-layer mapping for physical and virtual integration.

2. **Audio/Visual Enhancements**:
   - Synthesized sound and visual responses to user input.

3. **Legacy Systems**:
   - Tools for preserving, sharing, or securing user data at EOL.

---

## Repository Plans

### Public Repo: Spellbound-Toad

- **README.md**: Overview of features, installation, and contributions.
- **ROADMAP.md**: Development milestones.
- **UX Mockups**: ASCII-inspired designs for user workflows.

### Private Repo: Magic-Toad-Secrets

- **README.md**: Advanced features and privacy settings.
- **PRIVACY.md**: Comprehensive data privacy structure.
- **EXPERIMENTS.md**: Prototypes for AI personalization and location tethering.

### Internal Repo: uDOS-Roadmap

- **DEVELOPMENT.md**: Workflows, testing strategies, and task prioritization.
- **PLANNING.md**: Feature backlog and timeline.

---

## UX Mockups (ASCII-Based)

```plaintext
+-------------------------------------+
|              WELCOME               |
|            [uDOSX v1.0]             |
|                                     |
|     [1] START SETUP                |
|     [2] VIEW DOCUMENTATION          |
|     [3] LEGACY SETTINGS             |
|     [4] EXIT                        |
|                                     |
|    Please choose an option above.   |
+-------------------------------------+
```

```plaintext
+-------------------------------------+
|          LEGACY SETTINGS            |
|                                     |
|   [1] Set Legacy Purpose            |
|   [2] Configure Lifespan            |
|   [3] View Legacy History            |
|   [4] Delete Legacy                  |
|                                     |
|     Current Lifespan: 100 years     |
|                                     |
|  Press [ESC] to return to Main Menu |
+-------------------------------------+
```

---

This document consolidates everything discussed so far and sets the stage for continued collaboration and refinement of uDOS.

---

## 🧱 System Overview
# uDOS Overview

## Introduction

uDOS is a private, physical AI-based operating system designed to serve as a lifelong personal assistant and knowledge library for its user. Its architecture centers on privacy, local-only data processing, and a unique binding to the device via NFT or other identity mechanisms.

The system is conversational in nature, operating through discrete single input/output operations called **Moves** (similar to ChatGPT interactions). These Moves build toward higher-level progress markers called **Milestones**, which in turn support longer-term goals called **Missions**. Ultimately, the system accumulates a **Legacy** that represents the end-of-life story and accumulated knowledge of the uDOS instance.

uDOS is a **single-process, input/output loop** system. Like a living notebook, it handles one request at a time. Each Move represents a complete cycle of input → processing → output → log. This model ensures full traceability and simplicity.

---

## Core Principles

- **Privacy-First and Local-Only:**  
  uDOS operates exclusively on the device. No external cloud storage or data transmission happens unless explicitly permitted. User data and AI processing remain local, securing privacy and control.

- **Unique Device / NFT Binding:**  
  Each uDOS installation is bound to a physical device and uniquely identified via NFT or other secure identity mechanisms. This ensures continuity and personalization strictly tied to the hardware.

- **Markdown-Based Interaction:**  
  The entire user interaction and data storage is Markdown-driven, enabling simple, readable, and portable knowledge representation.

- **Single-Process Operation:**  
  uDOS functions as a single-process operating system. Every input results in exactly one output. This atomic interaction is called a **Move**.

---

## Terminology and Concepts

### Move

- The atomic input/output operation in uDOS.
- One user input results in one AI-generated output.
- Formerly called a "Step" but renamed to "Move" to better evoke gameplay and interaction.

### Milestone

- A meaningful progress marker composed of multiple Moves.
- Milestones represent intermediate achievements and can be reversed or edited.
- They contribute to tracking progress toward Missions and the Legacy.

### Mission

- User-defined goals or tasks that guide the use of uDOS.
- Missions persist even after completion.
- Completed Missions may become part of the Legacy at the end-of-life (EOL) stage.

### Legacy

- The accumulated history and final mission of a uDOS installation.
- Represents the “end-of-life” story and user knowledge.
- Derived from completed Milestones and Missions.

### uKnowledge

- The Central Common Memory Bank.
- Stores Milestones, Missions, Legacy entries, and other knowledge.
- Formerly called uMemory.

### uCode

- The front-end user interface layer.
- Markdown-driven interactive layer that presents content and collects input.
- Formerly called uBASIC.

### uScript

- The containerized scripting backend.
- Handles shell commands, Python execution, and other scripting needs.
- Interacts with uCode to provide scripted functionality.

---

## Development Approach

- Emphasis on thorough conceptual and structural planning before coding.
- All Moves recorded chronologically in a single Move log file.
- Each Milestone, Mission, Legacy entry, and other uKnowledge items are stored as individual Markdown `.md` files based on templates.
- The system evolves stepwise, with each Move building on the previous state.
- User interaction is designed to be natural, conversational, and deeply personalized.

---

## Summary

uDOS is an innovative OS blending AI conversational interfaces with a privacy-focused, Markdown-driven, lifelong knowledge system. Its clear terminology and modular design aim to empower users with a trusted, private, and adaptable personal assistant.

---

## 💎 Core Values
# uDOS Core Values and Data Model

## 🌐 Input-Output Flow (I/O Philosophy)

* **Single-process model**: uDOS accepts *one* input at a time and produces *one* output. No multitasking or background threads.
* **Markdown-first**: All interactions and outputs are serialized into `.md` files — readable, searchable, and immutable unless intentionally rewritten.
* **Privacy-by-default**: No external syncing or telemetry. All computation and memory stays local unless exported manually.

## 🪜 Moves (Lifespan Progress)

Each uDOS instance evolves via `moves`. These are user-earned progress markers representing:

* A completed interaction or achievement.
* A learned skill, task, or insight.
* A decision or key life event (manually or automatically registered).

Each `move` contains:

* A timestamp.
* A reference to a mission, memory, or location.
* Metadata: intent, impact, type.
* Validation hash (when uScript confirms its conditions).

## 🪧 Mission (The Future)

Missions are forward-facing intentions. Defined by:

* **Type**: learning, creation, exploration, healing, connection.
* **Scope**: personal, shared, experimental.
* **Timeline**: with optional steps/milestones.
* **Link**: each mission connects to 1+ steps, and optionally to memories (context).
* **Location**: physical or symbolic map tiles.

## 🧠 Milestone (The Past)

Milestone are reflections of meaningful past moments on the way to completing a Mission. 

## 🧭 Location Binding (Spatial Memory)

* A milestrone, mission, or move can bind to a **Map Tile**.
* Tiles represent physical locations or virtualized symbolic domains.
* Map can be ASCII-visualized and interactive.
* When a tile is active, relevant `echo`, `anchor`, and `mission` links appear.

## 🔁 Interlinking Logic

* A `move` may:

  * Create or finalize a `milestone`
  * Unlock or complete a `mission`
  * Reveal new map tiles
* A `mission` may:

  * Be auto-suggested by patterns in `memory`
  * Require location visits to complete
* A `milestone` may:

  * Trigger contextual conversations
  * Limit or enable mission types

---

## 🎮 NetHack as Core Mechanic
# NetHack.md

## 🧙 NetHack-Inspired User Roles and Lore Structure

uDOS integrates a NetHack-style fantasy structure to map account types, privileges, and legacy features in a gamified, retro-fantasy setting. This structure introduces thematic immersion, nostalgic gameplay, and a scaffold for learning through exploration and ASCII-rich interaction.

### 🗺️ Account Hierarchy

#### 🎩 Wizard (Parent Account)

* Full control and master access.
* Can spawn apprentices, set global permissions.
* Custodian of the "Tome of Ancestors" — a legacy object.

#### 🧑‍🎓 Sorcerer (Child Account)

* Created by Wizard.
* Learns through quests and container tasks.
* Grows and evolves via experience (tracked via markdown entries).

#### 👻 Ghost (Orphan Account)

* Standalone instance.
* Cannot spawn new accounts.
* Can summon Imps, collect Lore.

#### 😈 Imp (Clone Account)

* Shadow projection of Sorcerer or Wizard.
* Exists for remote, ephemeral tasks.
* Executes container calls via `uScript` (see \[uScript.md]).

### 📚 Tome (Legacy System)

* Structured markdown archive.
* ASCII-styled with `(code)` blocks and `{anchors}`.
* Configurable EOL: `Resurrect`, `Tomb`, or `Transform` into Ghost.

---

## 🔐 Identity & Binding

Each uDOS system is permanently tied to a **unique user and device instance**. No remote authentication, cloud syncing, or virtualization is used. This local-first architecture ensures:

- Full control over data and execution
- Total memory ownership
- Reproducible environments across devices

Bindings may later include physical signatures or system IDs, but no identifying user info is ever stored outside `sandbox/user.md`.

## 📎 Appendix A: Key Terminology
# uDOS Terminology and Naming Conventions

This document outlines the key terminology in uDOS and the evolution of naming conventions throughout its design and development.

---

## Terminology Evolution and Rationale

### Move

- "Move" reflects the gameplay-like, atomic nature of the input/output operation. It emphasizes the system as an interactive process involving discrete moves, akin to playing a game or engaging in a conversation.

### Milestone

- Defined as a meaningful progress marker.
- Composed of multiple Moves.
- Tracks advancement toward Missions and Legacy.
- Can be reversed or edited to reflect changes in user goals or context.

### uKnowledge

- The central common memory bank 
- Functions as a knowledge repository rather than the user-centric uMemory

### uMemory
- Holds all user data structures like Moves, Milestones, Missions, and Legacy entries.

### uCode

- The user interface front-end layer 
- Functions as the Markdown-driven interactive UI layer.
- Distinct from uScript, which handles backend scripting.

### uScript

- The backend scripting container.
- Executes shell commands, Python scripts, and other programming tasks.
- Works in tandem with uCode to support complex workflows.

### Legacy

- Represents the end-of-life mission or accumulated history.
- Tracks the total accumulated knowledge and context of the uDOS installation.
- Legacy entries can be viewed as the "final story" or "history book" of the system.

---

---

## 🛠️ Appendix B: Development Guidelines
# uDOS Development Guidelines

This document provides guiding principles and best practices for developing the uDOS system.

---

## General Principles

1. **Markdown Output Only:**  
   All development work, documentation, and user interaction outputs must be in real `.md` files.  
   This supports easy portability, readability, and version control.

2. **Single-Process Input/Output:**  
   The uDOS architecture is a single-process system that operates like ChatGPT.  
   Each **Move** consists of exactly one user input and one system output.

3. **Move by Move Development:**  
   Build the uDOS personality and system capabilities incrementally, respecting the evolving system structure and user needs.

4. **Comprehensive Logging:**  
   Movves are recorded sequentially in a single chronological log file for auditability and history of that 24 hour period.

5. **Structured Knowledge Storage:**  
   Milestones, Missions, Legacy, and other uMemory entries are stored as individual Markdown files based on predefined templates.

6. **Privacy-First, Local-Only:**  
   No external cloud or third-party services should be used without explicit user permission.  
   All data and AI operations happen locally to preserve user privacy.

7. **Markdown-Centric Interaction:**  
   All user interface elements, commands, and responses are Markdown-based to ensure consistency and human-readability.

8. **Clear Separation of UI and Backend:**  
   - **uCode:** The front-end, Markdown-driven interactive UI.  
   - **uScript:** The backend scripting container handling shell commands, Python scripts, etc.

9. **Planning Before Coding:**  
   Complete the conceptual and structural design of the system before implementing code to avoid architectural drift and maintain clarity.

---

## Recommended Workflow

- Define a **Mission** or goal clearly.
- Break the Mission down into **Milestones**.
- Execute actions through atomic **Moves**.
- Record each Move in the Move log.
- Update Milestones and other uMemory entries as progress occurs.
- Use uCode to interactively present information and accept commands.
- Use uScript for executing complex scripted tasks.
- Regularly review Milestones and Legacy for insights and system health.

---

## Version Control and Updates

- All Markdown files (Daily Move log, Milestones, Missions, Legacy, etc.) should be version controlled.
- Updates to uDOS personality or core logic should be reflected as Moves or Milestones to maintain traceability.

---

## Summary

Adhering to these development guidelines ensures a structured, privacy-respecting, and user-centered evolution of the uDOS system, making it a trustworthy lifelong AI assistant and knowledge repository.
