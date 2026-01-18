# NPC System Documentation

**Phase 6A: NPC & Dialogue System**  
**Version:** Core v1.1.0  
**Status:** Production Ready  
**Tests:** 27/27 passing ✅

---

## Overview

The NPC (Non-Player Character) system provides location-based NPCs with branching dialogue trees. Players can discover NPCs, initiate conversations, and navigate through dialogue options.

### Key Features

- **Location-based NPC spawning** - NPCs tied to specific locations
- **Dialogue trees** - Branching conversations with multiple paths
- **Context-aware conditions** - Dialogue options based on player stats/inventory
- **Pre-loaded NPCs** - 4 NPCs ready to use (2 merchants, 1 quest giver, 1 hostile)
- **Extensible** - Easy to add custom NPCs and dialogue trees

---

## Commands

### NPC - List NPCs at Location

```bash
NPC [location_id]
```

Lists all NPCs at the specified location.

**Examples:**

```bash
NPC L300-BJ10         # List NPCs at Tokyo
NPC                   # List NPCs at current location (if state available)
```

**Response:**

```python
{
    "status": "success",
    "message": "Found 2 NPC(s) at L300-BJ10",
    "npcs": [
        {
            "id": "merchant-tokyo-1",
            "name": "Kenji",
            "role": "merchant",
            "location": "L300-BJ10",
            "disposition": "friendly",
            "dialogue_state": "greeting",
            "inventory": [...],
            "dialogue_tree": "merchant_generic"
        },
        ...
    ],
    "location": "L300-BJ10"
}
```

---

### TALK - Start Conversation

```bash
TALK <npc_name>
```

Initiates a conversation with an NPC. Name search is **case-insensitive**.

**Examples:**

```bash
TALK Kenji
TALK Elder Tanaka
TALK kenji             # Case-insensitive
```

**Response:**

```python
{
    "status": "success",
    "npc": "Kenji",
    "text": "Welcome, traveler! Looking to buy or sell?",
    "options": [
        {"text": "Show me your wares", "next": "shop"},
        {"text": "I have items to sell", "next": "sell"},
        {"text": "Goodbye", "next": "goodbye"}
    ],
    "conversation_active": true
}
```

**Error Cases:**

- NPC not found at current location
- NPC name ambiguous (multiple matches)

---

### REPLY - Select Dialogue Option

```bash
REPLY <option_number>
```

Selects a numbered dialogue option (1-indexed for users).

**Examples:**

```bash
REPLY 1               # Select first option
REPLY 2               # Select second option
```

**Response:**

```python
{
    "status": "success",
    "text": "Here's what I have in stock: ...",
    "options": [
        {"text": "Back", "next": "greeting"},
        {"text": "Goodbye", "next": "goodbye"}
    ],
    "conversation_active": true,
    "action": "show_shop"  # Optional action field
}
```

**Terminal Nodes:**
When a conversation ends (no more options):

```python
{
    "status": "success",
    "text": "Safe travels, friend!",
    "options": [],
    "conversation_active": false
}
```

---

## NPC Data Format

### NPC Properties

```python
npc_data = {
    "id": str,                    # Unique identifier
    "name": str,                  # Display name
    "role": str,                  # merchant, quest_giver, hostile
    "location": str,              # Location ID (e.g., L300-BJ10)
    "disposition": str,           # friendly, wise, aggressive, etc.
    "dialogue_state": str,        # Current dialogue state
    "dialogue_tree": str,         # Dialogue tree ID

    # Role-specific fields
    "inventory": List[Dict],      # For merchants
    "quests": List[str],          # For quest givers
    "health": int,                # For hostile NPCs
    "attack": int,                # For hostile NPCs
    "defense": int,               # For hostile NPCs
    "loot": List[Dict]            # For hostile NPCs
}
```

### Merchant NPC Example

```python
{
    "id": "merchant-tokyo-1",
    "name": "Kenji",
    "role": "merchant",
    "location": "L300-BJ10",
    "disposition": "friendly",
    "dialogue_state": "greeting",
    "inventory": [
        {"name": "health_potion", "quantity": 5, "price": 10},
        {"name": "map_fragment", "quantity": 1, "price": 50}
    ],
    "dialogue_tree": "merchant_generic"
}
```

### Quest Giver NPC Example

```python
{
    "id": "quest-giver-1",
    "name": "Elder Tanaka",
    "role": "quest_giver",
    "location": "L300-BJ10",
    "disposition": "wise",
    "dialogue_state": "quest_available",
    "quests": ["find_lost_item", "explore_underground"],
    "dialogue_tree": "elder_quests"
}
```

### Hostile NPC Example

```python
{
    "id": "hostile-1",
    "name": "Rogue Agent",
    "role": "hostile",
    "location": "L300-BJ11",
    "disposition": "aggressive",
    "health": 50,
    "attack": 8,
    "defense": 5,
    "loot": [
        {"name": "rusty_key", "quantity": 1, "drop_chance": 0.7}
    ],
    "dialogue_tree": "hostile_generic"
}
```

---

## Dialogue Tree Format

### DialogueNode Structure

```python
DialogueNode(
    node_id: str,           # Unique node identifier
    text: str,              # Dialogue text to display
    options: List[Dict],    # Dialogue options
    condition: Callable     # Optional condition function
)
```

### Option Format

```python
{
    "text": str,            # Option text displayed to player
    "next": str,            # Next node ID to navigate to
    "action": str,          # Optional action (accept_quest, combat, etc.)
    "cost": int             # Optional cost (for purchases)
}
```

### Example Dialogue Tree

```python
from core.commands.dialogue_engine import DialogueTree, DialogueNode

# Create tree
merchant_tree = DialogueTree("custom_merchant")

# Root node
greeting = DialogueNode(
    "greeting",
    "Welcome! What can I do for you?",
    [
        {"text": "Buy items", "next": "shop"},
        {"text": "Sell items", "next": "sell"},
        {"text": "Leave", "next": "goodbye"}
    ]
)
merchant_tree.add_node(greeting, is_root=True)

# Shop node
shop = DialogueNode(
    "shop",
    "Here's what I have: Sword (50g), Shield (30g)",
    [
        {"text": "Buy Sword", "next": "buy_sword", "cost": 50},
        {"text": "Buy Shield", "next": "buy_shield", "cost": 30},
        {"text": "Back", "next": "greeting"}
    ]
)
merchant_tree.add_node(shop)

# Terminal node
goodbye = DialogueNode(
    "goodbye",
    "Come back anytime!",
    []  # No options = conversation ends
)
merchant_tree.add_node(goodbye)

# Register tree
dialogue_engine.add_custom_tree(merchant_tree)
```

---

## Pre-loaded NPCs

### Merchants

**Kenji (L300-BJ10 - Tokyo)**

- Role: merchant
- Disposition: friendly
- Inventory: health_potion (10g), map_fragment (50g)
- Dialogue: merchant_generic

**Min-jun (L300-BQ10 - Seoul)**

- Role: merchant
- Disposition: friendly
- Inventory: stamina_boost (15g), compass (25g)
- Dialogue: merchant_generic

### Quest Givers

**Elder Tanaka (L300-BJ10 - Tokyo)**

- Role: quest_giver
- Disposition: wise
- Quests: find_lost_item, explore_underground
- Dialogue: elder_quests

### Hostile

**Rogue Agent (L300-BJ11)**

- Role: hostile
- Disposition: aggressive
- Stats: 50 HP, 8 ATK, 5 DEF
- Loot: rusty_key (70% drop)
- Dialogue: hostile_generic

---

## Pre-loaded Dialogue Trees

### merchant_generic (4 nodes)

1. **greeting** - Welcome message with 3 options
   - Shop → Navigate to shop
   - Sell → Navigate to sell
   - Goodbye → End conversation

2. **shop** - Display merchant inventory
   - Lists items with prices
   - Terminal node (no further options)

3. **sell** - Accept player items
   - Offer to buy items
   - Navigate back or goodbye

4. **goodbye** - Farewell message
   - Terminal node

### elder_quests (4 nodes)

1. **quest_available** - Quest offering
   - Tell me more → quest_details
   - I'm busy → quest_decline

2. **quest_details** - Quest information
   - Accept quest → quest_accept
   - Decline → quest_decline

3. **quest_accept** - Quest accepted
   - Terminal node with quest start

4. **quest_decline** - Quest declined
   - Terminal node with polite farewell

### hostile_generic (3 nodes)

1. **encounter** - Hostile warning
   - Flee → flee
   - Fight → combat

2. **flee** - Escape encounter
   - Terminal node (player escapes)

3. **combat** - Initiate combat
   - Terminal node (combat starts)

---

## Integration Guide

### 1. Adding a Custom NPC

```python
from core.commands.npc_handler import NPCHandler

npc_handler = NPCHandler()

# Create custom NPC
custom_npc = {
    "id": "blacksmith-1",
    "name": "Hiro",
    "role": "merchant",
    "location": "L300-BK10",
    "disposition": "gruff",
    "dialogue_state": "greeting",
    "inventory": [
        {"name": "iron_sword", "quantity": 2, "price": 100},
        {"name": "steel_armor", "quantity": 1, "price": 250}
    ],
    "dialogue_tree": "blacksmith_custom"
}

# Add to registry
npc_handler.npcs["blacksmith-1"] = custom_npc
```

### 2. Adding a Custom Dialogue Tree

```python
from core.commands.dialogue_engine import DialogueEngine, DialogueTree, DialogueNode

dialogue_engine = DialogueEngine()

# Create custom tree
blacksmith_tree = DialogueTree("blacksmith_custom")

# Add nodes
greeting = DialogueNode(
    "greeting",
    "Need weapons or repairs?",
    [
        {"text": "Show me weapons", "next": "weapons"},
        {"text": "Can you repair this?", "next": "repairs"},
        {"text": "Just looking", "next": "goodbye"}
    ]
)
blacksmith_tree.add_node(greeting, is_root=True)

weapons = DialogueNode(
    "weapons",
    "I've got the finest blades in town: Iron Sword (100g), Steel Sword (250g)",
    [
        {"text": "Buy Iron Sword", "next": "buy_iron", "cost": 100},
        {"text": "Buy Steel Sword", "next": "buy_steel", "cost": 250},
        {"text": "Back", "next": "greeting"}
    ]
)
blacksmith_tree.add_node(weapons)

goodbye = DialogueNode("goodbye", "Come back when you need quality steel!", [])
blacksmith_tree.add_node(goodbye)

# Register tree
dialogue_engine.add_custom_tree(blacksmith_tree)
```

### 3. Using TalkHandler in TUI

```python
from core.commands.npc_handler import NPCHandler
from core.commands.dialogue_engine import DialogueEngine
from core.commands.talk_handler import TalkHandler
from core.tui.state import GameState

# Initialize
npc_handler = NPCHandler()
dialogue_engine = DialogueEngine()
talk_handler = TalkHandler(npc_handler, dialogue_engine)

# Set game state
game_state = GameState()
game_state.location = "L300-BJ10"
game_state.player_stats = {"level": 5, "gold": 100}
talk_handler.state = game_state

# Start conversation
result = talk_handler.handle("TALK", ["Kenji"], None, None)
print(result["text"])
for i, option in enumerate(result["options"], 1):
    print(f"{i}. {option['text']}")

# Reply
result = talk_handler.handle("REPLY", ["1"], None, None)
print(result["text"])
```

---

## Context & Conditions

Dialogue options can have conditions based on player context:

```python
def check_gold(context):
    """Check if player has enough gold"""
    return context.get("player_gold", 0) >= 50

expensive_option = DialogueNode(
    "expensive_item",
    "This rare artifact costs 50 gold",
    [
        {"text": "Buy it", "next": "purchase", "cost": 50},
        {"text": "Too expensive", "next": "greeting"}
    ],
    condition=check_gold  # Only show if player has 50+ gold
)
```

**Context Structure:**

```python
context = {
    "player_level": int,
    "player_gold": int,
    "player_inventory": List[str],
    "quests_completed": List[str],
    "npcs_met": List[str]
}
```

---

## Testing

Run the comprehensive test suite:

```bash
source .venv/bin/activate
PYTHONPATH=/Users/fredbook/Code/uDOS:$PYTHONPATH pytest memory/tests/integration/test_phase_6a_npc_system.py -v
```

**Test Coverage:**

- 8 NPCHandler tests
- 8 DialogueEngine tests
- 6 TalkHandler tests
- 5 Integration tests
- **Total: 27 tests, 100% passing** ✅

---

## API Reference

### NPCHandler Methods

```python
# List NPCs at location
npcs = npc_handler.get_npcs_at_location("L300-BJ10")

# Get NPC by ID
npc = npc_handler.get_npc_by_id("merchant-tokyo-1")

# Move NPC
npc_handler.move_npc("merchant-tokyo-1", "L300-BK10")

# Update NPC state
npc_handler.update_npc_state("merchant-tokyo-1", {
    "disposition": "friendly",
    "dialogue_state": "shop"
})
```

### DialogueEngine Methods

```python
# Start conversation
result = dialogue_engine.start_conversation("merchant_generic", context)

# Continue conversation
result = dialogue_engine.continue_conversation("merchant_generic", "shop", context)

# Add custom tree
dialogue_engine.add_custom_tree(custom_tree)

# Get tree
tree = dialogue_engine.get_tree("merchant_generic")
```

### TalkHandler Methods

```python
# Talk to NPC
result = talk_handler.handle("TALK", ["Kenji"], None, None)

# Reply to dialogue
result = talk_handler.handle("REPLY", ["1"], None, None)

# End conversation manually
talk_handler.end_conversation("player-1")
```

---

## Next Steps

### Phase 6A-2: Combat System

- Combat engine (turn-based)
- Weapons and items system
- Character stats and leveling
- Commands: ATTACK, DEFEND, USE, FLEE

### Phase 6A-3: Quest System

- Quest tracking and completion
- Quest journal
- Quest rewards
- Commands: QUEST, ACCEPT, DECLINE, COMPLETE

---

## References

- [Phase 6 Planning](../../docs/devlog/2026-01-18-phase-6-planning.md)
- [Test Suite](../../memory/tests/integration/test_phase_6a_npc_system.py)
- [Handler Architecture](../docs/COMMAND-ARCHITECTURE.md)

---

_Last Updated: 2026-01-18_  
_uDOS Core v1.1.0_  
_Phase 6A-1: NPC System - Production Ready_ ✅
