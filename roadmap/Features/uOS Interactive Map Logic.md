# uOS Interactive Map Logic: `step-check`

> The `step-check` logic container controls tile accessibility on the uOS Map based on a user's current life phase: Steps (present), Memory (past), or Legacy (future). Each tile on the map reflects an unlock state that adapts to user progress.

---

## 🧩 Tile States

| Tile State    | Description                        | Visual Marker | Access Condition            |
| ------------- | ---------------------------------- | ------------- | --------------------------- |
| `Locked`      | Not yet available                  | `█`           | Steps not yet completed     |
| `In Progress` | Currently active memory or mission | `▒`           | Step reached, not completed |
| `Complete`    | A completed memory or mission      | `░`           | Step marked as complete     |
| `Legacy`      | Preserved record from past lives   | `◘`           | Legacy data inherited       |

---

## 🔁 Shortcode Syntax for `step-check`

Use this shortcode block to dynamically check tile state:

```markdown
[step-check id="M05" type="memory"]
  [if locked] This memory is hidden. Complete earlier steps to reveal it. [/if]
  [if in-progress] You are recalling memory M05. Finish to archive it. [/if]
  [if complete] This memory has been recorded. Well done. [/if]
  [if legacy] ✨ This is a memory from a prior life. [/if]
[/step-check]
```

Each `id` links to a structured step node defined in the user state file. These can be loaded via `uScript` container `memory-query.sh`.

---

## 🧠 Container Pattern: `memory-query.sh`

```bash
#!/bin/bash
# Usage: ./memory-query.sh <step-id>

STEP_ID="$1"
DB_PATH="~/.uos/user_state/memory.db"

STATE=$(sqlite3 "$DB_PATH" "SELECT state FROM steps WHERE id = '$STEP_ID';")

case "$STATE" in
  locked)
    echo "locked"
    ;;
  in_progress)
    echo "in-progress"
    ;;
  complete)
    echo "complete"
    ;;
  legacy)
    echo "legacy"
    ;;
  *)
    echo "unknown"
    ;;
esac
```

Ensure the container is executable and mapped to the `step-check` shortcode renderer.

---

## 🧭 Example Map Tile With Logic

```markdown
# 📍 Tile M05 - The First Memory
[step-check id="M05" type="memory"]
  [if locked] 🔒 You must first remember who you are.
  [/if]
  [if in-progress] 🧠 You're starting to recall early dreams.
  [/if]
  [if complete] ✅ You remembered this fragment of your origin.
  [/if]
  [if legacy] ✨ An echo from a life once lived.
  [/if]
[/step-check]
```

---

## 🔮 Next Step

Would you like to now:

* Define the `.db` schema for `steps`, `missions`, and `memories`?
* Or establish the first tile matrix of the default Map layout?
