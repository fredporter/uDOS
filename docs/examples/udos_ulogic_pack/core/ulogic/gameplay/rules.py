from __future__ import annotations
from typing import Any, Dict, Tuple
import re

class GateEvaluator:
    _re = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=|<=|==|!=|>|<)\s*([0-9]+)\s*$")

    def evaluate(self, expr: str, metrics: Dict[str, Any]) -> Tuple[bool, str]:
        m = self._re.match(expr.strip())
        if not m: return False, "invalid_expr"
        key, op, num = m.group(1), m.group(2), float(m.group(3))
        lhs = float(metrics.get(key, 0))
        if op == ">=": ok = lhs >= num
        elif op == "<=": ok = lhs <= num
        elif op == ">": ok = lhs > num
        elif op == "<": ok = lhs < num
        elif op == "==": ok = lhs == num
        else: ok = lhs != num
        return ok, f"{key}={lhs} {op} {num}"
