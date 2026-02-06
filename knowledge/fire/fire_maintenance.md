---
uid: udos-guide-fire-20251204082500-UTC-L300AB51
title: Fire Maintenance
tags: [guide, knowledge, fire]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Fire Maintenance

**Category:** fire
**Difficulty:** beginner
**Generated:** 2025-11-27

## Overview

Maintaining a fire is as crucial as starting one in survival situations. A well-maintained fire provides consistent warmth, enables cooking, purifies water, signals for rescue, and offers psychological comfort. This guide covers essential techniques to keep your fire burning efficiently, conserve fuel, and ensure longevity for extended survival scenarios.

### Fire Maintenance Sequence

```sequence
Start->Base: Establish coal bed
Base->Feed: Add small fuel gradually
Feed->Arrange: Maintain airflow gaps
Arrange->Tend: Rake coals together
Tend->Monitor: Check fuel supply
Monitor->Gather: Collect more fuel
Gather->Add: Add medium fuel
Add->Build: Build up coal bed
Build->Bank: Prepare overnight banking
Bank->Cover: Cover with ash layer
Cover->Morning: Uncover and restart
```

### Fire Banking Decision Flow

```flow
st=>start: Evening fire
time=>condition: Hours until morning?
coals=>condition: Strong coal bed?
fuel=>condition: Large logs available?
weather=>condition: Dry conditions?
bank=>operation: Bank fire overnight
feed=>operation: Keep feeding fire
build=>operation: Build coal bed
gather=>operation: Gather large logs
cover=>operation: Cover with ash
morning=>end: Fire maintained

st->time
time(6-8 hours)->coals
time(< 6 hours)->feed->morning
coals(yes)->fuel
coals(no)->build->coals
fuel(yes)->weather
fuel(no)->gather->fuel
weather(yes)->bank->cover->morning
weather(no)->feed->morning
```

## Materials Needed

- **Graded fuel wood:**
  - Tinder: Fine, easily ignitable material (birch bark, dry grass, feather sticks)
  - Kindling: Small sticks, pencil-sized (twigs, split wood)
  - Fuel wood: Larger logs, wrist to forearm thickness
- Fire-tending tool (sturdy stick, branch, or shovel)
- Protective gloves (optional but recommended)
- Water or dirt for emergency extinguishing
- Dry storage area for backup fuel

## Step-by-Step Instructions

### 1. Establish Fuel Gradient

- Keep tinder, kindling, and fuel wood in separate piles
- Store all fuel upwind and away from fire (3+ feet)
- Protect reserve fuel from rain/snow
- Continuously gather more than you think you need

### 2. Feed the Fire Properly

**Small to Large Principle:**
1. Start with tinder base
2. Add kindling gradually as flames grow
3. Introduce small fuel wood once kindling burns hot
4. Add larger logs only when smaller wood is burning well

**Feeding Technique:**
- Add new wood to edges, not center
- Place logs parallel or crisscross for airflow
- Never smother fire with too much wood at once
- One piece at a time for control

### 3. Maintain Airflow

- Keep fire base elevated on rocks or green wood
- Ensure gaps between logs for oxygen circulation
- Use fire-tending stick to rearrange coals
- Break up ash buildup (restricts airflow)

### 4. Manage the Coal Bed

- Push partially burned wood into center
- Rake coals together for concentrated heat
- Add new fuel to hot coals, not flames
- Preserve coals for overnight banking

### 5. Overnight Fire Banking

**Method:**
1. Build up large coal bed (2-3 hours before sleep)
2. Add large hardwood logs in star/parallel pattern
3. Cover with layer of ash (insulates, slows burn)
4. Place large log on top (burns slowly all night)
5. In morning, brush away ash and add kindling

```[ASCII Diagram]
     Fire Maintenance Cycle
     
   Tinder → Kindling → Small → Large
     ░        ▒         ▓        █
     
   Coal Bed Management:
   ┌──────────────────┐
   │   New Fuel  →    │
   │   ██████ ▓▓▓▓    │
   │   ▒▒▒▒▒▒▒▒▒▒▒    │ Hot coals
   │   ░░░░░░░░░░░    │ Ash
   └──────────────────┘
   
   Star Fire (fuel conservation):
        ███
         ║
    ███══╬══███  Push ends in
         ║        as needed
        ███
```

## Safety Considerations

**Fire Safety:**
- Clear 10-foot radius of flammable materials
- Never leave fire unattended
- Keep water/dirt nearby for emergencies
- Wind changes can cause flare-ups

**Fuel Safety:**
- Avoid green wood (excess smoke, poor heat)
- Never use treated/painted wood (toxic fumes)
- Softwoods (pine, spruce) spark more than hardwoods
- Wet wood creates steam (can pop/explode)

**Nighttime Precautions:**
- Build fire away from shelter (sparks)
- Use reflector wall to direct heat
- Post watch if sleeping near fire
- Check overhead for dead branches (widowmakers)

**Environmental Ethics:**
- Use deadwood/downed timber only
- Minimize living tree damage
- Follow fire regulations/restrictions
- Fully extinguish before leaving

## Tips & Troubleshooting

**Common Mistakes:**
- Adding too much wood too fast (smothers fire)
- Not maintaining coal bed (harder to restart)
- Letting ash buildup choke airflow
- Using all dry wood at once (no reserve)

**Improving Efficiency:**
- Hardwoods (oak, maple) burn longer than softwoods
- Split wood burns faster than rounds
- Dry wood >20% more efficient than wet
- Smaller diameter = faster consumption

**Fuel Conservation:**
- Use star fire pattern (push ends in as needed)
- Bank fire when heat not actively needed
- Use reflector to maximize warmth
- Cook with coals, not flames

**Signs of Good Maintenance:**
- Steady, controllable flames
- Hot coal bed glowing orange/red
- Minimal smoke (complete combustion)
- Wood burning to ash, not charcoal

**Reviving Dying Fire:**
1. Clear ash from coal bed
2. Blow gently on coals (increase oxygen)
3. Add fine tinder to hot coals
4. Once flaming, add kindling gradually
5. Build back up to fuel wood

**Rainy Conditions:**
- Build fire under natural overhang/tarp
- Use standing dead wood (drier than ground fuel)
- Feather stick outer bark (dry inner wood)
- Keep backup tinder in waterproof container
- Split wet logs to access dry interior
