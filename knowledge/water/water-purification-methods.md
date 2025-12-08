---
tier: 3
category: water
title: "Water Purification Methods"
complexity: advanced
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Water Purification Methods

**Category:** Water Safety  
**Priority:** Critical ████████████  
**Time Required:** 5-60 minutes  
**Difficulty:** Beginner to Intermediate

---

## Overview

Safe drinking water is essential for survival. This guide covers field-tested purification methods ranked by effectiveness.

**Pathogen Removal Effectiveness:**
```
╔════════════════╦═════════╦═════════╦═════════╦═════════╗
║ Method         ║ Bacteria║ Viruses ║ Protozoa║ Chemical║
╠════════════════╬═════════╬═════════╬═════════╬═════════╣
║ Boiling        ║ ████████║ ████████║ ████████║ ░░░░░░░░║
║ Filtration     ║ ████████║ ░░░░░░░░║ ████████║ ██░░░░░░║
║ UV Light       ║ ████████║ ████████║ ████████║ ░░░░░░░░║
║ Iodine/Chlorine║ ████████║ ██████░░║ ████░░░░║ ░░░░░░░░║
║ Distillation   ║ ████████║ ████████║ ████████║ ████████║
╚════════════════╩═════════╩═════════╩═════════╩═════════╝

████████ = 100%, ██████ = 75%, ████ = 50%, ██ = 25%, ░░░░ = 0%
```

---

## 1. Boiling (Most Reliable)

### Method

```
┌─────────────────────────────────────┐
│  BOILING WATER PURIFICATION         │
├─────────────────────────────────────┤
│                                     │
│  Step 1: Filter debris              │
│  ┌───────┐                          │
│  │ Cloth │ ──→ Remove particles     │
│  └───────┘                          │
│      │                              │
│      ▼                              │
│  Step 2: Heat to rolling boil       │
│  ┌───────────────┐                  │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓ │ 100°C            │
│  │ ▒▒▒▒▒▒▒▒▒▒▒▒▒ │                  │
│  │ ░░░░░░░░░░░░░ │ Fire/Stove       │
│  └───────────────┘                  │
│      │                              │
│      ▼                              │
│  Step 3: Boil duration              │
│  Sea level:     1 minute            │
│  1000m+:        3 minutes           │
│  2000m+:        5 minutes           │
│      │                              │
│      ▼                              │
│  Step 4: Cool and store             │
│  ┌───────────────┐                  │
│  │ ▒▒▒▒▒▒▒▒▒▒▒▒▒ │ Safe water       │
│  └───────────────┘                  │
│                                     │
└─────────────────────────────────────┘
```

### Temperature vs. Time Chart

```
Elevation      Temperature    Time Required
═════════════════════════════════════════════
Sea Level      100°C          ▓ 1 min
1000m          96°C           ▓▓▓ 3 min
2000m          93°C           ▓▓▓▓▓ 5 min
3000m          90°C           ▓▓▓▓▓▓▓ 7 min
4000m+         87°C           ▓▓▓▓▓▓▓▓▓ 10 min
```

### Pros & Cons

✅ **Advantages:**
- Kills all pathogens (100% effective)
- No chemicals needed
- Works on any water source
- No special equipment required

❌ **Disadvantages:**
- Requires fuel/fire
- Time consuming (10-15 min total)
- Doesn't remove chemicals
- Hot water needs cooling

---

## 2. Filtration Systems

### Filter Types Comparison

```
╔════════════════╦═══════════╦═══════════╦═══════════╗
║ Filter Type    ║ Pore Size ║ Flow Rate ║ Lifespan  ║
╠════════════════╬═══════════╬═══════════╬═══════════╣
║ Ceramic        ║ 0.2-0.5µm ║ ██░░░░░░  ║ ████████  ║
║ Hollow Fiber   ║ 0.1µm     ║ ████████  ║ ████░░░░  ║
║ Activated Carbon║ 1-5µm    ║ ██████░░  ║ ████░░░░  ║
║ Reverse Osmosis║ 0.0001µm  ║ ░░░░░░░░  ║ ██████░░  ║
╚════════════════╩═══════════╩═══════════╩═══════════╝

Flow: ████████=Fast, ████=Medium, ██=Slow
Lifespan: ████████=Long (5000L+), ████=Medium (1000L)
```

### How Filters Work

```
┌─────────────────────────────────────────────┐
│         MULTI-STAGE FILTRATION              │
├─────────────────────────────────────────────┤
│                                             │
│  Raw Water Input ───→                       │
│                                             │
│  Stage 1: Pre-filter (removes sediment)     │
│  ┌───────────────────────────────────┐      │
│  │ █████████████████████████████████ │      │
│  │ Large particles trapped ▓▓▓▓▓▓▓▓▓ │      │
│  └───────────────┬───────────────────┘      │
│                  │                          │
│                  ▼                          │
│  Stage 2: Activated carbon (chemicals)      │
│  ┌───────────────────────────────────┐      │
│  │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │      │
│  │ Chemicals absorbed ░░░░░░░░░░░░░░ │      │
│  └───────────────┬───────────────────┘      │
│                  │                          │
│                  ▼                          │
│  Stage 3: Hollow fiber (0.1µm)              │
│  ┌───────────────────────────────────┐      │
│  │ ║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║ │      │
│  │ Bacteria/protozoa blocked         │      │
│  └───────────────┬───────────────────┘      │
│                  │                          │
│                  ▼                          │
│  Clean Water Output                         │
│  ┌───────────────────────────────────┐      │
│  │                                   │      │
│  │   Safe for drinking               │      │
│  └───────────────────────────────────┘      │
│                                             │
└─────────────────────────────────────────────┘
```

### Field-Improvised Filter

```
Materials: Bottle, cloth, sand, charcoal, gravel

┌─────────────────┐
│   Cut bottle    │  ← Water pours in
│   (bottom off)  │
├─────────────────┤
│ ░░░ Cloth ░░░░  │  ← Pre-filter
├─────────────────┤
│ ····Gravel····  │  ← Large particles
├─────────────────┤
│ ≈≈≈≈Sand≈≈≈≈≈≈  │  ← Fine particles
├─────────────────┤
│ ▓▓Charcoal▓▓▓▓  │  ← Chemicals/taste
├─────────────────┤
│ ····Gravel····  │  ← Support layer
├─────────────────┤
│ ░░░ Cloth ░░░░  │  ← Final filter
└────────┬────────┘
         │
         ▼
  Clean(er) water

⚠️ Still boil after filtering!
```

---

## 3. Chemical Treatment

### Iodine Tablets

```
╔════════════════════════════════════════════╗
║        IODINE TREATMENT GUIDE              ║
╠════════════════════════════════════════════╣
║                                            ║
║  Dosage: 2 tablets per liter               ║
║                                            ║
║  Wait Times (at 20°C):                     ║
║  ┌────────────────────────────────┐        ║
║  │ Clear water:    ▓▓▓▓ 30 min    │        ║
║  │ Cloudy water:   ▓▓▓▓▓▓▓▓ 60 min│        ║
║  │ Cold water (5°C):████████ 120min│       ║
║  └────────────────────────────────┘        ║
║                                            ║
║  Effectiveness:                            ║
║  Bacteria:  ████████ 99.9%                 ║
║  Viruses:   ██████░░ 75%                   ║
║  Giardia:   ████░░░░ 50% (needs longer)    ║
║                                            ║
╚════════════════════════════════════════════╝
```

### Chlorine (Bleach) Treatment

**Dosage Chart:**
```
Water Clarity    Bleach (5.25%)    Wait Time
═══════════════════════════════════════════════
Clear            2 drops/liter     ▓▓ 30 min
Cloudy           4 drops/liter     ▓▓▓▓ 60 min
Very Cloudy      Filter first!     ████ 120 min

1 drop ≈ 0.05ml
Use unscented bleach only!
```

### Chemical Treatment Timeline

```
Time: 0    15   30   45   60   75   90  105  120 min
      │    │    │    │    │    │    │    │    │
Clear │░░░░▓▓▓▓█████████████████████████████████
      │    │    │
      │    │    └─ Safe to drink
      │    └────── 50% pathogen kill
      └─────────── Chemical added

Cloudy│░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓████████████
      │                        │    │
      │                        │    └─ Safe
      │                        └────── 50% kill
      └─────────────────────────────── Added

░░░░ = Unsafe, ▓▓▓▓ = Reducing, ████ = Safe
```

---

## 4. UV Light Purification

### UV Pen Device

```
┌─────────────────────────────────────┐
│     UV STERILIZATION PROCESS        │
├─────────────────────────────────────┤
│                                     │
│  Device: ═══╦═══ ← UV bulb          │
│             ║                       │
│             ▼                       │
│  Water: ┌──────────┐                │
│         │▒▒▒▒▒▒▒▒▒▒│ ← Stir 90 sec  │
│         │░░UV░RAYS░│                │
│         │▒▒▒▒▒▒▒▒▒▒│                │
│         └──────────┘                │
│             │                       │
│             ▼                       │
│  Result: DNA destroyed in pathogens │
│                                     │
│  Effectiveness Timeline:            │
│  0 sec   ░░░░░░░░ 0%                │
│  30 sec  ▓▓▓▓░░░░ 50%               │
│  60 sec  ▓▓▓▓▓▓░░ 75%               │
│  90 sec  ████████ 99.9%             │
│                                     │
└─────────────────────────────────────┘
```

### Pros & Cons

✅ **Advantages:**
- Fast (90 seconds)
- No chemicals/taste
- Lightweight
- Effective against all pathogens

❌ **Disadvantages:**
- Requires batteries/power
- Doesn't work in cloudy water
- Expensive ($50-100)
- Can fail without warning

---

## 5. Solar Disinfection (SODIS)

### Method

```
┌───────────────────────────────────────────┐
│      SOLAR WATER DISINFECTION             │
├───────────────────────────────────────────┤
│                                           │
│  1. Fill clear plastic bottle             │
│     ┌─────────────────┐                   │
│     │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │                   │
│     │ ░Water░░░░░░░░░ │                   │
│     └─────────────────┘                   │
│                                           │
│  2. Place in direct sunlight (6 hours)    │
│                                           │
│           ☀️ SUN                          │
│            │││                            │
│            │││                            │
│            ▼▼▼                            │
│     ┌─────────────────┐                   │
│     │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ UV rays penetrate │
│     │ ▒Heating▒▒▒▒▒▒▒ │                   │
│     └─────────────────┘                   │
│            │                              │
│            ▼                              │
│  3. Pathogens destroyed by UV + heat      │
│                                           │
│  Time vs. Weather:                        │
│  Sunny (>50°C):    ▓▓▓▓▓▓ 6 hours         │
│  Partial cloud:    ▓▓▓▓▓▓▓▓▓▓ 2 days      │
│  Overcast:         Not recommended        │
│                                           │
└───────────────────────────────────────────┘
```

### Effectiveness Over Time

```
Hours:  0    2    4    6    8    10   12
        │    │    │    │    │    │    │
Clear:  ░░░░▒▒▒▒▓▓▓▓████████████████████
        │    │    │    │
        │    │    │    └─ 99.9% kill (6hr)
        │    │    └────── 90% kill
        │    └─────────── 50% kill
        └──────────────── Unsafe

Cloudy: ░░░░░░░░░░░░▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓████
        │              │              │
        │              │              └─ Safe (12hr)
        │              └──────────────── 50% kill
        └─────────────────────────────── Unsafe
```

---

## 6. Distillation

### Solar Still Diagram

```
┌─────────────────────────────────────────────┐
│         SOLAR STILL OPERATION               │
├─────────────────────────────────────────────┤
│                                             │
│              ☀️ Heat from sun               │
│                  │││                        │
│                  ▼▼▼                        │
│  ┌───────────────────────────────────┐      │
│  │     ╱╲  Clear plastic  ╱╲         │      │
│  │    ╱  ╲               ╱  ╲        │      │
│  │   ╱    ╲             ╱    ╲       │      │
│  │  ╱      ╲ Condensation     ╲      │      │
│  │ ╱   💧💧💧💧💧💧💧💧💧      ╲     │      │
│  │╱          │  │  │  │          ╲    │      │
│  │     ┌─────▼──▼──▼──▼─────┐    │   │      │
│  │     │  Collection cup     │    │   │      │
│  │     └─────────────────────┘    │   │      │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │   │      │
│  │  ▒▒▒ Dirty water/vegetation ▒  │   │      │
│  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │   │      │
│  └───────────────────────────────────┘      │
│                                             │
│  Process:                                   │
│  1. Sun heats water → evaporation           │
│  2. Water vapor rises → condenses on plastic│
│  3. Droplets run down → collect in cup      │
│  4. Pure water (no salts/chemicals)         │
│                                             │
│  Yield: ~500ml per day                      │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Emergency Purification Decision Tree

```
                      START
                        │
                        ▼
                 Have fuel/fire?
                   ╱        ╲
                 YES         NO
                 ╱            ╲
                ▼              ▼
         ┌──────────┐    Have filter?
         │  BOIL    │      ╱      ╲
         │  WATER   │    YES       NO
         └──────────┘    ╱          ╲
              │         ▼            ▼
              │   ┌──────────┐  Have chemicals?
              │   │ FILTER + │    ╱        ╲
              │   │   BOIL   │  YES         NO
              │   └──────────┘  ╱            ╲
              │        │       ▼              ▼
              │        │  ┌──────────┐  ┌──────────┐
              │        │  │CHEMICAL  │  │  SODIS   │
              │        │  │TREATMENT │  │(6+ hours)│
              │        │  └──────────┘  └──────────┘
              │        │       │             │
              └────────┴───────┴─────────────┘
                       │
                       ▼
                  SAFE WATER
```

---

## Method Comparison Matrix

```
╔════════════╦═══════╦═══════╦═══════╦════════╦═══════╗
║ Method     ║ Speed ║ Cost  ║ Weight║ Ease   ║ Rating║
╠════════════╬═══════╬═══════╬═══════╬════════╬═══════╣
║ Boiling    ║ ███   ║ █████ ║ ████  ║ ██████ ║ ████  ║
║ Filter     ║ ██████║ ███   ║ ███   ║ ██████ ║ █████ ║
║ UV Light   ║ ██████║ ██    ║ ██████║ ██████ ║ ████  ║
║ Iodine     ║ ███   ║ █████ ║ ██████║ ██████ ║ ████  ║
║ Chlorine   ║ ███   ║ █████ ║ ██████║ █████  ║ ████  ║
║ SODIS      ║ █     ║ █████ ║ ██████║ ██████ ║ ███   ║
║ Distill    ║ █     ║ █████ ║ ███   ║ ███    ║ ███   ║
╚════════════╩═══════╩═══════╩═══════╩════════╩═══════╝

██████ = Excellent, ████ = Good, ███ = Fair, ██ = Poor, █ = Bad
```

---

## Testing Water Safety

### Visual Inspection

```
┌─────────────────────────────────────┐
│      WATER QUALITY INDICATORS       │
├─────────────────────────────────────┤
│                                     │
│  SAFE:                              │
│  ┌─────────┐                        │
│  │         │ Clear                  │
│  │ ░░░░░░░ │ No odor                │
│  │         │ No visible particles   │
│  └─────────┘                        │
│       ✓ Probably safe (still treat!)│
│                                     │
│  CAUTION:                           │
│  ┌─────────┐                        │
│  │ ▒▒▒▒▒▒▒ │ Slightly cloudy        │
│  │ ░░▒▒░░░ │ Mild odor              │
│  │ ▒░░░▒▒░ │ Some particles         │
│  └─────────┘                        │
│       ⚠ Pre-filter required         │
│                                     │
│  DANGER:                            │
│  ┌─────────┐                        │
│  │ ▓▓█▓▓▓█ │ Very cloudy/brown      │
│  │ █▓░▓█▓░ │ Strong odor            │
│  │ ▓█▓░▓▓█ │ Visible contamination  │
│  └─────────┘                        │
│       ⛔ Avoid if possible          │
│                                     │
└─────────────────────────────────────┘
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════╗
║           WATER PURIFICATION QUICK REF            ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║ 🔥 BOILING: 1 min rolling boil (+1 min/1000m)    ║
║              100% effective                       ║
║                                                   ║
║ 🔬 FILTER:  Pump/squeeze through 0.1µm filter    ║
║              Good for bacteria/protozoa           ║
║                                                   ║
║ 💊 IODINE:  2 tablets/L, wait 30-60 min          ║
║              Good for bacteria, fair for viruses  ║
║                                                   ║
║ 💧 BLEACH:  2 drops/L clear, 4 drops/L cloudy    ║
║              Wait 30-60 min, 5.25% unscented      ║
║                                                   ║
║ ☀️ UV PEN:  Stir 90 seconds in clear water       ║
║              99.9% all pathogens                  ║
║                                                   ║
║ 🌞 SODIS:   Clear bottle, 6 hours direct sun     ║
║              Free but slow                        ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

---

## Related Resources

- **Finding Water:** `knowledge/survival/water/water-sources.md`
- **Storage:** `knowledge/survival/water/water-storage.md`
- **Hydration:** `knowledge/survival/water/hydration-needs.md`
- **Field Skills:** `knowledge/survival/skills/wilderness-survival.md`

---

**Priority:** ████████████ **CRITICAL SKILL**

Learn and practice multiple methods!
