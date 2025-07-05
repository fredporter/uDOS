# 🌀 uDOS — The User DOS Shell

**uDOS** is a single-process, Markdown-native, terminal-first operating system designed to give old devices new life and intelligent memory.  
It is for thinkers, tinkerers, writers, and dreamers — those who want a machine that remembers, evolves, and serves a singular user.

---

## 🌱 Vision

- **Human-first, single-user design**: uDOS runs for *you* — not the cloud, not corporations.
- **Markdown as the OS language**: Every Move, Mission, Milestone, and Map lives in plain `.md`.
- **Process minimalism**: One shell, one thread, one memory — a living notebook with intent.
- **Memory with purpose**: All actions form a legacy, built from Moves and Missions over time.
- **Cross-platform longevity**: Runs on modern macOS or Docker Desktop — but also thrives on old, repurposed machines.

---

## 🧠 Core Concepts

| Term         | Description                                                             |
|--------------|-------------------------------------------------------------------------|
| **Move**     | A single input/output action — the atomic thought in uDOS                |
| **Mission**  | A goal or project, composed of many moves                               |
| **Milestone**| A significant checkpoint on the way to completing a Mission             |
| **Legacy**   | Archived results or final output from a completed uDOS instance          |
| **uMemory**  | Your personal memory: logs, state, and active history                   |
| **uKnowledge** | Shared Markdown reference knowledge, maps, guides, and general info   |

---

## 📁 Repo Structure

```text
/uDOS
├── docker-compose.yml         # Docker container setup (root-level)
├── Dockerfile                 # Base image configuration
├── macos/                     # macOS launchers (.app and .command)
├── roadmap/                   # Living uDOS design documents
├── scripts/                   # Core logic: uCode CLI, dashboard, tools
├── templates/                 # Markdown templates for move, mission, etc.
├── uKnowledge/                # General Markdown knowledge store
├── uMemory/                   # User memory: logs, state, sessions, moves
├── sandbox/                   # Draft workspace for in-progress documents
├── repo_structure.txt         # Auto-generated directory tree
└── README.md                  # You're reading it
```

---

## 🚀 Running uDOS

uDOS is containerized via Docker but also supports macOS native launchers and legacy hardware.

### 🐳 Docker (Cross-platform)

#### ✅ Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- This repo cloned to: `~/uDOS`

#### 🌀 Launch

```bash
bash macos/Launch-uDOS.command
```

This will:

1. Stop any previous uDOS containers
2. Rebuild the container with current scripts
3. Launch uDOS into the `uCode` CLI shell

#### 🛠️ Common Troubleshooting

- **Volume Mount Errors**  
  Ensure the repo is located at `~/uDOS`, or update paths in `docker-compose.yml`.

- **Docker Not Running**  
  The launcher auto-starts Docker if needed.

---

### 🍏 macOS Native

- Double-click `macos/Launch🌀uDOS.app` for a GUI entrypoint.
- Use `macos/Quit-uDOS.command` to cleanly stop the container.
- All `.app` internals are excluded from version control.

---

### 💾 Legacy / Offline Mode

uDOS is designed to run as a memory shell on:
- Older repurposed laptops (via lightweight Linux + Docker)
- Offline environments (scripts can run without cloud)
- Experimental builds with no container layer (in progress)

---

## 🗺️ Roadmap Index

For full architecture, system structure, and design documents, see [`roadmap/`](roadmap/):

- [001-uDOS-foundation.md](roadmap/001-uDOS-foundation.md) — Core principles, terminology, mission structure
- [002-uDOS-format.md](roadmap/002-uDOS-format.md) — Templates, filenames, dashboard format, move logging
- [003-uDOS-execution.md](roadmap/003-uDOS-execution.md) — uCode runtime and uScript automation logic
- [004-uDOS-interface.md](roadmap/004-uDOS-interface.md) — ASCII UI design, UX philosophy, display modes
- [005-uDOS-location.md](roadmap/005-uDOS-location.md) — Tile logic, map mechanics, cross-device data sharing

---

## 🧬 Collaboration

This is a **co-created system** between:

- **Wizard**: The user and architect of uDOS.
- **Otter**: The AI assistant and memory-keeper within uDOS.

As of version **Beta v1.6.1**, the assistant has been formally named **Otter**.

Every session, file, command, and map is part of this collaboration.
We build together. We remember together.

---

## 🧬 Philosophy

uDOS is not an operating system in the conventional sense — it is a **memory companion**.

It does not multitask.  
It does not update itself silently.  
It does not forget.

Every session, every thought, every command — written in Markdown.  
Tracked as Moves.  
Built toward a Mission.  
Stored as a Legacy.

---

**uDOS Beta v1.6.1** — memory-bound and Markdown-powered.  
🦦 Otter active. Listening, logging, learning.
