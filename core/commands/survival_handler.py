"""
Survival Command Handler for uDOS v1.0.18 - Apocalypse Adventures
Handles STATUS, STATS, and survival-related commands.
"""

from typing import Dict, List
from core.services.survival_service import SurvivalService, SurvivalStat, StatusEffect


class SurvivalCommandHandler:
    """Handler for survival status commands"""

    def __init__(self, data_dir: str = "data"):
        """Initialize with survival service"""
        self.survival_service = SurvivalService(data_dir)

    def handle_command(self, command: str, args: List[str]) -> Dict:
        """
        Route survival commands to appropriate handlers.

        Args:
            command: Command name (STATUS, STATS, EFFECT, etc.)
            args: Command arguments

        Returns:
            Dict with command results
        """
        command_upper = command.upper()

        if command_upper in ["STATUS", "STAT"]:
            return self.handle_status(args)
        elif command_upper == "STATS":
            return self.handle_stats(args)
        elif command_upper == "EFFECT":
            return self.handle_effect(args)
        elif command_upper == "SURVIVE":
            return self.handle_survive(args)
        else:
            return {"type": "error", "message": f"Unknown survival command: {command}"}

    def handle_status(self, args: List[str]) -> Dict:
        """
        Handle STATUS command.

        Usage:
            STATUS - Show all survival stats
            STATUS [stat] - Show specific stat
            STATUS EFFECTS - Show active status effects
            STATUS EVENTS - Show recent survival events
        """
        if not args:
            # Show all stats
            stats = self.survival_service.get_all_stats()
            effects = self.survival_service.get_active_effects()

            return {
                "type": "status_overview",
                "stats": stats,
                "effects": effects,
                "warnings": self._get_warnings(stats)
            }

        subcmd = args[0].lower()

        if subcmd == "effects":
            effects = self.survival_service.get_active_effects()
            return {
                "type": "status_effects",
                "effects": effects,
                "total": len(effects)
            }

        elif subcmd == "events":
            limit = int(args[1]) if len(args) > 1 else 20
            events = self.survival_service.get_survival_events(limit)
            return {
                "type": "survival_events",
                "events": events,
                "total": len(events)
            }

        else:
            # Try to show specific stat
            try:
                stat = SurvivalStat[subcmd.upper()]
                stat_info = self.survival_service.get_stat(stat)
                return {
                    "type": "stat_detail",
                    "stat": stat_info
                }
            except KeyError:
                return {
                    "type": "error",
                    "message": f"Unknown stat: {subcmd}. Valid: {', '.join([s.value for s in SurvivalStat])}"
                }

    def handle_stats(self, args: List[str]) -> Dict:
        """
        Handle STATS command (alias for STATUS).

        Usage:
            STATS - Show all survival stats
            STATS UPDATE [stat] [value] - Update stat value
            STATS SET [stat] [value] - Set stat to absolute value
        """
        if not args:
            return self.handle_status([])

        subcmd = args[0].lower()

        if subcmd == "update" and len(args) >= 3:
            try:
                stat = SurvivalStat[args[1].upper()]
                change = float(args[2])
                reason = " ".join(args[3:]) if len(args) > 3 else "Manual update"

                result = self.survival_service.update_stat(stat, change, reason)
                return {
                    "type": "stat_updated",
                    "result": result
                }
            except (KeyError, ValueError) as e:
                return {
                    "type": "error",
                    "message": f"Invalid stat or value: {str(e)}"
                }

        elif subcmd == "set" and len(args) >= 3:
            try:
                stat = SurvivalStat[args[1].upper()]
                value = float(args[2])
                reason = " ".join(args[3:]) if len(args) > 3 else "Manual set"

                result = self.survival_service.set_stat(stat, value, reason)
                return {
                    "type": "stat_set",
                    "result": result
                }
            except (KeyError, ValueError) as e:
                return {
                    "type": "error",
                    "message": f"Invalid stat or value: {str(e)}"
                }

        else:
            return {
                "type": "error",
                "message": "Usage: STATS [UPDATE/SET] [stat] [value]"
            }

    def handle_effect(self, args: List[str]) -> Dict:
        """
        Handle EFFECT command.

        Usage:
            EFFECT - List all active effects
            EFFECT ADD [effect] [severity] [duration] - Add status effect
            EFFECT REMOVE [effect] - Remove status effect
            EFFECT CLEAR - Clear expired effects
        """
        if not args:
            effects = self.survival_service.get_active_effects()
            return {
                "type": "effects_list",
                "effects": effects,
                "total": len(effects)
            }

        subcmd = args[0].lower()

        if subcmd == "add" and len(args) >= 2:
            try:
                effect = StatusEffect[args[1].upper()]
                severity = int(args[2]) if len(args) > 2 else 1
                duration = int(args[3]) if len(args) > 3 else None
                description = " ".join(args[4:]) if len(args) > 4 else ""

                result = self.survival_service.add_status_effect(
                    effect, severity, duration, description
                )
                return {
                    "type": "effect_added",
                    "result": result
                }
            except (KeyError, ValueError) as e:
                return {
                    "type": "error",
                    "message": f"Invalid effect or parameters: {str(e)}"
                }

        elif subcmd == "remove" and len(args) >= 2:
            try:
                effect = StatusEffect[args[1].upper()]
                result = self.survival_service.remove_status_effect(effect)
                return {
                    "type": "effect_removed",
                    "result": result
                }
            except KeyError:
                return {
                    "type": "error",
                    "message": f"Unknown effect: {args[1]}"
                }

        elif subcmd == "clear":
            cleared = self.survival_service.clear_expired_effects()
            return {
                "type": "effects_cleared",
                "cleared": cleared,
                "total": len(cleared)
            }

        else:
            return {
                "type": "error",
                "message": "Usage: EFFECT [ADD/REMOVE/CLEAR]"
            }

    def handle_survive(self, args: List[str]) -> Dict:
        """
        Handle SURVIVE command.

        Usage:
            SURVIVE - Show survival overview
            SURVIVE TIME [hours] - Simulate time passing
            SURVIVE REST [hours] - Rest to recover fatigue
            SURVIVE EAT [amount] - Reduce hunger
            SURVIVE DRINK [amount] - Reduce thirst
        """
        if not args:
            stats = self.survival_service.get_all_stats()
            effects = self.survival_service.get_active_effects()
            warnings = self._get_warnings(stats)

            return {
                "type": "survival_overview",
                "stats": stats,
                "effects": effects,
                "warnings": warnings,
                "critical": any(w['level'] == 'critical' for w in warnings)
            }

        subcmd = args[0].lower()

        if subcmd == "time" and len(args) >= 2:
            try:
                hours = float(args[1])
                changes = self.survival_service.apply_time_decay(hours)
                return {
                    "type": "time_passed",
                    "hours": hours,
                    "changes": changes
                }
            except ValueError:
                return {
                    "type": "error",
                    "message": "Invalid hours value"
                }

        elif subcmd == "rest" and len(args) >= 2:
            try:
                hours = float(args[1])
                # Reduce fatigue, but increase hunger/thirst
                fatigue_reduction = -30 * hours
                hunger_increase = 5 * hours
                thirst_increase = 7 * hours

                changes = {
                    'fatigue': self.survival_service.update_stat(
                        SurvivalStat.FATIGUE, fatigue_reduction, f"Rested {hours}h"
                    ),
                    'hunger': self.survival_service.update_stat(
                        SurvivalStat.HUNGER, hunger_increase, f"Rested {hours}h"
                    ),
                    'thirst': self.survival_service.update_stat(
                        SurvivalStat.THIRST, thirst_increase, f"Rested {hours}h"
                    )
                }

                return {
                    "type": "rested",
                    "hours": hours,
                    "changes": changes
                }
            except ValueError:
                return {
                    "type": "error",
                    "message": "Invalid hours value"
                }

        elif subcmd == "eat" and len(args) >= 2:
            try:
                amount = float(args[1])
                # Reduce hunger
                result = self.survival_service.update_stat(
                    SurvivalStat.HUNGER, -amount, "Ate food"
                )
                return {
                    "type": "ate",
                    "amount": amount,
                    "result": result
                }
            except ValueError:
                return {
                    "type": "error",
                    "message": "Invalid amount value"
                }

        elif subcmd == "drink" and len(args) >= 2:
            try:
                amount = float(args[1])
                # Reduce thirst
                result = self.survival_service.update_stat(
                    SurvivalStat.THIRST, -amount, "Drank water"
                )
                return {
                    "type": "drank",
                    "amount": amount,
                    "result": result
                }
            except ValueError:
                return {
                    "type": "error",
                    "message": "Invalid amount value"
                }

        else:
            return {
                "type": "error",
                "message": "Usage: SURVIVE [TIME/REST/EAT/DRINK]"
            }

    def _get_warnings(self, stats: Dict[str, Dict]) -> List[Dict]:
        """Generate warning messages for critical/warning stats"""
        warnings = []

        for stat_name, stat_info in stats.items():
            if stat_info.get('status') == 'critical':
                warnings.append({
                    "stat": stat_name,
                    "level": "critical",
                    "message": f"{stat_name.upper()} is CRITICAL!",
                    "value": stat_info['current']
                })
            elif stat_info.get('status') == 'warning':
                warnings.append({
                    "stat": stat_name,
                    "level": "warning",
                    "message": f"{stat_name.upper()} needs attention",
                    "value": stat_info['current']
                })

        return warnings


# Helper functions for awarding XP on survival actions
def award_survival_xp(xp_handler, action: str, value: int = 5):
    """Award XP for survival actions"""
    if hasattr(xp_handler, 'award_usage_xp'):
        xp_handler.award_usage_xp(value, f"Survival action: {action}")
