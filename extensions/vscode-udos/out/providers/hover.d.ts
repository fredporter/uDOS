import * as vscode from 'vscode';
export declare class UPYHoverProvider implements vscode.HoverProvider {
    private commandDocs;
    provideHover(document: vscode.TextDocument, position: vscode.Position): vscode.Hover | null;
    private getVariableHover;
}
