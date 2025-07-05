# NetHack.md

## 🧙 NetHack-Inspired User Roles and Lore Structure

uOS integrates a NetHack-style fantasy structure to map account types, privileges, and legacy features in a gamified, retro-fantasy setting. This structure introduces thematic immersion, nostalgic gameplay, and a scaffold for learning through exploration and ASCII-rich interaction.

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
