import * as vscode from 'vscode';

export async function runScript(context: vscode.ExtensionContext): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'upy') {
        vscode.window.showErrorMessage('No .uPY file active');
        return;
    }

    const config = vscode.workspace.getConfiguration('udos');
    const apiUrl = config.get<string>('apiUrl', 'http://localhost:5001');
    const script = editor.document.getText();

    vscode.window.showInformationMessage('Running uDOS script...');
    
    // TODO: Implement API call to uDOS server
    // For now, show placeholder message
    vscode.window.showInformationMessage('Script execution: Coming in next implementation phase');
}

export async function runInSandbox(context: vscode.ExtensionContext): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'upy') {
        vscode.window.showErrorMessage('No .uPY file active');
        return;
    }

    vscode.window.showInformationMessage('Running in sandbox...');
    
    // TODO: Implement sandbox execution
    // For now, show placeholder message
    vscode.window.showInformationMessage('Sandbox execution: Coming in next implementation phase');
}
