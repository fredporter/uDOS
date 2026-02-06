---
uid: udos-guide-medical-20251204171300-UTC-L300AB99
title: Fractures, Sprains & Strains
tags: [guide, knowledge, medical]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Fractures, Sprains & Strains

**Category:** Medical - Essential Knowledge
**Priority:** HIGH - Common injuries, proper treatment prevents complications
**Season:** Year-round risk
**Difficulty:** Moderate - requires assessment skills

---

## Overview

Three common musculoskeletal injuries that are often confused:

```
╔════════════════════════════════════════════════════╗
║ FRACTURE = Broken bone                            ║
║ SPRAIN   = Damaged/torn ligament (bone to bone)   ║
║ STRAIN   = Damaged/torn muscle or tendon          ║
╚════════════════════════════════════════════════════╝
```

**Key difference:** All cause pain and swelling, but fractures may require immobilization and always need medical assessment.

---

## Quick Assessment

### Is It Broken? (Fracture Indicators)

**High probability of fracture if:**
- ⚠️ Obvious deformity (bone out of place)
- ⚠️ Bone visible through skin (compound fracture - EMERGENCY)
- ⚠️ Heard/felt a "snap" or "crack" at time of injury
- ⚠️ Unable to bear weight or use the limb at all
- ⚠️ Severe pain localized to one spot
- ⚠️ Swelling immediate and severe
- ⚠️ Numbness or tingling below injury
- ⚠️ Limb looks wrong (angle, rotation, length)

**Possible fracture if:**
- Deep, persistent pain at injury site
- Swelling and bruising significant
- Limited range of motion
- Point tenderness (hurts when you press exact spot)
- Pain increases with movement or weight

**Probably soft tissue (sprain/strain) if:**
- Pain more diffuse (spread out)
- Can somewhat use the limb
- Swelling develops gradually
- No deformity
- Pain improves with RICE treatment

**When in doubt:** Treat as fracture and seek medical assessment.

### Fracture vs Sprain Assessment Flow

```flow
st=>start: Limb injury occurred
deform=>condition: Visible deformity?
snap=>condition: Heard snap/crack?
weight=>condition: Can bear weight?
point=>condition: Point tenderness?
swelling=>condition: Immediate severe swelling?
fracture=>operation: Treat as FRACTURE
sprain=>operation: Likely sprain/strain
rice=>operation: Apply RICE treatment
splint=>operation: Splint and immobilize
emerg=>condition: Compound or severe?
call=>operation: Call 911
medical=>end: Seek medical care
home=>end: Home treatment

st->deform
deform(yes)->fracture->emerg
deform(no)->snap
snap(yes)->fracture->emerg
snap(no)->weight
weight(no)->point
weight(yes)->sprain->rice->home
point(yes)->swelling
point(no)->sprain->rice->home
swelling(yes)->fracture->emerg
swelling(no)->sprain->rice->home
emerg(yes)->call->medical
emerg(no)->splint->medical
```

### Splinting Sequence

```sequence
Rescuer->Injury: Assess fracture location
Injury->Rescuer: Identify break site
Rescuer->Pad: Pad splint materials
Pad->Position: Position splint materials
Position->Immobilize: Immobilize joint above and below
Immobilize->Secure: Secure with bandages
Secure->Check: Check circulation below injury
Check->Pulse: Verify pulse present
Pulse->Color: Check skin color/warmth
Color->Elevate: Elevate if possible
Elevate->Ice: Apply ice pack
Ice->Monitor: Monitor for changes
Monitor->Transport: Transport to hospital
```

---

## Fractures

### Types

**Closed fracture:**
- Bone broken but skin intact
- Serious but lower infection risk

**Compound/Open fracture:**
- Bone breaks through skin
- ⚠️ **MEDICAL EMERGENCY - CALL 000**
- High infection risk

**Greenstick:**
- Partial break (bone bends and cracks)
- Common in children

**Stress fracture:**
- Tiny crack from repeated stress
- Often not obvious initially

### Immediate Treatment

**DO:**

1. **Call 000 if:**
   - Compound fracture (bone through skin)
   - Suspected spine, neck, or skull fracture
   - Unconscious or severe pain
   - Numbness/tingling below injury
   - No pulse below injury
   - Severe bleeding

2. **Immobilize the injury:**
   ```
   Keep it still:
   ├─ Don't try to straighten it
   ├─ Splint in position found
   ├─ Immobilize joint above and below fracture
   └─ Pad splint (prevent pressure sores)
   ```

3. **Control bleeding** (if compound):
   - Clean cloth/dressing over wound
   - Apply gentle pressure around (not on) bone
   - Don't push bone back in

4. **Apply ice:**
   - 20 minutes on, 20 minutes off
   - Wrap ice in cloth (not directly on skin)
   - Reduces swelling and pain

5. **Elevate** (if possible):
   - Above heart level
   - Only if it doesn't cause more pain

6. **Monitor circulation:**
   - Check pulse below injury
   - Check color (should be pink, not blue/white)
   - Check sensation (can they feel touch?)
   - Check movement (can they wiggle fingers/toes?)
   - Recheck every 15-30 minutes

**DON'T:**
- ✗ Try to straighten or realign bone
- ✗ Push bone back through skin
- ✗ Move the person unnecessarily
- ✗ Give food or drink (may need surgery)
- ✗ Apply ice directly to skin
- ✗ Splint too tightly (cuts circulation)

### Splinting

**Purpose:** Keep broken bone from moving, prevent further damage.

**Principles:**
- Immobilize joint above and below fracture
- Pad well (clothing, towels, leaves)
- Splint in position found (don't straighten)
- Check circulation after splinting

**Improvised splint materials:**

```
Rigid supports:
├─ Sticks, branches
├─ Rolled newspaper/magazines
├─ Tent poles, ski poles
├─ Board, plank
├─ Rolled blanket (for arm)
└─ Neighbouring finger/toe (buddy tape)

Padding:
├─ Clothing, towels
├─ Grass, leaves, moss
├─ Soft fabric
└─ Bubble wrap, foam

Ties:
├─ Bandages, strips of cloth
├─ Belt, rope, string
├─ Tape
├─ Shoelaces
└─ Vines (in emergency)
```

**Splinting guide by location:**

**Arm/wrist:**
1. Place padded splint under forearm
2. Extend from elbow to past fingertips
3. Tie at wrist and mid-forearm (not over break)
4. Make sling to support arm across chest
5. Check fingers for color, warmth, sensation

**Leg/ankle:**
1. Place padded splints on both sides of leg
2. Extend from above knee to past foot
3. Tie above and below injury (at thigh, calf, ankle)
4. Don't remove boot if ankle injury (acts as splint)
5. Check toes for circulation

**Finger:**
1. Buddy tape to neighbouring finger
2. Place small padding between fingers
3. Tape at two points (above and below break)
4. Leave fingertips visible (check circulation)

**Collarbone:**
1. Make sling for arm on injured side
2. Bind arm to chest (gentle)
3. Sitting/standing position (more comfortable)

**Ribs:**
- DON'T bind/tape (restricts breathing)
- Support with pillow when sitting
- Breathe deeply regularly (prevent pneumonia)
- Seek medical care

### Suspected Spine/Neck Fracture

⚠️ **DO NOT MOVE - CALL 000 IMMEDIATELY**

**Suspect if:**
- Fall from height
- Vehicle accident
- Diving accident
- Severe head injury
- Neck or back pain
- Numbness/tingling in limbs
- Paralysis or weakness
- Loss of bladder/bowel control

**What to do:**
- Keep person still (talk to them, don't let them move)
- Stabilize head and neck (hands on both sides)
- Don't remove helmet if wearing one
- Keep airway open (jaw thrust, not head tilt)
- Wait for ambulance

---

## Sprains

### Definition

Ligament damage (ligaments connect bone to bone).

**Severity grades:**

```
╔═══════════╦════════════════════════════════════╗
║ Grade 1   ║ Mild - Stretched ligament          ║
║ (Mild)    ║ Minimal swelling, can walk/use     ║
║           ║ Recovery: 1-2 weeks                ║
╠═══════════╬════════════════════════════════════╣
║ Grade 2   ║ Moderate - Partial tear            ║
║ (Moderate)║ Swelling, bruising, limited use    ║
║           ║ Recovery: 3-6 weeks                ║
╠═══════════╬════════════════════════════════════╣
║ Grade 3   ║ Severe - Complete tear             ║
║ (Severe)  ║ Major swelling, can't use, unstable║
║           ║ Recovery: Months, may need surgery ║
╚═══════════╩════════════════════════════════════╝
```

### Common Locations

**Ankle** (most common):
- Rolling ankle on uneven ground
- Landing wrong from jump
- Pain on outer ankle usually

**Knee:**
- Twisting motion
- Sudden stop or direction change
- Can be serious (ACL, MCL tears)

**Wrist:**
- Falling on outstretched hand
- Impact sports

**Thumb:**
- Falling with thumb extended
- "Skier's thumb"

### RICE Treatment

**Primary treatment for first 48-72 hours:**

```
R = REST
├─ Don't use injured area
├─ Use crutches if ankle/knee (don't bear weight)
├─ Avoid activities that cause pain
└─ Allow healing

I = ICE
├─ Apply ice pack 20 minutes every 2-3 hours
├─ Wrap ice in cloth (not directly on skin)
├─ Reduces swelling and pain
└─ Continue for 48-72 hours

C = COMPRESSION
├─ Wrap with elastic bandage
├─ Snug but not too tight
├─ Check circulation (toes/fingers pink and warm)
├─ Loosen if numbness, tingling, or blue/white color
└─ Reduces swelling

E = ELEVATION
├─ Raise above heart level
├─ Use pillows to prop up
├─ Especially when resting/sleeping
└─ Gravity helps reduce swelling
```

**When to add heat:** After 48-72 hours, alternate ice and heat to promote healing.

### Recovery Timeline

**First 48 hours:**
- RICE protocol strictly
- Pain and swelling worst
- No weight bearing if ankle/knee
- Anti-inflammatory medication if available

**Days 3-7:**
- Swelling should decrease
- Gentle movement (without pain)
- Continue elevation when resting
- May start gentle stretching

**Week 2+:**
- Gradual return to activity
- Strengthening exercises
- May still have some swelling
- Don't rush it (re-injury risk)

### When to Seek Medical Care

**See doctor if:**
- Severe pain (can't bear weight at all)
- Swelling doesn't improve after 2-3 days
- Bruising very extensive
- Joint feels unstable
- Numbness or tingling
- Hearing/feeling a "pop" at time of injury
- No improvement after 1 week of RICE
- Joint gives out repeatedly

---

## Strains

### Definition

Muscle or tendon damage (tendons connect muscle to bone).

**Common causes:**
- Overuse (repetitive motion)
- Sudden exertion
- Poor lifting technique
- Not warming up before activity
- Fatigue

**Common locations:**
- Lower back (lifting)
- Hamstring (running)
- Calf (sudden push-off)
- Shoulder (overhead activity)

### Severity

```
╔═══════════╦════════════════════════════════════╗
║ Grade 1   ║ Mild - Few fibers torn             ║
║           ║ Some pain, minimal loss of function║
║           ║ Recovery: Few days to 1 week       ║
╠═══════════╬════════════════════════════════════╣
║ Grade 2   ║ Moderate - More fibers torn        ║
║           ║ Pain, swelling, reduced strength   ║
║           ║ Recovery: 2-4 weeks                ║
╠═══════════╬════════════════════════════════════╣
║ Grade 3   ║ Severe - Muscle completely torn    ║
║           ║ Severe pain, can't use muscle      ║
║           ║ Recovery: Months, may need surgery ║
╚═══════════╩════════════════════════════════════╝
```

### Treatment

**Acute phase (first 2-3 days):**
- RICE protocol (same as sprains)
- Avoid stretching initially
- Gentle compression (not too tight)

**Recovery phase (after 3 days):**
- Gentle stretching (no pain)
- Gradual strengthening
- Heat therapy (promotes blood flow)
- Massage (gentle, after initial swelling down)

**Return to activity:**
- Gradual increase
- Warm up properly
- Stop if pain returns
- Strengthen surrounding muscles

---

## Special Situations

### Bush/Remote Location

**Limited resources treatment:**

1. **Assessment crucial:**
   - Is it fracture? → Splint and evacuate
   - Is it severe sprain/strain? → RICE and monitor
   - Can person walk/self-rescue? → Plan accordingly

2. **Improvised splints:**
   - Use what's available (sticks, clothing, backpack straps)
   - Padding is critical (prevent pressure sores)
   - Check circulation frequently

3. **Evacuation decision:**
   ```
   Evacuate immediately if:
   ├─ Suspected fracture (especially femur, spine, pelvis)
   ├─ Compound fracture (infection risk)
   ├─ No pulse below injury
   ├─ Severe pain not controlled
   ├─ Unable to self-rescue
   └─ Getting worse despite treatment

   Monitor and decide if:
   ├─ Moderate sprain/strain
   ├─ Person can walk with support
   ├─ Swelling controlled with RICE
   └─ No concerning signs (numbness, color change)
   ```

4. **Pain management:**
   - Ice from stream (wrap in cloth)
   - Elevation (use backpack, logs)
   - Immobilization (reduces pain)
   - Distraction, reassurance

### Elderly Patients

**Higher risk:**
- Bones more fragile (osteoporosis)
- Healing slower
- Balance issues (fall risk)
- Medications (blood thinners complicate)

**Special considerations:**
- Lower threshold for medical care
- Even minor falls may cause fracture
- Hip fractures serious (require surgery)
- Wrist fractures common (catching self when falling)

### Children

**Differences:**
- Bones still growing (growth plate injuries)
- Heal faster than adults
- May not communicate pain well
- "Greenstick" fractures (partial break)

**Assessment:**
- Watch behavior (refusing to use limb)
- Compare to other side
- Any deformity → medical care
- Growth plate injuries need specialist

---

## Prevention

### General Strategies

**Strengthen muscles:**
- Strong muscles protect bones and joints
- Focus on core, legs for balance
- Regular resistance training

**Improve flexibility:**
- Stretch regularly
- Warm up before activity
- Cool down after
- Yoga, tai chi beneficial

**Good technique:**
- Proper lifting (bend knees, not back)
- Appropriate footwear
- Learn correct form for sports/activities

**Environmental awareness:**
- Watch for uneven ground
- Use handrails
- Good lighting
- Clear walkways of hazards

**Gradual progression:**
- Don't increase activity too quickly
- "10% rule" - increase distance/intensity by max 10% per week
- Rest days important

**Nutrition:**
- Adequate calcium (1000-1300mg daily)
- Vitamin D (sunlight, supplements if needed)
- Protein for muscle strength
- Hydration

### High-Risk Activities

**Hiking/bushwalking:**
- Proper boots (ankle support)
- Trekking poles (balance, reduce knee stress)
- Watch footing on descents
- Know your limits

**Sports:**
- Warm up properly
- Use protective equipment
- Know the rules
- Don't play through pain

**Home:**
- Non-slip mats in bathroom
- Good lighting on stairs
- Secure rugs
- Declutter walkways

**Work:**
- Proper lifting technique
- Mechanical aids when available
- Ergonomic setup
- Regular breaks

---

## Pain Management

**First 48 hours:**
- Ice (20 min every 2-3 hours)
- Elevation
- Immobilization
- Over-the-counter pain relief if available:
  * Paracetamol (1000mg every 6 hours, max 4000mg/day)
  * Ibuprofen (400mg every 6-8 hours with food)

**Ongoing:**
- Alternate ice/heat after 48 hours
- Gentle movement (prevents stiffness)
- Compression
- Distraction techniques

**Red flags (seek medical care):**
- Pain getting worse, not better
- Severe pain not controlled by medication
- Pain with numbness/tingling
- Pain preventing sleep despite medication

---

## Long-Term Complications

**If not treated properly:**

**Fractures:**
- Malunion (heals in wrong position)
- Nonunion (doesn't heal)
- Infection (compound fractures)
- Arthritis in joint
- Chronic pain
- Reduced function

**Sprains:**
- Chronic instability
- Repeated sprains
- Chronic pain
- Arthritis
- Compensatory injuries (favoring other side)

**Strains:**
- Chronic tightness
- Weakness
- Re-injury
- Compensatory strain elsewhere

**Prevention of complications:**
- Proper initial treatment
- Complete rehabilitation
- Gradual return to activity
- Address underlying issues (weakness, technique)

---

## Rehabilitation Exercises

### Ankle Sprain (after initial healing)

**Week 2-3:**
1. Alphabet: Write alphabet with toes (range of motion)
2. Towel slides: Pull towel toward you with toes
3. Balance: Stand on injured foot 30 seconds (hold wall if needed)

**Week 4+:**
1. Resistance: Use resistance band for all directions
2. Heel raises: Up on toes, slowly lower
3. Balance board: Progress to unstable surface

### Knee Sprain

**Initial:**
1. Quad sets: Tighten thigh muscle, hold 5 seconds
2. Straight leg raises: Lift leg 15cm, hold 5 seconds
3. Heel slides: Bend and straighten knee gently

**Later:**
1. Wall sits: Back against wall, bend knees 45°, hold 30 seconds
2. Step ups: Small step (10-15cm), up and down slowly
3. Balance exercises

### Wrist Sprain

**Early:**
1. Finger movements: Make fist, spread fingers
2. Wrist circles: Gentle rotation both directions
3. Flexion/extension: Bend wrist up and down gently

**Later:**
1. Resistance: Use resistance band or light weight
2. Grip strength: Squeeze ball or towel
3. Weight bearing: Gentle pressure on hands

**Principle:** Start gentle, progress gradually, stop if sharp pain.

---

## Summary Checklist

### Assessment
- [ ] Determine type (fracture vs sprain vs strain)
- [ ] Check for emergency signs (compound fracture, no pulse, spine injury)
- [ ] Assess ability to use limb

### Immediate Treatment
- [ ] Call 000 if emergency signs
- [ ] RICE protocol for sprains/strains
- [ ] Immobilize fractures
- [ ] Monitor circulation

### Ongoing Care
- [ ] Continue RICE for 48-72 hours
- [ ] Gradual return to movement
- [ ] Rehabilitation exercises
- [ ] Seek medical care if not improving

### Prevention
- [ ] Warm up before activity
- [ ] Proper technique
- [ ] Strengthen supporting muscles
- [ ] Environmental awareness

---

## Related Guides

- **Wound Care:** `GUIDE START wound-care-bleeding`
- **Shock Treatment:** `GUIDE START shock-treatment`
- **Pain Management:** `GUIDE START pain-management`
- **CPR:** `GUIDE START basic-cpr`

---

**Key Principle:** When in doubt, immobilize and seek medical assessment. Proper initial treatment prevents long-term complications.

**Emergency Number:** 000 (Australia)
