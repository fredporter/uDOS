# Variables in uCODE

**Level**: Beginner
**Time**: 15 minutes
**Category**: uCODE Basics
**Tags**: #variables #data-types #fundamentals

---

## 📖 What You'll Learn

- Declare and use variables
- Understand data types
- Variable naming rules
- Scope and lifetime
- Common patterns

---

## 🎯 Variables Explained

Variables store data for later use. In uCODE, declare variables with `SET`:

```ucode
SET username = "Alice"
SET age = 25
SET active = true
```

---

## 📊 Data Types

### Strings (Text)
```ucode
SET greeting = "Hello, World!"
SET filepath = "/data/notes.txt"
SET empty = ""
```

### Numbers
```ucode
SET count = 42
SET price = 19.99
SET negative = -10
```

### Booleans
```ucode
SET isActive = true
SET hasErrors = false
```

### Lists
```ucode
SET cities = ["Tokyo", "London", "Sydney"]
SET numbers = [1, 2, 3, 4, 5]
SET mixed = ["text", 42, true]
```

---

## 🔧 Using Variables

### Reading Variables
```ucode
# Use $ prefix to read variable value
SET name = "Bob"
PRINT "Hello, $name!"
# Output: Hello, Bob!
```

### Updating Variables
```ucode
SET counter = 0
SET counter = $counter + 1
PRINT "Counter: $counter"
# Output: Counter: 1
```

### String Concatenation
```ucode
SET first = "John"
SET last = "Doe"
SET fullname = "$first $last"
PRINT $fullname
# Output: John Doe
```

---

## 📝 Naming Rules

### ✅ Valid Names
```ucode
SET username = "alice"
SET user_name = "alice"
SET userName = "alice"
SET user1 = "alice"
SET _private = "secret"
```

### ❌ Invalid Names
```ucode
SET 1user = "alice"      # Can't start with number
SET user-name = "alice"  # No hyphens
SET user name = "alice"  # No spaces
SET SET = "value"        # Reserved keyword
```

### Best Practices
- Use descriptive names: `userCount` not `uc`
- Consistent style: `snake_case` or `camelCase`
- Prefix booleans: `isActive`, `hasData`
- Uppercase constants: `MAX_SIZE`

---

## 🎭 Variable Scope

### Global Scope
```ucode
# Available everywhere in script
SET globalVar = "accessible anywhere"

FUNCTION test
  PRINT $globalVar  # ✅ Works
END
```

### Local Scope
```ucode
FUNCTION calculate
  # Only accessible inside function
  SET localVar = 42
  PRINT $localVar  # ✅ Works
END

PRINT $localVar  # ❌ Error: undefined
```

### Block Scope
```ucode
IF $count > 0
  SET message = "Positive"  # Block-scoped
  PRINT $message            # ✅ Works
END

PRINT $message  # ❌ Error: out of scope
```

---

## 💡 Common Patterns

### Counter Pattern
```ucode
SET counter = 0
WHILE $counter < 5
  PRINT "Iteration: $counter"
  SET counter = $counter + 1
END
```

### Accumulator Pattern
```ucode
SET total = 0
SET numbers = [10, 20, 30, 40]

FOR num IN $numbers
  SET total = $total + $num
END

PRINT "Total: $total"
# Output: Total: 100
```

### Flag Pattern
```ucode
SET found = false
SET items = ["apple", "banana", "cherry"]

FOR item IN $items
  IF $item == "banana"
    SET found = true
    BREAK
  END
END

IF $found
  PRINT "Banana found!"
END
```

---

## 🧪 Practice Exercises

### Exercise 1: Personal Info
Create variables for your name, age, and location (grid cell + TZONE):

```ucode
SET name = "Your Name"
SET age = 25
SET location = "M240-GMT"  # London example

PRINT "Name: $name"
PRINT "Age: $age"
PRINT "Location: $location"
```

### Exercise 2: Temperature Converter
Convert Celsius to Fahrenheit:

```ucode
SET celsius = 25
SET fahrenheit = ($celsius * 9 / 5) + 32
PRINT "$celsius°C = $fahrenheit°F"
```

### Exercise 3: List Operations
Work with a list of cities:

```ucode
SET cities = ["Tokyo", "Delhi", "Shanghai"]
PRINT "Cities: $cities"

# Add a city
SET cities = $cities + ["Sydney"]
PRINT "Updated: $cities"

# Count cities
SET count = LENGTH($cities)
PRINT "Total cities: $count"
```

---

## 🎨 ASCII Diagram: Variable Storage

```
┌──────────────────────────┐
│   Variable Memory        │
├──────────────────────────┤
│ username → "Alice"       │
│ age      → 25            │
│ active   → true          │
│ cities   → ["T","L","S"] │
└──────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│   When Referenced        │
├──────────────────────────┤
│ $username → "Alice"      │
│ $age      → 25           │
│ $active   → true         │
└──────────────────────────┘
```

---

## 🚨 Common Errors

### Undefined Variable
```ucode
PRINT $missingVar
# ❌ Error: Variable 'missingVar' not defined
```

**Fix**: Declare before use
```ucode
SET missingVar = "now defined"
PRINT $missingVar  # ✅ Works
```

### Type Mismatch
```ucode
SET text = "hello"
SET result = $text + 5
# ❌ Error: Cannot add number to string
```

**Fix**: Convert types
```ucode
SET number = "42"
SET result = NUMBER($number) + 5
PRINT $result  # Output: 47
```

---

## 🏆 Challenge

Create a script that:
1. Stores your current location (grid cell + TZONE)
2. Stores the current timestamp (YYYY-MM-DD-HH-MM-SS-TZONE)
3. Creates a log entry combining both
4. Prints the formatted log

Example output:
```
[2025-11-16-14-30-00-AEST] Located at AA340-AEST (Sydney)
```

---

## 🔗 Related Guides

**Next**: [Control Flow](control-flow.md) - IF/ELSE and loops
**See Also**: [Data Types](data-types.md), [Functions](../functions.md)
**Advanced**: [Variable Scope](../best-practices/scope.md)

---

## 📚 uCODE Reference

```ucode
# Variable Commands
SET var = value          # Declare/update variable
GET var                  # Read variable (same as $var)
UNSET var               # Delete variable
EXISTS var              # Check if defined

# Type Conversions
STRING(value)           # Convert to string
NUMBER(value)           # Convert to number
BOOLEAN(value)          # Convert to boolean
LIST(value)             # Convert to list

# List Operations
LENGTH(list)            # Count items
APPEND(list, item)      # Add to end
INSERT(list, pos, item) # Add at position
REMOVE(list, item)      # Remove item
```

---

**Completion**: Mark this guide as complete:
```ucode
[PRIVATE|ADD|completed-guides|ucode-basics/variables.md]
```

**Time Spent**: ~15 minutes
**Next Step**: Try the exercises, then move to [Control Flow](control-flow.md)
