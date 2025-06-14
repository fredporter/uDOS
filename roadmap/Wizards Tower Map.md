## Wizard's Tower Map (Sample Zone)

```ascii
+-------------------------+
| [S]tairs    ▒▒▒▒▒▒▒▒▒▒▒ |
|             ▒     ▒   ▒ |
|   ▒▒▒▒▒▒▒▒▒ ▒ [L] ▒   ▒ |
|   ▒     ▒ ▒ ▒     ▒   ▒ |
|   ▒ [M] ▒ ▒ ▒▒▒▒▒▒▒▒▒ ▒ |
|   ▒     ▒ ▒           ▒ |
|   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ |
+-------------------------+
```

### Tile Legend
- `[S]` = Stairs (Entry/Exit to tower levels)
- `[M]` = Mission (future-bound goal, interactive)
- `[L]` = Legacy (past knowledge/memory archive)
- ▒ = Wall/Boundary

### uScript Triggers (Pseudocode)
```markdown
(code: mission_trigger)
```bash
#!/bin/bash
# Triggered when user moves onto [M]
echo "Mission activated: Solve the elemental puzzle in the Tower library."
uscript run puzzle_solver.py
```

(code: legacy_viewer)
```python
# Triggered when user visits [L]
from utils import display_legacy

display_legacy("wizard_ancestor.json")
```

### Shortcodes
- `(map:trigger:mission_trigger)` on tile `[M]`
- `(map:trigger:legacy_viewer)` on tile `[L]`

### Example Interaction (uBASIC Terminal)
```text
> step north
You have entered the Archive Room.
📜 Legacy available. (map:trigger:legacy_viewer)
> view legacy
"Displaying: The Origins of uOS Magic Stack..."
```

---
Next step: Shall we add more tile types (like `[K]` for Knowledge)? Or connect the tower map to another zone?
