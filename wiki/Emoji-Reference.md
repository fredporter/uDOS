# Emoji Reference

Complete list of `:emoji:` codes available in uPY v1.1.9+.

## Overview

uPY supports 80+ emoji codes that automatically convert to Unicode characters in PRINT statements. This makes your scripts more visual and engaging without requiring special input methods.

## Usage

```upy
PRINT(":heart: HP: 100")
PRINT(":sword: Attack!")
PRINT(":check: Quest Complete!")
```

**Output:**
```
❤️ HP: 100
⚔️ Attack!
✅ Quest Complete!
```

---

## Emoji Categories

### Status Indicators

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:check:` | ✅ | Quest Complete! |
| `:cross:` | ❌ | Failed |
| `:warning:` | ⚠️ | Low Health! |
| `:info:` | ℹ️ | Information |
| `:star:` | ⭐ | Achievement Unlocked |
| `:heart:` | ❤️ | Health/HP |
| `:ok:` | 👌 | Perfect! |
| `:thumbsup:` | 👍 | Good job! |

**Example:**
```upy
PRINT(":check: Mission complete!")
PRINT(":warning: Health below 20%")
PRINT(":star: Level up!")
```

---

### Game Items

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:sword:` | ⚔️ | Attack weapon |
| `:shield:` | 🛡️ | Defense equipment |
| `:bow:` | 🏹 | Ranged weapon |
| `:axe:` | 🪓 | Heavy weapon |
| `:potion:` | 🧪 | Health/Mana potion |
| `:coin:` | 🪙 | Currency/Gold |
| `:gem:` | 💎 | Precious stones |
| `:diamond:` | 💠 | Rare gems |
| `:key:` | 🔑 | Unlock doors |
| `:chest:` | 📦 | Treasure chest |
| `:map:` | 🗺️ | World map |
| `:scroll:` | 📜 | Quest scroll |
| `:book:` | 📖 | Spell book |
| `:hammer:` | 🔨 | Crafting tool |
| `:wrench:` | 🔧 | Repair tool |
| `:pick:` | ⛏️ | Mining tool |

**Example:**
```upy
PRINT(":sword: Iron Sword (+15 ATK)")
PRINT(":potion: Health Potion (Restore 50 HP)")
PRINT(":coin: Gold: $GOLD")
```

---

### Status Effects

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:fire:` | 🔥 | Fire damage/buff |
| `:ice:` | ❄️ | Ice/Freeze effect |
| `:poison:` | ☠️ | Poisoned status |
| `:skull:` | 💀 | Death/Critical |
| `:heal:` | 💚 | Healing effect |
| `:magic:` | ✨ | Magic/Mana |
| `:bolt:` | ⚡ | Lightning attack |
| `:zap:` | ⚡ | Electric damage |
| `:sparkles:` | ✨ | Magic sparkle |
| `:dizzy:` | 💫 | Stunned |
| `:boom:` | 💥 | Explosion |

**Example:**
```upy
PRINT(":fire: Burning! (5 DMG/turn)")
PRINT(":magic: MP: $MP/$MP-MAX")
PRINT(":boom: Critical hit!")
```

---

### Directions & Navigation

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:north:` | ⬆️ | Move north |
| `:south:` | ⬇️ | Move south |
| `:east:` | ➡️ | Move east |
| `:west:` | ⬅️ | Move west |
| `:up:` | ⏫ | Ascend/Up |
| `:down:` | ⏬ | Descend/Down |
| `:updown:` | ↕️ | Vertical |
| `:leftright:` | ↔️ | Horizontal |
| `:compass:` | 🧭 | Navigation |
| `:pin:` | 📍 | Location marker |

**Example:**
```upy
PRINT(":compass: Current location: Sydney")
PRINT(":north: Move north to forest")
PRINT(":pin: Checkpoint saved")
```

---

### UI Elements

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:menu:` | ☰ | Main menu |
| `:search:` | 🔍 | Search/Find |
| `:settings:` | ⚙️ | Settings menu |
| `:gear:` | ⚙️ | Configuration |
| `:save:` | 💾 | Save game |
| `:load:` | 📂 | Load file |
| `:exit:` | 🚪 | Exit/Leave |
| `:door:` | 🚪 | Enter/Exit |
| `:home:` | 🏠 | Home/Base |
| `:bell:` | 🔔 | Notification |
| `:flag:` | 🚩 | Flag/Marker |
| `:target:` | 🎯 | Target/Goal |

**Example:**
```upy
PRINT(":menu: Main Menu")
PRINT(":save: Game saved successfully")
PRINT(":target: Quest objective updated")
```

---

### Nature & Environment

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:sun:` | ☀️ | Daytime/Sunny |
| `:moon:` | 🌙 | Nighttime |
| `:cloud:` | ☁️ | Cloudy weather |
| `:rain:` | 🌧️ | Rainy weather |
| `:snow:` | 🌨️ | Snowy weather |
| `:tree:` | 🌲 | Forest/Trees |
| `:mountain:` | ⛰️ | Mountain terrain |
| `:water:` | 💧 | Water/Droplet |

**Example:**
```upy
PRINT(":sun: Morning arrives")
PRINT(":rain: It starts to rain")
PRINT(":tree: Dense forest ahead")
```

---

### Creatures & Enemies

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:dragon:` | 🐉 | Dragon enemy |
| `:snake:` | 🐍 | Snake creature |
| `:spider:` | 🕷️ | Spider enemy |
| `:bat:` | 🦇 | Bat creature |
| `:wolf:` | 🐺 | Wolf enemy |
| `:bear:` | 🐻 | Bear creature |
| `:ghost:` | 👻 | Ghost enemy |
| `:alien:` | 👽 | Alien creature |

**Example:**
```upy
PRINT(":dragon: Ancient Dragon appears!")
PRINT(":ghost: A ghost floats nearby")
```

---

### Emotions & Reactions

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:smile:` | 😊 | Happy/Pleased |
| `:happy:` | 😄 | Very happy |
| `:sad:` | 😢 | Sad/Crying |
| `:angry:` | 😠 | Angry/Mad |
| `:surprised:` | 😲 | Surprised |
| `:cool:` | 😎 | Cool/Confident |
| `:scared:` | 😱 | Scared/Afraid |
| `:sick:` | 🤢 | Sick/Ill |
| `:sleep:` | 😴 | Sleeping |
| `:zzz:` | 💤 | Sleep effect |
| `:think:` | 🤔 | Thinking |
| `:sweat:` | 😅 | Nervous |

**Example:**
```upy
PRINT(":smile: NPC: Welcome, traveler!")
PRINT(":scared: You feel a chill down your spine")
```

---

### Numbers & Symbols

| Code | Emoji | Usage Example |
|------|-------|---------------|
| `:zero:` | 0️⃣ | Number 0 |
| `:one:` | 1️⃣ | Number 1 |
| `:two:` | 2️⃣ | Number 2 |
| `:three:` | 3️⃣ | Number 3 |
| `:four:` | 4️⃣ | Number 4 |
| `:five:` | 5️⃣ | Number 5 |
| `:six:` | 6️⃣ | Number 6 |
| `:seven:` | 7️⃣ | Number 7 |
| `:eight:` | 8️⃣ | Number 8 |
| `:nine:` | 9️⃣ | Number 9 |
| `:ten:` | 🔟 | Number 10 |

**Example:**
```upy
PRINT(":one: First quest")
PRINT(":star::star::star: 3-star rating")
```

---

### Special Characters (Escaping)

When you need to display characters that have special meaning in uPY syntax:

| Code | Character | Use Case |
|------|-----------|----------|
| `:lbrack:` | `[` | Left square bracket |
| `:rbrack:` | `]` | Right square bracket |
| `:lparen:` | `(` | Left parenthesis |
| `:rparen:` | `)` | Right parenthesis |
| `:lbrace:` | `{` | Left curly brace |
| `:rbrace:` | `}` | Right curly brace |
| `:langle:` | `<` | Left angle bracket |
| `:rangle:` | `>` | Right angle bracket |
| `:quot:` | `"` | Double quote |
| `:apos:` | `'` | Apostrophe/Single quote |
| `:backtick:` | `` ` `` | Backtick |
| `:laquo:` | `«` | Left guillemet |
| `:raquo:` | `»` | Right guillemet |
| `:lsaquo:` | `‹` | Left single guillemet |
| `:rsaquo:` | `›` | Right single guillemet |

**Example:**
```upy
PRINT("Score: :lbrack:100:rbrack:")  # Output: Score: [100]
PRINT("He said :quot:Hello:quot:")   # Output: He said "Hello"
```

---

### Typography

| Code | Symbol | Name |
|------|--------|------|
| `:rarr:` | → | Right arrow |
| `:larr:` | ← | Left arrow |
| `:uarr:` | ↑ | Up arrow |
| `:darr:` | ↓ | Down arrow |
| `:rrarr:` | ⇒ | Double right arrow |
| `:llarr:` | ⇐ | Double left arrow |
| `:bullet:` | • | Bullet point |
| `:circle:` | ◦ | Circle |
| `:square:` | ▪ | Square |
| `:diamond:` | ◆ | Diamond |
| `:ndash:` | – | En dash |
| `:mdash:` | — | Em dash |
| `:hellip:` | … | Ellipsis |
| `:middot:` | · | Middle dot |
| `:nbsp:` | (space) | Non-breaking space |

**Example:**
```upy
PRINT(":bullet: Quest item")
PRINT("Option A :rarr: Village")
```

---

### Legal & Copyright

| Code | Symbol | Name |
|------|--------|------|
| `:copy:` | © | Copyright |
| `:reg:` | ® | Registered trademark |
| `:tm:` | ™ | Trademark |

---

### Math & Logic

| Code | Symbol | Name |
|------|--------|------|
| `:plus:` | + | Plus sign |
| `:minus:` | − | Minus sign |
| `:times:` | × | Multiplication |
| `:divide:` | ÷ | Division |
| `:equals:` | = | Equals |
| `:not:` | ¬ | Not/Negation |
| `:approx:` | ≈ | Approximately |
| `:infinity:` | ∞ | Infinity |
| `:lt:` | < | Less than |
| `:gt:` | > | Greater than |
| `:le:` | ≤ | Less than or equal |
| `:ge:` | ≥ | Greater than or equal |
| `:ne:` | ≠ | Not equal |

**Example:**
```upy
PRINT("Damage: 50 :times: 2 = 100")
PRINT("HP :ge: 50: Healthy")
```

---

### Currency

| Code | Symbol | Name |
|------|--------|------|
| `:dollar:` | $ | US Dollar |
| `:euro:` | € | Euro |
| `:pound:` | £ | British Pound |
| `:yen:` | ¥ | Japanese Yen |

---

## Complete Example

```upy
# RPG Combat with Emojis
$HP = 100
$ENEMY-HP = 50

PRINT("")
PRINT(":star::star::star: COMBAT :star::star::star:")
PRINT("")
PRINT(":shield: Your HP: $HP")
PRINT(":dragon: Enemy HP: $ENEMY-HP")
PRINT("")
PRINT(":sword: Attack! :boom: Critical hit!")
PRINT(":fire: Enemy takes 25 damage")
PRINT("")
PRINT(":check: Victory!")
PRINT(":coin: Loot: 100 gold")
PRINT(":sparkles: +50 XP")
```

---

## Best Practices

### Do ✅
- Use emojis to enhance readability
- Choose appropriate emojis for context
- Use consistently throughout your script
- Combine with descriptive text

### Don't ❌
- Overuse emojis (readability suffers)
- Use emojis as sole communication
- Mix emoji styles inconsistently
- Forget the colons (`:emoji:` not `emoji`)

---

## Technical Notes

- Emoji replacement happens at preprocessor stage
- Converted to Unicode before execution
- No performance impact
- Works in PRINT statements only
- Case-insensitive (`:Heart:` = `:heart:`)

---

## See Also

- [Function Programming Guide](Function-Programming-Guide.md)
- [uCODE Language Reference](uCODE-Language.md)
- [Migration Guide v1.1.9](Migration-Guide.md)
- [Command Reference](Command-Reference.md)

---

**Version**: uDOS v1.1.9+
**Total Emoji Codes**: 80+
**Source**: `core/interpreters/upy_preprocessor.py`
