"""RULE command handler - conditional gameplay automations paired with PLAY."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .base import BaseCommandHandler


class RuleHandler(BaseCommandHandler):
    """Handle RULE command surface.

    Commands:
      RULE
      RULE LIST
      RULE SHOW <rule_id>
      RULE ADD <rule_id> IF <condition> THEN <actions>
      RULE REMOVE <rule_id>
      RULE ENABLE <rule_id>
      RULE DISABLE <rule_id>
      RULE RUN [rule_id]
      RULE TEST IF <condition>
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        from core.services.gameplay_service import get_gameplay_service
        from core.services.user_service import get_user_manager

        current_user = get_user_manager().current()
        if not current_user:
            return {"status": "error", "message": "No active user"}

        gameplay = get_gameplay_service()
        username = current_user.username
        role = current_user.role.value
        gameplay.tick(username)

        if not params:
            return self._list_rules(gameplay)

        sub = params[0].lower()
        if sub in {"list", "status"}:
            return self._list_rules(gameplay)
        if sub == "show":
            if len(params) < 2:
                return {"status": "error", "message": "Syntax: RULE SHOW <rule_id>"}
            rule = gameplay.get_rule(params[1])
            if not rule:
                return {"status": "error", "message": f"Unknown rule: {params[1]}"}
            return {
                "status": "success",
                "message": f"Rule {params[1]}",
                "rule": rule,
                "output": self._format_rule(rule),
            }

        if sub == "add":
            if not gameplay.has_permission(role, "gameplay.rule_admin"):
                return {"status": "error", "message": "Permission denied: gameplay.rule_admin"}
            parsed = self._parse_add(params[1:])
            if not parsed:
                return {
                    "status": "error",
                    "message": "Syntax: RULE ADD <rule_id> IF <condition> THEN <actions>",
                }
            rule_id, if_expr, then_expr = parsed
            try:
                row = gameplay.set_rule(rule_id, if_expr=if_expr, then_expr=then_expr, source=f"rule:{username}")
            except ValueError as exc:
                return {"status": "error", "message": str(exc)}
            return {
                "status": "success",
                "message": f"Rule upserted: {rule_id}",
                "rule": row,
                "output": self._format_rule(row),
            }

        if sub == "remove":
            if not gameplay.has_permission(role, "gameplay.rule_admin"):
                return {"status": "error", "message": "Permission denied: gameplay.rule_admin"}
            if len(params) < 2:
                return {"status": "error", "message": "Syntax: RULE REMOVE <rule_id>"}
            ok = gameplay.delete_rule(params[1])
            if not ok:
                return {"status": "error", "message": f"Unknown rule: {params[1]}"}
            return {"status": "success", "message": f"Rule removed: {params[1]}", "output": f"Removed rule {params[1]}"}

        if sub in {"enable", "disable"}:
            if not gameplay.has_permission(role, "gameplay.rule_admin"):
                return {"status": "error", "message": "Permission denied: gameplay.rule_admin"}
            if len(params) < 2:
                return {"status": "error", "message": f"Syntax: RULE {sub.upper()} <rule_id>"}
            row = gameplay.set_rule_enabled(params[1], enabled=(sub == "enable"))
            if not row:
                return {"status": "error", "message": f"Unknown rule: {params[1]}"}
            return {
                "status": "success",
                "message": f"Rule {'enabled' if sub == 'enable' else 'disabled'}: {params[1]}",
                "rule": row,
                "output": self._format_rule(row),
            }

        if sub == "run":
            rid = params[1] if len(params) > 1 else None
            result = gameplay.run_rules(username, rid)
            fired = result.get("fired", [])
            blocked = result.get("blocked", [])
            lines = [f"RULE RUN {rid or 'all'}", f"fired={len(fired)} blocked={len(blocked)}"]
            for row in fired[:10]:
                lines.append(f"- fired: {row.get('id')}")
            for row in blocked[:10]:
                lines.append(f"- blocked: {row.get('id')} ({row.get('reason')})")
            return {
                "status": "success",
                "message": "Rules executed",
                "result": result,
                "output": "\n".join(lines),
            }

        if sub == "test":
            if len(params) < 3 or params[1].lower() != "if":
                return {"status": "error", "message": "Syntax: RULE TEST IF <condition>"}
            if_expr = " ".join(params[2:])
            requirements = gameplay._requirements_from_if_expression(if_expr)  # noqa: SLF001
            verdict = gameplay._evaluate_requirements(username, requirements)  # noqa: SLF001
            return {
                "status": "success",
                "message": "Rule condition evaluated",
                "requirements": requirements,
                "verdict": verdict,
                "output": f"RULE TEST IF {if_expr}\nok={verdict.get('ok')} blocked_by={verdict.get('blocked_by', [])}",
            }

        if sub in {"help", "-h", "--help"}:
            return {
                "status": "success",
                "message": self.__doc__ or "RULE help",
                "output": (self.__doc__ or "RULE help").strip(),
            }

        return {"status": "error", "message": f"Unknown RULE subcommand: {sub}"}

    def _parse_add(self, params: List[str]) -> Optional[Tuple[str, str, str]]:
        if len(params) < 4:
            return None
        rule_id = params[0]
        rest = " ".join(params[1:])
        upper = rest.upper()
        if_idx = upper.find("IF ")
        then_idx = upper.find(" THEN ")
        if if_idx != 0 or then_idx < 0:
            return None
        if_expr = rest[3:then_idx].strip()
        then_expr = rest[then_idx + 6 :].strip()
        if not if_expr or not then_expr:
            return None
        return rule_id, if_expr, then_expr

    def _list_rules(self, gameplay) -> Dict:
        rules = gameplay.list_rules()
        lines = ["RULE LIST"]
        for rid in sorted(rules.keys()):
            row = rules.get(rid, {})
            state = "on" if row.get("enabled", True) else "off"
            lines.append(f"- {rid} [{state}] IF {row.get('if', '')} THEN {row.get('then', '')}")
        if len(lines) == 1:
            lines.append("- none")
        return {
            "status": "success",
            "message": "Gameplay rules",
            "rules": rules,
            "output": "\n".join(lines),
        }

    def _format_rule(self, row: Dict) -> str:
        rid = row.get("id", "rule")
        state = "enabled" if row.get("enabled", True) else "disabled"
        return (
            f"RULE {rid}\n"
            f"State: {state}\n"
            f"IF: {row.get('if', '')}\n"
            f"THEN: {row.get('then', '')}"
        )
