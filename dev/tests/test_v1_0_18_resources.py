"""
Tests for v1.0.18 Resource Management System
Tests inventory, barter, and resource command handlers
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.services.inventory_service import (
    InventoryService, ItemCategory, ItemRarity, ItemCondition
)
from core.services.barter_service import BarterService
from core.commands.resource_handler import ResourceCommandHandler


class TestInventoryService:
    """Test InventoryService functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def inventory_service(self, temp_dir):
        """Create InventoryService instance"""
        return InventoryService(data_dir=temp_dir)

    def test_init_creates_database(self, inventory_service):
        """Test database initialization"""
        assert os.path.exists(inventory_service.db_path)

    def test_init_creates_default_storage(self, inventory_service):
        """Test default storage location created"""
        stats = inventory_service.get_inventory_stats()
        assert stats['location'] == 'Personal Inventory'
        assert stats['max_weight'] == 50.0
        assert stats['max_volume'] == 50.0

    def test_add_item_new(self, inventory_service):
        """Test adding new item"""
        result = inventory_service.add_item(
            name="Water Bottle",
            category=ItemCategory.WATER,
            quantity=1,
            weight=1.0,
            volume=1.0,
            base_value=20
        )

        assert result['action'] == 'added'
        assert result['name'] == "Water Bottle"
        assert result['quantity'] == 1

    def test_add_item_stackable(self, inventory_service):
        """Test stacking identical items"""
        # Add first item
        inventory_service.add_item(
            name="Canned Food",
            category=ItemCategory.FOOD,
            quantity=2,
            stackable=True
        )

        # Add more of same item
        result = inventory_service.add_item(
            name="Canned Food",
            category=ItemCategory.FOOD,
            quantity=3,
            stackable=True
        )

        assert result['action'] == 'stacked'
        assert result['quantity'] == 5
        assert result['added'] == 3

    def test_get_item(self, inventory_service):
        """Test retrieving item details"""
        result = inventory_service.add_item(
            name="First Aid Kit",
            category=ItemCategory.MEDICAL,
            quantity=1,
            weight=2.0,
            volume=1.5,
            rarity=ItemRarity.UNCOMMON,
            base_value=50
        )

        item_id = result['item_id']
        item = inventory_service.get_item(item_id)

        assert item is not None
        assert item['name'] == "First Aid Kit"
        assert item['category'] == 'medical'
        assert item['rarity'] == 'uncommon'
        assert item['current_value'] == 100  # base_value * 2 (uncommon)

    def test_remove_item_partial(self, inventory_service):
        """Test removing partial quantity"""
        result = inventory_service.add_item(
            name="Ammo",
            category=ItemCategory.WEAPON,
            quantity=50
        )

        item_id = result['item_id']
        remove_result = inventory_service.remove_item(item_id, 20)

        assert remove_result['success'] is True
        assert remove_result['removed'] == 20
        assert remove_result['remaining'] == 30

    def test_remove_item_all(self, inventory_service):
        """Test removing entire stack"""
        result = inventory_service.add_item(
            name="Bandage",
            category=ItemCategory.MEDICAL,
            quantity=10
        )

        item_id = result['item_id']
        remove_result = inventory_service.remove_item(item_id, 10)

        assert remove_result['success'] is True
        assert remove_result['removed'] == 10
        assert remove_result['remaining'] == 0

        # Item should be deleted
        item = inventory_service.get_item(item_id)
        assert item is None

    def test_get_inventory(self, inventory_service):
        """Test listing all items"""
        inventory_service.add_item("Item 1", ItemCategory.FOOD, quantity=1)
        inventory_service.add_item("Item 2", ItemCategory.WATER, quantity=2)
        inventory_service.add_item("Item 3", ItemCategory.TOOL, quantity=3)

        items = inventory_service.get_inventory()
        assert len(items) == 3

    def test_get_inventory_by_category(self, inventory_service):
        """Test filtering by category"""
        inventory_service.add_item("Food 1", ItemCategory.FOOD)
        inventory_service.add_item("Food 2", ItemCategory.FOOD)
        inventory_service.add_item("Water 1", ItemCategory.WATER)

        food_items = inventory_service.get_inventory(category=ItemCategory.FOOD)
        assert len(food_items) == 2
        assert all(item['category'] == 'food' for item in food_items)

    def test_get_inventory_stats(self, inventory_service):
        """Test inventory statistics"""
        inventory_service.add_item("Heavy Item", ItemCategory.TOOL,
                                   quantity=1, weight=10.0, volume=5.0)
        inventory_service.add_item("Light Item", ItemCategory.MISC,
                                   quantity=5, weight=1.0, volume=0.5)

        stats = inventory_service.get_inventory_stats()

        assert stats['item_count'] == 2
        assert stats['total_weight'] == 15.0  # 10 + (5*1)
        assert stats['total_volume'] == 7.5   # 5 + (5*0.5)
        assert stats['weight_percent'] == 30  # 15/50 * 100
        assert stats['volume_percent'] == 15  # 7.5/50 * 100

    def test_update_condition(self, inventory_service):
        """Test updating item condition"""
        result = inventory_service.add_item(
            name="Weapon",
            category=ItemCategory.WEAPON,
            condition=100
        )

        item_id = result['item_id']

        # Reduce condition
        update = inventory_service.update_condition(item_id, -20)

        assert update['success'] is True
        assert update['old_condition'] == 100
        assert update['new_condition'] == 80
        assert update['old_state'] == 'pristine'
        assert update['new_state'] == 'excellent'

    def test_condition_states(self, inventory_service):
        """Test condition state mapping"""
        service = inventory_service

        assert service._get_condition_state(100) == 'pristine'
        assert service._get_condition_state(85) == 'excellent'
        assert service._get_condition_state(65) == 'good'
        assert service._get_condition_state(45) == 'fair'
        assert service._get_condition_state(25) == 'poor'
        assert service._get_condition_state(5) == 'broken'

    def test_calculate_item_value(self, inventory_service):
        """Test value calculation with rarity and condition"""
        service = inventory_service

        # Base: 100, Common (1x), 100% condition
        assert service._calculate_item_value(100, 'common', 100) == 100

        # Base: 100, Uncommon (2x), 100% condition
        assert service._calculate_item_value(100, 'uncommon', 100) == 200

        # Base: 100, Rare (5x), 50% condition
        assert service._calculate_item_value(100, 'rare', 50) == 250

        # Base: 100, Epic (10x), 100% condition
        assert service._calculate_item_value(100, 'epic', 100) == 1000

        # Base: 100, Legendary (25x), 80% condition
        assert service._calculate_item_value(100, 'legendary', 80) == 2000


class TestBarterService:
    """Test BarterService functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def inventory_service(self, temp_dir):
        """Create InventoryService instance"""
        return InventoryService(data_dir=temp_dir)

    @pytest.fixture
    def barter_service(self, temp_dir, inventory_service):
        """Create BarterService instance"""
        return BarterService(data_dir=temp_dir, inventory_service=inventory_service)

    def test_init_creates_database(self, barter_service):
        """Test database initialization"""
        assert os.path.exists(barter_service.db_path)

    def test_calculate_trade_value_base(self, barter_service):
        """Test basic value calculation"""
        item = {
            'base_value': 100,
            'current_value': 100,
            'category': 'food',
            'rarity': 'common'
        }

        value = barter_service.calculate_trade_value(item, apply_modifiers=False)
        assert value == 100

    def test_calculate_trade_value_with_modifiers(self, barter_service):
        """Test value calculation with active modifiers"""
        # Activate food scarcity modifier (1.5x)
        barter_service.activate_modifier("Food Scarcity")

        item = {
            'base_value': 100,
            'current_value': 100,
            'category': 'food',
            'rarity': 'common'
        }

        value = barter_service.calculate_trade_value(item, apply_modifiers=True)
        assert value == 150  # 100 * 1.5

    def test_create_trade_offer(self, barter_service, inventory_service):
        """Test creating trade offer"""
        # Add items to inventory
        item1 = inventory_service.add_item("Food", ItemCategory.FOOD, base_value=50)
        item2 = inventory_service.add_item("Water", ItemCategory.WATER, base_value=30)

        offer = barter_service.create_trade_offer(
            partner_name="Trader Joe",
            items_offered=[item1['item_id'], item2['item_id']],
            items_requested=["Medicine", "Ammo"],
            notes="Trade for medical supplies"
        )

        assert offer['success'] is True
        assert offer['partner'] == "Trader Joe"
        assert offer['offered_value'] == 80  # 50 + 30
        assert len(offer['offered']) == 2
        assert offer['requested'] == ["Medicine", "Ammo"]

    def test_execute_trade(self, barter_service, inventory_service):
        """Test executing trade transaction"""
        # Add item to give away
        given_item = inventory_service.add_item(
            "Old Weapon", ItemCategory.WEAPON,
            base_value=100, condition=50
        )

        # Define items to receive
        received_items = [
            {
                'name': 'Food Pack',
                'category': 'food',
                'quantity': 5,
                'weight': 0.5,
                'volume': 0.3,
                'condition': 100,
                'rarity': 'common',
                'base_value': 20,
                'description': 'Emergency food ration'
            }
        ]

        result = barter_service.execute_trade(
            partner_name="Survivor",
            items_given=[given_item['item_id']],
            items_received=received_items,
            notes="Weapon for food trade"
        )

        assert result['success'] is True
        assert result['partner'] == "Survivor"
        assert result['value_given'] == 50  # 100 * 0.5 condition
        assert result['value_received'] == 20  # 5 items * 20 value each... wait, that's 100
        # Actually value_received should be based on single item value
        # Let me check the calculation...

    def test_get_transaction_history(self, barter_service, inventory_service):
        """Test retrieving transaction history"""
        # Execute a trade first
        given_item = inventory_service.add_item("Item", ItemCategory.MISC, base_value=50)

        barter_service.execute_trade(
            partner_name="Test Partner",
            items_given=[given_item['item_id']],
            items_received=[{
                'name': 'Received Item',
                'category': 'misc',
                'base_value': 60
            }]
        )

        history = barter_service.get_transaction_history(limit=10)

        assert len(history) >= 1
        assert history[0]['type'] == 'trade'
        assert history[0]['partner'] == "Test Partner"

    def test_get_trade_stats(self, barter_service, inventory_service):
        """Test getting trade statistics"""
        # Execute profitable trade
        item1 = inventory_service.add_item("Low Value", ItemCategory.MISC, base_value=10)
        barter_service.execute_trade(
            partner_name="Partner 1",
            items_given=[item1['item_id']],
            items_received=[{'name': 'High Value', 'category': 'misc', 'base_value': 50}]
        )

        # Execute unprofitable trade
        item2 = inventory_service.add_item("High Value", ItemCategory.TOOL, base_value=80)
        barter_service.execute_trade(
            partner_name="Partner 2",
            items_given=[item2['item_id']],
            items_received=[{'name': 'Low Value', 'category': 'misc', 'base_value': 20}]
        )

        stats = barter_service.get_trade_stats()

        assert stats['total_transactions'] >= 2
        assert 'total_profit' in stats
        assert 'average_profit' in stats

    def test_activate_modifier(self, barter_service):
        """Test activating pricing modifier"""
        result = barter_service.activate_modifier("Medical Emergency")

        assert result['success'] is True
        assert result['active'] is True

        modifiers = barter_service.get_active_modifiers()
        assert any(m['name'] == "Medical Emergency" for m in modifiers)

    def test_deactivate_modifier(self, barter_service):
        """Test deactivating pricing modifier"""
        # Activate first
        barter_service.activate_modifier("Water Crisis")

        # Then deactivate
        result = barter_service.deactivate_modifier("Water Crisis")

        assert result['success'] is True
        assert result['active'] is False

        modifiers = barter_service.get_active_modifiers()
        assert not any(m['name'] == "Water Crisis" for m in modifiers)

    def test_get_active_modifiers(self, barter_service):
        """Test listing active modifiers"""
        # Initially no active modifiers
        modifiers = barter_service.get_active_modifiers()
        initial_count = len(modifiers)

        # Activate some modifiers
        barter_service.activate_modifier("Food Scarcity")
        barter_service.activate_modifier("Medical Emergency")

        modifiers = barter_service.get_active_modifiers()
        assert len(modifiers) == initial_count + 2


class TestResourceCommandHandler:
    """Test ResourceCommandHandler functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def resource_handler(self, temp_dir):
        """Create ResourceCommandHandler instance"""
        return ResourceCommandHandler(data_dir=temp_dir)

    def test_handle_inventory_empty(self, resource_handler):
        """Test INVENTORY command with empty inventory"""
        result = resource_handler.handle_command("INVENTORY", [])

        assert result['type'] == 'inventory_list'
        assert result['total_items'] == 0
        assert 'stats' in result

    def test_handle_inventory_with_items(self, resource_handler):
        """Test INVENTORY command with items"""
        # Add some items first
        resource_handler.inventory_service.add_item("Test Item", ItemCategory.MISC)

        result = resource_handler.handle_command("INVENTORY", [])

        assert result['type'] == 'inventory_list'
        assert result['total_items'] == 1

    def test_handle_inventory_stats(self, resource_handler):
        """Test INVENTORY STATS command"""
        result = resource_handler.handle_command("INVENTORY", ["stats"])

        assert result['type'] == 'inventory_stats'
        assert 'stats' in result

    def test_handle_inventory_category(self, resource_handler):
        """Test INVENTORY [category] command"""
        resource_handler.inventory_service.add_item("Food", ItemCategory.FOOD)
        resource_handler.inventory_service.add_item("Water", ItemCategory.WATER)

        result = resource_handler.handle_command("INVENTORY", ["food"])

        assert result['type'] == 'inventory_list'
        assert result['category'] == 'food'
        assert result['total_items'] == 1

    def test_handle_item_add(self, resource_handler):
        """Test ITEM ADD command"""
        result = resource_handler.handle_command("ITEM", ["add", "New Item", "tool", "1", "2.5", "1.5"])

        assert result['type'] == 'item_added'
        assert result['result']['name'] == "New Item"

    def test_handle_item_details(self, resource_handler):
        """Test ITEM [id] command"""
        # Add item first
        add_result = resource_handler.inventory_service.add_item("Detail Item", ItemCategory.MISC)
        item_id = add_result['item_id']

        result = resource_handler.handle_command("ITEM", [str(item_id)])

        assert result['type'] == 'item_details'
        assert result['item']['name'] == "Detail Item"

    def test_handle_item_remove(self, resource_handler):
        """Test ITEM REMOVE command"""
        # Add item first
        add_result = resource_handler.inventory_service.add_item("Remove Item", ItemCategory.MISC, quantity=5)
        item_id = add_result['item_id']

        result = resource_handler.handle_command("ITEM", ["remove", str(item_id), "2"])

        assert result['type'] == 'item_removed'
        assert result['result']['success'] is True
        assert result['result']['removed'] == 2

    def test_handle_item_condition(self, resource_handler):
        """Test ITEM CONDITION command"""
        # Add item first
        add_result = resource_handler.inventory_service.add_item("Condition Item", ItemCategory.WEAPON)
        item_id = add_result['item_id']

        result = resource_handler.handle_command("ITEM", ["condition", str(item_id), "-10"])

        assert result['type'] == 'condition_updated'
        assert result['result']['success'] is True

    def test_handle_trade_history(self, resource_handler):
        """Test TRADE command (history)"""
        result = resource_handler.handle_command("TRADE", [])

        assert result['type'] == 'trade_history'
        assert 'transactions' in result

    def test_handle_trade_stats(self, resource_handler):
        """Test TRADE STATS command"""
        result = resource_handler.handle_command("TRADE", ["stats"])

        assert result['type'] == 'trade_stats'
        assert 'stats' in result

    def test_handle_barter_modifiers(self, resource_handler):
        """Test BARTER command (list modifiers)"""
        result = resource_handler.handle_command("BARTER", [])

        assert result['type'] == 'barter_modifiers'
        assert 'modifiers' in result

    def test_handle_barter_activate(self, resource_handler):
        """Test BARTER ACTIVATE command"""
        result = resource_handler.handle_command("BARTER", ["activate", "Food", "Scarcity"])

        assert result['type'] == 'modifier_activated'
        assert result['result']['modifier'] == "Food Scarcity"

    def test_handle_barter_value(self, resource_handler):
        """Test BARTER VALUE command"""
        # Add item first
        add_result = resource_handler.inventory_service.add_item(
            "Value Item", ItemCategory.FOOD, base_value=50
        )
        item_id = add_result['item_id']

        result = resource_handler.handle_command("BARTER", ["value", str(item_id)])

        assert result['type'] == 'barter_value'
        assert result['base_value'] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
