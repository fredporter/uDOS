"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.runScript = runScript;
exports.runInSandbox = runInSandbox;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
// Active sandbox instances
const sandboxes = new Map();
async function runScript(context) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'upy') {
        vscode.window.showErrorMessage('No .uPY file active');
        return;
    }
    const config = vscode.workspace.getConfiguration('udos');
    const apiUrl = config.get('apiUrl', 'http://localhost:5001');
    const showExecutionTime = config.get('showExecutionTime', true);
    const script = editor.document.getText();
    const scriptName = path.basename(editor.document.fileName);
    // Create debug panel
    const panel = vscode.window.createWebviewPanel('udosDebug', `uDOS: ${scriptName}`, vscode.ViewColumn.Two, { enableScripts: true });
    panel.webview.html = getDebugPanelHTML('Executing script...', scriptName);
    try {
        // Execute via API
        const startTime = Date.now();
        const response = await executeScript(apiUrl, script, false);
        const executionTime = (Date.now() - startTime) / 1000;
        // Update panel with results
        panel.webview.html = getDebugPanelHTML(response.output, scriptName, response.success, executionTime, response.errors, response.variables);
        if (response.success) {
            vscode.window.showInformationMessage(`✅ Script executed successfully${showExecutionTime ? ` (${executionTime.toFixed(2)}s)` : ''}`);
        }
        else {
            vscode.window.showErrorMessage(`❌ Script failed: ${response.errors[0] || 'Unknown error'}`);
        }
    }
    catch (error) {
        panel.webview.html = getDebugPanelHTML('', scriptName, false, 0, [error.message], {});
        vscode.window.showErrorMessage(`Failed to execute script: ${error.message}`);
    }
}
async function runInSandbox(context) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'upy') {
        vscode.window.showErrorMessage('No .uPY file active');
        return;
    }
    const config = vscode.workspace.getConfiguration('udos');
    const apiUrl = config.get('apiUrl', 'http://localhost:5001');
    const autoCleanup = config.get('sandboxAutoCleanup', true);
    const script = editor.document.getText();
    const scriptName = path.basename(editor.document.fileName);
    // Create sandbox instance
    const sandboxId = `sandbox_${Date.now()}`;
    const sandbox = {
        id: sandboxId,
        port: 5001, // Use same API for now, could spawn separate instance
        workspace: `/tmp/udos-sandbox-${Date.now()}`,
        created: new Date()
    };
    sandboxes.set(sandboxId, sandbox);
    // Create debug panel
    const panel = vscode.window.createWebviewPanel('udosSandbox', `🧪 Sandbox: ${scriptName}`, vscode.ViewColumn.Two, { enableScripts: true });
    panel.webview.html = getSandboxPanelHTML('Initializing sandbox...', scriptName, sandboxId);
    try {
        // Execute in sandbox (isolated flag)
        const startTime = Date.now();
        const response = await executeScript(apiUrl, script, true);
        const executionTime = (Date.now() - startTime) / 1000;
        // Update panel with results
        panel.webview.html = getSandboxPanelHTML(response.output, scriptName, sandboxId, response.success, executionTime, response.errors, response.variables, sandbox.workspace);
        if (response.success) {
            vscode.window.showInformationMessage(`🧪 Sandbox execution successful (${executionTime.toFixed(2)}s)`);
        }
        else {
            vscode.window.showWarningMessage(`⚠️ Sandbox execution failed: ${response.errors[0]}`);
        }
        // Cleanup on panel close
        if (autoCleanup) {
            panel.onDidDispose(() => {
                cleanupSandbox(sandboxId);
            });
        }
    }
    catch (error) {
        panel.webview.html = getSandboxPanelHTML('', scriptName, sandboxId, false, 0, [error.message], {}, sandbox.workspace);
        vscode.window.showErrorMessage(`Sandbox failed: ${error.message}`);
        if (autoCleanup) {
            cleanupSandbox(sandboxId);
        }
    }
}
async function executeScript(apiUrl, script, isolated) {
    try {
        // Try to use node-fetch if available, otherwise use fetch API
        const fetch = globalThis.fetch || require('node-fetch');
        const response = await fetch(`${apiUrl}/api/workflows/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                script: script,
                isolated: isolated,
                return_variables: true
            })
        });
        if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        return {
            success: data.success ?? true,
            output: data.output || data.result || '',
            errors: data.errors || [],
            variables: data.variables || {},
            execution_time: data.execution_time || 0,
            timestamp: new Date().toISOString()
        };
    }
    catch (error) {
        // If API is not available, return mock result
        if (error.code === 'ECONNREFUSED' || error.message.includes('fetch')) {
            return {
                success: false,
                output: '',
                errors: [`API server not running at ${apiUrl}. Start with: POKE API start`],
                variables: {},
                execution_time: 0,
                timestamp: new Date().toISOString()
            };
        }
        throw error;
    }
}
function cleanupSandbox(sandboxId) {
    const sandbox = sandboxes.get(sandboxId);
    if (sandbox) {
        // TODO: Call API to cleanup sandbox workspace
        sandboxes.delete(sandboxId);
        console.log(`Cleaned up sandbox: ${sandboxId}`);
    }
}
function getDebugPanelHTML(output, scriptName, success = true, executionTime = 0, errors = [], variables = {}) {
    const statusIcon = success ? '✅' : '❌';
    const statusText = success ? 'Success' : 'Failed';
    const statusColor = success ? '#4ade80' : '#f87171';
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #3e3e42;
        }
        .header h2 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        .status {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            background: ${statusColor}22;
            color: ${statusColor};
            border: 1px solid ${statusColor};
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .info-item {
            background: #252526;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #3e3e42;
        }
        .info-label {
            font-size: 11px;
            text-transform: uppercase;
            color: #858585;
            margin-bottom: 4px;
        }
        .info-value {
            font-size: 14px;
            font-weight: 500;
            color: #d4d4d4;
        }
        .section {
            margin-bottom: 24px;
        }
        .section h3 {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 12px 0;
            color: #d4d4d4;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .output-box {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }
        .error-box {
            background: #f8717122;
            border: 1px solid #f87171;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .error-item {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            color: #fca5a5;
            margin-bottom: 6px;
        }
        .error-item:last-child {
            margin-bottom: 0;
        }
        .var-table {
            width: 100%;
            border-collapse: collapse;
        }
        .var-table th {
            text-align: left;
            padding: 8px 12px;
            background: #252526;
            border: 1px solid #3e3e42;
            font-size: 12px;
            font-weight: 600;
            color: #d4d4d4;
        }
        .var-table td {
            padding: 8px 12px;
            border: 1px solid #3e3e42;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
        }
        .var-table td:first-child {
            color: #4ade80;
            font-weight: 500;
        }
        .var-table tr:hover {
            background: #252526;
        }
        .empty-message {
            color: #858585;
            font-style: italic;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h2>🚀 uDOS Debug Console</h2>
        <div class="status">${statusIcon} ${statusText}</div>
    </div>

    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Script</div>
            <div class="info-value">${scriptName}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Execution Time</div>
            <div class="info-value">${executionTime.toFixed(3)}s</div>
        </div>
        <div class="info-item">
            <div class="info-label">Timestamp</div>
            <div class="info-value">${new Date().toLocaleTimeString()}</div>
        </div>
    </div>

    ${errors.length > 0 ? `
    <div class="section">
        <h3>⚠️ Errors (${errors.length})</h3>
        <div class="error-box">
            ${errors.map(err => `<div class="error-item">❌ ${escapeHtml(err)}</div>`).join('')}
        </div>
    </div>
    ` : ''}

    <div class="section">
        <h3>📄 Output</h3>
        <div class="output-box">${output || '<span class="empty-message">No output</span>'}</div>
    </div>

    ${Object.keys(variables).length > 0 ? `
    <div class="section">
        <h3>🔢 Variables (${Object.keys(variables).length})</h3>
        <table class="var-table">
            <thead>
                <tr>
                    <th>Variable</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(variables).map(([key, value]) => `
                <tr>
                    <td>$${key}</td>
                    <td>${escapeHtml(JSON.stringify(value, null, 2))}</td>
                </tr>
                `).join('')}
            </tbody>
        </table>
    </div>
    ` : ''}
</body>
</html>`;
}
function getSandboxPanelHTML(output, scriptName, sandboxId, success = true, executionTime = 0, errors = [], variables = {}, workspace = '') {
    const statusIcon = success ? '✅' : '❌';
    const statusText = success ? 'Success' : 'Failed';
    const statusColor = success ? '#4ade80' : '#f87171';
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #3e3e42;
        }
        .header h2 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        .status {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            background: ${statusColor}22;
            color: ${statusColor};
            border: 1px solid ${statusColor};
        }
        .sandbox-badge {
            display: inline-block;
            padding: 4px 10px;
            background: #3b82f622;
            color: #60a5fa;
            border: 1px solid #3b82f6;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-left: 8px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .info-item {
            background: #252526;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #3e3e42;
        }
        .info-label {
            font-size: 11px;
            text-transform: uppercase;
            color: #858585;
            margin-bottom: 4px;
        }
        .info-value {
            font-size: 14px;
            font-weight: 500;
            color: #d4d4d4;
            word-break: break-all;
        }
        .section {
            margin-bottom: 24px;
        }
        .section h3 {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 12px 0;
            color: #d4d4d4;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .output-box {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }
        .error-box {
            background: #f8717122;
            border: 1px solid #f87171;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .error-item {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            color: #fca5a5;
            margin-bottom: 6px;
        }
        .empty-message {
            color: #858585;
            font-style: italic;
            font-size: 13px;
        }
        .note {
            background: #60a5fa22;
            border: 1px solid #60a5fa;
            border-radius: 6px;
            padding: 12px;
            font-size: 13px;
            color: #93c5fd;
            margin-top: 16px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2>🧪 Sandbox Console <span class="sandbox-badge">ISOLATED</span></h2>
        </div>
        <div class="status">${statusIcon} ${statusText}</div>
    </div>

    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Script</div>
            <div class="info-value">${scriptName}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Sandbox ID</div>
            <div class="info-value">${sandboxId}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Execution Time</div>
            <div class="info-value">${executionTime.toFixed(3)}s</div>
        </div>
        <div class="info-item">
            <div class="info-label">Workspace</div>
            <div class="info-value">${workspace || 'Isolated'}</div>
        </div>
    </div>

    <div class="note">
        🛡️ <strong>Sandbox Mode:</strong> This script executed in an isolated environment. No changes affect production data.
    </div>

    ${errors.length > 0 ? `
    <div class="section">
        <h3>⚠️ Errors (${errors.length})</h3>
        <div class="error-box">
            ${errors.map(err => `<div class="error-item">❌ ${escapeHtml(err)}</div>`).join('')}
        </div>
    </div>
    ` : ''}

    <div class="section">
        <h3>📄 Output</h3>
        <div class="output-box">${output || '<span class="empty-message">No output</span>'}</div>
    </div>
</body>
</html>`;
}
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
//# sourceMappingURL=executor.js.map