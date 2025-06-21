# 🌀 uOS — The User Operating System

**uOS** is a single-process, Markdown-native, terminal-first operating system designed to give old devices new life and intelligent memory.  
It is for thinkers, tinkerers, writers, and dreamers — those who want a machine that remembers, evolves, and serves a singular user.

---

## 🌱 Vision

- **Human-first, single-user design**: uOS runs for *you* — not the cloud, not corporations.
- **Markdown as the OS language**: Every Move, Mission, Milestone, and Map lives in plain `.md`.
- **Process minimalism**: One shell, one thread, one memory — a living notebook with intent.
- **Memory with purpose**: All actions form a legacy, built from Moves and Missions over time.
- **Cross-platform longevity**: Runs on modern macOS or Docker Desktop — but also thrives on old, repurposed machines.

---

## 🧠 Core Concepts

| Term         | Description                                                             |
|--------------|-------------------------------------------------------------------------|
| **Move**     | A single input/output action — the atomic thought in uOS                |
| **Mission**  | A goal or project, composed of many moves                               |
| **Milestone**| A significant checkpoint on the way to completing a Mission             |
| **Legacy**   | Archived results or final output from a completed uOS instance          |
| **uMemory**  | Your personal memory: logs, state, and active history                   |
| **uKnowledge** | Shared Markdown reference knowledge, maps, guides, and general info   |

---

## 📁 Repo Structure

```text
/uOS
├── docker-compose.yml         # Docker container setup (root-level)
├── Dockerfile                 # Base image configuration
├── macos/                     # macOS launchers (.app and .command)
├── roadmap/                   # Living uOS design documents
├── scripts/                   # Core logic: uCode CLI, dashboard, tools
├── templates/                 # Markdown templates for move, mission, etc.
├── uKnowledge/                # General Markdown knowledge store
├── uMemory/                   # User memory: logs, state, sessions, moves
├── sandbox/                   # Draft workspace for in-progress documents
├── repo_structure.txt         # Auto-generated directory tree
└── README.md                  # You're reading it
```

---

## 🚀 Running uOS

uOS is containerized via Docker but also supports macOS native launchers and legacy hardware.

### 🐳 Docker (Cross-platform)

#### ✅ Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- This repo cloned to: `~/uOS`

#### 🌀 Launch

```bash
bash macos/Launch-uOS.command
```

This will:

1. Stop any previous uOS containers
2. Rebuild the container with current scripts
3. Launch uOS into the `uCode` CLI shell

#### 🛠️ Common Troubleshooting

- **Volume Mount Errors**  
  Ensure the repo is located at `~/uOS`, or update paths in `docker-compose.yml`.

- **Docker Not Running**  
  The launcher auto-starts Docker if needed.

---

### 🍏 macOS Native

- Double-click `macos/Launch🌀uOS.app` for a GUI entrypoint.
- Use `macos/Quit-uOS.command` to cleanly stop the container.
- All `.app` internals are excluded from version control.

---

### 💾 Legacy / Offline Mode

uOS is designed to run as a memory shell on:
- Older repurposed laptops (via lightweight Linux + Docker)
- Offline environments (scripts can run without cloud)
- Experimental builds with no container layer (in progress)

---

## 📊 Roadmap Preview

✅ = complete / working  
🔄 = in progress / evolving

- ✅ Terminal CLI (`uCode`)
- ✅ Markdown Move/Mission logging
- ✅ Live ASCII Dashboard (`dash`)
- ✅ Recent Moves Tracker
- ✅ Error logging, session logging
- 🔄 Milestone & Legacy archiving
- 🔄 Map + Location engine (Tower of Knowledge)
- 🔄 Device lifetime tracking
- 🔄 Proximity-based sharing logic
- 🔄 Tour Mode (offline personal assistant)

---

## 🧬 Collaboration

This is a **co-created system** between:

- **Wizard**: The user and architect of uOS.
- **Otter**: The AI assistant and memory-keeper within uOS.

As of version **v1.4.2**, the assistant has been formally named **Otter**.

Every session, file, command, and map is part of this collaboration.
We build together. We remember together.

---

## 🧬 Philosophy

uOS is not an operating system in the conventional sense — it is a **memory companion**.

It does not multitask.  
It does not update itself silently.  
It does not forget.

Every session, every thought, every command — written in Markdown.  
Tracked as Moves.  
Built toward a Mission.  
Stored as a Legacy.

---

**Built by you. Remembered by uOS. Powered by Markdown.**  
*Guided by Otter 🦦 — your memory keeper.*

