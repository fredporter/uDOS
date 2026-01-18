"""
Simplified Configuration Dashboard
===================================

New streamlined config dashboard with:
- API status list (connected/missing)
- Global config file editor (Micro integration)
- File dropdown for multi-config support

Endpoints:
  GET /api/v1/config/dashboard    - Serve simplified config dashboard
"""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from typing import Dict, Any

from wizard.services.config_framework import get_config_framework, ConfigFramework

router = APIRouter(prefix="/dashboard", tags=["config-dashboard"])


@router.get("", response_class=HTMLResponse)
async def get_config_dashboard(framework: ConfigFramework = Depends(get_config_framework)) -> str:
    """Serve the simplified configuration dashboard."""
    files = framework.get_config_files()
    files_json = ', '.join(f'"{f}"' for f in files.keys())
    default_file = ".env" if ".env" in files else (list(files.keys())[0] if files else ".env")

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><span class="emoji-mono">⚙️</span> Config Dashboard</title>
    <link rel="stylesheet" href="/static/css/global.css">
    <style>
        .dashboard-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
            background-color: rgb(15 23 42);
        }}

        .dashboard-header {{
            padding: 1.5rem;
            background: linear-gradient(135deg, rgb(30 58 138) 0%, rgb(59 130 246) 100%);
            color: white;
            border-bottom: 1px solid rgb(51 65 85);
        }}

        .dashboard-header h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.75rem;
        }}

        .dashboard-header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        .dashboard-content {{
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 1rem;
            padding: 1rem;
            overflow: hidden;
        }}

        .panel {{
            display: flex;
            flex-direction: column;
            background-color: rgb(30 41 59);
            border: 1px solid rgb(51 65 85);
            border-radius: 0.5rem;
            overflow: hidden;
        }}

        .panel-header {{
            padding: 1rem;
            background-color: rgb(51 65 85);
            color: white;
            font-weight: 600;
            border-bottom: 1px solid rgb(71 85 105);
        }}

        .panel-body {{
            flex: 1;
            overflow: auto;
            padding: 1rem;
        }}

        .api-list {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        .api-item {{
            padding: 1rem;
            background-color: rgb(15 23 42);
            border: 1px solid rgb(51 65 85);
            border-radius: 0.375rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .api-item-info {{
            flex: 1;
        }}

        .api-item-name {{
            font-weight: 600;
            color: rgb(229 231 235);
            margin-bottom: 0.25rem;
        }}

        .api-item-category {{
            font-size: 0.8rem;
            color: rgb(156 163 175);
        }}

        .status-badge {{
            padding: 0.375rem 0.75rem;
            border-radius: 0.25rem;
            font-size: 0.85rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .status-connected {{
            background-color: rgba(34, 197, 94, 0.2);
            color: rgb(134 239 172);
        }}

        .status-missing {{
            background-color: rgba(239, 68, 68, 0.2);
            color: rgb(252 165 165);
        }}

        .status-partial {{
            background-color: rgba(245, 158, 11, 0.2);
            color: rgb(254 215 170);
        }}

        .editor-panel {{
            display: flex;
            flex-direction: column;
        }}

        .editor-toolbar {{
            display: flex;
            gap: 0.5rem;
            padding: 0.75rem 1rem;
            background-color: rgb(51 65 85);
            border-bottom: 1px solid rgb(71 85 105);
            align-items: center;
        }}

        .editor-toolbar label {{
            color: white;
            font-weight: 600;
            margin-right: 0.5rem;
        }}

        .editor-toolbar select {{
            padding: 0.5rem;
            border: 1px solid rgb(71 85 105);
            border-radius: 0.25rem;
            background-color: rgb(30 41 59);
            color: rgb(229 231 235);
            flex: 1;
            max-width: 200px;
        }}

        .editor-buttons {{
            display: flex;
            gap: 0.5rem;
            margin-left: auto;
        }}

        .btn-small {{
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
            background-color: rgba(59, 130, 246, 0.8);
            color: white;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s;
        }}

        .btn-small:hover {{
            background-color: rgb(59 130 246);
        }}

        .editor-textarea {{
            flex: 1;
            padding: 1rem;
            border: none;
            background-color: rgb(15 23 42);
            color: rgb(229 231 235);
            font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
            font-size: 0.875rem;
            line-height: 1.6;
            resize: none;
            overflow: auto;
        }}

        .editor-textarea:focus {{
            outline: none;
            box-shadow: inset 0 0 10px rgba(59, 130, 246, 0.3);
        }}

        .status-bar {{
            padding: 0.75rem 1rem;
            background-color: rgb(15 23 42);
            border-top: 1px solid rgb(51 65 85);
            color: rgb(156 163 175);
            font-size: 0.85rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
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

        .message {{
            margin-top: 0.5rem;
            padding: 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.85rem;
            display: none;
        }}

        .message.show {{
            display: block;
        }}

        .message.success {{
            background-color: rgba(34, 197, 94, 0.2);
            color: rgb(134 239 172);
        }}

        .message.error {{
            background-color: rgba(239, 68, 68, 0.2);
            color: rgb(252 165 165);
        }}

        @media (max-width: 1024px) {{
            .dashboard-content {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <h1><span class="emoji-mono">⚙️</span> Configuration Dashboard</h1>
            <p>Manage APIs and edit configuration files • Framework-based design for extensibility</p>
        </div>

        <div class="dashboard-content">
            <!-- API Status Panel -->
            <div class="panel">
                <div class="panel-header"><span class="emoji-mono">📡</span> API Status</div>
                <div class="panel-body">
                    <div class="api-list" id="apiList">
                        <div class="message show success" style="margin: 0;">Loading...</div>
                    </div>
                </div>
            </div>

            <!-- Config Editor Panel -->
            <div class="panel editor-panel">
                <div class="panel-header"><span class="emoji-mono">📝</span> Config Editor</div>
                <div class="editor-toolbar">
                    <label for="fileSelect">File:</label>
                    <select id="fileSelect" onchange="loadFile()">
                        {chr(10).join(f'<option value="{f}">{f}</option>' for f in files.keys())}
                    </select>
                    <div class="editor-buttons">
                        <button class="btn-small" onclick="saveFile()" title="Save (Ctrl+S)">💾 Save</button>
                        <button class="btn-small" onclick="reloadFile()" title="Reload from disk">🔄 Reload</button>
                    </div>
                </div>
                <textarea id="editorTextarea" class="editor-textarea" spellcheck="false"></textarea>
                <div class="status-bar">
                    <span id="statusText"><span class="status-indicator status-unsaved"></span> Ready</span>
                    <span id="fileInfo">0 bytes</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = "/api/v1/config";
        const EDITOR_API = "/api/v1/config/editor";
        const textarea = document.getElementById("editorTextarea");
        const fileSelect = document.getElementById("fileSelect");
        const statusText = document.getElementById("statusText");
        const fileInfo = document.getElementById("fileInfo");
        const apiList = document.getElementById("apiList");

        let currentFile = "{default_file}";
        let originalContent = "";
        let hasChanges = false;

        // Initialize
        document.addEventListener("DOMContentLoaded", () => {{
            loadAPIs();
            fileSelect.value = currentFile;
            loadFile();
        }});

        // Load API status list
        async function loadAPIs() {{
            try {{
                const response = await fetch(`${{API_BASE}}/framework/registry`);
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();

                apiList.innerHTML = "";

                // Check if data has categories
                if (!data.categories || typeof data.categories !== 'object') {{
                    apiList.innerHTML = '<div class="message show error">No API data available</div>';
                    return;
                }}

                let totalApis = 0;
                for (const [category, info] of Object.entries(data.categories)) {{
                    if (!info.apis || !Array.isArray(info.apis)) {{
                        continue;
                    }}

                    for (const api of info.apis) {{
                        const item = document.createElement("div");
                        item.className = "api-item";

                        const statusClass = api.status === "CONNECTED" ? "status-connected" :
                                          api.status === "PARTIAL" ? "status-partial" :
                                          "status-missing";

                        const statusEmoji = api.status === "CONNECTED" ? "🟢" :
                                          api.status === "PARTIAL" ? "🟡" :
                                          "🔴";

                        item.innerHTML = `
                            <div class="api-item-info">
                                <div class="api-item-name">${{api.name}}</div>
                                <div class="api-item-category">${{api.description || category}}</div>
                            </div>
                            <span class="status-badge ${{statusClass}}">${{statusEmoji}} ${{api.status}}</span>
                        `;
                        apiList.appendChild(item);
                        totalApis++;
                    }}
                }}

                if (totalApis === 0) {{
                    apiList.innerHTML = '<div class="message show error">No APIs configured</div>';
                }}
            }} catch (error) {{
                console.error('API Error:', error);
                apiList.innerHTML = `<div class="message show error">Error loading APIs: ${{error.message}}</div>`;
            }}
        }}

        // Track changes
        textarea.addEventListener("input", () => {{
            hasChanges = textarea.value !== originalContent;
            updateStatus();
            updateFileInfo();
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
                statusText.innerHTML = '<span class="status-indicator status-unsaved"></span> Loading...';
                const response = await fetch(`${{EDITOR_API}}/read/${{currentFile}}`);
                const data = await response.json();

                originalContent = data.content;
                textarea.value = originalContent;
                hasChanges = false;
                updateStatus();
                updateFileInfo();
                statusText.innerHTML = '<span class="status-indicator status-saved"></span> Loaded';
            }} catch (error) {{
                statusText.innerHTML = `<span class="status-indicator status-error"></span> Error loading`;
            }}
        }}

        async function saveFile() {{
            if (!hasChanges) {{
                statusText.innerHTML = '<span class="status-indicator status-saved"></span> No changes';
                return;
            }}

            try {{
                statusText.innerHTML = '<span class="status-indicator status-unsaved"></span> Saving...';
                const response = await fetch(`${{EDITOR_API}}/write/${{currentFile}}`, {{
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
                statusText.innerHTML = '<span class="status-indicator status-saved"></span> ✅ Saved';
            }} catch (error) {{
                statusText.innerHTML = `<span class="status-indicator status-error"></span> Error saving`;
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
                statusText.innerHTML = '<span class="status-indicator status-unsaved"></span> Unsaved changes';
            }} else {{
                statusText.innerHTML = '<span class="status-indicator status-saved"></span> Saved';
            }}
        }}

        function updateFileInfo() {{
            const bytes = new Blob([textarea.value]).size;
            const lines = textarea.value.split('\\n').length;
            fileInfo.textContent = `${{bytes}} bytes • ${{lines}} lines`;
        }}
    </script>
</body>
</html>
"""
