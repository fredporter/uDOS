"""
Config Editor Routes
====================

REST API for config file editing with Micro editor integration.

Endpoints:
  GET  /api/v1/config/editor/files    - List editable config files
  GET  /api/v1/config/editor/read/{filename}    - Read config file
  POST /api/v1/config/editor/write/{filename}   - Write config file
  GET  /api/v1/config/editor/ui       - Serve Micro editor UI
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List

from wizard.services.config_framework import get_config_framework, ConfigFramework

router = APIRouter(prefix="/editor", tags=["config-editor"])


class FileWriteRequest(BaseModel):
    """Request to write a config file."""
    content: str


@router.get("/files")
async def list_config_files(
    framework: ConfigFramework = Depends(get_config_framework)
) -> Dict[str, Any]:
    """List editable config files."""
    files = framework.get_config_files()
    return {
        "files": list(files.keys()),
        "default": ".env" if ".env" in files else None,
    }


@router.get("/read/{filename}")
async def read_config_file(
    filename: str,
    framework: ConfigFramework = Depends(get_config_framework)
) -> Dict[str, Any]:
    """Read a config file."""
    content = framework.read_config_file(filename)
    if content is None:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return {
        "filename": filename,
        "content": content,
    }


@router.post("/write/{filename}")
async def write_config_file(
    filename: str,
    request: FileWriteRequest,
    framework: ConfigFramework = Depends(get_config_framework)
) -> Dict[str, Any]:
    """Write a config file."""
    success = framework.write_config_file(filename, request.content)

    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to write {filename}")

    return {
        "status": "success",
        "message": f"File {filename} saved successfully",
        "filename": filename,
    }


@router.get("/ui", response_class=HTMLResponse)
async def get_editor_ui(
    framework: ConfigFramework = Depends(get_config_framework)
) -> str:
    """Serve Micro editor UI."""
    files = framework.get_config_files()
    default_file = ".env" if ".env" in files else (list(files.keys())[0] if files else None)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><span class="emoji-mono">📝</span> Config Editor</title>
    <link rel="stylesheet" href="/static/css/global.css">
    <style>
        .editor-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}

        .editor-header {{
            padding: 1rem;
            background: linear-gradient(135deg, rgb(30 58 138) 0%, rgb(59 130 246) 100%);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .editor-header h1 {{
            margin: 0;
            font-size: 1.5rem;
        }}

        .file-selector {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}

        .file-selector select {{
            padding: 0.5rem;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 0.25rem;
            background-color: rgba(0,0,0,0.2);
            color: white;
            font-size: 0.9rem;
        }}

        .editor-buttons {{
            display: flex;
            gap: 0.5rem;
        }}

        .editor-buttons button {{
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
            font-weight: 600;
            background-color: rgba(255,255,255,0.2);
            color: white;
            transition: all 0.2s;
        }}

        .editor-buttons button:hover {{
            background-color: rgba(255,255,255,0.3);
        }}

        .editor-content {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}

        .textarea-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}

        .editor-textarea {{
            flex: 1;
            padding: 1rem;
            border: none;
            background-color: rgb(30 41 59);
            color: rgb(229 231 235);
            font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            resize: none;
            overflow: auto;
        }}

        .editor-textarea:focus {{
            outline: none;
            box-shadow: inset 0 0 10px rgba(59, 130, 246, 0.3);
        }}

        .editor-status {{
            padding: 0.75rem 1rem;
            background-color: rgb(15 23 42);
            border-top: 1px solid rgb(51 65 85);
            color: rgb(156 163 175);
            font-size: 0.85rem;
        }}

        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }}

        .status-saved {{
            background-color: rgb(34 197 94);
        }}

        .status-unsaved {{
            background-color: rgb(245 158 11);
        }}

        .status-error {{
            background-color: rgb(239 68 68);
        }}
    </style>
</head>
<body>
    <div class="editor-container">
        <div class="editor-header">
            <h1><span class="emoji-mono">📝</span> Config Editor</h1>
            <div class="file-selector">
                <label for="fileSelect">File:</label>
                <select id="fileSelect" onchange="loadFile()">
                    {"".join(f'<option value="{f}">{f}</option>' for f in files.keys())}
                </select>
                <div class="editor-buttons">
                    <button onclick="saveFile()" class="btn-save" title="Save (Ctrl+S)">💾 Save</button>
                    <button onclick="reloadFile()" title="Reload from disk">🔄 Reload</button>
                </div>
            </div>
        </div>

        <div class="editor-content">
            <div class="textarea-container">
                <textarea id="editorTextarea" class="editor-textarea" spellcheck="false"></textarea>
            </div>
        </div>

        <div class="editor-status">
            <span class="status-indicator status-unsaved" id="statusDot"></span>
            <span id="statusText">Ready</span>
        </div>
    </div>

    <script>
        const API_BASE = "/api/v1/config/editor";
        const textarea = document.getElementById("editorTextarea");
        const fileSelect = document.getElementById("fileSelect");
        const statusDot = document.getElementById("statusDot");
        const statusText = document.getElementById("statusText");

        let currentFile = "{default_file}";
        let originalContent = "";
        let hasChanges = false;

        // Initialize
        document.addEventListener("DOMContentLoaded", () => {{
            fileSelect.value = currentFile;
            loadFile();
        }});

        // Track changes
        textarea.addEventListener("input", () => {{
            hasChanges = textarea.value !== originalContent;
            updateStatus();
        }});

        // Keyboard shortcuts
        document.addEventListener("keydown", (e) => {{
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {{
                e.preventDefault();
                saveFile();
            }}
        }});

        async function loadFile() {{
            currentFile = fileSelect.value;
            try {{
                statusText.textContent = "Loading...";
                const response = await fetch(`${{API_BASE}}/read/${{currentFile}}`);
                const data = await response.json();

                originalContent = data.content;
                textarea.value = originalContent;
                hasChanges = false;
                updateStatus();
                statusText.textContent = `Loaded: ${{currentFile}}`;
            }} catch (error) {{
                statusDot.className = "status-indicator status-error";
                statusText.textContent = `Error loading ${{currentFile}}: ${{error.message}}`;
            }}
        }}

        async function saveFile() {{
            if (!hasChanges) {{
                statusText.textContent = "No changes to save";
                return;
            }}

            try {{
                statusText.textContent = "Saving...";
                const response = await fetch(`${{API_BASE}}/write/${{currentFile}}`, {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{content: textarea.value}})
                }});

                if (!response.ok) {{
                    throw new Error("Save failed");
                }}

                originalContent = textarea.value;
                hasChanges = false;
                updateStatus();
                statusText.textContent = `✅ Saved: ${{currentFile}}`;
            }} catch (error) {{
                statusDot.className = "status-indicator status-error";
                statusText.textContent = `Error saving: ${{error.message}}`;
            }}
        }}

        function reloadFile() {{
            if (hasChanges && !confirm("Discard unsaved changes?")) {{
                return;
            }}
            loadFile();
        }}

        function updateStatus() {{
            if (hasChanges) {{
                statusDot.className = "status-indicator status-unsaved";
                statusText.textContent = "Unsaved changes";
            }} else {{
                statusDot.className = "status-indicator status-saved";
                statusText.textContent = "Saved";
            }}
        }}
    </script>
</body>
</html>
"""
