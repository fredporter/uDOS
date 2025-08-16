import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// uDOS Extension v1.2.0 - Universal Development & Operations System
export function activate(context: vscode.ExtensionContext) {
    console.log('uDOS v1.2.0 extension is now active with unified architecture!');

    // ===== CORE UDOS v1.2 COMMANDS =====
    
    let quickSetup = vscode.commands.registerCommand('udos.quickSetup', () => {
        runUDOSScript('./uCode/setup.sh', ['quick']);
        vscode.window.showInformationMessage('uDOS v1.2.0 Quick Setup initiated!');
    });

    let systemStatus = vscode.commands.registerCommand('udos.systemStatus', () => {
        runUDOSScript('./uCode/ucode.sh', ['STATUS']);
        vscode.window.showInformationMessage('Displaying uDOS v1.2.0 system status...');
    });

    let runCommand = vscode.commands.registerCommand('udos.runCommand', async () => {
        const command = await vscode.window.showInputBox({
            prompt: 'Enter uDOS command (v1.2.0 unified)',
            placeHolder: 'e.g., STATUS, MEMORY list, MISSION create, TEMPLATE list'
        });

        if (command) {
            await runUDOSCommand(command);
        }
    });

    let openMemory = vscode.commands.registerCommand('udos.openMemory', () => {
        const udosPath = getUDOSPath();
        if (udosPath) {
            const memoryPath = path.join(udosPath, 'uMemory');
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(memoryPath));
        }
    });

    // ===== TEMPLATE SYSTEM =====

    let createProject = vscode.commands.registerCommand('udos.createProject', async () => {
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            placeHolder: 'e.g., uDOS v1.3 Development'
        });

        if (projectName) {
            runUDOSScript('./uCode/ucode.sh', ['TEMPLATE', 'generate', 'project', projectName]);
        }
    });

    let createMission = vscode.commands.registerCommand('udos.createMission', async () => {
        const missionName = await vscode.window.showInputBox({
            prompt: 'Enter mission name', 
            placeHolder: 'e.g., Complete System Integration'
        });

        if (missionName) {
            runUDOSScript('./uCode/ucode.sh', ['MISSION', 'create', missionName]);
        }
    });

    let createMilestone = vscode.commands.registerCommand('udos.createMilestone', async () => {
        const milestoneName = await vscode.window.showInputBox({
            prompt: 'Enter milestone name',
            placeHolder: 'e.g., Beta Release Candidate'
        });

        if (milestoneName) {
            runUDOSScript('./uCode/ucode.sh', ['TEMPLATE', 'generate', 'milestone', milestoneName]);
        }
    });

    let listTemplates = vscode.commands.registerCommand('udos.listTemplates', () => {
        runUDOSScript('./uCode/ucode.sh', ['TEMPLATE', 'list']);
    });

    let generateScript = vscode.commands.registerCommand('udos.generateScript', async () => {
        const scriptName = await vscode.window.showInputBox({
            prompt: 'Enter script name',
            placeHolder: 'e.g., cleanup-system'
        });

        if (scriptName) {
            runUDOSScript('./uCode/ucode.sh', ['TEMPLATE', 'generate', 'ok-assistant', scriptName]);
        }
    });

    let processShortcodes = vscode.commands.registerCommand('udos.processShortcodes', () => {
        runUDOSScript('./uCode/ucode.sh', ['TEMPLATE', 'process']);
        vscode.window.showInformationMessage('Processing template shortcodes...');
    });

    // ===== OK-ASSISTANT SYSTEM =====

    let startAssistant = vscode.commands.registerCommand('udos.startAssistant', async () => {
        const assistantType = await vscode.window.showQuickPick([
            'Chester (Dog Assistant)',
            'Generic AI Assistant', 
            'Custom Assistant'
        ], {
            placeHolder: 'Select assistant type'
        });

        if (assistantType) {
            let assistant = 'generic';
            if (assistantType.includes('Chester')) assistant = 'chester';
            if (assistantType.includes('Custom')) assistant = 'custom';
            
            runUDOSScript('./uCode/ucode.sh', ['ASSISTANT', 'start', assistant]);
        }
    });

    let configureAssistant = vscode.commands.registerCommand('udos.configureAssistant', () => {
        const udosPath = getUDOSPath();
        if (udosPath) {
            const profilesPath = path.join(udosPath, 'uCompanion', 'profiles');
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(profilesPath));
        }
    });

    let listAssistants = vscode.commands.registerCommand('udos.listAssistants', () => {
        runUDOSScript('./uCode/ucode.sh', ['ASSISTANT', 'list']);
    });

    // ===== MONITORING & DASHBOARD =====

    let showDashboard = vscode.commands.registerCommand('udos.showDashboard', () => {
        runUDOSScript('./uCode/dash.sh', ['live']);
    });

    let generateDashboard = vscode.commands.registerCommand('udos.generateDashboard', () => {
        runUDOSScript('./uCode/dash.sh', ['build']);
    });

    let updateAnalytics = vscode.commands.registerCommand('udos.updateAnalytics', () => {
        runUDOSScript('./uCode/ucode.sh', ['ANALYTICS', 'update']);
        vscode.window.showInformationMessage('Updating system analytics...');
    });

    // ===== GEOGRAPHIC & MAPPING =====

    let browseMapping = vscode.commands.registerCommand('udos.browseMapping', () => {
        const udosPath = getUDOSPath();
        if (udosPath) {
            const mappingPath = path.join(udosPath, 'uMapping');
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(mappingPath));
        }
    });

    // ===== HELPER FUNCTIONS =====

    async function runUDOSCommand(command: string): Promise<void> {
        const terminal = vscode.window.createTerminal('uDOS v1.2.0');
        const udosPath = getUDOSPath();
        
        if (udosPath) {
            terminal.sendText(`cd "${udosPath}"`);
            terminal.sendText(`./uCode/ucode.sh ${command}`);
            terminal.show();
        } else {
            vscode.window.showErrorMessage('uDOS installation not found. Please ensure uDOS v1.2.0 is installed.');
        }
    }

    function runUDOSScript(scriptPath: string, args: string[] = []): void {
        const terminal = vscode.window.createTerminal('uDOS v1.2.0');
        const udosPath = getUDOSPath();
        
        if (udosPath) {
            terminal.sendText(`cd "${udosPath}"`);
            const command = `${scriptPath} ${args.join(' ')}`;
            terminal.sendText(command);
            terminal.show();
        } else {
            vscode.window.showErrorMessage('uDOS installation not found.');
        }
    }

    function getUDOSPath(): string | undefined {
        // Try to find uDOS installation
        const possiblePaths = [
            path.join(require('os').homedir(), 'uDOS'),
            path.join(process.cwd(), 'uDOS'),
            '/usr/local/uDOS'
        ];

        for (const udosPath of possiblePaths) {
            if (fs.existsSync(path.join(udosPath, 'uCode', 'ucode.sh'))) {
                return udosPath;
            }
        }

        return undefined;
    }

    // Register all commands
    const commands = [
        quickSetup, systemStatus, runCommand, openMemory,
        createProject, createMission, createMilestone, listTemplates, generateScript, processShortcodes,
        startAssistant, configureAssistant, listAssistants,
        showDashboard, generateDashboard, updateAnalytics,
        browseMapping
    ];

    commands.forEach(command => context.subscriptions.push(command));

    vscode.window.showInformationMessage('uDOS v1.2.0 Extension loaded successfully! Universal Development & Operations System ready.');
}

export function deactivate() {
    console.log('uDOS v1.2.0 extension is now deactivated.');
}
