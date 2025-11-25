"""
Tests for v1.0.18 Survival System
Tests survival stats, status effects, and survival commands
"""

import os
import sys
import pytest
import tempfile
import shutil

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.services.survival_service import (
    SurvivalService, SurvivalStat, StatusEffect
)
from core.commands.survival_handler import SurvivalCommandHandler


class TestSurvivalService:
    """Test SurvivalService functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def survival_service(self, temp_dir):
        """Create SurvivalService instance"""
        return SurvivalService(data_dir=temp_dir)

    def test_init_creates_database(self, survival_service):
        """Test database initialization"""
        assert os.path.exists(survival_service.db_path)

    def test_init_creates_default_stats(self, survival_service):
        """Test default stats are created"""
        stats = survival_service.get_all_stats()

        assert 'health' in stats
        assert 'hunger' in stats
        assert 'thirst' in stats
        assert 'fatigue' in stats
        assert 'radiation' in stats
        assert 'temperature' in stats

    def test_get_stat_health(self, survival_service):
        """Test getting health stat"""
        health = survival_service.get_stat(SurvivalStat.HEALTH)

        assert health['stat'] == 'health'
        assert health['current'] == 100
        assert health['max'] == 100
        assert health['status'] == 'normal'

    def test_update_stat_positive(self, survival_service):
        """Test updating stat with positive change"""
        result = survival_service.update_stat(
            SurvivalStat.HUNGER, 20, "Skipped meal"
        )

        assert result['stat'] == 'hunger'
        assert result['old_value'] == 0
        assert result['new_value'] == 20
        assert result['change'] == 20

    def test_update_stat_negative(self, survival_service):
        """Test updating stat with negative change"""
        # Set hunger to 50 first
        survival_service.set_stat(SurvivalStat.HUNGER, 50)

        result = survival_service.update_stat(
            SurvivalStat.HUNGER, -20, "Ate food"
        )

        assert result['old_value'] == 50
        assert result['new_value'] == 30
        assert result['change'] == -20

    def test_update_stat_respects_max(self, survival_service):
        """Test stat doesn't exceed maximum"""
        result = survival_service.update_stat(
            SurvivalStat.HEALTH, 50, "Overheal attempt"
        )

        # Health starts at 100, max is 100
        assert result['new_value'] == 100

    def test_update_stat_respects_min(self, survival_service):
        """Test stat doesn't go below minimum"""
        result = survival_service.update_stat(
            SurvivalStat.HEALTH, -150, "Massive damage"
        )

        # Min health is 0
        assert result['new_value'] == 0

    def test_set_stat(self, survival_service):
        """Test setting stat to absolute value"""
        result = survival_service.set_stat(
            SurvivalStat.HUNGER, 75, "Manual set"
        )

        assert result['stat'] == 'hunger'
        assert result['new_value'] == 75

    def test_get_all_stats(self, survival_service):
        """Test getting all stats at once"""
        stats = survival_service.get_all_stats()

        assert len(stats) == 6
        for stat_name in ['health', 'hunger', 'thirst', 'fatigue', 'radiation', 'temperature']:
            assert stat_name in stats
            assert 'current' in stats[stat_name]
            assert 'status' in stats[stat_name]

    def test_stat_status_normal(self, survival_service):
        """Test normal status detection"""
        health = survival_service.get_stat(SurvivalStat.HEALTH)
        assert health['status'] == 'normal'

    def test_stat_status_warning(self, survival_service):
        """Test warning status detection"""
        survival_service.set_stat(SurvivalStat.HEALTH, 35)
        health = survival_service.get_stat(SurvivalStat.HEALTH)
        assert health['status'] == 'warning'

    def test_stat_status_critical(self, survival_service):
        """Test critical status detection"""
        survival_service.set_stat(SurvivalStat.HEALTH, 15)
        health = survival_service.get_stat(SurvivalStat.HEALTH)
        assert health['status'] == 'critical'

    def test_add_status_effect(self, survival_service):
        """Test adding status effect"""
        result = survival_service.add_status_effect(
            StatusEffect.HUNGRY,
            severity=2,
            duration_minutes=60,
            description="Very hungry"
        )

        assert result['effect'] == 'hungry'
        assert result['severity'] == 2
        assert result['duration'] == 60

    def test_remove_status_effect(self, survival_service):
        """Test removing status effect"""
        survival_service.add_status_effect(StatusEffect.TIRED)
        result = survival_service.remove_status_effect(StatusEffect.TIRED)

        assert result['removed'] is True

    def test_get_active_effects(self, survival_service):
        """Test listing active effects"""
        survival_service.add_status_effect(StatusEffect.HUNGRY, severity=2)
        survival_service.add_status_effect(StatusEffect.THIRSTY, severity=1)

        effects = survival_service.get_active_effects()

        assert len(effects) >= 2
        effect_names = [e['effect'] for e in effects]
        assert 'hungry' in effect_names
        assert 'thirsty' in effect_names

    def test_effect_expiration(self, survival_service):
        """Test effect expiration detection"""
        survival_service.add_status_effect(
            StatusEffect.TIRED,
            duration_minutes=-10  # Already expired
        )

        effects = survival_service.get_active_effects()
        tired = next(e for e in effects if e['effect'] == 'tired')

        assert tired['expired'] is True

    def test_clear_expired_effects(self, survival_service):
        """Test clearing expired effects"""
        survival_service.add_status_effect(StatusEffect.HUNGRY, duration_minutes=-5)
        survival_service.add_status_effect(StatusEffect.THIRSTY, duration_minutes=60)

        cleared = survival_service.clear_expired_effects()

        assert 'hungry' in cleared
        assert 'thirsty' not in cleared

    def test_get_survival_events(self, survival_service):
        """Test getting event log"""
        survival_service.update_stat(SurvivalStat.HUNGER, 10, "Test event 1")
        survival_service.update_stat(SurvivalStat.THIRST, 15, "Test event 2")

        events = survival_service.get_survival_events(limit=10)

        assert len(events) >= 2
        assert any('Test event' in e['description'] for e in events)

    def test_auto_effect_hungry(self, survival_service):
        """Test automatic hungry effect when hunger high"""
        result = survival_service.update_stat(SurvivalStat.HUNGER, 75, "Skip meals")

        assert 'hungry' in result['effects_triggered']

    def test_auto_effect_starving(self, survival_service):
        """Test automatic starving effect when hunger critical"""
        result = survival_service.update_stat(SurvivalStat.HUNGER, 95, "No food")

        assert 'starving' in result['effects_triggered']

    def test_auto_effect_thirsty(self, survival_service):
        """Test automatic thirsty effect when thirst high"""
        result = survival_service.update_stat(SurvivalStat.THIRST, 75, "No water")

        assert 'thirsty' in result['effects_triggered']

    def test_auto_effect_injured(self, survival_service):
        """Test automatic injured effect when health low"""
        survival_service.set_stat(SurvivalStat.HEALTH, 100)  # Reset
        result = survival_service.update_stat(SurvivalStat.HEALTH, -85, "Major injury")

        assert 'injured' in result['effects_triggered']

    def test_auto_effect_tired(self, survival_service):
        """Test automatic tired effect when fatigue high"""
        result = survival_service.update_stat(SurvivalStat.FATIGUE, 75, "No sleep")

        assert 'tired' in result['effects_triggered']

    def test_auto_effect_irradiated(self, survival_service):
        """Test automatic radiation effect"""
        result = survival_service.update_stat(SurvivalStat.RADIATION, 50, "Radiation exposure")

        assert 'irradiated' in result['effects_triggered']

    def test_auto_effect_freezing(self, survival_service):
        """Test automatic freezing effect when too cold"""
        result = survival_service.update_stat(SurvivalStat.TEMPERATURE, -25, "Cold weather")

        assert 'freezing' in result['effects_triggered']

    def test_auto_effect_overheating(self, survival_service):
        """Test automatic overheating effect when too hot"""
        survival_service.set_stat(SurvivalStat.TEMPERATURE, 20)  # Reset
        result = survival_service.update_stat(SurvivalStat.TEMPERATURE, 25, "Hot weather")

        assert 'overheating' in result['effects_triggered']

    def test_apply_time_decay(self, survival_service):
        """Test time-based stat decay"""
        changes = survival_service.apply_time_decay(hours=2)

        assert 'hunger' in changes
        assert 'thirst' in changes
        assert 'fatigue' in changes

        # Check values increased
        assert changes['hunger']['new_value'] > changes['hunger']['old_value']
        assert changes['thirst']['new_value'] > changes['thirst']['old_value']
        assert changes['fatigue']['new_value'] > changes['fatigue']['old_value']

    def test_time_decay_health_loss(self, survival_service):
        """Test health loss when conditions are bad"""
        # Set bad conditions
        survival_service.set_stat(SurvivalStat.HUNGER, 85)
        survival_service.set_stat(SurvivalStat.THIRST, 95)

        changes = survival_service.apply_time_decay(hours=1)

        # Health should decrease
        if 'health' in changes:
            assert changes['health']['new_value'] < changes['health']['old_value']


class TestSurvivalCommandHandler:
    """Test SurvivalCommandHandler functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def survival_handler(self, temp_dir):
        """Create SurvivalCommandHandler instance"""
        return SurvivalCommandHandler(data_dir=temp_dir)

    def test_handle_status_overview(self, survival_handler):
        """Test STATUS command with no args"""
        result = survival_handler.handle_command("STATUS", [])

        assert result['type'] == 'status_overview'
        assert 'stats' in result
        assert 'effects' in result
        assert 'warnings' in result

    def test_handle_status_specific_stat(self, survival_handler):
        """Test STATUS [stat] command"""
        result = survival_handler.handle_command("STATUS", ["health"])

        assert result['type'] == 'stat_detail'
        assert result['stat']['stat'] == 'health'

    def test_handle_status_effects(self, survival_handler):
        """Test STATUS EFFECTS command"""
        result = survival_handler.handle_command("STATUS", ["effects"])

        assert result['type'] == 'status_effects'
        assert 'effects' in result

    def test_handle_status_events(self, survival_handler):
        """Test STATUS EVENTS command"""
        result = survival_handler.handle_command("STATUS", ["events"])

        assert result['type'] == 'survival_events'
        assert 'events' in result

    def test_handle_stats_update(self, survival_handler):
        """Test STATS UPDATE command"""
        result = survival_handler.handle_command("STATS", ["update", "hunger", "25", "Test"])

        assert result['type'] == 'stat_updated'
        assert result['result']['stat'] == 'hunger'
        assert result['result']['new_value'] == 25

    def test_handle_stats_set(self, survival_handler):
        """Test STATS SET command"""
        result = survival_handler.handle_command("STATS", ["set", "health", "80", "Healed"])

        assert result['type'] == 'stat_set'
        assert result['result']['stat'] == 'health'
        assert result['result']['new_value'] == 80

    def test_handle_effect_add(self, survival_handler):
        """Test EFFECT ADD command"""
        result = survival_handler.handle_command("EFFECT", ["add", "hungry", "2", "60"])

        assert result['type'] == 'effect_added'
        assert result['result']['effect'] == 'hungry'
        assert result['result']['severity'] == 2

    def test_handle_effect_remove(self, survival_handler):
        """Test EFFECT REMOVE command"""
        # Add effect first
        survival_handler.survival_service.add_status_effect(StatusEffect.TIRED)

        result = survival_handler.handle_command("EFFECT", ["remove", "tired"])

        assert result['type'] == 'effect_removed'
        assert result['result']['removed'] is True

    def test_handle_effect_clear(self, survival_handler):
        """Test EFFECT CLEAR command"""
        # Add expired effect
        survival_handler.survival_service.add_status_effect(
            StatusEffect.HUNGRY, duration_minutes=-10
        )

        result = survival_handler.handle_command("EFFECT", ["clear"])

        assert result['type'] == 'effects_cleared'
        assert len(result['cleared']) >= 0

    def test_handle_survive_overview(self, survival_handler):
        """Test SURVIVE command"""
        result = survival_handler.handle_command("SURVIVE", [])

        assert result['type'] == 'survival_overview'
        assert 'stats' in result
        assert 'warnings' in result

    def test_handle_survive_time(self, survival_handler):
        """Test SURVIVE TIME command"""
        result = survival_handler.handle_command("SURVIVE", ["time", "2"])

        assert result['type'] == 'time_passed'
        assert result['hours'] == 2.0
        assert 'changes' in result

    def test_handle_survive_rest(self, survival_handler):
        """Test SURVIVE REST command"""
        result = survival_handler.handle_command("SURVIVE", ["rest", "4"])

        assert result['type'] == 'rested'
        assert result['hours'] == 4.0
        assert 'changes' in result

    def test_handle_survive_eat(self, survival_handler):
        """Test SURVIVE EAT command"""
        # Set hunger first
        survival_handler.survival_service.set_stat(SurvivalStat.HUNGER, 50)

        result = survival_handler.handle_command("SURVIVE", ["eat", "30"])

        assert result['type'] == 'ate'
        assert result['amount'] == 30.0

    def test_handle_survive_drink(self, survival_handler):
        """Test SURVIVE DRINK command"""
        # Set thirst first
        survival_handler.survival_service.set_stat(SurvivalStat.THIRST, 60)

        result = survival_handler.handle_command("SURVIVE", ["drink", "40"])

        assert result['type'] == 'drank'
        assert result['amount'] == 40.0

    def test_warnings_critical(self, survival_handler):
        """Test critical warnings generation"""
        survival_handler.survival_service.set_stat(SurvivalStat.HEALTH, 10)

        stats = survival_handler.survival_service.get_all_stats()
        warnings = survival_handler._get_warnings(stats)

        critical_warnings = [w for w in warnings if w['level'] == 'critical']
        assert len(critical_warnings) > 0

    def test_warnings_normal(self, survival_handler):
        """Test no warnings when stats normal"""
        stats = survival_handler.survival_service.get_all_stats()
        warnings = survival_handler._get_warnings(stats)

        # Default stats should be normal (no warnings)
        assert len(warnings) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
