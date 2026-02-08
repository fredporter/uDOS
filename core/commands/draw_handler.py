"""DRAW command handler - viewport-aware ASCII rendering demos."""

from __future__ import annotations

from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.viewport_service import ViewportService
from core.tui.output import OutputToolkit
from core.services.logging_api import get_repo_root
from core.utils.text_width import truncate_to_width, pad_to_width
from core.utils.text_width import display_width


class DrawHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for DRAW command - render ASCII demo panels."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        mode = (params[0].lower().strip() if params else "demo")
        if mode.endswith(".md") or mode.endswith(".txt"):
            return self._block(params)
        if mode == "block":
            return self._block(params[1:])
        if mode in {"demo", "show"}:
            return self._demo()
        if mode in {"map", "grid"}:
            return self._map_panel()
        if mode in {"schedule", "calendar", "todo"}:
            return self._schedule_panel()
        if mode in {"timeline", "progress", "roadmap"}:
            return self._timeline_panel()
        return {
            "status": "error",
            "message": f"Unknown DRAW option: {mode}",
            "output": self._help(),
        }

    def _help(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("DRAW"),
                "DRAW DEMO              Render viewport-sized ASCII demo panels",
                "DRAW BLOCK <text>      Render block text (options: --border --invert --rainbow)",
                "DRAW <file.md>         Render ASCII file from seed templates/demos",
                "DRAW MAP               Render grid/map panel only",
                "DRAW SCHEDULE          Render schedule/calendar/todo panel only",
                "DRAW TIMELINE          Render timeline/progress/roadmap panel only",
            ]
        )

    def _block(self, params: List[str]) -> Dict:
        if not params:
            return {
                "status": "error",
                "message": "DRAW BLOCK requires text",
                "output": self._help(),
            }
        text = []
        file_path = None
        flags = {"--border", "--invert", "--rainbow"}
        border = False
        invert = False
        rainbow = False
        for token in params:
            if token in flags:
                if token == "--border":
                    border = True
                elif token == "--invert":
                    invert = True
                elif token == "--rainbow":
                    rainbow = True
            else:
                if token.endswith(".md") or token.endswith(".txt"):
                    file_path = token
                else:
                    text.append(token)
        if not text and not file_path:
            return {
                "status": "error",
                "message": "DRAW BLOCK requires text",
                "output": self._help(),
            }
        if file_path:
            art_lines = self._load_block_file(file_path)
        else:
            raw_text = " ".join(text)
            cleaned = "".join(ch for ch in raw_text.upper() if ch.isalnum() or ch == " ")
            cleaned = cleaned.replace(" ", "")
            cleaned = cleaned[:6] if cleaned else "?"
            art_lines = self._render_block_text(cleaned)
        output = self._style_block_output(art_lines, border=border, invert=invert, rainbow=rainbow)
        return {"status": "success", "output": output}

    def _demo(self) -> Dict:
        left = self._map_panel_body()
        right = self._schedule_panel_body()
        bottom = self._timeline_panel_body()

        cols = ViewportService().get_cols()
        header = OutputToolkit.banner("DRAW DEMO")
        split = OutputToolkit.columns(left.splitlines(), right.splitlines(), gap=4)
        footer = OutputToolkit.box("Timeline / Progress / Roadmap", bottom, width=cols)

        output = "\n".join([header, "", split, "", footer])
        return {"status": "success", "output": output}

    def _map_panel(self) -> Dict:
        cols = ViewportService().get_cols()
        body = self._map_panel_body()
        return {
            "status": "success",
            "output": OutputToolkit.box("Grid Layer / Map", body, width=cols),
        }

    def _schedule_panel(self) -> Dict:
        cols = ViewportService().get_cols()
        body = self._schedule_panel_body()
        return {
            "status": "success",
            "output": OutputToolkit.box("Schedule / Calendar / Todo", body, width=cols),
        }

    def _timeline_panel(self) -> Dict:
        cols = ViewportService().get_cols()
        body = self._timeline_panel_body()
        return {
            "status": "success",
            "output": OutputToolkit.box("Timeline / Progress / Roadmap", body, width=cols),
        }

    def _map_panel_body(self) -> str:
        cols = ViewportService().get_cols()
        inner = max(16, cols // 2 - 6)
        legend = "Legend: ■ core ▣ node ▢ edge"
        grid = [
            "┌────────────┬────────────┬────────────┐",
            "│ ■ L305-DA11│ ▣ L305-DA12│ ▢ L305-DA13│",
            "├────────────┼────────────┼────────────┤",
            "│ ▢ L305-DB11│ ■ L305-DB12│ ▣ L305-DB13│",
            "├────────────┼────────────┼────────────┤",
            "│ ▣ L305-DC11│ ▢ L305-DC12│ ■ L305-DC13│",
            "└────────────┴────────────┴────────────┘",
        ]
        lines = [legend, ""]
        lines.extend(grid)
        return "\n".join(truncate_to_width(line, inner) for line in lines)

    def _schedule_panel_body(self) -> str:
        cols = ViewportService().get_cols()
        inner = max(18, cols // 2 - 6)
        header = "Mon  Tue  Wed  Thu  Fri"
        rows = [
            "09:00  ■■■  .    .    ■■■  .",
            "11:00  ■■■  ■■■  .    .    .",
            "13:00  .    ■■■  ■■■  .    .",
            "15:00  .    .    ■■■  ■■■  .",
            "17:00  ■■■  .    .    ■■■  ■■■",
        ]
        todo = [
            "",
            "Todo:",
            "  [ ] Review wizard logs",
            "  [x] Sync viewport size",
            "  [ ] Ship v1.3 demo",
        ]
        lines = [header, "-" * len(header)]
        lines.extend(rows)
        lines.extend(todo)
        return "\n".join(truncate_to_width(line, inner) for line in lines)

    def _timeline_panel_body(self) -> str:
        cols = ViewportService().get_cols()
        inner = max(30, cols - 8)
        milestones = [
            ("v1.3.0", "Core setup + TUI"),
            ("v1.3.1", "Wizard dashboard"),
            ("v1.3.2", "Noun Project UI"),
            ("v1.3.3", "Self-heal + ports"),
        ]
        max_label = max(len(m[0]) for m in milestones)
        lines = ["Roadmap:"]
        for idx, (label, desc) in enumerate(milestones, 1):
            bar = OutputToolkit.progress_bar(idx, len(milestones), width=18)
            line = f"  {pad_to_width(label, max_label)}  {bar}  {desc}"
            lines.append(truncate_to_width(line, inner))
        return "\n".join(lines)

    def _render_block_text(self, text: str) -> List[str]:
        font = self._block_font()
        words = (text or "").upper().split()
        lines: List[str] = []
        for word in words:
            word_lines = [""] * 5
            for ch in word:
                glyph = font.get(ch, font["?"])
                for i in range(5):
                    word_lines[i] += glyph[i] + "  "
            if lines:
                lines.append("")
            lines.extend(word_lines)
        return lines or ["?"]

    def _load_block_file(self, file_arg: str) -> List[str]:
        repo_root = get_repo_root()
        candidates = []
        path = file_arg
        if not path.startswith("/"):
            candidates.extend(
                [
                    repo_root / "memory" / "system" / path,
                    repo_root / "memory" / "story" / path,
                    repo_root / "core" / "framework" / "seed" / "bank" / "system" / path,
                    repo_root / path,
                ]
            )
        else:
            candidates.append(path)
        for candidate in candidates:
            try:
                if hasattr(candidate, "exists") and candidate.exists():
                    content = candidate.read_text()
                    lines = [line.rstrip("\n") for line in content.splitlines()]
                    # Strip markdown code fences if present
                    while lines and (not lines[0].strip() or lines[0].strip().startswith("```")):
                        lines.pop(0)
                    while lines and (not lines[-1].strip() or lines[-1].strip().startswith("```")):
                        lines.pop()
                    return lines or [""]
            except Exception:
                continue
        return ["(missing block file)"]

    def _block_font(self) -> Dict[str, List[str]]:
        return {
            "A": ["█████", "██  ██", "█████", "██  ██", "██  ██"],
            "B": ["█████", "██  ██", "█████", "██  ██", "█████"],
            "C": ["█████", "██   ", "██   ", "██   ", "█████"],
            "D": ["████ ", "██ ██", "██ ██", "██ ██", "████ "],
            "E": ["█████", "██   ", "████ ", "██   ", "█████"],
            "F": ["█████", "██   ", "████ ", "██   ", "██   "],
            "G": ["█████", "██   ", "██ ██", "██  ██", "█████"],
            "H": ["██  ██", "██  ██", "█████", "██  ██", "██  ██"],
            "I": ["█████", "  ██ ", "  ██ ", "  ██ ", "█████"],
            "J": ["█████", "   ██", "   ██", "██ ██", "████ "],
            "K": ["██ ██", "███  ", "████ ", "███  ", "██ ██"],
            "L": ["██   ", "██   ", "██   ", "██   ", "█████"],
            "M": ["██ ██", "█████", "██ ██", "██  ██", "██  ██"],
            "N": ["██  ██", "███ ██", "█████", "██ ███", "██  ██"],
            "O": ["█████", "██  ██", "██  ██", "██  ██", "█████"],
            "P": ["█████", "██  ██", "█████", "██   ", "██   "],
            "Q": ["█████", "██  ██", "██  ██", "██ ███", "█████"],
            "R": ["█████", "██  ██", "█████", "██ ██", "██  ██"],
            "S": ["█████", "██   ", "█████", "   ██", "█████"],
            "T": ["█████", "  ██ ", "  ██ ", "  ██ ", "  ██ "],
            "U": ["██  ██", "██  ██", "██  ██", "██  ██", "█████"],
            "V": ["██  ██", "██  ██", "██  ██", " ███ ", "  █  "],
            "W": ["██  ██", "██  ██", "██ ██", "█████", "██ ██"],
            "X": ["██  ██", " ███ ", "  █  ", " ███ ", "██  ██"],
            "Y": ["██  ██", " ███ ", "  █  ", "  █  ", "  █  "],
            "Z": ["█████", "   ██", "  ██ ", " ██  ", "█████"],
            "0": ["█████", "██ ██", "██ ██", "██ ██", "█████"],
            "1": ["  ██ ", " ███ ", "  ██ ", "  ██ ", "█████"],
            "2": ["█████", "   ██", "█████", "██   ", "█████"],
            "3": ["█████", "   ██", " ███ ", "   ██", "█████"],
            "4": ["██ ██", "██ ██", "█████", "   ██", "   ██"],
            "5": ["█████", "██   ", "█████", "   ██", "█████"],
            "6": ["█████", "██   ", "█████", "██  ██", "█████"],
            "7": ["█████", "   ██", "  ██ ", " ██  ", " ██  "],
            "8": ["█████", "██  ██", "█████", "██  ██", "█████"],
            "9": ["█████", "██  ██", "█████", "   ██", "█████"],
            "?": ["█████", "   ██", " ███ ", "     ", "  ██ "],
            " ": ["  ", "  ", "  ", "  ", "  "],
        }

    def _style_block_output(self, lines: List[str], border: bool, invert: bool, rainbow: bool) -> str:
        if not lines:
            return ""
        width = max(display_width(line) for line in lines)
        padded = [pad_to_width(line, width) for line in lines]

        if border:
            pad_inner = width + 4
            top = "█" * pad_inner
            framed = [top]
            framed.append("██" + (" " * (pad_inner - 4)) + "██")
            for line in padded:
                framed.append(f"██  {line}  ██")
            framed.append("██" + (" " * (pad_inner - 4)) + "██")
            framed.append(top)
            padded = framed

        styled = []
        if rainbow:
            colors = ["\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m"]
            for idx, line in enumerate(padded):
                color = colors[idx % len(colors)]
                styled.append(f"{color}{line}\033[0m")
        else:
            styled = padded[:]

        if invert:
            styled = [OutputToolkit.invert(line) for line in styled]

        output = "\n".join(styled)
        return OutputToolkit._clamp(output)
