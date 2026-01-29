---
uid: udos-guide-medical-20251204172800-UTC-L300AB66
title: First Aid: Wound Care & Bleeding Control
tags: [guide, knowledge, medical]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# First Aid: Wound Care & Bleeding Control

**Category**: Medical Knowledge
**Difficulty**: Beginner to Intermediate
**Time Required**: Varies by severity
**Materials**: First aid kit or improvised supplies
**Critical**: Can be life-saving

## Overview

Proper wound care prevents infection and promotes healing. Bleeding control is a critical life-saving skill. In wilderness/survival situations, medical help may be hours or days away.

### Bleeding Control Decision Flow

```flow
st=>start: Bleeding injury
severity=>condition: Severity level?
capillary=>operation: Apply light pressure
venous=>operation: Direct pressure 10+ min
arterial=>operation: Immediate firm pressure
press=>condition: Bleeding stops?
elevate=>operation: Elevate limb
point=>operation: Pressure point
dress=>operation: Pressure dressing
tourni=>condition: Life threatening?
apply=>operation: Apply tourniquet
monitor=>operation: Monitor wound
safe=>end: Bleeding controlled
hosp=>end: Emergency transport

st->severity
severity(capillary)->capillary->press
severity(venous)->venous->press
severity(arterial)->arterial->press
press(yes)->dressing->monitor->safe
press(no)->elevate->point->tourni
tourni(yes)->apply->hosp
tourni(no)->dressing->monitor->safe
```

### Severe Bleeding Control Sequence

```sequence
Rescuer->Wound: Assess bleeding severity
Wound->Rescuer: Arterial bleeding detected
Rescuer->Pressure: Apply direct pressure
Pressure->Wound: Press firmly on wound
Wound->Check: Check after 10 minutes
Check->Rescuer: Still bleeding
Rescuer->Elevate: Raise limb above heart
Elevate->Point: Apply pressure point
Point->Rescuer: Still not controlled
Rescuer->Pack: Pack wound with gauze
Pack->Bandage: Apply pressure bandage
Bandage->Decision: Life threatening?
Decision->Tourniquet: Apply tourniquet
Tourniquet->Emergency: Call 911 immediately
Emergency->Hospital: Transport to hospital
```

## Types of Bleeding

### Capillary Bleeding (Minor)
- Oozing from surface
- Dark red color
- Slow flow
- Stops easily with pressure

### Venous Bleeding (Moderate)
- Steady flow
- Dark red/maroon color
- Flows continuously
- Needs sustained pressure

### Arterial Bleeding (SEVERE - Life Threatening)
- Spurting/pulsing
- Bright red color
- High pressure
- **Can cause death in minutes**
- **IMMEDIATE action required**

## Severe Bleeding Control (ABC Priority)

**If severe bleeding: Control bleeding BEFORE anything else**

### Step 1: Direct Pressure (First Response)

1. **Apply immediate pressure**:
   - Use cleanest cloth available (sterile gauze ideal)
   - Press firmly directly on wound
   - Don't peek or remove (breaks clot)
   - Maintain 10-15 minutes minimum

2. **Pressure points** (if direct pressure insufficient):
   - Apply pressure to artery between wound and heart
   - **Arm**: Brachial artery (inside upper arm)
   - **Leg**: Femoral artery (groin)
   - Use with direct pressure, not instead of

3. **Elevation** (if no fracture):
   - Raise injured area above heart
   - Reduces blood flow to area
   - Use with direct pressure

### Step 2: Pressure Dressing

If bleeding continues:

1. **Pack wound with gauze/cloth**
2. **Apply pressure bandage over packing**:
   - Wrap firmly (not cutting off circulation)
   - Check pulse below bandage (should still feel it)
   - Tape or tie securely

3. **If blood soaks through**:
   - **Don't remove original dressing**
   - Add more dressing on top
   - Increase pressure

### Step 3: Tourniquet (LAST RESORT - Life vs Limb)

**Use ONLY when**:
- Severe arterial bleeding from limb
- Direct pressure failing
- Multiple casualties (can't maintain pressure on all)
- Limb amputation/mangling

**Application**:

1. **Place 2-3 inches above wound** (closer to heart)
   - **Never place on joint**
   - On single bone if possible (not forearm/lower leg)

2. **Use wide material** (2"+ wide):
   - Commercial tourniquet (CAT, SOFTT)
   - Belt
   - Triangular bandage folded
   - **Never**: Wire, rope, string (causes tissue damage)

3. **Tighten until bleeding stops**:
   - Will be painful
   - Tighten more than you think necessary
   - Check that bleeding actually stopped

4. **Note time applied**:
   - Write on patient or tourniquet
   - Critical for medical handoff
   - Can cause permanent damage after 2 hours

5. **Don't loosen once applied**:
   - Can cause shock from toxin release
   - Medical decision only

**After tourniquet**: Get to medical care IMMEDIATELY

### Hemostatic Agents (Advanced)

**Commercial products**: QuikClot, Celox, HemCon

**Use**:
- Pack directly into wound
- Promotes rapid clotting
- Use with direct pressure
- Effective for areas tourniquet can't reach (junctional areas: groin, armpit, neck)

**Improvised**: Cayenne pepper (controversial - can work, may increase pain)

## Wound Types & Treatment

### Abrasions (Scrapes)

**Characteristics**:
- Surface skin damage
- Oozing/minor bleeding
- Dirt/debris common

**Treatment**:
1. **Clean thoroughly**:
   - Rinse with clean water (drinking quality)
   - Gentle scrubbing with soap if available
   - Remove all dirt/debris (prevents "tattooing")
   - Pat dry

2. **Apply antibiotic ointment** (if available):
   - Bacitracin, Neosporin, or triple antibiotic
   - Thin layer

3. **Cover with bandage**:
   - Non-stick pad
   - Tape or wrap
   - Change daily or when dirty/wet

4. **Monitor for infection**

### Lacerations (Cuts)

**Characteristics**:
- Clean or jagged edges
- Bleeding varies by depth
- May need closure

**Treatment**:

**Shallow cuts**:
1. Stop bleeding (pressure)
2. Clean thoroughly
3. Antibiotic ointment
4. Butterfly bandage or steri-strips to close
5. Cover with dressing

**Deep cuts** (may need stitches):
1. Control bleeding
2. Clean as much as possible
3. **If edges easily come together**:
   - Close with butterfly bandages or steri-strips
   - Apply perpendicular to cut
   - Start at center, work outward
   - Close edges without overlapping
4. Cover with sterile dressing
5. **Seek medical care if**:
   - Very deep (fat/muscle visible)
   - Gaping open
   - On face (scarring concern)
   - Over joint (may reopen)
   - Signs of infection

**Improvised closure**:
- Super glue (medical grade cyanoacrylate or regular in emergency)
- Duct tape strips
- Safety pins with thread

### Puncture Wounds

**Characteristics**:
- Small opening
- Deep penetration
- High infection risk

**Treatment**:

1. **If object still embedded**:
   - **DON'T REMOVE** if large or in torso/neck/head
   - Stabilize in place
   - Immediate medical care

2. **If small and superficial**:
   - Remove object
   - Allow to bleed briefly (flushes bacteria)
   - Clean thoroughly
   - Don't close (needs to drain from inside)

3. **Soak in warm soapy water** 3x daily

4. **Watch closely for infection** (high risk)

### Avulsions (Skin Torn Off)

**Treatment**:
1. Control bleeding
2. Clean wound and torn skin
3. If skin still attached, lay back in place
4. If separated, keep moist and cool (may be reattached)
5. Cover with non-stick dressing
6. Medical care ASAP

### Amputations

**Treatment**:
1. **Control bleeding** (tourniquet likely needed)
2. **Care for amputated part**:
   - Wrap in moist sterile gauze
   - Place in plastic bag
   - Place bag in ice water (NOT directly on ice)
   - Keep with patient
3. **Medical evacuation IMMEDIATELY**

## Wound Cleaning

### Irrigation (Best Method)

**Supplies**:
- Syringe (20-30cc) or irrigation syringe
- Clean water (drinking quality minimum)
- Saline solution (ideal) or clean water

**Process**:
1. Draw water into syringe
2. **Irrigate wound forcefully**:
   - Hold 2-3" from wound
   - Aim at angle (not straight in)
   - Use pressure to dislodge debris
   - Use large volume (liter+ for dirty wounds)

**Improvised irrigation**:
- Water bottle with small hole in cap
- Zip-lock bag with corner hole
- Squeeze bottle

### Scrubbing

**When**: Abrasions with ground-in dirt

1. Use gauze or clean cloth
2. Soap and water
3. Gentle circular motion
4. Rinse thoroughly

### What to Use

**Best to worst**:
1. Sterile saline
2. Clean (drinkable) water
3. Boiled and cooled water
4. Cleanest water available + purification tablet

**Don't use**:
- Hydrogen peroxide (damages tissue, delays healing)
- Alcohol (damages tissue, very painful)
- Iodine solutions (except diluted betadine for initial cleaning)

## Bandaging Principles

### Dressing (Direct on Wound)

**Types**:
- Sterile gauze pads (best)
- Non-stick pads (for weeping wounds)
- Clean cloth (improvised)

**Application**:
- Extends beyond wound edges
- Thick enough to absorb drainage
- Secured but not tight

### Bandage (Holds Dressing)

**Types**:
- Medical tape
- Elastic wrap (ACE bandage)
- Gauze roll
- Triangular bandage

**Technique**:
- Secure without cutting circulation
- Check pulse below bandage
- Check for numbness/tingling/color change

### When to Change

**Change dressing if**:
- Wet or dirty
- Blood soaking through
- Signs of infection
- Foul odor
- At least daily

## Infection Prevention & Recognition

### Prevention

1. **Clean wound thoroughly** (most important)
2. **Antibiotic ointment** if available
3. **Keep covered** (moist environment heals faster)
4. **Change dressings regularly**
5. **Keep area clean and dry**
6. **Avoid contamination**

### Signs of Infection (usually appears 24-72 hours post-injury)

**Early signs**:
- Increased pain
- Redness spreading from wound
- Warmth around wound
- Swelling
- Pus or cloudy drainage

**Severe infection**:
- Red streaks from wound (following lymph vessels)
- Fever
- Chills
- Swollen lymph nodes
- Severe pain
- Foul odor

**Action**:
- Clean more aggressively
- Remove any closure (needs to drain)
- Warm soaks 3-4x daily
- **Medical care urgently** (may need antibiotics)

### Improvised Infection Treatment

**Honey** (raw, unpasteurized):
- Natural antibiotic properties
- Apply to wound under dressing
- Change daily

**Garlic** (crushed):
- Antimicrobial
- Can be irritating
- Use cautiously

**Sugar**:
- Draws moisture, inhibits bacteria
- Pack wound, cover
- Change daily

**Maggot therapy** (extreme emergency):
- Certain fly larvae eat only dead tissue
- Natural debridement
- Medical-grade available; wild use risky

## Special Wounds

### Animal Bites

**High infection risk**:
1. Clean very thoroughly
2. **Don't close** (needs drainage)
3. Monitor closely for infection
4. **Rabies concern**: Medical care ASAP if any possibility
5. Human bites also very high infection risk

### Burns (Minor)

**First-degree** (red, painful):
- Cool with water 10-15 minutes
- Aloe vera or burn gel
- Cover loosely

**Second-degree** (blisters):
- Cool with water
- Don't pop intact blisters
- If broken, clean and dress
- Antibiotic ointment
- Cover with non-stick dressing

**Third-degree** (white/charred):
- **Don't cool** (shock risk)
- Cover with dry sterile dressing
- **Medical evacuation**

### Splinters

1. Clean area with soap and water
2. **Sterilize tweezers** (flame or alcohol)
3. Remove along angle of entry
4. Squeeze to encourage bleeding (flushes bacteria)
5. Clean again
6. Antibiotic ointment

**If deep or broken off**: May need incision to remove

## Improvised Supplies

### Bandages

- Clean t-shirt strips
- Bandana
- Socks (clean)
- Duct tape
- Plastic wrap (occlusive dressing)

### Wound Cleaning

- Boiled and cooled water
- Water purification tablets in water
- Saline: 1 tsp salt per liter water

### Antibiotic

- Honey (raw)
- Garlic (crushed)
- Pine pitch (antimicrobial)
- Sugar paste

## First Aid Kit Essentials

**Bleeding Control**:
- Tourniquet (CAT or SOFTT)
- Israeli bandage or pressure dressing
- Gauze pads (various sizes)
- Hemostatic gauze (QuikClot)

**Wound Care**:
- Adhesive bandages (various sizes)
- Non-stick pads
- Medical tape
- Elastic wrap
- Butterfly bandages/steri-strips
- Irrigation syringe
- Saline or sterile water

**Medications**:
- Triple antibiotic ointment
- Pain reliever (ibuprofen, acetaminophen)

**Tools**:
- Tweezers
- Scissors
- Gloves (multiple pairs)
- Safety pins

## When to Seek Medical Care

**Immediate**:
- Severe bleeding not controlled
- Deep wounds
- Amputations
- Wounds with arterial bleeding
- Embedded objects in torso/head/neck
- Severe burns

**Urgent** (within 24 hours):
- Deep lacerations needing closure
- Puncture wounds
- Animal/human bites
- Signs of infection
- Loss of function
- Numbness below wound

**Monitor closely**:
- Any wound in survival situation
- Watch for infection
- Re-evaluate if condition changes

---

---

## Diagram

```
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐        Apply direct pressure         ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐         Elevate if possible          ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐   Add more dressing (don't remove)   ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐       Pressure point if needed       ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐          Seek medical help           ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
```

---

**Related Guides**:
- Trauma Care Basics
- Shock Recognition & Treatment
- Fracture & Dislocation Care
- Burns & Scalds Treatment
- Improvised Medical Supplies
- Wilderness First Aid Kit
- Herbal Wound Care
