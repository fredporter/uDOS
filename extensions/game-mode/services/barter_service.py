"""
Barter Service for uDOS v1.0.18 - Apocalypse Adventures
Manages trading, bartering, and transaction history.
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional


class BarterService:
    """Service for managing barter transactions"""

    def __init__(self, data_dir: str = "data", inventory_service=None):
        """
        Initialize barter service with SQLite database.

        Args:
            data_dir: Directory for database storage
            inventory_service: InventoryService instance for item management
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "barter.db")
        self.inventory_service = inventory_service
        self._init_database()

    def _init_database(self):
        """Create barter database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Transactions table - stores all barter transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,  -- 'trade', 'buy', 'sell', 'gift'
                partner_name TEXT,                -- Trading partner
                items_given TEXT,                 -- JSON array of item IDs/names
                items_received TEXT,              -- JSON array of item IDs/names
                total_value_given INTEGER DEFAULT 0,
                total_value_received INTEGER DEFAULT 0,
                profit INTEGER DEFAULT 0,         -- Difference in values
                transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)

        # Trade offers table - pending/active trade offers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_name TEXT NOT NULL,
                items_offered TEXT,       -- JSON array
                items_requested TEXT,     -- JSON array
                status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected', 'expired'
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_date TEXT,
                notes TEXT
            )
        """)

        # Pricing modifiers table - dynamic pricing based on various factors
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricing_modifiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modifier_name TEXT NOT NULL UNIQUE,
                modifier_type TEXT NOT NULL,  -- 'category', 'rarity', 'condition', 'global'
                target TEXT,                   -- Specific category/rarity if applicable
                multiplier REAL DEFAULT 1.0,   -- Price multiplier
                active BOOLEAN DEFAULT 1,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)

        # Add default pricing modifiers
        default_modifiers = [
            ("Desperate Seller", "global", None, 0.7, "Selling at discount"),
            ("Shrewd Negotiator", "global", None, 1.3, "Buying at premium"),
            ("Medical Emergency", "category", "medical", 2.0, "Medical items in high demand"),
            ("Food Scarcity", "category", "food", 1.5, "Food items more valuable"),
            ("Water Crisis", "category", "water", 2.5, "Water critically needed")
        ]

        for name, mod_type, target, multiplier, desc in default_modifiers:
            cursor.execute("""
                INSERT OR IGNORE INTO pricing_modifiers
                (modifier_name, modifier_type, target, multiplier, active, description)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (name, mod_type, target, multiplier, desc))

        conn.commit()
        conn.close()

    def calculate_trade_value(self, item_details: Dict, apply_modifiers: bool = True) -> int:
        """
        Calculate trade value for an item.

        Args:
            item_details: Dict with item info (base_value, rarity, condition, category)
            apply_modifiers: Whether to apply active pricing modifiers

        Returns:
            Calculated trade value
        """
        base_value = item_details.get('current_value', item_details.get('base_value', 10))

        if not apply_modifiers:
            return base_value

        # Apply pricing modifiers
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get global modifiers
        cursor.execute("""
            SELECT multiplier FROM pricing_modifiers
            WHERE active = 1 AND modifier_type = 'global'
        """)
        global_mods = cursor.fetchall()

        # Get category-specific modifiers
        category = item_details.get('category')
        if category:
            cursor.execute("""
                SELECT multiplier FROM pricing_modifiers
                WHERE active = 1 AND modifier_type = 'category' AND target = ?
            """, (category,))
            category_mods = cursor.fetchall()
        else:
            category_mods = []

        # Get rarity-specific modifiers
        rarity = item_details.get('rarity')
        if rarity:
            cursor.execute("""
                SELECT multiplier FROM pricing_modifiers
                WHERE active = 1 AND modifier_type = 'rarity' AND target = ?
            """, (rarity,))
            rarity_mods = cursor.fetchall()
        else:
            rarity_mods = []

        conn.close()

        # Apply all modifiers
        total_multiplier = 1.0
        for mod in global_mods + category_mods + rarity_mods:
            total_multiplier *= mod[0]

        return int(base_value * total_multiplier)

    def create_trade_offer(self, partner_name: str, items_offered: List[int],
                          items_requested: List[str], notes: str = "") -> Dict:
        """
        Create a trade offer.

        Args:
            partner_name: Name of trading partner
            items_offered: List of item IDs from inventory
            items_requested: List of item names requested
            notes: Additional notes

        Returns:
            Dict with offer details
        """
        if not self.inventory_service:
            return {"success": False, "error": "Inventory service not available"}

        # Calculate value of offered items
        offered_value = 0
        offered_items = []
        for item_id in items_offered:
            item = self.inventory_service.get_item(item_id)
            if item:
                offered_value += self.calculate_trade_value(item)
                offered_items.append({
                    "id": item_id,
                    "name": item['name'],
                    "value": self.calculate_trade_value(item)
                })

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Store as JSON-like text (simple format)
        offered_str = ",".join([f"{i['id']}:{i['name']}" for i in offered_items])
        requested_str = ",".join(items_requested)

        cursor.execute("""
            INSERT INTO trade_offers (partner_name, items_offered, items_requested, notes)
            VALUES (?, ?, ?, ?)
        """, (partner_name, offered_str, requested_str, notes))

        offer_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "success": True,
            "offer_id": offer_id,
            "partner": partner_name,
            "offered": offered_items,
            "offered_value": offered_value,
            "requested": items_requested,
            "status": "pending"
        }

    def execute_trade(self, partner_name: str, items_given: List[int],
                     items_received: List[Dict], notes: str = "") -> Dict:
        """
        Execute a trade transaction.

        Args:
            partner_name: Name of trading partner
            items_given: List of item IDs to trade away
            items_received: List of dicts with new item details
            notes: Transaction notes

        Returns:
            Dict with transaction details
        """
        if not self.inventory_service:
            return {"success": False, "error": "Inventory service not available"}

        # Calculate value given
        value_given = 0
        given_items = []
        for item_id in items_given:
            item = self.inventory_service.get_item(item_id)
            if item:
                value_given += self.calculate_trade_value(item)
                given_items.append(f"{item_id}:{item['name']}")
                # Remove from inventory
                self.inventory_service.remove_item(item_id, item['quantity'])

        # Calculate value received and add items
        value_received = 0
        received_items = []
        for item_details in items_received:
            # Add to inventory
            from extensions.game_mode.services.inventory_service import ItemCategory, ItemRarity
            category = ItemCategory[item_details.get('category', 'MISC').upper()]
            rarity = ItemRarity[item_details.get('rarity', 'COMMON').upper()]

            result = self.inventory_service.add_item(
                name=item_details['name'],
                category=category,
                quantity=item_details.get('quantity', 1),
                weight=item_details.get('weight', 0.0),
                volume=item_details.get('volume', 0.0),
                condition=item_details.get('condition', 100),
                rarity=rarity,
                base_value=item_details.get('base_value', 10),
                description=item_details.get('description', '')
            )

            # Calculate value
            item_value = self.calculate_trade_value(item_details)
            value_received += item_value
            received_items.append(f"{result['item_id']}:{item_details['name']}")

        # Record transaction
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        profit = value_received - value_given

        cursor.execute("""
            INSERT INTO transactions (
                transaction_type, partner_name, items_given, items_received,
                total_value_given, total_value_received, profit, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('trade', partner_name, ",".join(given_items), ",".join(received_items),
              value_given, value_received, profit, notes))

        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "success": True,
            "transaction_id": transaction_id,
            "partner": partner_name,
            "value_given": value_given,
            "value_received": value_received,
            "profit": profit,
            "profit_percent": int((profit / value_given * 100)) if value_given > 0 else 0,
            "fair_trade": abs(profit) <= (value_given * 0.1)  # Within 10% is fair
        }

    def get_transaction_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent transaction history.

        Args:
            limit: Number of transactions to retrieve

        Returns:
            List of transaction dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, transaction_type, partner_name, items_given, items_received,
                   total_value_given, total_value_received, profit, transaction_date, notes
            FROM transactions
            ORDER BY transaction_date DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()

        transactions = []
        for row in results:
            transactions.append({
                "id": row[0],
                "type": row[1],
                "partner": row[2],
                "items_given": row[3],
                "items_received": row[4],
                "value_given": row[5],
                "value_received": row[6],
                "profit": row[7],
                "date": row[8],
                "notes": row[9]
            })

        return transactions

    def get_trade_stats(self) -> Dict:
        """Get overall trading statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]

        # Total profit
        cursor.execute("SELECT SUM(profit) FROM transactions")
        total_profit = cursor.fetchone()[0] or 0

        # Average profit
        cursor.execute("SELECT AVG(profit) FROM transactions WHERE profit IS NOT NULL")
        avg_profit = cursor.fetchone()[0] or 0

        # Best deal
        cursor.execute("""
            SELECT partner_name, profit, transaction_date
            FROM transactions
            ORDER BY profit DESC
            LIMIT 1
        """)
        best_deal = cursor.fetchone()

        # Worst deal
        cursor.execute("""
            SELECT partner_name, profit, transaction_date
            FROM transactions
            ORDER BY profit ASC
            LIMIT 1
        """)
        worst_deal = cursor.fetchone()

        conn.close()

        stats = {
            "total_transactions": total_transactions,
            "total_profit": total_profit,
            "average_profit": round(avg_profit, 2)
        }

        if best_deal:
            stats["best_deal"] = {
                "partner": best_deal[0],
                "profit": best_deal[1],
                "date": best_deal[2]
            }

        if worst_deal:
            stats["worst_deal"] = {
                "partner": worst_deal[0],
                "profit": worst_deal[1],
                "date": worst_deal[2]
            }

        return stats

    def activate_modifier(self, modifier_name: str) -> Dict:
        """Activate a pricing modifier"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pricing_modifiers
            SET active = 1
            WHERE modifier_name = ?
        """, (modifier_name,))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return {
            "success": affected > 0,
            "modifier": modifier_name,
            "active": True
        }

    def deactivate_modifier(self, modifier_name: str) -> Dict:
        """Deactivate a pricing modifier"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pricing_modifiers
            SET active = 0
            WHERE modifier_name = ?
        """, (modifier_name,))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return {
            "success": affected > 0,
            "modifier": modifier_name,
            "active": False
        }

    def get_active_modifiers(self) -> List[Dict]:
        """Get all active pricing modifiers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT modifier_name, modifier_type, target, multiplier, description
            FROM pricing_modifiers
            WHERE active = 1
        """)

        results = cursor.fetchall()
        conn.close()

        modifiers = []
        for row in results:
            modifiers.append({
                "name": row[0],
                "type": row[1],
                "target": row[2],
                "multiplier": row[3],
                "description": row[4]
            })

        return modifiers
