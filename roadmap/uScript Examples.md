# uScript: uOS Native Scripting Language

## \[Overview]

`uScript` is the native scripting language of uOS, built to extend and evolve user interaction beyond uBASIC. Inspired by Markdown, BASIC, and modern scripting paradigms, it is designed for clarity, power, and seamless container integration.

* **No line numbers**, modern syntax
* **Fully Markdown-compatible**
* **Support for ASCII I/O and graphical overlays**
* **Embedded container calls** to Python, Bash, etc.
* **Anchor-linkable code**, reusable macros

## \[Philosophy]

* Empower the user to create, learn, and modify with minimal friction.
* Promote clear, modular logic for educational and creative coding.
* Bridge play and logic: netHack-style events, BASIC-style logic, Python-style execution.

---

## \[Syntax Basics]

### (Code) Blocks

All code is wrapped in `(code)` blocks:

```
(code)
print "Hello, World!"
(code)
```

### Comments

Use `#` for single-line comments:

```
(code)
# This is a comment
print "Run"
(code)
```

### Variables

Auto-typed at runtime. Declare simply:

```
(code)
name = "Wizard"
level = 3
(code)
```

### Conditionals

```
(code)
if level > 2:
    print "Access granted"
else:
    print "Access denied"
(code)
```

### Loops

```
(code)
for i in range(1, 6):
    print "Potion #" + str(i)
(code)
```

---

## \[Interactive Logic Examples]

### \[Dice Roll Game]

```
(code)
import random
roll = random.randint(1,6)
print "You rolled a ", roll
if roll == 6:
    print "Critical hit!"
(code)
```

### \[Inventory Loop]

```
(code)
inventory = ["Sword", "Shield", "Potion"]
for item in inventory:
    print "You carry: ", item
(code)
```

---

## \[Containers]

uScript integrates with containers using the `call` keyword. Arguments can be passed directly as Markdown-safe arrays or dicts.

### Call a Python Container:

```
(code)
call python:
  script: "/scripts/generate_poem.py"
  args:
    theme: "stars"
    lines: 4
(code)
```

### Return Handling

Returned content can be used in uScript as plain text or ASCII renderings:

```
(code)
result = call python:
  script: "/scripts/get_weather.py"
  args:
    city: "Sydney"
print result
(code)
```

---

## \[Macro Commands]

Macros let you define reusable blocks with parameters.

```
(code)
macro greet(name):
    print "Hello, " + name + "!"
end

call greet("Master")
(code)
```

---

## \[ASCII and UI Layer Support]

Use `draw` or `ascii` to send content to visual layers.

```
(code)
ascii:
  text: "YOU DIED"
  style: red-blink
  pos: [40,12]
(code)
```

```
(code)
draw map:
  source: "/maps/temple.txt"
  layer: 2
(code)
```

---

## \[uScript Goals]

* Expand from uBASIC with structured logic and interactive storytelling
* Enable integration with containerized AI, agents, or automation
* Act as the core scripting interface for uOS modules and maps

## \[Next]

* Define `uScript Standard Library`
* Enable runtime debugging view
* Embed macros into Markdown for cross-scripting

> "A good spell is a script you understand."

---
