---
title: "Chinese Astrology Reference"
id: reference-chinese-astrology
type: reference
category: reference
tags: [reference, reference]
difficulty: beginner
last_updated: 2026-01-29
---

# Chinese Astrology Reference

**Category:** Reference  
**Tags:** astrology, chinese, animals, elements, cycles  
**Difficulty:** Beginner

---

## Overview

Chinese astrology is based on a 60-year cycle combining 12 zodiac animals with 5 elements. Unlike Western astrology which uses birth month, Chinese astrology primarily uses birth year.

---

## The 12 Animals

Each animal represents personality traits and has compatibility relationships with others.

### Animal Cycle

The animals follow a fixed 12-year cycle:

| Order | Animal | Chinese | Years (Recent) | Traits |
|-------|--------|---------|----------------|--------|
| 1 | Rat | 鼠 | 2020, 2032 | Clever, resourceful, quick-witted |
| 2 | Ox | 牛 | 2021, 2033 | Dependable, methodical, patient |
| 3 | Tiger | 虎 | 2022, 2034 | Brave, confident, competitive |
| 4 | Rabbit | 兔 | 2023, 2035 | Gentle, elegant, compassionate |
| 5 | Dragon | 龙 | 2024, 2036 | Ambitious, energetic, charismatic |
| 6 | Snake | 蛇 | 2025, 2037 | Wise, intuitive, sophisticated |
| 7 | Horse | 马 | 2026, 2038 | Active, animated, free-spirited |
| 8 | Goat | 羊 | 2027, 2039 | Calm, gentle, sympathetic |
| 9 | Monkey | 猴 | 2028, 2040 | Sharp, curious, playful |
| 10 | Rooster | 鸡 | 2029, 2041 | Observant, hardworking, confident |
| 11 | Dog | 狗 | 2030, 2042 | Loyal, honest, prudent |
| 12 | Pig | 猪 | 2031, 2043 | Compassionate, generous, diligent |

### Calculating Animal Year

```python
def chinese_animal(year: int) -> str:
    animals = [
        "rat", "ox", "tiger", "rabbit", "dragon", "snake",
        "horse", "goat", "monkey", "rooster", "dog", "pig"
    ]
    return animals[(year - 4) % 12]
```

Note: Chinese New Year falls between January 21 and February 20. For precise calculation, check if the date is before or after Chinese New Year.

---

## The 5 Elements

Elements add another dimension to animal signs, creating the 60-year cycle.

| Element | Chinese | Yin/Yang | Associations |
|---------|---------|----------|--------------|
| Wood | 木 | Yang | Growth, creativity, expansion |
| Fire | 火 | Yin | Passion, energy, transformation |
| Earth | 土 | Yang | Stability, grounding, nurturing |
| Metal | 金 | Yin | Strength, determination, focus |
| Water | 水 | Yang | Wisdom, flexibility, intuition |

### Element Cycle

Each element governs two consecutive years:

```
Wood Rat (2024) → Wood Ox (2025)
Fire Tiger (2026) → Fire Rabbit (2027)
Earth Dragon (2028) → Earth Snake (2029)
Metal Horse (2030) → Metal Goat (2031)
Water Monkey (2032) → Water Rooster (2033)
```

### Calculating Element

```python
def chinese_element(year: int) -> str:
    elements = ["wood", "fire", "earth", "metal", "water"]
    return elements[((year - 4) % 10) // 2]
```

---

## Compatibility Triangles

Animals are grouped into four compatibility triangles:

### Trine Groups (Most Compatible)

| Group | Animals | Shared Traits |
|-------|---------|---------------|
| 1 | Rat, Dragon, Monkey | Action-oriented, innovative |
| 2 | Ox, Snake, Rooster | Determined, methodical |
| 3 | Tiger, Horse, Dog | Idealistic, independent |
| 4 | Rabbit, Goat, Pig | Peaceful, artistic |

### Opposing Signs (Challenging)

Animals 6 positions apart can clash:

- Rat ↔ Horse
- Ox ↔ Goat
- Tiger ↔ Monkey
- Rabbit ↔ Rooster
- Dragon ↔ Dog
- Snake ↔ Pig

---

## Mood Factor Integration

Chinese astrology contributes to mood factors through:

1. **Year Element Compatibility** - Current year element vs birth year element
2. **Animal Cycle Position** - Where current year falls relative to birth animal
3. **Elemental Balance** - Wood feeds Fire feeds Earth feeds Metal feeds Water

### Element Interaction

| Interaction | Example | Effect |
|-------------|---------|--------|
| Generating | Wood → Fire | Supportive (+) |
| Controlling | Water → Fire | Challenging (-) |
| Same | Fire → Fire | Neutral (=) |

```python
def element_compatibility(birth_element: str, current_element: str) -> float:
    generating = {
        "wood": "fire", "fire": "earth", "earth": "metal",
        "metal": "water", "water": "wood"
    }
    controlling = {
        "wood": "earth", "earth": "water", "water": "fire",
        "fire": "metal", "metal": "wood"
    }
    
    if generating.get(birth_element) == current_element:
        return 0.7  # Birth element generates current (supportive)
    elif generating.get(current_element) == birth_element:
        return 0.6  # Current generates birth (receiving)
    elif controlling.get(birth_element) == current_element:
        return 0.3  # Birth controls current (draining)
    elif controlling.get(current_element) == birth_element:
        return 0.4  # Current controls birth (challenging)
    else:
        return 0.5  # Neutral
```

---

## 2026: Year of the Fire Horse

The current year (2026) is the Year of the Fire Horse:

- **Animal:** Horse (active, free-spirited)
- **Element:** Fire (passion, energy)
- **Combined:** High energy year, favoring action and change

Best compatibility with:
- Tiger and Dog (trine group)
- Goat (natural ally)

Challenging for:
- Rat (opposing sign)
- Ox (adjacent clash)

---

## References

- Fung, Angela. "The Handbook of Chinese Horoscopes" (2010)
- Helmer Aslaksen. "The Mathematics of the Chinese Calendar"
- Hong Kong Observatory Chinese Calendar

---

Last Updated: 2026-01-07
