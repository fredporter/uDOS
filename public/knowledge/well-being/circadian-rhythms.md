# Circadian Rhythms

**Category:** Well-Being  
**Tags:** sleep, biology, chronotype, alertness  
**Difficulty:** Beginner

---

## Overview

Circadian rhythms are 24-hour cycles that regulate physiological processes including sleep-wake cycles, hormone release, body temperature, and cognitive performance. Understanding your circadian rhythm helps optimize productivity and wellbeing.

---

## The Biological Clock

Your body has a master clock in the suprachiasmatic nucleus (SCN) of the brain. It responds primarily to light signals from the eyes.

### Key Hormones

| Hormone | Peak Time | Function |
|---------|-----------|----------|
| Cortisol | 06:00-08:00 | Alertness, stress response |
| Melatonin | 21:00-03:00 | Sleep initiation, recovery |
| Testosterone | 07:00-09:00 | Energy, mood (males) |
| Growth Hormone | 23:00-02:00 | Repair, recovery |

### Alertness Curve

A typical alertness pattern for an intermediate chronotype:

```
Alertness
   ^
   |     ____
   |    /    \        ___
   |   /      \      /   \
   |  /        \    /     \
   | /          \__/       \
   +----------------------------> Time
   6  8  10  12  14  16  18  20  22
       |        |        |
      Peak    Dip     Second
               |       Peak
          Afternoon
            Slump
```

---

## Chronotypes

People vary in their natural sleep-wake preferences. This is called chronotype.

### The Three Main Chronotypes

| Chronotype | Wake Preference | Peak Alertness | Sleep Preference |
|------------|-----------------|----------------|------------------|
| Early (Lark) | 05:00-06:30 | 09:00-11:00 | 21:00-22:00 |
| Intermediate | 06:30-08:00 | 10:00-12:00 | 22:00-23:30 |
| Late (Owl) | 08:00-10:00 | 11:00-13:00 | 00:00-02:00 |

### Chronotype Assessment

Simple questions to determine your type:

1. **If free to choose, when would you wake?**
   - Before 6:30 AM → Early
   - 6:30-8:00 AM → Intermediate
   - After 8:00 AM → Late

2. **When do you feel most mentally sharp?**
   - Morning (before noon) → Early
   - Late morning/early afternoon → Intermediate
   - Afternoon/evening → Late

3. **What time would you naturally fall asleep?**
   - Before 10 PM → Early
   - 10 PM - midnight → Intermediate
   - After midnight → Late

---

## The Afternoon Dip

Almost everyone experiences reduced alertness in early afternoon (typically 13:00-15:00). This is biological, not just caused by lunch.

### Causes

- Post-prandial (after eating) drowsiness
- Natural circadian trough
- Accumulated sleep pressure

### Strategies

1. **Time low-demand tasks** for this period
2. **Brief nap** (10-20 minutes) if possible
3. **Light exposure** - go outside
4. **Movement** - short walk
5. **Cold water** - face or drink

---

## Optimizing Your Day

### For Early Chronotypes

| Time | Best Activities |
|------|-----------------|
| 06:00-09:00 | Deep work, complex problems |
| 09:00-12:00 | Peak productivity, decisions |
| 13:00-15:00 | Routine tasks, meetings |
| 15:00-18:00 | Collaborative work |
| After 18:00 | Wind down, light tasks |

### For Intermediate Chronotypes

| Time | Best Activities |
|------|-----------------|
| 08:00-10:00 | Warm-up, planning |
| 10:00-13:00 | Peak productivity |
| 14:00-16:00 | Routine tasks, meetings |
| 16:00-18:00 | Second wind, creative work |
| After 19:00 | Wind down |

### For Late Chronotypes

| Time | Best Activities |
|------|-----------------|
| 09:00-11:00 | Warm-up, emails, routine |
| 11:00-14:00 | Building momentum |
| 15:00-19:00 | Peak productivity |
| 19:00-22:00 | Creative work, deep focus |
| After 22:00 | Wind down |

---

## Light Exposure

Light is the primary signal for your circadian clock.

### Morning Light

- Get bright light (ideally sunlight) within 30 minutes of waking
- Helps shift clock earlier if needed
- Suppresses melatonin, increases cortisol

### Evening Light

- Reduce bright light 2 hours before bed
- Blue light from screens is especially disruptive
- Use warm/dim lighting

### Light Intensity

| Environment | Lux Level | Effect |
|-------------|-----------|--------|
| Outdoors sunny | 10,000-100,000 | Strong wake signal |
| Outdoors cloudy | 1,000-10,000 | Moderate wake signal |
| Indoor lighting | 100-500 | Weak signal |
| Computer screen | 50-300 | Blue-light concern |
| Candlelight | 10-15 | Minimal disruption |

---

## Mood Factor Integration

Circadian phase contributes to the mood composite through:

1. **Time of Day** - Position in daily alertness curve
2. **Chronotype Alignment** - How well schedule matches preference
3. **Light Exposure** - Recent bright light history
4. **Sleep Timing** - Regularity of sleep schedule

### Circadian Factor Calculation

```python
def circadian_factor(hour: float, chronotype: str = "intermediate") -> float:
    """Calculate alertness factor based on time and chronotype."""
    peak_hours = {"early": 10.0, "intermediate": 11.0, "late": 12.0}
    peak = peak_hours.get(chronotype, 11.0)
    
    # Primary morning peak
    morning = exp(-((hour - peak) ** 2) / 8)
    
    # Secondary evening peak (smaller)
    evening = exp(-((hour - (peak + 8)) ** 2) / 12) * 0.7
    
    # Afternoon dip
    dip = exp(-((hour - 15) ** 2) / 4) * 0.3
    
    return max(0.0, min(1.0, morning + evening - dip))
```

---

## References

- Roenneberg, T. "Internal Time: Chronotypes, Social Jet Lag, and Why You're So Tired" (2012)
- Walker, M. "Why We Sleep" (2017)
- Harvard Medical School Division of Sleep Medicine

---

Last Updated: 2026-01-07
