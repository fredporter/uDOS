---
uid: udos-guide-reference-20260129221000-UTC-L300AB88
title: Celestial Mechanics Reference
tags: [guide, knowledge, reference]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Celestial Mechanics Reference

**Category:** Reference  
**Tags:** astronomy, moon, sun, tides, cycles  
**Difficulty:** Intermediate

---

## Overview

Celestial mechanics describes the mathematical principles governing the motion of celestial bodies. For mood factor calculations, we primarily use **lunar** and **solar** cycles, which have measurable effects on Earth and biological systems.

---

## Lunar Cycles

The Moon follows several overlapping cycles that affect tidal forces and light conditions.

### Synodic Month (Phases)

The time between identical lunar phases (e.g., new moon to new moon).

- **Duration:** 29.53059 days
- **Reference Point:** New Moon on January 6, 2000 at 18:14 UTC

| Phase | Day Range | Illumination | Traditional Association |
|-------|-----------|--------------|-------------------------|
| New Moon | 0-1.85 | 0% | New beginnings, introspection |
| Waxing Crescent | 1.85-7.38 | 1-49% | Growth, intention setting |
| First Quarter | 7.38-9.23 | 50% | Action, decision making |
| Waxing Gibbous | 9.23-14.77 | 51-99% | Refinement, patience |
| Full Moon | 14.77-16.61 | 100% | Completion, illumination |
| Waning Gibbous | 16.61-22.15 | 99-51% | Gratitude, sharing |
| Last Quarter | 22.15-24.0 | 50% | Release, letting go |
| Waning Crescent | 24.0-29.53 | 49-1% | Rest, reflection |

### Anomalistic Month (Distance)

The time between lunar perigees (closest approaches to Earth).

- **Duration:** 27.55455 days
- **Perigee:** Moon closest to Earth (~356,500 km)
- **Apogee:** Moon furthest from Earth (~406,700 km)

The difference in distance creates variation in tidal forces of approximately 20%.

### Calculation

```
days_since_new_moon = (current_date - reference_new_moon) mod 29.53059
phase_position = days_since_new_moon / 29.53059

# Phase as 0.0-1.0 factor (full moon = 1.0, new moon = 0.0)
phase_factor = 0.5 + 0.5 * cos(2π * (phase_position - 0.5))
```

---

## Solar Cycles

### Solar Declination

The angle between the Sun and Earth's equatorial plane, causing seasons.

- **Range:** -23.44° (winter solstice) to +23.44° (summer solstice)
- **Equinoxes:** 0° (March 21, September 23)

Day length affects light exposure and circadian rhythms:

| Season | Declination | Day Length (50°N) | Effect |
|--------|-------------|-------------------|--------|
| Summer Solstice | +23.44° | ~16.5 hours | High alertness |
| Winter Solstice | -23.44° | ~7.5 hours | Reduced energy |
| Equinoxes | 0° | 12 hours | Balanced |

### Solar Day Position

Time of day affects solar radiation angle:

```
solar_elevation = 90° - latitude + declination

# Higher elevation = stronger light signal to circadian system
# Peak at solar noon (varies by longitude and time zone)
```

---

## Tidal Forces

Tides are caused by gravitational pull of Moon and Sun.

### Spring and Neap Tides

- **Spring Tides:** New/Full Moon - Sun and Moon aligned, maximum tidal range
- **Neap Tides:** Quarter Moons - Sun and Moon at 90°, minimum tidal range

### Tidal Factor

```
# Combined lunar-solar gravitational factor
tidal_strength = lunar_distance_factor * phase_alignment_factor

# phase_alignment: 1.0 at new/full moon, 0.5 at quarters
```

---

## Scientific Basis

Studies have found correlations between lunar cycles and:

- Sleep patterns (Cajochen et al., 2013 - Current Biology)
- Birth rates (statistical patterns in some populations)
- Menstrual cycles (average ~29.5 days, similar to synodic month)

However, effects are subtle and individual variation is high. The mood factor system treats celestial influences as one input among many.

---

## References

- Meeus, Jean. "Astronomical Algorithms" (1991)
- Cajochen, C. et al. "Evidence that the Lunar Cycle Influences Human Sleep" Current Biology (2013)
- USNO Astronomical Applications Department

---

*Last Updated: 2026-01-07*
