---
tier: 2
category: navigation
title: "Compass Use"
complexity: intermediate
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Compass Use

**Category:** navigation
**Difficulty:** beginner
**Generated:** 2025-11-27

## Overview

A compass is an essential navigation tool that provides reliable direction-finding capability without batteries or satellites. Mastering compass use is a fundamental survival skill that enables terrain navigation, route planning, and safe return to camp or civilization. This guide covers baseplate compass operation, taking bearings, and using a compass with maps.

### Taking and Following a Bearing Sequence

```sequence
Navigator->Target: Identify destination landmark
Target->Compass: Point travel arrow at target
Compass->Bezel: Rotate bezel to align needle
Bezel->Navigator: Read bearing number
Navigator->Compass: Hold level at waist
Compass->Body: Turn body to align needle
Body->Direction: Travel arrow shows route
Direction->Landmark: Pick closer landmark on line
Landmark->Walk: Walk to landmark
Walk->Check: Check compass again
Check->Repeat: Pick new landmark
Repeat->Destination: Reach target
```

### Navigation Decision Flow

```flow
st=>start: Need to navigate
map=>condition: Have map?
known=>condition: Know destination bearing?
plot=>operation: Plot course on map
take=>operation: Take field bearing
follow=>operation: Follow bearing
landmark=>operation: Pick intermediate landmarks
check=>condition: Reached destination?
return=>condition: Need to return?
back=>operation: Add/subtract 180 degrees
arrived=>end: Destination reached

st->map
map(yes)->plot->follow
map(no)->known
known(yes)->follow
known(no)->take->follow
follow->landmark->check
check(no)->landmark
check(yes)->return
return(yes)->back->follow
return(no)->arrived
```

## Materials Needed

- **Baseplate compass** with:
  - Rotating bezel (azimuth ring)
  - Orienting arrow/meridian lines
  - Direction of travel arrow
  - Transparent baseplate
- Topographic map (for advanced techniques)
- Pencil (for marking)
- Ruler (often built into compass)

## Step-by-Step Instructions

### 1. Understand Compass Parts

**Key Components:**
- **Magnetic Needle:** Red end points North
- **Rotating Bezel:** Dial marked 0-360 degrees
- **Orienting Arrow:** Fixed arrow in bezel housing
- **Direction of Travel Arrow:** Points where you're heading
- **Baseplate:** Clear plastic with ruler/scales

### 2. Take a Field Bearing (Point-to-Point)

1. **Hold compass level** at waist height
2. **Point direction of travel arrow** at target/landmark
3. **Rotate bezel** until orienting arrow aligns with red needle
4. **Read bearing** where bezel meets baseplate (0-360°)
5. **Follow bearing:** Keep needle and orienting arrow aligned while walking

### 3. Follow a Bearing

1. Set desired bearing on bezel (align with baseplate index)
2. Hold compass level in front
3. Turn your body until red needle aligns with orienting arrow
4. Direction of travel arrow now points your route
5. Pick distant landmark on that line and walk to it
6. Repeat: check compass, pick new landmark, walk

### 4. Return Bearing (Back-Azimuth)

To return to start point:
1. Add 180° to original bearing (or subtract 180° if over 180)
2. Set new bearing on compass
3. Follow same procedure as above
4. Example: Original bearing 45° → Return bearing 225°

### 5. Using with a Map

**Orient Map to North:**
1. Place compass on map
2. Align orienting lines with map's north-south grid
3. Rotate map and compass together until needle points north
4. Map now matches terrain

**Plot a Course:**
1. Draw line on map from current position to destination
2. Place compass edge along line
3. Rotate bezel until orienting lines align with map north
4. Read bearing at index mark
5. Remove compass from map and follow bearing in field

```[ASCII Diagram]
  Baseplate Compass
  
  ┌─────────────────────┐
  │   ╱╲ Travel Arrow   │
  │   ││               │
  │   ││    N          │
  │  ┌┴┴┐  ╱│╲         │
  │  │▓▓│ W─┼─E        │ Rotating
  │  │▓▓│  ╲│╱         │ Bezel
  │  └──┘    S          │
  │   ↑│               │
  │   ││  Magnetic     │
  │   ││  Needle       │
  │  Orienting Arrow   │
  │                     │
  └─────────────────────┘
     Baseplate
     
  Needle in Arrow = On Course
  
     ↑ Red    ↑ Orient
     │        │
    ═══      ═══  ✓ Aligned
```

## Safety Considerations

**Magnetic Declination:**
- Compass points to magnetic north (not true north)
- Declination varies by location (can be 20°+ difference)
- Check maps for local declination value
- Adjust bearing accordingly (add for East, subtract for West)

**Metal Interference:**
- Keep compass away from metal objects (knife, belt buckle)
- Electronics can deflect needle
- Power lines affect readings
- Use compass 6+ feet from large metal objects

**Common Errors:**
- Holding compass unlevel (needle drags)
- Following wrong end of needle (180° error)
- Not accounting for declination
- Misreading degree markings

**Environmental Limitations:**
- Near magnetic poles, compass unreliable
- Extreme cold can slow needle movement
- Lightning risk - avoid during storms
- Some rock formations have magnetic properties

## Tips & Troubleshooting

**Common Mistakes:**
- Walking with compass at eye level (causes needle drag)
- Not picking intermediate landmarks (drift off course)
- Trusting one bearing check (verify frequently)
- Ignoring declination (can be miles off target)

**Improving Accuracy:**
- Take multiple bearings to confirm
- Use distant landmarks when possible
- Re-check bearing every 5-10 minutes
- Account for terrain obstacles (detour around, regain bearing)

**Quick Direction Finding:**
- Hold compass flat
- Let needle settle
- Red = North
- No need for bearings if just finding cardinal directions

**Survival Situations:**
- Compass more reliable than phone GPS (no batteries needed)
- Works in any weather/lighting
- Practice in familiar areas before emergency
- Teach technique to group members (redundancy)

**Leapfrogging Technique:**
1. Take bearing
2. Identify landmark on bearing (tree, rock)
3. Walk to landmark
4. Take bearing again from new position
5. Repeat - accounts for terrain obstacles

**Night Navigation:**
- Use luminous compass (glow-in-the-dark bezel)
- Brief light exposure charges glow
- Take bearing in daylight, follow at night
- Use stars to verify direction

**Landmark Selection:**
- Choose distinctive features (lone tree, rock outcrop)
- Distant objects minimize bearing error
- Multiple small landmarks better than one far landmark
- Mark passage points to verify progress
