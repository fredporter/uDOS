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

## Python Control Flow

### Conditionals (if/elif/else)

```python
from udos_core import *

# Get player status
player_hp = get_var("player-hp", 100)
player_level = get_var("player-level", 1)

# Complex conditional logic
if player_hp < 20:
    PRINT["CRITICAL: Health very low!"]
    HEAL_SPRITE["player"|"50"|"emergency-kit"]
    GUIDE["medical/wounds"|"detailed"]
elif player_hp < 50:
    PRINT["WARNING: Health low"]
    HEAL_SPRITE["player"|"20"|"bandage"]
elif player_hp < 80:
    PRINT["Health moderate"]
else:
    PRINT["Health excellent"]

# Nested conditionals
if player_level > 5:
    if player_hp > 80:
        PRINT["Ready for advanced missions!"]
    else:
        PRINT["Level high but health low - rest first"]
```

### Ternary Operator

```python
# Concise conditional assignment
status = "healthy" if player_hp > 80 else "injured"
PRINT[f"Status: {status}"]

# Nested ternary
priority = "critical" if hp < 20 else "urgent" if hp < 50 else "normal"

# With function calls
action = HEAL_SPRITE["player"|"50"|"medkit"] if hp < 30 else PRINT["No healing needed"]
```

### Loops

#### For Loops

```python
# Iterate over inventory
inventory = ["axe", "rope", "knife", "water-filter"]

for item in inventory:
    PRINT[f"Checking {item}..."]
    if item == "water-filter":
        PRINT["Essential item found!"]

# Loop with index
for i, item in enumerate(inventory, 1):
    PRINT[f"{i}. {item}"]

# Loop over range
for day in range(1, 8):  # Days 1-7
    PRINT[f"Day {day} survival log"]
    water_consumed = 5
    set_var(f"water-day-{day}", water_consumed)

# Loop over dictionary
resources = {"water": 50, "food": 30, "wood": 20}
for resource, amount in resources.items():
    PRINT[f"{resource}: {amount}"]
    if amount < 25:
        PRINT[f"  ⚠ {resource} running low!"]
```

#### While Loops

```python
# Monitor water level
water = get_var("water-level", 100)

while water > 0:
    PRINT[f"Water: {water} liters"]
    
    # Daily consumption
    water -= 5
    
    if water < 30:
        PRINT["Warning: Water low!"]
        GUIDE["water/collection"|"quick"]
        break
    
    set_var("water-level", water)

# Infinite loop with break
checkpoint_count = 0
while True:
    checkpoint_count += 1
    CHECKPOINT_SAVE[f"auto-{checkpoint_count}"]
    
    if checkpoint_count >= 10:
        break  # Stop after 10 checkpoints
```

#### Loop Control

```python
# Continue - skip to next iteration
for item in inventory:
    if item == "broken-tool":
        continue  # Skip broken items
    PRINT[f"Using {item}"]

# Break - exit loop early
for location in search_area:
    if check_water_source(location):
        PRINT[f"Water found at {location}!"]
        break  # Stop searching

# Else clause (runs if loop completes without break)
for item in inventory:
    if item == "water-filter":
        PRINT["Filter found!"]
        break
else:
    PRINT["No filter - need to find one"]
    GUIDE["water/filtration"|"detailed"]
```

---

## Functions

### Basic Functions

```python
def check_resources():
    """Check all resource levels."""
    water = get_var("water-level", 100)
    food = get_var("food-supply", 50)
    wood = get_var("wood-count", 30)
    
    PRINT[f"Water: {water} | Food: {food} | Wood: {wood}"]
    return water, food, wood

# Call function
w, f, wd = check_resources()
```

### Functions with Parameters

```python
def heal_player(amount, item_name):
    """Heal player by specified amount."""
    current_hp = get_var("player-hp", 100)
    max_hp = get_var("player-max-hp", 100)
    
    new_hp = min(current_hp + amount, max_hp)  # Cap at max
    set_var("player-hp", new_hp)
    
    HEAL_SPRITE["player"|str(amount)|item_name]
    PRINT[f"Healed {amount} HP using {item_name}"]
    
    return new_hp

# Usage
heal_player(30, "bandage")
heal_player(50, "medkit")
```

### Default Parameters

```python
def guide_lookup(topic, complexity="detailed"):
    """Look up survival guide with default complexity."""
    GUIDE[f"{topic}"|complexity]
    PRINT[f"Showing {complexity} guide for {topic}"]

# Use default
guide_lookup("water/purification")  # Uses "detailed"

# Override default
guide_lookup("fire/bow-drill", "simple")
```

### Keyword Arguments

```python
def create_checkpoint(name, save_inventory=True, save_location=True):
    """Create checkpoint with optional data."""
    CHECKPOINT_SAVE[name]
    
    if save_inventory:
        inv = get_var("inventory", "[]")
        set_var(f"checkpoint-{name}-inventory", inv)
    
    if save_location:
        loc = get_var("current-location", "unknown")
        set_var(f"checkpoint-{name}-location", loc)
    
    PRINT[f"Checkpoint '{name}' saved"]

# Various calling styles
create_checkpoint("camp-setup")
create_checkpoint("pre-storm", save_inventory=False)
create_checkpoint("exploration", save_location=True, save_inventory=True)
```

### Return Values

```python
def calculate_days_remaining(water, daily_use):
    """Calculate how many days water will last."""
    if daily_use == 0:
        return float('inf')  # Infinite days if no use
    
    days = water / daily_use
    return int(days)

# Use return value
water_level = get_var("water-level", 50)
days = calculate_days_remaining(water_level, 5)
PRINT[f"Water will last {days} days"]

if days < 3:
    PRINT["Need to collect water soon!"]
    GUIDE["water/collection"|"quick"]
```

### Lambda Functions

```python
# Simple anonymous functions
square = lambda x: x ** 2
PRINT[f"5 squared: {square(5)}"]

# Use with sort
resources = [
    {"name": "water", "amount": 50},
    {"name": "food", "amount": 30},
    {"name": "wood", "amount": 70}
]

# Sort by amount
sorted_resources = sorted(resources, key=lambda x: x["amount"])
for res in sorted_resources:
    PRINT[f"{res['name']}: {res['amount']}"]

# Filter with lambda
low_resources = list(filter(lambda x: x["amount"] < 40, resources))
```

---

## List Comprehensions

### Basic Comprehensions

```python
# Create list from range
squares = [x**2 for x in range(10)]
PRINT[f"Squares: {squares}"]

# Transform existing list
items = ["axe", "rope", "knife"]
upper_items = [item.upper() for item in items]

# With condition
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Multiple conditions
valid_resources = [r for r in resources if r > 0 and r < 100]
```

### Nested Comprehensions

```python
# 2D grid
grid = [[f"{x},{y}" for x in range(3)] for y in range(3)]
for row in grid:
    PRINT[str(row)]

# Flatten nested list
nested = [[1, 2], [3, 4], [5, 6]]
flat = [item for sublist in nested for item in sublist]
PRINT[f"Flattened: {flat}"]
```

### Dictionary Comprehensions

```python
# Create dictionary from lists
keys = ["water", "food", "wood"]
values = [50, 30, 20]
resources_dict = {k: v for k, v in zip(keys, values)}

# Transform dictionary
doubled = {k: v*2 for k, v in resources_dict.items()}

# Filter dictionary
low_resources = {k: v for k, v in resources_dict.items() if v < 40}

# Swap keys and values
swapped = {v: k for k, v in resources_dict.items()}
```

### Set Comprehensions

```python
# Unique values
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = {x for x in numbers}

# Transform to set
items = ["axe", "rope", "axe", "knife"]
unique_items = {item.lower() for item in items}
```

---

## Data Structures

### Lists

```python
# Creation
inventory = []
inventory = ["axe", "rope", "knife"]
inventory = list(range(10))

# Adding items
inventory.append("water-filter")
inventory.extend(["compass", "map"])
inventory.insert(0, "priority-item")  # Add at index 0

# Removing items
inventory.remove("axe")  # Remove by value
item = inventory.pop()  # Remove and return last item
item = inventory.pop(0)  # Remove and return at index
inventory.clear()  # Remove all

# Accessing
first = inventory[0]
last = inventory[-1]
middle = inventory[len(inventory)//2]

# Slicing
first_three = inventory[:3]
last_two = inventory[-2:]
every_other = inventory[::2]
reversed_list = inventory[::-1]

# Searching
if "axe" in inventory:
    PRINT["Have axe"]

index = inventory.index("rope")  # Find index
count = inventory.count("axe")  # Count occurrences

# Sorting
inventory.sort()  # In-place sort
sorted_inv = sorted(inventory)  # Return new sorted list
inventory.sort(reverse=True)  # Descending

# List operations
combined = inventory1 + inventory2
repeated = inventory * 3
length = len(inventory)
```

### Dictionaries

```python
# Creation
player = {}
player = {"name": "Hero", "hp": 100, "level": 5}
player = dict(name="Hero", hp=100, level=5)

# Accessing
name = player["name"]
hp = player.get("hp", 100)  # With default
level = player.get("level")

# Adding/updating
player["xp"] = 450
player.update({"gold": 50, "items": 10})

# Removing
del player["gold"]
xp = player.pop("xp", 0)  # Remove and return with default

# Checking
if "hp" in player:
    PRINT[f"HP: {player['hp']}"]

# Iterating
for key in player:
    PRINT[f"{key}: {player[key]}"]

for key, value in player.items():
    PRINT[f"{key}: {value}"]

# Dictionary methods
keys = player.keys()
values = player.values()
items = player.items()

# Merging (Python 3.9+)
defaults = {"hp": 100, "mp": 50}
player = defaults | player  # Player values override defaults
```

### Tuples

```python
# Creation (immutable)
location = (10, 20, 100)  # x, y, layer
coords = 10, 20, 100  # Parentheses optional

# Unpacking
x, y, layer = location

# Single element (needs comma)
single = (42,)

# Accessing
x = location[0]
layer = location[-1]

# Tuple as dictionary key (immutable, so allowed)
grid_data = {
    (0, 0): "camp",
    (1, 0): "water",
    (0, 1): "shelter"
}
```

### Sets

```python
# Creation (unique, unordered)
visited = set()
visited = {"AA340", "AB340", "AC340"}
visited = set(["AA340", "AB340", "AA340"])  # Duplicates removed

# Adding
visited.add("AD340")
visited.update(["AE340", "AF340"])

# Removing
visited.remove("AA340")  # Error if not present
visited.discard("ZZ999")  # No error if not present
item = visited.pop()  # Remove and return arbitrary item

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

union = a | b  # {1, 2, 3, 4, 5, 6}
intersection = a & b  # {3, 4}
difference = a - b  # {1, 2}
symmetric_diff = a ^ b  # {1, 2, 5, 6}

# Testing
if 3 in a:
    PRINT["Found 3"]

is_subset = a <= b
is_superset = a >= b
```

---

## Error Handling

### Try/Except

```python
# Basic error handling
try:
    level = int(user_input)
    set_var("player-level", level)
except ValueError:
    PRINT["Error: Invalid number"]
    level = 1  # Default

# Multiple exception types
try:
    file_data = load_file("config.json")
    config = json.loads(file_data)
except FileNotFoundError:
    PRINT["Config file not found"]
    config = {}
except json.JSONDecodeError:
    PRINT["Invalid JSON format"]
    config = {}

# Catch all exceptions
try:
    risky_operation()
except Exception as e:
    PRINT[f"Error: {e}"]
    print(f"DEBUG: {type(e).__name__}")
```

### Finally

```python
# Cleanup code that always runs
file = None
try:
    file = open("data.txt", "r")
    data = file.read()
finally:
    if file:
        file.close()  # Always close file

# Better: Use context manager
try:
    with open("data.txt", "r") as file:
        data = file.read()
except FileNotFoundError:
    PRINT["File not found"]
```

### Else Clause

```python
# Runs if no exception occurred
try:
    result = calculate_distance(start, end)
except ValueError:
    PRINT["Invalid coordinates"]
else:
    PRINT[f"Distance: {result}"]
    set_var("last-distance", result)
```

### Custom Exceptions

```python
class InsufficientResourcesError(Exception):
    """Raised when resources are too low."""
    pass

def craft_item(item_name, resources):
    """Craft item if enough resources."""
    required = get_recipe(item_name)
    
    for resource, amount in required.items():
        if resources.get(resource, 0) < amount:
            raise InsufficientResourcesError(
                f"Need {amount} {resource}, have {resources.get(resource, 0)}"
            )
    
    # Craft the item
    consume_resources(resources, required)
    return item_name

# Usage
try:
    item = craft_item("shelter", {"wood": 20, "rope": 5})
    PRINT[f"Crafted: {item}"]
except InsufficientResourcesError as e:
    PRINT[f"Cannot craft: {e}"]
    GUIDE["resource/gathering"|"quick"]
```

---

## File Operations

### Reading Files

```python
from pathlib import Path

# Read entire file
with open("memory/docs/notes.txt", "r") as f:
    content = f.read()

# Read line by line
with open("memory/docs/log.txt", "r") as f:
    for line in f:
        PRINT[line.strip()]

# Read all lines as list
with open("memory/docs/items.txt", "r") as f:
    lines = f.readlines()

# Using Path (recommended)
config_file = Path("memory/bank/user/settings.json")
if config_file.exists():
    content = config_file.read_text()
```

### Writing Files

```python
# Write (overwrites)
with open("memory/docs/output.txt", "w") as f:
    f.write("New content\n")
    f.write("Second line\n")

# Append
with open("memory/logs/events.log", "a") as f:
    f.write(f"{datetime.now()}: Event logged\n")

# Write lines
lines = ["Line 1", "Line 2", "Line 3"]
with open("output.txt", "w") as f:
    f.writelines([line + "\n" for line in lines])

# Using Path
output_file = Path("memory/docs/report.txt")
output_file.write_text("Report content here")
```

### JSON Files

```python
import json

# Read JSON
with open("memory/bank/user/variables.json", "r") as f:
    data = json.load(f)

# Write JSON
data = {"player-name": "Hero", "player-level": 5}
with open("memory/bank/user/variables.json", "w") as f:
    json.dump(data, f, indent=2)

# Parse JSON string
json_str = '{"key": "value"}'
data = json.loads(json_str)

# Generate JSON string
data = {"key": "value"}
json_str = json.dumps(data, indent=2)
```

### Path Operations

```python
from pathlib import Path

# Create Path object
user_dir = Path("memory/bank/user")

# Check existence
if user_dir.exists():
    PRINT["Directory exists"]

# Create directory
user_dir.mkdir(parents=True, exist_ok=True)

# List files
for file in user_dir.glob("*.json"):
    PRINT[f"Found: {file.name}"]

# Join paths
config_file = user_dir / "settings.json"

# Get parts
name = config_file.name  # "settings.json"
stem = config_file.stem  # "settings"
suffix = config_file.suffix  # ".json"
parent = config_file.parent  # Path("memory/bank/user")
```

---

## Import and Modules

### Standard Library

```python
# Date and time
from datetime import datetime, timedelta

now = datetime.now()
PRINT[f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"]

tomorrow = now + timedelta(days=1)
week_ago = now - timedelta(weeks=1)

# Math
import math

distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
angle = math.atan2(dy, dx)
rounded = math.ceil(distance)

# Random
import random

dice_roll = random.randint(1, 6)
choice = random.choice(["water", "food", "wood"])
samples = random.sample(inventory, 3)  # Pick 3 random items
random.shuffle(inventory)  # Shuffle in place

# Collections
from collections import Counter, defaultdict, deque

# Count occurrences
items = ["axe", "rope", "axe", "knife", "axe"]
counts = Counter(items)
PRINT[f"Axes: {counts['axe']}"]

# Default dictionary
resources = defaultdict(int)  # Default value 0
resources["water"] += 10  # No KeyError

# Deque (efficient queue)
queue = deque([1, 2, 3])
queue.append(4)  # Add right
queue.appendleft(0)  # Add left
item = queue.pop()  # Remove right
item = queue.popleft()  # Remove left
```

### Third-Party Packages

```python
# Requests (HTTP)
import requests

response = requests.get("https://api.example.com/data")
data = response.json()

# Numpy (numerical computing)
import numpy as np

distances = np.array([10, 20, 15, 30])
mean_distance = distances.mean()
max_distance = distances.max()

# Pandas (data analysis)
import pandas as pd

df = pd.DataFrame({
    "resource": ["water", "food", "wood"],
    "amount": [50, 30, 20]
})

low_resources = df[df["amount"] < 40]
```

---

## Advanced Patterns

### Decorators

```python
def log_calls(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        PRINT[f"Calling {func.__name__}"]
        result = func(*args, **kwargs)
        PRINT[f"Finished {func.__name__}"]
        return result
    return wrapper

@log_calls
def important_operation():
    PRINT["Doing important work..."]
    return 42

# Usage
result = important_operation()
# Output:
# Calling important_operation
# Doing important work...
# Finished important_operation
```

### Context Managers

```python
from contextlib import contextmanager

@contextmanager
def checkpoint_context(name):
    """Context manager for automatic checkpoint save/restore."""
    CHECKPOINT_SAVE[f"before-{name}"]
    try:
        yield
    except Exception as e:
        PRINT[f"Error: {e}"]
        CHECKPOINT_LOAD[f"before-{name}"]
        raise
    finally:
        CHECKPOINT_SAVE[f"after-{name}"]

# Usage
with checkpoint_context("exploration"):
    # Your risky code here
    explore_dangerous_area()
```

### Generators

```python
def resource_monitor(threshold):
    """Generator that yields when resources are low."""
    while True:
        water = get_var("water-level", 100)
        food = get_var("food-supply", 50)
        
        if water < threshold:
            yield "water"
        if food < threshold:
            yield "food"

# Usage
monitor = resource_monitor(30)
for low_resource in monitor:
    PRINT[f"Low {low_resource}!"]
    GUIDE[f"{low_resource}/collection"|"quick"]
```

### Type Hints

```python
from typing import List, Dict, Optional, Union

def calculate_resources(
    inventory: List[str],
    amounts: Dict[str, int],
    multiplier: Optional[float] = None
) -> int:
    """Calculate total resources with optional multiplier."""
    total = sum(amounts.values())
    
    if multiplier is not None:
        total = int(total * multiplier)
    
    return total

# Type hints help IDE autocomplete and catch errors early
```

---

## Performance Tips

### 1. Use Built-ins

```python
# ✅ Fast: Built-in sum
total = sum(values)

# ❌ Slower: Manual loop
total = 0
for v in values:
    total += v
```

### 2. List Comprehensions

```python
# ✅ Fast: List comprehension
squares = [x**2 for x in range(1000)]

# ❌ Slower: Loop with append
squares = []
for x in range(1000):
    squares.append(x**2)
```

### 3. Generators for Large Data

```python
# ✅ Memory efficient: Generator
def read_large_file(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()

# ❌ Memory intensive: Load all at once
with open(filepath) as f:
    lines = f.readlines()  # All in memory
```

### 4. Set Operations

```python
# ✅ Fast: Set membership test O(1)
visited = set(["AA340", "AB340", "AC340"])
if "AA340" in visited:
    pass

# ❌ Slower: List membership test O(n)
visited = ["AA340", "AB340", "AC340"]
if "AA340" in visited:
    pass
```

---

## Debugging

### Print Debugging

```python
# Add debug prints
def complex_calculation(a, b):
    print(f"DEBUG: a={a}, b={b}")
    result = a * b + (a - b)
    print(f"DEBUG: result={result}")
    return result
```

### Python Debugger (pdb)

```python
import pdb

def buggy_function():
    x = 10
    y = 20
    pdb.set_trace()  # Debugger stops here
    result = x / y
    return result

# Commands in debugger:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code
# q - quit
```

### Assertions

```python
def set_player_hp(hp):
    """Set player HP with validation."""
    assert hp >= 0, "HP cannot be negative"
    assert hp <= 100, "HP cannot exceed 100"
    set_var("player-hp", hp)
```

---

## Related Documentation

- **[uCODE Beginner Commands](uCODE-Beginner-Commands.md)** - Start here if new
- **[Python-First Guide](uCODE-Python-First-Guide.md)** - Architecture overview
- **[Migration Guide](dev/tools/README-MIGRATION.md)** - Upgrade old scripts

---

**Level:** Advanced  
**Version:** v1.2.24  
**Performance:** 925,078 ops/sec native Python execution
