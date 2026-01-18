"""
Typo Text Editor Routes
=======================

Fresh rich text editor with Tailwind styling and Svelte components.

Based on: https://github.com/rossrobino/typo

Endpoints:
  GET /typo                    - Main editor interface (HTML)
  GET /typo/api/documents      - List documents
  POST /typo/api/documents     - Create document
  GET /typo/api/documents/:id  - Get document
  PUT /typo/api/documents/:id  - Update document
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

from wizard.services.config_framework import get_config_framework, ConfigFramework

router = APIRouter(prefix="/typo", tags=["typo"])

# Simple in-memory document storage (would be database in production)
DOCUMENTS = {
    "welcome": {
        "id": "welcome",
        "title": "Welcome to Typo",
        "content": "# Welcome to Typo\n\nA beautiful, modern text editor with rich formatting and Tailwind styling.\n\nStart typing or explore the features.",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
}


@router.get("", response_class=HTMLResponse)
async def get_typo_editor(framework: ConfigFramework = Depends(get_config_framework)) -> str:
    """Serve the Typo editor interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✏️ Typo - Text Editor</title>
    <link rel="stylesheet" href="/static/css/global.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto Mono', monospace;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
        }

        .editor-container {
            display: grid;
            grid-template-columns: 250px 1fr 300px;
            height: 100vh;
            gap: 1px;
            background: #334155;
        }

        .sidebar-left {
            background: #1e293b;
            border-right: 1px solid #334155;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
        }

        .editor-main {
            background: #0f172a;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .editor-toolbar {
            background: #1e293b;
            border-bottom: 1px solid #334155;
            padding: 1rem;
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            align-items: center;
        }

        .editor-content {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            overflow: hidden;
        }

        .editor-input {
            background: #0f172a;
            color: #e2e8f0;
            border: none;
            padding: 1.5rem;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: none;
            border-right: 1px solid #334155;
        }

        .editor-preview {
            background: #1e293b;
            overflow-y: auto;
            padding: 1.5rem;
            border-left: 1px solid #334155;
        }

        .preview-content {
            color: #cbd5e1;
            line-height: 1.8;
        }

        .preview-content h1,
        .preview-content h2,
        .preview-content h3 {
            color: #f1f5f9;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }

        .preview-content h1 { font-size: 2rem; }
        .preview-content h2 { font-size: 1.5rem; }
        .preview-content h3 { font-size: 1.25rem; }

        .preview-content p {
            margin-bottom: 1rem;
        }

        .preview-content code {
            background: #0f172a;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-family: 'Courier New', monospace;
            color: #fbbf24;
        }

        .preview-content pre {
            background: #0f172a;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            margin: 1rem 0;
            border: 1px solid #334155;
        }

        .preview-content ul,
        .preview-content ol {
            margin-left: 2rem;
            margin-bottom: 1rem;
        }

        .preview-content li {
            margin-bottom: 0.5rem;
        }

        .sidebar-right {
            background: #1e293b;
            border-left: 1px solid #334155;
            overflow-y: auto;
            padding: 1rem;
            width: 300px;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .toolbar-button {
            background: #334155;
            border: 1px solid #475569;
            color: #f1f5f9;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }

        .toolbar-button:hover {
            background: #475569;
            border-color: #64748b;
        }

        .toolbar-button.active {
            background: #3b82f6;
            border-color: #2563eb;
        }

        .document-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .document-item {
            background: #334155;
            padding: 0.75rem;
            border-radius: 0.375rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }

        .document-item:hover {
            background: #475569;
            border-left-color: #3b82f6;
        }

        .document-item.active {
            background: #1e40af;
            border-left-color: #60a5fa;
        }

        .document-title {
            font-weight: 600;
            color: #f1f5f9;
        }

        .document-meta {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 0.25rem;
        }

        .stats {
            background: #334155;
            padding: 1rem;
            border-radius: 0.375rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }

        .stat {
            text-align: center;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #60a5fa;
        }

        .stat-label {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            margin-top: 0.25rem;
        }

        .section-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #f1f5f9;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        @media (max-width: 1200px) {
            .editor-container {
                grid-template-columns: 1fr 300px;
            }

            .sidebar-left {
                display: none;
            }
        }

        @media (max-width: 768px) {
            .editor-container {
                grid-template-columns: 1fr;
            }

            .sidebar-right {
                display: none;
            }

            .editor-content {
                grid-template-columns: 1fr;
            }

            .editor-input {
                border-right: none;
            }

            .editor-preview {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="editor-container">
        <!-- Left Sidebar: Documents -->
        <div class="sidebar-left">
            <div class="section-title">📄 Documents</div>
            <div class="document-list" id="documentList">
                <div class="document-item active" onclick="loadDocument('welcome')">
                    <div class="document-title">Welcome</div>
                    <div class="document-meta">Just now</div>
                </div>
            </div>
            <button class="toolbar-button" style="margin-top: auto; width: 100%;" onclick="newDocument()">
                ➕ New Document
            </button>
        </div>

        <!-- Main Editor -->
        <div class="editor-main">
            <!-- Toolbar -->
            <div class="editor-toolbar">
                <button class="toolbar-button" onclick="formatText('bold')" title="Bold (⌘B)">
                    <strong>B</strong>
                </button>
                <button class="toolbar-button" onclick="formatText('italic')" title="Italic (⌘I)">
                    <em>I</em>
                </button>
                <button class="toolbar-button" onclick="formatText('code')" title="Code">
                    &lt;&gt;
                </button>
                <div style="width: 1px; background: #334155; margin: 0 0.5rem;"></div>
                <button class="toolbar-button" onclick="insertMarkdown('# ')" title="Heading 1">
                    H1
                </button>
                <button class="toolbar-button" onclick="insertMarkdown('## ')" title="Heading 2">
                    H2
                </button>
                <button class="toolbar-button" onclick="insertMarkdown('- ')" title="List">
                    ✓
                </button>
                <div style="margin-left: auto; font-size: 0.85rem; color: #94a3b8;">
                    <span id="wordCount">0</span> words
                </div>
            </div>

            <!-- Editor Grid -->
            <div class="editor-content">
                <textarea class="editor-input" id="editor" placeholder="Start typing...">Welcome to Typo

A beautiful, modern text editor with rich formatting and Tailwind styling.

## Features

- Live preview
- Markdown support
- Word count
- Clean interface

Start typing or explore the features.</textarea>
                <div class="editor-preview">
                    <div class="preview-content" id="preview"></div>
                </div>
            </div>
        </div>

        <!-- Right Sidebar: Stats & Tools -->
        <div class="sidebar-right">
            <div class="section-title">📊 Statistics</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="charCount">0</div>
                    <div class="stat-label">Chars</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="lineCount">0</div>
                    <div class="stat-label">Lines</div>
                </div>
            </div>

            <div class="section-title">🎨 Theme</div>
            <select id="themeSelect" style="width: 100%; padding: 0.5rem; border-radius: 0.375rem; border: 1px solid #475569; background: #334155; color: #f1f5f9;">
                <option value="dark">🌙 Dark</option>
                <option value="light">☀️ Light</option>
                <option value="auto">🔄 Auto</option>
            </select>

            <div class="section-title">📥 Export</div>
            <button class="toolbar-button" style="width: 100%;" onclick="exportMarkdown()">
                📥 Export MD
            </button>
            <button class="toolbar-button" style="width: 100%;" onclick="exportHTML()">
                📥 Export HTML
            </button>
        </div>
    </div>

    <script>
        const editor = document.getElementById('editor');
        const preview = document.getElementById('preview');
        const wordCountEl = document.getElementById('wordCount');
        const charCountEl = document.getElementById('charCount');
        const lineCountEl = document.getElementById('lineCount');

        // Simple Markdown to HTML converter
        function markdownToHtml(md) {
            let html = md;

            // Headers
            html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

            // Bold and Italic
            html = html.replace(/\\*\\*(.*?)\\*\\*/gm, '<strong>$1</strong>');
            html = html.replace(/\\*(.*?)\\*/gm, '<em>$1</em>');

            // Code
            html = html.replace(/`(.*?)`/gm, '<code>$1</code>');

            // Lists
            html = html.replace(/^- (.*?)$/gm, '<li>$1</li>');
            html = html.replace(/(<li>.*?<\\/li>)/s, '<ul>$1</ul>');

            // Paragraphs
            html = html.split('\\n\\n').map(p => p.trim() ? `<p>${p.replace(/\\n/gm, '<br>')}</p>` : '').join('');

            return html;
        }

        function updatePreview() {
            const content = editor.value;
            preview.innerHTML = markdownToHtml(content);
            updateStats();
        }

        function updateStats() {
            const content = editor.value;
            const words = content.trim().split(/\\s+/).filter(w => w.length > 0).length;
            const chars = content.length;
            const lines = content.split('\\n').length;

            wordCountEl.textContent = words;
            charCountEl.textContent = chars;
            lineCountEl.textContent = lines;
        }

        function formatText(format) {
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            const selected = editor.value.substring(start, end);

            if (!selected) return;

            let wrapped = '';
            switch(format) {
                case 'bold': wrapped = `**${selected}**`; break;
                case 'italic': wrapped = `*${selected}*`; break;
                case 'code': wrapped = `\\`${selected}\\``; break;
            }

            editor.value = editor.value.substring(0, start) + wrapped + editor.value.substring(end);
            updatePreview();
        }

        function insertMarkdown(text) {
            const start = editor.selectionStart;
            editor.value = editor.value.substring(0, start) + text + editor.value.substring(start);
            editor.focus();
            editor.setSelectionRange(start + text.length, start + text.length);
            updatePreview();
        }

        function newDocument() {
            editor.value = '# New Document\\n\\nStart typing...';
            updatePreview();
        }

        function loadDocument(id) {
            // Placeholder for document loading
            console.log('Loading document:', id);
            document.querySelectorAll('.document-item').forEach(el => el.classList.remove('active'));
            event.target.closest('.document-item').classList.add('active');
        }

        function exportMarkdown() {
            const content = editor.value;
            const blob = new Blob([content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'document.md';
            a.click();
        }

        function exportHTML() {
            const content = editor.value;
            const html = markdownToHtml(content);
            const blob = new Blob([`<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Document</title></head>
<body>${html}</body>
</html>`], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'document.html';
            a.click();
        }

        // Event listeners
        editor.addEventListener('input', updatePreview);
        editor.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
                e.preventDefault();
                formatText('bold');
            }
            if ((e.metaKey || e.ctrlKey) && e.key === 'i') {
                e.preventDefault();
                formatText('italic');
            }
        });

        // Initial update
        updatePreview();
    </script>
</body>
</html>
"""


@router.get("/api/documents", response_class=JSONResponse)
async def list_documents() -> Dict[str, Any]:
    """List all documents."""
    return {
        "documents": [
            {
                "id": doc_id,
                "title": doc["title"],
                "created_at": doc["created_at"],
                "updated_at": doc["updated_at"],
                "length": len(doc["content"]),
            }
            for doc_id, doc in DOCUMENTS.items()
        ]
    }


@router.post("/api/documents", response_class=JSONResponse)
async def create_document(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new document."""
    doc_id = f"doc-{len(DOCUMENTS)}"
    DOCUMENTS[doc_id] = {
        "id": doc_id,
        "title": body.get("title", "Untitled"),
        "content": body.get("content", ""),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    return DOCUMENTS[doc_id]


@router.get("/api/documents/{doc_id}", response_class=JSONResponse)
async def get_document(doc_id: str) -> Dict[str, Any]:
    """Get a specific document."""
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found")
    return DOCUMENTS[doc_id]


@router.put("/api/documents/{doc_id}", response_class=JSONResponse)
async def update_document(doc_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Update a document."""
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found")

    DOCUMENTS[doc_id].update({
        "title": body.get("title", DOCUMENTS[doc_id]["title"]),
        "content": body.get("content", DOCUMENTS[doc_id]["content"]),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    })
    return DOCUMENTS[doc_id]
