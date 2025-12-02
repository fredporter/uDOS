"""
uDOS Game Services

Core gameplay systems consolidated from extensions/play/services/

Services:
- xp_service: Experience points and skill progression
- inventory_service: Item management and tracking
- survival_service: Health, hunger, thirst, and survival stats
- scenario_engine: Story/scenario execution engine
- scenario_service: Scenario data management
- barter_game_service: In-game trading/bartering system

Migrated: Phase 4 (December 2, 2025)
"""

from .xp_service import XPService, XPCategory, SkillTree
from .inventory_service import InventoryService, ItemCategory, ItemCondition, ItemRarity
from .survival_service import SurvivalService, SurvivalStat, StatusEffect
from .scenario_engine import ScenarioEngine, EventType
from .scenario_service import ScenarioService
from .barter_game_service import BarterService as BarterGameService

__all__ = [
    # XP System
    'XPService',
    'XPCategory',
    'SkillTree',

    # Inventory System
    'InventoryService',
    'ItemCategory',
    'ItemCondition',
    'ItemRarity',

    # Survival System
    'SurvivalService',
    'SurvivalStat',
    'StatusEffect',

    # Scenario System
    'ScenarioEngine',
    'EventType',
    'ScenarioService',

    # Barter System (gameplay)
    'BarterGameService',
]
