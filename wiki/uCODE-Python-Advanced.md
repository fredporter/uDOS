# uCODE Python Advanced Features (v1.2.24)

**Level:** Advanced  
**Focus:** Full Python programming in uCODE  
**Last Updated:** December 13, 2025

---

## Overview

With v1.2.24's Python-first architecture, you have access to **the entire Python ecosystem** while writing uCODE scripts. This guide covers advanced programming features beyond basic commands.

**Prerequisites:**
- Comfortable with [uCODE Beginner Commands](uCODE-Beginner-Commands.md)
- Basic Python knowledge (variables, if/else, loops)
- Understanding of [Python-First Guide](uCODE-Python-First-Guide.md)

---

## Transition from UPPERCASE to Lowercase

### Beginner Level: UPPERCASE uCODE

```python
# Beginner syntax - UPPERCASE for visual consistency with uCODE
PRINT[Hello, world!]
IF GET[$player-hp] < 50 THEN HEAL*SPRITE[player|30|medkit]
FUNCTION[@daily*check]
```

### Intermediate Level: Mixed Syntax

```python
# Intermediate - Mix UPPERCASE uCODE with lowercase Python
from udos_core import *

player_hp = get_var("player-hp", 100)
if player_hp < 50:
    HEAL*SPRITE("player", 30, "medkit")  # uCODE command
```

### Advanced Level: Pure Lowercase Python

**From this point forward, this guide uses standard lowercase Python syntax.**

```python
# Advanced - Pure Python with uCODE as imported functions
from udos_core import guide, heal_sprite, checkpoint_save

player_hp = 100

if player_hp < 50:
    heal_sprite("player", 30, "medkit")
    guide("medical/wounds", "detailed")
    checkpoint_save("emergency-heal")
```

---

## Python Control Flow

### Conditionals (if/elif/else)

```python
from udos_core import *

# Get player status
player_hp = get_var("player-hp", 100)
player_level = get_var("player-level", 1)

# Complex conditional logic
if player_hp < 20:
    print("CRITICAL: Health very low!")
    heal_sprite("player", 50, "emergency-kit")
    guide("medical/wounds", "detailed")
elif player_hp < 50:
    print("WARNING: Health low")
    heal_sprite("player", 20, "bandage")
elif player_hp < 80:
    print("Health moderate")
else:
    print("Health excellent")

# Nested conditionals
if player_level > 5:
    if player_hp > 80:
        print("Ready for advanced missions!")
    else:
        print("Level high but health low - rest first")
```

### Ternary Operator

```python
# Concise conditional assignment
status = "healthy" if player_hp > 80 else "injured"
print(f"Status: {status}")

# Nested ternary
priority = "critical" if hp < 20 else "urgent" if hp < 50 else "normal"

# With function calls
action = heal_sprite("player", 50, "medkit") if hp < 30 else print("No healing needed")
```

### Loops

#### For Loops

```python
# Iterate over inventory
inventory = ["axe", "rope", "knife", "water-filter"]

for item in inventory:
    print(f"Checking {item}...")
    if item == "water-filter":
        print("Essential item found!")

# Loop with index
for i, item in enumerate(inventory, 1):
    print(f"{i}. {item}")

# Loop over range
for day in range(1, 8):  # Days 1-7
    print(f"Day {day} survival log")
    water_consumed = 5
    set_var(f"water-day-{day}", water_consumed)

# Loop over dictionary
resources = {"water": 50, "food": 30, "wood": 20}
for resource, amount in resources.items():
    print(f"{resource}: {amount}")
    if amount < 25:
        print(f"  ⚠️ {resource} running low!")
```

#### While Loops

```python
# Monitor water level
water_level = get_var("water-level", 100)
daily_consumption = 5

days_survived = 0
while water_level > 0:
    water_level -= daily_consumption
    days_survived += 1
    print(f"Day {days_survived}: Water at {water_level}L")
    
    if water_level < 30:
        print("⚠️ Water critical!")
        guide("water/collection", "detailed")
        break

print(f"Survived {days_survived} days")
```

#### List Comprehensions

```python
# Filter resources below threshold
resources = [100, 45, 23, 67, 15, 89]
low_resources = [r for r in resources if r < 30]
print(f"Low resources: {low_resources}")

# Transform data
inventory = ["axe", "rope", "knife"]
upper_inventory = [item.upper() for item in inventory]

# Conditional comprehension
hp_values = [100, 45, 78, 23, 91]
critical = [hp for hp in hp_values if hp < 30]
healthy = [hp for hp in hp_values if hp >= 80]

# Dictionary comprehension
items = ["axe", "rope", "knife"]
item_counts = {item: inventory.count(item) for item in items}
```

---

## Functions

### Basic Functions

```python
def check_health(sprite_id):
    """Check sprite health and heal if needed."""
    hp = get_var(f"{sprite_id}-hp", 100)
    
    if hp < 30:
        print(f"{sprite_id}: CRITICAL")
        heal_sprite(sprite_id, 50, "emergency-kit")
    elif hp < 60:
        print(f"{sprite_id}: Low")
        heal_sprite(sprite_id, 20, "bandage")
    else:
        print(f"{sprite_id}: Healthy")
    
    return hp

# Call function
player_hp = check_health("player")
companion_hp = check_health("companion")
```

### Functions with Multiple Parameters

```python
def calculate_survival_time(water, food, people=1, climate="temperate"):
    """Calculate days of survival with current resources.
    
    Args:
        water: Water in liters
        food: Food in days worth
        people: Number of people (default 1)
        climate: hot | temperate | cold (default temperate)
    
    Returns:
        Tuple of (water_days, food_days, min_days)
    """
    # Adjust consumption by climate
    water_per_day = {
        "hot": 5,
        "temperate": 3,
        "cold": 2
    }
    
    daily_water = water_per_day[climate] * people
    water_days = water / daily_water
    food_days = food / people
    
    min_days = min(water_days, food_days)
    
    return water_days, food_days, min_days

# Use function
water_days, food_days, survival = calculate_survival_time(100, 30, people=2, climate="hot")
print(f"Water: {water_days:.1f} days")
print(f"Food: {food_days:.1f} days")
print(f"Survival time: {survival:.1f} days")
```

### Functions Returning Multiple Values

```python
def assess_camp_status():
    """Assess all camp resource levels."""
    water = get_var("water-level", 100)
    food = get_var("food-supply", 50)
    wood = get_var("wood-count", 30)
    
    water_ok = water >= 30
    food_ok = food >= 20
    wood_ok = wood >= 15
    
    all_ok = water_ok and food_ok and wood_ok
    
    return water_ok, food_ok, wood_ok, all_ok

# Unpack results
w_ok, f_ok, wd_ok, camp_ok = assess_camp_status()

if camp_ok:
    print("✅ Camp fully stocked")
else:
    print("⚠️ Camp needs supplies")
    if not w_ok:
        guide("water/collection", "simple")
    if not f_ok:
        guide("food/foraging", "simple")
```

### Lambda Functions

```python
# Simple lambda
square = lambda x: x ** 2
print(square(5))  # 25

# Lambda with conditionals
status = lambda hp: "healthy" if hp > 80 else "injured"
print(status(90))  # healthy

# Lambda in sorting
players = [
    {"name": "Alice", "hp": 90},
    {"name": "Bob", "hp": 45},
    {"name": "Charlie", "hp": 75}
]
sorted_players = sorted(players, key=lambda p: p["hp"])

# Lambda in filtering
high_hp = list(filter(lambda p: p["hp"] > 70, players))
```

---

## Classes and Objects

### Basic Classes

```python
class Survivor:
    """Represent a survivor with health, inventory, and skills."""
    
    def __init__(self, name, hp=100):
        """Initialize survivor."""
        self.name = name
        self.hp = hp
        self.max_hp = 100
        self.inventory = []
        self.level = 1
        self.xp = 0
    
    def heal(self, amount):
        """Heal survivor by amount."""
        self.hp = min(self.hp + amount, self.max_hp)
        print(f"{self.name} healed to {self.hp} HP")
    
    def add_item(self, item):
        """Add item to inventory."""
        self.inventory.append(item)
        print(f"{self.name} acquired {item}")
    
    def status(self):
        """Display survivor status."""
        print(f"=== {self.name} ===")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Level: {self.level}")
        print(f"XP: {self.xp}")
        print(f"Items: {len(self.inventory)}")

# Create survivors
player = Survivor("Hero")
companion = Survivor("Buddy", hp=80)

# Use methods
player.heal(20)
player.add_item("axe")
player.status()
```

### Classes with Properties

```python
class ResourceManager:
    """Manage camp resources with thresholds."""
    
    def __init__(self):
        self._water = 100
        self._food = 50
        self.min_water = 30
        self.min_food = 20
    
    @property
    def water(self):
        """Get water level."""
        return self._water
    
    @water.setter
    def water(self, value):
        """Set water level with validation."""
        if value < 0:
            raise ValueError("Water cannot be negative")
        self._water = value
        if value < self.min_water:
            print(f"⚠️ Water low: {value}L")
            guide("water/collection", "detailed")
    
    @property
    def food(self):
        """Get food level."""
        return self._food
    
    @food.setter
    def food(self, value):
        """Set food level with validation."""
        if value < 0:
            raise ValueError("Food cannot be negative")
        self._food = value
        if value < self.min_food:
            print(f"⚠️ Food low: {value} days")
            guide("food/foraging", "detailed")
    
    def consume_daily(self):
        """Consume daily resources."""
        self.water -= 5
        self.food -= 1
        print(f"Daily consumption: {self.water}L water, {self.food} days food")

# Use resource manager
camp = ResourceManager()
camp.water = 25  # Triggers warning
camp.consume_daily()
```

### Inheritance

```python
class Character:
    """Base class for all characters."""
    
    def __init__(self, name, hp=100):
        self.name = name
        self.hp = hp
        self.max_hp = hp
    
    def heal(self, amount):
        """Heal character."""
        self.hp = min(self.hp + amount, self.max_hp)

class Player(Character):
    """Player character with inventory and XP."""
    
    def __init__(self, name, hp=100):
        super().__init__(name, hp)
        self.inventory = []
        self.xp = 0
        self.level = 1
    
    def gain_xp(self, amount):
        """Gain experience points."""
        self.xp += amount
        # Level up every 1000 XP
        new_level = 1 + (self.xp // 1000)
        if new_level > self.level:
            self.level = new_level
            print(f"{self.name} leveled up to {self.level}!")

class Companion(Character):
    """Companion character with loyalty."""
    
    def __init__(self, name, hp=80):
        super().__init__(name, hp)
        self.loyalty = 50
    
    def increase_loyalty(self, amount):
        """Increase companion loyalty."""
        self.loyalty = min(self.loyalty + amount, 100)
        print(f"{self.name} loyalty: {self.loyalty}")

# Create characters
hero = Player("Hero")
buddy = Companion("Buddy")

hero.gain_xp(500)
buddy.increase_loyalty(20)
```

---

## Data Structures

### Lists

```python
# Create and modify lists
inventory = ["axe", "rope", "knife"]
inventory.append("water-filter")
inventory.extend(["bandage", "firestarter"])
inventory.insert(0, "compass")

# Remove items
inventory.remove("rope")
last_item = inventory.pop()
del inventory[0]

# List operations
print(len(inventory))
print("axe" in inventory)
inventory.sort()
inventory.reverse()

# Slicing
first_three = inventory[:3]
last_two = inventory[-2:]
every_other = inventory[::2]
```

### Dictionaries

```python
# Create dictionaries
resources = {
    "water": 100,
    "food": 50,
    "wood": 30
}

# Access and modify
resources["water"] = 95
resources["tools"] = 5

# Dictionary methods
keys = resources.keys()
values = resources.values()
items = resources.items()

# Safe access
water = resources.get("water", 0)
metal = resources.get("metal", 0)  # Returns 0 if not found

# Update multiple values
resources.update({"water": 90, "food": 45})

# Remove items
del resources["wood"]
tools = resources.pop("tools")

# Iterate
for resource, amount in resources.items():
    print(f"{resource}: {amount}")
```

### Sets

```python
# Create sets
required_items = {"axe", "rope", "knife", "water-filter"}
available_items = {"axe", "rope", "bandage", "firestarter"}

# Set operations
missing = required_items - available_items
print(f"Missing: {missing}")

have = required_items & available_items
print(f"Have: {have}")

all_items = required_items | available_items
print(f"All items: {all_items}")

# Add/remove
required_items.add("compass")
required_items.remove("knife")
required_items.discard("hammer")  # Doesn't error if not present
```

### Tuples

```python
# Immutable sequences
location = (33.87, 151.21, 100)  # lat, lon, layer
lat, lon, layer = location  # Unpacking

# Named tuples
from collections import namedtuple

Location = namedtuple("Location", ["lat", "lon", "layer"])
sydney = Location(33.87, 151.21, 100)
print(f"Sydney: {sydney.lat}, {sydney.lon}, layer {sydney.layer}")
```

---

## File Operations

### Reading Files

```python
from pathlib import Path

# Read text file
def load_guide(category, name):
    """Load survival guide content."""
    path = Path(f"knowledge/{category}/{name}.md")
    
    if not path.exists():
        print(f"Guide not found: {path}")
        return None
    
    with path.open() as f:
        content = f.read()
    
    return content

# Use function
water_guide = load_guide("water", "purification")
print(water_guide)
```

### Writing Files

```python
# Write text file
def save_mission_log(mission_id, log_data):
    """Save mission log to file."""
    path = Path(f"memory/logs/missions/{mission_id}.log")
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open("w") as f:
        f.write(log_data)
    
    print(f"Log saved: {path}")

# Use function
log = "Mission started: establish-camp\nLocation: AA340\nStatus: ACTIVE"
save_mission_log("mission-001", log)
```

### JSON Files

```python
import json

# Write JSON
def save_checkpoint(name, data):
    """Save checkpoint data as JSON."""
    path = Path(f"memory/checkpoints/{name}.json")
    
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Checkpoint saved: {name}")

# Read JSON
def load_checkpoint(name):
    """Load checkpoint data from JSON."""
    path = Path(f"memory/checkpoints/{name}.json")
    
    if not path.exists():
        return None
    
    with path.open() as f:
        data = json.load(f)
    
    return data

# Use functions
checkpoint_data = {
    "player_hp": 85,
    "water_level": 50,
    "location": "AA340",
    "timestamp": "2025-12-13T10:30:00"
}
save_checkpoint("camp-established", checkpoint_data)
loaded = load_checkpoint("camp-established")
```

---

## Error Handling

### Try/Except

```python
def safe_heal(sprite_id, amount):
    """Heal sprite with error handling."""
    try:
        hp = get_var(f"{sprite_id}-hp")
        new_hp = hp + amount
        set_var(f"{sprite_id}-hp", new_hp)
        print(f"{sprite_id} healed to {new_hp} HP")
    except ValueError as e:
        print(f"Error healing {sprite_id}: {e}")
        # Set default
        set_var(f"{sprite_id}-hp", 100)
    except Exception as e:
        print(f"Unexpected error: {e}")

# Use function
safe_heal("player", 20)
safe_heal("invalid", 10)  # Handles error gracefully
```

### Multiple Exceptions

```python
def load_resource_file(filename):
    """Load resource configuration with error handling."""
    try:
        with open(filename) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in: {filename}")
        return {}
    except PermissionError:
        print(f"Permission denied: {filename}")
        return {}

# Use function
config = load_resource_file("config.json")
```

### Finally Clause

```python
def update_resource_file(filename, data):
    """Update resource file with cleanup."""
    file_handle = None
    try:
        file_handle = open(filename, "w")
        json.dump(data, file_handle, indent=2)
        print(f"Updated: {filename}")
    except IOError as e:
        print(f"Error writing {filename}: {e}")
    finally:
        if file_handle:
            file_handle.close()
```

### Custom Exceptions

```python
class ResourceDepletedError(Exception):
    """Exception for when a resource is depleted."""
    pass

def consume_resource(resource_name, amount):
    """Consume resource, raise exception if depleted."""
    current = get_var(resource_name, 0)
    
    if current < amount:
        raise ResourceDepletedError(
            f"{resource_name} depleted: need {amount}, have {current}"
        )
    
    new_amount = current - amount
    set_var(resource_name, new_amount)
    return new_amount

# Use with error handling
try:
    remaining = consume_resource("water-level", 10)
    print(f"Water remaining: {remaining}")
except ResourceDepletedError as e:
    print(f"⚠️ {e}")
    guide("water/collection", "detailed")
```

---

## Advanced Patterns

### Decorators

```python
def log_execution(func):
    """Decorator to log function execution."""
    def wrapper(*args, **kwargs):
        print(f"Executing: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Completed: {func.__name__}")
        return result
    return wrapper

@log_execution
def establish_camp(location):
    """Establish camp at location."""
    print(f"Setting up camp at {location}")
    checkpoint_save(f"camp-{location}")
    return True

# Use decorated function
establish_camp("AA340")
```

### Context Managers

```python
from contextlib import contextmanager

@contextmanager
def mission_context(mission_id):
    """Context manager for mission execution."""
    print(f"Starting mission: {mission_id}")
    checkpoint_save(f"mission-{mission_id}-start")
    
    try:
        yield mission_id
    finally:
        print(f"Mission completed: {mission_id}")
        checkpoint_save(f"mission-{mission_id}-complete")

# Use context manager
with mission_context("establish-camp") as mission:
    print(f"Executing {mission}")
    # Mission code here
```

### Generators

```python
def daily_water_consumption(initial_water, daily_use):
    """Generate daily water levels."""
    water = initial_water
    day = 1
    
    while water > 0:
        yield day, water
        water -= daily_use
        day += 1

# Use generator
for day, water in daily_water_consumption(100, 5):
    print(f"Day {day}: {water}L")
    if water < 30:
        print("⚠️ Water running low!")
        break
```

---

## Integration with uCODE Commands

### Wrapping uCODE in Python

```python
from udos_core import *

class SurvivalManager:
    """High-level survival management."""
    
    def __init__(self):
        self.resources = {
            "water": get_var("water-level", 100),
            "food": get_var("food-supply", 50),
            "wood": get_var("wood-count", 30)
        }
    
    def check_all_resources(self):
        """Check all resources and trigger guides if needed."""
        for resource, amount in self.resources.items():
            if amount < 30:
                print(f"⚠️ {resource} low: {amount}")
                
                # Trigger appropriate guide
                if resource == "water":
                    guide("water/collection", "detailed")
                elif resource == "food":
                    guide("food/foraging", "detailed")
                elif resource == "wood":
                    guide("making/fire", "simple")
    
    def save_state(self):
        """Save current state as checkpoint."""
        checkpoint_save("resource-check-complete")
        
        # Update all stored values
        for resource, amount in self.resources.items():
            set_var(f"{resource}-level", amount)

# Use manager
manager = SurvivalManager()
manager.check_all_resources()
manager.save_state()
```

---

## Performance Optimization

### Efficient Loops

```python
# ❌ Slow: Multiple function calls
for i in range(1000):
    result = get_var("counter", 0)
    result += 1
    set_var("counter", result)

# ✅ Fast: Batch operations
counter = get_var("counter", 0)
for i in range(1000):
    counter += 1
set_var("counter", counter)
```

### List Comprehensions vs Loops

```python
# ❌ Slower
squares = []
for x in range(1000):
    squares.append(x ** 2)

# ✅ Faster
squares = [x ** 2 for x in range(1000)]
```

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_water_needs(days, people, climate):
    """Calculate water needs with caching."""
    # Expensive calculation
    base_rate = {"hot": 5, "temperate": 3, "cold": 2}
    return days * people * base_rate[climate]

# First call: calculates
result1 = calculate_water_needs(7, 2, "hot")

# Second call: cached
result2 = calculate_water_needs(7, 2, "hot")  # Instant
```

---

## Testing

### Unit Tests

```python
import unittest

class TestSurvivalFunctions(unittest.TestCase):
    """Test survival management functions."""
    
    def test_calculate_survival_time(self):
        """Test survival time calculation."""
        water_days, food_days, min_days = calculate_survival_time(
            water=100,
            food=30,
            people=2,
            climate="hot"
        )
        
        self.assertEqual(water_days, 10.0)
        self.assertEqual(food_days, 15.0)
        self.assertEqual(min_days, 10.0)
    
    def test_heal_function(self):
        """Test healing function."""
        survivor = Survivor("Test", hp=50)
        survivor.heal(30)
        self.assertEqual(survivor.hp, 80)
        
        # Test max HP cap
        survivor.heal(50)
        self.assertEqual(survivor.hp, 100)

if __name__ == "__main__":
    unittest.main()
```

---

## Best Practices Summary

### 1. Use Type Hints

```python
def calculate_days(water: float, consumption: float) -> float:
    """Calculate days of water supply."""
    return water / consumption
```

### 2. Document Everything

```python
def complex_function(param1, param2):
    """
    One-line summary.
    
    Longer description explaining what the function does,
    how it works, and any important details.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is negative
    """
    pass
```

### 3. Follow PEP 8

```python
# Good variable names
player_health = 100
water_collection_rate = 5

# Good function names
def check_resource_levels():
    pass

# Good class names
class ResourceManager:
    pass
```

### 4. Handle Errors

```python
# Always use try/except for risky operations
try:
    result = risky_operation()
except SpecificError as e:
    handle_error(e)
```

---

## Next Steps

You now have the full Python ecosystem at your disposal:

1. **Build Complex Systems** - Create sophisticated survival simulations
2. **Integrate Libraries** - Use numpy, pandas, matplotlib, etc.
3. **Create Extensions** - Build uDOS extensions in Python
4. **Contribute** - Share your advanced scripts with the community

---

## Reference

- **Beginner:** [uCODE Beginner Commands](uCODE-Beginner-Commands.md)
- **Intermediate:** [uCODE Python-First Guide](uCODE-Python-First-Guide.md)
- **Quick Lookup:** [uCODE Quick Reference](uCODE-Quick-Reference.md)
- **Python Docs:** https://docs.python.org/3/

---

**Level:** Advanced  
**Prerequisites:** [Python-First Guide](uCODE-Python-First-Guide.md)  
**Version:** v1.2.24
