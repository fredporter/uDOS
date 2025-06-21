# uKnowledge Storage & Offload Plan – uOS

## 📦 Overview

The `uKnowledge` directory holds all knowledge artifacts in uOS. This includes missions, milestones, legacy entries, shared data, and private reflections. It evolves over time and may grow significantly depending on usage.

This plan defines:

* Storage structure
* Index and metadata files
* Offload policy
* Re-import model for archived Markdown

---

## 🧱 Directory Layout

```plaintext
/uOS/uKnowledge/
├── bank/                 # Core knowledge entries (flat or nested)
│   ├── index.md          # Searchable index of topics
│   ├── map_logic.md
│   └── ...
├── missions/             # Each mission = 1 .md file
│   ├── mission_uos_001.md
│   └── ...
├── milestones/           # Milestones = 1 .md file each
│   ├── milestone_uos_001_001.md
│   └── ...
├── legacies/             # Final records sealed at EOL
│   └── legacy_wizardowl_001.md
├── moves/                # Single-file chronological ledger
│   └── move_log.md
├── shared/               # Collaborative or published content
│   ├── public/
│   ├── project/
│   ├── collective/
│   └── transient/
├── private/              # User-only or controlled access knowledge
│   ├── personal/
│   ├── depersonalized/
│   ├── controlled/
│   └── limited/
└── archive/              # Compressed, offloaded knowledge vaults
    ├── knowledge_2025_Q2.zip
    └── legacy_wizardowl_001.md
```

---

## 🗂️ Metadata Conventions

Every folder with dynamic entries includes:

* `index.md` → topic-ordered links
* `meta.json` → timestamped, machine-parsable keys

Example `/missions/index.md`:

```markdown
# Mission Index

- [Build the uKnowledge System](missions/mission_uos_001.md)
- [Establish Wizard Vault](/missions/mission_uos_002.md)
```

---

## 📤 Offload Strategy

* When storage exceeds threshold (e.g. 1000 markdown files), archive older content:

  * `.zip` or `.tar.gz` format
  * Signed with system hash for authenticity
  * Optionally encrypted with user-defined passphrase
* Archived in `/uKnowledge/archive/`
* Triggers Move log entry + adds archive pointer to dashboard

---

## 🔁 Reimport

Archived content may be:

* Extracted into a temporary `tmp_restore/` namespace
* Reviewed by user (with prompts)
* Manually restored into active folders or sealed in `legacies/`

---

## 🧭 Next Step

Would you like to define the `/uKnowledge/archive/` `.meta.json` schema next, or generate the first `bank/index.md` to begin tracking knowledge topics?
