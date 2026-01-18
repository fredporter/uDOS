# Mood Factors System - Technical Specification

**Version:** 3.0.0 (Planned)  
**Status:** Design Phase  
**Author:** uDOS Core Team  
**Created:** 2026-01-07

---

## Overview

A scientific, multi-factor mood influence system that combines celestial mechanics, behavioral analysis, and temporal patterns into a unified mathematical model. The system is designed to be:

- **Mathematical** - All factors normalized to 0.0-1.0 scale with weighted influences
- **Privacy-first** - Sensitive data hashed, local-only storage
- **Offline-capable** - No internet required for calculations
- **Extensible** - New factors can be added without breaking existing calculations

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MOOD COMPOSITE SCORE                         │
│                         (0.0 - 1.0 scale)                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  CELESTIAL  │  │  TEMPORAL   │  │ BEHAVIORAL  │  │ BIOLOGICAL │ │
│  │   FACTORS   │  │   FACTORS   │  │   FACTORS   │  │  FACTORS   │ │
│  │   (0.25)    │  │   (0.25)    │  │   (0.30)    │  │   (0.20)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Factor Categories

### 1. CELESTIAL FACTORS (Weight: 0.25)

Astronomical and astrological influences based on actual celestial mechanics.

| Factor | Weight | Source | Description |
|--------|--------|--------|-------------|
| `lunar_phase` | 0.30 | Calculated | Moon phase (synodic cycle ~29.53 days) |
| `lunar_distance` | 0.15 | Calculated | Moon perigee/apogee (tidal influence) |
| `solar_position` | 0.20 | Calculated | Season, day length, solar declination |
| `planetary_hours` | 0.10 | Calculated | Traditional planetary hour system |
| `zodiac_transit` | 0.15 | Birth data | Sun sign compatibility with transits |
| `chinese_element` | 0.10 | Birth data | Year element cycle influence |

#### Lunar Phase Calculation

```python
# Synodic month: 29.53059 days
# Reference: Known new moon (Jan 6, 2000, 18:14 UTC)
def lunar_phase_factor(timestamp: datetime) -> float:
    """Returns 0.0-1.0 based on lunar cycle position."""
    days_since_ref = (timestamp - REFERENCE_NEW_MOON).total_seconds() / 86400
    phase_position = (days_since_ref % 29.53059) / 29.53059
    
    # Full moon (0.5) = peak, New moon (0.0/1.0) = trough
    return 0.5 + 0.5 * math.cos(2 * math.pi * (phase_position - 0.5))
```

#### Lunar Distance (Tidal) Calculation

```python
# Anomalistic month: 27.55455 days (perigee to perigee)
# Perigee = closer = stronger tidal pull = higher factor
def lunar_distance_factor(timestamp: datetime) -> float:
    """Returns 0.0-1.0 based on moon distance (tidal influence)."""
    days_since_perigee = (timestamp - REFERENCE_PERIGEE).total_seconds() / 86400
    position = (days_since_perigee % 27.55455) / 27.55455
    
    # Perigee (0.0) = closest = 1.0, Apogee (0.5) = furthest = 0.0
    return 0.5 + 0.5 * math.cos(2 * math.pi * position)
```

#### Chinese Zodiac System

| Animal | Years | Element Cycle | Yin/Yang |
|--------|-------|---------------|----------|
| Rat | ...2020, 2032 | Wood→Fire→Earth→Metal→Water | Yang |
| Ox | ...2021, 2033 | (60-year cycle) | Yin |
| Tiger | ...2022, 2034 | | Yang |
| ... | | | |

```python
CHINESE_ANIMALS = [
    "rat", "ox", "tiger", "rabbit", "dragon", "snake",
    "horse", "goat", "monkey", "rooster", "dog", "pig"
]
CHINESE_ELEMENTS = ["wood", "fire", "earth", "metal", "water"]

def chinese_zodiac(year: int) -> tuple[str, str]:
    """Returns (animal, element) for a given year."""
    animal = CHINESE_ANIMALS[(year - 4) % 12]
    element = CHINESE_ELEMENTS[((year - 4) % 60) // 12]
    return animal, element
```

---

### 2. TEMPORAL FACTORS (Weight: 0.25)

Time-based influences derived from circadian rhythms and calendar patterns.

| Factor | Weight | Source | Description |
|--------|--------|--------|-------------|
| `circadian_phase` | 0.35 | Time of day | Biological clock alignment |
| `ultradian_rhythm` | 0.15 | 90-min cycles | BRAC (Basic Rest-Activity Cycle) |
| `day_of_week` | 0.15 | Calendar | Weekday vs weekend patterns |
| `season_factor` | 0.20 | Solar declination | Light exposure duration |
| `numerology_day` | 0.15 | Date calculation | Day number resonance |

#### Circadian Phase Model

```python
def circadian_factor(hour: float, chronotype: str = "intermediate") -> float:
    """
    Model circadian alertness based on time of day and chronotype.
    
    Chronotypes:
    - "early" (lark): Peak 09:00-11:00, trough 15:00
    - "intermediate": Peak 10:00-12:00, trough 15:00
    - "late" (owl): Peak 11:00-13:00, trough 09:00
    """
    peak_hours = {"early": 10.0, "intermediate": 11.0, "late": 12.0}
    peak = peak_hours.get(chronotype, 11.0)
    
    # Bimodal distribution with afternoon dip
    morning_component = math.exp(-((hour - peak) ** 2) / 8)
    evening_component = math.exp(-((hour - (peak + 8)) ** 2) / 12) * 0.7
    afternoon_dip = math.exp(-((hour - 15) ** 2) / 4) * 0.3
    
    return max(0, min(1, morning_component + evening_component - afternoon_dip))
```

#### Numerology Day Number

```python
def numerology_day_number(date: date) -> int:
    """Reduce date to single digit (1-9) or master number (11, 22, 33)."""
    total = date.day + date.month + sum(int(d) for d in str(date.year))
    while total > 9 and total not in (11, 22, 33):
        total = sum(int(d) for d in str(total))
    return total

def numerology_factor(day_number: int, personal_number: int) -> float:
    """Calculate resonance between day number and personal number."""
    if day_number == personal_number:
        return 1.0  # Perfect resonance
    elif day_number in get_compatible_numbers(personal_number):
        return 0.7  # Compatible
    else:
        return 0.4  # Neutral
```

---

### 3. BEHAVIORAL FACTORS (Weight: 0.30)

Real-time analysis of user interaction patterns.

| Factor | Weight | Source | Description |
|--------|--------|--------|-------------|
| `typing_speed` | 0.20 | Input analysis | WPM relative to baseline |
| `typing_rhythm` | 0.15 | Keystroke timing | Consistency of intervals |
| `prompt_frequency` | 0.20 | Session tracking | Commands per time unit |
| `prompt_complexity` | 0.15 | Command analysis | Simple vs complex commands |
| `error_rate` | 0.15 | Input analysis | Typos, corrections, retries |
| `session_duration` | 0.15 | Time tracking | Focus duration patterns |

#### Typing Speed Analysis

```python
@dataclass
class TypingMetrics:
    """Collected typing behavior metrics."""
    chars_per_minute: float = 0.0
    inter_key_interval_mean: float = 0.0  # ms
    inter_key_interval_std: float = 0.0   # ms
    pause_frequency: float = 0.0          # pauses > 2s per minute
    backspace_ratio: float = 0.0          # corrections / total keys

def typing_speed_factor(current_cpm: float, baseline_cpm: float) -> float:
    """
    Compare current typing speed to user's baseline.
    
    Returns:
    - > 0.5: Faster than usual (possibly energized or rushing)
    - = 0.5: Normal pace
    - < 0.5: Slower than usual (possibly fatigued or thoughtful)
    """
    ratio = current_cpm / baseline_cpm if baseline_cpm > 0 else 1.0
    return max(0.0, min(1.0, 0.5 + (ratio - 1.0) * 0.5))
```

#### Prompt Complexity Scoring

```python
COMMAND_COMPLEXITY = {
    # Simple (0.2)
    "STATUS": 0.2, "HELP": 0.2, "TIME": 0.2, "CLEAR": 0.2,
    # Medium (0.5)
    "GUIDE": 0.5, "SEARCH": 0.5, "LIST": 0.5, "WELLBEING": 0.5,
    # Complex (0.8)
    "MAKE": 0.8, "BUNDLE": 0.8, "MISSION": 0.8, "AI": 0.8,
    # High (1.0)
    "DEV": 1.0, "REPAIR": 1.0, "SHAKEDOWN": 1.0,
}

def prompt_complexity_factor(commands: list[str], window_minutes: int = 30) -> float:
    """Average complexity of recent commands."""
    if not commands:
        return 0.5
    scores = [COMMAND_COMPLEXITY.get(cmd.upper(), 0.5) for cmd in commands]
    return sum(scores) / len(scores)
```

---

### 4. BIOLOGICAL FACTORS (Weight: 0.20)

Inferred biological state based on available data.

| Factor | Weight | Source | Description |
|--------|--------|--------|-------------|
| `self_reported_energy` | 0.40 | User input | WELLBEING ENERGY command |
| `self_reported_mood` | 0.30 | User input | WELLBEING MOOD command |
| `activity_inference` | 0.15 | Behavior | Inferred from patterns |
| `break_recency` | 0.15 | Session tracking | Time since last break |

---

## Composite Calculation

```python
@dataclass
class MoodFactorResult:
    """Result of mood factor calculation."""
    factor_name: str
    raw_value: float      # 0.0 - 1.0
    weight: float         # Category weight
    sub_weight: float     # Factor weight within category
    contribution: float   # raw_value * weight * sub_weight
    confidence: float     # Data quality (0.0 - 1.0)

class MoodComposite:
    """Calculate composite mood score from all factors."""
    
    CATEGORY_WEIGHTS = {
        "celestial": 0.25,
        "temporal": 0.25,
        "behavioral": 0.30,
        "biological": 0.20,
    }
    
    def calculate(self) -> tuple[float, list[MoodFactorResult]]:
        """
        Calculate composite mood score.
        
        Returns:
            Tuple of (composite_score, list of factor results)
        """
        results = []
        total_contribution = 0.0
        total_weight = 0.0
        
        for category, cat_weight in self.CATEGORY_WEIGHTS.items():
            factors = self._calculate_category(category)
            for factor in factors:
                factor.contribution = factor.raw_value * cat_weight * factor.sub_weight
                total_contribution += factor.contribution * factor.confidence
                total_weight += cat_weight * factor.sub_weight * factor.confidence
                results.append(factor)
        
        composite = total_contribution / total_weight if total_weight > 0 else 0.5
        return composite, results
```

---

## Secure User Data Handling

### Sensitive Data Classification

| Data Type | Sensitivity | Storage | Hashing |
|-----------|-------------|---------|---------|
| Birth date | HIGH | Encrypted | SHA-256 in logs |
| Birth time | HIGH | Encrypted | SHA-256 in logs |
| Birth place | HIGH | Encrypted | SHA-256 in logs |
| Zodiac sign | LOW | Plain | Not required |
| Typing patterns | MEDIUM | Local only | Rolling averages |
| Session history | MEDIUM | Local only | Anonymized |

### Data Storage Schema

```python
# memory/private/identity.enc (encrypted)
{
    "birth_date": "1990-03-15",      # Full date for calculations
    "birth_time": "14:30",           # Optional, for precise charts
    "birth_place": {                 # Optional, for location-based
        "lat": 51.5074,
        "lon": -0.1278,
        "tz": "Europe/London"
    },
    "chronotype": "intermediate",    # early/intermediate/late
    "created": "2026-01-07T...",
    "updated": "2026-01-07T..."
}

# memory/private/wellbeing/state.json (plain, derived data only)
{
    "zodiac_western": "pisces",      # Derived, not sensitive
    "zodiac_chinese": "horse",       # Derived, not sensitive
    "chinese_element": "metal",      # Derived, not sensitive
    "personal_number": 7,            # Numerology, derived
    "last_mood_score": 0.65,
    "typing_baseline_cpm": 280,
    "updated": "2026-01-07T..."
}
```

### Log Hashing

```python
import hashlib
from datetime import date

def hash_sensitive(value: str, salt: str = "") -> str:
    """One-way hash for logging sensitive data."""
    combined = f"{value}{salt}{date.today().isoformat()}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

# In logs:
# [LOCAL] Birth data updated for user [hash:a1b2c3d4e5f6g7h8]
# [LOCAL] Mood calculated: 0.65 (celestial: 0.58, temporal: 0.72)
# Never: [LOCAL] Birth date set to 1990-03-15
```

---

## API Surface

### New Commands

```bash
# Identity setup (encrypted storage)
WELLBEING IDENTITY              # Show derived data (zodiac, etc.)
WELLBEING IDENTITY SETUP        # Guided setup with encryption
WELLBEING IDENTITY CLEAR        # Remove all birth data

# Factor analysis
WELLBEING FACTORS               # Show all current factors
WELLBEING FACTORS celestial     # Show celestial factors only
WELLBEING FACTORS --verbose     # Detailed calculation breakdown

# Composite mood
WELLBEING SCORE                 # Current composite score
WELLBEING SCORE --history       # Score over time (graph)
```

### Service API

```python
class MoodFactorService:
    """Main service for mood factor calculations."""
    
    def get_composite_score(self) -> float:
        """Get current composite mood score (0.0-1.0)."""
        
    def get_factor_breakdown(self) -> list[MoodFactorResult]:
        """Get detailed breakdown of all factors."""
        
    def get_category_scores(self) -> dict[str, float]:
        """Get scores by category."""
        
    def record_behavior(self, event: BehaviorEvent) -> None:
        """Record a behavioral event for analysis."""
        
    def set_identity(self, birth_date: date, ...) -> None:
        """Set identity data (encrypted storage)."""
```

---

## Knowledge Articles Required

The following articles should be added to the knowledge bank:

1. `knowledge/reference/celestial-mechanics.md` - Lunar cycles, solar position
2. `knowledge/reference/circadian-rhythms.md` - Biological clock science
3. `knowledge/reference/western-astrology.md` - Zodiac system reference
4. `knowledge/reference/chinese-astrology.md` - Animal years, elements
5. `knowledge/reference/numerology-basics.md` - Number systems
6. `knowledge/well-being/mood-factors.md` - How the system works
7. `knowledge/well-being/chronotypes.md` - Early bird vs night owl
8. `knowledge/well-being/ultradian-rhythms.md` - 90-minute cycles

---

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Encrypted identity storage
- [ ] Log hashing utilities
- [ ] Factor calculation framework
- [ ] Composite score calculator

### Phase 2: Celestial Factors
- [ ] Lunar phase calculation
- [ ] Lunar distance (tidal) calculation
- [ ] Solar position / season
- [ ] Planetary hours
- [ ] Chinese zodiac integration

### Phase 3: Temporal Factors
- [ ] Circadian model
- [ ] Ultradian rhythm tracking
- [ ] Numerology calculations
- [ ] Season awareness

### Phase 4: Behavioral Analysis
- [ ] Typing metrics collection
- [ ] Prompt frequency tracking
- [ ] Command complexity analysis
- [ ] Session pattern recognition

### Phase 5: Knowledge Base
- [ ] Create reference articles
- [ ] Add wellbeing articles
- [ ] Cross-reference linking

---

## References

- Lunar calculations: Jean Meeus, "Astronomical Algorithms"
- Circadian rhythms: Roenneberg et al., "Epidemiology of the human circadian clock"
- Typing patterns: Epp et al., "Identifying emotional states using keystroke dynamics"
- Chinese calendar: Helmer Aslaksen, "The Mathematics of the Chinese Calendar"

---

*Last Updated: 2026-01-07*
