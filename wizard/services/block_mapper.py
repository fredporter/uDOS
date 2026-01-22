"""
BlockMapper — Parse uDOS markdown ↔ Notion blocks

Maps between:
- uDOS markdown format (standard + runtime blocks)
- Internal Block representation
- Notion API JSON format

Supports roundtrip conversion: markdown → blocks → Notion → markdown
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class BlockType(str, Enum):
    """Standard + Runtime block types"""

    # Standard Markdown
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    PARAGRAPH = "paragraph"
    QUOTE = "quote"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    TO_DO = "to_do"
    CODE = "code"
    IMAGE = "image"
    DIVIDER = "divider"
    CALLOUT = "callout"

    # Runtime Blocks
    STATE = "state"
    SET = "set"
    FORM = "form"
    IF = "if"
    NAV = "nav"
    PANEL = "panel"
    MAP = "map"


@dataclass
class RichText:
    """Rich text with annotations"""

    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    link: Optional[str] = None

    def to_notion(self) -> Dict[str, Any]:
        """Convert to Notion rich_text format"""
        return {
            "type": "text",
            "text": {
                "content": self.text,
                "link": {"url": self.link} if self.link else None,
            },
            "annotations": {
                "bold": self.bold,
                "italic": self.italic,
                "code": self.code,
                "strikethrough": False,
                "underline": False,
                "color": "default",
            },
            "plain_text": self.text,
            "href": self.link,
        }


@dataclass
class DBBinding:
    """External database binding configuration"""

    provider: str
    path: str
    namespace: str
    bind: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to YAML-compatible dict"""
        return {
            "provider": self.provider,
            "path": self.path,
            "namespace": self.namespace,
            "bind": self.bind,
        }


@dataclass
class Block:
    """Internal block representation"""

    type: BlockType
    content: str
    children: List["Block"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    rich_text: List[RichText] = field(default_factory=list)
    db_binding: Optional[DBBinding] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize block to dict"""
        return {
            "type": self.type.value,
            "content": self.content,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
            "db_binding": self.db_binding.to_dict() if self.db_binding else None,
        }


class BlockMapper:
    """Maps uDOS markdown ↔ Notion blocks"""

    def __init__(self):
        self.runtime_block_types = {"state", "set", "form", "if", "nav", "panel", "map"}

    # ============ PARSE MARKDOWN ============

    def parse_markdown(self, content: str) -> List[Block]:
        """
        Parse markdown string → Block objects

        Args:
            content: Markdown source text

        Returns:
            List of Block objects
        """
        blocks: List[Block] = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Headings
            if line.startswith("# "):
                blocks.append(
                    Block(
                        type=BlockType.HEADING_1,
                        content=line[2:].strip(),
                        rich_text=[RichText(line[2:].strip())],
                    )
                )
                i += 1
            elif line.startswith("## "):
                blocks.append(
                    Block(
                        type=BlockType.HEADING_2,
                        content=line[3:].strip(),
                        rich_text=[RichText(line[3:].strip())],
                    )
                )
                i += 1
            elif line.startswith("### "):
                blocks.append(
                    Block(
                        type=BlockType.HEADING_3,
                        content=line[4:].strip(),
                        rich_text=[RichText(line[4:].strip())],
                    )
                )
                i += 1

            # Divider
            elif line.strip() in ["---", "***", "___"]:
                blocks.append(Block(type=BlockType.DIVIDER, content=""))
                i += 1

            # Blockquote
            elif line.startswith("> "):
                blocks.append(
                    Block(
                        type=BlockType.QUOTE,
                        content=line[2:].strip(),
                        rich_text=[RichText(line[2:].strip())],
                    )
                )
                i += 1

            # Code fence (runtime block or regular code)
            elif line.startswith("```"):
                block, next_i = self._parse_code_fence(lines, i)
                if block:
                    blocks.append(block)
                i = next_i

            # Bullet list
            elif line.startswith("- "):
                items: List[str] = []
                while i < len(lines) and lines[i].startswith("- "):
                    items.append(lines[i][2:].strip())
                    i += 1
                for item in items:
                    blocks.append(
                        Block(
                            type=BlockType.BULLETED_LIST_ITEM,
                            content=item,
                            rich_text=[RichText(item)],
                        )
                    )

            # Numbered list
            elif re.match(r"^\d+\. ", line):
                items: List[str] = []
                while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                    items.append(re.sub(r"^\d+\. ", "", lines[i]).strip())
                    i += 1
                for item in items:
                    blocks.append(
                        Block(
                            type=BlockType.NUMBERED_LIST_ITEM,
                            content=item,
                            rich_text=[RichText(item)],
                        )
                    )

            # Regular paragraph
            else:
                blocks.append(
                    Block(
                        type=BlockType.PARAGRAPH,
                        content=line.strip(),
                        rich_text=[RichText(line.strip())],
                    )
                )
                i += 1

        return blocks

    def _parse_code_fence(
        self, lines: List[str], start_index: int
    ) -> Tuple[Optional[Block], int]:
        """Parse code fence (could be runtime block or regular code)"""
        if not lines[start_index].startswith("```"):
            return None, start_index + 1

        # Extract language
        lang_line = lines[start_index][3:].strip()
        lang = lang_line if lang_line else "text"

        # Find closing fence
        code_lines: List[str] = []
        i = start_index + 1
        while i < len(lines) and not lines[i].startswith("```"):
            code_lines.append(lines[i])
            i += 1

        if i < len(lines):
            i += 1

        code_content = "\n".join(code_lines).strip()

        if lang in self.runtime_block_types:
            return (
                Block(
                    type=BlockType(lang),
                    content=code_content,
                    metadata={"runtime": True, "language": "typescript"},
                    rich_text=[RichText(code_content)],
                ),
                i,
            )

        return (
            Block(
                type=BlockType.CODE,
                content=code_content,
                metadata={"language": lang},
                rich_text=[RichText(code_content)],
            ),
            i,
        )

    # ============ CONVERT TO NOTION ============

    def to_notion_api(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """
        Convert Block objects → Notion API format

        Args:
            blocks: List of Block objects

        Returns:
            List of Notion API block dicts
        """
        notion_blocks: List[Dict[str, Any]] = []
        for block in blocks:
            notion_block = self._block_to_notion(block)
            if notion_block:
                if isinstance(notion_block, list):
                    notion_blocks.extend(notion_block)
                else:
                    notion_blocks.append(notion_block)
        return notion_blocks

    def _block_to_notion(self, block: Block) -> Any:
        """Convert single Block → Notion API block"""
        notion_block: Dict[str, Any] = {
            "object": "block",
            "type": block.type.value,
        }

        if block.type == BlockType.HEADING_1:
            notion_block["heading_1"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
                "is_toggleable": False,
            }

        elif block.type == BlockType.HEADING_2:
            notion_block["heading_2"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
                "is_toggleable": False,
            }

        elif block.type == BlockType.HEADING_3:
            notion_block["heading_3"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
                "is_toggleable": False,
            }

        elif block.type == BlockType.PARAGRAPH:
            notion_block["paragraph"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
            }

        elif block.type == BlockType.QUOTE:
            notion_block["quote"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
            }

        elif block.type == BlockType.CODE:
            notion_block["code"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "language": block.metadata.get("language", "text"),
                "caption": [],
            }

        elif block.type == BlockType.BULLETED_LIST_ITEM:
            notion_block["bulleted_list_item"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
            }

        elif block.type == BlockType.NUMBERED_LIST_ITEM:
            notion_block["numbered_list_item"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "color": "default",
            }

        elif block.type == BlockType.DIVIDER:
            notion_block["divider"] = {}

        elif block.type in [BlockType.STATE, BlockType.SET, BlockType.FORM]:
            caption_text = f"[uDOS:{block.type.value.upper()}]"
            notion_block["type"] = "code"
            notion_block["code"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "language": "typescript",
                "caption": [RichText(caption_text).to_notion()],
            }

        elif block.type == BlockType.IF:
            notion_block["type"] = "heading_2"
            notion_block["heading_2"] = {
                "rich_text": [RichText(f"if {block.content}").to_notion()],
                "color": "default",
                "is_toggleable": True,
            }

        elif block.type == BlockType.NAV:
            notion_block["callout"] = {
                "rich_text": [rt.to_notion() for rt in block.rich_text],
                "icon": {"emoji": "🧭"},
                "color": "blue_background",
            }

        elif block.type == BlockType.PANEL:
            notion_block["type"] = "column_list"
            notion_block["column_list"] = {}

        elif block.type == BlockType.MAP:
            notion_block["type"] = "table"
            notion_block["table"] = {
                "table_width": 2,
                "has_column_header": True,
                "has_row_header": False,
            }

        return notion_block

    # ============ CONVERT FROM NOTION ============

    def from_notion_blocks(self, notion_blocks: List[Dict[str, Any]]) -> str:
        """
        Convert Notion blocks → markdown string

        Args:
            notion_blocks: List of Notion API block dicts
        """
        markdown_lines: List[str] = []
        for block in notion_blocks:
            block_type = block.get("type")
            content = block.get(block_type, {})

            if block_type == "heading_1":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"# {text}")
            elif block_type == "heading_2":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"## {text}")
            elif block_type == "heading_3":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"### {text}")
            elif block_type == "paragraph":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(text)
            elif block_type == "quote":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"> {text}")
            elif block_type == "code":
                language = content.get("language", "text")
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"```{language}\n{text}\n```")
            elif block_type == "bulleted_list_item":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"- {text}")
            elif block_type == "numbered_list_item":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"1. {text}")
            elif block_type == "divider":
                markdown_lines.append("---")
            elif block_type == "callout":
                text = self._rich_text_to_markdown(content.get("rich_text", []))
                markdown_lines.append(f"> {text}")
            elif block_type == "table":
                rows = content.get("children", [])
                for row in rows:
                    row_cells = []
                    for cell in row.get("table_row", {}).get("cells", []):
                        row_cells.append(self._rich_text_to_markdown(cell))
                    markdown_lines.append(" | ".join(row_cells))
            else:
                # Fallback: preserve unknown block as comment
                markdown_lines.append(f"<!-- Unsupported block: {block_type} -->")

        return "\n".join(markdown_lines)

    def _rich_text_to_markdown(self, rich_text: List[Dict[str, Any]]) -> str:
        """Convert Notion rich_text array to markdown string"""
        parts: List[str] = []
        for rt in rich_text:
            text = rt.get("plain_text", "")
            annotations = rt.get("annotations", {})

            if annotations.get("code"):
                text = f"`{text}`"
            if annotations.get("bold"):
                text = f"**{text}**"
            if annotations.get("italic"):
                text = f"*{text}*"
            if rt.get("href"):
                text = f"[{text}]({rt['href']})"

            parts.append(text)

        return "".join(parts)

    def _slugify(self, text: str) -> str:
        """Simple slugify for anchors"""
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        return text.strip("-")
