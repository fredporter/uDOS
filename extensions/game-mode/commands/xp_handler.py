"""
XP Command Handler for uDOS v1.0.18
Handles XP, SKILL, and ACHIEVEMENT commands
"""

from typing import Dict, List, Optional
from core.services.xp_service import XPService, XPCategory, SkillTree


class XPCommandHandler:
    """Handles experience point related commands"""

    def __init__(self):
        self.xp_service = XPService()
        self.commands = {
            "XP": self.handle_xp,
            "SKILL": self.handle_skill,
            "SKILLS": self.handle_skills,
            "ACHIEVEMENT": self.handle_achievement,
            "ACHIEVEMENTS": self.handle_achievements
        }

    def handle_command(self, command: str, args: List[str]) -> Dict:
        """Route command to appropriate handler"""
        cmd = command.upper()
        if cmd in self.commands:
            return self.commands[cmd](args)
        return {"error": f"Unknown XP command: {command}"}

    def handle_xp(self, args: List[str]) -> Dict:
        """
        Handle XP command

        Usage:
            XP                  - Show total XP and level
            XP STATUS           - Same as XP
            XP BREAKDOWN        - Show XP by category
            XP HISTORY [n]      - Show recent XP transactions
        """
        if not args or args[0].upper() == "STATUS":
            return self._xp_status()

        subcommand = args[0].upper()

        if subcommand == "BREAKDOWN":
            return self._xp_breakdown()
        elif subcommand == "HISTORY":
            limit = int(args[1]) if len(args) > 1 else 10
            return self._xp_history(limit)
        else:
            return {"error": f"Unknown XP subcommand: {args[0]}"}

    def _xp_status(self) -> Dict:
        """Show total XP and equivalent level"""
        total_xp = self.xp_service.get_total_xp()
        breakdown = self.xp_service.get_xp_breakdown()

        # Calculate overall level from total XP
        level = self.xp_service._calculate_level(total_xp)
        next_level_xp = self.xp_service._xp_for_level(level + 1)

        return {
            "type": "xp_status",
            "total_xp": total_xp,
            "level": level,
            "next_level_xp": next_level_xp,
            "breakdown": breakdown,
            "message": f"💫 Total XP: {total_xp} (Level {level})\n" +
                      f"   Next Level: {next_level_xp - total_xp} XP needed\n\n" +
                      f"   📊 Category Breakdown:\n" +
                      f"      Usage:        {breakdown['usage']} XP\n" +
                      f"      Information:  {breakdown['information']} XP\n" +
                      f"      Contribution: {breakdown['contribution']} XP\n" +
                      f"      Connection:   {breakdown['connection']} XP"
        }

    def _xp_breakdown(self) -> Dict:
        """Show detailed XP breakdown"""
        breakdown = self.xp_service.get_xp_breakdown()
        total = self.xp_service.get_total_xp()

        lines = ["📊 XP Breakdown by Category\n"]
        lines.append("=" * 40)

        for category, xp in breakdown.items():
            percentage = (xp / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            lines.append(f"{category.capitalize():12} {xp:6} XP [{bar}] {percentage:.1f}%")

        lines.append("=" * 40)
        lines.append(f"{'Total':12} {total:6} XP")

        return {
            "type": "xp_breakdown",
            "breakdown": breakdown,
            "total": total,
            "message": "\n".join(lines)
        }

    def _xp_history(self, limit: int) -> Dict:
        """Show recent XP transactions"""
        transactions = self.xp_service.get_recent_xp(limit)

        if not transactions:
            return {
                "type": "xp_history",
                "transactions": [],
                "message": "No XP transactions yet"
            }

        lines = [f"📜 Recent XP Transactions (Last {len(transactions)})\n"]
        lines.append("=" * 60)

        for tx in transactions:
            timestamp = tx['timestamp'].split('T')[1][:8]  # HH:MM:SS
            lines.append(
                f"{timestamp} | {tx['category'].capitalize():12} | "
                f"+{tx['amount']:3} XP | {tx['reason']}"
            )

        return {
            "type": "xp_history",
            "transactions": transactions,
            "message": "\n".join(lines)
        }

    def handle_skill(self, args: List[str]) -> Dict:
        """
        Handle SKILL command

        Usage:
            SKILL <name>        - Show specific skill status
        """
        if not args:
            return {"error": "Usage: SKILL <name>"}

        skill_name = args[0].lower()

        # Find matching skill
        skill = None
        for s in SkillTree:
            if s.value == skill_name:
                skill = s
                break

        if not skill:
            return {"error": f"Unknown skill: {skill_name}\nAvailable: {', '.join(s.value for s in SkillTree)}"}

        status = self.xp_service.get_skill_status(skill)

        # Build progress bar
        progress = status['progress_percent']
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        return {
            "type": "skill_status",
            "skill": status,
            "message": f"🎯 {skill.value.capitalize()} Skill\n" +
                      f"   Level: {status['level']}\n" +
                      f"   XP: {status['xp']} / {status['next_level_xp']}\n" +
                      f"   Progress: [{bar}] {progress}%"
        }

    def handle_skills(self, args: List[str]) -> Dict:
        """
        Handle SKILLS command

        Usage:
            SKILLS              - Show all skill statuses
        """
        all_skills = self.xp_service.get_all_skills()

        lines = ["🎯 Survival Skills Progress\n"]
        lines.append("=" * 60)
        lines.append(f"{'Skill':<12} {'Level':<7} {'XP':<15} {'Progress'}")
        lines.append("-" * 60)

        for skill_data in all_skills:
            skill = skill_data['skill'].capitalize()
            level = f"Lv {skill_data['level']}"
            xp = f"{skill_data['xp']}/{skill_data['next_level_xp']}"

            # Progress bar
            progress = skill_data['progress_percent']
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            progress_display = f"[{bar}] {progress}%"

            lines.append(f"{skill:<12} {level:<7} {xp:<15} {progress_display}")

        return {
            "type": "skills_status",
            "skills": all_skills,
            "message": "\n".join(lines)
        }

    def handle_achievement(self, args: List[str]) -> Dict:
        """
        Handle ACHIEVEMENT command (alias for ACHIEVEMENTS)
        """
        return self.handle_achievements(args)

    def handle_achievements(self, args: List[str]) -> Dict:
        """
        Handle ACHIEVEMENTS command

        Usage:
            ACHIEVEMENTS            - Show all achievements
            ACHIEVEMENTS UNLOCKED   - Show only unlocked achievements
        """
        unlocked_only = args and args[0].upper() == "UNLOCKED"
        achievements = self.xp_service.get_achievements(unlocked_only)

        if not achievements:
            return {
                "type": "achievements",
                "achievements": [],
                "message": "No achievements unlocked yet. Keep exploring!"
            }

        unlocked = [a for a in achievements if a['unlocked']]
        total = len(achievements)

        lines = [f"🏆 Achievements ({len(unlocked)}/{total} Unlocked)\n"]
        lines.append("=" * 60)

        for ach in achievements:
            status = "✅" if ach['unlocked'] else "🔒"
            lines.append(f"{status} {ach['name']}")
            lines.append(f"   {ach['description']}")

            if ach['unlocked'] and ach['unlocked_at']:
                date = ach['unlocked_at'].split('T')[0]
                lines.append(f"   Unlocked: {date}")

            lines.append("")

        return {
            "type": "achievements",
            "achievements": achievements,
            "unlocked_count": len(unlocked),
            "total_count": total,
            "message": "\n".join(lines)
        }


def award_usage_xp(command: str, xp_service: Optional[XPService] = None) -> None:
    """
    Award XP for command usage.
    Call this from command handlers to award usage XP.

    Args:
        command: Command that was executed
        xp_service: XP service instance (creates new if None)
    """
    if xp_service is None:
        xp_service = XPService()

    # Award 1 XP for any command usage
    result = xp_service.award_xp(
        XPCategory.USAGE,
        1,
        reason=f"Command executed: {command}",
        context=command
    )

    # Check for achievements
    if result.get('achievements'):
        for ach in result['achievements']:
            print(f"\n🎉 Achievement Unlocked: {ach['name']}")
            print(f"   {ach['description']}\n")


def award_information_xp(amount: int, context: str, xp_service: Optional[XPService] = None) -> None:
    """
    Award XP for consuming information.

    Args:
        amount: XP amount (typically 5-50 depending on content length)
        context: What was read (guide name, article, etc)
        xp_service: XP service instance (creates new if None)
    """
    if xp_service is None:
        xp_service = XPService()

    result = xp_service.award_xp(
        XPCategory.INFORMATION,
        amount,
        reason=f"Knowledge consumed",
        context=context
    )

    if result.get('achievements'):
        for ach in result['achievements']:
            print(f"\n🎉 Achievement Unlocked: {ach['name']}")
            print(f"   {ach['description']}\n")


def award_contribution_xp(amount: int, context: str, xp_service: Optional[XPService] = None) -> None:
    """
    Award XP for contributing knowledge/resources.

    Args:
        amount: XP amount (typically 10-100 depending on contribution)
        context: What was contributed
        xp_service: XP service instance (creates new if None)
    """
    if xp_service is None:
        xp_service = XPService()

    result = xp_service.award_xp(
        XPCategory.CONTRIBUTION,
        amount,
        reason=f"Knowledge/resource contributed",
        context=context
    )

    if result.get('achievements'):
        for ach in result['achievements']:
            print(f"\n🎉 Achievement Unlocked: {ach['name']}")
            print(f"   {ach['description']}\n")


def award_connection_xp(amount: int, context: str, xp_service: Optional[XPService] = None) -> None:
    """
    Award XP for making connections.

    Args:
        amount: XP amount (typically 20-50 per connection)
        context: Who/what was connected
        xp_service: XP service instance (creates new if None)
    """
    if xp_service is None:
        xp_service = XPService()

    result = xp_service.award_xp(
        XPCategory.CONNECTION,
        amount,
        reason=f"Connection established",
        context=context
    )

    if result.get('achievements'):
        for ach in result['achievements']:
            print(f"\n🎉 Achievement Unlocked: {ach['name']}")
            print(f"   {ach['description']}\n")
