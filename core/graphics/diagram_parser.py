"""
Diagram Parser

Parse and render text-based diagrams:
- Markdown fenced code blocks (```diagram, ```teletext, ```pattern)
- ASCII art diagrams
- Flowcharts (flowchart.js syntax)
- Sequence diagrams
- Grid-based spatial diagrams
"""

from typing import List, Dict, Tuple, Optional
import re


class DiagramParser:
    """Parse text diagrams and convert to renderable format"""

    DIAGRAM_TYPES = [
        "diagram",
        "teletext",
        "pattern",
        "flowchart",
        "sequence",
        "grid",
        "ascii-art",
    ]

    def __init__(self):
        self.parsers = {
            "teletext": self.parse_teletext,
            "pattern": self.parse_pattern,
            "flowchart": self.parse_flowchart,
            "grid": self.parse_grid,
        }

    def extract_diagrams(self, markdown_text: str) -> List[Dict]:
        """Extract all diagram blocks from markdown"""
        diagrams = []

        # Match fenced code blocks
        pattern = r"```(\w+)(.*?)\n(.*?)```"
        matches = re.finditer(pattern, markdown_text, re.DOTALL)

        for match in matches:
            lang = match.group(1)
            options = match.group(2).strip()
            content = match.group(3)

            if lang in self.DIAGRAM_TYPES:
                diagrams.append(
                    {
                        "type": lang,
                        "options": self.parse_options(options),
                        "content": content,
                        "raw": match.group(0),
                    }
                )

        return diagrams

    def parse_options(self, options_str: str) -> Dict:
        """Parse diagram options from block header"""
        opts = {}
        if not options_str:
            return opts

        # Simple key=value parsing
        pairs = re.findall(r'(\w+)=(["\']?)([^"\'>\s]+)\2', options_str)
        for key, _, value in pairs:
            opts[key] = value

        return opts

    def parse_teletext(self, content: str, options: Dict) -> Dict:
        """Parse teletext block diagram

        Expected format:
        ```teletext width=80 height=24
        [line of teletext characters]
        [line of teletext characters]
        ...
        ```
        """
        lines = content.strip().split("\n")
        width = int(options.get("width", 80))
        height = int(options.get("height", len(lines)))

        # Pad or truncate lines
        processed_lines = []
        for line in lines[:height]:
            if len(line) < width:
                line = line + " " * (width - len(line))
            elif len(line) > width:
                line = line[:width]
            processed_lines.append(line)

        # Pad height if needed
        while len(processed_lines) < height:
            processed_lines.append(" " * width)

        return {
            "type": "teletext",
            "width": width,
            "height": height,
            "lines": processed_lines,
        }

    def parse_pattern(self, content: str, options: Dict) -> Dict:
        """Parse pattern definition

        Expected format:
        ```pattern type=chevrons phase=0
        (pattern description or parameters)
        ```
        """
        pattern_type = options.get("type", "generic")
        phase = int(options.get("phase", 0))

        return {
            "type": "pattern",
            "pattern_type": pattern_type,
            "phase": phase,
            "content": content.strip(),
        }

    def parse_flowchart(self, content: str, options: Dict) -> Dict:
        """Parse flowchart.js syntax

        Simple node/edge parsing for terminal rendering
        """
        nodes = []
        edges = []

        for line in content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            # Node definition: id=>type: text
            if "=>" in line:
                match = re.match(r"(\w+)=>(\w+):\s*(.+)", line)
                if match:
                    node_id, node_type, text = match.groups()
                    nodes.append(
                        {
                            "id": node_id,
                            "type": node_type,
                            "text": text,
                        }
                    )

            # Edge definition: id1->id2
            elif "->" in line:
                parts = line.split("->")
                if len(parts) == 2:
                    edges.append(
                        {
                            "from": parts[0].strip(),
                            "to": parts[1].strip(),
                        }
                    )

        return {
            "type": "flowchart",
            "nodes": nodes,
            "edges": edges,
        }

    def parse_grid(self, content: str, options: Dict) -> Dict:
        """Parse grid-based spatial diagram

        Expected format:
        ```grid layer=L300 cell=AA10
        [grid content with location markers]
        ```
        """
        layer = options.get("layer", "L300")
        cell = options.get("cell", "AA10")

        lines = content.strip().split("\n")

        return {
            "type": "grid",
            "layer": layer,
            "cell": cell,
            "lines": lines,
        }

    def parse(self, markdown_text: str) -> List[Dict]:
        """Parse all diagrams in markdown text"""
        diagrams = self.extract_diagrams(markdown_text)

        parsed = []
        for diagram in diagrams:
            dtype = diagram["type"]
            if dtype in self.parsers:
                result = self.parsers[dtype](diagram["content"], diagram["options"])
                result["raw"] = diagram["raw"]
                parsed.append(result)
            else:
                # Return as-is for unknown types
                parsed.append(diagram)

        return parsed


if __name__ == "__main__":
    # Demo parsing
    test_markdown = """
# Test Document

Some text here.

```teletext width=40 height=3
🬀🬁🬂🬃🬄🬅🬆🬇🬈🬉
▀▄█▌▐▖▗▘▙▚▛▜▝▞▟
░▒▓█
```

More text.

```pattern type=chevrons phase=5
Animated chevron pattern
```

```flowchart
start=>start: Start
process=>operation: Process Data
end=>end: End
start->process
process->end
```
"""

    parser = DiagramParser()
    diagrams = parser.parse(test_markdown)

    print(f"Found {len(diagrams)} diagrams:\n")
    for i, diag in enumerate(diagrams, 1):
        print(f"{i}. Type: {diag['type']}")
        if "lines" in diag:
            print(f"   Lines: {len(diag['lines'])}")
        print()
