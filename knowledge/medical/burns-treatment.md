---
tier: 3
category: medical
title: "Burns Treatment & Prevention"
complexity: advanced
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Burns Treatment & Prevention

**Category:** Medical - Essential Knowledge
**Priority:** HIGH - Common injury, proper treatment critical
**Season:** Year-round risk, elevated during bushfire season
**Difficulty:** Moderate - severity assessment important

---

## Overview

Burns damage skin and sometimes deeper tissue. Severity depends on depth and area affected.

**Three factors determine treatment:**
1. **Depth** (degree of burn)
2. **Size** (percentage of body affected)
3. **Location** (face, hands, joints most serious)

### Burn Treatment Decision Flow

```flow
st=>start: Burn injury occurs
source=>operation: Remove from heat source
assess=>condition: Degree of burn?
first=>operation: Cool water 10-20 min
second=>condition: Size > palm?
third=>operation: Call 911 immediately
cover=>operation: Cover with clean cloth
pain=>operation: Pain management
medical=>condition: Seek medical care?
hosp=>end: Hospital treatment
home=>end: Home care

st->source->assess
assess(1st degree)->first->cover->pain->home
assess(2nd degree)->first->second
second(yes)->cover->medical
second(no)->cover->pain->home
assess(3rd degree)->third->hosp
medical(yes)->hosp
medical(no)->home
```

### Burn Treatment Sequence

```sequence
Victim->Rescuer: Burn injury sustained
Rescuer->Source: Remove from heat
Source->Rescuer: Stop burning process
Rescuer->Victim: Remove jewelry/clothing
Victim->Cool: Apply cool running water
Cool->Victim: Cool for 10-20 minutes
Victim->Assess: Evaluate burn severity
Assess->Rescuer: Determine degree
Rescuer->Victim: Cover with clean cloth
Victim->Rescuer: Do not apply ice
Rescuer->Pain: Give pain relief if available
Pain->Victim: Monitor for shock
Victim->Rescuer: Keep warm (not burned area)
Rescuer->Medical: Seek care if severe
```

---

## Burn Severity

### By Depth

```
╔═══════════════════════════════════════════════════════════╗
║ FIRST DEGREE (Superficial)                               ║
╟───────────────────────────────────────────────────────────╢
║ Affects: Outer skin layer only (epidermis)               ║
║ Looks: Red, no blisters, dry                             ║
║ Feels: Painful, sensitive to touch                       ║
║ Examples: Mild sunburn, brief contact with heat          ║
║ Heals: 3-7 days, no scarring                             ║
║ Treatment: Home care usually sufficient                  ║
╚═══════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════╗
║ SECOND DEGREE (Partial Thickness)                        ║
╟───────────────────────────────────────────────────────────╢
║ Affects: Outer and second layer (epidermis + dermis)     ║
║ Looks: Red, blistered, wet/shiny, may be mottled         ║
║ Feels: Very painful, sensitive to air/pressure           ║
║ Examples: Severe sunburn, hot liquid, brief flame        ║
║ Heals: 2-3 weeks for shallow, 3-8 weeks for deep         ║
║ Treatment: Medical care if large or deep                 ║
║ Scarring: Possible, especially if deep                   ║
╚═══════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════╗
║ THIRD DEGREE (Full Thickness)                            ║
╟───────────────────────────────────────────────────────────╢
║ Affects: All skin layers, may reach muscle/bone          ║
║ Looks: White, brown, black, charred, leathery            ║
║ Feels: Little to no pain (nerves destroyed)              ║
║ Examples: Prolonged flame, chemical, electrical          ║
║ Heals: Doesn't heal on own, needs skin graft             ║
║ Treatment: EMERGENCY - CALL 000                          ║
║ Scarring: Severe, permanent                              ║
╚═══════════════════════════════════════════════════════════╝
```

**Key indicator:** If you're not sure between 2nd and 3rd degree, treat as 3rd degree and seek medical care.

### By Size

**Rule of Nines (adults):**

```
Body part               Percentage
──────────────────────────────────
Head & neck                   9%
Each arm                      9% (18% total)
Chest                         9%
Abdomen                       9%
Upper back                    9%
Lower back                    9%
Each leg (front)              9% (36% total)
Each leg (back)               9%
Groin                         1%
──────────────────────────────────
TOTAL                       100%
```

**Hand method (for scattered burns):**
- Victim's palm (including fingers) = approximately 1% of their body surface

**Seek immediate medical care if burn covers:**
- > 10% in adults
- > 5% in children or elderly
- Any significant area on face, hands, feet, genitals, major joints

---

## Immediate Treatment

### First Aid Protocol

**For ALL burns:**

```
STOP - DROP - ROLL (if clothing on fire)
↓
REMOVE from heat source
↓
COOL with running water (20 minutes)
↓
REMOVE jewelry, tight clothing (before swelling)
↓
COVER with clean, dry, non-stick dressing
↓
ASSESS severity
↓
SEEK MEDICAL CARE if needed
```

### Detailed Steps

**1. COOL THE BURN**

```
DO:
├─ Cool running water for 20 minutes
├─ Lukewarm/cool (not ice cold)
├─ Start ASAP (within 3 minutes ideal)
├─ Can cool for up to 3 hours after burn
├─ For chemical burns: flush for 20+ minutes
└─ Remove clothing while cooling (if not stuck)

DON'T:
├─ ✗ Use ice or ice water (damages tissue further)
├─ ✗ Apply butter, oil, grease, toothpaste
├─ ✗ Break blisters
├─ ✗ Touch burn with dirty hands
└─ ✗ Use adhesive bandages directly on burn
```

**Why 20 minutes?** Burns continue damaging tissue after heat source removed. Cooling stops this process.

**2. REMOVE CONSTRICTING ITEMS**

- Rings, bracelets, watches
- Tight clothing (unless stuck to skin)
- Boots, shoes if feet burned
- Do this WHILE cooling (swelling happens fast)

**If clothing stuck:** Leave it. Cut around it if needed. Don't pull.

**3. COVER THE BURN**

```
Best coverage:
├─ Clean, dry, non-stick dressing
├─ Plastic wrap/cling film (clean piece)
├─ Clean cloth (loosely applied)
└─ Sterile gauze (if available)

Avoid:
├─ ✗ Fluffy materials (cotton wool - fibers stick)
├─ ✗ Adhesive directly on burn
├─ ✗ Tight wrapping
└─ ✗ Anything dirty or used
```

**Purpose:** Protects from infection, reduces pain (keeps air off), prevents fluid loss.

**4. MANAGE PAIN**

- Cooling helps most
- Elevation (if arm/leg)
- Paracetamol or ibuprofen (if available)
- Keep covered (air on burn hurts)

**5. MONITOR FOR SHOCK**

Burns can cause shock, especially large burns:
- Pale, clammy skin
- Rapid pulse
- Rapid breathing
- Confusion
- Weakness

**Treatment:** Lay down, elevate legs (unless burns on legs), keep warm (but not burned area), reassure.

---

## When to Call 000

**EMERGENCY - Call immediately if:**

- ⚠️ Third degree burn (any size)
- ⚠️ Burns to face, hands, feet, genitals, major joints
- ⚠️ Burns covering > 10% body area (> palm size on child)
- ⚠️ Chemical or electrical burn
- ⚠️ Burn from explosion
- ⚠️ Inhalation injury (smoke, hot air)
- ⚠️ Victim is child, elderly, pregnant, or has medical conditions
- ⚠️ Signs of shock
- ⚠️ Unconscious

**See doctor within 24 hours if:**
- Second degree burn larger than palm
- Burn on face (even if small)
- Unsure of severity
- Not up to date on tetanus vaccine
- Signs of infection developing

---

## Specific Burn Types

### Sunburn

**Prevention (Australian sun is intense):**
```
Sun safety:
├─ Slip on shirt (long sleeves best)
├─ Slop on SPF 50+ sunscreen
│   ├─ Apply 20 minutes before sun
│   ├─ Reapply every 2 hours
│   └─ After swimming/sweating
├─ Slap on wide-brim hat (10cm+ brim)
├─ Seek shade (especially 10:00-15:00)
└─ Slide on sunglasses (UV protection)
```

**Treatment:**
1. Get out of sun immediately
2. Cool bath or damp cloths
3. Moisturizer (aloe vera, sorbolene)
4. Hydrate well (drink extra water)
5. Paracetamol/ibuprofen for pain
6. Loose clothing
7. No further sun exposure until healed

**Seek medical care if:**
- Extensive blistering
- Fever, chills
- Dizziness, nausea
- Covers large area
- Extreme pain

### Chemical Burns

**Common sources:**
- Cleaning products
- Pool chemicals
- Car battery acid
- Fertilizers
- Industrial chemicals

**Treatment:**
```
1. REMOVE source
   ├─ Brush off dry chemical first (don't wet it initially)
   ├─ Remove contaminated clothing
   └─ Protect yourself (don't touch chemical)

2. FLUSH with water
   ├─ Running water for 20+ minutes
   ├─ Longer if chemical not identified
   ├─ Remove contact lenses if eyes affected
   └─ Continue flushing until ambulance arrives

3. CALL 000
   ├─ All chemical burns need medical assessment
   ├─ Identify chemical if possible
   └─ Bring container/label if safe

4. DON'T neutralize
   ├─ ✗ Don't add acid to base or vice versa
   └─ Creates heat reaction (worse burn)
```

**Eyes:** Flush for minimum 20 minutes. Hold eyelid open. Tilt head so water runs away from unaffected eye.

### Electrical Burns

⚠️ **ALWAYS CALL 000 FOR ELECTRICAL BURNS**

**Why serious:**
- Surface burn may look small
- Internal damage can be extensive
- Can affect heart rhythm
- May have entry and exit wounds

**Immediate:**
1. Make sure power is OFF
2. Don't touch victim if still in contact with power
3. Call 000
4. Check breathing (be ready for CPR)
5. Cool burns as usual
6. Monitor heart rate/breathing continuously

**Don't underestimate:** Small visible burn can hide serious internal injury.

### Fire/Flame Burns

**Immediate:**
1. STOP - DROP - ROLL (if clothes on fire)
2. Smother flames (blanket, jacket)
3. Remove from fire area
4. Cool as usual
5. Assess airway (smoke inhalation?)

**Check for inhalation injury:**
- Singed nose hairs, eyebrows
- Soot around nose/mouth
- Coughing, wheezing
- Hoarse voice
- Difficulty breathing

**If inhalation suspected:** CALL 000 - can cause airway swelling hours later.

### Hot Liquid (Scalds)

**Common in kitchens:**
- Boiling water
- Hot oil/fat
- Hot drinks
- Steam

**Treatment:**
1. Remove from source
2. Remove clothing immediately (continues burning if soaked)
3. Cool for 20 minutes
4. Cover

**Prevention:**
- Handles inward on stove
- No children in kitchen when cooking
- Test bath water before entering
- Secure hot drinks away from edge

---

## Burn Care (After Initial Treatment)

### First 24-48 Hours

**Keep clean:**
- Wash hands before touching
- Change dressing daily
- Clean with mild soap and water
- Pat dry gently

**Pain management:**
- Paracetamol/ibuprofen
- Keep covered (reduces pain)
- Elevate if possible
- Cool compresses (clean cloth)

**Monitor for infection:**

```
Warning signs:
├─ Increased pain after first few days
├─ Increased redness, swelling
├─ Red streaks from burn
├─ Pus or cloudy fluid
├─ Fever
├─ Foul smell
└─ Burn feels hot

→ See doctor if any infection signs
```

### Blister Care

**DON'T pop blisters:**
- Natural protection from infection
- Clean, sterile fluid inside
- Speeds healing
- Reduces pain

**If blister breaks:**
1. Wash gently with soap and water
2. Apply antibiotic ointment (if available)
3. Cover with non-stick dressing
4. Change dressing daily
5. Watch for infection

**Large blisters:** See doctor (may need to drain safely).

### Healing Phase

**First degree burns (3-7 days):**
- May peel (like sunburn)
- Moisturize regularly
- Protect from sun
- Should heal completely

**Second degree burns (2-8 weeks):**
- Keep moist (aids healing)
- Don't pick at peeling skin
- Gentle movement (prevents stiffness)
- Protect new skin (very sensitive)
- May scar

**Third degree burns:**
- Requires medical management
- Skin grafts likely
- Physical therapy may be needed
- Significant scarring

---

## Scar Management

**Minimize scarring:**

**During healing:**
- Keep moist (prevents cracking)
- Protect from sun (new skin darkens easily)
- Gentle massage (once healed)
- Pressure garments (if recommended)

**After healed:**
- Massage scar tissue daily
- Silicone sheets (if recommended)
- Sun protection (SPF 50+)
- Vitamin E oil (some evidence it helps)

**Severe scars:**
- See doctor about options
- May include laser treatment, surgery
- Physical therapy if limits movement

---

## Special Situations

### Bushfire Burns

**Immediate priorities:**
1. Get to safety (burnt-over area)
2. Assess breathing (smoke inhalation common)
3. Cool burns (any clean water)
4. Cover to prevent heat loss (burns lose heat fast)
5. Call 000 or get to hospital

**Radiant heat burns:**
- Can burn through clothing
- Often extensive area
- Face, hands, arms common
- Serious even if look superficial

**Ember burns:**
- Multiple small burns
- Can smolder in clothing
- Check whole body
- Remove all clothing to check

### Burns in Remote Areas

**Challenges:**
- Limited clean water
- No medical supplies
- Evacuation difficult
- Infection risk high

**Priorities:**
```
1. Cool as best you can
   ├─ Stream water (if reasonably clean)
   ├─ Wet cloth (change frequently)
   └─ Continue for 20 minutes minimum

2. Cover to protect
   ├─ Cleanest cloth available
   ├─ Plastic bag (if clean)
   ├─ Leaves (last resort, if large leaf, clean)
   └─ Keep it on (protects from dirt/insects)

3. Pain management
   ├─ Keep covered
   ├─ Elevate
   ├─ Distraction
   └─ Any medication available

4. Evacuate if:
   ├─ Second degree > palm size
   ├─ Any third degree
   ├─ Face/hands/joints involved
   ├─ Multiple scattered burns
   └─ Limited ability to care for it
```

### Children

**Higher risk:**
- Thinner skin (burns deeper)
- Larger surface area to weight (more serious)
- Curious (pull hot things down)
- Can't escape quickly

**Treatment differences:**
- Lower threshold for medical care
- Smaller burns still serious
- More prone to shock
- Dehydration risk (burns lose fluid)

**Prevention critical:**
- Supervision in kitchen
- Kettles/cords out of reach
- Check bath water
- Hot drinks out of reach
- Stove guards

### Elderly

**Higher risk:**
- Thinner skin
- Slower healing
- Reduced sensation (don't notice heat)
- Mobility issues (can't escape)

**Complications more common:**
- Infection
- Slow healing
- Long-term disability

**Prevention:**
- Check water heaters (< 50°C)
- Electric blanket safety
- Supervision if memory issues

---

## Prevention Strategies

### Home

**Kitchen:**
- Handles inward
- Don't leave cooking unattended
- Keep children out
- Oven mitts handy
- Fire extinguisher accessible

**Bathroom:**
- Test water before entering
- Hot water system < 50°C
- Non-slip mats
- Supervise children

**General:**
- Working smoke alarms
- Fire escape plan
- Fire extinguisher/blanket
- Check electrical cords
- Safe heater use

### Bushfire Preparation

**Before fire season:**
- Clear fuel around house
- Know evacuation routes
- Emergency kit ready
- Fire plan practiced

**During bushfire:**
- Appropriate clothing (wool, cotton, cover all skin)
- Stay inside if defendable
- Wet down area around house
- Fill baths/containers with water

**After fire:**
- Wait for all-clear
- Check for embers
- Beware hot surfaces
- Hydrate well

### Outdoor Activities

**Camping:**
- Fire safety (contained, attended, extinguished)
- Keep water nearby
- First aid kit with burn supplies
- Know evacuation routes

**Bushwalking:**
- Sun protection
- Portable stove safety
- Emergency plan

### Work

**High-risk jobs:**
- Follow safety procedures
- Use protective equipment
- Fire extinguisher training
- First aid trained personnel
- Emergency plan

---

## First Aid Kit for Burns

**Essential items:**

```
Burn-specific:
├─ Sterile gauze pads (various sizes)
├─ Non-stick dressings
├─ Plastic wrap/cling film
├─ Burn gel/cream (if available)
├─ Adhesive tape
└─ Scissors (to cut clothing)

General:
├─ Clean water (bottled)
├─ Mild soap
├─ Paracetamol/ibuprofen
├─ Antibiotic ointment
├─ Thermometer
└─ Emergency numbers list
```

**Don't include:**
- Ice packs (can cause cold injury)
- Butter, oils, creams (make worse)
- Cotton wool (fibers stick)

---

## Myths vs Facts

**MYTH:** "Use butter/oil on burns"
**FACT:** Traps heat, increases damage, infection risk. Use cool water only.

**MYTH:** "Pop blisters to let them heal"
**FACT:** Blisters protect from infection. Leave intact unless very large.

**MYTH:** "Ice is best for cooling"
**FACT:** Ice causes further damage. Use cool running water.

**MYTH:** "Toothpaste helps burns"
**FACT:** Not sterile, can cause infection. Use cool water and cover.

**MYTH:** "Butter reduces scarring"
**FACT:** No evidence. Keep moist, protect from sun, gentle massage.

**MYTH:** "Pee on it" (jellyfish/burns)
**FACT:** Not sterile, doesn't help, can make worse. Use vinegar for jellyfish, cool water for burns.

---

## Long-Term Effects

**Physical:**
- Scarring (worse without proper treatment)
- Contractures (skin tightens, limits movement)
- Skin sensitivity (heat, cold, sun)
- Color changes (hyperpigmentation/hypopigmentation)
- Itching (can last months)

**Prevention:**
- Proper initial treatment
- Keep wounds moist during healing
- Physical therapy if needed
- Sun protection
- Massage and moisturize

**Psychological:**
- Appearance anxiety
- PTSD (from incident)
- Depression (if severe burns)

**Support available:**
- Counseling
- Support groups
- Occupational therapy
- Burn survivor networks

---

## Summary Checklist

### Immediate Response
- [ ] Remove from heat source
- [ ] Cool with running water (20 minutes)
- [ ] Remove jewelry/tight clothing
- [ ] Cover with clean, dry dressing
- [ ] Assess severity

### Call 000 If:
- [ ] Third degree burn (any size)
- [ ] Face, hands, feet, genitals, joints
- [ ] > 10% body surface area
- [ ] Chemical or electrical burn
- [ ] Child, elderly, pregnant
- [ ] Signs of shock or breathing difficulty

### Ongoing Care
- [ ] Keep clean, change dressing daily
- [ ] Monitor for infection
- [ ] Don't pop blisters
- [ ] Pain management
- [ ] Follow-up medical care if needed

### Prevention
- [ ] Sun protection (slip, slop, slap)
- [ ] Kitchen safety
- [ ] Fire safety plan
- [ ] First aid kit stocked

---

## Related Guides

- **Shock Treatment:** `GUIDE START shock-treatment`
- **Wound Care:** `GUIDE START wound-care-bleeding`
- **CPR:** `GUIDE START basic-cpr`
- **Bushfire Survival:** `GUIDE START bushfire-survival`

---

**Key Principle:** Cool immediately, cover cleanly, assess carefully. When in doubt, seek medical care.

**Emergency Number:** 000 (Australia)
**Poisons Information:** 13 11 26 (for chemical burns)
