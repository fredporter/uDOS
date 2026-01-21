---
tier: 3
category: medical
title: "Shock Treatment & Recognition"
complexity: advanced
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Shock Treatment & Recognition

**Category:** Medical - Critical Emergency
**Priority:** CRITICAL - Life threatening, requires immediate action
**Season:** Year-round risk
**Difficulty:** Moderate - recognition crucial, treatment straightforward

---

## Overview

Shock is a life-threatening condition where the body's organs and tissues don't receive enough blood flow and oxygen.

**Not the same as:**
- Emotional shock (psychological response)
- Electric shock (electrical injury)

**Medical shock = circulatory failure**

```
Normal circulation:
Heart → Blood vessels → Organs → Oxygen delivered ✓

Shock:
Heart → Blood vessels → Organs → Insufficient oxygen ✗
                ↓
        Organs begin to fail
                ↓
        Death if untreated
```

**Timeline:** Can progress rapidly (minutes to hours). Early recognition and treatment crucial.

### Shock Recognition & Response Flowchart

```flow
st=>start: Victim injured/ill
signs=>condition: Shock signs present?
call=>operation: Call 911 immediately
type=>condition: Identify shock type
hypo=>operation: Treat bleeding/fluids
ana=>operation: Use EpiPen
card=>operation: Position comfortably
position=>operation: Elevate legs 12 inches
warm=>operation: Keep warm
monitor=>operation: Monitor vitals
help=>condition: Help arrived?
cont=>operation: Continue care
hosp=>end: Hospital treatment

st->signs
signs(yes)->call->type
signs(no)->monitor
type(hypovolemic)->hypo->position
type(anaphylactic)->ana->position
type(cardiogenic)->card->position
position->warm->monitor->help
help(no)->cont->help
help(yes)->hosp
```

### Shock Treatment Sequence

```sequence
Rescuer->Victim: Assess for shock signs
Victim->Rescuer: Signs detected
Rescuer->Emergency: Call 911
Emergency->Rescuer: Help on the way
Rescuer->Victim: Stop visible bleeding
Victim->Rescuer: Control bleeding
Rescuer->Victim: Lay victim flat
Victim->Rescuer: Elevate legs 12 inches
Rescuer->Victim: Keep warm with blanket
Victim->Rescuer: Loosen tight clothing
Rescuer->Victim: Do not give food/water
Victim->Monitor: Check pulse/breathing
Monitor->Rescuer: Vitals checked
Rescuer->Victim: Provide reassurance
Victim->Ambulance: Transport to hospital
```

---

## Types of Shock

### Hypovolemic Shock (Volume Loss)

**Cause:** Not enough blood/fluid in circulatory system

**Common causes:**
```
Bleeding:
├─ External wounds
├─ Internal bleeding (not visible)
├─ Ruptured organs
└─ Major fractures (femur can lose 1-2L internally)

Fluid loss:
├─ Severe dehydration
├─ Severe vomiting/diarrhea
├─ Burns (fluid loss through damaged skin)
└─ Heat exhaustion/stroke
```

**Most common type** after trauma.

### Cardiogenic Shock (Heart Problem)

**Cause:** Heart can't pump effectively

**Common causes:**
```
├─ Heart attack
├─ Severe irregular heartbeat
├─ Heart valve problems
└─ Heart muscle damage
```

**Recognition:** Often chest pain, difficulty breathing, history of heart problems.

### Anaphylactic Shock (Severe Allergic Reaction)

**Cause:** Extreme allergic reaction causing blood vessels to dilate

**Common triggers:**
```
├─ Insect stings (bees, wasps, ants)
├─ Food allergies (nuts, shellfish, eggs)
├─ Medications (antibiotics, pain relievers)
└─ Latex
```

**Rapid onset:** Can progress to life-threatening in minutes.

**Key signs:**
- Swelling (face, lips, tongue, throat)
- Difficulty breathing/swallowing
- Hives, rash
- Rapid progression

### Septic Shock (Infection)

**Cause:** Severe infection spreads through bloodstream

**Common sources:**
```
├─ Pneumonia
├─ Urinary tract infection
├─ Abdominal infections
├─ Wound infections
└─ Bacterial bloodstream infection
```

**Timeline:** Usually develops over hours to days (not immediate).

**Key signs:**
- Fever (or sometimes very low temperature)
- Confusion
- Rapid breathing
- Known infection

### Neurogenic Shock (Nerve System)

**Cause:** Spinal cord injury disrupts blood vessel control

**Common causes:**
```
├─ Spinal cord injury
├─ Severe head injury
└─ Spinal anesthesia complications
```

**Different presentation:**
- May have warm, dry skin (not cold, clammy)
- Normal or slow heart rate (not rapid)

---

## Recognition - Universal Signs

**Regardless of type, most shock presents with:**

### Early Signs (Compensated Shock)

Body is trying to maintain blood pressure:

```
Mental state:
├─ Anxiety, restlessness
├─ Feeling of impending doom
├─ Confused, disoriented
└─ Increasingly agitated

Skin:
├─ Pale, cool, clammy (cold sweat)
├─ Grayish color
├─ Blue lips/fingernails (cyanosis)
└─ Mottled appearance

Vital signs:
├─ Rapid pulse (> 100 bpm)
├─ Weak pulse
├─ Rapid breathing (> 20 breaths/min)
├─ Shallow breathing
└─ Normal or slightly low blood pressure (still compensating)

Other:
├─ Thirst
├─ Nausea
└─ Weakness
```

**Critical:** If you recognize these signs, treat immediately. Don't wait for worsening.

### Late Signs (Decompensated Shock)

Body can no longer maintain blood pressure:

```
Mental state:
├─ Severe confusion
├─ Unresponsive
├─ Unconscious
└─ Seizures possible

Skin:
├─ Very pale or bluish
├─ Cold to touch
└─ Clammy, sweaty

Vital signs:
├─ Very rapid, weak pulse (> 120 bpm)
├─ OR very slow pulse (near death)
├─ Rapid, gasping breathing
├─ Low blood pressure (< 90 systolic)
└─ Irregular breathing

Other:
├─ Dilated pupils
├─ No urine output
└─ Organ failure beginning
```

⚠️ **MEDICAL EMERGENCY - Minutes matter**

---

## Immediate Treatment

### Call 000 First

**Always call emergency services if you suspect shock:**
- Tell them: "Person is in shock" or "Person showing signs of shock"
- Provide location
- Describe what happened
- Stay on line for instructions

### General Shock Treatment (While Waiting for Ambulance)

**The "Shock Position":**

```
1. Lay person flat on back
   ├─ On firm surface if possible
   ├─ Clear area around them
   └─ Unless:
       ├─ Spinal injury suspected → don't move
       ├─ Head injury → raise head slightly (30°)
       ├─ Difficulty breathing → raise head/shoulders
       ├─ Vomiting → turn on side
       └─ Pregnant → tilt to left side

2. Elevate legs 30cm (12 inches)
   ├─ Use blankets, backpack, pillows
   ├─ Brings blood to vital organs
   └─ DON'T elevate if:
       ├─ Suspected spine, neck, hip, leg fracture
       ├─ Difficulty breathing (makes worse)
       ├─ Head injury
       └─ Snakebite (keep limb still and level)

3. Keep warm
   ├─ Cover with blanket, jacket, towels
   ├─ Prevent heat loss (shock impairs temperature regulation)
   ├─ Under AND over if possible
   └─ DON'T overheat (no electric blankets, hot water bottles)

4. Reassure
   ├─ Talk calmly
   ├─ Explain what you're doing
   ├─ Stay with them
   └─ Reduces anxiety (helps slow progression)

5. Monitor continuously
   ├─ Check breathing every minute
   ├─ Check pulse if able
   ├─ Watch for changes
   └─ Be ready to start CPR if needed
```

**Visual - Shock Position:**
```
        ╭───╮
        │ ○ │  ← Head (flat or slightly raised)
        ╰───╯
         ╱╲
    ═══╱══╲═══  ← Body (flat on back)
      ╱    ╲
     ╱      ╲
    ▲▲      ▲▲  ← Legs elevated 30cm
    ▲▲      ▲▲
    ▲▲▲▲▲▲▲▲▲▲  ← Support (blankets, backpack)
```

### What NOT to Do

```
DON'T:
├─ ✗ Give anything to eat or drink (may need surgery)
│   Exception: Conscious diabetic in low blood sugar shock
├─ ✗ Move person unnecessarily (unless in danger)
├─ ✗ Leave person alone (except briefly to call 000)
├─ ✗ Overheat (causes blood to pool in skin, away from organs)
├─ ✗ Give alcohol or cigarettes
├─ ✗ Let person sit or stand up
└─ ✗ Dismiss their symptoms ("You'll be fine")
```

---

## Specific Treatments

### Bleeding/Hemorrhagic Shock

**Priority:** Stop the bleeding

```
1. Direct pressure
   ├─ Clean cloth/dressing on wound
   ├─ Press firmly
   ├─ Don't remove first dressing (add more on top)
   └─ Maintain pressure continuously

2. Elevate if limb (and no fracture)

3. Pressure points if bleeding not controlled
   ├─ Arm: brachial artery (inner upper arm)
   └─ Leg: femoral artery (groin crease)

4. Tourniquet only if:
   ├─ Severe, life-threatening bleeding
   ├─ Direct pressure failed
   ├─ Amputation or severe limb trauma
   └─ Note time applied (write on person's forehead if needed)

5. Shock position once bleeding controlled
```

**For internal bleeding:**
- Can't see it, can't stop it
- Suspect if: severe impact, abdominal pain, distended abdomen, shock signs without obvious injury
- Keep person still, shock position, call 000

### Anaphylactic Shock

⚠️ **Use EpiPen/adrenaline auto-injector if available**

```
1. Call 000 immediately
   "Anaphylaxis" or "severe allergic reaction"

2. Use adrenaline auto-injector
   ├─ If person has one, use it
   ├─ Inject into outer mid-thigh
   ├─ Can go through clothing if needed
   ├─ Hold for 3 seconds
   ├─ Massage injection site 10 seconds
   └─ Note time of injection

3. Position based on symptoms
   ├─ If breathing OK: shock position (flat, legs up)
   ├─ If breathing difficult: sit up
   ├─ If unconscious: recovery position (on side)
   └─ If pregnant: left side

4. May need second dose
   ├─ If no improvement after 5 minutes
   ├─ Use second EpiPen if available
   └─ Tell ambulance how many doses given

5. Monitor continuously
   ├─ Ready to start CPR if needed
   └─ Condition can deteriorate rapidly
```

**Even if EpiPen works and person improves:**
- Still need emergency medical care
- Can relapse (biphasic reaction)
- Hospital observation required

### Cardiogenic Shock (Heart Attack)

```
1. Call 000 - "suspected heart attack"

2. Position
   ├─ Sit up or semi-reclined (easier to breathe)
   ├─ NOT flat (makes breathing harder)
   └─ Support with pillows, backpack

3. Aspirin if available
   ├─ One 300mg tablet (chew it)
   ├─ Only if:
   │   ├─ Conscious and can swallow
   │   ├─ Not allergic to aspirin
   │   └─ No stomach bleeding history
   └─ Helps prevent clot from getting worse

4. Loosen tight clothing

5. Keep calm, reassure

6. Monitor breathing
   └─ Ready for CPR if stops breathing
```

**Do NOT:**
- Lay flat (makes breathing worse)
- Give water or food
- Leave person alone

### Septic Shock (Infection)

```
1. Call 000 - needs hospital treatment (IV antibiotics)

2. Shock position (flat, legs up)

3. Keep warm

4. Monitor closely
   └─ Can deteriorate rapidly

5. Note symptoms for ambulance
   ├─ When symptoms started
   ├─ Known infection source
   ├─ Recent illnesses/injuries
   └─ Medications taken
```

---

## Special Situations

### Bush/Remote Location

**Challenges:**
- No ambulance available
- Limited supplies
- Evacuation difficult

**Priorities:**

```
1. Activate emergency beacon/call for help
   ├─ Satellite phone
   ├─ PLB (Personal Locator Beacon)
   ├─ EPIRB (Emergency Position Indicating Radio Beacon)
   └─ Mobile if any signal

2. Treat based on cause
   ├─ Bleeding: stop it (pressure, elevation, tourniquet if needed)
   ├─ Dehydration: oral rehydration if conscious
   ├─ Allergic: EpiPen if available
   └─ Unknown: treat symptoms

3. Shock position
   ├─ Keep warm (critical in bush)
   ├─ Protect from elements
   └─ Shelter if possible

4. Evacuation decision
   ├─ Severe shock = need helicopter evacuation
   ├─ Don't attempt to walk person out
   ├─ Wait for rescue if help is coming
   └─ Only move if in immediate danger (fire, flood, etc.)

5. Continuous monitoring
   ├─ Breathing
   ├─ Pulse
   ├─ Consciousness
   └─ Temperature
```

**Improvised warming:**
- Space blanket (gold/silver emergency blanket)
- Sleeping bag
- Multiple layers clothing
- Body heat from others (carefully)
- Insulate from ground

### Pregnant Person

**Modifications:**

```
1. Don't lay flat on back after 20 weeks pregnancy
   ├─ Uterus compresses major blood vessels
   ├─ Makes shock worse
   └─ Can reduce blood flow to baby

2. Left side position
   ├─ Tilt to left side (15-30°)
   ├─ Use rolled blanket/clothing behind back
   └─ Relieves pressure on blood vessels

3. If must be on back
   ├─ Tilt pelvis to left
   ├─ Put rolled blanket under right hip
   └─ Shifts uterus off blood vessels
```

**Any shock in pregnancy = urgent**
- Mother and baby both at risk
- Call 000 immediately

### Children

**Differences:**

**Recognition harder:**
- Children compensate better initially
- Can look OK then deteriorate rapidly
- Lower threshold for calling 000

**Vital signs different:**

```
Normal heart rate by age:
├─ Infant (0-1 year):     100-160 bpm
├─ Toddler (1-3 years):   90-150 bpm
├─ Preschool (3-5 years): 80-140 bpm
├─ School age (6-12):     70-120 bpm
└─ Adolescent (12+):      60-100 bpm

Shock = heart rate significantly above these ranges
```

**Treatment same principles:**
- Shock position (flat, legs elevated)
- Keep warm
- Reassure (child and parents)
- Call 000

### Elderly

**Higher risk:**
- Less physiological reserve
- Medications may mask symptoms
- Chronic conditions complicate

**Special considerations:**
- May not show typical signs (pulse may not increase if on beta-blockers)
- Confusion may be early sign
- Skin may always be cool (poor circulation)
- Lower threshold for emergency care

---

## Monitoring While Waiting for Help

### Check and Record

**Every 5 minutes, check:**

```
AVPU Scale (Consciousness):
├─ A = Alert (awake, responding normally)
├─ V = Responds to Voice (needs calling to respond)
├─ P = Responds to Pain (only responds to pinch)
└─ U = Unresponsive (no response at all)

Breathing:
├─ Rate (count for 30 seconds, double it)
├─ Depth (shallow, normal, labored)
└─ Sound (quiet, wheezing, gurgling)

Pulse (if can find it):
├─ Rate (count for 30 seconds, double it)
├─ Strength (strong, weak, thready)
└─ Regular vs irregular

Skin:
├─ Color (pink, pale, gray, blue)
├─ Temperature (warm, cool, cold)
└─ Moisture (dry, clammy, sweaty)

Pupils:
├─ Size (equal, dilated, constricted)
└─ Reaction to light (if can check)
```

**Write it down if possible:**
- Helps ambulance crew
- Track if improving or worsening

**Example record:**
```
Time    AVPU  Breathing  Pulse  Skin
14:30   A     18/min     95     Pale, cool
14:35   V     22/min     110    Pale, clammy
14:40   V     24/min     120    Gray, clammy
```

---

## Recovery Position

**Use if:**
- Unconscious but breathing
- Risk of vomiting
- You must leave briefly (to call for help)

**How:**

```
1. Kneel beside person
2. Straighten legs
3. Place near arm at right angle
4. Bring far arm across chest, back of hand to near cheek
5. Bend far knee
6. Roll toward you, supporting head
7. Adjust hand under cheek
8. Tilt head back to keep airway open
9. Check breathing continues
```

**Visual:**
```
     ╭───╮
     │ ○─┤ ← Head tilted back, hand under cheek
     ╰───╯
      ╱│
     ╱ │╲
    ╱  │ ╲
   ▼   │  ▼ ← One knee bent, stable position
```

**Prevents:**
- Airway blockage from tongue falling back
- Choking on vomit
- Aspiration

**Still monitor closely** - breathing can stop.

---

## Prevention

### General

```
Awareness:
├─ Know your allergies (wear medical alert bracelet)
├─ Carry EpiPen if prescribed
├─ Manage chronic conditions
└─ Stay hydrated (especially heat, exercise)

Safety:
├─ Wear protective equipment (work, sports)
├─ Follow safety rules (driving, heights, machinery)
├─ Safe food handling (prevent infection)
└─ Proper wound care (prevent infection)

Medical:
├─ Control diabetes
├─ Manage heart conditions
├─ Take medications as prescribed
└─ Regular check-ups
```

### Recognize and Act Early

**Early treatment prevents progression:**
- If someone looks unwell after injury → monitor closely
- If vital signs changing → call for help early
- Trust your instincts → better to call 000 unnecessarily than too late

---

## When to Seek Medical Care

### Call 000 if:

```
⚠️ Signs of shock:
├─ Pale, cool, clammy skin
├─ Rapid, weak pulse
├─ Rapid breathing
├─ Confusion, anxiety
├─ Weakness, dizziness
└─ After any significant injury

⚠️ After treatment:
├─ Used EpiPen (even if improved)
├─ Severe bleeding (even if stopped)
├─ Possible internal bleeding
├─ Suspected heart attack
└─ Severe infection signs
```

### See Doctor Same Day if:

- Moderate injury with some shock signs
- Persistent dizziness after dehydration
- Infection not improving with antibiotics
- Feeling "not right" after incident

**Don't minimize symptoms** - shock can be subtle initially.

---

## Psychological Shock vs Medical Shock

### Psychological Shock (Acute Stress Reaction)

**What it is:**
- Emotional response to traumatic event
- Not life-threatening (though distressing)
- Different treatment needed

**Signs:**
```
├─ Feeling numb, detached
├─ Disbelief ("This isn't real")
├─ Crying, shaking
├─ May sit very still
├─ May talk rapidly
└─ Heart may race (from anxiety, not medical shock)
```

**Key differences:**
- Skin color normal (not pale/gray)
- Pulse rapid but strong (not weak/thready)
- Can respond normally when asked questions
- Improves with reassurance

**Treatment:**
- Reassure calmly
- Remove from scene if possible
- Let them talk or stay quiet (their choice)
- Don't rush them
- Offer water if wanted
- Professional support later if needed

**Can become medical shock if:**
- Physical injury also present
- Severe anxiety causes hyperventilation → fainting → injury

**When unsure:** Treat as medical shock (better safe).

---

## Summary Checklist

### Recognition
- [ ] Pale, cool, clammy skin
- [ ] Rapid, weak pulse
- [ ] Rapid breathing
- [ ] Confusion, anxiety, restlessness
- [ ] Weakness, dizziness

### Immediate Actions
- [ ] Call 000
- [ ] Shock position (flat, legs elevated 30cm)
- [ ] Keep warm (blanket over and under)
- [ ] Treat cause if known (stop bleeding, use EpiPen, etc.)
- [ ] Reassure person
- [ ] Monitor continuously

### Don't
- [ ] Give food or drink
- [ ] Move unnecessarily
- [ ] Leave alone
- [ ] Let sit or stand up
- [ ] Dismiss symptoms

### Special Cases
- [ ] Pregnant: left side position
- [ ] Breathing difficulty: raise head/shoulders
- [ ] Unconscious: recovery position
- [ ] Vomiting: turn on side

---

## Related Guides

- **CPR:** `GUIDE START basic-cpr`
- **Wound Care & Bleeding:** `GUIDE START wound-care-bleeding`
- **Heat Illness:** `GUIDE START heat-illness`
- **Dehydration:** `GUIDE START dehydration-treatment`
- **Anaphylaxis:** `GUIDE START allergic-reactions` (when created)
- **Burns:** `GUIDE START burns-treatment`

---

**Key Principle:** Shock is a progressive emergency. Early recognition and treatment save lives. When in doubt, call 000 and start treatment.

**Emergency Number:** 000 (Australia)

**Remember:** Shock position = Flat on back, legs elevated, keep warm, reassure, monitor.

---

## Diagram

```
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐            Collect water             ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐              Pre-filter              ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐                Purify                ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐             Cool & store             ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
```
