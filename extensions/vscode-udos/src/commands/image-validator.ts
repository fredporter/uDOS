import * as vscode from 'vscode';

export async function previewSVG(uri: vscode.Uri): Promise<void> {
    vscode.window.showInformationMessage(`Previewing SVG: ${uri.fsPath}`);
    
    // TODO: Implement SVG preview
    // For now, show placeholder message
    vscode.window.showInformationMessage('SVG preview: Coming in next implementation phase');
}

export async function previewASCII(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file active');
        return;
    }

    vscode.window.showInformationMessage('Previewing ASCII art...');
    
    // TODO: Implement ASCII preview
    // For now, show placeholder message
    vscode.window.showInformationMessage('ASCII preview: Coming in next implementation phase');
}

export async function validateTeletext(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file active');
        return;
    }

    vscode.window.showInformationMessage('Validating teletext...');
    
    // TODO: Implement teletext validation
    // For now, show placeholder message
    vscode.window.showInformationMessage('Teletext validation: Coming in next implementation phase');
}
