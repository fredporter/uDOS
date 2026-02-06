---
uid: udos-guide-medical-20251204171400-UTC-L300AB52
title: Heat Stroke & Heat Exhaustion
tags: [guide, knowledge, medical]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Heat Stroke & Heat Exhaustion

**Category:** Emergency Medical
**Priority:** CRITICAL - Can be fatal
**Season:** High risk in hot months (Oct-Mar)
**Time Sensitive:** Heat stroke is a medical emergency

---

## Overview

Heat-related illness occurs when the body can't cool itself effectively. In hot climates, this is a serious and potentially deadly risk.

**Two main conditions:**
1. **Heat Exhaustion** - Serious but treatable
2. **Heat Stroke** - LIFE THREATENING emergency

### Heat Illness Assessment Flowchart

```flow
st=>start: Person in hot environment
symptoms=>condition: Heat symptoms present?
temp=>condition: Temp > 40°C?
sweat=>condition: Still sweating?
mental=>condition: Confused/altered?
exhaust=>operation: Heat Exhaustion
stroke=>operation: Heat Stroke
cool=>operation: Move to cool location
hydrate=>operation: Give water slowly
emerg=>operation: Call 911 immediately
ice=>operation: Apply ice packs
monitor=>operation: Monitor closely
recov=>end: Recovery
hosp=>end: Hospital treatment

st->symptoms
symptoms(yes)->temp
symptoms(no)->recov
temp(yes)->stroke->emerg->ice->hosp
temp(no)->sweat
sweat(yes)->mental
sweat(no)->stroke->emerg->ice->hosp
mental(yes)->stroke->emerg->ice->hosp
mental(no)->exhaust->cool->hydrate->monitor->recov
```

### Heat Exhaustion Treatment Sequence

```sequence
Rescuer->Victim: Identify heat exhaustion
Victim->Rescuer: Check symptoms
Rescuer->Cool: Move to shade/AC
Cool->Remove: Remove excess clothing
Remove->Apply: Apply cool wet cloths
Apply->Fan: Fan while misting
Fan->Drink: Give water slowly
Drink->Elevate: Elevate legs
Elevate->Monitor: Monitor for 30 min
Monitor->Check: Symptoms improving?
Check->Rescuer: Continue cooling
Rescuer->Recovery: Rest 24 hours
```

### Heat Stroke Emergency Response

```sequence
Rescuer->Victim: Identify heat stroke
Victim->Emergency: Call 911 immediately
Emergency->Cool: Begin rapid cooling
Cool->Ice: Apply ice to neck, armpits, groin
Ice->Water: Immerse in cool water if possible
Water->Monitor: Check vitals continuously
Monitor->Position: Recovery position if unconscious
Position->Ambulance: Await emergency services
Ambulance->Hospital: Immediate transport
Hospital->Treatment: Intensive care
```

---

## Heat Exhaustion

**What it is:** Body overheating but still able to sweat and cool itself (partially).

### Signs & Symptoms

```
Physical:
├─ Heavy sweating (key sign - still sweating)
├─ Pale, cool, clammy skin
├─ Fast, weak pulse
├─ Muscle cramps
├─ Fatigue, weakness
├─ Nausea, vomiting
└─ Headache, dizziness

Mental:
├─ Mild confusion
├─ Irritability
└─ Anxiety
```

**Temperature:** 37-40°C (normal to slightly elevated)

### Treatment

**Immediate actions:**

1. **Move to cool place**
   - Shade or air conditioning
   - Out of sun immediately
   - Lie down, elevate legs slightly

2. **Cool the body**
   - Remove excess clothing
   - Apply cool, wet cloths to neck, armpits, groin
   - Fan while misting with water
   - Cool shower if able

3. **Rehydrate**
   - Sip water slowly (don't chug)
   - 250ml every 15 minutes
   - Electrolyte drink if available
   - NO alcohol or caffeine

4. **Monitor closely**
   - Stay with person
   - Watch for worsening symptoms
   - If no improvement in 30-60 minutes → seek medical help
   - If vomiting continues → seek medical help

**Recovery:** Rest for 24 hours minimum, avoid heat

---

## Heat Stroke

**What it is:** Body's cooling system has FAILED. Core temperature dangerously high.

⚠️ **THIS IS A MEDICAL EMERGENCY - CALL 000**

### Signs & Symptoms

```
Critical Signs:
╔════════════════════════════════════════╗
║ Temperature > 40°C (104°F)             ║
║ DRY, hot skin (NOT sweating)           ║
║ Altered mental state (confused, etc)   ║
║ Any ONE of these = HEAT STROKE         ║
╚════════════════════════════════════════╝

Physical:
├─ Hot, DRY skin (sweating has stopped)
├─ OR profuse sweating that won't cool them
├─ Rapid, strong pulse (then weak)
├─ Throbbing headache
├─ Nausea, vomiting
├─ Seizures
└─ Unconsciousness

Mental:
├─ Confusion, disorientation
├─ Slurred speech
├─ Aggressive behavior
├─ Hallucinations
└─ Loss of consciousness
```

**Key difference from exhaustion:** NO sweating or sweating ineffective, temperature > 40°C, severe confusion/unconsciousness.

### Treatment

**THIS IS LIFE OR DEATH - ACT FAST**

```
Priority Order:
1. CALL 000 (emergency services)
2. COOL THE PERSON (immediately)
3. Monitor and support until help arrives
```

**Cooling steps:**

1. **Move to shade/cool area immediately**

2. **Remove clothing** (down to underwear)

3. **Cool the body rapidly** (every second counts):

   **Best methods:**
   - Immerse in cold water (bath, creek, pool) if possible
   - Cover with wet sheets and fan continuously
   - Ice packs to neck, armpits, groin
   - Spray with water and fan
   - Wet towels over body, replace as they warm

   **Goal:** Get temperature below 39°C as fast as possible

4. **Monitor:**
   - Check breathing
   - Check consciousness
   - Check temperature if possible
   - Be ready for CPR if breathing stops

**DO NOT:**
- Give aspirin or paracetamol (won't help, may harm)
- Give anything to drink if unconscious
- Leave person alone
- Use alcohol rubs (dangerous)
- Cool too rapidly if conscious and improving (can cause shock)

**Recovery:** Hospital treatment required. Can take days to fully recover. Risk of organ damage.

---

## Risk Factors

**Environmental:**
- High temperature (> 35°C)
- High humidity (sweat doesn't evaporate)
- Direct sun exposure
- No breeze/air movement
- First hot day of season (not acclimatized)

**Personal:**
- Not used to heat (visitors, recent arrivals)
- Dehydration
- Heavy physical activity in heat
- Age (very young, elderly)
- Alcohol or drug use
- Certain medications (diuretics, antihistamines)
- Obesity
- Previous heat illness
- Medical conditions (heart disease, diabetes)

**Occupational:**
- Outdoor work
- Physical labor
- Heavy/protective clothing
- Limited shade access

---

## Prevention

### Hydration

```
Water Intake Guidelines:

Normal conditions:
├─ 2-3 litres per day

Hot weather (not active):
├─ 3-4 litres per day

Hot weather + physical work:
├─ 500ml-1L per hour
└─ Drink BEFORE thirsty

Signs of adequate hydration:
├─ Pale yellow urine
├─ Urinating regularly (every 2-4 hours)
└─ No excessive thirst
```

**Electrolytes matter:**
- Add pinch of salt to water if sweating heavily
- Sports drinks (dilute by half)
- Eat salty snacks with water

### Clothing

**Best choices:**
- Light colors (reflect heat)
- Loose fitting (air circulation)
- Breathable fabrics (cotton, linen)
- Wide-brimmed hat
- Sunglasses

**Avoid:**
- Dark colors
- Tight clothing
- Synthetic fabrics (except modern athletic wear)

### Activity Modification

**Hot day strategies:**

```
Daily Schedule:
06:00-10:00  ████████ Work/activity (cooler)
10:00-15:00  ░░░░░░░░ REST in shade (hottest)
15:00-19:00  ████████ Work/activity (cooling)
19:00-06:00  ████████ Normal activity (cool)
```

**During activity:**
- Take breaks every 15-30 minutes
- Rest in shade
- Drink water each break
- Remove hat/helmet to cool head
- Wet hair/neck

**Acclimatization:**
- Takes 7-14 days to adjust to heat
- Gradually increase activity in heat
- First few days = shortest work periods

### Environment Control

**Create cool spaces:**
- Shade structures
- Wet towels over doorways (evaporative cooling)
- Cross-ventilation (open opposite windows)
- Close curtains/blinds during day
- Fans (effective up to ~35°C)
- Mist fans (even better)

**Cooling techniques:**
- Cold shower before activity
- Wet bandana around neck
- Spray bottle for misting
- Feet in cool water during breaks
- Damp shirt (evaporative cooling)

---

## High-Risk Situations

### Working in Heat

**Warning signs you need to stop:**
- Stopped sweating (or very little sweat)
- Dizziness, lightheadedness
- Muscle cramps
- Extreme fatigue
- Nausea
- Headache
- Feeling very hot

**Action:** Stop immediately, rest in shade, hydrate, cool down.

### Outdoor Events/Festivals

**Extra risks:**
- Crowds (hard to cool off)
- Alcohol (dehydrates)
- Dancing/activity (generates heat)
- Limited shade
- Peer pressure to "keep going"

**Safety:**
- Drink water between every alcoholic drink
- Take regular shade breaks
- Watch friends for signs
- Leave if feeling unwell

### Vehicles

**Never leave anyone in a parked car:**
- Car interior can reach 60°C+ in 10 minutes
- Even with windows cracked
- Even in shade
- ESPECIALLY children/elderly/pets

**If vehicle breaks down:**
- Stay with vehicle (shelter, visible)
- Create shade (clothing, seat covers)
- Ration water
- Signal for help
- Only walk if you know help is close (< 2km)

---

## Treatment Comparison

```
╔═══════════════╦════════════════════╦═══════════════════╗
║ Aspect        ║ Heat Exhaustion    ║ Heat Stroke       ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Sweating      ║ Heavy sweating     ║ NO sweating       ║
║               ║                    ║ (or ineffective)  ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Skin          ║ Cool, pale, clammy ║ Hot, dry/flushed  ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Temperature   ║ < 40°C             ║ > 40°C            ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Mental state  ║ Mild confusion     ║ Severe confusion  ║
║               ║ Irritable          ║ or unconscious    ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Urgency       ║ Serious            ║ LIFE THREATENING  ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Treatment     ║ Cool, rest, fluids ║ CALL 000          ║
║               ║ Monitor closely    ║ Rapid cooling     ║
╠═══════════════╬════════════════════╬═══════════════════╣
║ Recovery      ║ 24 hours rest      ║ Hospital required ║
║               ║                    ║ Days to recover   ║
╚═══════════════╩════════════════════╩═══════════════════╝
```

---

## When to Seek Medical Help

**IMMEDIATE (call 000):**
- Temperature > 40°C
- Unconscious or very confused
- Seizure
- Not sweating despite heat
- Difficulty breathing
- Chest pain
- No improvement after cooling

**Soon (GP/clinic):**
- Heat exhaustion not improving after 1 hour of treatment
- Vomiting continues (can't keep fluids down)
- Symptoms return
- Concerned about complications

---

## Special Populations

### Children

**Higher risk because:**
- Generate more heat relative to size
- Less efficient sweating
- May not recognize symptoms
- May not ask for water

**Extra precautions:**
- Frequent water breaks (every 15 minutes)
- Limit active play in heat
- Light clothing
- Shade mandatory
- Watch closely

### Elderly

**Higher risk because:**
- Less able to regulate temperature
- Reduced thirst sensation
- Medications affect cooling
- May have mobility issues (can't get water/shade)

**Extra precautions:**
- Scheduled hydration (don't rely on thirst)
- Check on regularly
- Air conditioning or cool room access
- Medical alert if alone

### Pregnant Women

**Higher risk:**
- Increased metabolic heat
- Dehydration affects baby

**Extra precautions:**
- Reduce activity in heat
- Increase hydration
- Frequent cooling breaks
- Consult doctor if heat exposure required

---

## Homemade Rehydration Solution

**If sports drinks unavailable:**

```
Recipe:
1 litre clean water
6 teaspoons sugar
½ teaspoon salt

Mix well and drink.
```

**Why it works:**
- Sugar helps absorb water faster
- Salt replaces lost electrolytes
- Better than plain water for heavy sweating

---

## Summary Checklist

### Prevention
- [ ] Drink water regularly (don't wait for thirst)
- [ ] Wear light, loose clothing
- [ ] Take breaks in shade
- [ ] Avoid midday heat (10am-3pm)
- [ ] Acclimatize gradually

### Recognition
- [ ] Know the difference: sweating = exhaustion, no sweat = stroke
- [ ] Watch for confusion, dizziness, nausea
- [ ] Check on vulnerable people regularly

### Treatment
- [ ] Heat exhaustion: cool, rest, fluids, monitor
- [ ] Heat stroke: CALL 000, cool rapidly, don't leave alone

---

## Related Guides

- **Dehydration:** `GUIDE START dehydration-treatment`
- **CPR:** `GUIDE START basic-cpr` (if person stops breathing)
- **Shock:** `GUIDE START shock-treatment`
- **Water Safety:** `GUIDE START water-sources`

---

**Remember:** Heat illness is preventable. Most deaths occur because people:
1. Don't recognize symptoms early
2. Don't stop activity soon enough
3. Don't cool down aggressively enough

When in doubt, stop, cool down, hydrate. You can always resume later. You can't undo heat stroke.

**Emergency Number:** 000 (Australia)
