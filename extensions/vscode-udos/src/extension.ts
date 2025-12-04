import * as vscode from 'vscode';
import { UPYCompletionProvider } from './providers/completion';
import { UPYHoverProvider } from './providers/hover';
import { runScript, runInSandbox } from './commands/executor';
import { checkKnowledgeQuality } from './commands/knowledge-checker';
import { previewSVG, previewASCII, validateTeletext } from './commands/image-validator';

export function activate(context: vscode.ExtensionContext) {
    console.log('uDOS Language Support extension is now active');

    // Register language providers
    const upySelector: vscode.DocumentSelector = { language: 'upy', scheme: 'file' };

    // Completion provider (IntelliSense)
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            upySelector,
            new UPYCompletionProvider(),
            '.',  // Trigger on dot for $VARIABLE.PROPERTY
            ' '   // Trigger on space for command completion
        )
    );

    // Hover provider (documentation)
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(
            upySelector,
            new UPYHoverProvider()
        )
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('udos.runScript', () => runScript(context)),
        vscode.commands.registerCommand('udos.runInSandbox', () => runInSandbox(context)),
        vscode.commands.registerCommand('udos.checkKnowledgeQuality', () => checkKnowledgeQuality(context)),
        vscode.commands.registerCommand('udos.previewSVG', (uri: vscode.Uri) => previewSVG(uri)),
        vscode.commands.registerCommand('udos.previewASCII', () => previewASCII()),
        vscode.commands.registerCommand('udos.validateTeletext', () => validateTeletext())
    );

    // Status bar
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(beaker) uDOS';
    statusBarItem.tooltip = 'uDOS Extension Active';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

export function deactivate() {
    console.log('uDOS Language Support extension is now deactivated');
}
