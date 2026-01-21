---
tier: 2
category: shelter
title: "Shelter Site Selection"
complexity: intermediate
last_updated: 2025-12-04
author: uDOS
version: 1.1
---

# Shelter Site Selection

**Category:** shelter
**Difficulty:** beginner
**Generated:** 2025-11-27

## Overview

Proper shelter site selection is critical for survival - your location can mean the difference between a safe, restful camp and a dangerous, miserable night. This guide covers essential criteria for evaluating and choosing the best shelter location based on protection, resources, safety, and rescue visibility. Good site selection saves time, conserves energy, and maximizes survival chances.

### Shelter Site Selection Decision Flow

```flow
st=>start: Need shelter site
level=>condition: Ground level?
hazards=>condition: Hazards present?
water=>condition: Water nearby?
wind=>condition: Wind protection?
material=>condition: Materials available?
drainage=>condition: Good drainage?
ideal=>operation: Excellent site
accept=>operation: Acceptable site
search=>operation: Keep searching
build=>end: Begin shelter construction

st->level
level(yes)->hazards
level(no)->search->st
hazards(no)->water
hazards(yes)->search->st
water(yes)->wind
water(no)->search->st
wind(yes)->material
wind(no)->accept->build
material(yes)->drainage
material(no)->accept->build
drainage(yes)->ideal->build
drainage(no)->accept->build
```

### Site Evaluation Sequence

```sequence
Start->Safety: Check immediate dangers
Safety->Clear: Look overhead for deadfall
Clear->Ground: Test ground stability
Ground->Water: Locate water source
Water->Wind: Assess wind direction
Wind->Resources: Check building materials
Resources->Drainage: Test drainage
Drainage->Visibility: Consider rescue visibility
Visibility->Decision: Evaluate all factors
Decision->Mark: Mark selected site
Mark->Build: Begin construction
```

## Materials Needed

- Observation skills (primary tool)
- Walking stick (to test ground/probe for hazards)
- Compass (for orientation)
- Map (if available)
- Whistle (for signaling if separated from group)
- Flagging tape/markers (to mark potential sites)

## Step-by-Step Instructions

### 1. Assess Immediate Safety

**Avoid:**
- Flash flood zones (dry washes, narrow valleys)
- Below dead/leaning trees (widowmakers)
- Steep slopes (rockfall/landslide risk)
- Animal trails/dens
- Insect nests (check overhead and ground)

**Look for:**
- Level ground
- Stable trees (for shelter support)
- Clear overhead (no loose branches)
- Distance from water (100+ feet - flooding risk)

### 2. Evaluate Environmental Protection

**Wind Protection:**
- Natural windbreaks (ridge, dense vegetation, rock wall)
- Avoid hilltops/exposed ridges (maximum wind)
- Check prevailing wind direction

**Weather Shelter:**
- Natural overhead cover (rock overhang, dense canopy)
- South-facing sites (Northern Hemisphere - more sun)
- Avoid valley bottoms (cold air sinks, frost pockets)

**Drainage:**
- Slight slope for water runoff
- No depressions (water pools)
- Above flood level

### 3. Check Resource Availability

**Water:**
- Within reasonable distance (5-15 minutes walk)
- Not TOO close (insects, animals, flooding)
- Stream/lake visible or audible

**Firewood:**
- Abundant deadwood nearby
- Standing dead trees (drier than ground fuel)
- Mixed sizes (tinder, kindling, fuel)

**Building Materials:**
- Branches, leaves, bark for shelter
- Rocks for fire ring/tools
- Natural materials for insulation

### 4. Assess Rescue/Signal Visibility

**If awaiting rescue:**
- Open area nearby for signals
- Visible from air (clearing, beach, ridgetop)
- Near trail/road (but not directly on it)

**If evading:**
- Concealed from trails
- Natural camouflage
- Minimal smoke (cooking fires only)

### 5. Ground Conditions

**Test ground:**
- Probe with stick for soft/boggy spots
- Check for ant hills, snake holes
- Remove rocks, sticks, pinecones
- Look for level sleeping area (6-7 feet)

**Avoid:**
- Rocky ground (uncomfortable, cold)
- Sandy/loose soil (unstable, hard to dig)
- Dense roots (hard to clear)

```[ASCII Diagram]
  Ideal Shelter Site Layout
  
       Wind Direction  ←
  ┌────────────────────────┐
  │  Ridge/Trees          │ Windbreak
  │    (Windbreak)         │
  └────────────────────────┘
  
      ▲  ▲  ▲
     ╱│╲╱│╲╱│╲  Shelter
    ╱ │ ╱ │ ╱ │   (3-5' from
   ╱  │╱  │╱  │    windbreak)
  
    ═══════════  Slight slope
                  (drainage)
  
  ～～～～～～～～  Water source
  (100+ ft away)
```

## Safety Considerations

**Flash Flood Danger:**
- Check for high-water marks on rocks/trees
- Avoid canyons, washes, dry streambeds
- Monitor weather upstream
- Rain elsewhere can cause local flooding

**Wildlife Hazards:**
- No food near shelter (attract animals)
- Check for scat, tracks, bedding areas
- Avoid game trails (animal highways)
- Bears prefer dense cover near water

**Falling Hazards:**
- "Widowmakers" - dead branches overhead
- Loose rocks on slopes above
- Unstable trees (check for rot)
- Snow-laden branches

**Environmental Hazards:**
- Lightning - avoid lone trees, peaks
- Avalanche - check slope angles (>30°)
- Rockfall - avoid talus slopes
- Tides - coastal camps above high tide

## Tips & Troubleshooting

**Common Mistakes:**
- Camping too close to water (flooding, insects)
- Choosing first available site (hasty decision)
- Ignoring overhead hazards
- Setting up in dark (can't see dangers)

**Improving Site Selection:**
- Scout area in daylight
- Check multiple potential sites
- Spend 15-20 minutes observing before committing
- Walk perimeter looking up AND down

**Quick Site Evaluation (Priority Order):**
1. Safe? (No immediate hazards)
2. Dry? (No flooding/pooling risk)
3. Sheltered? (Wind/weather protection)
4. Resources? (Water, fuel, materials nearby)
5. Visible? (For rescue, if needed)

**Signs of Good Site:**
- Wildlife avoids it (not a trail/den)
- Moderate vegetation (not too dense, not barren)
- Minimal ground prep needed
- Natural advantages (rock wall, clearing)
- Peaceful/comfortable feeling (trust instincts)

**Emergency/Dark Conditions:**
- Use headlamp to scan overhead
- Feel ground with hands for slope/debris
- Listen for water sounds (flooding risk)
- Set up minimal shelter, improve at dawn
- Mark site perimeter with reflective tape

**Group Site Selection:**
- Large enough for all shelters (10+ ft between)
- Central fire area
- Latrine 200+ ft downwind and downhill from water
- Establish trails to water/latrine (prevent getting lost)
