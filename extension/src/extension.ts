import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('uDOS v1.0 extension is now active!');

    // Register v1.0 commands with user role awareness
    let runCommand = vscode.commands.registerCommand('udos.runCommand', async () => {
        const command = await vscode.window.showInputBox({
            prompt: 'Enter uDOS command (role-aware)',
            placeHolder: 'e.g., HELP, DASH, CHECK, VALIDATE'
        });

        if (command) {
            await runUDOSCommand(command);
        }
    });

    let validateInstallation = vscode.commands.registerCommand('udos.validateInstallation', () => {
        runUDOSScript('./uCode/validate-installation.sh', ['full']);
    });

    let showUserRole = vscode.commands.registerCommand('udos.showUserRole', () => {
        runUDOSScript('./uCode/user-roles.sh', ['info']);
    });

    let initializeUser = vscode.commands.registerCommand('udos.initializeUser', () => {
        runUDOSScript('./uCode/init-user.sh', []);
    });

    let startChester = vscode.commands.registerCommand('udos.startChester', () => {
        runUDOSScript('./uCode/companion-system.sh', ['start_chester']);
    });

    let generateDashboard = vscode.commands.registerCommand('udos.generateDashboard', () => {
        runUDOSScript('./uCode/dash.sh', ['build']);
    });

    let createMission = vscode.commands.registerCommand('udos.createMission', async () => {
        const missionName = await vscode.window.showInputBox({
            prompt: 'Enter mission name',
            placeHolder: 'e.g., Setup Development Environment'
        });

        if (missionName) {
            runUDOSScript('./uCode/structure.sh', ['mission', missionName]);
        }
    });

    let viewWithGlow = vscode.commands.registerCommand('udos.viewWithGlow', (uri: vscode.Uri) => {
        const terminal = vscode.window.createTerminal('uDOS Glow');
        terminal.sendText(`glow "${uri.fsPath}"`);
        terminal.show();
    });

    // Register completion provider for uScript with v1.0 commands
    const provider = vscode.languages.registerCompletionItemProvider(
        'uscript',
        {
            provideCompletionItems(_document: vscode.TextDocument, _position: vscode.Position) {
                const completions: vscode.CompletionItem[] = [];

                // v1.0 uDOS commands with role awareness
                const commands = [
                    'LOG', 'RUN', 'TREE', 'LIST', 'DASH', 'SYNC', 'HELP',
                    'RESTART', 'REBOOT', 'DESTROY', 'IDENTITY', 'DEBUG',
                    'VALIDATE', 'USER_ROLE', 'CHESTER', 'PERMISSIONS',
                    'CHECK USER', 'CHECK LOCATION', 'CHECK TIMEZONE',
                    'JSON LIST', 'JSON SEARCH', 'JSON EXPORT',
                    'TEMPLATE LIST', 'TEMPLATE GENERATE',
                    'MAP GENERATE', 'MAP REGION', 'MAP CITY'
                ];

                commands.forEach(cmd => {
                    const completion = new vscode.CompletionItem(cmd, vscode.CompletionItemKind.Keyword);
                    completion.documentation = new vscode.MarkdownString(`Execute uDOS command: \`${cmd}\``);
                    completions.push(completion);
                });

                // Visual Basic style keywords
                const vbKeywords = [
                    'SET', 'IF', 'THEN', 'ELSE', 'END IF', 'FOR', 'NEXT', 
                    'DO', 'WHILE', 'LOOP', 'FUNCTION', 'END FUNCTION',
                    'SUB', 'END SUB', 'DIM', 'AS', 'STRING', 'INTEGER'
                ];

                vbKeywords.forEach(keyword => {
                    const completion = new vscode.CompletionItem(keyword, vscode.CompletionItemKind.Keyword);
                    completion.documentation = new vscode.MarkdownString(`uScript keyword: \`${keyword}\``);
                    completions.push(completion);
                });

                return completions;
            }
        },
        ' ', '\n'
    );

    context.subscriptions.push(runCommand, generateDashboard, createMission, viewWithGlow, validateInstallation, showUserRole, initializeUser, startChester, provider);

    // Status bar
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = "$(terminal) uDOS";
    statusBarItem.tooltip = "Click to run uDOS command";
    statusBarItem.command = 'udos.runCommand';
    statusBarItem.show();

    context.subscriptions.push(statusBarItem);
}

function runUDOSCommand(command: string) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder found');
        return;
    }

    const terminal = vscode.window.createTerminal('uDOS Shell');
    terminal.sendText(`cd "${workspaceFolder.uri.fsPath}"`);
    terminal.sendText(`echo "${command}" | ./uCode/ucode.sh`);
    terminal.show();
}

function runUDOSScript(script: string, args: string[] = []) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder found');
        return;
    }

    const terminal = vscode.window.createTerminal('uDOS Script');
    terminal.sendText(`cd "${workspaceFolder.uri.fsPath}"`);
    terminal.sendText(`${script} ${args.join(' ')}`);
    terminal.show();
}

export function deactivate() {}
