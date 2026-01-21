"""
Knowledge Routes Blueprint
===========================

Knowledge bank endpoints: stats, search, view, add, tiers.
~5 endpoints for knowledge system.
"""

from flask import Blueprint, jsonify, request, g
import logging

from ..services import execute_command, init_udos_systems

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")


# ============================================================================
# KNOWLEDGE BANK ENDPOINTS
# ============================================================================


@knowledge_bp.route("/stats")
def api_knowledge_stats():
    """Get tier statistics."""
    result = execute_command("[KNOWLEDGE|STATS]")
    return jsonify(result)


@knowledge_bp.route("/search")
def api_knowledge_search():
    """Search knowledge across tiers."""
    query = request.args.get("query", "*")
    tier = request.args.get("tier")
    tags = request.args.get("tags")

    cmd_parts = ["SEARCH", query]
    if tier:
        cmd_parts.extend(["--tier", tier])
    if tags:
        cmd_parts.extend(["--tags", tags])

    command = f"[KNOWLEDGE|{' '.join(cmd_parts)}]"
    result = execute_command(command)
    return jsonify(result)


@knowledge_bp.route("/view/<knowledge_id>")
def api_knowledge_view(knowledge_id):
    """View specific knowledge item."""
    result = execute_command(f"[KNOWLEDGE|VIEW {knowledge_id}]")
    return jsonify(result)


@knowledge_bp.route("/add", methods=["POST"])
def api_knowledge_add():
    """Add new knowledge item."""
    data = request.json
    tier = data.get("tier", 0)
    knowledge_type = data.get("type", "note")
    title = data.get("title", "")
    content = data.get("content", "")
    tags = data.get("tags", [])

    command = f"[KNOWLEDGE|ADD {tier} {knowledge_type} {title}]"
    # Note: This is simplified - full implementation would need
    # multi-line content handling via API
    result = execute_command(command)
    return jsonify(result)


@knowledge_bp.route("/tiers")
def api_knowledge_tiers():
    """List tier descriptions."""
    result = execute_command("[KNOWLEDGE|TIERS]")
    return jsonify(result)


# ============================================================================
# TELEDESK ENDPOINTS
# ============================================================================

# Page number mappings to knowledge categories
TELEDESK_MAPPINGS = {
    # 200-299: Survival
    200: "survival",
    201: "survival/shelter",
    210: "survival/water",
    220: "survival/fire",
    230: "survival/food",
    240: "survival/navigation",
    # 300-399: Technical
    300: "tech",
    310: "tech/hardware",
    320: "tech/software",
    330: "tech/networking",
    # 400-499: Medical
    400: "medical",
    410: "medical/first-aid",
    420: "medical/emergency",
    # 500-599: Navigation
    500: "navigation",
    # 600-699: Communication
    600: "communication",
    # 700-799: Tools
    700: "tools",
    710: "tools/making",
    # 800-899: Food/Water
    800: "food",
    810: "water",
}


@knowledge_bp.route("/teledesk/page/<int:page_num>")
def api_teledesk_page(page_num: int):
    """
    Get a teletext-style page from knowledge bank.

    Page ranges:
    - 100-199: Index/Getting Started (built-in)
    - 200-299: Survival Knowledge
    - 300-399: Technical Reference
    - 400-499: Medical & First Aid
    - 500-599: Navigation & Maps
    - 600-699: Communication
    - 700-799: Tools & Making
    - 800-899: Food & Water
    - 900-999: System Commands (built-in)
    """
    import os
    from pathlib import Path

    # Built-in pages handled client-side (100-199, 900-999)
    if page_num < 200 or page_num >= 900:
        return jsonify({"error": "Built-in page", "page": None}), 404

    # Find matching knowledge category
    category = None
    for base_page, cat in sorted(TELEDESK_MAPPINGS.items(), reverse=True):
        if page_num >= base_page:
            category = cat
            break

    if not category:
        return jsonify({"error": "Unknown page range", "page": None}), 404

    # Try to load from knowledge bank
    knowledge_root = Path(os.environ.get("UDOS_ROOT", ".")) / "knowledge"
    category_path = knowledge_root / category

    if not category_path.exists():
        return jsonify({"error": "Category not found", "page": None}), 404

    # Calculate sub-page index within category
    base_page = next(
        bp for bp in sorted(TELEDESK_MAPPINGS.keys(), reverse=True) if page_num >= bp
    )
    page_index = page_num - base_page

    # Find markdown files in category
    md_files = sorted(category_path.glob("*.md"))
    if not md_files:
        # Try README.md in subdirectories
        for subdir in category_path.iterdir():
            if subdir.is_dir():
                readme = subdir / "README.md"
                if readme.exists():
                    md_files.append(readme)
        md_files = sorted(md_files)

    if page_index >= len(md_files):
        return jsonify({"error": "Page index out of range", "page": None}), 404

    # Load and convert markdown to teletext
    md_file = md_files[page_index]
    content = md_file.read_text(encoding="utf-8")

    page = markdown_to_teletext(content, page_num, category)
    return jsonify({"page": page})


def markdown_to_teletext(markdown: str, page_num: int, category: str) -> dict:
    """Convert markdown to teletext page format."""
    lines = []
    md_lines = markdown.split("\n")

    title = f"PAGE {page_num}"
    links = [{"page": 100, "label": "Index"}]

    for line in md_lines:
        # Extract title from first heading
        if line.startswith("# ") and not lines:
            title = line[2:].upper()[:36]
            lines.append("╔══════════════════════════════════════╗")
            lines.append(f"║ {title:<36} ║")
            lines.append("╚══════════════════════════════════════╝")
            lines.append("")
            continue

        # Skip metadata blocks
        if line.strip() == "---":
            continue

        # Convert markdown elements
        converted = line
        if line.startswith("## "):
            converted = "  " + line[3:].upper()
            lines.append("  ─────────────────────────────────────")
        elif line.startswith("### "):
            converted = "   " + line[4:]
        elif line.startswith("- "):
            converted = "  • " + line[2:]
        elif line.startswith("```"):
            lines.append("  ─────────────────────────────────────")
            continue
        else:
            # Remove markdown formatting
            converted = line.replace("**", "").replace("*", "").replace("`", "")

        # Truncate to 40 chars
        lines.append(converted[:40])

    # Pad to 23 lines
    while len(lines) < 23:
        lines.append("")

    return {
        "number": page_num,
        "title": title,
        "category": category.split("/")[0] if "/" in category else category,
        "content": lines[:23],
        "links": links,
        "source": "knowledge",
    }
