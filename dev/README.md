# /dev - Development Workspace

**Purpose**: Local development workspace for uDOS contributors. This folder is primarily gitignored to keep the distribution repository clean.

---

## Structure

### `/dev/planning/` ✅ GIT TRACKED
Roadmaps, feature specifications, and release planning documents that contributors need.

- **roadmap/** - Long-term vision (v1.1.0+)
- **features/** - Feature specifications and designs
- **releases/** - Release planning and checklists

### `/dev/archive/` ❌ NOT TRACKED
Historical development notes, session summaries, and completed phase documentation.

- **v1.0.x/** - All v1.0 series development history
  - sessions/ - Session summaries
  - phases/ - Phase completion reports
  - summaries/ - Development summaries
  - docs-original/ - Original /docs folder content
- **historical/** - Older archived content

### `/dev/notes/` ❌ NOT TRACKED
Personal developer notes, scratch work, and unformed ideas.

- **scratch/** - Temporary working files
- **ideas/** - Brainstorming and concepts

### `/dev/tools/` ✅ GIT TRACKED (Optional)
Development utilities and scripts useful for contributors.

- **scripts/** - Helper scripts for development tasks

---

## Git Tracking Strategy

**Tracked**:
- `/dev/README.md` (this file)
- `/dev/planning/` (roadmaps and specs)
- `/dev/tools/` (shared dev utilities)

**Gitignored**:
- `/dev/archive/` (local dev history)
- `/dev/notes/` (personal notes)

---

## For Contributors

1. **Roadmap planning** → Use `/dev/planning/roadmap/`
2. **Feature specs** → Use `/dev/planning/features/`
3. **Release notes** → Use `/dev/planning/releases/`
4. **Personal notes** → Use `/dev/notes/` (gitignored)
5. **Development utilities** → Use `/dev/tools/scripts/`

Keep `/dev/archive/` for your own session notes and development history - these are local-only and won't clutter the repository.

---

## Relationship to Other Folders

- **/core** - Read-only system code (tracked)
- **/knowledge** - Read-only knowledge base (tracked)
- **/extensions** - Read-only extensions (tracked)
- **/memory** - User workspace (gitignored, template tracked)
- **/dev** - Development workspace (mostly gitignored)
- **/wiki** - Public documentation (tracked separately)

---

**Note**: This folder structure supports clean separation between production code, user content, and development work.
