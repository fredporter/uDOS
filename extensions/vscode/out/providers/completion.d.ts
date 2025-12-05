import * as vscode from 'vscode';
export declare class UPYCompletionProvider implements vscode.CompletionItemProvider {
    private commands;
    provideCompletionItems(document: vscode.TextDocument, position: vscode.Position): vscode.CompletionItem[];
    private getVariableCompletions;
    private getMissionPropertyCompletions;
    private getWorkflowPropertyCompletions;
    private getCheckpointPropertyCompletions;
    private getGuidePropertyCompletions;
}
