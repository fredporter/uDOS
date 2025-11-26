# Teletext Pattern Examples

Comprehensive collection of teletext patterns for uSCRIPT use.

## Ocean Patterns

### Deep Ocean
```
████████████████████
████████████████████
████████████████████
```
**Character:** `█` (full block)
**Usage:** `PANEL TERRAIN map 0 0 100 50 ocean_deep`

### Ocean Gradient (Deep to Shallow)
```
████████████████████
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
░░░░░░░░░░░░░░░░░░░░
```
**Pattern:** Deep (█) → Ocean (▓) → Shallow (▒) → Coast (░)

### Water Waves
```
≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~
~≈~≈~≈~≈~≈~≈~≈~≈~≈~≈
≈~≈~≈~≈~≈~≈~≈~≈~≈~≈~
```
**Pattern:** `waves`
**Usage:** `PANEL PATTERN map 0 0 20 10 waves`

## Land Patterns

### Plains
```
····················
 · · · · · · · · · ·
····················
```
**Character:** `·` (middle dot)

### Grassland
```
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
```
**Character:** `≈` (almost equal)

### Forest
```
♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠
 ♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠
♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠ ♠
```
**Character:** `♠` (spade)
**Pattern:** Staggered placement for natural look

### Dense Jungle
```
♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣
♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣♣
```
**Character:** `♣` (club)

### Desert
```
∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴
∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴∴
```
**Character:** `∴` (therefore)

## Elevation Patterns

### Hills
```
    ∩    ∩∩    ∩
  ∩∩∩∩  ∩∩∩∩  ∩∩∩
∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩
```
**Character:** `∩` (intersection)

### Mountains
```
    ▲        ▲
   ▲▲▲      ▲▲▲
  ▲▲▲▲▲    ▲▲▲▲▲
 ▲▲▲▲▲▲▲  ▲▲▲▲▲▲▲
```
**Character:** `▲` (triangle)

### Mountain Range
```
  ▲   ▲▲  ▲    ▲▲▲
 ▲▲▲ ▲▲▲▲▲▲▲  ▲▲▲▲▲
▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩∩
```
**Pattern:** Peaks (▲) on hills (∩)

## Urban Patterns

### Sparse Urban
```
▪  ▪    ▪  ▪   ▪
   ▪  ▪    ▪  ▪
▪    ▪  ▪    ▪
```
**Character:** `▪` (small square)

### City
```
■ ■ ■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■ ■ ■
```
**Character:** `■` (large square)

### Metropolitan
```
●●●●●●●●●●●●●●●●●●●●
●●●●●●●●●●●●●●●●●●●●
●●●●●●●●●●●●●●●●●●●●
```
**Character:** `●` (circle)

## Gradient Patterns

### 4-Step Gradient (Dark to Light)
```
████████████████████
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
░░░░░░░░░░░░░░░░░░░░
```
**Sequence:** `█ ▓ ▒ ░`

### Smooth Vertical Gradient
```
████▓▓▓▓▒▒▒▒░░░░
████▓▓▓▓▒▒▒▒░░░░
████▓▓▓▓▒▒▒▒░░░░
```

### Smooth Horizontal Gradient
```
██▓▒░
██▓▒░
██▓▒░
```

## Decorative Patterns

### Checkerboard
```
█░█░█░█░█░█░█░█░█░█░
░█░█░█░█░█░█░█░█░█░█
█░█░█░█░█░█░█░█░█░█░
░█░█░█░█░█░█░█░█░█░█
```
**Pattern:** `checkerboard`

### Diagonal Stripes
```
▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚
▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞
▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚
```
**Pattern:** `diagonal`

### Dots
```
· · · · · · · · · ·
 · · · · · · · · ·
· · · · · · · · · ·
```
**Pattern:** `dots`

## Box Patterns

### Simple Border
```
┌────────────────────┐
│                    │
│                    │
│                    │
└────────────────────┘
```

### Double Border
```
╔════════════════════╗
║                    ║
║                    ║
║                    ║
╚════════════════════╝
```

### Rounded Border
```
╭────────────────────╮
│                    │
│                    │
│                    │
╰────────────────────╯
```

## Progress Bar Patterns

### Basic Progress
```
[████████████████████░░░░░░░░] 75%
```

### Gradient Progress
```
[████████▓▓▓▓▒▒▒▒░░░░        ] 60%
```

### Multi-Level Progress
```
CPU:  [████████████████████] 100%
RAM:  [████████████░░░░░░░░]  60%
DISK: [████▓▓▒▒░░░░░░░░░░░░]  25%
```

### Loading Animation Frames
```
Frame 1: [░░░░░░░░░░░░░░░░░░░░]  0%
Frame 2: [▒░░░░░░░░░░░░░░░░░░░] 10%
Frame 3: [▓▒░░░░░░░░░░░░░░░░░░] 20%
Frame 4: [█▓▒░░░░░░░░░░░░░░░░░] 30%
```

## Weather Patterns

### Clear Sky
```
☀        ☀        ☀


```

### Cloudy
```
  ☁   ☁     ☁   ☁
 ☁  ☁   ☁  ☁  ☁
   ☁   ☁  ☁    ☁
```

### Rainy
```
☁ ☁ ☁ ☁ ☁ ☁ ☁ ☁ ☁
🌧 🌧 🌧 🌧 🌧 🌧 🌧 🌧
│ │ │ │ │ │ │ │ │ │
```

### Snowy
```
❄  ❄  ❄  ❄  ❄  ❄
  ❄  ❄  ❄  ❄  ❄
❄  ❄  ❄  ❄  ❄  ❄
```

## Terrain Transitions

### Ocean to Land
```
████▓▓▓▓▒▒▒▒░░░░····≈≈≈≈♠♠♠♠
████▓▓▓▓▒▒▒▒░░░░····≈≈≈≈♠♠♠♠
```
**Sequence:** Deep ocean → Ocean → Shallow → Coast → Plains → Grassland → Forest

### Land to Mountains
```
····≈≈≈≈♠♠♠♠∩∩∩∩▲▲▲▲
····≈≈≈≈♠♠♠♠∩∩∩∩▲▲▲▲
```
**Sequence:** Plains → Grassland → Forest → Hills → Mountains

### Complete Terrain Cross-Section
```
████▓▓▓▓▒▒▒▒░░░░····≈≈≈≈♠♠♠♠∩∩∩∩▲▲▲▲∩∩∩∩∴∴∴∴
Deep |Ocean|Shal|Coas|Plai|Gras|Fore|Hill|Moun|Hill|Dese
```

## Map Legends

### Standard Map Legend
```
Ocean/Water:     Land Types:      Elevation:
█ Deep Ocean     · Plains         ∩ Hills
▓ Ocean          ≈ Grassland      ▲ Mountains
▒ Shallow        ♠ Forest
░ Coast          ♣ Jungle         Urban:
~ River          ∴ Desert         ▪ Urban
○ Lake           ❄ Ice/Snow       ■ City
                                  ● Metro
```

## Usage Examples

### Example 1: Small Island Map (20×10)
```
████████████████████
███▓▓▓▓▓▓▓▓▓▓▓▓▓▓███
██▓▒▒░░░····░░▒▒▓██
██▒░····♠♠♠····░▒██
██░···♠♠∩∩♠♠···░██
██░···♠♠∩∩♠♠···░██
██▒░····♠♠♠····░▒██
██▓▒▒░░░····░░▒▒▓██
███▓▓▓▓▓▓▓▓▓▓▓▓▓▓███
████████████████████
```

### Example 2: Continent Section (40×15)
```
████████████████████████████████████████
████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████████████
██████▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓████████████
████▓▓▒▒░░░░░░░░░░░░░░░▒▒▒▒▓▓▓▓▓▓████████
██▓▓▒▒░░····················░░▒▒▒▒▓▓▓▓████
██▒▒░░······≈≈≈≈≈≈≈≈≈≈······░░░▒▒▒▓▓▓▓██
▓▒░░····≈≈≈≈♠♠♠♠♠♠♠♠≈≈≈≈····░░░▒▒▒▓▓▓▓
▒░░····≈≈♠♠♠♠∩∩∩∩∩♠♠♠♠≈≈····░░▒▒▒▒▓▓▓
▒░····≈≈♠♠∩∩∩▲▲▲▲∩∩∩♠♠≈≈····░░▒▒▒▒▓▓▓
░····≈≈♠♠∩∩∩∩▲▲∩∩∩∩♠♠≈≈····░░░▒▒▒▒▓▓
░····≈≈♠♠♠∩∩∩∩∩∩∩∩♠♠♠≈≈····░░░▒▒▒▒▓▓
▒░····≈≈♠♠♠♠♠♠♠♠♠♠≈≈≈≈····░░░▒▒▒▒▓▓▓
▒▒░░····≈≈≈≈≈≈≈≈≈≈≈≈····░░░░▒▒▒▒▓▓▓▓▓
▓▒▒░░░░················░░░░▒▒▒▒▓▓▓▓▓███
▓▓▒▒▒░░░░░░░░░░░░░░░░░░░▒▒▒▒▓▓▓▓████████
```

### Example 3: Urban Area with Rivers (30×12)
```
····≈≈≈≈····≈≈≈≈····≈≈≈≈····
··▪··♠··▪··♠··▪··♠··▪··♠··▪
▪▪▪▪~~~~▪▪▪▪~~~~▪▪▪▪~~~~▪▪
■■■■~~~~■■■■~~~~■■■■~~~~■■
■●■■~~~~■●■■~~~~■●■■~~~~■●
■■■■~~~~■■■■~~~~■■■■~~~~■■
▪▪▪▪~~~~▪▪▪▪~~~~▪▪▪▪~~~~▪▪
··▪··♠··▪··♠··▪··♠··▪··♠··▪
····≈≈≈≈····≈≈≈≈····≈≈≈≈····
```
**Legend:** ● Metro, ■ City, ▪ Urban, ♠ Parks, ~ River, ≈ Grass

## Integration with uSCRIPT

### Generate Island Map
```
[PANEL|CREATE*island*20*10*7]
[PANEL|TERRAIN*island*0*0*20*10*ocean_deep]
[PANEL|TERRAIN*island*2*1*16*8*ocean]
[PANEL|TERRAIN*island*4*2*12*6*ocean_shallow]
[PANEL|TERRAIN*island*6*3*8*4*coast]
[PANEL|TERRAIN*island*8*4*4*2*plains]
[PANEL|SHOW*island]
[PANEL|EMBED*island*maps/island.md]
```

### Generate Progress Dashboard
```
[PANEL|CREATE*dashboard*50*10*7]
[PANEL|WRITE*dashboard*0*0*SYSTEM STATUS DASHBOARD]
[PANEL|WRITE*dashboard*0*2*CPU:  [████████████████████] 100%]
[PANEL|WRITE*dashboard*0*3*RAM:  [████████████░░░░░░░░]  60%]
[PANEL|WRITE*dashboard*0*4*DISK: [████▓▓▒▒░░░░░░░░░░░░]  25%]
[PANEL|SHOW*dashboard]
```

---

**See:** `data/system/graphics/teletext/README.md` for complete reference.
