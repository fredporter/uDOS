"""DRAW command handler - viewport-aware ASCII rendering demos."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.services.viewport_service import ViewportService
from core.tui.output import OutputToolkit
from core.services.logging_api import get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.utils.text_width import truncate_to_width, pad_to_width
from core.utils.text_width import display_width


class DrawHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for DRAW command - render ASCII demo panels."""

    def __init__(self):
        super().__init__()
        self._pattern_index = 0

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        runtime_mode = "auto"
        args = params[:]
        if args and args[0].lower() in {"--py", "--ts"}:
            runtime_mode = args[0][2:].lower()
            args = args[1:]

        md_output, save_path, args = self._extract_output_flags(args)
        mode = (args[0].lower().strip() if args else "demo")
        if mode == "md":
            md_output = True
            args = args[1:]
            mode = (args[0].lower().strip() if args else "demo")

        if mode == "pat":
            if runtime_mode == "py":
                result = self._pattern_py(args[1:])
            else:
                result = self._pattern(args[1:])
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW PAT")
        if mode.endswith(".md") or mode.endswith(".txt"):
            result = self._block(args)
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW BLOCK")
        if mode == "block":
            result = self._block(args[1:])
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW BLOCK")
        if mode in {"demo", "show"}:
            result = self._demo()
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW DEMO")
        if mode in {"map", "grid"}:
            result = self._map_panel()
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW MAP")
        if mode in {"schedule", "calendar", "todo"}:
            result = self._schedule_panel()
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW SCHEDULE")
        if mode in {"timeline", "progress", "roadmap"}:
            result = self._timeline_panel()
            return self._finalize_output(result, md_output=md_output, save_path=save_path, title="DRAW TIMELINE")
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
                "DRAW MD <mode>         Render any DRAW mode as markdown fenced diagram",
                "DRAW --md <mode>       Same as DRAW MD; keeps script-friendly arg order",
                "DRAW --save <file.md>  Save output (plain or markdown) under memory/story by default",
                "DRAW MAP               Render grid/map panel only",
                "DRAW SCHEDULE          Render schedule/calendar/todo panel only",
                "DRAW TIMELINE          Render timeline/progress/roadmap panel only",
                "DRAW PAT [args]        Pattern ops (LIST|CYCLE|TEXT|<pattern>) via TS (default) or --py",
            ]
        )

    def _extract_output_flags(self, args: List[str]) -> Tuple[bool, Optional[str], List[str]]:
        md_output = False
        save_path: Optional[str] = None
        out: List[str] = []
        i = 0
        while i < len(args):
            tok = args[i]
            low = tok.lower()
            if low == "--md":
                md_output = True
                i += 1
                continue
            if low == "--save":
                if i + 1 < len(args):
                    save_path = args[i + 1]
                    i += 2
                    continue
            out.append(tok)
            i += 1
        return md_output, save_path, out

    def _pattern(self, params: List[str]) -> Dict:
        script = get_repo_root() / "core" / "runtime" / "pattern_runner.js"
        if not script.exists():
            return {"status": "error", "message": f"Pattern runner missing: {script}"}

        action = "render"
        args: List[str] = []
        if not params:
            action = "render"
            name = ["c64", "chevrons", "scanlines", "raster", "progress", "mosaic"][self._pattern_index % 6]
            self._pattern_index += 1
            args = [name]
        else:
            head = params[0].lower()
            if head == "list":
                action = "list"
            elif head == "cycle":
                action = "cycle"
                args = params[1:]
            elif head == "text":
                action = "text"
                args = params[1:]
            else:
                action = "render"
                args = [head]

        ts_runtime = TSRuntimeService()
        cmd = [ts_runtime.node_cmd, str(script), action, *args]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "DRAW PAT failed",
                "details": result.stderr.strip() or result.stdout.strip(),
            }

        try:
            payload = json.loads(result.stdout.strip() or "{}")
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid DRAW PAT payload", "details": result.stdout.strip()}

        status = payload.get("status", "error")
        if action == "list" and status == "success":
            pats = payload.get("patterns", [])
            lines = [OutputToolkit.banner("DRAW PAT LIST"), ""]
            for p in pats:
                lines.append(f"- {p}")
            return {"status": "success", "output": "\n".join(lines), "patterns": pats}

        output = payload.get("output") or payload.get("message") or "No output"
        return {"status": status, "message": payload.get("message", "DRAW PAT"), "output": output, "payload": payload}

    def _pattern_py(self, params: List[str]) -> Dict:
        patterns = ["c64", "chevrons", "scanlines", "raster", "progress", "mosaic"]
        if not params:
            name = patterns[self._pattern_index % len(patterns)]
            self._pattern_index += 1
            return {"status": "success", "message": "DRAW PAT (py)", "output": self._render_py_pattern(name), "pattern": name}

        head = params[0].lower()
        if head == "list":
            lines = [OutputToolkit.banner("DRAW PAT LIST"), ""]
            lines.extend(f"- {p}" for p in patterns)
            return {"status": "success", "message": "Pattern list", "patterns": patterns, "output": "\n".join(lines)}

        if head == "cycle":
            name = patterns[self._pattern_index % len(patterns)]
            self._pattern_index += 1
            return {"status": "success", "message": "DRAW PAT CYCLE (py)", "output": self._render_py_pattern(name), "pattern": name}

        if head == "text":
            text = " ".join(params[1:]).strip() or "DRAW"
            return self._block(text.split())

        name = head
        if name not in patterns:
            return {"status": "error", "message": f"Unknown pattern: {name}", "output": "Use: DRAW PAT LIST"}
        return {"status": "success", "message": "DRAW PAT (py)", "output": self._render_py_pattern(name), "pattern": name}

    def _render_py_pattern(self, name: str) -> str:
        cols = max(24, ViewportService().get_cols())
        width = min(cols - 2, 72)
        if name == "scanlines":
            lines = [("█" * width) if i % 2 == 0 else ("░" * width) for i in range(10)]
            return "\n".join(lines)
        if name == "chevrons":
            return "\n".join(
                truncate_to_width((" " * i) + ">>>>>=====<<<<<", width) for i in range(0, 10)
            )
        if name == "raster":
            lines = []
            for row in range(10):
                line = "".join("▓" if (row + col) % 2 == 0 else "░" for col in range(min(width, 48)))
                lines.append(line)
            return "\n".join(lines)
        if name == "progress":
            lines = [OutputToolkit.progress_bar(i, 10, width=28) for i in range(1, 11)]
            return "\n".join(lines)
        if name == "mosaic":
            return "\n".join(
                "".join("█" if (r * c) % 3 == 0 else "▒" if (r + c) % 2 == 0 else "░" for c in range(min(width, 48)))
                for r in range(10)
            )
        # c64 default
        rows = [
            "╔" + "═" * (min(width, 48) - 2) + "╗",
            "║  COMMODORE 64 STYLE RASTER DEMO"[: max(0, min(width, 48) - 1)],
            "╠" + "═" * (min(width, 48) - 2) + "╣",
        ]
        for i in range(6):
            fill = "".join("█" if (i + j) % 3 == 0 else " " for j in range(min(width, 48) - 4))
            rows.append(f"║ {fill} ║")
        rows.append("╚" + "═" * (min(width, 48) - 2) + "╝")
        return "\n".join(rows)

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

    def _to_markdown_diagram(self, output: str, title: str) -> str:
        body = (output or "").rstrip("\n")
        lines = [f"# {title}", "", "```text", body, "```", ""]
        return "\n".join(lines)

    def _resolve_save_path(self, save_path: str) -> Path:
        target = Path(save_path)
        if target.is_absolute():
            return target
        repo_root = get_repo_root()
        return repo_root / "memory" / "story" / target

    def _finalize_output(
        self,
        result: Dict,
        *,
        md_output: bool = False,
        save_path: Optional[str] = None,
        title: str = "DRAW",
    ) -> Dict:
        if not isinstance(result, dict) or result.get("status") != "success":
            return result

        output = str(result.get("output", ""))
        if md_output:
            output = self._to_markdown_diagram(output, title)
            result["output"] = output
            result["format"] = "markdown"
        else:
            result["format"] = "text"

        if save_path:
            try:
                target = self._resolve_save_path(save_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(output)
                result["saved_to"] = str(target)
                message = result.get("message") or "DRAW saved"
                result["message"] = f"{message} | saved: {target}"
            except Exception as exc:
                return {
                    "status": "error",
                    "message": f"Failed to save DRAW output: {exc}",
                    "output": result.get("output", ""),
                }
        return result
