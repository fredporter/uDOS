"""
Inventory Service for uDOS v1.0.18 - Apocalypse Adventures
Manages item tracking, condition monitoring, and weight/volume management.
"""

import sqlite3
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ItemCategory(Enum):
    """Item categories for organization"""
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    TOOL = "tool"
    WEAPON = "weapon"
    ARMOR = "armor"
    FUEL = "fuel"
    MATERIAL = "material"
    MISC = "misc"


class ItemCondition(Enum):
    """Item condition states"""
    PRISTINE = "pristine"      # 100% durability
    EXCELLENT = "excellent"    # 80-99% durability
    GOOD = "good"             # 60-79% durability
    FAIR = "fair"             # 40-59% durability
    POOR = "poor"             # 20-39% durability
    BROKEN = "broken"         # 0-19% durability


class ItemRarity(Enum):
    """Item rarity levels affecting barter value"""
    COMMON = "common"          # 1x base value
    UNCOMMON = "uncommon"      # 2x base value
    RARE = "rare"             # 5x base value
    EPIC = "epic"             # 10x base value
    LEGENDARY = "legendary"    # 25x base value


class InventoryService:
    """Service for managing player inventory"""

    def __init__(self, data_dir: str = "data"):
        """Initialize inventory service with SQLite database"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "inventory.db")
        self._init_database()

    def _init_database(self):
        """Create inventory database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Items table - stores all inventory items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                weight REAL DEFAULT 0.0,      -- kg per item
                volume REAL DEFAULT 0.0,      -- liters per item
                condition INTEGER DEFAULT 100, -- durability percentage
                rarity TEXT DEFAULT 'common',
                base_value INTEGER DEFAULT 10, -- base barter value
                consumable BOOLEAN DEFAULT 0,  -- can be consumed/used up
                stackable BOOLEAN DEFAULT 1,   -- can stack in inventory
                description TEXT,
                acquired_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Storage locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                max_weight REAL DEFAULT 100.0,
                max_volume REAL DEFAULT 100.0,
                description TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Item storage mapping - links items to storage locations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_storage (
                item_id INTEGER,
                location_id INTEGER,
                FOREIGN KEY (item_id) REFERENCES items(id),
                FOREIGN KEY (location_id) REFERENCES storage_locations(id),
                PRIMARY KEY (item_id, location_id)
            )
        """)

        # Create default storage location (personal inventory)
        cursor.execute("""
            INSERT OR IGNORE INTO storage_locations (name, max_weight, max_volume, description)
            VALUES ('Personal Inventory', 50.0, 50.0, 'Items carried on person')
        """)

        conn.commit()
        conn.close()

    def add_item(self, name: str, category: ItemCategory, quantity: int = 1,
                 weight: float = 0.0, volume: float = 0.0, condition: int = 100,
                 rarity: ItemRarity = ItemRarity.COMMON, base_value: int = 10,
                 consumable: bool = False, stackable: bool = True,
                 description: str = "", location: str = "Personal Inventory") -> Dict:
        """
        Add item to inventory.

        Args:
            name: Item name
            category: Item category
            quantity: Number of items
            weight: Weight per item in kg
            volume: Volume per item in liters
            condition: Durability percentage (0-100)
            rarity: Item rarity level
            base_value: Base barter value
            consumable: Can be consumed/used up
            stackable: Can stack in inventory
            description: Item description
            location: Storage location name

        Returns:
            Dict with item details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if stackable item already exists
        if stackable:
            cursor.execute("""
                SELECT id, quantity FROM items
                WHERE name = ? AND category = ? AND condition = ?
            """, (name, category.value, condition))
            existing = cursor.fetchone()

            if existing:
                item_id, current_qty = existing
                new_qty = current_qty + quantity
                cursor.execute("""
                    UPDATE items
                    SET quantity = ?, last_updated = ?
                    WHERE id = ?
                """, (new_qty, datetime.now().isoformat(), item_id))
                conn.commit()
                conn.close()

                return {
                    "item_id": item_id,
                    "name": name,
                    "action": "stacked",
                    "quantity": new_qty,
                    "added": quantity
                }

        # Insert new item
        cursor.execute("""
            INSERT INTO items (
                name, category, quantity, weight, volume, condition,
                rarity, base_value, consumable, stackable, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category.value, quantity, weight, volume, condition,
              rarity.value, base_value, consumable, stackable, description))

        item_id = cursor.lastrowid

        # Link to storage location
        cursor.execute("SELECT id FROM storage_locations WHERE name = ?", (location,))
        location_result = cursor.fetchone()
        if location_result:
            location_id = location_result[0]
            cursor.execute("""
                INSERT INTO item_storage (item_id, location_id)
                VALUES (?, ?)
            """, (item_id, location_id))

        conn.commit()
        conn.close()

        return {
            "item_id": item_id,
            "name": name,
            "action": "added",
            "quantity": quantity,
            "location": location
        }

    def remove_item(self, item_id: int, quantity: int = 1) -> Dict:
        """
        Remove item from inventory.

        Args:
            item_id: ID of item to remove
            quantity: Number to remove

        Returns:
            Dict with removal details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name, quantity FROM items WHERE id = ?", (item_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return {"success": False, "error": "Item not found"}

        name, current_qty = result

        if quantity >= current_qty:
            # Remove entire stack
            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
            cursor.execute("DELETE FROM item_storage WHERE item_id = ?", (item_id,))
            removed = current_qty
            remaining = 0
        else:
            # Reduce quantity
            new_qty = current_qty - quantity
            cursor.execute("""
                UPDATE items
                SET quantity = ?, last_updated = ?
                WHERE id = ?
            """, (new_qty, datetime.now().isoformat(), item_id))
            removed = quantity
            remaining = new_qty

        conn.commit()
        conn.close()

        return {
            "success": True,
            "item_id": item_id,
            "name": name,
            "removed": removed,
            "remaining": remaining
        }

    def get_item(self, item_id: int) -> Optional[Dict]:
        """Get item details by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, category, quantity, weight, volume, condition,
                   rarity, base_value, consumable, stackable, description,
                   acquired_date, last_updated
            FROM items WHERE id = ?
        """, (item_id,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        return {
            "id": result[0],
            "name": result[1],
            "category": result[2],
            "quantity": result[3],
            "weight": result[4],
            "volume": result[5],
            "condition": result[6],
            "condition_state": self._get_condition_state(result[6]),
            "rarity": result[7],
            "base_value": result[8],
            "consumable": bool(result[9]),
            "stackable": bool(result[10]),
            "description": result[11],
            "acquired_date": result[12],
            "last_updated": result[13],
            "total_weight": result[4] * result[3],
            "total_volume": result[5] * result[3],
            "current_value": self._calculate_item_value(result[8], result[7], result[6])
        }

    def get_inventory(self, location: str = "Personal Inventory",
                     category: Optional[ItemCategory] = None) -> List[Dict]:
        """
        Get all items in inventory.

        Args:
            location: Storage location name
            category: Optional category filter

        Returns:
            List of item dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category:
            cursor.execute("""
                SELECT i.id, i.name, i.category, i.quantity, i.weight, i.volume,
                       i.condition, i.rarity, i.base_value, i.consumable,
                       i.stackable, i.description
                FROM items i
                JOIN item_storage ist ON i.id = ist.item_id
                JOIN storage_locations sl ON ist.location_id = sl.id
                WHERE sl.name = ? AND i.category = ?
                ORDER BY i.category, i.name
            """, (location, category.value))
        else:
            cursor.execute("""
                SELECT i.id, i.name, i.category, i.quantity, i.weight, i.volume,
                       i.condition, i.rarity, i.base_value, i.consumable,
                       i.stackable, i.description
                FROM items i
                JOIN item_storage ist ON i.id = ist.item_id
                JOIN storage_locations sl ON ist.location_id = sl.id
                WHERE sl.name = ?
                ORDER BY i.category, i.name
            """, (location,))

        results = cursor.fetchall()
        conn.close()

        items = []
        for row in results:
            items.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "quantity": row[3],
                "weight": row[4],
                "volume": row[5],
                "condition": row[6],
                "condition_state": self._get_condition_state(row[6]),
                "rarity": row[7],
                "base_value": row[8],
                "consumable": bool(row[9]),
                "stackable": bool(row[10]),
                "description": row[11],
                "total_weight": row[4] * row[3],
                "total_volume": row[5] * row[3],
                "current_value": self._calculate_item_value(row[8], row[7], row[6])
            })

        return items

    def get_inventory_stats(self, location: str = "Personal Inventory") -> Dict:
        """Get inventory statistics for a location"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get total weight and volume
        cursor.execute("""
            SELECT SUM(i.weight * i.quantity), SUM(i.volume * i.quantity)
            FROM items i
            JOIN item_storage ist ON i.id = ist.item_id
            JOIN storage_locations sl ON ist.location_id = sl.id
            WHERE sl.name = ?
        """, (location,))

        result = cursor.fetchone()
        total_weight = result[0] if result[0] else 0.0
        total_volume = result[1] if result[1] else 0.0

        # Get location capacity
        cursor.execute("""
            SELECT max_weight, max_volume FROM storage_locations WHERE name = ?
        """, (location,))
        capacity = cursor.fetchone()

        # Get item count
        cursor.execute("""
            SELECT COUNT(*) FROM items i
            JOIN item_storage ist ON i.id = ist.item_id
            JOIN storage_locations sl ON ist.location_id = sl.id
            WHERE sl.name = ?
        """, (location,))
        item_count = cursor.fetchone()[0]

        conn.close()

        return {
            "location": location,
            "item_count": item_count,
            "total_weight": round(total_weight, 2),
            "max_weight": capacity[0],
            "weight_percent": int((total_weight / capacity[0]) * 100),
            "total_volume": round(total_volume, 2),
            "max_volume": capacity[1],
            "volume_percent": int((total_volume / capacity[1]) * 100)
        }

    def update_condition(self, item_id: int, condition_delta: int) -> Dict:
        """
        Update item condition (durability).

        Args:
            item_id: Item ID
            condition_delta: Change in condition (-100 to +100)

        Returns:
            Dict with updated condition
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name, condition FROM items WHERE id = ?", (item_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return {"success": False, "error": "Item not found"}

        name, current_condition = result
        new_condition = max(0, min(100, current_condition + condition_delta))

        cursor.execute("""
            UPDATE items
            SET condition = ?, last_updated = ?
            WHERE id = ?
        """, (new_condition, datetime.now().isoformat(), item_id))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "item_id": item_id,
            "name": name,
            "old_condition": current_condition,
            "new_condition": new_condition,
            "old_state": self._get_condition_state(current_condition),
            "new_state": self._get_condition_state(new_condition)
        }

    def _get_condition_state(self, condition: int) -> str:
        """Convert condition percentage to state"""
        if condition >= 100:
            return ItemCondition.PRISTINE.value
        elif condition >= 80:
            return ItemCondition.EXCELLENT.value
        elif condition >= 60:
            return ItemCondition.GOOD.value
        elif condition >= 40:
            return ItemCondition.FAIR.value
        elif condition >= 20:
            return ItemCondition.POOR.value
        else:
            return ItemCondition.BROKEN.value

    def _calculate_item_value(self, base_value: int, rarity: str, condition: int) -> int:
        """
        Calculate current item value based on rarity and condition.

        Value = base_value * rarity_multiplier * (condition / 100)
        """
        rarity_multipliers = {
            "common": 1,
            "uncommon": 2,
            "rare": 5,
            "epic": 10,
            "legendary": 25
        }

        multiplier = rarity_multipliers.get(rarity, 1)
        value = base_value * multiplier * (condition / 100)
        return int(value)
