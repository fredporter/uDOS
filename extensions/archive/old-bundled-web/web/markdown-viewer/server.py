#!/usr/bin/env python3
"""
uDOS Markdown Viewer
Flask web server for browsing and rendering knowledge library
Port: 9000
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
import markdown2
from thefuzz import fuzz, process
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

# Configuration
CONFIG_FILE = Path(__file__).parent / 'config.json'
if CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    config = {
        'port': 9000,
        'knowledge_root': '../../../../knowledge',
        'diagrams_root': '../../../../data/system/diagrams',
        'fuzzy_threshold': 60,
        'max_results': 50,
        'enable_emoji': True,
        'enable_syntax_highlight': True,
        'theme': 'github-dark'
    }

# Resolve paths
UDOS_ROOT = Path(__file__).parent.parent.parent.parent.parent
KNOWLEDGE_ROOT = (UDOS_ROOT / config['knowledge_root']).resolve()
DIAGRAMS_ROOT = (UDOS_ROOT / config['diagrams_root']).resolve()


def get_all_markdown_files():
    """Get all .md files from knowledge and diagrams directories."""
    files = []

    # Knowledge files
    if KNOWLEDGE_ROOT.exists():
        for md_file in KNOWLEDGE_ROOT.rglob('*.md'):
            rel_path = md_file.relative_to(KNOWLEDGE_ROOT)
            files.append({
                'path': str(md_file),
                'rel_path': str(rel_path),
                'name': md_file.name,
                'category': str(rel_path.parts[0]) if rel_path.parts else 'root',
                'type': 'knowledge'
            })

    # Diagram files
    if DIAGRAMS_ROOT.exists():
        for md_file in DIAGRAMS_ROOT.rglob('*.md'):
            rel_path = md_file.relative_to(DIAGRAMS_ROOT)
            files.append({
                'path': str(md_file),
                'rel_path': str(rel_path),
                'name': md_file.name,
                'category': str(rel_path.parts[0]) if rel_path.parts else 'root',
                'type': 'diagram'
            })

    return files


def render_markdown(md_path):
    """Render markdown file to HTML with syntax highlighting."""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Render markdown with extras
        extras = [
            'fenced-code-blocks',
            'tables',
            'break-on-newline',
            'header-ids',
            'toc',
            'strike',
            'task_list'
        ]

        html = markdown2.markdown(content, extras=extras)

        # Add syntax highlighting if enabled
        if config['enable_syntax_highlight']:
            # This would need additional processing for code blocks
            # For now, Pygments CSS is included in template
            pass

        return {
            'html': html,
            'toc': html.toc_html if hasattr(html, 'toc_html') else None,
            'metadata': html.metadata if hasattr(html, 'metadata') else {}
        }

    except Exception as e:
        return {
            'html': f'<p>Error rendering markdown: {str(e)}</p>',
            'toc': None,
            'metadata': {}
        }


def fuzzy_search_files(query, threshold=None):
    """Fuzzy search across all markdown files."""
    if threshold is None:
        threshold = config['fuzzy_threshold']

    all_files = get_all_markdown_files()

    # Search in file names and paths
    results = []
    for file_info in all_files:
        # Calculate fuzzy match scores
        name_score = fuzz.partial_ratio(query.lower(), file_info['name'].lower())
        path_score = fuzz.partial_ratio(query.lower(), file_info['rel_path'].lower())

        # Use best score
        score = max(name_score, path_score)

        if score >= threshold:
            results.append({
                **file_info,
                'score': score
            })

    # Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)

    # Limit results
    return results[:config['max_results']]


def get_category_tree():
    """Build hierarchical category tree."""
    tree = {
        'knowledge': {},
        'diagrams': {}
    }

    all_files = get_all_markdown_files()

    for file_info in all_files:
        file_type = file_info['type']
        path_parts = Path(file_info['rel_path']).parts

        # Build nested structure
        current = tree[file_type]
        for part in path_parts[:-1]:  # Exclude filename
            if part not in current:
                current[part] = {}
            current = current[part]

        # Add file to category
        if '_files' not in current:
            current['_files'] = []
        current['_files'].append(file_info)

    return tree


# Routes

@app.route('/')
def index():
    """Main viewer interface."""
    return render_template('index.html', config=config)


@app.route('/api/browse')
def api_browse():
    """List all knowledge library files."""
    try:
        files = get_all_markdown_files()
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search')
def api_search():
    """Fuzzy search across files."""
    query = request.args.get('q', '')
    threshold = int(request.args.get('threshold', config['fuzzy_threshold']))

    if not query:
        return jsonify({
            'success': False,
            'error': 'Query parameter required'
        }), 400

    try:
        results = fuzzy_search_files(query, threshold)
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/render')
def api_render():
    """Render markdown file to HTML."""
    file_path = request.args.get('path', '')

    if not file_path:
        return jsonify({
            'success': False,
            'error': 'Path parameter required'
        }), 400

    # Security: ensure path is within allowed directories
    abs_path = Path(file_path).resolve()
    if not (str(abs_path).startswith(str(KNOWLEDGE_ROOT)) or
            str(abs_path).startswith(str(DIAGRAMS_ROOT))):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403

    if not abs_path.exists():
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404

    try:
        result = render_markdown(abs_path)
        return jsonify({
            'success': True,
            'path': file_path,
            **result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/categories')
def api_categories():
    """Get category tree."""
    try:
        tree = get_category_tree()
        return jsonify({
            'success': True,
            'tree': tree
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/diagrams')
def api_diagrams():
    """List all diagrams."""
    try:
        all_files = get_all_markdown_files()
        diagrams = [f for f in all_files if f['type'] == 'diagram']
        return jsonify({
            'success': True,
            'diagrams': diagrams,
            'count': len(diagrams)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'markdown-viewer',
        'port': config['port'],
        'knowledge_root': str(KNOWLEDGE_ROOT),
        'diagrams_root': str(DIAGRAMS_ROOT)
    })


if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════╗
║  📚 uDOS Markdown Viewer                 ║
╠══════════════════════════════════════════╣
║  Port: {config['port']}                          ║
║  URL:  http://localhost:{config['port']}         ║
╠══════════════════════════════════════════╣
║  Knowledge: {str(KNOWLEDGE_ROOT)[:30]:30} ║
║  Diagrams:  {str(DIAGRAMS_ROOT)[:30]:30} ║
╚══════════════════════════════════════════╝
""")

    app.run(
        host='0.0.0.0',
        port=config['port'],
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )
