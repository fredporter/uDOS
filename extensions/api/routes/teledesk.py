"""
Teledesk API Routes - Knowledge Bank Teletext Browser

Provides teletext-style pages from the knowledge bank.
Pages 100-199: Index/navigation (builtin in frontend)
Pages 200-899: Knowledge bank content
Pages 900-999: System reference (builtin in frontend)
"""

from flask import Blueprint, jsonify, request
import logging
from pathlib import Path
import re

logger = logging.getLogger("api.teledesk")

teledesk_bp = Blueprint("teledesk", __name__, url_prefix="/api/teledesk")

# Knowledge bank location
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
KNOWLEDGE_PATH = PROJECT_ROOT / "knowledge"

# Page number to knowledge category mapping
PAGE_CATEGORIES = {
    (200, 299): {
        "path": "shelter",
        "category": "survival",
        "label": "Shelter & Protection",
    },
    (300, 399): {
        "path": "code",
        "category": "technical",
        "label": "Technical Reference",
    },
    (400, 499): {
        "path": "medical",
        "category": "medical",
        "label": "Medical & First Aid",
    },
    (500, 599): {
        "path": "navigation",
        "category": "navigation",
        "label": "Navigation & Maps",
    },
    (600, 699): {
        "path": "communication",
        "category": "communication",
        "label": "Communication",
    },
    (700, 799): {"path": "making", "category": "tools", "label": "Tools & Making"},
    (800, 899): {"path": "food", "category": "food", "label": "Food & Water"},
}

# Cache for discovered pages
_page_cache: dict = {}
_index_cache: dict = {}
_initialized = False


def markdown_to_teletext(
    content: str, page_num: int, title: str = "", category: str = "knowledge"
) -> dict:
    """Convert markdown content to teletext page format."""
    lines = []
    md_lines = content.split("\n")

    # Use provided title or extract from content
    if not title:
        for line in md_lines:
            if line.startswith("# "):
                title = line[2:].strip().upper()[:36]
                break
        if not title:
            title = f"PAGE {page_num}"

    # Create header
    lines.append("╔══════════════════════════════════════╗")
    lines.append(f"║ {title.center(36)} ║")
    lines.append("╚══════════════════════════════════════╝")
    lines.append("")

    in_code_block = False
    skip_first_heading = True

    for line in md_lines:
        # Skip first heading (already in header)
        if skip_first_heading and line.startswith("# "):
            skip_first_heading = False
            continue

        # Handle code blocks
        if line.startswith("```"):
            in_code_block = not in_code_block
            lines.append("  ─────────────────────────────────────")
            continue

        # Convert markdown to plain text
        converted = line
        converted = re.sub(r"^## ", "  ", converted)
        converted = re.sub(r"^### ", "   ", converted)
        converted = re.sub(r"\*\*(.*?)\*\*", r"\1", converted)
        converted = re.sub(r"\*(.*?)\*", r"\1", converted)
        converted = re.sub(r"`(.*?)`", r"\1", converted)
        converted = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", converted)
        converted = re.sub(r"^- ", "  • ", converted)
        converted = re.sub(r"^\d+\. ", "  ", converted)

        if in_code_block:
            converted = "  " + converted

        # Truncate to 40 cols
        lines.append(converted[:40])

    # Pad to fill screen
    while len(lines) < 22:
        lines.append("")

    return {
        "number": page_num,
        "title": title,
        "category": category,
        "content": lines[:22],
        "links": [{"page": 100, "label": "Index"}],
        "source": "knowledge",
    }


def parse_frontmatter(content: str) -> tuple:
    """Simple frontmatter parser - returns (metadata dict, content)."""
    if not content.startswith("---"):
        return {}, content

    try:
        end = content.index("---", 3)
        fm_text = content[3:end].strip()
        body = content[end + 3 :].strip()

        # Parse YAML-like frontmatter
        metadata = {}
        for line in fm_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip("\"'")

        return metadata, body
    except ValueError:
        return {}, content


def scan_knowledge_folder(
    folder_path: Path, category_info: dict, start_page: int
) -> list:
    """Scan a knowledge folder and create teletext pages."""
    pages = []
    page_num = start_page

    if not folder_path.exists():
        return pages

    # Find all markdown files
    md_files = sorted(folder_path.glob("**/*.md"))

    for md_file in md_files:
        if page_num >= start_page + 100:  # Max 100 pages per category
            break

        try:
            content = md_file.read_text(encoding="utf-8")
            metadata, body = parse_frontmatter(content)

            title = metadata.get(
                "title", md_file.stem.replace("-", " ").replace("_", " ").title()
            )

            page = markdown_to_teletext(
                body,
                page_num,
                title=title.upper()[:36],
                category=category_info["category"],
            )
            page["source_file"] = str(md_file.relative_to(KNOWLEDGE_PATH))
            pages.append(page)
            _page_cache[page_num] = page

            page_num += 1

        except Exception as e:
            logger.warning(f"Failed to parse {md_file}: {e}")
            continue

    return pages


def build_category_index(category_key: tuple, category_info: dict, pages: list) -> dict:
    """Build an index page for a category."""
    start_page, end_page = category_key

    lines = [
        "╔══════════════════════════════════════╗",
        f'║ {category_info["label"].upper().center(36)} ║',
        "╚══════════════════════════════════════╝",
        "",
        f"  Pages {start_page}-{end_page}",
        "  ─────────────────────────────────────",
        "",
    ]

    # Add page listings
    for page in pages[:12]:  # Max 12 entries to fit screen
        title = page["title"][:24]
        lines.append(f'  {page["number"]} ... {title}')

    if len(pages) > 12:
        lines.append(f"  ... and {len(pages) - 12} more pages")

    lines.append("")
    lines.append("  ─────────────────────────────────────")
    lines.append("  ← 100 Index")

    while len(lines) < 22:
        lines.append("")

    return {
        "number": start_page,
        "title": category_info["label"].upper(),
        "category": "index",
        "content": lines[:22],
        "links": [{"page": 100, "label": "Index"}]
        + [{"page": p["number"], "label": p["title"][:16]} for p in pages[:4]],
        "source": "generated",
    }


def init_knowledge_pages():
    """Initialize knowledge pages from the knowledge bank."""
    global _page_cache, _index_cache, _initialized

    if _initialized:
        return

    logger.info(f"[TELEDESK] Scanning knowledge bank at {KNOWLEDGE_PATH}")

    for page_range, category_info in PAGE_CATEGORIES.items():
        start_page, end_page = page_range
        folder_path = KNOWLEDGE_PATH / category_info["path"]

        pages = scan_knowledge_folder(folder_path, category_info, start_page + 1)

        if pages:
            # Build category index
            index_page = build_category_index(page_range, category_info, pages)
            _page_cache[start_page] = index_page
            _index_cache[category_info["path"]] = pages

            logger.info(
                f"[TELEDESK] Loaded {len(pages)} pages for {category_info['label']}"
            )

    _initialized = True
    logger.info(f"[TELEDESK] Initialized with {len(_page_cache)} total pages")


@teledesk_bp.route("/page/<int:page_num>", methods=["GET"])
def get_page(page_num: int):
    """Get a teletext page by number."""
    try:
        if page_num < 100 or page_num > 999:
            return jsonify({"error": "Page number must be between 100 and 999"}), 400

        # Initialize pages if needed
        init_knowledge_pages()

        # Check cache
        if page_num in _page_cache:
            return jsonify({"page": _page_cache[page_num]})

        # Page not found
        return jsonify({"page": None, "error": f"Page {page_num} not found"}), 404

    except Exception as e:
        logger.error(f"Error getting page: {e}")
        return jsonify({"error": str(e)}), 500


@teledesk_bp.route("/pages", methods=["GET"])
def list_pages():
    """List all available teletext pages."""
    try:
        init_knowledge_pages()

        pages_summary = []
        for page_num, page in sorted(_page_cache.items()):
            pages_summary.append(
                {
                    "number": page_num,
                    "title": page["title"],
                    "category": page["category"],
                }
            )

        return jsonify({"pages": pages_summary, "total": len(pages_summary)})

    except Exception as e:
        logger.error(f"Error listing pages: {e}")
        return jsonify({"error": str(e)}), 500


@teledesk_bp.route("/search", methods=["GET"])
def search_pages():
    """Search teletext pages."""
    try:
        query = request.args.get("q", "").lower()

        if not query:
            return jsonify({"error": "Search query required"}), 400

        init_knowledge_pages()

        results = []
        for page_num, page in _page_cache.items():
            # Search in title and content
            if query in page["title"].lower() or any(
                query in line.lower() for line in page["content"]
            ):
                results.append(
                    {
                        "number": page_num,
                        "title": page["title"],
                        "category": page["category"],
                    }
                )

        return jsonify(
            {"results": results[:20], "total": len(results)}  # Limit results
        )

    except Exception as e:
        logger.error(f"Error searching pages: {e}")
        return jsonify({"error": str(e)}), 500


@teledesk_bp.route("/refresh", methods=["POST"])
def refresh_pages():
    """Force refresh of knowledge pages cache."""
    global _page_cache, _index_cache, _initialized

    try:
        _page_cache = {}
        _index_cache = {}
        _initialized = False

        init_knowledge_pages()

        return jsonify(
            {"success": True, "message": f"Refreshed {len(_page_cache)} pages"}
        )

    except Exception as e:
        logger.error(f"Error refreshing pages: {e}")
        return jsonify({"error": str(e)}), 500
