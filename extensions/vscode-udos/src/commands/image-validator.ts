import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface SVGReport {
    valid: boolean;
    dimensions?: { width: string; height: string };
    viewBox?: string;
    elementCount: number;
    issues: string[];
    warnings: string[];
}

interface ASCIIReport {
    valid: boolean;
    dimensions: { width: number; height: number };
    issues: string[];
    hasNonASCII: boolean;
    hasTabs: boolean;
}

interface TeletextReport {
    valid: boolean;
    pageNumber?: string;
    lineCount: number;
    colorCodes: number;
    issues: string[];
}

export async function previewSVG(uri: vscode.Uri): Promise<void> {
    try {
        const svgContent = fs.readFileSync(uri.fsPath, 'utf-8');
        const report = validateSVG(svgContent);

        const panel = vscode.window.createWebviewPanel(
            'svgPreview',
            `SVG: ${path.basename(uri.fsPath)}`,
            vscode.ViewColumn.Two,
            { enableScripts: true }
        );

        panel.webview.html = getSVGPreviewHTML(svgContent, path.basename(uri.fsPath), report);

        if (!report.valid) {
            vscode.window.showWarningMessage(`SVG has ${report.issues.length} validation issues`);
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to preview SVG: ${error.message}`);
    }
}

export async function previewASCII(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file active');
        return;
    }

    const selection = editor.selection;
    const text = editor.document.getText(selection.isEmpty ? undefined : selection);

    if (!text) {
        vscode.window.showWarningMessage('No text selected');
        return;
    }

    const report = validateASCII(text);

    const panel = vscode.window.createWebviewPanel(
        'asciiPreview',
        'ASCII Art Preview',
        vscode.ViewColumn.Two,
        { enableScripts: true }
    );

    panel.webview.html = getASCIIPreviewHTML(text, report);

    if (!report.valid) {
        vscode.window.showWarningMessage(`ASCII art has ${report.issues.length} validation issues`);
    }
}

export async function validateTeletext(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file active');
        return;
    }

    const content = editor.document.getText();
    const report = validateTeletextFormat(content);

    const panel = vscode.window.createWebviewPanel(
        'teletextValidation',
        `Teletext: ${path.basename(editor.document.fileName)}`,
        vscode.ViewColumn.Two,
        { enableScripts: true }
    );

    panel.webview.html = getTeletextValidationHTML(content, report);

    if (report.valid) {
        vscode.window.showInformationMessage('✅ Teletext format valid');
    } else {
        vscode.window.showWarningMessage(`⚠️ Teletext has ${report.issues.length} format issues`);
    }
}

function validateSVG(content: string): SVGReport {
    const issues: string[] = [];
    const warnings: string[] = [];
    let elementCount = 0;

    // Check for SVG root element
    if (!content.includes('<svg')) {
        issues.push('No <svg> root element found');
        return { valid: false, elementCount: 0, issues, warnings };
    }

    // Extract dimensions
    const widthMatch = content.match(/width=["']([^"']+)["']/);
    const heightMatch = content.match(/height=["']([^"']+)["']/);
    const viewBoxMatch = content.match(/viewBox=["']([^"']+)["']/);

    const dimensions = widthMatch && heightMatch ? {
        width: widthMatch[1],
        height: heightMatch[1]
    } : undefined;

    const viewBox = viewBoxMatch ? viewBoxMatch[1] : undefined;

    if (!dimensions) {
        warnings.push('Missing width/height attributes');
    }

    if (!viewBox) {
        warnings.push('Missing viewBox (affects scaling)');
    }

    // Count elements (rough estimate)
    elementCount = (content.match(/<(\w+)/g) || []).length;

    if (elementCount > 500) {
        warnings.push(`High element count (${elementCount}) - may be slow to render`);
    }

    // Check for text elements with small font sizes
    const textMatches = content.matchAll(/<text[^>]*font-size=["'](\d+)["']/g);
    for (const match of textMatches) {
        const fontSize = parseInt(match[1]);
        if (fontSize < 12) {
            warnings.push(`Small font size (${fontSize}px) - readability concern`);
        }
    }

    // Check for common issues
    if (content.includes('NaN') || content.includes('undefined')) {
        issues.push('Contains NaN or undefined values');
    }

    return {
        valid: issues.length === 0,
        dimensions,
        viewBox,
        elementCount,
        issues,
        warnings
    };
}

function validateASCII(content: string): ASCIIReport {
    const issues: string[] = [];
    const lines = content.split('\n');
    
    // Check width consistency
    const widths = lines.map(l => l.length);
    const maxWidth = Math.max(...widths);
    const minWidth = Math.min(...widths);

    if (maxWidth - minWidth > 2) {
        issues.push(`Inconsistent line widths (${minWidth}-${maxWidth} chars)`);
    }

    // Check for non-ASCII characters
    let hasNonASCII = false;
    for (let i = 0; i < lines.length; i++) {
        for (let j = 0; j < lines[i].length; j++) {
            const code = lines[i].charCodeAt(j);
            if (code > 127) {
                hasNonASCII = true;
                issues.push(`Non-ASCII character at line ${i + 1}, col ${j + 1}: '${lines[i][j]}' (code ${code})`);
                break; // Only report first occurrence per line
            }
        }
    }

    // Check for tabs
    const hasTabs = content.includes('\t');
    if (hasTabs) {
        issues.push('Contains tabs - use spaces for consistent rendering');
    }

    // Check for trailing spaces
    const linesWithTrailingSpaces = lines.filter(l => l.endsWith(' ')).length;
    if (linesWithTrailingSpaces > lines.length * 0.1) {
        issues.push(`Many lines have trailing spaces (${linesWithTrailingSpaces}/${lines.length})`);
    }

    return {
        valid: issues.length === 0,
        dimensions: { width: maxWidth, height: lines.length },
        issues,
        hasNonASCII,
        hasTabs
    };
}

function validateTeletextFormat(content: string): TeletextReport {
    const issues: string[] = [];
    const lines = content.split('\n');

    // Teletext pages are 24 lines × 40 columns
    const expectedLines = 24;
    const expectedWidth = 40;

    if (lines.length !== expectedLines) {
        issues.push(`Wrong line count: ${lines.length} (expected ${expectedLines})`);
    }

    for (let i = 0; i < lines.length; i++) {
        if (lines[i].length !== expectedWidth) {
            issues.push(`Line ${i + 1} wrong width: ${lines[i].length} chars (expected ${expectedWidth})`);
        }
    }

    // Check for page number (usually in format P100, P200, etc.)
    const pageMatch = content.match(/P(\d{3})/);
    const pageNumber = pageMatch ? pageMatch[1] : undefined;

    // Count ANSI color codes
    const colorCodes = (content.match(/\x1b\[\d+m/g) || []).length;

    if (colorCodes === 0) {
        issues.push('No color codes found - plain text only');
    }

    return {
        valid: issues.length === 0,
        pageNumber,
        lineCount: lines.length,
        colorCodes,
        issues
    };
}

function getSVGPreviewHTML(svgContent: string, fileName: string, report: SVGReport): string {
    const statusColor = report.valid ? '#4ade80' : '#f87171';
    const statusText = report.valid ? 'Valid' : 'Issues Found';

    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 24px;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #3e3e42;
        }
        h1 {
            font-size: 24px;
            margin: 0;
            color: #fff;
        }
        .status {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            background: ${statusColor}22;
            color: ${statusColor};
            border: 1px solid ${statusColor};
        }
        .preview-container {
            background: #fff;
            border: 1px solid #3e3e42;
            border-radius: 8px;
            padding: 32px;
            margin-bottom: 24px;
            text-align: center;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .info-card {
            background: #252526;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #3e3e42;
        }
        .info-label {
            font-size: 12px;
            color: #858585;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .info-value {
            font-size: 18px;
            font-weight: 600;
            color: #d4d4d4;
        }
        .issue-list {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
        }
        .issue-item {
            padding: 8px 0;
            border-bottom: 1px solid #3e3e42;
            font-size: 14px;
        }
        .issue-item:last-child {
            border-bottom: none;
        }
        .issue-item.error {
            color: #f87171;
        }
        .issue-item.warning {
            color: #fbbf24;
        }
        h2 {
            font-size: 18px;
            margin: 24px 0 16px 0;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 ${fileName}</h1>
        <div class="status">${statusText}</div>
    </div>

    <div class="preview-container">
        ${svgContent}
    </div>

    <div class="info-grid">
        ${report.dimensions ? `
        <div class="info-card">
            <div class="info-label">Dimensions</div>
            <div class="info-value">${report.dimensions.width} × ${report.dimensions.height}</div>
        </div>
        ` : ''}
        ${report.viewBox ? `
        <div class="info-card">
            <div class="info-label">ViewBox</div>
            <div class="info-value">${report.viewBox}</div>
        </div>
        ` : ''}
        <div class="info-card">
            <div class="info-label">Element Count</div>
            <div class="info-value">${report.elementCount}</div>
        </div>
    </div>

    ${report.issues.length > 0 ? `
    <h2>❌ Errors (${report.issues.length})</h2>
    <div class="issue-list">
        ${report.issues.map(issue => `<div class="issue-item error">• ${issue}</div>`).join('')}
    </div>
    ` : ''}

    ${report.warnings.length > 0 ? `
    <h2>⚠️ Warnings (${report.warnings.length})</h2>
    <div class="issue-list">
        ${report.warnings.map(warning => `<div class="issue-item warning">• ${warning}</div>`).join('')}
    </div>
    ` : ''}

    ${report.valid && report.warnings.length === 0 ? `
    <div style="text-align: center; padding: 32px; background: #4ade8022; border: 1px solid #4ade80; border-radius: 8px; margin-top: 24px;">
        <div style="font-size: 48px; margin-bottom: 12px;">✅</div>
        <div style="font-size: 18px; font-weight: 600; color: #4ade80;">SVG Validation Passed</div>
        <div style="font-size: 14px; color: #858585; margin-top: 8px;">No issues found</div>
    </div>
    ` : ''}
</body>
</html>`;
}

function getASCIIPreviewHTML(content: string, report: ASCIIReport): string {
    const statusColor = report.valid ? '#4ade80' : '#f87171';
    const statusText = report.valid ? 'Valid ASCII' : 'Issues Found';

    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 24px;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #3e3e42;
        }
        h1 {
            font-size: 24px;
            margin: 0;
            color: #fff;
        }
        .status {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            background: ${statusColor}22;
            color: ${statusColor};
            border: 1px solid ${statusColor};
        }
        .preview-container {
            background: #000;
            border: 1px solid #3e3e42;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            font-family: 'Courier New', 'Consolas', monospace;
            font-size: 14px;
            line-height: 1.2;
            white-space: pre;
            overflow-x: auto;
            color: #0f0;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .info-card {
            background: #252526;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #3e3e42;
        }
        .info-label {
            font-size: 12px;
            color: #858585;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .info-value {
            font-size: 18px;
            font-weight: 600;
            color: #d4d4d4;
        }
        .issue-list {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
        }
        .issue-item {
            padding: 8px 0;
            border-bottom: 1px solid #3e3e42;
            font-size: 14px;
            color: #f87171;
        }
        .issue-item:last-child {
            border-bottom: none;
        }
        h2 {
            font-size: 18px;
            margin: 24px 0 16px 0;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📟 ASCII Art Preview</h1>
        <div class="status">${statusText}</div>
    </div>

    <div class="preview-container">${escapeHtml(content)}</div>

    <div class="info-grid">
        <div class="info-card">
            <div class="info-label">Dimensions</div>
            <div class="info-value">${report.dimensions.width} × ${report.dimensions.height}</div>
        </div>
        <div class="info-card">
            <div class="info-label">Total Characters</div>
            <div class="info-value">${content.length.toLocaleString()}</div>
        </div>
        <div class="info-card">
            <div class="info-label">Non-ASCII</div>
            <div class="info-value" style="color: ${report.hasNonASCII ? '#f87171' : '#4ade80'}">
                ${report.hasNonASCII ? 'Yes' : 'No'}
            </div>
        </div>
        <div class="info-card">
            <div class="info-label">Contains Tabs</div>
            <div class="info-value" style="color: ${report.hasTabs ? '#fbbf24' : '#4ade80'}">
                ${report.hasTabs ? 'Yes' : 'No'}
            </div>
        </div>
    </div>

    ${report.issues.length > 0 ? `
    <h2>⚠️ Issues (${report.issues.length})</h2>
    <div class="issue-list">
        ${report.issues.slice(0, 20).map(issue => `<div class="issue-item">• ${escapeHtml(issue)}</div>`).join('')}
        ${report.issues.length > 20 ? `<div style="padding: 8px 0; color: #858585; text-align: center;">... and ${report.issues.length - 20} more issues</div>` : ''}
    </div>
    ` : `
    <div style="text-align: center; padding: 32px; background: #4ade8022; border: 1px solid #4ade80; border-radius: 8px; margin-top: 24px;">
        <div style="font-size: 48px; margin-bottom: 12px;">✅</div>
        <div style="font-size: 18px; font-weight: 600; color: #4ade80;">ASCII Validation Passed</div>
        <div style="font-size: 14px; color: #858585; margin-top: 8px;">No issues found</div>
    </div>
    `}
</body>
</html>`;
}

function getTeletextValidationHTML(content: string, report: TeletextReport): string {
    const statusColor = report.valid ? '#4ade80' : '#f87171';
    const statusText = report.valid ? 'Valid Format' : 'Issues Found';

    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 24px;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #3e3e42;
        }
        h1 {
            font-size: 24px;
            margin: 0;
            color: #fff;
        }
        .status {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            background: ${statusColor}22;
            color: ${statusColor};
            border: 1px solid ${statusColor};
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .info-card {
            background: #252526;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #3e3e42;
        }
        .info-label {
            font-size: 12px;
            color: #858585;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .info-value {
            font-size: 18px;
            font-weight: 600;
            color: #d4d4d4;
        }
        .spec-box {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 24px;
        }
        .spec-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #3e3e42;
        }
        .spec-item:last-child {
            border-bottom: none;
        }
        .issue-list {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
        }
        .issue-item {
            padding: 8px 0;
            border-bottom: 1px solid #3e3e42;
            font-size: 14px;
            color: #f87171;
        }
        .issue-item:last-child {
            border-bottom: none;
        }
        h2 {
            font-size: 18px;
            margin: 24px 0 16px 0;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📺 Teletext Validation</h1>
        <div class="status">${statusText}</div>
    </div>

    <div class="info-grid">
        ${report.pageNumber ? `
        <div class="info-card">
            <div class="info-label">Page Number</div>
            <div class="info-value">P${report.pageNumber}</div>
        </div>
        ` : ''}
        <div class="info-card">
            <div class="info-label">Line Count</div>
            <div class="info-value" style="color: ${report.lineCount === 24 ? '#4ade80' : '#f87171'}">
                ${report.lineCount} ${report.lineCount === 24 ? '✓' : '(expected 24)'}
            </div>
        </div>
        <div class="info-card">
            <div class="info-label">Color Codes</div>
            <div class="info-value">${report.colorCodes}</div>
        </div>
    </div>

    <h2>📋 Teletext Specification</h2>
    <div class="spec-box">
        <div class="spec-item">
            <span>Lines per page:</span>
            <span style="font-weight: 600;">24</span>
        </div>
        <div class="spec-item">
            <span>Columns per line:</span>
            <span style="font-weight: 600;">40</span>
        </div>
        <div class="spec-item">
            <span>Character set:</span>
            <span style="font-weight: 600;">7-bit ASCII + control codes</span>
        </div>
        <div class="spec-item">
            <span>Color support:</span>
            <span style="font-weight: 600;">8 colors (ANSI escape codes)</span>
        </div>
    </div>

    ${report.issues.length > 0 ? `
    <h2>⚠️ Format Issues (${report.issues.length})</h2>
    <div class="issue-list">
        ${report.issues.map(issue => `<div class="issue-item">• ${escapeHtml(issue)}</div>`).join('')}
    </div>
    ` : `
    <div style="text-align: center; padding: 32px; background: #4ade8022; border: 1px solid #4ade80; border-radius: 8px; margin-top: 24px;">
        <div style="font-size: 48px; margin-bottom: 12px;">✅</div>
        <div style="font-size: 18px; font-weight: 600; color: #4ade80;">Teletext Format Valid</div>
        <div style="font-size: 14px; color: #858585; margin-top: 8px;">Meets 24×40 specification</div>
    </div>
    `}
</body>
</html>`;
}

function escapeHtml(text: string): string {
    const map: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
