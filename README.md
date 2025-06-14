Here is your updated README.md for the root of the ~/uOS repo, combining the Docker usage instructions and the uOS vision:

⸻


# 🌀 uOS — The User Operating System

uOS is a single-process, Markdown-native, terminal-first operating system designed to give old devices new life and intelligent memory.  
It is for thinkers, tinkerers, writers, and dreamers — those who want a machine that remembers, evolves, and serves a singular user.

---

## 🌱 Vision

- **Human-first, single-user design**: uOS runs for *you* — not the cloud, not corporations.
- **Markdown as the OS language**: Every Move, Mission, Log, and Map lives in plain-text `.md`.
- **Process minimalism**: One shell, one brain, one thread — like a living notebook.
- **Memory with purpose**: All interactions build toward Milestones, Mission completion, and Legacy.

---

## 🧠 Core Concepts

| Term       | Meaning                                                        |
|------------|----------------------------------------------------------------|
| **Move**   | A single input/output step, like a thought or command          |
| **Mission**| A defined goal or task sequence                                |
| **Milestone**| A major progress checkpoint on a Mission                     |
| **Legacy** | Preserved outputs from a completed uOS lifetime                |
| **uKnowledge** | The memory structure of all markdown knowledge             |

---

## 📁 Repo Structure

/uOS
├── src/                   # uCode shell scripts and interface logic
├── uKnowledge/           # Markdown memory bank (logs, missions, state, etc.)
├── roadmap/              # Living documentation and development vision
├── repo_structure.txt    # Dynamically generated tree of this repo
├── Launch-uOS.command    # Launcher script for Docker-based execution
├── docker-compose.yml    # Docker container configuration
├── README.md             # This file

---

## 🐳 Run uOS with Docker

uOS is containerized via Docker to isolate system memory and runtime.

### ✅ Prerequisites

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Ensure Docker is running before launching uOS

### 🚀 Launching

Use the included `.command` launcher:

```bash
~/uOS/Launch-uOS.command

This script will:
	1.	Stop any previous uOS containers
	2.	Rebuild the container to apply updates
	3.	Run uOS interactively and drop you into the uCode CLI

🛠️ Troubleshooting

If you see:

invalid spec: :/app: empty section between colons

… it means Docker couldn’t locate the right mount path. Make sure:
	•	You have the repo at ~/uOS
	•	You’re not relying on unset environment variables

⸻

🛣️ Roadmap Preview
	•	✅ Markdown CLI Shell (uCode)
	•	✅ Knowledge logging system (moves.md, milestones/, etc.)
	•	🔄 ASCII Dashboard UI
	•	🔄 Mission & Milestone Tracker
	•	🔄 Lifetime tracking
	•	🔄 Map/Location engine
	•	🔄 Tower of Knowledge exploration
	•	🔄 Offline-first Tour mode
	•	🔄 Personal hardware recognition & identity lock

⸻

🧬 Philosophy

uOS is not an operating system in the conventional sense — it’s a memory companion.
It stores your thoughts as Markdown. It remembers. It evolves with your intent.
Each interaction matters. Each session has value.
When the instance ends, the Legacy remains.

⸻

Built by you. Remembered by uOS. Powered by Markdown.

