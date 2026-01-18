---
tier: 1
category: medical
title: "Basic CPR (Cardiopulmonary Resuscitation)"
complexity: basic
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Basic CPR (Cardiopulmonary Resuscitation)

**Category**: Survival > First Aid
**Last Updated**: November 14, 2025
**Source**: International resuscitation guidelines

> ⚠️ **Emergency**: If someone is unresponsive and not breathing, call emergency services (911/112/999) IMMEDIATELY, then begin CPR.

# Basic CPR

## Overview

Cardiopulmonary Resuscitation (CPR) is a critical, life-saving technique performed when someone's breathing or heart stops, often due to cardiac arrest. Immediate and effective CPR can double or triple a person's chance of survival by maintaining blood flow to the brain and other vital organs until professional medical help arrives or an Automated External Defibrillator (AED) can be used. This guide focuses on practical steps for a survival scenario.

### CPR Sequence Diagram

```sequence
Rescuer->Scene: Check for dangers
Scene->Victim: Tap shoulder and shout
Victim->Rescuer: No response detected
Rescuer->Help: Call 911 immediately
Help->Rescuer: Emergency services notified
Rescuer->Victim: Position flat on back
Victim->Rescuer: Airway opened
Rescuer->Victim: 30 chest compressions
Victim->Rescuer: 2 rescue breaths
Rescuer->Victim: Continue 30:2 cycle
Victim->Check: Check for pulse/breathing
Check->Rescuer: No pulse detected
Rescuer->Victim: Continue CPR cycles
Victim->AED: Apply if available
AED->Rescuer: Follow device prompts
Rescuer->Continue: Until help arrives
```

### CPR Decision Flow

```flow
st=>start: Find unresponsive person
safe=>condition: Scene safe?
call=>operation: Call 911
respond=>condition: Responsive?
breathing=>condition: Breathing normally?
cpr=>operation: Begin CPR 30:2
aed=>condition: AED available?
apply=>operation: Apply AED
help=>condition: Help arrived?
cont=>operation: Continue CPR
recov=>end: Recovery position

st->safe
safe(yes)->respond
safe(no)->recov
respond(no)->call
respond(yes)->recov
call->breathing
breathing(no)->cpr
breathing(yes)->recov
cpr->aed
aed(yes)->apply->help
aed(no)->help
help(no)->cont->help
help(yes)->recov
```

## Materials Needed

*   **A Firm, Flat Surface:** Essential for effective chest compressions (e.g., the ground, a sturdy floor).
*   **Gloves (optional but recommended):** If available, to protect against potential disease transmission.
*   **Barrier Device (e.g., pocket mask, face shield - optional):** If rescue breaths are to be given, these protect the rescuer.
*   **Automated External Defibrillator (AED) (if available):** An electronic device that can analyze heart rhythm and deliver an electrical shock to restore normal rhythm.

## Step-by-Step Instructions

**1. Check the Scene and the Person**
*   **Ensure Safety:** Before approaching, quickly assess the scene for any dangers (traffic, falling debris, active threats). Your safety is paramount.
*   **Check for Responsiveness:** Tap the person's shoulder firmly and shout loudly, "Are you okay? Are you okay?"
*   **Look for Signs of Life:** Quickly scan for normal breathing (gasping or irregular breathing is *not* normal breathing) and any movement. Do this for no more than 10 seconds.
*   **Call for Help:** If the person is unresponsive and not breathing normally, immediately yell for help. If alone and you have a mobile device, call emergency services (e.g., 911, 112, 999) and put it on speakerphone, then begin CPR. If others are present, designate someone to call for help and retrieve an AED if available.

**2. Position the Person**
*   Carefully roll the person onto their back on a firm, flat surface (like the ground).
*   Ensure their airway is clear and their arms are straight by their sides if possible.

**3. Begin Chest Compressions (Hands-Only CPR)**
*   **Locate Hand Position:** Kneel beside the person. Place the heel of one hand in the center of their chest, on the lower half of the breastbone (sternum).
*   **Second Hand Placement:** Place the heel of your other hand directly on top of the first hand. Interlace your fingers or keep them raised to ensure pressure is not applied to the ribs
