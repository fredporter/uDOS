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

### 📚 Tome of Ancestors (Legacy System)

* Structured markdown archive.
* ASCII-styled with `(code)` blocks and `{anchors}`.
* Configurable EOL: `Resurrect`, `Tomb`, or `Transform` into Ghost.

---

## 🧩 Game Mechanics & ASCII-Driven Exploration

### 🎮 Dungeon Maps

* Retro ASCII-style (160x90 grid).
* Each map zone defined as a `(code)` block:

```md
(code)
+-------------------------+
|      🧙 Wizard's Keep     |
|  🧪 Potions  📜 Spells     |
+-------------------------+
(code)
```

### 🧰 Interactive Items

Each item invokes a `uScript` container. For example:

```md
(code)
[scroll_of_transfer]
call python spell-scroll.py with args: 'encrypt knowledge', output to /lore/scrolls
(code)
```

### 🐉 Encounters

* Triggers quests or puzzles.
* Written as `(code)` logic blocks:

```md
(code)
if player_class == 'Sorcerer' and has_item('talisman'):
    call python trial.py with args: 'initiate test'
(code)
```

---

## 📦 uScript Integration

All scripted logic is run via the `uScript` container engine.

### 🔁 Pattern

```md
(code)
call python {script}.py with args: {arguments}, output to /data/vault
(code)
```

### 🔒 Secure Calls

* All calls sandboxed.
* Only pre-approved container scripts allowed.
* Results returned as Markdown `(code)` blocks and saved to Tome.

---

## 🔄 Progression Loop

| Stage       | Action Type          | Description                                          |
| ----------- | -------------------- | ---------------------------------------------------- |
| 🧱 Entry    | Explore              | Navigate ASCII dungeons.                             |
| 🗺️ Mapping | Design               | Use blocks to build zones.                           |
| ✍️ Coding   | Learn uBASIC/uScript | Use `uBASIC` to trigger `uScript` containers.        |
| 🛠️ Project | Create Mechanisms    | Develop interactive objects, triggers, and outcomes. |
| 🧠 Mastery  | Legacy Mode          | Finalize Tome and create resurrection paths.         |

---

## 🤝 Collaboration

* Public zones are shared via `[Spellbound-Toad]` network.
* Proximity required to transfer Lore (physical-first philosophy).
* Shared Tombs use markdown replication with EOL signing.

---

## 📌 Example Shortcode Quest Chain

```md
(code)
[quest: knowledge-delve]
require_class: Sorcerer
step1: call python decipher.py with args: "scroll_of_lore"
step2: map new zone to /vault/cavern-lore
reward: +20 XP, unlock zone: Forgotten Library
(code)
```

---

## 🔗 Related Modules

* \[uBASIC.md]: Markdown logic interface with ASCII+shortcode.
* \[uScript.md]: Shell and Python container system.
* \[uOS.md]: Root OS design document.

---

**Next:** Review \[uScript.md] to define container structure, security, and API for `call python`, `call shell`, and input/output patterns.
