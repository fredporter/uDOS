---
tier: 3
category: medical
title: "Choking & Airway Obstruction"
complexity: advanced
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Choking & Airway Obstruction

**Category:** Medical - Critical Emergency
**Priority:** CRITICAL - Life threatening, minutes matter
**Season:** Year-round risk
**Difficulty:** Moderate - requires quick action, proper technique

---

## Overview

Choking occurs when food or an object blocks the airway, preventing breathing.

**Critical timeline:**
```
0-4 minutes:   Brain has oxygen reserves
4-6 minutes:   Brain damage begins
6-10 minutes:  Brain damage likely
> 10 minutes:  Severe brain damage or death
```

**Speed is essential.** Don't hesitate - act immediately.

### Choking Response Flowchart

```flow
st=>start: Person choking
assess=>condition: Can cough/speak?
mild=>operation: Encourage coughing
severe=>operation: Call 911
conscious=>condition: Still conscious?
back=>operation: 5 back blows
abdom=>operation: 5 abdominal thrusts
cleared=>condition: Object cleared?
unconscious=>operation: Begin CPR
repeat=>operation: Repeat back/abdominal
safe=>end: Object expelled

st->assess
assess(yes)->mild->safe
assess(no)->severe->conscious
conscious(yes)->back->abdom->cleared
cleared(yes)->safe
cleared(no)->repeat->cleared
conscious(no)->unconscious->safe
```

### Heimlich Maneuver Sequence

```sequence
Rescuer->Victim: Identify severe choking
Victim->Rescuer: Cannot speak/breathe
Rescuer->Help: Call for emergency help
Rescuer->Victim: Stand behind victim
Victim->Rescuer: Position fist above navel
Rescuer->Victim: Grasp fist with other hand
Victim->Rescuer: Quick upward thrusts
Rescuer->Victim: Repeat 5 times
Victim->Check: Check if cleared
Check->Rescuer: Object still lodged
Rescuer->Victim: Continue thrusts
Victim->Rescuer: Object expelled
Rescuer->Victim: Monitor breathing
```

---

## Recognition

### Mild vs Severe Obstruction

```
╔════════════════════════════════════════════════════════╗
║ MILD OBSTRUCTION (Partial)                            ║
╟────────────────────────────────────────────────────────╢
║ Can cough forcefully                                   ║
║ Can speak or cry                                       ║
║ Can breathe (wheezing/noisy)                          ║
║ May be able to clear it themselves                    ║
║                                                        ║
║ ACTION: Encourage coughing, stay with them            ║
╚════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════╗
║ SEVERE OBSTRUCTION (Complete or near-complete)        ║
╟────────────────────────────────────────────────────────╢
║ ⚠️ Cannot cough or cough is weak/silent              ║
║ ⚠️ Cannot speak or cry                               ║
║ ⚠️ Cannot breathe or gasping                         ║
║ ⚠️ Universal choking sign (hands at throat)          ║
║ ⚠️ Face turning blue/purple                          ║
║ ⚠️ May become unconscious                            ║
║                                                        ║
║ ACTION: Immediate intervention required - 000         ║
╚════════════════════════════════════════════════════════╝
```

**Universal choking sign:**
```
    Both hands clutching throat
         ╭───╮
         │ O │  ← Panicked expression
         ╰───╯
      ✋╱   ╲✋  ← Hands at throat
```

**Ask:** "Are you choking?"
- If they nod but can't speak → SEVERE
- If they can say "yes" → mild (monitor)

---

## Treatment: Conscious Adult/Child (> 1 year)

### Step-by-Step Protocol

**1. ASSESS**
```
Is obstruction severe?
├─ Yes → Continue to Step 2
└─ No (can cough/speak) → Encourage coughing, stay with them
```

**2. CALL FOR HELP**
- Shout for someone to call 000
- If alone and person still conscious, treat first, call after

**3. BACK BLOWS (5 repetitions)**

```
Position:
├─ Stand to side and slightly behind
├─ Support chest with one hand (lean them forward)
├─ Deliver up to 5 sharp blows between shoulder blades
└─ Use heel of other hand

Technique:
├─ Aim between shoulder blades
├─ Sharp, upward angle
├─ Check mouth after each blow
└─ Stop if object dislodged
```

**Visual:**
```
     ╭───╮
     │ X │  ← Victim (leaning forward)
     ╰───╯
       ╱╲
      ╱  ╲
     ▼    ▼

Support →  ★  ← Back blow
chest         (between shoulders,
              upward angle)
```

**4. ABDOMINAL THRUSTS / HEIMLICH (5 repetitions)**

```
Position:
├─ Stand behind victim
├─ Wrap arms around waist
├─ Place fist above navel, below ribs
├─ Grasp fist with other hand
└─ Pull sharply inward and upward

Technique:
├─ Quick, forceful thrust
├─ Aim upward into diaphragm
├─ Check mouth after each thrust
└─ Stop if object dislodged
```

**Visual:**
```
      ╭───╮
      │ X │  ← Victim
      ╰───╯
     ╱ ▲▲ ╲
    ╱  ▲▲  ╲
   ╱   ▲▲   ╲
  👊←fist
  (above navel,
   below ribs,
   thrust inward
   & upward)
```

**5. ALTERNATE**
```
Repeat cycle until:
├─ Object dislodged and breathing restored
├─ Victim becomes unconscious
└─ Emergency services arrive

Cycle:
5 back blows → 5 abdominal thrusts → 5 back blows → ...
```

**6. IF BECOMES UNCONSCIOUS**
- Lower to ground carefully
- Call 000 if not already called
- Begin CPR (see below)

---

## Treatment: Unconscious Adult/Child

### When to Use This

- Person was choking and lost consciousness
- Found unconscious and suspect choking

### Protocol

**1. CALL 000 IMMEDIATELY**
- Or have someone else call

**2. BEGIN CPR**

**Why CPR for choking?**
- Chest compressions may dislodge object
- Provides circulation even if partial airway
- Standard protocol for unconscious non-breathing person

**Modified CPR for choking:**

```
1. Position:
   ├─ Lay flat on back
   ├─ Hard, flat surface
   └─ Clear area around them

2. Open airway:
   ├─ Tilt head back, lift chin
   ├─ LOOK in mouth
   └─ If object visible and easy to remove → remove it
      (Don't do blind finger sweep - can push deeper)

3. Check breathing:
   ├─ Look for chest rise
   ├─ Listen for breath sounds
   └─ If not breathing normally → start CPR

4. CPR cycle (30:2):

   30 Chest compressions:
   ├─ Center of chest (between nipples)
   ├─ Hands stacked, arms straight
   ├─ Push hard (5-6cm depth)
   ├─ Push fast (100-120 per minute)
   └─ Let chest fully recoil

   Check mouth:
   ├─ After each set of compressions
   ├─ Look for dislodged object
   └─ Remove if visible and accessible

   2 Rescue breaths:
   ├─ Tilt head, lift chin
   ├─ Pinch nose
   ├─ Seal mouth over theirs
   ├─ Blow steadily for 1 second
   ├─ Watch for chest rise
   ├─ If chest doesn't rise → object still blocking
   └─ Continue CPR regardless

5. Continue until:
   ├─ Object dislodged and breathing resumes
   ├─ Emergency services arrive and take over
   └─ You're too exhausted to continue
```

**Key difference from standard CPR:**
- Check mouth after every 30 compressions
- Remove object if visible
- Compressions may dislodge object

---

## Treatment: Infant (< 1 year)

⚠️ **Different technique - DO NOT use abdominal thrusts on infants**

### Conscious Infant

**1. ASSESS**
- Cannot cough effectively
- Cannot cry or crying is weak/silent
- Difficulty breathing
- Blue/purple color

**2. CALL FOR HELP**

**3. BACK BLOWS (5 repetitions)**

```
Position:
├─ Sit or kneel
├─ Hold baby face down along forearm
├─ Head lower than body
├─ Support head/jaw with hand
└─ Rest forearm on your thigh

Technique:
├─ Use heel of hand
├─ Strike between shoulder blades
├─ Firm blows (less force than adult)
├─ Check mouth after each
└─ Stop if object out
```

**Visual:**
```
     ★ ← Back blows
      ↓
   ╭──○──╮  ← Infant (face down)
   │  ══  │
   ╰──────╯
   ▼▼▼▼▼▼▼▼  ← Forearm
   ▼▼▼▼▼▼▼▼
   ════════   ← Your thigh
```

**4. CHEST THRUSTS (5 repetitions)**

⚠️ **NOT abdominal thrusts - chest thrusts for infants**

```
Position:
├─ Turn baby face up
├─ Along other forearm
├─ Head lower than body
├─ Support head with hand
└─ Rest forearm on thigh

Technique:
├─ Two fingers on lower half of breastbone
├─ Just below nipple line
├─ Press down 4cm (one-third chest depth)
├─ Sharp thrusts, not slow pressure
├─ Check mouth after each
└─ Stop if object out
```

**Visual:**
```
        ╭──○──╮  ← Infant (face up)
        │  ││  │
        ╰──╮╰──╯
           ▼▼  ← Chest thrusts
          (two fingers,
           lower breastbone)
```

**5. ALTERNATE**
```
5 back blows → 5 chest thrusts → repeat
Continue until:
├─ Object dislodged
├─ Baby starts breathing/crying
└─ Baby becomes unconscious
```

### Unconscious Infant

**1. CALL 000**

**2. INFANT CPR**

```
1. Position:
   ├─ Flat on back
   ├─ Firm surface
   └─ Support head

2. Open airway:
   ├─ Gentle head tilt (not as far as adult)
   ├─ Lift chin
   └─ Check mouth (remove object if visible)

3. CPR cycle (30:2):

   30 Chest compressions:
   ├─ Two fingers on lower breastbone
   ├─ Press 4cm (one-third depth)
   ├─ 100-120 per minute
   └─ Check mouth after compressions

   2 Rescue breaths:
   ├─ Cover baby's mouth AND nose with your mouth
   ├─ Gentle puffs (like blowing out candle)
   ├─ Watch for chest rise
   └─ 1 second per breath

4. Continue until help arrives
```

---

## Self-Rescue (Choking Alone)

**If you're choking and alone:**

### Method 1: Self-Heimlich

```
1. Make fist above navel
2. Grasp with other hand
3. Thrust inward and upward forcefully
4. Repeat until object dislodged
```

### Method 2: Chair/Table Edge

```
1. Position abdomen over back of chair or table edge
2. Edge should be above navel, below ribs
3. Thrust yourself against edge
4. Repeated forceful thrusts
5. Object should dislodge
```

**Visual:**
```
    You
     │
     ▼
   ╭───╮
   │ X │ ←── Thrust yourself down
   ╰─┬─╯     onto edge
     │
   ══╬══  ←── Chair back / table edge
   ▲▲│▲▲      (hits below ribs,
   ▲▲│▲▲       above navel)
     │
   ┌─┴─┐
   │   │  ←── Chair
   └───┘
```

**Don't wait** - act immediately. Better to try and fail than hesitate.

---

## Special Situations

### Pregnant or Obese Person

**Problem:** Can't do abdominal thrusts effectively

**Solution:** Chest thrusts instead

```
Position:
├─ Stand behind
├─ Arms under armpits
├─ Hands on center of chest
└─ Base of breastbone

Technique:
├─ Fist on breastbone
├─ Grasp with other hand
├─ Pull straight back forcefully
├─ No upward angle
└─ Repeat 5 times

Alternate with back blows as usual
```

### Choking on Liquid

**Different scenario:**
- Often from inhaling liquid (aspiration)
- May cause coughing fit
- Usually can clear with coughing

**Response:**
- Encourage coughing
- Lean forward
- Don't do back blows/Heimlich unless severe obstruction
- Seek medical care if persistent coughing, difficulty breathing

### Dentures

**Risk:** Can dislodge and block airway

**If person wearing dentures chokes:**
- Treat as normal
- Don't worry about removing dentures first
- Check mouth after interventions (may see denture)

---

## After Successful Dislodgement

**Even if object cleared, seek medical care if:**

```
See doctor if:
├─ Abdominal thrusts were used (internal injury possible)
├─ Persistent coughing
├─ Difficulty swallowing
├─ Sensation of something still there
├─ Any breathing difficulty
├─ Infant or child (always check after choking incident)
└─ Elderly person

Possible complications:
├─ Rib fracture (from compressions/thrusts)
├─ Internal abdominal injury
├─ Part of object still in airway
├─ Aspiration (object went into lungs)
└─ Throat/esophagus damage
```

**What to tell doctor:**
- What was being eaten/swallowed
- How long choking lasted
- What interventions used
- Whether person lost consciousness
- Any ongoing symptoms

---

## Prevention

### General Strategies

**Eating habits:**
```
DO:
├─ Cut food into small pieces
├─ Chew thoroughly before swallowing
├─ Eat slowly, don't rush
├─ Sit upright while eating
├─ Don't talk with mouth full
├─ Avoid alcohol before eating (reduces coordination)
└─ Stay alert (don't eat while drowsy)

AVOID:
├─ Eating while walking, running, playing
├─ Lying down while eating
├─ Eating in moving vehicle (bumps cause swallowing reflex)
├─ Laughing with food in mouth
└─ Eating while distracted (TV, phone)
```

### High-Risk Foods

**Adults:**

```
Common choking hazards:
├─ Large pieces of meat
├─ Dry, crumbly foods (crackers, dry bread)
├─ Sticky foods (peanut butter by spoon)
├─ Bones in fish/chicken
├─ Hard lollies
├─ Marshmallows
└─ Foods eaten too fast
```

**Children (< 4 years):**

```
AVOID completely:
├─ Whole grapes (cut into quarters lengthwise)
├─ Cherry tomatoes (cut into quarters)
├─ Hard lollies, cough drops
├─ Popcorn
├─ Nuts and seeds
├─ Raw carrot rounds (grate or cook)
├─ Hot dogs/sausages (slice lengthwise, then small pieces)
├─ Large spoonfuls of peanut butter
├─ Chewing gum
├─ Marshmallows
└─ Chunks of cheese or apple
```

**Modification strategies:**
- Grate hard fruits/vegetables
- Cook until soft
- Cut grapes/tomatoes lengthwise into small pieces
- Spread nut butters thinly
- Supervise all eating

### Infants (< 1 year)

**Choking risks:**

```
Keep away:
├─ Small toys, toy parts (< 4cm diameter)
├─ Coins, buttons
├─ Batteries (especially button batteries)
├─ Small balls, marbles
├─ Balloons (major choking risk)
├─ Hard foods
└─ Anything that fits in toilet paper tube (choking hazard)
```

**Safe eating:**
- Breast milk or formula only until 6 months
- Introduce solids gradually
- Soft, mashable foods
- No honey until 12 months (botulism risk, not choking)
- Always supervise

### Elderly/High-Risk

**Increased risk due to:**
- Difficulty swallowing (dysphagia)
- Dentures (reduce sensation)
- Medications (dry mouth, drowsiness)
- Neurological conditions
- Dementia

**Precautions:**
- Softer diet
- Smaller portions
- Encourage thorough chewing
- Ensure dentures fit properly
- Sit upright for 30+ minutes after eating
- Supervision if needed
- Speech pathologist assessment if frequent coughing while eating

---

## Common Mistakes

**❌ Blind finger sweep:**
- Can push object deeper
- Only remove if clearly visible and reachable

**❌ Slapping back while upright:**
- Less effective than correct technique
- Need sharp blows, leaning forward

**❌ Abdominal thrusts on infant:**
- Can cause internal injury
- Use chest thrusts only

**❌ Giving drinks while choking:**
- Can make worse
- Only after airway clear

**❌ Waiting to see if they can clear it:**
- If severe obstruction (can't breathe/speak), act immediately
- Seconds matter

**❌ Hitting too gently:**
- Back blows need to be forceful
- Better too hard than too soft

**❌ Stopping too soon:**
- Continue until object out or person unconscious
- Don't give up

---

## Training & Practice

**Why training helps:**
- Builds muscle memory
- Reduces panic response
- Increases confidence
- Better outcomes

**Where to learn:**
```
Training options:
├─ St John Ambulance Australia (courses nationwide)
├─ Australian Red Cross (first aid courses)
├─ Local community centers
├─ Workplace first aid training
├─ Online refresher courses
└─ Parenting classes (infant choking)
```

**Skills to practice:**
- Recognizing severity
- Correct hand position
- Proper force/technique
- Infant vs child vs adult differences
- Self-rescue

**Recommended:** Take course every 3 years, practice technique regularly.

---

## Quick Reference Card

### Adult/Child Conscious
```
1. Ask "Are you choking?"
2. If can't speak/breathe → Call 000
3. 5 back blows (between shoulders, lean forward)
4. 5 abdominal thrusts (above navel, inward & up)
5. Repeat until object out or unconscious
```

### Adult/Child Unconscious
```
1. Call 000
2. CPR (30 compressions : 2 breaths)
3. Check mouth after each compression set
4. Remove object if visible
5. Continue until help arrives
```

### Infant Conscious
```
1. 5 back blows (face down on forearm, head low)
2. 5 chest thrusts (face up, two fingers on breastbone)
3. Repeat until object out or unconscious
NO abdominal thrusts on infants
```

### Infant Unconscious
```
1. Call 000
2. Infant CPR (30:2, two fingers, gentle breaths)
3. Check mouth after compressions
4. Continue until help arrives
```

### Self-Rescue
```
1. Self-Heimlich (fist above navel, thrust up)
2. OR bend over chair/table edge, thrust down
3. Repeat forcefully until object out
```

---

## Key Reminders

✓ **Speed matters** - brain damage begins at 4-6 minutes
✓ **Force matters** - back blows and thrusts need to be HARD
✓ **Can't speak = severe** - act immediately
✓ **Different for infants** - chest thrusts, not abdominal
✓ **Check mouth** - after each intervention, remove if visible
✓ **Don't give up** - continue until object out or unconscious
✓ **Seek medical care** - even after successful dislodgement
✓ **Prevention** - cut food small, chew thoroughly, supervise children

---

## Related Guides

- **CPR:** `GUIDE START basic-cpr`
- **Shock Treatment:** `GUIDE START shock-treatment`
- **Child Safety:** `GUIDE START child-safety-basics`

---

**Key Principle:** Don't hesitate. Severe choking is a life-threatening emergency. Act immediately and forcefully. You can't make it worse - they can't breathe.

**Emergency Number:** 000 (Australia)
**First Aid Training:** St John Ambulance Australia, Australian Red Cross
