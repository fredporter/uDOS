from __future__ import annotations
from typing import List
def lint_markdown(text: str) -> List[str]:
    errs: List[str] = []
    if "\t" in text: errs.append("tabs_found")
    if not text.strip(): errs.append("empty")
    return errs
