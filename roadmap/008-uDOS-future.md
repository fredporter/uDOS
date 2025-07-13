# 008-uDOS-future.md
# uDOS Beta v1.6.1 – Future Package Integrations

This roadmap outlines future GitHub integrations planned for `uDOS/src/pkg/`. Each tool is selected for its minimal footprint, offline compatibility, and usefulness in a terminal-centric operating system.

---

## 📦 Planned Package Integrations

| Name      | Type       | Purpose                            | Status     |
|-----------|------------|------------------------------------|------------|
| `micro`   | Text Editor| Core TUI text editing              | ✅ Integrated (Beta) |
| `nethack` | Game       | ASCII roguelike game               | 🚧 In Progress |
| `figlet`  | ASCII Tool | Big text banners                   | ✅ Integrated |
| `toilet`  | ASCII Tool | Fancy figlet (filters/colors)      | 🔜 Planned |
| `boxes`   | ASCII Tool | Draw boxes around terminal text    | 🔜 Planned |
| `nnn`     | File Mgmt  | Minimal terminal file browser      | 🔜 Planned |
| `jrnl`    | Log Tool   | Personal journaling CLI            | 🔜 Planned |
| `bat`     | Viewer     | Enhanced `cat` with syntax         | 🔜 Planned |
| `fd`      | Search     | Fast `find` tool                   | 🔜 Planned |
| `ripgrep` | Search     | Fast `grep` alternative            | 🔜 Planned |
| `glow`    | Viewer     | Render Markdown in terminal        | 🔜 Planned |
| `tldr`    | Docs       | Simplified man pages               | 🔜 Planned |
| `pfetch`  | System     | Pretty system summary              | 🔜 Planned |

---

## 📁 Integration Structure (per tool)

Each package lives at: `uDOS/src/pkg/<name>/`

### Required Files:
- `install.sh` — Installer (from source or binary)
- `run.sh` — Launch script (called via `uCode run <name>`)
- `README.md` — Usage, notes, integration info
- `check.sh` — Optional system check (for `uCode check`)
- `Dockerfile` — Optional fallback container (airgapped use)

---

## 🧩 Integration Milestones

### 📅 Q3 2025 Goals
- [ ] Finalize `nethack` installation and sandboxing
- [ ] Fork and localize `toilet`, `boxes`, `nnn`
- [ ] Add `uCode new` templates: `ascii`, `explore`, `journal`
- [ ] Integrate `jrnl` with `uMemory/moves-YYYY-MM-DD.md`
- [ ] Enable `bat`, `fd`, and `ripgrep` for content indexing
- [ ] Add `tldr` to support inline documentation
- [ ] Display `pfetch` in `uCode dash`

---

## 📘 Notes

- All installs are sandboxed in `$HOME/.local/` or `sandbox/pkg/`
- No runtime dependencies on package managers
- Markdown-based documentation for each tool added to `uKnowledge/pkg/`

---

## 📎 Suggested Usage Examples

```bash
# View markdown as rendered ASCII
uCode run glow uKnowledge/001-toolchain-roadmap.md

# Quick journal entry
uCode run jrnl "Today I debugged the install.sh script."

# Explore uMemory
uCode run nnn uMemory/

# Search Markdown logs
uCode run rg "ssh key" uMemory/

# Visual disk check
uCode run duf

🔁 Fork Targets (Canonical)

For each package, fork and pin:

micro      → https://github.com/zyedidia/micro
nethack    → https://github.com/NetHack/NetHack
figlet     → https://github.com/cmatsuoka/figlet
toilet     → https://github.com/cacalabs/toilet
boxes      → https://github.com/ascii-boxes/boxes
nnn        → https://github.com/jarun/nnn
jrnl       → https://github.com/jrnl-org/jrnl
bat        → https://github.com/sharkdp/bat
fd         → https://github.com/sharkdp/fd
ripgrep    → https://github.com/BurntSushi/ripgrep
glow       → https://github.com/charmbracelet/glow
tldr       → https://github.com/tldr-pages/tldr
pfetch     → https://github.com/dylanaraps/pfetch

✳️ Each integration should follow uDOS Q3 packaging standards: local-by-default, single-binary preferred, zero internet use after install.

---

Let me know if you'd like me to now scaffold the folders and `.sh` files for any specific tool above (e.g. `toilet`, `boxes`, or `nnn`) so you can start testing integrations locally.