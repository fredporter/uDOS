"""
Dialogue Engine

Parse and execute dialogue trees with branching logic.
Supports conditions, player stats checks, and state persistence.
"""

from typing import Dict, List, Any, Optional, Callable


class DialogueNode:
    """Single dialogue node with options and conditions"""

    def __init__(
        self,
        node_id: str,
        text: str,
        options: Optional[List[Dict[str, Any]]] = None,
        condition: Optional[Callable] = None,
    ):
        self.node_id = node_id
        self.text = text
        self.options = options or []
        self.condition = condition

    def evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """Check if node condition is met"""
        if self.condition is None:
            return True
        return self.condition(context)


class DialogueTree:
    """Collection of dialogue nodes forming a conversation tree"""

    def __init__(self, tree_id: str):
        self.tree_id = tree_id
        self.nodes: Dict[str, DialogueNode] = {}
        self.root_node: Optional[str] = None

    def add_node(self, node: DialogueNode, is_root: bool = False):
        """Add node to tree"""
        self.nodes[node.node_id] = node
        if is_root:
            self.root_node = node.node_id

    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_root(self) -> Optional[DialogueNode]:
        """Get root node"""
        if self.root_node:
            return self.nodes.get(self.root_node)
        return None


class DialogueEngine:
    """Manages dialogue trees and conversation state"""

    def __init__(self):
        self.trees: Dict[str, DialogueTree] = {}
        self._load_default_trees()

    def _load_default_trees(self):
        """Load default dialogue trees"""
        # Merchant generic tree
        merchant_tree = DialogueTree("merchant_generic")

        root = DialogueNode(
            "greeting",
            "Welcome, traveler! Looking to buy or sell?",
            [
                {"text": "Show me your wares", "next": "shop"},
                {"text": "I have items to sell", "next": "sell"},
                {"text": "Just browsing", "next": "goodbye"},
            ],
        )
        merchant_tree.add_node(root, is_root=True)

        shop_node = DialogueNode(
            "shop",
            "Here's what I have in stock:",
            [
                {
                    "text": "Buy health potion (10 gold)",
                    "next": "buy_potion",
                    "cost": 10,
                },
                {"text": "Buy map fragment (50 gold)", "next": "buy_map", "cost": 50},
                {"text": "Actually, I'll come back later", "next": "goodbye"},
            ],
        )
        merchant_tree.add_node(shop_node)

        sell_node = DialogueNode(
            "sell",
            "I'll buy your items for fair prices. What do you have?",
            [
                {"text": "Sell common items", "next": "sell_common"},
                {"text": "Never mind", "next": "goodbye"},
            ],
        )
        merchant_tree.add_node(sell_node)

        goodbye_node = DialogueNode("goodbye", "Safe travels, friend!", [])
        merchant_tree.add_node(goodbye_node)

        self.trees["merchant_generic"] = merchant_tree

        # Quest giver tree
        quest_tree = DialogueTree("elder_quests")

        quest_root = DialogueNode(
            "quest_available",
            "Greetings, young one. I have a task that requires courage.",
            [
                {"text": "Tell me more", "next": "quest_details"},
                {"text": "I'm busy right now", "next": "quest_decline"},
            ],
        )
        quest_tree.add_node(quest_root, is_root=True)

        quest_details = DialogueNode(
            "quest_details",
            "A precious item was lost in the underground. Will you retrieve it?",
            [
                {
                    "text": "I accept this quest",
                    "next": "quest_accept",
                    "action": "accept_quest",
                },
                {"text": "I need to prepare first", "next": "quest_decline"},
            ],
        )
        quest_tree.add_node(quest_details)

        quest_accept = DialogueNode(
            "quest_accept",
            "Excellent! May fortune favor you.",
            [],
        )
        quest_tree.add_node(quest_accept)

        quest_decline = DialogueNode(
            "quest_decline",
            "Return when you're ready.",
            [],
        )
        quest_tree.add_node(quest_decline)

        self.trees["elder_quests"] = quest_tree

        # Hostile NPC tree
        hostile_tree = DialogueTree("hostile_generic")

        hostile_root = DialogueNode(
            "encounter",
            "You shouldn't have come here...",
            [
                {"text": "Back down slowly", "next": "flee", "action": "flee"},
                {"text": "Prepare for combat", "next": "combat", "action": "combat"},
            ],
        )
        hostile_tree.add_node(hostile_root, is_root=True)

        flee_node = DialogueNode(
            "flee",
            "*The hostile NPC lets you leave*",
            [],
        )
        hostile_tree.add_node(flee_node)

        combat_node = DialogueNode(
            "combat",
            "*Combat initiated*",
            [],
        )
        hostile_tree.add_node(combat_node)

        self.trees["hostile_generic"] = hostile_tree

    def get_tree(self, tree_id: str) -> Optional[DialogueTree]:
        """Get dialogue tree by ID"""
        return self.trees.get(tree_id)

    def start_conversation(
        self, tree_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start conversation from tree root"""
        tree = self.get_tree(tree_id)
        if not tree:
            return {
                "status": "error",
                "message": f"Dialogue tree not found: {tree_id}",
            }

        root_node = tree.get_root()
        if not root_node:
            return {
                "status": "error",
                "message": f"No root node in tree: {tree_id}",
            }

        if not root_node.evaluate_condition(context):
            return {
                "status": "error",
                "message": "Dialogue conditions not met",
            }

        return {
            "status": "success",
            "node_id": root_node.node_id,
            "text": root_node.text,
            "options": root_node.options,
        }

    def continue_conversation(
        self, tree_id: str, node_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Continue conversation to specified node"""
        tree = self.get_tree(tree_id)
        if not tree:
            return {
                "status": "error",
                "message": f"Dialogue tree not found: {tree_id}",
            }

        node = tree.get_node(node_id)
        if not node:
            return {
                "status": "error",
                "message": f"Dialogue node not found: {node_id}",
            }

        if not node.evaluate_condition(context):
            return {
                "status": "error",
                "message": "Dialogue conditions not met",
            }

        # Terminal node (end of conversation)
        if not node.options:
            return {
                "status": "success",
                "node_id": node.node_id,
                "text": node.text,
                "options": [],
                "complete": True,
            }

        return {
            "status": "success",
            "node_id": node.node_id,
            "text": node.text,
            "options": node.options,
            "complete": False,
        }

    def add_custom_tree(self, tree: DialogueTree):
        """Add custom dialogue tree"""
        self.trees[tree.tree_id] = tree
