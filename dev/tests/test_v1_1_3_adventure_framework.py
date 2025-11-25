"""
Test Suite for v1.1.3.2 - Apocalypse Adventure Framework
Tests: SCENARIO command, NetHack-style gameplay, resource/inventory, survival mechanics

Test Coverage (60 tests total):
- Scenario System: 12 tests
- Resource & Inventory: 10 tests
- Survival Mechanics: 10 tests
- Map Gameplay: 10 tests
- Mission System: 10 tests
- Integration: 8 tests

Author: uDOS Development Team
Version: 1.1.3.2
Date: 2025-11-24
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))


class ScenarioState:
    """Represents game state during scenario"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Scenario:
    """Interactive scenario/quest"""

    def __init__(self, id: str, title: str, description: str,
                 difficulty: str = "normal"):
        self.id = id
        self.title = title
        self.description = description
        self.difficulty = difficulty  # easy, normal, hard, extreme
        self.state = ScenarioState.ACTIVE
        self.current_step = 0
        self.steps = []
        self.objectives = []
        self.rewards = {}
        self.start_time = datetime.now().timestamp()
        self.completion_time = None
        self.choices_made = []

    def add_step(self, step_id: str, text: str, choices: List[Dict] = None):
        """Add story step with choices"""
        self.steps.append({
            'id': step_id,
            'text': text,
            'choices': choices or [],
            'visited': False
        })

    def make_choice(self, choice_index: int) -> bool:
        """Make choice and advance story"""
        if self.current_step >= len(self.steps):
            return False

        step = self.steps[self.current_step]
        if choice_index < 0 or choice_index >= len(step.get('choices', [])):
            return False

        choice = step['choices'][choice_index]
        self.choices_made.append({
            'step': self.current_step,
            'choice': choice,
            'timestamp': datetime.now().timestamp()
        })

        step['visited'] = True

        # Apply consequences
        if 'next_step' in choice:
            self.current_step = choice['next_step']
        else:
            self.current_step += 1

        return True

    def complete(self, success: bool = True):
        """Complete scenario"""
        self.state = ScenarioState.COMPLETED if success else ScenarioState.FAILED
        self.completion_time = datetime.now().timestamp()

    def get_duration(self) -> float:
        """Get scenario duration in seconds"""
        end = self.completion_time or datetime.now().timestamp()
        return end - self.start_time


class ItemType:
    """Item types for inventory"""
    FOOD = "food"
    WATER = "water"
    TOOL = "tool"
    WEAPON = "weapon"
    MEDICAL = "medical"
    RESOURCE = "resource"
    QUEST = "quest"


class Item:
    """Inventory item"""

    def __init__(self, id: str, name: str, item_type: str,
                 weight: float = 1.0, stackable: bool = True):
        self.id = id
        self.name = name
        self.item_type = item_type
        self.weight = weight
        self.stackable = stackable
        self.quantity = 1
        self.durability = 100.0  # For tools/weapons
        self.properties = {}  # Additional properties

    def use(self, amount: int = 1) -> bool:
        """Use/consume item"""
        if not self.stackable and amount > 1:
            return False

        if self.quantity < amount:
            return False

        self.quantity -= amount
        return True

    def repair(self, amount: float):
        """Repair item durability"""
        self.durability = min(100.0, self.durability + amount)

    def degrade(self, amount: float):
        """Reduce item durability"""
        self.durability = max(0.0, self.durability - amount)
        return self.durability > 0


class Inventory:
    """Player inventory system"""

    def __init__(self, max_weight: float = 50.0):
        self.items = {}  # id -> Item
        self.max_weight = max_weight

    def add_item(self, item: Item) -> bool:
        """Add item to inventory"""
        # Check weight limit
        if self.get_total_weight() + item.weight > self.max_weight:
            return False

        # Stack if possible
        if item.stackable and item.id in self.items:
            self.items[item.id].quantity += item.quantity
        else:
            self.items[item.id] = item

        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        if item_id not in self.items:
            return False

        item = self.items[item_id]
        if item.quantity < quantity:
            return False

        item.quantity -= quantity
        if item.quantity <= 0:
            del self.items[item_id]

        return True

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID"""
        return self.items.get(item_id)

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains item"""
        item = self.items.get(item_id)
        return item is not None and item.quantity >= quantity

    def get_total_weight(self) -> float:
        """Calculate total inventory weight"""
        return sum(item.weight * item.quantity for item in self.items.values())

    def get_items_by_type(self, item_type: str) -> List[Item]:
        """Get all items of specific type"""
        return [item for item in self.items.values() if item.item_type == item_type]


class SurvivalStats:
    """Player survival statistics"""

    def __init__(self):
        self.health = 100.0
        self.hunger = 100.0  # 0 = starving, 100 = full
        self.thirst = 100.0  # 0 = dehydrated, 100 = hydrated
        self.stamina = 100.0
        self.morale = 100.0
        self.last_update = datetime.now().timestamp()

    def update(self, time_elapsed: float = 1.0):
        """Update stats based on time passage (hours)"""
        # Natural degradation per hour
        self.hunger = max(0, self.hunger - (5.0 * time_elapsed))
        self.thirst = max(0, self.thirst - (10.0 * time_elapsed))
        self.stamina = min(100, self.stamina + (20.0 * time_elapsed))  # Recover when resting

        # Health degradation from hunger/thirst
        if self.hunger < 20:
            self.health = max(0, self.health - (2.0 * time_elapsed))
        if self.thirst < 20:
            self.health = max(0, self.health - (5.0 * time_elapsed))

        # Morale affected by health
        if self.health < 50:
            self.morale = max(0, self.morale - (1.0 * time_elapsed))

        self.last_update = datetime.now().timestamp()

    def eat(self, nutrition: float):
        """Consume food"""
        self.hunger = min(100, self.hunger + nutrition)

    def drink(self, hydration: float):
        """Consume water"""
        self.thirst = min(100, self.thirst + hydration)

    def rest(self, hours: float):
        """Rest to recover stamina"""
        self.stamina = min(100, self.stamina + (30.0 * hours))
        self.update(hours)

    def take_damage(self, amount: float):
        """Reduce health"""
        self.health = max(0, self.health - amount)

    def heal(self, amount: float):
        """Restore health"""
        self.health = min(100, self.health + amount)

    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.health > 0

    def get_status(self) -> str:
        """Get overall status"""
        if self.health < 20:
            return "critical"
        elif self.health < 50:
            return "injured"
        elif self.hunger < 30 or self.thirst < 30:
            return "struggling"
        elif self.stamina < 30:
            return "exhausted"
        else:
            return "healthy"


class MapCell:
    """Map cell with terrain and events"""

    def __init__(self, x: int, y: int, terrain: str = "plains"):
        self.x = x
        self.y = y
        self.terrain = terrain  # plains, forest, mountain, water, desert, urban
        self.explored = False
        self.items = []
        self.threats = []
        self.resources = []
        self.events = []

    def add_item(self, item: Item):
        """Add item to cell"""
        self.items.append(item)

    def add_threat(self, threat: Dict):
        """Add threat/enemy to cell"""
        self.threats.append(threat)

    def add_resource(self, resource: Dict):
        """Add resource node to cell"""
        self.resources.append(resource)

    def explore(self):
        """Mark cell as explored"""
        self.explored = True

    def is_safe(self) -> bool:
        """Check if cell is safe"""
        return len(self.threats) == 0


class GameMap:
    """NetHack-style game map"""

    def __init__(self, width: int = 30, height: int = 30):
        self.width = width
        self.height = height
        self.cells = {}  # (x, y) -> MapCell
        self.player_pos = (0, 0)

        # Initialize map
        for y in range(height):
            for x in range(width):
                self.cells[(x, y)] = MapCell(x, y)

    def get_cell(self, x: int, y: int) -> Optional[MapCell]:
        """Get cell at position"""
        return self.cells.get((x, y))

    def move_player(self, dx: int, dy: int) -> bool:
        """Move player relative to current position"""
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        # Check bounds
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            return False

        self.player_pos = (new_x, new_y)
        cell = self.get_cell(new_x, new_y)
        if cell:
            cell.explore()

        return True

    def get_current_cell(self) -> Optional[MapCell]:
        """Get cell at player position"""
        return self.get_cell(*self.player_pos)

    def get_visible_cells(self, radius: int = 5) -> List[MapCell]:
        """Get cells within visibility radius"""
        px, py = self.player_pos
        visible = []

        for y in range(max(0, py - radius), min(self.height, py + radius + 1)):
            for x in range(max(0, px - radius), min(self.width, px + radius + 1)):
                cell = self.get_cell(x, y)
                if cell:
                    visible.append(cell)

        return visible


class Mission:
    """Adventure mission/quest"""

    def __init__(self, id: str, title: str, description: str):
        self.id = id
        self.title = title
        self.description = description
        self.objectives = []
        self.rewards = {}
        self.requirements = {}
        self.state = "available"  # available, active, completed, failed
        self.progress = 0.0

    def add_objective(self, obj_id: str, description: str, required: bool = True):
        """Add mission objective"""
        self.objectives.append({
            'id': obj_id,
            'description': description,
            'required': required,
            'completed': False,
            'progress': 0.0
        })

    def complete_objective(self, obj_id: str) -> bool:
        """Mark objective as completed"""
        for obj in self.objectives:
            if obj['id'] == obj_id:
                obj['completed'] = True
                obj['progress'] = 100.0
                self._update_progress()
                return True
        return False

    def update_objective_progress(self, obj_id: str, progress: float):
        """Update objective progress"""
        for obj in self.objectives:
            if obj['id'] == obj_id:
                obj['progress'] = min(100.0, progress)
                self._update_progress()
                break

    def _update_progress(self):
        """Calculate overall mission progress"""
        if not self.objectives:
            self.progress = 0.0
            return

        total = sum(obj['progress'] for obj in self.objectives)
        self.progress = total / len(self.objectives)

        # Check if mission complete
        required_complete = all(
            obj['completed'] for obj in self.objectives if obj['required']
        )
        if required_complete:
            self.state = "completed"

    def is_available(self, player_level: int, inventory: Inventory) -> bool:
        """Check if mission is available to player"""
        # Check level requirement
        if 'min_level' in self.requirements:
            if player_level < self.requirements['min_level']:
                return False

        # Check item requirements
        if 'items' in self.requirements:
            for item_id, quantity in self.requirements['items'].items():
                if not inventory.has_item(item_id, quantity):
                    return False

        return True


class AdventureGame:
    """Main adventure game controller"""

    def __init__(self, player_name: str):
        self.player_name = player_name
        self.stats = SurvivalStats()
        self.inventory = Inventory()
        self.game_map = GameMap()
        self.current_scenario = None
        self.missions = {}  # id -> Mission
        self.active_missions = []
        self.game_time = 0.0  # In-game hours
        self.real_start = datetime.now().timestamp()

    def start_scenario(self, scenario: Scenario):
        """Start interactive scenario"""
        self.current_scenario = scenario

    def advance_time(self, hours: float):
        """Advance game time and update stats"""
        self.game_time += hours
        self.stats.update(hours)

    def add_mission(self, mission: Mission):
        """Add mission to game"""
        self.missions[mission.id] = mission

    def start_mission(self, mission_id: str) -> bool:
        """Activate a mission"""
        mission = self.missions.get(mission_id)
        if not mission or mission.state != "available":
            return False

        # Check availability
        if not mission.is_available(1, self.inventory):  # TODO: track player level
            return False

        mission.state = "active"
        self.active_missions.append(mission_id)
        return True

    def get_active_missions(self) -> List[Mission]:
        """Get all active missions"""
        return [self.missions[mid] for mid in self.active_missions]


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestScenarioSystem(unittest.TestCase):
    """Test scenario/story system (12 tests)"""

    def test_scenario_creation(self):
        """Test scenario initialization"""
        scenario = Scenario('test1', 'First Quest', 'A test scenario', 'easy')
        self.assertEqual(scenario.title, 'First Quest')
        self.assertEqual(scenario.state, ScenarioState.ACTIVE)
        self.assertEqual(scenario.current_step, 0)

    def test_add_steps(self):
        """Test adding scenario steps"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('step1', 'You wake up...', [
            {'text': 'Go left', 'next_step': 1},
            {'text': 'Go right', 'next_step': 2}
        ])

        self.assertEqual(len(scenario.steps), 1)
        self.assertEqual(scenario.steps[0]['id'], 'step1')
        self.assertEqual(len(scenario.steps[0]['choices']), 2)

    def test_make_choice(self):
        """Test making choices"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('step1', 'Choose path', [
            {'text': 'Left', 'next_step': 1},
            {'text': 'Right', 'next_step': 2}
        ])
        scenario.add_step('step2', 'Left path')
        scenario.add_step('step3', 'Right path')

        result = scenario.make_choice(1)  # Choose right
        self.assertTrue(result)
        self.assertEqual(scenario.current_step, 2)
        self.assertEqual(len(scenario.choices_made), 1)

    def test_invalid_choice(self):
        """Test invalid choice index"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('step1', 'Choose', [{'text': 'Only option'}])

        result = scenario.make_choice(5)
        self.assertFalse(result)

    def test_scenario_completion(self):
        """Test completing scenario"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.complete(success=True)

        self.assertEqual(scenario.state, ScenarioState.COMPLETED)
        self.assertIsNotNone(scenario.completion_time)

    def test_scenario_failure(self):
        """Test failing scenario"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.complete(success=False)

        self.assertEqual(scenario.state, ScenarioState.FAILED)

    def test_scenario_duration(self):
        """Test scenario duration tracking"""
        scenario = Scenario('test1', 'Quest', 'Description')
        import time
        time.sleep(0.01)
        duration = scenario.get_duration()

        self.assertGreater(duration, 0)

    def test_difficulty_levels(self):
        """Test different difficulty settings"""
        easy = Scenario('e1', 'Easy', 'Desc', 'easy')
        hard = Scenario('h1', 'Hard', 'Desc', 'hard')
        extreme = Scenario('x1', 'Extreme', 'Desc', 'extreme')

        self.assertEqual(easy.difficulty, 'easy')
        self.assertEqual(hard.difficulty, 'hard')
        self.assertEqual(extreme.difficulty, 'extreme')

    def test_choice_tracking(self):
        """Test choice history tracking"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('s1', 'Step 1', [{'text': 'A'}, {'text': 'B'}])
        scenario.add_step('s2', 'Step 2', [{'text': 'C'}])

        scenario.make_choice(0)
        scenario.make_choice(0)

        self.assertEqual(len(scenario.choices_made), 2)
        self.assertEqual(scenario.choices_made[0]['step'], 0)

    def test_step_visited_flag(self):
        """Test step visited tracking"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('s1', 'Step', [{'text': 'Next'}])

        self.assertFalse(scenario.steps[0]['visited'])
        scenario.make_choice(0)
        self.assertTrue(scenario.steps[0]['visited'])

    def test_linear_progression(self):
        """Test linear step progression"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('s1', 'Step 1', [{'text': 'Next'}])
        scenario.add_step('s2', 'Step 2', [{'text': 'Next'}])
        scenario.add_step('s3', 'Step 3')

        scenario.make_choice(0)
        self.assertEqual(scenario.current_step, 1)
        scenario.make_choice(0)
        self.assertEqual(scenario.current_step, 2)

    def test_branching_narrative(self):
        """Test branching story paths"""
        scenario = Scenario('test1', 'Quest', 'Description')
        scenario.add_step('s1', 'Fork', [
            {'text': 'Path A', 'next_step': 1},
            {'text': 'Path B', 'next_step': 2}
        ])
        scenario.add_step('s2', 'Path A result')
        scenario.add_step('s3', 'Path B result')

        scenario.make_choice(0)  # Choose Path A
        self.assertEqual(scenario.current_step, 1)


class TestResourceInventory(unittest.TestCase):
    """Test resource and inventory system (10 tests)"""

    def test_item_creation(self):
        """Test creating items"""
        item = Item('water_bottle', 'Water Bottle', ItemType.WATER, weight=0.5)
        self.assertEqual(item.name, 'Water Bottle')
        self.assertEqual(item.item_type, ItemType.WATER)
        self.assertEqual(item.quantity, 1)

    def test_item_use(self):
        """Test using/consuming items"""
        item = Item('food', 'Canned Food', ItemType.FOOD)
        item.quantity = 5

        result = item.use(2)
        self.assertTrue(result)
        self.assertEqual(item.quantity, 3)

    def test_item_durability(self):
        """Test item durability system"""
        tool = Item('axe', 'Axe', ItemType.TOOL, stackable=False)
        tool.degrade(30)

        self.assertEqual(tool.durability, 70)
        tool.repair(20)
        self.assertEqual(tool.durability, 90)

    def test_inventory_add(self):
        """Test adding items to inventory"""
        inv = Inventory(max_weight=10.0)
        item = Item('food', 'Food', ItemType.FOOD, weight=1.0)

        result = inv.add_item(item)
        self.assertTrue(result)
        self.assertEqual(len(inv.items), 1)

    def test_inventory_weight_limit(self):
        """Test inventory weight constraints"""
        inv = Inventory(max_weight=5.0)
        heavy_item = Item('boulder', 'Boulder', ItemType.RESOURCE, weight=10.0)

        result = inv.add_item(heavy_item)
        self.assertFalse(result)

    def test_inventory_stacking(self):
        """Test item stacking"""
        inv = Inventory()
        item1 = Item('food', 'Food', ItemType.FOOD)
        item2 = Item('food', 'Food', ItemType.FOOD)
        item2.quantity = 3

        inv.add_item(item1)
        inv.add_item(item2)

        self.assertEqual(len(inv.items), 1)
        self.assertEqual(inv.items['food'].quantity, 4)

    def test_inventory_remove(self):
        """Test removing items"""
        inv = Inventory()
        item = Item('food', 'Food', ItemType.FOOD)
        item.quantity = 5
        inv.add_item(item)

        result = inv.remove_item('food', 2)
        self.assertTrue(result)
        self.assertEqual(inv.items['food'].quantity, 3)

    def test_inventory_has_item(self):
        """Test checking item existence"""
        inv = Inventory()
        item = Item('key', 'Key', ItemType.QUEST, stackable=False)
        inv.add_item(item)

        self.assertTrue(inv.has_item('key'))
        self.assertFalse(inv.has_item('sword'))

    def test_inventory_by_type(self):
        """Test getting items by type"""
        inv = Inventory()
        inv.add_item(Item('food1', 'Apple', ItemType.FOOD))
        inv.add_item(Item('food2', 'Bread', ItemType.FOOD))
        inv.add_item(Item('tool1', 'Axe', ItemType.TOOL))

        food_items = inv.get_items_by_type(ItemType.FOOD)
        self.assertEqual(len(food_items), 2)

    def test_inventory_total_weight(self):
        """Test total weight calculation"""
        inv = Inventory()
        inv.add_item(Item('i1', 'Item 1', ItemType.RESOURCE, weight=2.0))
        inv.add_item(Item('i2', 'Item 2', ItemType.RESOURCE, weight=3.0))

        self.assertEqual(inv.get_total_weight(), 5.0)


class TestSurvivalMechanics(unittest.TestCase):
    """Test survival stat system (10 tests)"""

    def test_stats_initialization(self):
        """Test survival stats start at full"""
        stats = SurvivalStats()
        self.assertEqual(stats.health, 100.0)
        self.assertEqual(stats.hunger, 100.0)
        self.assertEqual(stats.thirst, 100.0)

    def test_hunger_degradation(self):
        """Test hunger decreases over time"""
        stats = SurvivalStats()
        stats.update(time_elapsed=2.0)  # 2 hours

        self.assertLess(stats.hunger, 100.0)
        self.assertGreaterEqual(stats.hunger, 90.0)  # 5 per hour

    def test_thirst_degradation(self):
        """Test thirst decreases faster than hunger"""
        stats = SurvivalStats()
        stats.update(time_elapsed=1.0)

        hunger_loss = 100.0 - stats.hunger
        thirst_loss = 100.0 - stats.thirst

        self.assertGreater(thirst_loss, hunger_loss)

    def test_eating(self):
        """Test eating restores hunger"""
        stats = SurvivalStats()
        stats.hunger = 50.0
        stats.eat(30.0)

        self.assertEqual(stats.hunger, 80.0)

    def test_drinking(self):
        """Test drinking restores thirst"""
        stats = SurvivalStats()
        stats.thirst = 40.0
        stats.drink(50.0)

        self.assertEqual(stats.thirst, 90.0)

    def test_resting(self):
        """Test resting recovers stamina"""
        stats = SurvivalStats()
        stats.stamina = 30.0
        stats.rest(2.0)  # 2 hours

        self.assertGreater(stats.stamina, 30.0)

    def test_health_from_starvation(self):
        """Test low hunger damages health"""
        stats = SurvivalStats()
        stats.hunger = 10.0
        stats.update(time_elapsed=1.0)

        self.assertLess(stats.health, 100.0)

    def test_health_from_dehydration(self):
        """Test low thirst damages health"""
        stats = SurvivalStats()
        stats.thirst = 10.0
        stats.update(time_elapsed=1.0)

        self.assertLess(stats.health, 100.0)

    def test_is_alive(self):
        """Test alive/dead status"""
        stats = SurvivalStats()
        self.assertTrue(stats.is_alive())

        stats.health = 0.0
        self.assertFalse(stats.is_alive())

    def test_status_levels(self):
        """Test status classification"""
        stats = SurvivalStats()

        self.assertEqual(stats.get_status(), 'healthy')

        stats.health = 40.0
        self.assertEqual(stats.get_status(), 'injured')

        stats.health = 10.0
        self.assertEqual(stats.get_status(), 'critical')


class TestMapGameplay(unittest.TestCase):
    """Test NetHack-style map (10 tests)"""

    def test_map_creation(self):
        """Test map initialization"""
        game_map = GameMap(width=10, height=10)
        self.assertEqual(game_map.width, 10)
        self.assertEqual(game_map.height, 10)
        self.assertEqual(len(game_map.cells), 100)

    def test_player_movement(self):
        """Test player can move"""
        game_map = GameMap(10, 10)
        game_map.player_pos = (5, 5)

        result = game_map.move_player(1, 0)  # Move right
        self.assertTrue(result)
        self.assertEqual(game_map.player_pos, (6, 5))

    def test_movement_bounds(self):
        """Test movement respects map bounds"""
        game_map = GameMap(10, 10)
        game_map.player_pos = (0, 0)

        result = game_map.move_player(-1, 0)  # Try to go left from edge
        self.assertFalse(result)
        self.assertEqual(game_map.player_pos, (0, 0))

    def test_cell_exploration(self):
        """Test cells get explored on visit"""
        game_map = GameMap(10, 10)
        cell = game_map.get_current_cell()

        self.assertFalse(cell.explored)
        game_map.move_player(1, 0)
        new_cell = game_map.get_current_cell()
        self.assertTrue(new_cell.explored)

    def test_cell_items(self):
        """Test adding items to cells"""
        game_map = GameMap(10, 10)
        cell = game_map.get_cell(5, 5)
        item = Item('sword', 'Sword', ItemType.WEAPON)

        cell.add_item(item)
        self.assertEqual(len(cell.items), 1)

    def test_cell_threats(self):
        """Test adding threats to cells"""
        game_map = GameMap(10, 10)
        cell = game_map.get_cell(5, 5)

        self.assertTrue(cell.is_safe())
        cell.add_threat({'name': 'Wolf', 'level': 3})
        self.assertFalse(cell.is_safe())

    def test_terrain_types(self):
        """Test different terrain types"""
        game_map = GameMap(10, 10)
        cell = game_map.get_cell(0, 0)

        cell.terrain = 'forest'
        self.assertEqual(cell.terrain, 'forest')

    def test_visible_cells(self):
        """Test getting visible cells"""
        game_map = GameMap(10, 10)
        game_map.player_pos = (5, 5)

        visible = game_map.get_visible_cells(radius=2)
        self.assertGreater(len(visible), 0)
        self.assertLessEqual(len(visible), 25)  # 5x5 area

    def test_cell_resources(self):
        """Test resource nodes in cells"""
        game_map = GameMap(10, 10)
        cell = game_map.get_cell(3, 3)

        cell.add_resource({'type': 'water', 'amount': 10})
        self.assertEqual(len(cell.resources), 1)

    def test_diagonal_movement(self):
        """Test diagonal movement"""
        game_map = GameMap(10, 10)
        game_map.player_pos = (5, 5)

        game_map.move_player(1, 1)  # Move diagonally
        self.assertEqual(game_map.player_pos, (6, 6))


class TestMissionSystem(unittest.TestCase):
    """Test mission/quest system (10 tests)"""

    def test_mission_creation(self):
        """Test creating missions"""
        mission = Mission('m1', 'Find Water', 'Locate water source')
        self.assertEqual(mission.title, 'Find Water')
        self.assertEqual(mission.state, 'available')

    def test_add_objectives(self):
        """Test adding mission objectives"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.add_objective('obj1', 'Find item', required=True)
        mission.add_objective('obj2', 'Optional task', required=False)

        self.assertEqual(len(mission.objectives), 2)

    def test_complete_objective(self):
        """Test completing objectives"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.add_objective('obj1', 'Task 1')

        result = mission.complete_objective('obj1')
        self.assertTrue(result)
        self.assertTrue(mission.objectives[0]['completed'])

    def test_objective_progress(self):
        """Test updating objective progress"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.add_objective('obj1', 'Collect 10 items')

        mission.update_objective_progress('obj1', 50.0)
        self.assertEqual(mission.objectives[0]['progress'], 50.0)

    def test_mission_progress_calculation(self):
        """Test overall mission progress"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.add_objective('obj1', 'Task 1')
        mission.add_objective('obj2', 'Task 2')

        mission.update_objective_progress('obj1', 100.0)
        mission.update_objective_progress('obj2', 50.0)

        self.assertEqual(mission.progress, 75.0)

    def test_mission_completion(self):
        """Test mission auto-completes"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.add_objective('obj1', 'Task 1', required=True)

        mission.complete_objective('obj1')
        self.assertEqual(mission.state, 'completed')

    def test_optional_objectives(self):
        """Test optional objectives don't block completion"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.add_objective('obj1', 'Required', required=True)
        mission.add_objective('obj2', 'Optional', required=False)

        mission.complete_objective('obj1')
        self.assertEqual(mission.state, 'completed')

    def test_mission_requirements(self):
        """Test mission level requirements"""
        mission = Mission('m1', 'Hard Quest', 'Description')
        mission.requirements['min_level'] = 10

        inv = Inventory()
        self.assertFalse(mission.is_available(5, inv))
        self.assertTrue(mission.is_available(10, inv))

    def test_mission_item_requirements(self):
        """Test mission item requirements"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.requirements['items'] = {'key': 1}

        inv = Inventory()
        self.assertFalse(mission.is_available(1, inv))

        inv.add_item(Item('key', 'Key', ItemType.QUEST))
        self.assertTrue(mission.is_available(1, inv))

    def test_mission_rewards(self):
        """Test mission reward structure"""
        mission = Mission('m1', 'Quest', 'Description')
        mission.rewards = {'xp': 100, 'items': ['sword']}

        self.assertEqual(mission.rewards['xp'], 100)
        self.assertIn('sword', mission.rewards['items'])


class TestIntegration(unittest.TestCase):
    """Integration tests (8 tests)"""

    def test_full_adventure_workflow(self):
        """Test complete adventure game flow"""
        game = AdventureGame('Player1')

        # Add item to inventory
        food = Item('food', 'Food', ItemType.FOOD)
        game.inventory.add_item(food)

        # Advance time
        game.advance_time(1.0)

        # Check stats updated
        self.assertLess(game.stats.hunger, 100.0)
        self.assertTrue(game.stats.is_alive())

    def test_scenario_with_survival(self):
        """Test scenario affects survival stats"""
        game = AdventureGame('Player1')
        scenario = Scenario('s1', 'Lost in Desert', 'Find water')
        scenario.add_step('s1', 'You are thirsty', [
            {'text': 'Drink from canteen', 'next_step': 1}
        ])

        game.start_scenario(scenario)
        game.stats.thirst = 50.0

        # Make choice to drink
        scenario.make_choice(0)
        game.stats.drink(30.0)

        self.assertEqual(game.stats.thirst, 80.0)

    def test_map_exploration_finds_items(self):
        """Test exploring map reveals items"""
        game = AdventureGame('Player1')

        # Place item on map
        cell = game.game_map.get_cell(1, 0)
        item = Item('water', 'Water', ItemType.WATER)
        cell.add_item(item)

        # Move to cell
        game.game_map.move_player(1, 0)
        current_cell = game.game_map.get_current_cell()

        self.assertTrue(current_cell.explored)
        self.assertEqual(len(current_cell.items), 1)

    def test_mission_with_inventory(self):
        """Test mission requires inventory items"""
        game = AdventureGame('Player1')
        mission = Mission('m1', 'Repair Tool', 'Description')
        mission.requirements['items'] = {'parts': 3}
        mission.add_objective('obj1', 'Fix the generator')

        game.add_mission(mission)

        # Can't start without parts
        result = game.start_mission('m1')
        self.assertFalse(result)

        # Add parts and try again
        parts = Item('parts', 'Parts', ItemType.RESOURCE)
        parts.quantity = 3
        game.inventory.add_item(parts)

        result = game.start_mission('m1')
        self.assertTrue(result)

    def test_survival_death_scenario(self):
        """Test player can die from starvation"""
        game = AdventureGame('Player1')

        # Simulate severe starvation and dehydration
        game.stats.hunger = 0
        game.stats.thirst = 0

        # Update over time - need more hours for death with current damage rates
        # At 5 damage/hour from dehydration + 2/hour from starvation = 7 damage/hour
        # Need ~15 hours to drop from 100 to 0 health
        for _ in range(15):
            game.advance_time(1.0)

        self.assertFalse(game.stats.is_alive())

    def test_threat_combat_scenario(self):
        """Test encountering threats on map"""
        game = AdventureGame('Player1')

        # Add threat to next cell
        cell = game.game_map.get_cell(1, 0)
        cell.add_threat({'name': 'Wolf', 'damage': 20})

        # Move to cell with threat
        game.game_map.move_player(1, 0)
        current_cell = game.game_map.get_current_cell()

        self.assertFalse(current_cell.is_safe())

        # Simulate taking damage from threat
        threat = current_cell.threats[0]
        game.stats.take_damage(threat['damage'])

        self.assertEqual(game.stats.health, 80.0)

    def test_resource_gathering(self):
        """Test gathering resources from map"""
        game = AdventureGame('Player1')

        # Add resource to cell
        cell = game.game_map.get_cell(2, 2)
        cell.add_resource({'type': 'wood', 'amount': 5})

        # Move to cell
        game.game_map.player_pos = (2, 2)
        current_cell = game.game_map.get_current_cell()

        # Gather resource
        resource = current_cell.resources[0]
        wood = Item('wood', 'Wood', ItemType.RESOURCE)
        wood.quantity = resource['amount']
        game.inventory.add_item(wood)

        self.assertTrue(game.inventory.has_item('wood', 5))

    def test_time_based_events(self):
        """Test time passage triggers events"""
        game = AdventureGame('Player1')

        # Start well-fed
        initial_hunger = game.stats.hunger

        # Advance 5 hours
        game.advance_time(5.0)

        # Check time advanced and stats degraded
        self.assertEqual(game.game_time, 5.0)
        self.assertLess(game.stats.hunger, initial_hunger)
        self.assertLess(game.stats.thirst, 100.0)


def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestScenarioSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceInventory))
    suite.addTests(loader.loadTestsFromTestCase(TestSurvivalMechanics))
    suite.addTests(loader.loadTestsFromTestCase(TestMapGameplay))
    suite.addTests(loader.loadTestsFromTestCase(TestMissionSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
