---
uid: udos-guide-medical-20251204171600-UTC-L300AB54
title: Hypothermia Treatment & Prevention
tags: [guide, knowledge, medical]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Hypothermia Treatment & Prevention

**Category:** Medical - Critical Emergency
**Priority:** HIGH - Can occur even in Australia (mountains, Tasmania, cold nights)
**Season:** Higher risk May-September, year-round in alpine areas
**Difficulty:** Moderate - prevention easier than treatment

---

## Overview

Hypothermia occurs when the body loses heat faster than it can produce it, causing core body temperature to drop below 35°C.

**Normal body temperature:** 36.5-37.5°C
**Hypothermia:** < 35°C
**Severe hypothermia:** < 28°C

```
Temperature ranges:
37°C  ████████████████  Normal
36°C  ████████████████
35°C  ════════════════  ← HYPOTHERMIA begins
34°C  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  Mild
33°C  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
32°C  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
30°C  ░░░░░░░░░░░░░░░░  ← Moderate
28°C  ░░░░░░░░░░░░░░░░
26°C  ░░░░░░░░░░░░░░░░  ← Severe (life-threatening)
24°C  ░░░░░░░░░░░░░░░░
```

**Key fact:** Can happen in temperatures as high as 10-15°C if conditions are right (wet, wind, exhaustion).

---

## Yes, Even in Australia

**Common misconception:** "Australia is warm, hypothermia won't happen here"

**Reality - High risk areas:**

```
Alpine regions:
├─ Snowy Mountains (NSW/VIC)
├─ Victorian Alps
├─ Tasmania (mountains and lowlands)
├─ Australian Alps
└─ Can snow May-October, sometimes beyond

Cool temperate:
├─ Tasmania (year-round risk)
├─ Southern Victoria
├─ Adelaide Hills
├─ Southern NSW highlands
└─ Nights can drop to 0-5°C

Water-related:
├─ Southern Ocean (cold year-round)
├─ Bass Strait
├─ Cool ocean currents
└─ Water conducts heat 25× faster than air
```

**Australian hypothermia deaths occur regularly:**
- Bushwalkers in alpine areas
- Overnight camping in cold conditions
- Ocean/river immersion
- Elderly at home (inadequate heating)
- Homeless population

**Don't underestimate** - particularly wet + wind + exhaustion combination.

### Hypothermia Treatment Sequence

```sequence
Rescuer->Victim: Identify hypothermia signs
Victim->Rescuer: Assess severity stage
Rescuer->Shelter: Move to warm, dry location
Shelter->Wet: Remove wet clothing
Wet->Dry: Replace with dry clothes
Dry->Insulate: Wrap in blankets/sleeping bag
Insulate->Warm: Apply heat packs to core
Warm->Liquids: Give warm sweet drinks
Liquids->Monitor: Check temp and vitals
Monitor->Rescuer: Continue rewarming
Rescuer->Decision: Severe hypothermia?
Decision->Hospital: Call 911 for severe cases
Hospital->Emergency: Immediate transport
```

### Hypothermia Assessment & Response Flow

```flow
st=>start: Person exposed to cold
signs=>condition: Showing hypothermia signs?
stage=>condition: Severity stage?
mild=>operation: Active rewarming
mod=>operation: Passive rewarming only
severe=>operation: Call 911 immediately
shelter=>operation: Move to shelter
wet=>operation: Remove wet clothes
dry=>operation: Add dry insulation
heat=>operation: External heat sources
drink=>operation: Warm sweet drinks
monitor=>operation: Monitor vitals
recov=>end: Gradual recovery
hosp=>end: Hospital treatment

st->signs
signs(yes)->stage
signs(no)->recov
stage(mild)->shelter->wet->dry->mild->heat->drink->monitor->recov
stage(moderate)->shelter->wet->dry->mod->monitor->recov
stage(severe)->severe->hosp
```

---

## Stages & Symptoms

### Mild Hypothermia (35-32°C)

**Body trying to warm itself:**

```
Physical signs:
├─ Shivering (vigorous, uncontrollable)
├─ Cold, pale skin
├─ Numbness in extremities
├─ Clumsy, stumbling
├─ Slurred speech
├─ Rapid breathing
└─ Rapid pulse

Mental/behavioral:
├─ Confusion
├─ Poor judgment
├─ Difficulty concentrating
├─ Apathy ("I don't care")
├─ Irritability
├─ May deny problem
└─ Memory problems
```

**Critical sign:** "Umbles" - Stumbles, Mumbles, Fumbles, Grumbles

**Still reversible** with proper treatment. Person can often walk/function somewhat.

### Moderate Hypothermia (32-28°C)

**Body losing ability to rewarm itself:**

```
Physical signs:
├─ Shivering stops (DANGER - not getting warmer!)
├─ Skin very cold, may be blue/gray
├─ Slow, shallow breathing
├─ Slow, weak pulse
├─ Muscle stiffness
├─ Dilated pupils
├─ Loss of coordination
└─ Cannot walk properly

Mental/behavioral:
├─ Severe confusion
├─ Irrational behavior
├─ Paradoxical undressing (feels hot, removes clothes)
├─ Drowsiness
├─ Slurred or no speech
└─ May become combative
```

**MEDICAL EMERGENCY** - Call 000

**Handle very carefully** - rough movement can cause cardiac arrest.

### Severe Hypothermia (< 28°C)

**Life-threatening:**

```
Physical signs:
├─ No shivering
├─ Rigid muscles
├─ Very slow breathing (may be hard to detect)
├─ Very slow, weak, irregular pulse (may be hard to find)
├─ Unconscious or barely conscious
├─ Skin ice cold
└─ May appear dead

Critical:
├─ Cardiac arrest risk (any sudden movement)
├─ Breathing may stop
├─ Pulse may be undetectable
└─ Pupils fixed and dilated
```

⚠️ **"Not dead until warm and dead"**
- Don't assume death
- People have survived severe hypothermia
- Continue treatment and evacuation
- Hospital can rewarm core safely

---

## Immediate Treatment

### General Principles

```
Order of priorities:
1. Prevent further heat loss
2. Handle extremely gently (if moderate/severe)
3. Rewarm gradually
4. Get medical help
5. Monitor continuously
```

### Mild Hypothermia Treatment

**If person is shivering, alert, walking:**

```
1. Get out of cold/wet environment
   ├─ Into shelter (tent, hut, building, vehicle)
   ├─ Out of wind
   └─ Dry location

2. Remove wet clothing
   ├─ Replace with dry clothing
   ├─ If no dry clothes, wring out wet ones
   └─ Cover with space blanket, sleeping bag, dry blankets

3. Insulate from ground
   ├─ Sleeping pad, mattress
   ├─ Blankets, clothing, packs
   └─ Ground conducts heat away

4. Add layers
   ├─ Dry hat (lose lots of heat through head)
   ├─ Dry gloves/socks
   ├─ Insulated jacket
   └─ Wrap in sleeping bag/blankets

5. Warm drinks
   ├─ Warm (not hot) water, tea, soup
   ├─ Add sugar (quick energy for heat production)
   ├─ Sip slowly
   └─ Only if fully conscious and can swallow

6. High-energy food
   ├─ If can eat normally
   ├─ Chocolate, nuts, energy bars
   ├─ Carbs + fat = energy for heat
   └─ Don't force if nauseous

7. Gentle exercise
   ├─ If can do it (walk around, arm circles)
   ├─ Generates internal heat
   ├─ Stop if too exhausted
   └─ NOT for moderate/severe hypothermia

8. External heat sources (if available)
   ├─ Warm water bottles wrapped in cloth
   ├─ Heat packs (wrapped, not directly on skin)
   ├─ Place on torso, groin, armpits (not extremities)
   └─ Check skin frequently (can burn)

9. Monitor
   ├─ Should improve within 30-60 minutes
   ├─ If not improving → seek medical help
   └─ If worsening → call 000
```

### Moderate to Severe Hypothermia

⚠️ **CALL 000 IMMEDIATELY**

**Critical rules:**

```
DO:
├─ Handle extremely gently
│   └─ Rough movement can trigger cardiac arrest
├─ Keep horizontal (lying flat)
│   └─ Sitting/standing can cause blood pressure drop → death
├─ Prevent further heat loss
│   └─ Insulate, cover, shelter
├─ Monitor breathing constantly
│   └─ Ready to start CPR
├─ Passive rewarming only
│   └─ Let body rewarm itself slowly
└─ Wait for advanced medical care

DON'T:
├─ ✗ Rub or massage
├─ ✗ Move roughly
├─ ✗ Give alcohol
├─ ✗ Give hot drinks (unless very mild hypothermia)
├─ ✗ Apply direct heat (hot water bottles, heat packs)
├─ ✗ Rewarm extremities first
│   └─ Sends cold blood to core → "afterdrop" → cardiac arrest
├─ ✗ Let them walk or exert
└─ ✗ Assume they're dead (continue CPR until hospital)
```

**Rewarming shock (afterdrop):**
- Cold blood from extremities returns to heart
- Core temperature drops further
- Can cause cardiac arrest
- Why gentle, passive rewarming is critical

**Insulation only:**
```
Layer system:
Ground → Insulation (pads, blankets) →
Person → Space blanket (vapor barrier) →
Sleeping bag → More blankets
```

**Paradoxical undressing:**
- Person feels hot, tries to remove clothes
- Sign of severe hypothermia
- Gently prevent if possible
- Don't argue or restrain forcefully (can trigger cardiac arrest)
- Redirect, distract, layer over them

### CPR for Hypothermia

**If unconscious and not breathing normally:**

```
1. Check breathing for up to 1 minute
   ├─ Breathing slows dramatically in hypothermia
   ├─ Take time to assess
   └─ Feel for breath on cheek, watch chest

2. Check pulse for up to 1 minute
   ├─ Pulse very slow and weak
   ├─ Check carotid (neck) and femoral (groin)
   └─ Be patient

3. If no breathing/pulse → start CPR
   ├─ Same as normal CPR (30 compressions : 2 breaths)
   ├─ Continue until:
   │   ├─ Person revives
   │   ├─ Medical help arrives
   │   └─ Physically cannot continue
   └─ Don't give up early - people have survived

4. One shock only if AED available
   ├─ If no response, continue CPR
   └─ Further shocks unlikely to work until rewarmed
```

**"Not dead until warm and dead"** - Continue resuscitation even if seems futile.

---

## Specific Situations

### Immersion Hypothermia (Cold Water)

**Extreme danger:**
- Water conducts heat 25× faster than air
- Can lose consciousness in 15-30 minutes (cold water)
- Death can occur in 30-60 minutes

**Temperature timeline:**

```
Water temp    Exhaustion/        Expected survival
              unconsciousness    time

< 4°C         15-30 min          30-90 min
4-10°C        30-60 min          1-3 hours
10-15°C       1-2 hours          1-6 hours
15-20°C       2-7 hours          2-40 hours
> 20°C        3-12 hours         3+ hours
```

**If you fall in cold water:**

```
1. Control breathing
   ├─ Cold shock causes gasping (can inhale water)
   ├─ Focus on breathing slowly
   └─ 30-60 seconds for shock to pass

2. Keep clothes on
   ├─ Trap layer of water (warms to body temp)
   ├─ Provides flotation
   └─ Only remove heavy boots if sinking

3. Don't try to swim unless shore very close
   ├─ Swimming increases heat loss
   ├─ Exhausts you faster
   └─ Float/tread water minimally

4. HELP position (if alone)
   ├─ Heat Escape Lessening Posture
   ├─ Knees to chest
   ├─ Arms crossed holding life jacket
   └─ Protects core

5. Huddle position (if group)
   ├─ Group together
   ├─ Sides/chests touching
   └─ Share body heat

6. Get out ASAP
   ├─ Climb onto capsized boat
   ├─ Grab any floating object
   └─ Get help immediately
```

**After rescue from cold water:**

```
1. Handle gently (cardiac arrest risk)
2. Lay horizontal
3. Remove wet clothes carefully
4. Dry off (pat, don't rub)
5. Insulate thoroughly
6. Call 000 (even if seems OK)
7. Monitor continuously
   └─ "Circum-rescue collapse" can occur during/after rescue
```

### Bushwalking/Hiking

**Common scenario:**
- Started warm, got cold
- Got wet (rain, creek crossing, sweat)
- Became exhausted
- Temperature dropped
- Wind increased

**Prevention critical:**

```
Clothing layers:
├─ Base layer (wool or synthetic, NOT cotton)
├─ Insulation layer (fleece, down)
├─ Shell layer (waterproof, windproof)
├─ Hat (always carry)
└─ Gloves (always carry)

Plus:
├─ Extra warm layer (emergency)
├─ Space blanket
├─ Waterproof rain gear
└─ Change of socks
```

**If hypothermia developing on trail:**

```
1. Stop immediately
   └─ Don't push on ("summit fever" = danger)

2. Set up emergency shelter
   ├─ Tent
   ├─ Tarp/fly
   ├─ Emergency bivvy bag
   └─ Even just space blanket in dense trees

3. Change into dry clothes

4. Insulate from ground

5. Get into sleeping bag

6. High-energy food & warm drinks

7. Decide: wait out or call for help
   ├─ If improving: can wait, then reassess
   ├─ If not improving: activate PLB/call rescue
   └─ If worsening: call 000/rescue immediately
```

**Don't:**
- Try to "walk it off" (exhaustion makes worse)
- Wait until severe (harder to treat)
- Split up group (buddy system critical)

### Elderly at Home

**Hidden hypothermia risk:**

**Why vulnerable:**
```
├─ Reduced ability to sense cold
├─ Reduced ability to generate heat (slower metabolism)
├─ Reduced shivering response
├─ Medications affect temperature regulation
├─ Limited mobility (can't put on more clothes, adjust heating)
├─ Economic factors (heating costs)
└─ Social isolation (no one checking on them)
```

**Indoor hypothermia:**
- Can occur at 15-20°C indoor temperature
- Often gradual onset
- May not realize how cold they are

**Prevention:**
```
Home environment:
├─ Maintain 20-24°C indoor temperature
├─ Adequate heating (affordable, accessible)
├─ Draft excluders
├─ Heavy curtains
└─ Carpets/rugs

Personal:
├─ Multiple layers (easier than one heavy item)
├─ Hat indoors (lots of heat lost through head)
├─ Warm socks, slippers
├─ Hot water bottle (wrapped safely)
└─ Regular hot drinks and meals

Social:
├─ Regular check-ins (family, neighbors, services)
├─ Phone calls
├─ Meal delivery (ensures hot food)
└─ Community center visits
```

**Signs to watch for:**
- Confusion (may be only sign)
- Slow movements
- Pale, cold skin
- Drowsiness
- Slow speech

**If suspected:** Call doctor/000, gently rewarm, monitor closely.

### Babies & Children

**Higher risk:**
```
├─ Larger surface area to body weight ratio
├─ Lose heat faster
├─ Less body fat (insulation)
├─ Can't tell you they're cold
└─ Can't put on more clothes themselves
```

**Prevention:**
```
Indoors:
├─ Room temperature 20-22°C
├─ Extra layer than adult would wear
├─ Hat for newborns (even indoors)
├─ Check extremities (hands, feet should be warm)
└─ Not too many blankets (SIDS risk)

Outdoors:
├─ Layer clothing
├─ Waterproof outer layer
├─ Hat (always)
├─ Mittens (warmer than gloves)
├─ Limit time in cold
└─ Check frequently (can't tell you)
```

**Signs:**
- Quiet, lethargic
- Refusing food
- Skin cool to touch (especially abdomen)
- Pale or blue-tinged skin
- Weak cry

**Treatment:**
- Skin-to-skin contact (under blankets)
- Wrap in warm blankets
- Warm room
- Warm (not hot) bath if mild and conscious
- Call doctor/000 if concerned

---

## Prevention Strategies

### Clothing System

**Layering principle:**

```
Base layer (next to skin):
├─ Purpose: wick moisture away
├─ Material: merino wool, synthetic
├─ ✗ NEVER cotton ("cotton kills" when wet)
└─ Long underwear, thermal top

Mid layer (insulation):
├─ Purpose: trap warm air
├─ Material: fleece, down, synthetic insulation
├─ Multiple thin layers better than one thick
└─ Jacket, vest, extra fleece

Outer layer (shell):
├─ Purpose: block wind and rain
├─ Material: waterproof, breathable (Gore-tex, etc.)
├─ Critical in wind/rain
└─ Rain jacket, waterproof pants

Extremities:
├─ Hat (30% of heat loss through head)
├─ Gloves or mittens (mittens warmer)
├─ Warm socks (wool or synthetic)
└─ Waterproof boots
```

**Why cotton is dangerous:**
- Absorbs water (sweat or rain)
- Holds moisture against skin
- Conducts heat away from body when wet
- Loses all insulation value
- "Cotton kills" in cold, wet conditions

### The "Umbles" - Early Warning

**Recognize these early signs:**

```
Stumbles  → Poor coordination
Mumbles   → Slurred speech
Fumbles   → Difficulty with fine motor tasks
Grumbles  → Unusual irritability, complaints
```

**If you or companion showing umbles:**
- STOP activity immediately
- Add layers
- Eat high-energy food
- Drink warm fluids
- Get to shelter
- Reassess before continuing

### Stay Dry

**Wetness multiplies heat loss:**

```
Causes of wetness:
├─ Rain (carry waterproof gear)
├─ Stream crossings (avoid if possible, change socks after)
├─ Snow (waterproof shell, gaiters)
├─ Sweat (remove layers before overheating)
└─ Dew (watch for in morning)

Prevention:
├─ Waterproof outer layer
├─ Pack cover or dry bags
├─ Extra dry clothes in waterproof bag
├─ Change wet clothes ASAP
└─ Ventilate to reduce sweat (unzip when active)
```

### Energy & Hydration

**Body generates heat from burning fuel:**

```
Eat regularly:
├─ High-calorie foods (nuts, chocolate, energy bars)
├─ Fats and carbs (energy for heat production)
├─ Don't wait until hungry
└─ Small amounts frequently

Drink fluids:
├─ Dehydration impairs heat production
├─ Warm drinks ideal (tea, hot chocolate, soup)
├─ Even cold water better than nothing
└─ Don't wait until thirsty
```

### Wind Chill

**Wind increases heat loss dramatically:**

```
Wind chill effect:
Air temp   Wind speed   Feels like
10°C       0 km/h       10°C
10°C       20 km/h      6°C
10°C       40 km/h      3°C
10°C       60 km/h      1°C

0°C        0 km/h       0°C
0°C        20 km/h      -5°C
0°C        40 km/h      -9°C
0°C        60 km/h      -12°C
```

**Protection:**
- Windproof outer layer critical
- Seek shelter from wind
- Natural windbreaks (rocks, trees, terrain)
- Face away from wind

### Emergency Shelter

**If caught out, need warmth:**

```
Shelter options:
├─ Tent (best)
├─ Emergency bivvy bag
├─ Space blanket (limited, but better than nothing)
├─ Tarp/fly (with ground sheet)
├─ Natural shelter:
│   ├─ Dense trees (less wind)
│   ├─ Rock overhang (dry)
│   ├─ Snow cave (if enough snow, advanced skill)
│   └─ Avoid low areas (cold air sinks)
└─ Improvised (branches, leaves, anything)
```

**Insulation from ground:**
- Sleeping pad
- Pack
- Branches, leaves, extra clothing
- Ground conducts heat away very effectively

---

## Risk Factors

**Higher risk individuals:**

```
Age:
├─ Elderly (impaired temperature regulation)
├─ Infants (lose heat quickly)
└─ Very young children (can't communicate)

Medical:
├─ Diabetes
├─ Hypothyroidism
├─ Heart disease
├─ Malnutrition
├─ Dementia (poor judgment, may not dress appropriately)
└─ Previous hypothermia (increased susceptibility)

Medications:
├─ Alcohol (dilates blood vessels, loses heat)
├─ Beta-blockers (reduce shivering)
├─ Sedatives (reduce awareness)
└─ Some psychiatric medications

Behavioral:
├─ Exhaustion (reduces heat production)
├─ Inadequate clothing
├─ Hunger (no fuel for heat)
├─ Dehydration
└─ Homelessness

Environmental:
├─ Cold air temperature
├─ Wind
├─ Wet conditions (rain, immersion)
├─ Unexpected cold (unprepared)
└─ Prolonged exposure
```

---

## Myths vs Facts

**MYTH:** "You need freezing temperatures for hypothermia"
**FACT:** Can occur at 10-15°C if wet, windy, or exhausted.

**MYTH:** "Alcohol warms you up"
**FACT:** Dilates blood vessels, increases heat loss. Feels warm but actually dangerous.

**MYTH:** "Rub extremities to rewarm"
**FACT:** Can cause tissue damage and send cold blood to core (dangerous).

**MYTH:** "Give hot bath to severe hypothermia victim"
**FACT:** Can cause rewarming shock and cardiac arrest. Gradual warming only.

**MYTH:** "If they stop shivering, they're warming up"
**FACT:** Stopped shivering = severe hypothermia, body can't warm itself.

**MYTH:** "Cotton is fine for bushwalking"
**FACT:** "Cotton kills" - loses all insulation when wet.

---

## Summary Checklist

### Prevention
- [ ] Layer clothing (base, mid, outer)
- [ ] Avoid cotton (wool or synthetic)
- [ ] Stay dry (waterproof outer layer)
- [ ] Eat and drink regularly
- [ ] Recognize early signs (umbles)
- [ ] Carry emergency shelter & space blanket

### Recognition
- [ ] Mild: shivering, confusion, stumbling
- [ ] Moderate: no shivering, severe confusion, drowsy
- [ ] Severe: barely/un conscious, rigid, very slow breathing

### Treatment - Mild
- [ ] Get to shelter
- [ ] Remove wet clothes
- [ ] Add dry layers
- [ ] Warm drinks & food
- [ ] Monitor closely

### Treatment - Moderate/Severe
- [ ] Call 000
- [ ] Handle extremely gently
- [ ] Keep horizontal
- [ ] Prevent further heat loss (insulate)
- [ ] NO active rewarming
- [ ] Monitor breathing (ready for CPR)

---

---

## Diagram

```diagram flowchart
START: Recognize symptoms
STEP: Move to shelter
STEP: Remove wet clothing
STEP: Warm gradually
END: Monitor & treat
```

---

## Related Guides

- **Shelter Construction:** `GUIDE START shelter-construction`
- **Layering for Cold:** `GUIDE START cold-weather-clothing` (when created)
- **Emergency Signaling:** `GUIDE START emergency-signaling` (when created)
- **CPR:** `GUIDE START basic-cpr`
- **Shock Treatment:** `GUIDE START shock-treatment`

---

**Key Principle:** Prevention is far easier than treatment. Layer properly, stay dry, eat/drink regularly, and recognize early warning signs.

**Emergency Number:** 000 (Australia)

**Remember:** "Cotton kills, wool wins" and "Not dead until warm and dead"
