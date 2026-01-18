"""
Export Routes Blueprint
=======================

PDF export and presentation generation endpoints.
Integrates with markdown-to-pdf and marp libraries.

[LOCAL] All processing is local - no web access required.
"""

from flask import Blueprint, jsonify, request, g, send_file, Response
from pathlib import Path
import logging
import subprocess
import tempfile
import os
import shutil
from datetime import datetime

from ..services import get_project_root

api_logger = logging.getLogger("uDOS.API")
project_root = get_project_root()

# Create blueprint
export_bp = Blueprint("export", __name__, url_prefix="/api/export")

# Library paths
MARP_PATH = project_root / "library" / "marp"
MD2PDF_PATH = project_root / "library" / "markdown-to-pdf"


# ============================================================================
# PDF EXPORT
# ============================================================================


@export_bp.route("/pdf", methods=["POST"])
def export_pdf():
    """
    Export markdown file to PDF.

    [LOCAL] Uses markdown-to-pdf library if available, falls back to basic HTML/CSS print.

    Body:
        path: str - Path to markdown file
        options: dict - Optional PDF settings (paper_size, margins, etc.)
    """
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json() or {}
        file_path = data.get("path")
        options = data.get("options", {})

        if not file_path:
            return jsonify({"success": False, "error": "No file path provided"}), 400

        path = Path(file_path)
        if not path.exists():
            return jsonify({"success": False, "error": "File not found"}), 404

        api_logger.info(f"[{correlation_id}][LOCAL] PDF export requested: {path.name}")

        # Read markdown content
        content = path.read_text(encoding="utf-8")

        # Try markdown-to-pdf if available
        md2pdf_cli = MD2PDF_PATH / "node_modules" / ".bin" / "md-to-pdf"
        if md2pdf_cli.exists():
            return _export_with_md2pdf(path, content, options, correlation_id)

        # Fallback to basic HTML generation (for print dialog)
        return _export_as_html(path, content, options, correlation_id)

    except Exception as e:
        api_logger.error(f"[{correlation_id}][LOCAL] PDF export failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def _export_with_md2pdf(path: Path, content: str, options: dict, correlation_id: str):
    """Export using markdown-to-pdf library."""
    try:
        # Create temp output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"{path.stem}.pdf"

            # Build command
            cmd = ["npx", "md-to-pdf", str(path), "--dest", str(output_path)]

            # Add options
            if options.get("paper_size"):
                cmd.extend(
                    ["--pdf-options", f'{{"format": "{options["paper_size"]}"}}']
                )

            result = subprocess.run(
                cmd, cwd=str(MD2PDF_PATH), capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0 and output_path.exists():
                api_logger.info(
                    f"[{correlation_id}][LOCAL] PDF generated: {output_path.name}"
                )
                return send_file(
                    output_path,
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=f"{path.stem}.pdf",
                )
            else:
                api_logger.warning(
                    f"[{correlation_id}] md-to-pdf failed: {result.stderr}"
                )
                return _export_as_html(path, content, options, correlation_id)

    except subprocess.TimeoutExpired:
        api_logger.error(f"[{correlation_id}] PDF generation timed out")
        return _export_as_html(path, content, options, correlation_id)


def _export_as_html(path: Path, content: str, options: dict, correlation_id: str):
    """Generate printable HTML as fallback."""
    # Simple markdown to HTML conversion
    html_content = _markdown_to_html(content)

    # Get paper size from options
    paper = options.get("paper_size", "A4")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{path.stem}</title>
    <style>
        @page {{
            size: {paper};
            margin: 2cm;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 21cm;
            margin: 0 auto;
            padding: 2cm;
        }}
        h1 {{ font-size: 24pt; margin-bottom: 1em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
        h2 {{ font-size: 18pt; margin-top: 1.5em; }}
        h3 {{ font-size: 14pt; margin-top: 1em; }}
        code {{ background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; font-family: 'JetBrains Mono', monospace; }}
        pre {{ background: #f4f4f4; padding: 1em; overflow-x: auto; border-radius: 5px; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 1em 0; padding-left: 1em; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        th, td {{ border: 1px solid #ddd; padding: 0.5em; text-align: left; }}
        th {{ background: #f4f4f4; }}
        @media print {{
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    api_logger.info(
        f"[{correlation_id}][LOCAL] Generated printable HTML for: {path.name}"
    )

    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f'inline; filename="{path.stem}.html"'},
    )


# ============================================================================
# PRESENTATION / SLIDES
# ============================================================================


@export_bp.route("/slides", methods=["POST"])
def export_slides():
    """
    Generate presentation slides from markdown.

    [LOCAL] Uses Marp if available, falls back to remark-style HTML slides.

    Body:
        path: str - Path to markdown file
        options: dict - Slide options (theme, transition, etc.)
    """
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json() or {}
        file_path = data.get("path")
        options = data.get("options", {})

        if not file_path:
            return jsonify({"success": False, "error": "No file path provided"}), 400

        path = Path(file_path)
        if not path.exists():
            return jsonify({"success": False, "error": "File not found"}), 404

        api_logger.info(
            f"[{correlation_id}][LOCAL] Slides export requested: {path.name}"
        )

        # Read markdown content
        content = path.read_text(encoding="utf-8")

        # Check if content has Marp frontmatter or slide separators
        has_marp = content.startswith("---") and "marp: true" in content[:500]
        has_separators = "\n---\n" in content or "\n***\n" in content

        # Try Marp if available and content has Marp markers
        marp_cli = MARP_PATH / "node_modules" / ".bin" / "marp"
        if marp_cli.exists() and has_marp:
            return _export_with_marp(path, content, options, correlation_id)

        # Use remark-style slides
        return _export_remark_slides(path, content, options, correlation_id)

    except Exception as e:
        api_logger.error(f"[{correlation_id}][LOCAL] Slides export failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def _export_with_marp(path: Path, content: str, options: dict, correlation_id: str):
    """Export using Marp CLI."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"{path.stem}.html"

            cmd = [
                "npx",
                "@marp-team/marp-cli",
                str(path),
                "-o",
                str(output_path),
                "--html",
            ]

            # Add theme if specified
            if options.get("theme"):
                cmd.extend(["--theme", options["theme"]])

            result = subprocess.run(
                cmd, cwd=str(MARP_PATH), capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0 and output_path.exists():
                html = output_path.read_text()
                api_logger.info(f"[{correlation_id}][LOCAL] Marp slides generated")
                return Response(html, mimetype="text/html")
            else:
                api_logger.warning(
                    f"[{correlation_id}] Marp failed, using remark fallback"
                )
                return _export_remark_slides(path, content, options, correlation_id)

    except subprocess.TimeoutExpired:
        return _export_remark_slides(path, content, options, correlation_id)


def _export_remark_slides(path: Path, content: str, options: dict, correlation_id: str):
    """Generate remark.js-style presentation."""
    # Escape content for JavaScript
    escaped_content = (
        content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    )

    theme = options.get("theme", "default")
    ratio = options.get("ratio", "16:9")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{path.stem} - Presentation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        
        .remark-slide-content {{
            font-size: 24px;
            padding: 1em 2em;
        }}
        
        .remark-slide-content h1 {{
            font-size: 2.5em;
            margin-bottom: 0.5em;
            color: #1a1a1a;
        }}
        
        .remark-slide-content h2 {{
            font-size: 1.8em;
            color: #333;
        }}
        
        .remark-slide-content code {{
            background: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        
        .remark-slide-content pre code {{
            display: block;
            padding: 1em;
            overflow-x: auto;
        }}
        
        .remark-slide-number {{
            font-size: 12px;
            opacity: 0.6;
        }}
        
        /* System 7 theme */
        .theme-system7 .remark-slide-content {{
            background: linear-gradient(180deg, #c0c0c0 0%, #d0d0d0 100%);
            border: 2px solid #000;
        }}
        
        .theme-system7 .remark-slide-content h1 {{
            font-family: 'Chicago', 'ChicagoFLF', monospace;
            text-shadow: 1px 1px 0 #fff;
        }}
        
        /* Dark theme */
        .theme-dark .remark-slide-content {{
            background: #1a1a1a;
            color: #f0f0f0;
        }}
        
        .theme-dark .remark-slide-content h1,
        .theme-dark .remark-slide-content h2 {{
            color: #fff;
        }}
    </style>
</head>
<body class="theme-{theme}">
    <textarea id="source">
{content}
    </textarea>
    <script src="https://remarkjs.com/downloads/remark-latest.min.js"></script>
    <script>
        var slideshow = remark.create({{
            ratio: '{ratio}',
            highlightStyle: 'monokai',
            highlightLines: true,
            countIncrementalSlides: false
        }});
    </script>
</body>
</html>"""

    api_logger.info(
        f"[{correlation_id}][LOCAL] Remark slides generated for: {path.name}"
    )

    return Response(html, mimetype="text/html")


# ============================================================================
# PRINT PREVIEW
# ============================================================================


@export_bp.route("/preview", methods=["POST"])
def print_preview():
    """
    Generate print preview HTML for a markdown file.

    Body:
        path: str - Path to markdown file
        content: str - Optional content override
        format: str - 'a4' or 'letter'
    """
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        data = request.get_json() or {}
        file_path = data.get("path")
        content = data.get("content")
        paper_format = data.get("format", "a4")

        # Get content from file or use provided
        if content is None:
            if not file_path:
                return (
                    jsonify({"success": False, "error": "No path or content provided"}),
                    400,
                )
            path = Path(file_path)
            if not path.exists():
                return jsonify({"success": False, "error": "File not found"}), 404
            content = path.read_text(encoding="utf-8")
            title = path.stem
        else:
            title = "Preview"

        html_content = _markdown_to_html(content)

        # A4: 210mm x 297mm, Letter: 8.5in x 11in
        page_width = "210mm" if paper_format == "a4" else "8.5in"
        page_height = "297mm" if paper_format == "a4" else "11in"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 20px;
            background: #808080;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        .page {{
            width: {page_width};
            min-height: {page_height};
            margin: 0 auto 20px auto;
            padding: 25mm;
            background: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .page-content {{
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a1a;
        }}
        h1 {{ font-size: 20pt; margin-top: 0; }}
        h2 {{ font-size: 16pt; }}
        h3 {{ font-size: 13pt; }}
        code {{ background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 1em; overflow-x: auto; }}
        @media print {{
            body {{ background: none; padding: 0; }}
            .page {{ box-shadow: none; margin: 0; }}
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="page-content">
            {html_content}
        </div>
    </div>
</body>
</html>"""

        api_logger.debug(f"[{correlation_id}][LOCAL] Print preview generated")
        return Response(html, mimetype="text/html")

    except Exception as e:
        api_logger.error(f"[{correlation_id}][LOCAL] Print preview failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# HELPERS
# ============================================================================


def _markdown_to_html(content: str) -> str:
    """Simple markdown to HTML conversion without external dependencies."""
    import re

    # Code blocks (must be first)
    content = re.sub(
        r"```(\w+)?\n(.*?)```",
        lambda m: f'<pre><code class="language-{m.group(1) or ""}">{_escape_html(m.group(2))}</code></pre>',
        content,
        flags=re.DOTALL,
    )

    # Headings
    content = re.sub(r"^##### (.+)$", r"<h5>\1</h5>", content, flags=re.MULTILINE)
    content = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", content, flags=re.MULTILINE)
    content = re.sub(r"^### (.+)$", r"<h3>\1</h3>", content, flags=re.MULTILINE)
    content = re.sub(r"^## (.+)$", r"<h2>\1</h2>", content, flags=re.MULTILINE)
    content = re.sub(r"^# (.+)$", r"<h1>\1</h1>", content, flags=re.MULTILINE)

    # Bold and italic
    content = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", content)
    content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
    content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", content)
    content = re.sub(r"__(.+?)__", r"<strong>\1</strong>", content)
    content = re.sub(r"_(.+?)_", r"<em>\1</em>", content)

    # Inline code
    content = re.sub(r"`([^`]+)`", r"<code>\1</code>", content)

    # Links and images
    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', content)
    content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', content)

    # Blockquotes
    content = re.sub(
        r"^> (.+)$", r"<blockquote>\1</blockquote>", content, flags=re.MULTILINE
    )

    # Horizontal rules
    content = re.sub(r"^---+$", r"<hr>", content, flags=re.MULTILINE)
    content = re.sub(r"^\*\*\*+$", r"<hr>", content, flags=re.MULTILINE)

    # Lists (simple)
    content = re.sub(r"^- (.+)$", r"<li>\1</li>", content, flags=re.MULTILINE)
    content = re.sub(r"^(\d+)\. (.+)$", r"<li>\2</li>", content, flags=re.MULTILINE)

    # Wrap consecutive list items
    content = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f"<ul>{m.group(0)}</ul>", content)

    # Paragraphs (for remaining text blocks)
    lines = content.split("\n")
    result = []
    in_para = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_para:
                result.append("</p>")
                in_para = False
            result.append("")
        elif stripped.startswith("<"):
            if in_para:
                result.append("</p>")
                in_para = False
            result.append(line)
        else:
            if not in_para:
                result.append("<p>")
                in_para = True
            result.append(line)

    if in_para:
        result.append("</p>")

    return "\n".join(result)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
