import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface QualityIssue {
    file: string;
    type: 'missing_frontmatter' | 'outdated' | 'too_short' | 'broken_link' | 'missing_examples' | 'no_tags' | 'incomplete';
    severity: 'error' | 'warning' | 'info';
    message: string;
    data?: any;
}

interface GuideMetadata {
    path: string;
    category: string;
    title: string;
    frontmatter?: any;
    content: string;
    wordCount: number;
    lastModified?: Date;
}

interface QualityReport {
    totalGuides: number;
    scannedGuides: number;
    issues: QualityIssue[];
    flaggedForRegen: string[];
    categories: Record<string, number>;
    qualityMetrics: {
        avgWordCount: number;
        withFrontmatter: number;
        withExamples: number;
        withTags: number;
        outdated: number;
    };
}

export async function checkKnowledgeQuality(context: vscode.ExtensionContext): Promise<void> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const knowledgeRoot = path.join(workspaceFolder.uri.fsPath, 'knowledge');

    if (!fs.existsSync(knowledgeRoot)) {
        vscode.window.showErrorMessage('Knowledge directory not found');
        return;
    }

    // Show progress
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Scanning knowledge base',
        cancellable: false
    }, async (progress) => {
        progress.report({ message: 'Loading guides...' });

        // Scan all guides
        const guides = await scanKnowledgeBase(knowledgeRoot);

        progress.report({ message: `Analyzing ${guides.length} guides...` });

        // Run quality checks
        const report = await analyzeQuality(guides, (current, total) => {
            progress.report({
                message: `Analyzing ${current}/${total}...`,
                increment: (1 / total) * 100
            });
        });

        // Show report in webview
        const panel = vscode.window.createWebviewPanel(
            'knowledgeQuality',
            'Knowledge Quality Report',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = getQualityReportHTML(report);

        // Generate REGEN command file if there are flagged guides
        if (report.flaggedForRegen.length > 0) {
            const shouldGenerate = await vscode.window.showInformationMessage(
                `Found ${report.flaggedForRegen.length} guides that need regeneration. Generate REGEN script?`,
                'Yes', 'No'
            );

            if (shouldGenerate === 'Yes') {
                await generateRegenScript(workspaceFolder.uri.fsPath, report.flaggedForRegen);
            }
        }

        vscode.window.showInformationMessage(
            `✅ Quality check complete: ${report.scannedGuides} guides scanned, ${report.issues.length} issues found`
        );
    });
}

async function scanKnowledgeBase(knowledgeRoot: string): Promise<GuideMetadata[]> {
    const guides: GuideMetadata[] = [];
    const categories = ['water', 'fire', 'shelter', 'food', 'navigation', 'medical'];

    for (const category of categories) {
        const categoryPath = path.join(knowledgeRoot, category);

        if (!fs.existsSync(categoryPath)) {
            continue;
        }

        const files = fs.readdirSync(categoryPath);

        for (const file of files) {
            if (!file.endsWith('.md')) {
                continue;
            }

            const filePath = path.join(categoryPath, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            const stats = fs.statSync(filePath);

            // Extract frontmatter
            const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
            let frontmatter: any = null;

            if (frontmatterMatch) {
                try {
                    // Parse YAML frontmatter (simple parser)
                    frontmatter = parseFrontmatter(frontmatterMatch[1]);
                } catch (error) {
                    console.error(`Failed to parse frontmatter for ${filePath}:`, error);
                }
            }

            const wordCount = content.split(/\s+/).length;

            guides.push({
                path: filePath,
                category,
                title: frontmatter?.title || file.replace('.md', ''),
                frontmatter,
                content,
                wordCount,
                lastModified: stats.mtime
            });
        }
    }

    return guides;
}

function parseFrontmatter(yamlText: string): any {
    const result: any = {};
    const lines = yamlText.split('\n');

    for (const line of lines) {
        const match = line.match(/^(\w+):\s*(.+)$/);
        if (match) {
            const [, key, value] = match;
            // Simple value parsing
            if (value.startsWith('[') && value.endsWith(']')) {
                result[key] = value.slice(1, -1).split(',').map(v => v.trim());
            } else if (value.startsWith('"') && value.endsWith('"')) {
                result[key] = value.slice(1, -1);
            } else {
                result[key] = value;
            }
        }
    }

    return result;
}

async function analyzeQuality(
    guides: GuideMetadata[],
    progressCallback: (current: number, total: number) => void
): Promise<QualityReport> {
    const issues: QualityIssue[] = [];
    const categories: Record<string, number> = {};

    let totalWordCount = 0;
    let withFrontmatter = 0;
    let withExamples = 0;
    let withTags = 0;
    let outdated = 0;

    for (let i = 0; i < guides.length; i++) {
        const guide = guides[i];
        progressCallback(i + 1, guides.length);

        // Count by category
        categories[guide.category] = (categories[guide.category] || 0) + 1;

        // Check frontmatter
        if (!guide.frontmatter) {
            issues.push({
                file: guide.path,
                type: 'missing_frontmatter',
                severity: 'error',
                message: 'Missing YAML frontmatter'
            });
        } else {
            withFrontmatter++;
        }

        // Check last reviewed date
        if (guide.frontmatter?.last_reviewed) {
            const lastReview = new Date(guide.frontmatter.last_reviewed);
            const daysSinceReview = (Date.now() - lastReview.getTime()) / (1000 * 60 * 60 * 24);

            if (daysSinceReview > 365) {
                outdated++;
                issues.push({
                    file: guide.path,
                    type: 'outdated',
                    severity: 'warning',
                    message: `Not reviewed in ${Math.floor(daysSinceReview)} days`,
                    data: { daysSinceReview: Math.floor(daysSinceReview) }
                });
            }
        }

        // Check word count
        totalWordCount += guide.wordCount;

        if (guide.wordCount < 300) {
            issues.push({
                file: guide.path,
                type: 'too_short',
                severity: 'warning',
                message: `Only ${guide.wordCount} words (minimum 300 recommended)`,
                data: { wordCount: guide.wordCount }
            });
        }

        // Check for examples
        if (guide.content.includes('Example:') || guide.content.match(/```[\s\S]*?```/)) {
            withExamples++;
        } else {
            issues.push({
                file: guide.path,
                type: 'missing_examples',
                severity: 'info',
                message: 'No examples or code blocks found'
            });
        }

        // Check for tags
        if (guide.frontmatter?.tags && guide.frontmatter.tags.length > 0) {
            withTags++;
        } else {
            issues.push({
                file: guide.path,
                type: 'no_tags',
                severity: 'info',
                message: 'No tags defined'
            });
        }

        // Check for broken internal links
        const linkMatches = guide.content.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g);
        for (const match of linkMatches) {
            const linkPath = match[2];
            // Only check relative paths
            if (!linkPath.startsWith('http') && !linkPath.startsWith('#')) {
                const fullPath = path.resolve(path.dirname(guide.path), linkPath);
                if (!fs.existsSync(fullPath)) {
                    issues.push({
                        file: guide.path,
                        type: 'broken_link',
                        severity: 'error',
                        message: `Broken link: ${linkPath}`,
                        data: { link: linkPath }
                    });
                }
            }
        }
    }

    // Determine guides flagged for regeneration
    const criticalTypes = ['missing_frontmatter', 'broken_link', 'too_short', 'outdated'];
    const flaggedForRegen = [...new Set(
        issues
            .filter(i => criticalTypes.includes(i.type))
            .map(i => i.file)
    )];

    return {
        totalGuides: guides.length,
        scannedGuides: guides.length,
        issues,
        flaggedForRegen,
        categories,
        qualityMetrics: {
            avgWordCount: Math.round(totalWordCount / guides.length),
            withFrontmatter,
            withExamples,
            withTags,
            outdated
        }
    };
}

async function generateRegenScript(workspaceRoot: string, flaggedGuides: string[]): Promise<void> {
    const commands: string[] = [
        '# Knowledge Regeneration Script',
        '# Generated: ' + new Date().toISOString(),
        '# Guides flagged for regeneration: ' + flaggedGuides.length,
        ''
    ];

    for (const guidePath of flaggedGuides) {
        const relativePath = path.relative(path.join(workspaceRoot, 'knowledge'), guidePath);
        const parts = relativePath.split(path.sep);
        const category = parts[0];
        const fileName = parts[parts.length - 1].replace('.md', '');

        // Read file to get title
        const content = fs.readFileSync(guidePath, 'utf-8');
        const titleMatch = content.match(/^#\s+(.+)$/m);
        const title = titleMatch ? titleMatch[1] : fileName;

        commands.push(`# Regenerate: ${category}/${fileName}`);
        commands.push(`GENERATE GUIDE ${category} "${title}" --complexity detailed --regen`);
        commands.push('');
    }

    const outputPath = path.join(workspaceRoot, 'memory', 'workflows', 'missions', 'knowledge-regen-batch.upy');
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, commands.join('\n'));

    const doc = await vscode.workspace.openTextDocument(outputPath);
    await vscode.window.showTextDocument(doc);

    vscode.window.showInformationMessage(`Generated REGEN script: ${path.basename(outputPath)}`);
}

function getQualityReportHTML(report: QualityReport): string {
    const errorIssues = report.issues.filter(i => i.severity === 'error');
    const warningIssues = report.issues.filter(i => i.severity === 'warning');
    const infoIssues = report.issues.filter(i => i.severity === 'info');

    const issuesByType = report.issues.reduce((acc, issue) => {
        acc[issue.type] = (acc[issue.type] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

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
        h1 {
            font-size: 28px;
            margin: 0 0 24px 0;
            color: #fff;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .summary-card {
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #3e3e42;
        }
        .summary-value {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .summary-label {
            font-size: 13px;
            color: #858585;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .section {
            margin-bottom: 32px;
        }
        .section h2 {
            font-size: 18px;
            margin: 0 0 16px 0;
            color: #fff;
            font-weight: 600;
        }
        .issue-group {
            margin-bottom: 24px;
        }
        .issue-group h3 {
            font-size: 14px;
            margin: 0 0 12px 0;
            color: #d4d4d4;
            font-weight: 600;
        }
        .issue-list {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            overflow: hidden;
        }
        .issue-item {
            padding: 12px 16px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .issue-item:last-child {
            border-bottom: none;
        }
        .issue-icon {
            flex-shrink: 0;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }
        .issue-icon.error {
            background: #f87171;
            color: #fff;
        }
        .issue-icon.warning {
            background: #fbbf24;
            color: #000;
        }
        .issue-icon.info {
            background: #60a5fa;
            color: #fff;
        }
        .issue-content {
            flex: 1;
        }
        .issue-file {
            font-size: 12px;
            color: #858585;
            font-family: 'Consolas', monospace;
            margin-bottom: 4px;
        }
        .issue-message {
            font-size: 14px;
            color: #d4d4d4;
        }
        .regen-list {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 16px;
            max-height: 400px;
            overflow-y: auto;
        }
        .regen-item {
            font-family: 'Consolas', monospace;
            font-size: 13px;
            padding: 6px 0;
            color: #fca5a5;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }
        .stat-item {
            background: #252526;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #3e3e42;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .stat-label {
            font-size: 12px;
            color: #858585;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 8px;
        }
        .badge.success {
            background: #4ade8022;
            color: #4ade80;
            border: 1px solid #4ade80;
        }
        .badge.warning {
            background: #fbbf2422;
            color: #fbbf24;
            border: 1px solid #fbbf24;
        }
    </style>
</head>
<body>
    <h1>📚 Knowledge Quality Report</h1>

    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-value">${report.scannedGuides}</div>
            <div class="summary-label">Total Guides</div>
        </div>
        <div class="summary-card">
            <div class="summary-value" style="color: ${errorIssues.length > 0 ? '#f87171' : '#4ade80'}">${report.issues.length}</div>
            <div class="summary-label">Issues Found</div>
        </div>
        <div class="summary-card">
            <div class="summary-value" style="color: ${report.flaggedForRegen.length > 0 ? '#fbbf24' : '#4ade80'}">${report.flaggedForRegen.length}</div>
            <div class="summary-label">Flagged for REGEN</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">${report.qualityMetrics.avgWordCount}</div>
            <div class="summary-label">Avg Word Count</div>
        </div>
    </div>

    <div class="section">
        <h2>Quality Metrics</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">${report.qualityMetrics.withFrontmatter}</div>
                <div class="stat-label">With Frontmatter</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${report.qualityMetrics.withExamples}</div>
                <div class="stat-label">With Examples</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${report.qualityMetrics.withTags}</div>
                <div class="stat-label">With Tags</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: ${report.qualityMetrics.outdated > 0 ? '#fbbf24' : '#4ade80'}">${report.qualityMetrics.outdated}</div>
                <div class="stat-label">Outdated (>1 year)</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Categories</h2>
        <div class="stats-grid">
            ${Object.entries(report.categories).map(([cat, count]) => `
            <div class="stat-item">
                <div class="stat-value">${count}</div>
                <div class="stat-label">${cat.charAt(0).toUpperCase() + cat.slice(1)}</div>
            </div>
            `).join('')}
        </div>
    </div>

    ${errorIssues.length > 0 ? `
    <div class="section">
        <h2>❌ Errors (${errorIssues.length}) <span class="badge warning">Critical</span></h2>
        <div class="issue-list">
            ${errorIssues.slice(0, 20).map(issue => `
            <div class="issue-item">
                <div class="issue-icon error">!</div>
                <div class="issue-content">
                    <div class="issue-file">${path.basename(issue.file)}</div>
                    <div class="issue-message">${issue.message}</div>
                </div>
            </div>
            `).join('')}
            ${errorIssues.length > 20 ? `<div style="padding: 12px; text-align: center; color: #858585; font-size: 13px;">... and ${errorIssues.length - 20} more</div>` : ''}
        </div>
    </div>
    ` : ''}

    ${warningIssues.length > 0 ? `
    <div class="section">
        <h2>⚠️ Warnings (${warningIssues.length})</h2>
        <div class="issue-list">
            ${warningIssues.slice(0, 20).map(issue => `
            <div class="issue-item">
                <div class="issue-icon warning">⚠</div>
                <div class="issue-content">
                    <div class="issue-file">${path.basename(issue.file)}</div>
                    <div class="issue-message">${issue.message}</div>
                </div>
            </div>
            `).join('')}
            ${warningIssues.length > 20 ? `<div style="padding: 12px; text-align: center; color: #858585; font-size: 13px;">... and ${warningIssues.length - 20} more</div>` : ''}
        </div>
    </div>
    ` : ''}

    ${report.flaggedForRegen.length > 0 ? `
    <div class="section">
        <h2>🔄 Guides Flagged for Regeneration (${report.flaggedForRegen.length})</h2>
        <div class="regen-list">
            ${report.flaggedForRegen.map(file => `
            <div class="regen-item">📄 ${path.relative(path.join(file, '../..'), file)}</div>
            `).join('')}
        </div>
    </div>
    ` : ''}

    ${report.issues.length === 0 ? `
    <div class="section">
        <div style="text-align: center; padding: 48px; background: #4ade8022; border: 1px solid #4ade80; border-radius: 8px;">
            <div style="font-size: 48px; margin-bottom: 16px;">✅</div>
            <div style="font-size: 18px; font-weight: 600; color: #4ade80;">All Guides Pass Quality Checks!</div>
            <div style="font-size: 14px; color: #858585; margin-top: 8px;">No issues found in ${report.scannedGuides} guides</div>
        </div>
    </div>
    ` : ''}
</body>
</html>`;
}
