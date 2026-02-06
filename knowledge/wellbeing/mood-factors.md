---
uid: udos-guide-wellbeing-20260130022100-UTC-L300AB51
title: Mood Factors System
tags: [guide, knowledge, wellbeing]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Mood Factors System

**Category:** Well-Being  
**Tags:** mood, factors, composite, science  
**Difficulty:** Intermediate

---

## Overview

The uDOS Mood Factors System calculates a composite wellbeing score from multiple input sources. The system is designed to be:

- **Mathematical** - All inputs normalized to 0.0-1.0 scale
- **Weighted** - Different factors contribute proportionally
- **Transparent** - You can see what influences your score
- **Private** - All data stays on your device

---

## The Four Factor Categories

Your composite mood score draws from four categories:

```
COMPOSITE MOOD SCORE (0.0 - 1.0)
├── CELESTIAL FACTORS (25%)
│   ├── Lunar phase
│   ├── Lunar distance (tidal)
│   ├── Solar position / season
│   ├── Western zodiac compatibility
│   └── Chinese zodiac element
│
├── TEMPORAL FACTORS (25%)
│   ├── Circadian phase (time of day)
│   ├── Ultradian rhythm (90-min cycles)
│   ├── Day of week
│   ├── Season
│   └── Numerology resonance
│
├── BEHAVIORAL FACTORS (30%)
│   ├── Typing speed vs baseline
│   ├── Typing rhythm consistency
│   ├── Command frequency
│   ├── Command complexity
│   ├── Error/correction rate
│   └── Session duration
│
└── BIOLOGICAL FACTORS (20%)
    ├── Self-reported energy
    ├── Self-reported mood
    ├── Inferred activity level
    └── Time since last break
```

---

## How Scores Are Calculated

### Raw Factor Values

Each factor produces a value from 0.0 to 1.0:

- **0.0** - Lowest/negative influence
- **0.5** - Neutral baseline
- **1.0** - Highest/positive influence

### Weighted Contribution

Factors are weighted within their category and by category weight:

```
contribution = raw_value × category_weight × factor_weight
```

Example for lunar phase:

```
raw_value = 0.85 (near full moon)
category_weight = 0.25 (celestial)
factor_weight = 0.30 (within celestial)

contribution = 0.85 × 0.25 × 0.30 = 0.064
```

### Composite Calculation

All contributions are summed and normalized:

```
composite = Σ(contribution × confidence) / Σ(weight × confidence)
```

The confidence factor accounts for data quality - factors with more data have higher confidence.

---

## Interpreting Your Score

| Score Range | Interpretation | System Response |
|-------------|----------------|-----------------|
| 0.80 - 1.00 | Excellent | Suggest complex tasks |
| 0.60 - 0.79 | Good | Normal operations |
| 0.40 - 0.59 | Moderate | Lighter workload |
| 0.20 - 0.39 | Low | Rest suggested |
| 0.00 - 0.19 | Very Low | Conservation mode |

---

## Viewing Your Factors

### Quick Score

```bash
WELLBEING SCORE
# Output: Composite Mood: 0.67 (Good)
```

### Category Breakdown

```bash
WELLBEING FACTORS
# Shows all four categories with sub-factors
```

### Detailed Analysis

```bash
WELLBEING FACTORS --verbose
# Full calculation breakdown with weights
```

---

## Scientific Basis

### Empirically Supported Factors

These factors have research backing:

- **Circadian rhythms** - Strong evidence for alertness patterns
- **Sleep/break timing** - Clear cognitive effects
- **Typing patterns** - Correlated with emotional state (Epp et al., 2011)
- **Lunar illumination** - Subtle sleep effects (Cajochen, 2013)

### Pattern-Based Factors

These provide structure without strong empirical validation:

- **Numerology** - Pattern framework, weighted low
- **Zodiac compatibility** - Traditional system, weighted low
- **Planetary hours** - Historical scheduling system

The system weights empirical factors higher than pattern-based factors.

---

## Privacy and Security

### Sensitive Data

Birth date, time, and place are:

- Stored encrypted in `memory/bank/private/identity.enc`
- Never transmitted
- Hashed in logs (you see `[hash:a1b2c3d4]` not the actual data)

### Behavioral Data

Typing patterns and session data are:

- Stored locally only
- Aggregated into baselines (individual keystrokes not stored)
- Deletable with `WELLBEING RESET`

### Log Hashing

Sensitive values are one-way hashed before logging:

```
[LOCAL] Identity updated for user [hash:7f3a9c2e]
[LOCAL] Composite mood: 0.67 (celestial: 0.72, temporal: 0.58, ...)
```

---

## Customization

### Adjusting Category Weights

If certain factors feel more relevant to you:

```bash
WELLBEING FACTORS WEIGHT celestial 0.15
WELLBEING FACTORS WEIGHT behavioral 0.40
```

### Disabling Categories

```bash
WELLBEING FACTORS DISABLE celestial
# Redistributes weight to other categories
```

### Personal Calibration

The system learns your patterns over time:

- Typing baseline adapts to your normal speed
- Break recommendations adjust to your session lengths
- Chronotype detection from actual wake/sleep patterns

---

## Related Commands

- `WELLBEING STATUS` - Current state overview
- `WELLBEING IDENTITY` - Birth data and derived values
- `WELLBEING CELESTIAL` - Astronomical influences
- `WELLBEING HISTORY` - Score over time

---

## Further Reading

- [Circadian Rhythms](./circadian-rhythms.md) - Biological clock science
- [Celestial Mechanics](../reference/celestial-mechanics.md) - Moon and sun cycles
- [Chinese Astrology](../reference/chinese-astrology.md) - Animal years and elements
- [Numerology Basics](../reference/numerology-basics.md) - Number patterns

---

Last Updated: 2026-01-07
